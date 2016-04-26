; vim:set syntax=pic ts=8:
;
		LIST N=86
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
; This hooks into the Lumos ISR block for high-priority interrupts 
; 
	IF LUMOS_CHIP_TYPE != LUMOS_CHIP_QSCC && LUMOS_CHIP_TYPE != LUMOS_CHIP_QSRC
	 ERROR "qscc_hook_isr only used for QS*C systems"
	ENDIF

QSCC_INT_TMR1:
	BTFSS	PIR1, TMR1IF, ACCESS		; TMR1 overflow
	BRA	QSCC_INT_END
	BCF	PIR1, TMR1IF, ACCESS		; acknowledge interrupt
	INFSNZ	QS_BTN_TMR_U, F, ACCESS		; increment next significant byte
	INCF	QS_BTN_TMR_T, F, ACCESS		; carry to most significant byte 
QSCC_INT_END:
