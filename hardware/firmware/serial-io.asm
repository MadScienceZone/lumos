; vim:set syntax=pic ts=8:
		LIST n=90
;@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
;@@                                                                         @@
;@@                                                                         @@
;@@  @@@   @@@@@  @@@@   @@@   @@@   @              @@@      @   @@@        @@
;@@ @   @  @      @   @   @   @   @  @               @       @  @   @       @@
;@@ @      @      @   @   @   @   @  @               @      @   @   @       @@
;@@  @@@   @@@@   @@@@    @   @@@@@  @      @@@@@    @     @    @   @       @@
;@@     @  @      @ @     @   @   @  @               @    @     @   @       @@
;@@ @   @  @      @  @    @   @   @  @               @   @      @   @       @@
;@@  @@@   @@@@@  @   @  @@@  @   @  @@@@@          @@@  @       @@@        @@
;@@                                                                         @@
;@@ Copyright (c) 2012 by Steven L. Willoughby, Aloha, Oregon, USA.  All    @@
;@@ Rights Reserved.                                                        @@
;@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
;
; Portions based on earlier code copyright (c) 2004, 2005, 2006, 2007, 2008, 
; 2009, Steven L. Willoughby, Aloha, Oregon, USA.  All Rights Reserved.
;
; General serial console I/O handling
; This module manages the TXIE interrupt masks as needed
;
	RADIX		DEC
; 
;==============================================================================
; PUBLIC ENTRY POINTS
;==============================================================================
;	SIO_INIT	Initialize module (call this once first)
;
#include "serial-io-bits.inc"
#ifndef LUMOS_ARCH
	ERROR "Architecture not configured"
#endif

;==============================================================================
; REGISTERS USED
;==============================================================================
;
;                    bit 7      6      5      4      3      2      1      0
;                     _______________________________________________________
; $F9D PIE1          |      |      |      |      |      |      |      |      |
;                    |      |      | RCIE | TXIE |      |      |      |      |
;                    |______|______|______|______|______|______|______|______|
; $F9E PIR1          |      |      |      |      |      |      |      |      |
;                    |      |      | RXIF | TXIF |      |      |      |      |
;                    |______|______|______|______|______|______|______|______|
; $F9F IPR1          |      |      |      |      |      |      |      |      |
;                    |      |      | RXIP | TXIP |      |      |      |      |
;                    |______|______|______|______|______|______|______|______|
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
; Three memory banks are used: one for each of the data buffers, and a third
; for the variables used by this module.
;	
;                    bit 7      6      5      4      3      2      1      0
;                     _______________________________________________________
; +$00 SIO_STATUS    |      |      |SIO_  |SIO_  |RXDATA|TXDATA|RXDATA|TXDATA|
;                    |      |      | FERR | ORUN |_FULL |_FULL |_QUEUE|_QUEUE|
;                    |______|______|______|______|______|______|______|______|
; +$01 SIO_INPUT     |                                                       |
;                    | Character last read from serial port                  |
;                    |______|______|______|______|______|______|______|______|
; +$02 SIO_OUTPUT    |                                                       |
;                    | Character last written to serial port                 |
;                    |______|______|______|______|______|______|______|______|
; +$03 TX_BUF_START  |                                                       |
;                    | Pointer into TX_BUFFER at NEXT char to be transmitted |
;                    |______|______|______|______|______|______|______|______|
; +$04 TX_BUF_END    |                                                       |
;                    | Pointer into TX_BUFFER where next char will be stored |
;                    |______|______|______|______|______|______|______|______|
; +$05 RX_BUF_START  |                                                       |
;                    | Pointer into RX_BUFFER at NEXT char to be transmitted |
;                    |______|______|______|______|______|______|______|______|
; +$06 RX_BUF_END    |                                                       |
;                    | Pointer into RX_BUFFER where next char will be stored |
;                    |______|______|______|______|______|______|______|______|
; +$07 TX_CHAR       |                                                       |
;                    | Temporary storage for character being output.         |
;                    |______|______|______|______|______|______|______|______|
; +$08 SIO_X         |                                                       |
;                    | Temporary storage register                            |
;                    |______|______|______|______|______|______|______|______|
; +$09 FSR1H_SAVE    |///////////////////////////|Temp store for high-order  |
;                    |///////////////////////////|bits of caller's FSR1 ptr  |
;                    |///////////////////////////|______|______|______|______|
; +$0A FSR1L_SAVE    |                                                       |
;                    | Temporary storage for low-order bits of caller's FSR1 |
;                    |______|______|______|______|______|______|______|______|
; +$0B B32__BCD_ASC  | 5-byte BCD output buffer      10-byte ASCII output    |
; +$0C               | for binary-to-BCD conv.  ---> buffer for binary or    |
; +$0D               | Also input to BCD to ASCII    BCD to ASCII conversions|
; +$0E               | conversion.           /|\               |             |
; +$0F               |........................|.               |             |
; +$10 B32__BIN      | 4-byte binary input    |                |             |
; +$11               | for bin-to-BCD conversion               |             |
; +$12               |                                         |             |
; +$13               |                                         |             |
; +$14               |////////////////////////////______|______V______|______|
;
;
;

_SIO_TXBUF_DATA	UDATA	SIO_TX_BUFFER_START
TX_BUFFER:
	RES .256

_SIO_RXBUF_DATA	UDATA	SIO_RX_BUFFER_START
RX_BUFFER:
	RES .256

_SIO_VAR_DATA	UDATA	SIO_DATA_START
	GLOBAL	SIO_STATUS	; export this out to other modules
	GLOBAL	SIO_INPUT, SIO_OUTPUT
	GLOBAL	B32__BIN, B32__BCD_ASC

SIO_STATUS	RES	1	; SIO module general status bits
SIO_INPUT	RES	1	; external buffer to receive Rx byte
SIO_OUTPUT	RES	1	; external buffer to send Tx byte
TX_BUF_START	RES	1	; Pointer to start of Tx ring buffer
TX_BUF_END	RES	1	; Pointer to end of Tx ring buffer
RX_BUF_START	RES	1	; Pointer to start of Tx ring buffer
RX_BUF_END	RES	1	; Pointer to end of Tx ring buffer
TX_CHAR		RES	1	; Holding area for character on its way out
SIO_X		RES	1	; Temporary variable
SIO_TMPPC	RES	1	; Temporary to read PC to latch it
FSR1H_SAVE	RES	1	; Storage for caller's FSR1H value
FSR1L_SAVE	RES	1	; Storage for caller's FSR1L value
B32__BIT	RES	1	; Current bit being converted
B32__OUTCTR	RES	1	; Output counter
B32__FSR0H	RES	1	; Temporary FSR0H storage
B32__FSR0L	RES	1	; Temporary FSR0L storage
B32__FSR1H	RES	1	; Temporary FSR1H storage
B32__FSR1L	RES	1	; Temporary FSR1L storage
B32__BCD_ASC	RES	5	; Storage for BCD conversion routines
B32__BIN	RES	4	; **MUST** follow B32__BCD_ASC
;                      --
;                      27       ; ***DO NOT ADD MORE*** without checking
; 				; elsewhere; on some small chips we have
;				; had to locate this in tiny corners of RAM.

;==============================================================================
;
; The baud rate calculations are:
; low-speed   8-bit (BRG16=0, BRGH=0) is Fosc/[64(n+1)]
; high-speed  8-bit (BRG16=0, BRGH=1) is Fosc/[16(n+1)]
; low-speed  16-bit (BRG16=1, BRGH=0) is Fosc/[16(n+1)]
; high-speed 16-bit (BRG16=1, BRGH=1) is Fosc/[4(n+1)]
;
; for desired baud rate of b,
;	X = [((Fosc/b)/d)-1]	(d is multiplier above; e.g. 64 in first case)
;	X goes into SPBRG (or SPBRGH:SPBRG if 16 bit)
;	error = (Fosc/d(X+1) - b) / b
;
;
; Operational notes
;
; Sending:
;	When TXIF is set, TXREG is ready to accept another byte
;	data byte written to TXREG and is sent out the port
;	TRMT bit is clear while byte is sent, then set when it's done.
; Receiving:
;	When a byte is received, RXIF is set
;	RCSTA will alert to errors and holds bit 9 if used
;	RCREG holds the received byte
;	if error, clear CREN to clear error state
;	clear RXIF to acknowledge receipt
;
; The Tx and Rx buffers are 256-byte ring buffers each in a single
; RAM page.  The 8-bit pointers that index them are assumed to wrap
; around naturally to create the ring buffer effect.  Changing the
; buffer sizes will require recoding the pointer arithmetic.
;
; In each case, the buffer has two pointers: START, which points to the
; next character to be read out of the buffer, and END, which points to
; the location where the next character will be written into the buffer.
;
;   BUFFER   Q 
; [________] 0 If START=END, the buffer is empty.  If the QUEUE flag is
;  ^           clear, this means the buffer is empty, as opposed to the
;  ^           case where the pointers wrap around to be equal again,
;              but QUEUE is set (meaning buffer is full).
; [H_______] 1 Pushing "H" into the buffer means writing it to [E++],
;  ^^          so E points to the next available location.
;  SE
;
; [HELLO___] 1 Pushing "ELLO" continues...
;  ^    ^
;  S    E
;
; [__LLO___] 1 Pulling two bytes from the buffer meas reading from [S++].
;    ^  ^      (The buffer really still contains [HELLO___] but since the
;    S  E      pointer's moved on, we're ignoring the "HE" we read and those
;              bytes will be overwritten later.)
; [O_LLO, W] 1 Pushing ", WO" illustrates how we wrap around in the ring
;   ^^         buffer, so no matter where we're reading/writing there is
;   ES         always the same maximum available buffer space.
;
; [ORLLO, W] 1 Pushing one more byte fills the buffer (START=END), so we
;    ^         won't allow more writes until some more is read.
;    ^
;
; [OR____ W] 1 Reading more, leaves more room...
;    ^   ^
;    E   S
;
; [ORLD!_ W] 1 for more data...
;       ^^
;       ES
;
; [________] 0 reading it back to empty leaves it like this.  It's ready
;       ^      regardless of where in the buffer the pointers are located.
;       ^      the QUEUE flag is cleared to indicate no data are queued.
;


_SIO_CODE CODE
	GLOBAL	SIO_INIT
	GLOBAL	SIO_ECHO
	GLOBAL	SIO_ECHO_W
	GLOBAL	SIO_WRITE
	GLOBAL	SIO_WRITE_W
	GLOBAL	SIO_PUTCHAR
	GLOBAL	SIO_PUTCHAR_W
	GLOBAL	SIO_RECV
	GLOBAL	SIO_SEND
	GLOBAL	SIO_NEWLINE
	GLOBAL	SIO_GETCHAR
	GLOBAL	SIO_GETCHAR_W
	GLOBAL	SIO_READ
	GLOBAL	SIO_READ_W
	GLOBAL	SIO_PRINT_HEX
	GLOBAL	SIO_PRINT_HEX_W
	GLOBAL	SIO_SET_BAUD_W
	GLOBAL	SIO_FLUSH_INPUT
	GLOBAL	SIO_FLUSH_OUTPUT
	GLOBAL	B32__BIN2BCD
	GLOBAL	B32__BCD2ASCII
;
;==============================================================================
; SIO_INIT 
;
; Set up the USART for serial communications.
; The following global symbols need to be exported by the caller:
;	SIO_RX_BUFFER_START*	Starting addr of 256-byte Rx buffer
;	SIO_TX_BUFFER_START*	Starting addr of 256-byte Tx buffer
;	SIO_DATA_START		Starting addr of SIO module variables
;
; *must be aligned to the start of a 256-byte RAM bank
;
; AFFECTS:	RAM data bank
;	
;==============================================================================

	IF SIO_RX_BUFFER_START & 0xFF
		ERROR "SIO_RX_BUFFER_START must be on a 256-byte RAM boundary."
	ENDIF

	IF SIO_TX_BUFFER_START & 0xFF
		ERROR "SIO_TX_BUFFER_START must be on a 256-byte RAM boundary."
	ENDIF
	
SIO_INIT:
	CLRWDT
	BANKSEL	SIO_DATA_START
;
; Set up I/O pins
;
        IF LUMOS_ARCH == LUMOS_ARCH_14K50
	 BSF	TRISB, 5, ACCESS	; RX pin on PORTB<5>
	 BCF	TRISB, 7, ACCESS	; TX pin on PORTB<7>
	ELSE
	 BSF	TRISC, 7, ACCESS	; RX pin on PORTC<7>
	 BCF	TRISC, 6, ACCESS	; TX pin on PORTC<6>
	ENDIF
;
; Set up EUSART for asynchronous serial I/O
;
; STEP 1. Set baud rate to SPBRGH:SPBRG
;
	MOVLW	SIO_19200		; default baud rate is 19.2k
	CALL	SIO_SET_BAUD_W
