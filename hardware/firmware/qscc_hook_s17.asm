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
	 ERROR "qscc_hook_s17 only used for QS*C systems"
	ENDIF

S17_DATA_NIL:
	DECFSZ	WREG, W, ACCESS
	BRA	S18_DATA_NIL
	GOTO	ERR_COMMAND

S18_DATA_NIL:
	DECFSZ	WREG, W, ACCESS
	BRA	S19_DATA
	GOTO	ERR_COMMAND

S19_DATA:
	DECFSZ	WREG, W, ACCESS
	GOTO	S20_DATA
	;
	; S19: QS_QUERY command received.
	;
	;   ___7______6______5______4______3______2______1______0__
	;  |                                  |                    |
	;  |                0                 |          7         | YY_COMMAND
	;  |______|______|______|______|______|______|______|______|
	;  |      |      |      |      |                           |
	;  |   0  |   0  |   0  |   0  |             10            | (not saved)
	;  |______|______|______|______|______|______|______|______|
	;  |      |      |      |      |      |      |      |      |
	;  |   0  |   1  |   1  |   0  |   0  |Button| Ping | Stop | YY_DATA
	;  |______|______|______|______|______|______|______|______|
	;
	;
	CLRWDT
	MOVLW	B'11111000'			; Verify YY_DATA's constant bits
	ANDWF	YY_DATA, W, ACCESS
	MOVWF	YY_YY, ACCESS
	MOVLW	B'01100000'
	CPFSEQ	YY_YY, ACCESS
	GOTO	ERR_COMMAND
	
