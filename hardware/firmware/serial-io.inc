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
;
#include "serial-io-bits.inc"
; 
;==============================================================================
; PUBLIC ENTRY POINTS
;==============================================================================
;
	EXTERN	SIO_INIT 	; Call this to set up the module before use.
	EXTERN	SIO_RECV	; Call from ISR when a byte is received.
	EXTERN	SIO_SEND	; Call from ISR when clear to send next byte.
	EXTERN	SIO_ECHO	; Print char in SIO_OUTPUT in printable form.**
	EXTERN	SIO_ECHO_W	; Print char in WREG in printable form.* **
	EXTERN	SIO_WRITE	; Print char in SIO_OUTPUT in raw form.
	EXTERN	SIO_WRITE_W	; Print char in WREG in raw form.
	EXTERN	SIO_PUTCHAR	; Blocking form of SIO_WRITE.**
	EXTERN	SIO_PUTCHAR_W	; Blocking form of SIO_WRITE_W.**
	EXTERN	SIO_READ	; Read a character to SIO_INPUT.
	EXTERN	SIO_READ_W	; Read a character to SIO_INPUT and WREG.
	EXTERN	SIO_GETCHAR	; Blocking form of SIO_READ.**
	EXTERN	SIO_GETCHAR_W	; Blocking form of SIO_READ_W.**
	EXTERN	SIO_NEWLINE	; Print a carriage return/line feed.**
	EXTERN	SIO_PRINT_HEX	; Print value in SIO_OUTPUT as hex byte.**
	EXTERN	SIO_PRINT_HEX_W	; Print value in SIO_OUTPUT as hex byte.* **
	EXTERN	B32__BIN2BCD	; B32__BIN[4] -> B32__BCD_ASC[5]; big-endian
	EXTERN	B32__BCD2ASCII	; B32__BCD_ASC[5] -> B32__BCD_ASC[10]
	EXTERN	SIO_SET_BAUD_W	; Set baud rate from code in W (See serial-io-bits.inc)
;
; *Also overwrites SIO_OUTPUT.
; **Blocks execution until device/buffer ready.
;
; The SIO_READ functions are non-blocking, in case you need non-blocking I/O,
; although a better approach would be to check SIO_STATUS<RXDATA_QUEUE> to see
; if there's data queued up waiting to be read before calling SIO_READ.
; Alternatively the SIO_GETCHAR functions always block to wait for data to be
; available.  The SIO_PUTCHAR, SIO_NEWLINE, and SIO_ECHO functions always block 
; until the characters can be successfully buffered to be transmitted.  A
; non-blocking write is avilable from SIO_WRITE.
;
; "printable form" means that control characters print as the two-character
; sequence "^x" (i.e., 0x00="^@", 0x01="^A", etc.); the escape character 0x1B
; prints as "$"; the delete character 0x7F prints as "^?"; and meta-characters
; (i.e., 0x80-0xFF) print as "M-" followed by what the character would have
; echoed as if the high bit were not sent (e.g., 0x80="M-^@", 0xD0="M-P").
;
; "raw form" send the 8-bit byte to the serial port with no translation at all.
;
; The READ functions are non-blocking; they will return 0 if no character is
; available (check SIO_STATUS<RXDATA_QUEUE> to see if data is ready to read).
;
; The GETCHAR functions are blocking; they will wait until they are able to write
; data before completing.
;
;==============================================================================
; PUBLIC DATA
;==============================================================================
;
	EXTERN	SIO_STATUS	; status register (see serial-io-bits.inc for bit values)
	EXTERN	SIO_INPUT	; last byte read from serial port (output from module)
	EXTERN	SIO_OUTPUT	; byte to write to serial port (input to module)
	EXTERN	B32__BIN	; 4-byte big-endian input to B32__BIN2BCD
	EXTERN	B32__BCD_ASC	; 5-byte output from B32__BIN2BCD and input/output to/from
				; B32__BCD2ASCII.
;
; If writing data to the port and the buffer fills up, the printed characters
; will be ignored past the point where the buffer fills up, and the SIO_STATUS<TXDATA_FULL>
; flag will be set.
;
; If too much data arrives at the serial port before you read it out with this module's
; functions, the extra incoming bytes will be discarded, and the SIO_STATUS<RXDATA_FULL>
; flag will be set.
;
; Framing errors and buffer overruns (data received faster than the SIO_RECV function
; could handle them, usually because the SIO_RECV function isn't being called quickly
; enough) cause the SIO_STATUS<SIO_FERR> and SIO_STATUS<SIO_ORUN> bits to be set,
; respectively.
;
; It is the caller's responsibility to clear these flags.
;
; This module will automatically turn on/off the TXIE interrupt enable
; bit as needed to handle shipping out buffered data to the serial port.
; Just ensure that your ISR calls SIO_RECV when an RXIF interrupt is
; detected (you should clear RXIF when that's done), and you also call
; SIO_SEND when TXIF is detected (and clear that bit, too).
;