;
; STEP 2. Set up Tx/Rx buffers and other variables.
;
	;
	; Zero buffer contents (probably unnecessary, but I'm a purist)
	;
	BANKSEL	TX_BUFFER
	CLRWDT
	LFSR	FSR0, TX_BUFFER
CLR_NEXT_TX:
	CLRF	POSTINC0
	TSTFSZ	FSR0L, ACCESS
	BRA	CLR_NEXT_TX
	
	BANKSEL	RX_BUFFER
	CLRWDT
	LFSR	FSR0, RX_BUFFER
CLR_NEXT_RX:
	CLRF	POSTINC0
	TSTFSZ	FSR0L, ACCESS
	BRA	CLR_NEXT_RX
	;
	; Initialize buffer pointers and status register
	;
	BANKSEL	SIO_DATA_START
	CLRF	SIO_STATUS, BANKED	; all status bits default to cleared
	CLRF	TX_BUF_START		; set start and end buffer pointers at
	CLRF	TX_BUF_END		; start of buffer (==buffer empty)
	CLRF	RX_BUF_START
	CLRF	RX_BUF_END
;
; STEP 3. Enable port and set modes.
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
;
; STEP 4. Enable interrupts (DOES NOT enable global interrupts; that is
;         assumed to be under the caller's control)
;
	RETURN

;==============================================================================
; PUBLIC ENTRY POINTS FOR I/O
;==============================================================================
;
SIO_FLUSH_INPUT:
	BANKSEL	SIO_DATA_START
	CLRF	SIO_X, BANKED
	BTFSS	PIE1, RCIE, ACCESS
	BRA	SIO_FLUSH_IN_1
	BCF	PIE1, RCIE, ACCESS	; turn off interrupts
	BSF	SIO_X, 0, BANKED	; remember to enable interrupts again
SIO_FLUSH_IN_1:
	CLRF	RX_BUF_START, BANKED
	CLRF	RX_BUF_END, BANKED
	BCF 	SIO_STATUS, RXDATA_FULL, BANKED
	BCF 	SIO_STATUS, RXDATA_QUEUE, BANKED
	BTFSC	SIO_X, 0, BANKED
	BSF	PIE1, RCIE, ACCESS	; turn interrupt back on if set initially
	RETURN

SIO_FLUSH_OUTPUT:
	BANKSEL	SIO_DATA_START
	CLRF	SIO_X, BANKED
	BTFSS	PIE1, TXIE, ACCESS
	BRA	SIO_FLUSH_OUT_1
	BCF	PIE1, TXIE, ACCESS	; turn off interrupts
	BSF	SIO_X, 0, BANKED	; remember to enable interrupts again
SIO_FLUSH_OUT_1:
	CLRF	TX_BUF_START, BANKED
	CLRF	TX_BUF_END, BANKED
	BCF     SIO_STATUS, TXDATA_FULL, BANKED
	BCF     SIO_STATUS, TXDATA_QUEUE, BANKED
	BTFSC	SIO_X, 0, BANKED
	BSF	PIE1, TXIE, ACCESS	; turn interrupt back on if set initially
	RETURN

SIO_SET_BAUD_W:
	BANKSEL	SIO_DATA_START
	CLRWDT
	MOVWF	SIO_X, BANKED
	CALL	BAUDTBLH
	MOVWF	SPBRGH, ACCESS
	MOVF	SIO_X, W, BANKED
	CALL	BAUDTBLL
	MOVWF	SPBRG, ACCESS
	RETURN

SIO_ECHO_W:
	BANKSEL	SIO_DATA_START
	MOVWF	SIO_OUTPUT, BANKED
SIO_ECHO:
	CLRWDT
	BANKSEL	SIO_DATA_START
	BTFSS	SIO_OUTPUT, 7, BANKED	; is char 7-bit clean?
	BRA	ECHO_7BITS		; yes: skip this next bit
	MOVLW	'M'			
	RCALL	SIO_PUTCHAR_W		; output "M-" then the stripped char
	MOVLW	'-'
	RCALL	SIO_PUTCHAR_W
	BCF	SIO_OUTPUT, 7, BANKED	; strip high bit
ECHO_7BITS:
	MOVLW	0x7F			; is the character DELETE?
	CPFSEQ	SIO_OUTPUT, BANKED
	BRA	ECHO_NOT_DELETE		; no: go on to next test
	MOVLW	'^'			; yes: print as "^?"
	RCALL	SIO_PUTCHAR_W
	MOVLW	'?'
	MOVWF	SIO_OUTPUT, BANKED
ECHO_NOT_DELETE:
	MOVLW	0x1B			; is the character ESCAPE?
	CPFSEQ	SIO_OUTPUT, BANKED
	BRA	ECHO_NOT_ESCAPE		; no: go on...
	MOVLW	'$'
	MOVWF	SIO_OUTPUT, BANKED	; yes: print as "$"
ECHO_NOT_ESCAPE:
	BTFSS	SIO_OUTPUT, 6, BANKED	; is it a control character?
	BTFSC	SIO_OUTPUT, 5, BANKED	; (i.e., bits <7:5>=000)
	BRA	ECHO_PLAIN		; no: print normally
	MOVLW	'^'
	RCALL	SIO_PUTCHAR_W		; yes: print as "^<char>"
	BSF	SIO_OUTPUT, 6, BANKED	; set bit 6 to shift to upper-case char
ECHO_PLAIN:
	MOVF	SIO_OUTPUT, W, BANKED	; pick up final character to print
	RCALL	SIO_PUTCHAR_W		; and output it.
	RETURN

SIO_PUTCHAR:
	BANKSEL	SIO_DATA_START
	MOVF	SIO_OUTPUT, W, BANKED

SIO_PUTCHAR_W:
	CLRWDT					
	BANKSEL	SIO_DATA_START
	MOVWF	TX_CHAR, BANKED			

SPIN_FOR_BUF_DRAIN:
	BTFSS	SIO_STATUS, TXDATA_QUEUE, BANKED; Check to see if buffer full
	BRA	WRITE_OK			; OK because it's totally empty
	MOVF	TX_BUF_START, W, BANKED		; Next check for START==END
	CPFSEQ	TX_BUF_END, BANKED
	BRA	WRITE_OK			; START != END, so we're good.
	BRA	SPIN_FOR_BUF_DRAIN		; loop back until buffer not full

SIO_WRITE:
	BANKSEL	SIO_DATA_START
	MOVF	SIO_OUTPUT, W, BANKED

SIO_WRITE_W:
	CLRWDT					
	BANKSEL	SIO_DATA_START
	MOVWF	TX_CHAR, BANKED			
	BTFSS	SIO_STATUS, TXDATA_QUEUE, BANKED; Check to see if buffer full
	BRA	WRITE_OK			; OK because it's totally empty
	MOVF	TX_BUF_START, W, BANKED		; Next check for START==END
	CPFSEQ	TX_BUF_END, BANKED
	BRA	WRITE_OK			; START != END, so we're good.
	BSF	SIO_STATUS, TXDATA_FULL, BANKED	; flag buffer as full and give up
	RETURN
	
WRITE_OK:					; OK to write byte into next slot in the buffer
	MOVFF	TX_BUF_END, FSR1L 		; load buffer pointer
	MOVLW	HIGH(TX_BUFFER)
	MOVWF	FSR1H, ACCESS
	MOVFF	TX_CHAR, INDF1			; move character into Tx buffer
	BSF	SIO_STATUS, TXDATA_QUEUE, BANKED; flag that data are in the buffer now
	INCF	TX_BUF_END, F, BANKED		; increment pointer (will wrap around)
	BSF	PIE1, TXIE, ACCESS		; enable TX interrupt to send to H/W
	RETURN

SIO_NEWLINE:
	CLRWDT
	MOVLW	0x0D
	RCALL	SIO_PUTCHAR_W
	MOVLW	0x0A
	RCALL	SIO_PUTCHAR_W
	RETURN


SIO_READ_W:
	RCALL	SIO_READ
	MOVF	SIO_INPUT, W, BANKED
	RETURN

SIO_READ:
	CLRWDT
	BANKSEL	SIO_DATA_START
	BTFSC	SIO_STATUS, RXDATA_QUEUE, BANKED; Is data waiting to be read?
	BRA	READ_OK				; yes, branch down to handle it
	CLRF	SIO_INPUT, BANKED		; no, return zero
	RETURN

READ_OK:					; get next byte out of buffer
	MOVFF	RX_BUF_START, FSR1L 		; load buffer pointer
	MOVLW	HIGH(RX_BUFFER)
	MOVWF	FSR1H, ACCESS
	MOVFF	INDF1, SIO_INPUT		; retrieve byte at start of buffer
	INCF	RX_BUF_START, F, BANKED		; advance pointer (will wrap around)
	MOVF	RX_BUF_START, W, BANKED		; have we run out of data? (start == end)
	CPFSEQ	RX_BUF_END, BANKED
	BRA	READ_DONE			; no, leave everything alone for next time
	BCF	SIO_STATUS, RXDATA_QUEUE, BANKED; yes, clear the queue bit (buffer empty)
READ_DONE:
	RETURN

SIO_GETCHAR_W:
	RCALL	SIO_GETCHAR
	MOVF	SIO_INPUT, W, BANKED
	RETURN

SIO_GETCHAR:
	BANKSEL	SIO_DATA_START
GC_SPIN	CLRWDT
	BTFSS	SIO_STATUS, RXDATA_QUEUE, BANKED; wait here until data arrives
	BRA	GC_SPIN
	BRA	SIO_READ

;==============================================================================
; HIGHER LEVEL I/O FUNCIONS
;==============================================================================
;
; SIO_PRINT_HEX		Print value in SIO_OUTPUT as 2-digit hex value
; SIO_PRINT_HEX_W	Convenience function to take value from W (->SIO_OUTPUT)
;
SIO_PRINT_HEX_W:
	BANKSEL	SIO_DATA_START
	MOVWF	SIO_OUTPUT, BANKED

SIO_PRINT_HEX:
	CLRWDT
	BANKSEL	SIO_DATA_START
	MOVFF	SIO_OUTPUT, SIO_X	; Move value aside (we'll need SIO_OUTPUT)
	SWAPF	SIO_X, W, BANKED	; Get first nybble
	CALL	HEXTBL			; Convert to ASCII character in W
	CALL	SIO_PUTCHAR_W		; and print
	MOVF	SIO_X, W, BANKED	; Get last nybble
	CALL	HEXTBL			;
	CALL	SIO_PUTCHAR_W		;
	RETURN

;
; 32-bit BCD and ASCII conversion routines
; derived (and then ported to PIC18 and modified by Steve Willoughby)
; from Microchip app note AN526 + modifications by Mike Keitz and
; Ron Kreymborg.  Contributed to the PIC developer community (PICList)
;
; B32__BIN2BCD	 Convert 32-bit int to 10-digit BCD.
;	INPUT:	B32__BIN
;	OUTPUT: B32__BCD_ASC
;
B32__BIN2BCD:
	BANKSEL	SIO_DATA_START
	CLRWDT
	MOVLW	.32			; bits to convert
	MOVWF	B32__BIT, BANKED	; cycle counter
	CLRF	B32__BCD_ASC
	CLRF	B32__BCD_ASC+1
	CLRF	B32__BCD_ASC+2
	CLRF	B32__BCD_ASC+3
	CLRF	B32__BCD_ASC+4
	MOVFF	FSR0H, B32__FSR0H
	MOVFF	FSR0L, B32__FSR0L

B32__B2BCD_BIT:
	LFSR	FSR0, B32__BCD_ASC
	MOVLW	.5
	MOVWF	B32__OUTCTR, BANKED
	
B32__B2BCD_LOOP:
	CLRWDT
	MOVLW	0x33
	ADDWF	INDF0, F
	BTFSC	INDF0, 3		; low result > 7?
	ANDLW	0xF0			; yes: take 3 out
	BTFSC	INDF0, 7		; high result > 7?
	ANDLW	0x0F			; yes
	SUBWF	POSTINC0, F		; results <=7, subtract back
	DECFSZ	B32__OUTCTR, F, BANKED	
	BRA	B32__B2BCD_LOOP
	; 
	; Get another bit by shifting the whole 32-bit value one bit to the left
	; by cascading 8-bit shifts via carry (carry carries the bit across between
	; them).
	;                                   BIN[0]   BIN[1]   BIN[2]   BIN[3]
	;                                  @bcdefgh ijklmnop qrstuvwx yzABCDEF
	RLCF	B32__BIN+3, F, BANKED	 ; @bcdefgh ijklmnop qrstuvwxyzABCDEF?
	RLCF	B32__BIN+2, F, BANKED	 ; @bcdefgh ijklmnopqrstuvwxy zABCDEF?
	RLCF	B32__BIN+1, F, BANKED	 ; @bcdefghijklmnopq rstuvwxy zABCDEF?
	RLCF	B32__BIN+0, F, BANKED	 ;@bcdefghi jklmnopq rstuvwxy zABCDEF?
	;                                 |____________________________________________
	;                                                                              |
	;                                   BCD[0]   BCD[1]   BCD[2]   BCD[3]   BCD[4] V
	;                                  abcdefgh ijklmnop qrstuvwx yzABCDEF GHIJKLMN@
	RLCF	B32__BCD_ASC+4, F, BANKED; abcdefgh ijklmnop qrstuvwx yzABCDEFGHIJKLMN@
	RLCF	B32__BCD_ASC+3, F, BANKED; abcdefgh ijklmnop qrstuvwxyzABCDEFG HIJKLMN@
	RLCF	B32__BCD_ASC+2, F, BANKED; abcdefgh ijklmnopqrstuvwxy zABCDEFG HIJKLMN@
	RLCF	B32__BCD_ASC+1, F, BANKED; abcdefghijklmnopq rstuvwxy zABCDEFG HIJKLMN@
	RLCF	B32__BCD_ASC+0, F, BANKED;abcdefghi jklmnopq rstuvwxy zABCDEFG HIJKLMN@
	;                                  bcdefghi jklmnopq rstuvwxy zABCDEFG HIJKLMN@
	DECFSZ	B32__BIT, F, BANKED
	BRA	B32__B2BCD_BIT
	MOVFF	B32__FSR0H, FSR0H
	MOVFF	B32__FSR0L, FSR0L
	RETURN
	
;
; B32__BCD2ASCII
;
; Convert 10-digit BCD (in 5 bytes) to 10-character ASCII
; string
;
; buffer at B32__BCD_ASC:
;     ______________
;   0|BCD0      ASC0|  Modified in place
;   1|BCD1      ASC1|
;   2|BCD2 ---> ASC2|          /|\
;   3|BCD3      ASC3|           |
;   4|BCD4      ASC4| <-- SRC pointer FSR0
;   5|          ASC5|
;   6|          ASC6|
;   7|          ASC7|          /|\
;   8|          ASC8|           |
;   9|__________ASC9| <-- DST pointer FSR1
; 
;
B32__BCD2ASCII:
	CLRWDT
	BANKSEL	SIO_DATA_START
	MOVFF	FSR0H, B32__FSR0H		; Save old FSR values
	MOVFF	FSR0L, B32__FSR0L
	MOVFF	FSR1H, B32__FSR1H
	MOVFF	FSR1L, B32__FSR1L
	LFSR	FSR0, B32__BCD_ASC+4		; Set data pointers (src)
	LFSR	FSR1, B32__BCD_ASC+9		; (dst)
	
	
	
	MOVLW	.5
	MOVWF	B32__OUTCTR, BANKED

B32__BCD2A_LOOP:
	MOVF	INDF0, W			; least significant digit
	ANDLW	0x0F
	ADDLW	'0'
	MOVWF	POSTDEC1
	SWAPF	POSTDEC0, W			; most significant digit
	ANDLW	0x0F
	ADDLW	'0'
	MOVWF	POSTDEC1
	DECFSZ	B32__OUTCTR, F, BANKED
	BRA	B32__BCD2A_LOOP
	MOVFF	B32__FSR0H, FSR0H		; Restore old FSR values
	MOVFF	B32__FSR0L, FSR0L
	MOVFF	B32__FSR1H, FSR1H
	MOVFF	B32__FSR1L, FSR1L
	RETURN
	



	

;==============================================================================
; LOW-LEVEL I/O
;
; These are generally called from interrupt service routines to handle the
; passing of data bytes between the buffers and the serial transceiver 
; hardware.
;
; SIO_RECV	Call this when you know there's a byte waiting to be read in
;		from the USART.
; SIO_SEND	Call this when you know there's a byte that needs to be sent
;		to the USART and it's ready to send it.
;
;==============================================================================

SIO_SEND:
	CLRWDT
	BANKSEL	SIO_DATA_START
	BTFSC	SIO_STATUS, TXDATA_QUEUE, BANKED; Is data waiting to go out?
	BRA	TX_OK				; yes, branch down to handle it
	BCF	PIE1, TXIE, ACCESS		; no, block TX interrupt until needed again
	RETURN

TX_OK:						; push next byte out of buffer
	MOVFF	FSR1H, FSR1H_SAVE		; save pointer (remember we're an ISR here)
	MOVFF	FSR1L, FSR1L_SAVE
	MOVFF	TX_BUF_START, FSR1L 		; load buffer pointer
	MOVLW	HIGH(TX_BUFFER)
	MOVWF	FSR1H, ACCESS
	MOVFF	INDF1, TXREG			; transmit byte at buffer position
	INCF	TX_BUF_START, F, BANKED		; advance pointer (will wrap around)
	MOVF	TX_BUF_START, W, BANKED		; have we run out of data? (start == end)
	CPFSEQ	TX_BUF_END, BANKED
	BRA	TX_DONE				; no, leave everything alone for next time
	BCF	SIO_STATUS, TXDATA_QUEUE, BANKED; yes, clear the queue bit (buffer empty)
TX_DONE:
	MOVFF	FSR1H_SAVE, FSR1H		; restore saved registers
	MOVFF	FSR1L_SAVE, FSR1L
	RETURN

SIO_RECV:
	CLRWDT
	BANKSEL	SIO_DATA_START
	BTFSC	RCSTA, FERR, ACCESS		; Framing error?
	RCALL	ERR_FRAMING			; yes: go handle it.
	BTFSC	RCSTA, OERR, ACCESS		; Overrun error?
	RCALL	ERR_OVERRUN			; yes: go handle that.
	BTFSS	SIO_STATUS, RXDATA_QUEUE, BANKED; Is there data already in the buffer?
	BRA	RX_OK				; no: go ahead and write into empty buffer
	MOVF	RX_BUF_START, W, BANKED		; check for buffer full condition:
	CPFSEQ	RX_BUF_END, BANKED		;   buf not empty but start==end
	BRA	RX_OK				; not full yet: go ahead and write
	BSF	SIO_STATUS, RXDATA_FULL, BANKED	; FULL! flag the error and write nothing
	MOVF	RCREG, W, ACCESS		; pull byte out of serial port and ignore it.
	RETURN					; (necessary or UART will flag an overrun state)
	
RX_OK:						; OK to write byte into next slot in the buffer
	MOVFF	FSR1H, FSR1H_SAVE		; save pointer (remember we're an ISR here)
	MOVFF	FSR1L, FSR1L_SAVE
	MOVFF	RX_BUF_END, FSR1L 		; load buffer pointer
	MOVLW	HIGH(RX_BUFFER)
	MOVWF	FSR1H, ACCESS
	MOVFF	RCREG, INDF1			; move received byte into buffer
	BSF	SIO_STATUS, RXDATA_QUEUE, BANKED; flag that data are in the buffer now
	INCF	RX_BUF_END, F, BANKED		; increment pointer (will wrap around)
	MOVFF	FSR1H_SAVE, FSR1H		; restore caller's FSR1 pointer
	MOVFF	FSR1L_SAVE, FSR1L
	RETURN

ERR_FRAMING:
	BSF	SIO_STATUS, SIO_FERR, BANKED	; flag framing error for caller to handle
	RETURN					; I believe this clears on next valid Rx byte

ERR_OVERRUN:
	BSF	SIO_STATUS, SIO_ORUN, BANKED	; flag overrun error for caller to handle
	BCF	RCSTA, CREN, ACCESS		; reset error by disabling serial receiver
	BSF	RCSTA, CREN, ACCESS		; and then enabling it again.
	RETURN
	

_SIO_LOOKUP_TABLES CODE SIO_TABLE_START
HEXTBL	ORG	SIO_TABLE_START
	
	ANDLW	0x0F
	RLNCF	WREG, F, ACCESS			; offset*2
	MOVFF	PCL, SIO_TMPPC			; latch high bits of PC
	ADDWF	PCL, F, ACCESS			; branch into table
	DT	"0123456789ABCDEF"

;   300 baud 8234  error 0.001%
;   600 baud 4219	 0.004%
;  1200 baud 208C        0.004%
;  2400 baud 1045        0.016%
;  4800 baud 0822        0.016%
;  9600 baud 0410        0.064%
; 19200 baud 0207        0.160%
; 38400 baud 0103        0.160%
; 57600 baud 00AC        0.353%
;115200 baud 0055        0.937%
;250000 baud 0027        0.000%

BAUDTBLH:
	ANDLW	0x1F
	RLNCF	WREG, F, ACCESS
	MOVFF	PCL, SIO_TMPPC
	ADDWF	PCL, F, ACCESS
	DT	0x82, 0x42, 0x20, 0x10, 0x08
	DT	0x04, 0x02, 0x01, 0x00, 0x00
	DT	0x00, 0x00, 0x00, 0x00, 0x00
	DT	0x00, 0x00
	DT	0x02, 0x02, 0x02, 0x02, 0x02	; fall back to 19200
	DT	0x02, 0x02, 0x02, 0x02, 0x02
	DT	0x02, 0x02, 0x02, 0x02, 0x02
BAUDTBLL:
	ANDLW	0x1F
	RLNCF	WREG, F, ACCESS
	MOVFF	PCL, SIO_TMPPC
	ADDWF	PCL, F, ACCESS
	DT	0x34, 0x19, 0x8C, 0x45, 0x22
	DT	0x10, 0x07, 0x03, 0xAC, 0x55
	DT	0x27, 0x13, 0x09, 0x04, 0x03
	DT	0x01, 0x00
	DT	0x07, 0x07, 0x07, 0x07, 0x07	; fall back to 19200
	DT	0x07, 0x07, 0x07, 0x07, 0x07
	DT	0x07, 0x07, 0x07, 0x07, 0x07

	
;==============================================================================
;==============================================================================
	END
;==============================================================================
;==============================================================================
