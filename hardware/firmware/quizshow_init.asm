; vim:set syntax=pic ts=8:
;
		LIST n=90
;@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
;@@                                                                         @@
;@@  @@@   @   @  @@@@@  @@@@@                QUIZ SHOW HARDWARE CONTROLLER @@
;@@ @   @  @   @    @        @                FIRMWARE VERSION 4.0          @@ 
;@@ @   @  @   @    @       @                                               @@
;@@ @   @  @   @    @      @                  FOR HARDWARE REVISION 4.0     @@
;@@ @ @ @  @   @    @     @                   QSCC - QUIZ SHOW CONTESTANT   @@
;@@ @  @@  @   @    @    @                    QSRC - QUIZ SHOW REMOTE       @@
;@@ @@@@@   @@@   @@@@@  @@@@@                                              @@
;@@                                                                         @@
;@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
;
; Copyright (c) 2014 by Steven L. Willoughby, Aloha, Oregon, USA.  
; All Rights Reserved.  Quiz Show portions are unreleased trade secret
; information.
;
; Based on previous works by the same author, some of which are released
; under the Open Software License, version 3.0, which portions are available
; separately for free download.
;
; -*- -*- -* -*- -*- -*- -*- -*- -* -*- -*- -*- -*- -*- -* -*- -*- -*- -*- -*-
;
; Device initialization code.  See lumos_main.asm for hardware implementation
; details.  Most of the initialization will be done in the Lumos firmware.
;
#include "lumos_config.inc"
#include "quizshow_config.inc"
		RADIX		DEC
;
;==============================================================================
; PUBLIC ENTRY POINTS
;==============================================================================
QUIZSHOW_CODE_INIT CODE
	GLOBAL	QSCC_INIT
;
; QSCC_INIT  (nil -> nil)
;
;	Initialize the CPU in addition to LUMOS_INIT's results for the QSCC/QSRC circuit
;
QSCC_INIT:
	CLRWDT
	MOVLW	B'00000000'		; T1CON		Timer 1 Control
		; 1			; 1-------	Read/write as 16-bit unit
		;  0			; -0------	Device clock from other source
		;   00			; --00----	1:1 Prescale
		;     1    		; ----1---	Timer oscillator enabled
		;      0		; -----0--	Don't synchronize external clock
		;       0		; ------0-	Clock source = Fosc/4 (10MHz)
		;        0		; -------0	Don't start running
	MOVWF	T1CON, ACCESS
	

	; Turn on with 	BSF INTCON, GIE/GIEH, PEIE/GIEL
	; PIR1, TMR1IF
	; PIE1, TMR1IE
	; IPR1, TMR1IP
	; T1CON, TMR1ON
	RETURN
	END
