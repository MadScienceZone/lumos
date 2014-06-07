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
; This hooks into the Lumos device initialization code which sets up I/O pins.
; We want them arranged differently than the Lumos controllers do, but we put
; the QuizShow code here to keep the Lumos product clean and separate.
; 
	IF LUMOS_CHIP_TYPE != LUMOS_CHIP_QSCC && LUMOS_CHIP_TYPE != LUMOS_CHIP_QSRC
	 ERROR "qscc_hook_main_pins only used for QS*C systems"
	ENDIF

;
; QSCC
;
    		    IF LUMOS_CHIP_TYPE == LUMOS_CHIP_QSCC
N_BUTTONS	     EQU	6	; X L A B C D
BTN_IDX_X0	     EQU	0
BTN_IDX_L0	     EQU	1
BTN_IDX_A0	     EQU	2
BTN_IDX_B0	     EQU	3
BTN_IDX_C0	     EQU	4
BTN_IDX_D0	     EQU	5
PORT_RX		     EQU	PORTC
BIT_RX		     EQU	7

HAS_T_R		     EQU	1
HAS_ACTIVE	     EQU	0
HAS_SENSORS	     EQU	0
HAS_OPTION	     EQU	0
HAS_STATUS_LEDS	     EQU	0
HAS_POWER_CTRL	     EQU	0

PLAT_T_R	     EQU	LATC
PORT_T_R	     EQU	PORTC
TRIS_T_R	     EQU	TRISC
BIT_T_R		     EQU	3

PLAT_0		     EQU	LATC	; XR
PLAT_1		     EQU	LATC	; XG
PLAT_2		     EQU	LATC	; XB
PLAT_3		     EQU	LATE	; LR
PLAT_4		     EQU	LATE	; LY
PLAT_5		     EQU	LATE	; LG
PLAT_6		     EQU	LATB	; AL
PLAT_7		     EQU	LATB	; BL
PLAT_8		     EQU	LATB	; CL
PLAT_9		     EQU	LATB	; DL
PLAT_10		     EQU	LATB	; FR
PLAT_11		     EQU	LATB	; FG
PLAT_12		     EQU	LATB	; FB
PLAT_13		     EQU	LATB	; FW
SSR_MAX		     EQU	13

BIT_0		     EQU	2	; XR
BIT_1		     EQU	1	; XG
BIT_2		     EQU	0	; XB
BIT_3		     EQU	2	; LR
BIT_4		     EQU	0	; LY
BIT_5		     EQU	1	; LG
BIT_6		     EQU	7	; AL
BIT_7		     EQU	6	; BL
BIT_8		     EQU	5	; CL
BIT_9		     EQU	4	; DL
BIT_10		     EQU	3	; FR
BIT_11		     EQU	2	; FG
BIT_12		     EQU	1	; FB
BIT_13		     EQU	0	; FW
		    ELSE
    		     IF LUMOS_CHIP_TYPE == LUMOS_CHIP_QSRC
N_BUTTONS	      EQU	10	; X0 L0 X1 L1 ... X4 L4
BTN_IDX_X0	      EQU	0
BTN_IDX_L0	      EQU	1
BTN_IDX_X1	      EQU	2
BTN_IDX_L1	      EQU	3
BTN_IDX_X2	      EQU	4
BTN_IDX_L2	      EQU	5
BTN_IDX_X3	      EQU	6
BTN_IDX_L3	      EQU	7
BTN_IDX_X4	      EQU	8
BTN_IDX_L4	      EQU	9
PORT_RX		      EQU	PORTC
BIT_RX		      EQU	7

HAS_T_R		      EQU	1
HAS_ACTIVE	      EQU	0
HAS_SENSORS	      EQU	0
HAS_OPTION	      EQU	0
HAS_STATUS_LEDS	      EQU	0
HAS_POWER_CTRL	      EQU	0

PLAT_T_R	      EQU	LATC
PORT_T_R	      EQU	PORTC
TRIS_T_R	      EQU	TRISC
BIT_T_R		      EQU	3

PLAT_0		      EQU	LATC	; X0R
PLAT_1		      EQU	LATC	; X0G
PLAT_2		      EQU	LATC	; X0B
PLAT_3		      EQU	LATE	; L0R
PLAT_4		      EQU	LATB	; X1R
PLAT_5		      EQU	LATB	; X1G
PLAT_6		      EQU	LATB	; X1B
PLAT_7		      EQU	LATB	; L1R
PLAT_8		      EQU	LATB	; X2R
PLAT_9		      EQU	LATB	; X2G
PLAT_10		      EQU	LATB	; X2B
PLAT_11		      EQU	LATE	; L2R
PLAT_12		      EQU	LATD	; X3R
PLAT_13		      EQU	LATD	; X3G
PLAT_14		      EQU	LATD	; X3B
PLAT_15		      EQU	LATE	; L3R
PLAT_16		      EQU	LATB	; X4R
PLAT_17		      EQU	LATD	; X4G
PLAT_18		      EQU	LATD	; X4B
PLAT_19		      EQU	LATD	; L4R
SSR_MAX		      EQU	19

BIT_0		      EQU	2	; X0R
BIT_1		      EQU	1	; X0G
BIT_2		      EQU	0	; X0B
BIT_3		      EQU	2	; L0R
BIT_4		      EQU	7	; X1R
BIT_5		      EQU	6	; X1G
BIT_6		      EQU	5	; X1B
BIT_7		      EQU	4	; L1R
BIT_8		      EQU	3	; X2R
BIT_9		      EQU	2	; X2G
BIT_10		      EQU	1	; X2B
BIT_11		      EQU	0	; L2R
BIT_12		      EQU	7	; X3R
BIT_13		      EQU	6	; X3G
BIT_14		      EQU	5	; X3B
BIT_15		      EQU	1	; L3R
BIT_16		      EQU	0	; X4R
BIT_17		      EQU	3	; X4G
BIT_18		      EQU	1	; X4B
BIT_19		      EQU	2	; L4R
		     ENDIF
		    ENDIF

