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
; serial io (SIO) module bit definitions, included by caller and the module
;
#include "serial-io-user.inc"
;	
;                    bit 7      6      5      4      3      2      1      0
;                     _______________________________________________________
; +$00 SIO_STATUS    |      |      |SIO_  |SIO_  |RXDATA|TXDATA|RXDATA|TXDATA|
;                    |      |      | FERR | ORUN |_FULL |_FULL |_QUEUE|_QUEUE|
;                    |______|______|______|______|______|______|______|______|
;
TXDATA_QUEUE	EQU	0	; Tx data waiting in buffer now to be sent
RXDATA_QUEUE	EQU	1	; Rx data waiting in buffer to be retrieved
TXDATA_FULL	EQU	2	; Tx buffer full
RXDATA_FULL	EQU	3	; Rx buffer full
SIO_ORUN	EQU	4	; I/O Error: incoming data overrun  (caller clears)
SIO_FERR	EQU	5	; I/O Error: break/framing error received  (caller clears)
;
; Baud rate settings
;
SIO_300		EQU	0x00
SIO_600		EQU	0x01
SIO_1200	EQU	0x02
SIO_2400	EQU	0x03
SIO_4800	EQU	0x04
SIO_9600	EQU	0x05
SIO_19200	EQU	0x06
SIO_38400	EQU	0x07
SIO_57600	EQU	0x08
SIO_115200	EQU	0x09
SIO_250000	EQU	0x0A
