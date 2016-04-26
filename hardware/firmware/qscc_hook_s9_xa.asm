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
; This hooks into the Lumos command interpreter to add extended commands 
; (state 9)
; 
	IF LUMOS_CHIP_TYPE != LUMOS_CHIP_QSCC && LUMOS_CHIP_TYPE != LUMOS_CHIP_QSRC
	 ERROR "qscc_hook_s9_xa only used for QS*C systems"
	ENDIF

S9_XA_QS_QUERY:
	DECFSZ	WREG, W, ACCESS
	BRA	S9_XB_BTN_MASK
	MOVLW	.19
	MOVWF	YY_STATE, ACCESS
	RETURN

S9_XB_BTN_MASK:
	DECFSZ	WREG, W, ACCESS
	BRA	S9_XC_DISP_TEXT
	MOVLW	.20
	MOVWF	YY_STATE, ACCESS
	RETURN

S9_XC_DISP_TEXT:
	DECFSZ	WREG, W, ACCESS
	BRA	S9_XD_DISP_BITMAP
	WAIT_FOR_SENTINEL .67, B'01010101', .14
	RETURN

S9_XD_DISP_BITMAP:
	DECFSZ	WREG, W, ACCESS
	BRA	S9_XE_ERR_COMMAND
	WAIT_FOR_SENTINEL .59, B'01100110', .15
	RETURN

S9_XE_ERR_COMMAND:
	GOTO	ERR_COMMAND
