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
; This hooks into the Lumos command interpretation code so that we handle
; globally-recognized commands, which isn't something Lumos controllers do.
;
; Force global commands to be our address
;
; Context: SIO data bank selected
; SIO_INPUT contains command byte on input.
; RETURN from here will end command interpretation, so if we branch to
; a command handler, its return will go back to our caller.
;
	MOVLW	b'10001111'	; 8F: Global Blackout
	CPFSEQ	SIO_INPUT, BANKED
	BRA	QSCC_G_C_1
	GOTO	S0_CMD0

QSCC_G_C_1:
	GOTO	S0_CMD0
	MOVLW	b'11011111'	; DF: Global Start
	CPFSEQ	SIO_INPUT, BANKED
	BRA	QSCC_G_C_2
	GOTO	QSCC_CMD5_START

QSCC_G_C_2:
