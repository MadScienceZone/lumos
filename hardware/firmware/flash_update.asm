; vim:set syntax=pic ts=8:
		LIST n=90
;@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
;@@                                                                         @@
;@@                                                                         @@
;@@ @@@@@  @       @@@    @@@   @   @                                       @@
;@@ @      @      @   @  @   @  @   @    FLASH ROM UPDATE LOADER            @@
;@@ @      @      @   @  @      @   @                                       @@
;@@ @@@@   @      @@@@@   @@@   @@@@@    1.0                                @@
;@@ @      @      @   @      @  @   @                                       @@
;@@ @      @      @   @  @   @  @   @                                       @@
;@@ @      @@@@@  @   @   @@@   @   @                                       @@
;@@                                                                         @@
;@@ Copyright (c) 2013 by Steven L. Willoughby, Aloha, Oregon, USA.  All    @@
;@@ Rights Reserved.                                                        @@
;@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
;
; This should be located in high memory, out of the way of the other
; bits of code. Its purpose is to receive a new ROM image from a host PC
; and burn it into the microcontroller's flash.
;
; To start, call FLASH_UPDATE_START.  This overwrites the $000000 restart
; vector to jump into FLASH_UPDATE_BOOT and then reboots the device.
; From this point on, a reset will jump back into the flash routine, so
; a failed firmware update can simply be restarted.
;
; Any time the device reboots while doing a firmware update, it jumps to
; FLASH_UPDATE_BOOT which sets the baud rate to 9600 and jumps to 
; FLASH_UPDATE_NEXT_BLOCK, which in turn receives an update block from
; the host and burns it into the flash memory.
;
; When finished, FLASH_UPDATE_END is called, which sets the reset vector
; back to _BOOT.
;
;
; This module takes over the entire device operation, disabling all interrupts
; for the duration of its execution and assuming nothing else.  It sets up and
; maintains the UART locally.
;
; The following assumptions are made about the CPU memory layout:
;
;          ____________________
;  $00000 | Restart vector     | Overwritten to boot into update loader
;  $00007 |____________________| then eventually overwritten by final image block
;  $00008 |                    | 
;         |                    | The flash loader can change this zone.
;         | update area        | The addresses shown are typical but 
;         |                    | configurable in the .inc files.
;  $16FFF |____________________|
;  $17000 | Flash loader code  | This module
;  $17FFF |____________________|
;
	PROCESSOR 	18F4685
	RADIX		DEC
; 
;==============================================================================
; PUBLIC ENTRY POINTS
;==============================================================================
	GLOBAL		FLASH_UPDATE_START	; Begin firmware update process
	GLOBAL		FLASH_UPDATE_BOOT	; Boot entry vector for recovery from errors
	GLOBAL		FLASH_UPDATE_NEXT_BLOCK	; Accept next block or end marker
	GLOBAL		FLASH_UPDATE_END	; Revert to run mode
;
#include <p18f4685.inc>
#include "flash_update_bits.inc"

;==============================================================================
; REGISTERS USED
;==============================================================================
;
;                    bit 7      6      5      4      3      2      1      0
;                     _______________________________________________________
; $FF8 TBLPTRU       |/////////////|      |                                  |
;                    |/////////////|bit 21| Flash memory table ptr <20:16>   |
;                    |/////////////|______|______|______|______|______|______|
; $FF7 TBLPTRH       |                                                       |
;                    |                Flash memory table ptr <15:8>          |
;                    |______|______|______|______|______|______|______|______|
; $FF6 TBLPTRL       |                                                       |
;                    |                Flash memory table ptr <7:0>           |
;                    |______|______|______|______|______|______|______|______|
; $FF5 TABLAT        |                                                       |
;                    |                Flash membory table data latch         |
;                    |______|______|______|______|______|______|______|______|
; $FF2 INTCON        | GIEH | GIEL |      |      |      |      |      |      |
;                    | GIE  | PEIE |      |      |      |      |      |      |
;                    |______|______|______|______|______|______|______|______|
; $FA7 EECON2        |                                                       |
;                    |       EEPROM control (write sequence protocol)        |
;                    |______|______|______|______|______|______|______|______|
; $FA6 EECON1        |      |      |//////|      |      |      |      |      |
;                    |EEPGD | CFGS |//////| FREE |WRERR | WREN |  WR  |  RD  |
;                    |______|______|//////|______|______|______|______|______|
; $FA2 IPR2          |      |      |//////|      |      |      |      |      |
;                    |OSCFIP|      |//////| EEIP |      |      |      |      |
;                    |______|______|//////|______|______|______|______|______|
; $F9E PIR1          |      |      |      |      |      |      |      |      |
;                    |      |      | RCIF | TXIF |      |      |      |      |
;                    |______|______|______|______|______|______|______|______|
; $FA1 PIR2          |      |      |//////|      |      |      |      |      |
;                    |OSCFIF|      |//////| EEIF |      |      |      |      |
;                    |______|______|//////|______|______|______|______|______|
; $FA0 PIE2          |      |      |//////|      |      |      |      |      |
;                    |OSCFIE|      |//////| EEIE |      |      |      |      |
;                    |______|______|//////|______|______|______|______|______|
; $FAB RCSTA         |      |      |      |      |      |      |      |      |
;                    | SPEN |  RX9 | SREN | CREN |ADDEN | FERR | OERR | RX9D |
;                    |______|______|______|______|______|______|______|______|
; $FAC TXSTA         |      |      |      |      |      |      |      |      |
;                    | CSRC |  TX9 | TXEN | SYNC |SENDB | BRGH | TRMT | TX9D |
;                    |______|______|______|______|______|______|______|______|
; $FAD TXREG         |                                                       |
;                    | Byte to be transmitted (bit 9 is in TX9D if used)     |
;                    |______|______|______|______|______|______|______|______|
; $FAE RCREG         |                                                       |
;                    | Byte received (bit 9 is in RX9D if used)              |
;                    |______|______|______|______|______|______|______|______|
; $FAF SPBRG         |                                                       |
;                    | Baud-rate generator value (lower byte if 16-bit mode) |
;                    |______|______|______|______|______|______|______|______|
; $FB0 SPBRGH        |                                                       |
;                    | Baud-rate generator value (upper byte) if 16-bit mode |
;                    |______|______|______|______|______|______|______|______|
; $FB8 BAUDCON       |      |      |//////|      |      |//////|      |      |
;                    |ADBOVF| RCIDL|//////| SCKP |BRG16 |//////|  WUE |ABDEN |
;                    |______|______|//////|______|______|//////|______|______|
;
;==============================================================================
; RAM LOCATIONS USED
;==============================================================================
;
; Two memory banks are used: one for the data buffer, and a second for all our
; variables.  Since this code is isolated from everything else so utterly, we
; don't even have the assembler reserve space for this, we just grab memory
; locations and use them.  The system won't be running any other code while
; we're active.
;	
;                    bit 7      6      5      4      3      2      1      0
;                     _______________________________________________________
; $000 FLASH_UPD_BUF |                                                       |
;                    |    64-byte data buffer for each block to flash        |
;                    |                                                       |
;                                                .
;                                                .
;                                                .
; $03F               |                                                       |
;                    |                                                       |
;                    |______|______|______|______|______|______|______|______|
; $040 FLASH_UPD_RC  |                                                       |
;                    |    Checksum received from host (BYTE AFTER BUF)       |
;                    |______|______|______|______|______|______|______|______|
; $041 FLASH_UPD_CKS |                                                       |
;                    |    Checksum of bytes received so far (BYTE AFTER BUF) |
;                    |______|______|______|______|______|______|______|______|
; $042 FLASH_UPD_I   |                                                       |
;                    |    General index variable                             |
;                    |______|______|______|______|______|______|______|______|
; $043 FLASH_UPD_DLY |                                                       |
;                    |    Delay counter                                      |
;                    |______|______|______|______|______|______|______|______|
; $044 FLASH_UPD_CMP |                                                       |
;                    |    Comparison value                                   |
;                    |______|______|______|______|______|______|______|______|
; $045 FLASH_UPD_FLAG|                                  |      |      |      |
;                    |                                  |FINAL |ERROR |FIRST |
;                    |______|______|______|______|______|______|______|______|
; $046 FLASH_UPD_INP |                                                       |
;                    |    Received byte                                      |
;                    |______|______|______|______|______|______|______|______|
; $047 FLASH_UPD_BLKH|                                                       |
;                    |    Current block ID <19:12>                           |
;                    |______|______|______|______|______|______|______|______|
; $048 FLASH_UPD_BLKL|                                         | 11 = undef  |
;                    |    Current block ID <11:6>              | 00 = block# |
;                    |______|______|______|______|______|______|______|______|
; $049 FLASH_UPD_X   |                                                       |
;                    |    General-purpose temporary variable                 |
;                    |______|______|______|______|______|______|______|______|
; $04A               |                                                       |
;                    |    Unused RAM                                         |
;                                                .
;                                                .
;                                                .
; $05F               |                                                       |
;                    |                                                       |
; End of ACCESS bank |______|______|______|______|______|______|______|______|
;
;
;

FLASH_UPD_BUF	EQU	0x000
FLASH_UPD_BUFSZ	EQU	0x040	; MUST be 64
FLASH_UPD_RC 	EQU	0x040
FLASH_UPD_CKS	EQU	0x041
FLASH_UPD_I	EQU	0x042
FLASH_UPD_DLY	EQU	0x043
FLASH_UPD_CMP	EQU	0x044
FLASH_UPD_FLAG	EQU	0x045		; flags for this module:
FL_FL_FIRST 	EQU	0		; -------X  Set if we're looking for the first nybble of an octet
FL_FL_ERROR	EQU	1		; ------X-  Set if last operation failed
FL_FL_FINAL	EQU	2		; -----X--  Set if this is our last block to update
FLASH_UPD_INP	EQU	0x046
FLASH_UPD_BLKH	EQU	0x047
FLASH_UPD_BLKL	EQU	0x048
FLASH_UPD_X	EQU	0x049
	IF FLASH_UPD_BUFSZ != .64
	 ERROR "FLASH_UPD_BUFSZ must be 64 bytes (hardware requirement)"
	ENDIF
	IF FLASH_UPD_RC != FLASH_UPD_BUF + FLASH_UPD_BUFSZ
	 ERROR "FLASH_UPD_RC must immediately follow FLASH_UPD_BUF"
	ENDIF

_FLASH_UPD	CODE	FLASH_UPDATE_START_ADDR
FLASH_UPDATE_START:
;
;	Start the reflashing process by changing the boot vector to point to us
;	and rebooting.
;
		CLRWDT
		BCF	INTCON, GIEH, ACCESS	; shut off ALL interrupts forever until we're done with this.
		BCF	INTCON, GIEL, ACCESS	
		CLRF	TBLPTRU		; target flash address $000000
		CLRF	TBLPTRH
		CLRF	TBLPTRL
FLASH_UPD_S0:	RCALL	FLASH_UPD_READ_BLOCK
		BTFSC	FLASH_UPD_FLAG, FL_FL_ERROR, ACCESS
		BRA	FLASH_UPD_S0
		; PIC18 GOTO instruction: 1110 1111 kkkk kkkk 1111 kkkk kkkk kkkk
		;                                   7.......0      19...........8
		; LSB is in even addressees, so in memory this is:
		; $000 kkkkkkkk  address<7:0>
		; $001 11101111  opcode
		; $002 kkkkkkkk  address<15:8>
		; $003 1111kkkk  address<19:16>
		;
		MOVLW	LOW(FLASH_UPDATE_BOOT)	; overwrite memory with new jump instruction
		MOVWF	0x000, ACCESS		; into FLASH ROM addresses $000000-$000003
		MOVLW	0xEF
		MOVWF	0x001, ACCESS		
		MOVLW	HIGH(FLASH_UPDATE_BOOT)
		MOVWF	0x002, ACCESS		
		MOVLW	UPPER(FLASH_UPDATE_BOOT)
		IORLW	0xF0
		MOVWF	0x003, ACCESS	
FLASH_UPD_S1:	RCALL	FLASH_UPD_BURN_BLOCK
		BTFSC	FLASH_UPD_FLAG, FL_FL_ERROR, ACCESS
		BRA	FLASH_UPD_S1
             	RCALL	FLASH_UPD_VERIFY_BLOCK
		BTFSC	FLASH_UPD_FLAG, FL_FL_ERROR, ACCESS
		BRA	FLASH_UPD_S1		; repeat until you get it right
		RESET
		
FLASH_UPD_READ_BLOCK:
;	Take 64-byte block at TBLPTR and copy it to RAM at FLASH_UPD_BUF.
;	FL_FL_ERROR indicates success of the operation.
;	Also moves table pointer back to start of block.
;
		CLRWDT
		LFSR	FSR0, FLASH_UPD_BUF
		MOVLW	FLASH_UPD_BUFSZ
		MOVWF	FLASH_UPD_I, ACCESS
FLASH_UPD_RB:
		CLRWDT
		TBLRD*+
		MOVFF	TABLAT, POSTINC0
		DECFSZ	FLASH_UPD_I, F, ACCESS
		BRA	FLASH_UPD_RB
FLASH_UPD_REWIND:
		TBLRD*-				; move pointer back into 64-byte block
		MOVLW	b'11000000'
		ANDWF	TBLPTRL, F, ACCESS	; and move back to start of that block
		BCF	FLASH_UPD_FLAG, FL_FL_ERROR, ACCESS
		RETURN
		
		
FLASH_UPD_BURN_BLOCK:
;	Take 64-byte block at FLASH_UPD_BUF and burn it starting at TBLPTR.
;	FL_FL_ERROR indicates success.
;	Also moves table pointer back to start of block.
;
		CLRWDT
		BSF	EECON1, EEPGD, ACCESS	; initiate bulk erase of flash memory block
		BCF	EECON1, CFGS, ACCESS	; (the write operation can only burn 1s -> 0s
		BSF	EECON1, WREN, ACCESS	; so we need to start by erasing every byte
		BSF	EECON1, FREE, ACCESS	; to 0xFF first)
		MOVLW	0x55
		MOVWF	EECON2, ACCESS
		MOVLW	0xAA
		MOVWF	EECON2, ACCESS
		BSF	EECON1, WR, ACCESS	; CPU stalls here until flash is erased

		CLRWDT
		MOVLW	FLASH_UPD_BUFSZ		; copy new block into holding registers 
		MOVWF	FLASH_UPD_I, ACCESS
		LFSR	FSR0, FLASH_UPD_BUF
FLASH_UPD_BB:	CLRWDT
		MOVFF	POSTINC0, TABLAT
		TBLWT*+				; each byte in RAM -> FLASH holding register
		DECFSZ	FLASH_UPD_I, F, ACCESS
		BRA	FLASH_UPD_BB
		RCALL	FLASH_UPD_REWIND	; move TBLPTR back to start of block
		
		BSF	EECON1, EEPGD, ACCESS	; initiate burn into FLASH
		BCF	EECON1, CFGS, ACCESS
		BSF	EECON1, WREN, ACCESS
		BCF	EECON1, FREE, ACCESS
		MOVLW	0x55
		MOVWF	EECON2, ACCESS
		MOVLW	0xAA
		MOVWF	EECON2, ACCESS		
		BSF	EECON1, WR, ACCESS	; CPU stalls here until flash is written

		BCF	EECON1, WREN, ACCESS	; disable further write access
		BCF	PIR2, EEIF, ACCESS
		BCF	FLASH_UPD_FLAG, FL_FL_ERROR, ACCESS
		BTFSC	EECON1, WRERR, ACCESS	; did we exit normally?
		BSF	FLASH_UPD_FLAG, FL_FL_ERROR, ACCESS
		RETURN
		

FLASH_UPD_VERIFY_BLOCK:
;	Compare 64-byte block at TBLPTR against RAM at FLASH_UPD_BUF.
;	set W=0 if identical, >0 if not
;	Also rewinds TBLPTR to start of block
;
		CLRWDT
		LFSR	FSR0, FLASH_UPD_BUF
		MOVLW	FLASH_UPD_BUFSZ
		MOVWF	FLASH_UPD_I, ACCESS
FLASH_UPD_VB:	CLRWDT
		TBLRD*+
		MOVF	POSTINC0, W, ACCESS
		CPFSEQ	TABLAT, ACCESS
		BRA	FLASH_UPD_VB_ERROR
		DECFSZ	FLASH_UPD_I, F, ACCESS
		BRA	FLASH_UPD_VB
		BCF	FLASH_UPD_FLAG, FL_FL_ERROR, ACCESS
		BRA	FLASH_UPD_REWIND

FLASH_UPD_VB_ERROR:
		RCALL	FLASH_UPD_REWIND
		BSF	FLASH_UPD_FLAG, FL_FL_ERROR, ACCESS
		RETURN
		

FLASH_UPDATE_BOOT:
; any time the CPU is reset while we're trying to update the firmware,
; we come here so we can keep trying the update until it's complete.
; It's important that the PC host downloading the firmware to us doesn't
; tell us it's complete if it really isn't.  We will keep coming back
; for more until the PC tells us we're ready to resume normal operations
; with the new firmware image.
;
		CLRWDT
		CLRF	STKPTR, ACCESS
		;
		; Boot-time defaults: SLEEP=SLEEP, no INT priorities, BOR enabled
		; interrupts disabled, All I/O pins inputs (tri-state); WDT off
		CLRF	T0CON, ACCESS
		MOVLW	b'00100000'
		MOVWF	CANSTAT, ACCESS
		CLRF	INTCON, ACCESS		; just to be sure!
		;
		; set up serial port pins
		;
		BSF	TRISC, 7, ACCESS	; RX pin on PORTC<7> is an input
		BCF	TRISC, 6, ACCESS	; TX pin on PORTC<6> is an output
		IF HAS_T_R
		 BCF	TRIS_T_R, BIT_T_R, ACCESS; T/R bit is output
		ENDIF
		
		;
		; set baud rate generator
		; Fosc = 40.000 MHz, BRGH=1, BRG16=1, 9600 baud => SPBRG=.1040=$0410, 0.06% error
		;
		MOVLW	0x04
		MOVWF	SPBRGH, ACCESS
		MOVLW	0x10
		MOVWF	SPBRG, ACCESS
		;
		;
		; configure and start the UART
		;
		MOVLW	b'10010000'
			; 1-------	; Serial I/O ON
			; -0------	; RX9 disabled
			; --X-----	; not used for async
			; ---1----	; receiver enabled
			; ----0---	; don't use address detection
			; -----0--	; framing error detected
			; ------0-	; overrun error detected
			; -------0	; bit 9 if used
		MOVWF	RCSTA, ACCESS
		MOVLW	b'00100100'
			; X-------	; Clock source (not used for async)
			; -0------	; TX9 disabled
			; --1-----	; transmitter enabled
			; ---0----	; asynchronous mode selected
			; ----0---	; not sending BREAK
			; -----1--	; high-speed baud rate
			; ------X- 	; TX buffer status (R/0)
			; -------0	; bit 9 if used
		MOVWF	TXSTA, ACCESS
		MOVLW	b'00001000'
			; 0-------	; auto-baud acquisition rollover status clear
			; -X------	; receive idle status
			; --XX-X--	; N/A
			; ----1---	; 16-bit baud rate (SPBRGH:SPBRG)
			; ------0-	; don't wake up on RX
			; -------0 	; don't detect baud rate
		MOVWF	BAUDCON, ACCESS
		SETF	FLASH_UPD_BLKH, ACCESS	; set block ID to FFFF (which is not
		SETF	FLASH_UPD_BLKL, ACCESS	; ever a valid ID)
;;;;; REMOVED ;;;;;;	MOVLW	0x2A
;;;;; REMOVED ;;;;;;	RCALL	FLASH_UPDATE_SEND		; status OOOO*
		;
		;       ||
		;      _||_
		;      \  /
		;	\/
		;
FLASH_UPDATE_NEXT_BLOCK:
;
; wait for next block from host.  This is where all the protocol stuff happens.
; Upon entering flash mode (including if the board resets in the middle), the
; board sends a 0x2A ('*') status response to the host.  If this is received, 
; the host should abandon the flash operation (if one was underway) and start over.
;
; These status response codes are five-byte sequences: bbbbs where bbbb is the
; current block ID, encoded the same way they are sent to us from the PC, or
; "OOOO" (i.e., 0xffff) if no block is currently defined, and s is the one-byte
; status code (like 0x2A for "ready").
;
;
; The board sends 0x2A ('*') when it boots and is ready for a block of data.
;
; The PC can send a block start or query command.
;	0x51 ('Q')	Query 		->
;					<-  OOOO*       Ready for 1st block transfer
;					<-  bbbb*       Ready for next block transfer
;
;       0x3e ('>')      Load block      ->
;					<-  bbbb*       Block burned successfully
;					<-  bbbbn       Block receive error
;					<-  bbbb!       Illegal target address
;					<-  bbbbb 	Block burn error
;					<-  bbbbv	Block verification error
;
; when aborted, ignores silently everything up to the next 'Q' or '>'.
;
; To burn a 64-byte block, the PC sends:
; 	0x3E ('>') + page<19:4> + 0x7C ('|') + <64 bytes> + checksum + '.'
;
; burning block 0 ends the firmware update process.
;
; bytes, incl checksum, are sent as two printable characters as <nybble> + 0x40, 
; i.e., @ABCDEFGHIJKLMNO
; for   0123456789ABCDEF
;
; so the 64-byte sequence 00 01 02 03 04 05 06 07 08 09 0A 0B 0C 0D 0E 0F
;                         10 11 12 13 14 15 16 17 18 19 1A 1B 1C 1D 1E 1F
;                         20 21 22 23 24 25 26 27 28 29 2A 2B 2C 2D 2E 2F
;                         30 31 32 33 34 35 36 37 38 39 3A 3B 3C 3D 3E 3F
; for block $010340-$01037F would be sent as:
;	Address $010340 -> $1034 (other bits implied) -> "A@CD"
;	>A@CD|@@@A@B@C@D@E@F@G@H@I@J@K@L@M@N@OA@AAABACADAEAFAGAHAIAJAKALAMANAOB@BABBBCBDBEBFBGBHBIBJBKBLBMBNBOC@CACBCCCDCECFCGCHCICJCKCLCMCNCOML.
;	Sum of address = $10 + $34 = $44
;	Sum of data    = $07E0    -> $E0
;	Total                      = $24 0010 0100
;	1-comp                     = $DB 1101 1011
;       2-comp                     = $DC 1101 1100 -> "ML"
;
; checksum is the 8-bit 2's compliment of the sum of the page address and data bytes

;                     A@CD
;                     1034
;              0001 0000 0011 0100
;
; TBLPTRU .... 0001
; TBLPTRH           0000 0011
; TBLPTRL                     01xx xxxx
; 
		CLRWDT
		CLRF	FLASH_UPD_CKS, ACCESS
		RCALL	FLASH_UPDATE_RECV
FLASH_UPD_GOT_BYTE:
		CLRF	FLASH_UPD_FLAG, ACCESS	; clear all flags at start: !FINAL, !ERROR, !FIRST
		MOVLW	0x51			; Q: query -> * 
		CPFSEQ	FLASH_UPD_INP, ACCESS
		BRA	FLASH_UPD_TRY_BLOCK
		MOVLW	0x2A
		RCALL	FLASH_UPDATE_SEND
		BRA	FLASH_UPDATE_NEXT_BLOCK
FLASH_UPD_TRY_BLOCK:
		MOVLW	0x3E			; >: start block load
		CPFSEQ	FLASH_UPD_INP, ACCESS
		BRA	FLASH_UPD_INVALID_CMD
		;
		; begin transfer of a block of data
		; 
		; target address: abcd|
		LFSR	FSR0, FLASH_UPD_BUF
		MOVLW	.2
		MOVWF	FLASH_UPD_I
		RCALL	FLASH_UPD_READ_BINARY_BLOCK
		BTFSC	FLASH_UPD_FLAG, FL_FL_ERROR, ACCESS
		BRA	FLASH_UPD_INVALID_DATA
		;
		; check sentinel byte
		;
		RCALL	FLASH_UPDATE_RECV
		MOVLW	0x7C			; '|' separates address from data
		CPFSEQ	FLASH_UPD_INP, ACCESS
		BRA	FLASH_UPD_INVALID_DATA
		;
		; set target address to TBLPTR; if it's block #0 this is our final one
		;
		BCF	FLASH_UPD_FLAG, FL_FL_FINAL, ACCESS
		MOVF	0x00, F, ACCESS
		BNZ	FLASH_UPD_TBNZ
		MOVF	0x01, F, ACCESS
		BNZ	FLASH_UPD_TBNZ
		BSF	FLASH_UPD_FLAG, FL_FL_FINAL, ACCESS
		;
		; $000  aaaabbbb )   TBLPTRU 0000aaaa	  16-bit block ID translated to
		; $001  ccccdddd )=> TBLPTRH bbbbcccc     20-bit FLASH ROM address aligned
		;                )   TBLPTRL dd000000     to 64-byte boundary
		;
FLASH_UPD_TBNZ:	SWAPF	0x00, W, ACCESS
		ANDLW	0x0F
		MOVWF	TBLPTRU, ACCESS			; U=0000aaaa H=XXXXXXXX L=XXXXXXXX
		SWAPF	0x00, W, ACCESS
		ANDLW	0xF0
		MOVWF	TBLPTRH, ACCESS			; U=0000aaaa H=bbbb0000 L=XXXXXXXX
		SWAPF	0x01, W, ACCESS
		ANDLW	0x0F
		IORWF	TBLPTRH, F, ACCESS		; U=0000aaaa H=bbbbcccc L=XXXXXXXX
		SWAPF	0x01, W, ACCESS
		ANDLW	0xC0
		MOVWF	TBLPTRL, ACCESS			; U=0000aaaa H=bbbbcccc L=dd000000
		;
		; sanity check that they didn't try to assign into a non-aligned block
		;
		MOVF	0x01, W, ACCESS
		ANDLW	0x3F
		BNZ	FLASH_UPD_INVALID_ADDRESS
		;
		; or if they want to overwrite the flash loader itself
		;
		MOVLW	UPPER(FLASH_UPDATE_LAST_BLK)
             	CPFSEQ	TBLPTRU, ACCESS
		BRA	FLASH_UPD_0ANE			; 0000aaaa != legal value, we're nearly done
		MOVLW	HIGH(FLASH_UPDATE_LAST_BLK)	; 0000aaaa == legal value, check next byte
		CPFSEQ	TBLPTRH, ACCESS			
		BRA	FLASH_UPD_BCNE			; bbbbcccc != legal value, we're nearly done
		MOVLW	LOW(FLASH_UPDATE_LAST_BLK)	; bbbbcccc == legal value too, check last byte
		CPFSEQ	TBLPTRL, ACCESS
		BRA	FLASH_UPD_D0NE			; dddd0000 != legal value, we're nearly done
		BRA	FLASH_UPD_A_OK			; all bytes == legal value, we're OK
FLASH_UPD_0ANE: CPFSGT	TBLPTRU, ACCESS	
		BRA	FLASH_UPD_A_OK			; 0000aaaa < legal value, we're OK
		BRA	FLASH_UPD_INVALID_ADDRESS	; 0000aaaa > legal value, abort
FLASH_UPD_BCNE: CPFSGT	TBLPTRH, ACCESS	
		BRA	FLASH_UPD_A_OK			; bbbbcccc < legal value, we're OK
		BRA	FLASH_UPD_INVALID_ADDRESS	; bbbbcccc > legal value, abort
FLASH_UPD_D0NE: CPFSGT	TBLPTRL, ACCESS	
		BRA	FLASH_UPD_A_OK			; dd000000 < legal value, we're OK
		BRA	FLASH_UPD_INVALID_ADDRESS	; dd000000 > legal value, abort
		;
		; Address OK, proceed...
		;
FLASH_UPD_A_OK:	CLRWDT
		LFSR	FSR0, FLASH_UPD_BUF
		MOVLW	.65
		MOVWF	FLASH_UPD_I, ACCESS		; read 65 more bytes (64+checksum)
		RCALL	FLASH_UPD_READ_BINARY_BLOCK
		BTFSC	FLASH_UPD_FLAG, FL_FL_ERROR, ACCESS
		BRA	FLASH_UPD_INVALID_DATA
		;
		; Check final sentinel byte
		;
		RCALL	FLASH_UPDATE_RECV
		MOVLW	'.'			; '.' terminates data
		CPFSEQ	FLASH_UPD_INP, ACCESS
		BRA	FLASH_UPD_INVALID_DATA
		;
		; Check computed checksum value (must be zero)
		;
		TSTFSZ	FLASH_UPD_CKS, ACCESS
		BRA	FLASH_UPD_INVALID_DATA
		;
		; Acknowledge receipt
		;
		MOVLW	'y'
		RCALL	FLASH_UPDATE_SEND
		;
		; Burn it now
		;
		RCALL	FLASH_UPD_BURN_BLOCK
		BTFSC	FLASH_UPD_FLAG, FL_FL_ERROR, ACCESS
		BRA	FLASH_UPD_EB
		MOVLW	'B'
		RCALL	FLASH_UPDATE_SEND
             	RCALL	FLASH_UPD_VERIFY_BLOCK
		BTFSC	FLASH_UPD_FLAG, FL_FL_ERROR, ACCESS
		BRA	FLASH_UPD_EV
		MOVLW	'V'
		RCALL	FLASH_UPDATE_SEND

FLASH_UPD_EB:	MOVLW	'b'
		BRA	FLASH_UPD_ERR
FLASH_UPD_EV:	MOVLW	'v'
		BRA	FLASH_UPD_ERR
		BTFSS	FLASH_UPD_FLAG, FL_FL_FINAL, ACCESS
		BRA	FLASH_UPDATE_NEXT_BLOCK
		;
		;       ||
		;      _||_
		;      \  /
		;	\/
		;

FLASH_UPDATE_END:
		CLRWDT
;
; Stop the download process.
; At this point, we have just written page zero with our new boot vector
; so all we need to do really is just reboot.
; (I was going to reset the boot vector here, but on second thought,
; that risks booting into a partially-burned--i.e., corrupt--firmware
; image, so once you start this process the only way out is to complete
; a download successfully.)
;
		RESET		; Go home.
		GOTO	0	; No, seriously, go.


FLASH_UPD_READ_BINARY_BLOCK:
; Read exactly FLASH_UPD_I bytes into memory at [FSR0+] by reading
; each nybble plus 0x40. On any error, set ERROR status and return
;
		TSTFSZ	FLASH_UPD_I, ACCESS			; if they asked for 0 bytes to be read
		BRA	FLASH_UPD_RBB0				; then we don't have much to do here.
		BCF	FLASH_UPD_FLAG, FL_FL_ERROR, ACCESS
		RETURN
FLASH_UPD_RBB0:	BSF	FLASH_UPD_FLAG, FL_FL_FIRST, ACCESS	; first nybble
FLASH_UPD_RBB:	CLRWDT
		RCALL	FLASH_UPDATE_RECV			; next byte
		; valid data bytes are 0x40~0x4F only
		MOVLW	0xF0
		ANDWF	FLASH_UPD_INP, W, ACCESS		; test for 0100xxxx
		MOVWF	FLASH_UPD_CMP, ACCESS
		MOVLW	0x40
		CPFSEQ	FLASH_UPD_CMP, ACCESS
		BRA	FLASH_UPD_INVALID_DATA
		; convert to actual nybble value
		MOVLW	0x0F
		ANDWF	FLASH_UPD_INP, F, ACCESS
		; move into RAM location
		BTFSS	FLASH_UPD_FLAG, FL_FL_FIRST, ACCESS
		BRA	FLASH_UPD_RBB2
		; first nybble: swap into high nybble of [FSR0]
		SWAPF	FLASH_UPD_INP, W, ACCESS
		MOVWF	INDF0, ACCESS
		BCF	FLASH_UPD_FLAG, FL_FL_FIRST, ACCESS
		BRA	FLASH_UPD_RBB
FLASH_UPD_RBB2:	CLRWDT
		; 2nd nybble: OR into low nybble of [FSR0+]
		MOVF	FLASH_UPD_INP, W, ACCESS
		IORWF	INDF0, F, ACCESS
		MOVF	POSTINC0, W, ACCESS
		ADDWF	FLASH_UPD_CKS, F, ACCESS
		DECFSZ	FLASH_UPD_I, F, ACCESS
		BRA	FLASH_UPD_RBB0
		BCF	FLASH_UPD_FLAG, FL_FL_ERROR, ACCESS
		RETURN

FLASH_UPD_INVALID_DATA:
		MOVLW	0x6E			; n: error
FLASH_UPD_E_AB:	RCALL	FLASH_UPDATE_SEND
		RCALL	FLASH_UPD_ABORT
		BRA	FLASH_UPD_GOT_BYTE

FLASH_UPD_INVALID_ADDRESS:
		MOVLW	0x21			; !: error
		BRA	FLASH_UPD_E_AB

FLASH_UPD_INVALID_CMD:
		MOVLW	0x6E			; n: error
FLASH_UPD_ERR:	RCALL	FLASH_UPDATE_SEND
		BRA	FLASH_UPDATE_NEXT_BLOCK

FLASH_UPDATE_SEND:
;
; Send a status respose to the serial port.  This is the encoded block ID and
; the byte in W.
;
		CLRWDT
		IF HAS_T_R
		 RCALL	FLASH_UPD_PAUSE
		 BSF 	PLAT_T_R, BIT_T_R, ACCESS
		 RCALL	FLASH_UPD_PAUSE
		ENDIF
		MOVWF	FLASH_UPD_X, ACCESS	; store the status byte until we're ready for it
		SWAPF	FLASH_UPD_BLKH, W, ACCESS ; send blk id aaaabbbbccccdd000000
		ANDLW	0x0f			  ;             ^^^^
		IORLW	0x40
		RCALL	FLASH_UPD_TX_W
		MOVF	FLASH_UPD_BLKH, W, ACCESS ; send blk id aaaabbbbccccdd000000
		ANDLW	0x0f			  ;                 ^^^^
		IORLW	0x40
		RCALL	FLASH_UPD_TX_W
		SWAPF	FLASH_UPD_BLKL, W, ACCESS ; send blk id aaaabbbbccccdd000000
		ANDLW	0x0f			  ;                     ^^^^
		IORLW	0x40
		RCALL	FLASH_UPD_TX_W
		MOVF	FLASH_UPD_BLKL, W, ACCESS ; send blk id aaaabbbbccccdd000000
		ANDLW	0x0f			  ;                         ^^^^
		IORLW	0x40
		RCALL	FLASH_UPD_TX_W
		MOVF	FLASH_UPD_X, W, ACCESS	  ; send status byte
		RCALL	FLASH_UPD_TX_W
		IF HAS_T_R
		 RCALL	FLASH_UPD_PAUSE
		 BCF	PLAT_T_R, BIT_T_R, ACCESS
		 RCALL	FLASH_UPD_PAUSE
		ENDIF
		RETURN

FLASH_UPD_TX_W:
FLASH_UPD_TXRDY	CLRWDT
		BTFSS	PIR1, TXIF, ACCESS	; wait for transmitter ready
		BRA	FLASH_UPD_TXRDY
		MOVWF	TXREG, ACCESS		; send byte in W to serial port
FLASH_UPD_RDY2:	CLRWDT
		BTFSS	PIR1, TXIF, ACCESS	; wait for transmitter ready again
		BRA	FLASH_UPD_RDY2
FLASH_UPD_RDY3: CLRWDT
		BTFSS	TXSTA, TRMT, ACCESS	; wait for character to fully leave serial port
		BRA	FLASH_UPD_RDY3
		RETURN

FLASH_UPDATE_RECV:
		CLRWDT
		BTFSS	RCSTA, FERR, ACCESS
		BRA	FLASH_UPD_RC1
		; framing error
		; (ignore)
FLASH_UPD_RC1:	BTFSS	RCSTA, OERR, ACCESS
		BRA	FLASH_UPD_RC2
		; overrun error
		BCF	RCSTA, CREN, ACCESS	; reset serial receiver
		BSF	RCSTA, CREN, ACCESS
		MOVLW	0x6E
		RCALL	FLASH_UPDATE_SEND
		BRA	FLASH_UPD_ABORT
FLASH_UPD_RC2: 	BTFSS	PIR1, RCIF, ACCESS	; wait for charater to arrive
		BRA	FLASH_UPDATE_RECV
		MOVFF	RCREG, FLASH_UPD_INP
		RETURN

FLASH_UPD_PAUSE:					; Delay 1,025 uS (~1mS)
		SETF	FLASH_UPD_DLY, ACCESS		; 1
FLASH_UPD_P_L:	CLRWDT					; 1 \
		DECFSZ	FLASH_UPD_DLY, F, ACCESS	; 1 | x 255   +1
		BRA	FLASH_UPD_P_L			; 2 /	      +1
		RETURN                                  ;             +2

FLASH_UPD_ABORT:
		; arrange to ignore everything until next Q or > received
		RCALL	FLASH_UPDATE_RECV
		MOVLW	0x51				; 'Q' received?
		CPFSEQ	FLASH_UPD_INP, ACCESS
		BRA	FLASH_UPD_AB1			; no, check for '>'
		RETURN					; yes, return 
FLASH_UPD_AB1:	MOVLW	0x3E				; '>' received?
		CPFSEQ	FLASH_UPD_INP, ACCESS
		BRA	FLASH_UPD_ABORT			; no, loop back to wait for next char
		RETURN					; yes, return

		END