QS_QFLG_BUTTONS	EQU	2
QS_QFLG_PING	EQU	1
QS_QFLG_STOP	EQU	0
	EXTERN	BTN_X0_TIME_T
	EXTERN	BTN_X0_TIME_U
	EXTERN	BTN_X0_TIME_H
	EXTERN	BTN_X0_TIME_L
	EXTERN	BTN_X0_FLAGS

	BTFSC	YY_DATA, QS_QFLG_STOP, ACCESS
	CALL	QS_STOP_SCANNER
	;
	; report out status:
	;
	;      ___7______6______5______4______3______2______1______0__
	;     |                           |                           |
	; 00  |   1      1      1      1  |         address           | 
	;     |______|______|______|______|______|______|______|______|
	;     |      |                                                |
	; 01  |   0  |   0      0      1      1      1      0      1  |
	;     |______|______|______|______|______|______|______|______|
	;  
	;
	;   If ping-only (p=1)
	;      ___7______6______5______4______3______2______1______0__
	;     |      |      |             PACKET LENGTH               |
	; 02  |   0  |   s  |   0      0      0      0      0     0   |
	;     |______|______|______|______|______|______|______|______|
	;
	;
	;   Else If button or full query (p=0)
	;      ___7______6______5______4______3______2______1______0__      //QSCC//
	;     |      |      |             PACKET LENGTH               |     ////////
	; 02  |   0  |   s  |                                         |     ////////
	;     |______|______|______|______|______|______|______|______|___  ////////
	;     |      |      |      BUTTON PRESSED ALREADY?            | |   ////////
	; 03  |   0  |   0  |   A      B      C      D      L     X   | |   ////////
	;     |______|______|______|______|______|______|______|______| 2   ////////
	;     |      |      |      BUTTON MASKED OUT (IGNORED)?       | |   ////////
	; 04  |   0  |   0  |   A      B      C      D      L     X   | |   ////////
	;     |______|______|______|______|______|______|______|______|_V_  ////////
	;
	;      ___7______6______5______4______3______2______1______0__      \\QSRC\\
	;     |      |      |              PACKET LENGTH              |     \\\\\\\\
	; 02  |   0  |   s  |                                         |     \\\\\\\\
	;     |______|______|______|______|______|______|______|______|___  \\\\\\\\
	;     |      |  L3  |     X3      |     L0      |     X0      | |   \\\\\\\\ 
	; 03  |   0  | Press|Masked Press |Masked Press |Masked Press | |   \\\\\\\\
	;     |______|______|______|______|______|______|______|______| |   \\\\\\\\
	;     |      |  L4  |     X4      |     L1      |     X1      | |   \\\\\\\\
	; 04  |   0  | Press|Masked Press |Masked Press |Masked Press | 3   \\\\\\\\
	;     |______|______|______|______|______|______|______|______| |   \\\\\\\\
	;     |      |      |  L4  |  L3  |     L2      |     X2      | |   \\\\\\\\
	; 05  |   0  |   0  |Masked|Masked|Masked Press |Masked Press | |   \\\\\\\\
	;     |______|______|______|______|______|______|______|______|_V_  \\\\\\\\
	;
	;   Additionally If full query (b=0)
	;      ___7______6______5______4______3______2______1______0__ _____//QSCC//
	;     |                                           Bits <31:24>| | | ////////
	; +1  | Button press time (if "pressed" bit set) x 100 nS     | | | ////////
	;     |.......................................................| | | ////////
	;     |                                           Bits <23:16>| | | ////////
	; +2  |                                                       | | | ////////
	;     |.......................................................| X | ////////
	;     |                                           Bits <15:08>| | | ////////
	; +3  |                                                       | | | ////////
	;     |.......................................................| | | ////////
	;     |                                           Bits <07:00>| | | ////////
	; +4  |                                                       | | | ////////
	;     |______|______|______|______|______|______|______|______|_V_| ////////
	;     |                                           Bits <31:24>| | | ////////
	; +5  | Button press time (if "pressed" bit set) x 100 nS     | | | ////////
	;     |.......................................................| | | ////////
	;     |                                           Bits <23:16>| | | ////////
	; +6  |                                                       | |+24////////
	;     |.......................................................| L | ////////
	;     |                                           Bits <15:08>| | | ////////
	; +7  |                                                       | | | ////////
	;     |.......................................................| | | ////////
	;     |                                           Bits <07:00>| | | ////////
	; +8  |                                                       | | | ////////
	;     |______|______|______|______|______|______|______|______|_V_| ////////
	;                                                                 | ////////
	;                                 |                               | ////////
	;                                 |  likewise A, B, C, D          | ////////
	;                                 V                               | ////////
	;      ___7______6______5______4______3______2______1______0__  | | ////////
	;     |                                           Bits <07:00>| D | ////////
	; +24 |                                                       | | | ////////
	;     |______|______|______|______|______|______|______|______|_V_V_////////
	;
	;      ___7______6______5______4______3______2______1______0__ _____\\QSRC\\
	;     |                                           Bits <31:24>| | | \\\\\\\\
	; +1  | Button press time (if "pressed" bit set) x 100 nS     | | | \\\\\\\\
	;     |.......................................................| | | \\\\\\\\
	;     |                                           Bits <23:16>| | | \\\\\\\\
	; +2  |                                                       | | | \\\\\\\\
	;     |.......................................................|X0 | \\\\\\\\
	;     |                                           Bits <15:08>| | | \\\\\\\\
	; +3  |                                                       | | | \\\\\\\\
	;     |.......................................................| | | \\\\\\\\
	;     |                                           Bits <07:00>| | | \\\\\\\\
	; +4  |                                                       | | | \\\\\\\\
	;     |______|______|______|______|______|______|______|______|_V_| \\\\\\\\
	;     |                                           Bits <31:24>| | | \\\\\\\\
	; +5  | Button press time (if "pressed" bit set) x 100 nS     | | | \\\\\\\\
	;     |.......................................................| | | \\\\\\\\
	;     |                                           Bits <23:16>| | | \\\\\\\\
	; +6  |                                                       | |+40\\\\\\\\
	;     |.......................................................|L0 | \\\\\\\\
	;     |                                           Bits <15:08>| | | \\\\\\\\
	; +7  |                                                       | | | \\\\\\\\
	;     |.......................................................| | | \\\\\\\\
	;     |                                           Bits <07:00>| | | \\\\\\\\
	; +8  |                                                       | | | \\\\\\\\
	;     |______|______|______|______|______|______|______|______|_V_| \\\\\\\\
	;                                                                 | \\\\\\\\
	;                                 |                               | \\\\\\\\
	;                                 |  likewise X1, L1, ..., L4     | \\\\\\\\
	;                                 V                               | \\\\\\\\
	;      ___7______6______5______4______3______2______1______0__  | | \\\\\\\\
	;     |                                           Bits <07:00>|L4 | \\\\\\\\
	; +40 |                                                       | | | \\\\\\\\
	;     |______|______|______|______|______|______|______|______|_V_V_\\\\\\\\
	;
	;
	; Finally:
	;
	;      ___7______6______5______4______3______2______1______0__ 
	;     |      |      |                    |                    |
	; +x  |   0  |   s  |   1      0      1  | Packet Length & 7  |
	;     |______|______|______|______|______|______|______|______|
	;
	;

	CALL	TR_ON_DELAY
	BSF	PLAT_T_R, BIT_T_R, ACCESS		; Fire up our transmitter now
	BCF	SSR_STATE2, INHIBIT_OUTPUT, ACCESS	; Allow sending output
	MOVLW	0xf0
	IORWF	MY_ADDRESS, W, ACCESS
	CALL	SIO_WRITE_W			; 00 start byte 		<1111aaaa>
	MOVLW	0x1d				; 01 extended ID byte for       <00011101>
	CALL	SIO_WRITE_W			;    for this type of reply
	
	BTFSC	YY_DATA, QS_QFLG_PING, ACCESS	; If ping-only, send short packet
	GOTO	QS_QUERY_PING

	;
	; Figure out ultimate packet length
	;
	IF LUMOS_CHIP_TYPE == LUMOS_CHIP_QSCC
	 MOVLW	.2
	 BTFSS	YY_DATA, QS_QFLG_BUTTONS, ACCESS
	 ADDLW	.24
	ELSE
	 IF LUMOS_CHIP_TYPE == LUMOS_CHIP_QSRC
	  MOVLW	.3
	  BTFSS	YY_DATA, QS_QFLG_BUTTONS, ACCESS
	  ADDLW	.40
	 ENDIF
	ENDIF
	BTFSC	QUIZSHOW_FLAGS, QS_FLAG_SCANNING, ACCESS
	BSF	WREG, 6, ACCESS			; YY_YY = 0spppppp (header byte)
	MOVWF	YY_YY, ACCESS
	CALL	SIO_WRITE_W			; 02 payload length	<0spppppp>

	BANKSEL	QUIZSHOW_DATA
	IF LUMOS_CHIP_TYPE == LUMOS_CHIP_QSCC
	 CLRF	WREG, ACCESS
	 BTFSC	BTN_X0_FLAGS + BTN_IDX_X0, BTN_FLG_PRESSED, BANKED
	 BSF	WREG, 0, ACCESS
	 BTFSC	BTN_X0_FLAGS + BTN_IDX_L0, BTN_FLG_PRESSED, BANKED
	 BSF	WREG, 1, ACCESS
	 BTFSC	BTN_X0_FLAGS + BTN_IDX_D0, BTN_FLG_PRESSED, BANKED
	 BSF	WREG, 2, ACCESS
	 BTFSC	BTN_X0_FLAGS + BTN_IDX_C0, BTN_FLG_PRESSED, BANKED
	 BSF	WREG, 3, ACCESS
	 BTFSC	BTN_X0_FLAGS + BTN_IDX_B0, BTN_FLG_PRESSED, BANKED
	 BSF	WREG, 4, ACCESS
	 BTFSC	BTN_X0_FLAGS + BTN_IDX_A0, BTN_FLG_PRESSED, BANKED
	 BSF	WREG, 5, ACCESS
	 CALL	SIO_WRITE_W			; 03 pressed flags 	<00ABCDLX>

	 CLRF	WREG, ACCESS
	 BTFSC	BTN_X0_FLAGS + BTN_IDX_X0, BTN_FLG_MASKED, BANKED
	 BSF	WREG, 0, ACCESS
	 BTFSC	BTN_X0_FLAGS + BTN_IDX_L0, BTN_FLG_MASKED, BANKED
	 BSF	WREG, 1, ACCESS
	 BTFSC	BTN_X0_FLAGS + BTN_IDX_D0, BTN_FLG_MASKED, BANKED
	 BSF	WREG, 2, ACCESS
	 BTFSC	BTN_X0_FLAGS + BTN_IDX_C0, BTN_FLG_MASKED, BANKED
	 BSF	WREG, 3, ACCESS
	 BTFSC	BTN_X0_FLAGS + BTN_IDX_B0, BTN_FLG_MASKED, BANKED
	 BSF	WREG, 4, ACCESS
	 BTFSC	BTN_X0_FLAGS + BTN_IDX_A0, BTN_FLG_MASKED, BANKED
	 BSF	WREG, 5, ACCESS
	 CALL	SIO_WRITE_W			; 04 masked flags 	<00ABCDLX>
	ELSE
	 IF LUMOS_CHIP_TYPE == LUMOS_CHIP_QSRC
	  CLRF	WREG, ACCESS
	  BTFSC	BTN_X0_FLAGS + BTN_IDX_X0, BTN_FLG_PRESSED, BANKED
	  BSF	WREG, 0, ACCESS
	  BTFSC	BTN_X0_FLAGS + BTN_IDX_X0, BTN_FLG_MASKED, BANKED
	  BSF	WREG, 1, ACCESS
	  BTFSC	BTN_X0_FLAGS + BTN_IDX_L0, BTN_FLG_PRESSED, BANKED
	  BSF	WREG, 2, ACCESS
	  BTFSC	BTN_X0_FLAGS + BTN_IDX_L0, BTN_FLG_MASKED, BANKED
	  BSF	WREG, 3, ACCESS
	  BTFSC	BTN_X0_FLAGS + BTN_IDX_X3, BTN_FLG_PRESSED, BANKED
	  BSF	WREG, 4, ACCESS
	  BTFSC	BTN_X0_FLAGS + BTN_IDX_X3, BTN_FLG_MASKED, BANKED
	  BSF	WREG, 5, ACCESS
	  BTFSC	BTN_X0_FLAGS + BTN_IDX_L3, BTN_FLG_PRESSED, BANKED
	  BSF	WREG, 6, ACCESS			;                        3330000
	  CALL	SIO_WRITE_W			; 03 x=press X=mask    <0lXxLlXx>

	  CLRF	WREG, ACCESS
	  BTFSC	BTN_X0_FLAGS + BTN_IDX_X1, BTN_FLG_PRESSED, BANKED
	  BSF	WREG, 0, ACCESS
	  BTFSC	BTN_X0_FLAGS + BTN_IDX_X1, BTN_FLG_MASKED, BANKED
	  BSF	WREG, 1, ACCESS
	  BTFSC	BTN_X0_FLAGS + BTN_IDX_L1, BTN_FLG_PRESSED, BANKED
	  BSF	WREG, 2, ACCESS
	  BTFSC	BTN_X0_FLAGS + BTN_IDX_L1, BTN_FLG_MASKED, BANKED
	  BSF	WREG, 3, ACCESS
	  BTFSC	BTN_X0_FLAGS + BTN_IDX_X4, BTN_FLG_PRESSED, BANKED
	  BSF	WREG, 4, ACCESS
	  BTFSC	BTN_X0_FLAGS + BTN_IDX_X4, BTN_FLG_MASKED, BANKED
	  BSF	WREG, 5, ACCESS
	  BTFSC	BTN_X0_FLAGS + BTN_IDX_L4, BTN_FLG_PRESSED, BANKED
	  BSF	WREG, 6, ACCESS			;                        4441111
	  CALL	SIO_WRITE_W			; 04 x=press X=mask    <0lXxLlXx>

	  CLRF	WREG, ACCESS
	  BTFSC	BTN_X0_FLAGS + BTN_IDX_X2, BTN_FLG_PRESSED, BANKED
	  BSF	WREG, 0, ACCESS
	  BTFSC	BTN_X0_FLAGS + BTN_IDX_X2, BTN_FLG_MASKED, BANKED
	  BSF	WREG, 1, ACCESS
	  BTFSC	BTN_X0_FLAGS + BTN_IDX_L2, BTN_FLG_PRESSED, BANKED
	  BSF	WREG, 2, ACCESS
	  BTFSC	BTN_X0_FLAGS + BTN_IDX_L2, BTN_FLG_MASKED, BANKED
	  BSF	WREG, 3, ACCESS
	  BTFSC	BTN_X0_FLAGS + BTN_IDX_L3, BTN_FLG_MASKED, BANKED
	  BSF	WREG, 4, ACCESS
	  BTFSC	BTN_X0_FLAGS + BTN_IDX_L4, BTN_FLG_MASKED, BANKED
	  BSF	WREG, 5, ACCESS			;                         432222
	  CALL	SIO_WRITE_W			; 05 x=press X=mask    <00LLLlXx>
	 ELSE
	  ERROR "Invalid chip selection"
	 ENDIF
	ENDIF

	BTFSC	YY_DATA, QS_QFLG_BUTTONS, ACCESS	
	GOTO	QS_QUERY_DONE
	;
	; Not *just* looking for button states? 
	; send timing data as well now
	;
