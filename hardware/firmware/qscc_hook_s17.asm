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
	BRA	S20_DATA
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

	BTFSC	YY_DATA, QS_QFLG_STOP, ACCESS
	CALL	QS_STOP_SCANNER
	;
	; XXX report out status
	;
	CLRF	YY_STATE, ACCESS
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

	IF LUMOS_CHIP_TYPE == LUMOS_CHIP_QSCC 
	 MOVLW	B'01100000'		; Check postbyte 2 constant 01100000
	 CPFSEQ	YY_DATA, ACCESS
	 GOTO	ERR_COMMAND
	 ;
 	 ; XXX set button masks
	 ;
	ELSE
	 IF LUMOS_CHIP_TYPE == LUMOS_CHIP_QSRC
	  BTFSS	YY_DATA, 5, ACCESS	; Check postbyte 2 constant xx00xxxx
	  BTFSC YY_DATA, 4, ACCESS
	  GOTO	ERR_COMMAND
	  ;
 	  ; XXX set button masks
	  ;
	 ENDIF
	ENDIF
	CLRF	YY_STATE, ACCESS
	RETURN
	  
S22_DATA:
	ERR_BUG	0x05, ERR_CLASS_OVERRUN
