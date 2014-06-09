; vim:set syntax=pic ts=8:
;
		LIST n=90
;@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
;@@                                                                         @@
;@@ @      @   @  @   @   @@@    @@@          LUMOS: LIGHT ORCHESTRATION    @@
;@@ @      @   @  @@ @@  @   @  @   @         SYSTEM FIRMWARE VERSION 3.0   @@
;@@ @      @   @  @ @ @  @   @  @                                           @@
;@@ @      @   @  @   @  @   @   @@@   @@@@@  FOR 24- AND 48-CHANNEL AC/DC  @@
;@@ @      @   @  @   @  @   @      @         LUMOS CONTROLLER UNITS        @@
;@@ @      @   @  @   @  @   @  @   @         BASED ON THE PIC18F4685 CHIP  @@
;@@ @@@@@   @@@   @   @   @@@    @@@                                        @@
;@@                                                                         @@
;@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
;
; Copyright (c) 2012, 2014 by Steven L. Willoughby, Aloha, Oregon, USA.  
; All Rights Reserved.  
; Released under the terms and conditions of the Open Software
; License, version 3.0.
;
; Portions based on earlier code copyright (c) 2004, 2005, 2006, 2007
; Steven L. Willoughby, Aloha, Oregon, USA.  All Rights Reserved.
;
; -*- -*- -* -*- -*- -*- -*- -*- -* -*- -*- -*- -*- -*- -* -*- -*- -*- -*- -*-
;
#ifndef LUMOS_SET_SSR_INC
#define LUMOS_SET_SSR_INC

 IF LUMOS_ARCH == LUMOS_ARCH_4685
SSR_DATA_BANK	EQU	0x400
MAIN_DATA	EQU	0x500
YY_BUF_LEN	EQU	.200
 ELSE
  IF LUMOS_ARCH == LUMOS_ARCH_14K50
SSR_DATA_BANK	EQU	0x060
MAIN_DATA	EQU	0x088
YY_BUF_LEN	EQU	.90 
  ELSE
   ERROR "Invalid architecture switch for SSR_DATA_BANK"
  ENDIF
 ENDIF

;
; SSR_FLAGS words for each output show state information about those
; channels.
;
FADE_UP		EQU	7	; 1-------  This channel is fading up
FADE_DOWN	EQU	6	; -1------  This channel is fading down
FADE_CYCLE	EQU	5	; --1-----  This channel is fading up<-->down
MAX_OFF_TIME	EQU	4	; ---1----  Use maximum off-time in cycle
BIT_FADE_UP	EQU	0x80
BIT_FADE_DOWN	EQU	0x40
BIT_FADE_CYCLE	EQU	0x20
BIT_MAX_OFF_TIME EQU	0x10

SET_SSR_VALUE MACRO IDX, LEVEL
	BANKSEL	SSR_DATA_BANK
	 MOVLW	LEVEL
	 MOVWF	SSR_00_VALUE+IDX, BANKED
	 CLRF	SSR_00_STEP+IDX, BANKED
	 CLRF	SSR_00_SPEED+IDX, BANKED
	 CLRF	SSR_00_COUNTER+IDX, BANKED
	 CLRF	SSR_00_FLAGS+IDX, BANKED
	ENDM

SET_SSR_PATTERN	MACRO IDX, LEVEL, STEP, SPEED, FLAGS
	BANKSEL	SSR_DATA_BANK
	 MOVLW	LEVEL
	 MOVWF	SSR_00_VALUE+IDX, BANKED
	 MOVLW	STEP
	 MOVWF	SSR_00_STEP+IDX, BANKED
	 MOVLW	SPEED
	 MOVWF	SSR_00_SPEED+IDX, BANKED
	 MOVWF	SSR_00_COUNTER+IDX, BANKED
	 MOVLW	FLAGS
	 MOVWF	SSR_00_FLAGS+IDX, BANKED
	ENDM

SET_SSR_NORMAL_MODE MACRO IDX
	 SET_SSR_PATTERN IDX, 0, 1, 3, BIT_FADE_UP|BIT_FADE_CYCLE
	ENDM

SET_SSR_DMX_MODE MACRO IDX
	 SET_SSR_PATTERN IDX, 0, 1, 1, BIT_FADE_UP|BIT_FADE_CYCLE
	ENDM

SET_SSR_RAPID_FLASH MACRO IDX
	 SET_SSR_PATTERN IDX, 255, 255, 30, BIT_FADE_DOWN|BIT_FADE_CYCLE
	ENDM

SET_SSR_BLINK_FADE MACRO IDX
	 SET_SSR_PATTERN IDX, 255,   2,  1, BIT_FADE_DOWN
	ENDM

SET_SSR_SLOW_FLASH MACRO IDX
	 SET_SSR_PATTERN IDX, 255, 255, 30, BIT_FADE_DOWN|BIT_FADE_CYCLE|BIT_MAX_OFF_TIME
	ENDM

SET_SSR_RAPID_FADE MACRO IDX
	 SET_SSR_PATTERN IDX, 0, 4, 1, BIT_FADE_UP|BIT_FADE_CYCLE
	ENDM

SET_SSR_SLOW_FADE MACRO IDX
	 SET_SSR_PATTERN IDX, 0, 1, 1, BIT_FADE_UP|BIT_FADE_CYCLE
	ENDM

SET_SSR_STEADY MACRO IDX
	 SET_SSR_VALUE IDX, 255
	ENDM

SET_SSR_OFF MACRO IDX
	 SET_SSR_VALUE IDX, 0
	ENDM
#endif
