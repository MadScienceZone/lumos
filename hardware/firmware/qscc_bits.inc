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
; This defines the bits for bit-encoded flags, etc.
; 
#ifndef QSCC_BITS_INC
#define QSCC_BITS_INC

	IF LUMOS_CHIP_TYPE != LUMOS_CHIP_QSCC && LUMOS_CHIP_TYPE != LUMOS_CHIP_QSRC
	 ERROR "qscc_bits only used for QS*C systems"
	ENDIF
					; QUIZSHOW_FLAGS
QS_FLAG_DOING120 EQU	2		; -----1--	Doing "every 1/120 sec tasks" now
QS_FLAG_ON_120_S EQU	1		; ------1-	Need to do "every 1/120 sec tasks" now
QS_FLAG_SCANNING EQU	0		; -------1	Scanner running

					; BTN_??_FLAGS
BTN_FLG_LCK_ACK	EQU	4		; ---1----	Button lock acknowledged already
BTN_FLG_ACTIVE	EQU	3		; ----1---	Button being pressed now
BTN_FLG_LOCKED	EQU	2		; -----1--	Button locked out
BTN_FLG_MASKED	EQU	1		; ------1-	Button ignored
BTN_FLG_PRESSED	EQU	0		; -------1	Button pressed already

QUIZSHOW_DATA	EQU	0xC00
#endif