QS_SEND_BUTTON_TIME MACRO BTN_IDX
	 MOVFF	BTN_X0_TIME_T + BTN_IDX, WREG
	 SEND_8_BIT_W
	 MOVFF	BTN_X0_TIME_U + BTN_IDX, WREG
	 SEND_8_BIT_W
	 MOVFF	BTN_X0_TIME_H + BTN_IDX, WREG
	 SEND_8_BIT_W
	 MOVFF	BTN_X0_TIME_L + BTN_IDX, WREG
	 SEND_8_BIT_W
	ENDM

	IF LUMOS_CHIP_TYPE == LUMOS_CHIP_QSCC	
	 QS_SEND_BUTTON_TIME BTN_IDX_X0
	 QS_SEND_BUTTON_TIME BTN_IDX_L0
	 QS_SEND_BUTTON_TIME BTN_IDX_A0
	 QS_SEND_BUTTON_TIME BTN_IDX_B0
	 QS_SEND_BUTTON_TIME BTN_IDX_C0
	 QS_SEND_BUTTON_TIME BTN_IDX_D0
	ELSE
	 IF LUMOS_CHIP_TYPE == LUMOS_CHIP_QSRC
	  QS_SEND_BUTTON_TIME BTN_IDX_X0
	  QS_SEND_BUTTON_TIME BTN_IDX_L0
	  QS_SEND_BUTTON_TIME BTN_IDX_X1
	  QS_SEND_BUTTON_TIME BTN_IDX_L1
	  QS_SEND_BUTTON_TIME BTN_IDX_X2
	  QS_SEND_BUTTON_TIME BTN_IDX_L2
	  QS_SEND_BUTTON_TIME BTN_IDX_X3
	  QS_SEND_BUTTON_TIME BTN_IDX_L3
	  QS_SEND_BUTTON_TIME BTN_IDX_X4
	  QS_SEND_BUTTON_TIME BTN_IDX_L4
	 ELSE
	  ERROR "Invalid chip selection"
	 ENDIF
	ENDIF
	GOTO	QS_QUERY_DONE

QS_QUERY_PING:
	CLRF	YY_YY, ACCESS			; packet length = 0
	BTFSC	QUIZSHOW_FLAGS, QS_FLAG_SCANNING, ACCESS
	BSF	YY_YY, 6, ACCESS		; 02 packet length+s	<0spppppp>
	MOVF	YY_YY, W, ACCESS
	CALL	SIO_WRITE_W

QS_QUERY_DONE:					; Final packet:
	MOVLW	B'01000111'			; 0spppppp         p=packet length
	ANDWF	YY_YY, W, ACCESS		; 0s000ppp    	   s=scanner status
	BSF	WREG, 5, ACCESS			; 0s100ppp
	BSF	WREG, 3, ACCESS			; 0s101ppp
	CALL 	SIO_WRITE_W

	BSF	SSR_STATE, DRAIN_TR, ACCESS	; schedule transmitter shut-down
	CLRF	YY_STATE, ACCESS		; return to idle state for next command
	RETURN


S20_DATA:
	DECFSZ	WREG, W, ACCESS
	BRA	S21_DATA
	;
	; SET_BUTTON_MASKS first byte received
	; Store in YY_YY, wait for second byte.
	;
	MOVFF	YY_DATA, YY_YY
	INCF	YY_STATE, F, ACCESS	; -> state 21 (wait for final byte)
	RETURN

S21_DATA:
	DECFSZ	WREG, W, ACCESS
	BRA	S22_DATA
	;
	; S21: QS_SET_BUTTON_MASKS command received.
	;
	;   ___7______6______5______4______3______2______1______0__
	;  |                                  |                    |
	;  |                0                 |          7         | YY_COMMAND
	;  |______|______|______|______|______|______|______|______|
	;  |      |      |      |      |                           |
	;  |   0  |   0  |   0  |   0  |             11            | (not saved)
	;  |______|______|______|______|______|______|______|______|
	;  |      |      | BUTTON MASKS (1=disabled, 0=enabled)    |
	;  |   0  |   0  |   A  |   B  |   C  |   D  |   L  |   X  | YY_YY  
	;  |______|______|__L2__|__X2__|__L1__|__X1__|__L0__|__X0__|        <-- QSRC
	;  |      |      |                                         |
	;  |   0  |   1  |   1  |   0  |   0  |   0  |   0  |   0  | YY_DATA
	;  |______|______|___0__|___0__|__L4__|__X4__|__L3__|__X3__|        <-- QSRC
	;
	;
	BTFSS	YY_YY, 7, ACCESS	; Check postbyte 1 constant 00xxxxxx
	BTFSC	YY_YY, 6, ACCESS
	GOTO	ERR_COMMAND

	BTFSS	YY_DATA, 7, ACCESS	; Check postbyte 2 constant 01xxxxxx
	BTFSS	YY_DATA, 6, ACCESS
	GOTO	ERR_COMMAND

UPDATE_BTN_MASK	MACRO BTN_IDX, SRC, BIT
	 BCF	BTN_X0_FLAGS + BTN_IDX, BTN_FLG_MASKED, BANKED
	 BTFSC 	SRC, BIT, ACCESS
	 BSF	BTN_X0_FLAGS + BTN_IDX, BTN_FLG_MASKED, BANKED
	ENDM

	IF LUMOS_CHIP_TYPE == LUMOS_CHIP_QSCC 
	 MOVLW	B'01100000'		; Check postbyte 2 constant 01100000
	 CPFSEQ	YY_DATA, ACCESS
	 GOTO	ERR_COMMAND
	 ;
 	 ;  set button masks
	 ;
 	 BANKSEL QUIZSHOW_DATA
	 UPDATE_BTN_MASK BTN_IDX_X0, YY_YY, 0
	 UPDATE_BTN_MASK BTN_IDX_L0, YY_YY, 1
	 UPDATE_BTN_MASK BTN_IDX_A0, YY_YY, 5
	 UPDATE_BTN_MASK BTN_IDX_B0, YY_YY, 4
	 UPDATE_BTN_MASK BTN_IDX_C0, YY_YY, 3
	 UPDATE_BTN_MASK BTN_IDX_D0, YY_YY, 2
	ELSE
	 IF LUMOS_CHIP_TYPE == LUMOS_CHIP_QSRC
	  BTFSS	YY_DATA, 5, ACCESS	; Check postbyte 2 constant xx00xxxx
	  BTFSC YY_DATA, 4, ACCESS
	  GOTO	ERR_COMMAND
	  ;
 	  ; set button masks
	  ;
  	  BANKSEL QUIZSHOW_DATA
	  UPDATE_BTN_MASK BTN_IDX_X0, YY_YY, 0
	  UPDATE_BTN_MASK BTN_IDX_L0, YY_YY, 1
	  UPDATE_BTN_MASK BTN_IDX_X1, YY_YY, 2
	  UPDATE_BTN_MASK BTN_IDX_L1, YY_YY, 3
	  UPDATE_BTN_MASK BTN_IDX_X2, YY_YY, 4
	  UPDATE_BTN_MASK BTN_IDX_L2, YY_YY, 5
	  UPDATE_BTN_MASK BTN_IDX_X3, YY_DATA, 0
	  UPDATE_BTN_MASK BTN_IDX_L3, YY_DATA, 1
	  UPDATE_BTN_MASK BTN_IDX_X4, YY_DATA, 2
	  UPDATE_BTN_MASK BTN_IDX_L4, YY_DATA, 3
	 ENDIF
	ENDIF
	CLRF	YY_STATE, ACCESS
	RETURN
	  
S22_DATA:
	ERR_BUG	0x05, ERR_CLASS_OVERRUN
