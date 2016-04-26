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
	 ERROR "qscc_hook_s6_14 only used for QS*C systems"
	ENDIF

S6_14_DATA_QS:
; XXX needs to be rewritten for the new readerboards
; XXX needs to be rewritten for the new readerboards
; XXX needs to be rewritten for the new readerboards

	DECFSZ	WREG, W, ACCESS 
	BRA	S6_15_DATA
	;
	; S6.14: DISP_TEXT command received.
	;
	;   ___7______6______5______4______3______2______1______0__
	;  |                                  |                    |
	;  |                0                 |          7         | YY_COMMAND
	;  |______|______|______|______|______|______|______|______|
	;  |      |      |      |      |                           |
	;  |   0  |   0  |   0  |   0  |            12             | (not saved)
	;  |______|______|______|______|______|______|______|______|
	;  |      |      |                                         |
	;  |   0  |   0  |                N                        | YY_BUFFER+0
	;  |______|______|______|______|______|______|______|______|
	;  |                                                       |
	;  |                Character code 0                       | YY_BUFFER+1
	;  |______|______|______|______|______|______|______|______|
	;  |                                                       |
	;  |                Character code 1                       | YY_BUFFER+2
	;  |______|______|______|______|______|______|______|______|
	;                              :
	;                              :
	;   _______________________________________________________
	;  |                                                       |
	;  |                Character code N-1                     | YY_BUFFER+N
	;  |______|______|______|______|______|______|______|______|
	;  |      |                                                |
	;  |   0  |   1      0      1      0      1      0      1  | YY_DATA
	;  |______|______|______|______|______|______|______|______|
	;
	; Validate inputs
	;
	INCF	YY_BUFFER, W, ACCESS		; expecting N+1 bytes
	SUBWF	YY_BUF_IDX, W, ACCESS		; input bytes in packet
	BC	S6_14_VALID			; N+1 bytes received (plus final)? good.
	GOTO	S6_KEEP_LOOKING			; input too small? keep going

S6_14_VALID:
	BZ	S6_14_DISP_TEXT			; exact byte length? great, execute command
	GOTO	ERR_COMMAND			; oops, too many bytes received!

S6_14_DISP_TEXT:
	;
	; XXX display YYBUFFER[1]..YYBUFFER[YY_BUFFER[0]] on scoreboard
	;
	CLRF	YY_STATE, ACCESS
	RETURN

S6_15_DATA:
; XXX needs to be rewritten for the new readerboards
; XXX needs to be rewritten for the new readerboards
; XXX needs to be rewritten for the new readerboards
	DECFSZ	WREG, W, ACCESS 
	BRA	S6_16_DATA
	;
	; S6.15: DISP_BITMAP command received.
	;
	;   ___7______6______5______4______3______2______1______0__
	;  |                                  |                    |
	;  |                0                 |          7         | YY_COMMAND
	;  |______|______|______|______|______|______|______|______|
	;  |      |      |      |      |                           |
	;  |   0  |   0  |   0  |   0  |            13             | (not saved)
	;  |______|______|______|______|______|______|______|______|
	;  |                                                       |
	;  | (0,0)  (0,1) ...                                      | YY_BUFFER+0
	;  |______|______|______|______|______|______|______|______|
	;                              :
	;                              :
	;   _______________________________________________________
	;  |                                                       |
	;  |                                          (6,62) (6,63)| YY_BUFFER+55
	;  |______|______|______|______|______|______|______|______|
	;  |      |                                                |
	;  |   0  |   1      1      0      0      1      1      0  | YY_DATA
	;  |______|______|______|______|______|______|______|______|
	;
	; Validate inputs
	;
	MOVLW	.56                		; expecting 56 bytes
	SUBWF	YY_BUF_IDX, W, ACCESS		; input bytes in packet
	BC	S6_15_VALID			; 56 bytes received (plus final)? good.
	GOTO	S6_KEEP_LOOKING			; input too small? keep going

S6_15_VALID:
	BZ	S6_15_DISP_BITMAP		; exact byte length? great, execute command
	GOTO	ERR_COMMAND			; oops, too many bytes received!

S6_15_DISP_BITMAP:
	;
	; XXX display YYBUFFER[0]..YYBUFFER[55] as raw bits
	;
	CLRF	YY_STATE, ACCESS
	RETURN

S6_16_DATA:
	DECFSZ	WREG, W, ACCESS 
	BRA	S6_17_DATA
	;
	; S6.16: CF_SET_QS_PARAMS command received
	;
	;   ___7______6______5______4______3______2______1______0__
	;  |                                  |                    |
	;  |                0                 |          7         | YY_COMMAND
	;  |______|______|______|______|______|______|______|______|
	;  |      |      |      |      |                           |
	;  |   0  |   1  |   1  |   1  |             6             | (not saved)
	;  |______|______|______|______|______|______|______|______|
	;  |                                                       |
	;  |                Lockout time (x 1/120 sec)             | YY_BUFFER+0
	;  |______|______|______|______|______|______|______|______|
	;  |      |                                                |
	;  |   0  |   0      1      1      0      0      1      0  | YY_BUFFER+1
	;  |______|______|______|______|______|______|______|______|
	;  |      |                                                |
	;  |   0  |   1      0      1      1      0      1      0  | YY_DATA
	;  |______|______|______|______|______|______|______|______|
	;
	; Validate inputs
	;
	MOVLW	.2                		; expecting 2 bytes
	SUBWF	YY_BUF_IDX, W, ACCESS		; input bytes in packet
	BC	S6_16_VALID			; 2 bytes received (plus final)? good.
	GOTO	S6_KEEP_LOOKING			; input too small? keep going

S6_16_VALID:
	BZ	S6_16_CF_SET_QS_PARAMS		; exact byte length? great, execute command
	GOTO	ERR_COMMAND			; oops, too many bytes received!

S6_16_CF_SET_QS_PARAMS:
	;
	; Validate first sentinel byte
	;
	MOVLW	0x32
	CPFSEQ	YY_BUFFER+1, ACCESS
	GOTO	ERR_COMMAND
	;
	; set params
	;
	MOVFF	YY_BUFFER, QUIZSHOW_LCKTM
	CLRF	YY_STATE, ACCESS
	RETURN

S6_17_DATA:
	ERR_BUG	0x05, ERR_CLASS_OVERRUN
