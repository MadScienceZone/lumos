; vim:set syntax=pic ts=8:
;
;@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
;@@                                                                         @@
;@@ @      @   @  @   @   @@@    @@@          LUMOS: LIGHT ORCHESTRATION    @@
;@@ @      @   @  @@ @@  @   @  @   @         SYSTEM FIRMWARE VERSION 3.0   @@
;@@ @      @   @  @ @ @  @   @  @                                           @@
;@@ @      @   @  @   @  @   @   @@@   @@@@@  FOR 4-, 24-, AND 48-CH AC/DC  @@
;@@ @      @   @  @   @  @   @      @         LUMOS CONTROLLER UNITS        @@
;@@ @      @   @  @   @  @   @  @   @         BASED ON THE PIC18F4685 AND   @@
;@@ @@@@@   @@@   @   @   @@@    @@@          PIC18F14K50 CHIPS             @@
;@@                                                                         @@
;@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
;
; Copyright (c) 2015 by Steven L. Willoughby, Aloha, Oregon, USA.  All Rights
; Reserved.  Released under the terms and conditions of the Open Software
; License, version 3.0.
;
; Portions based on earlier code copyright (c) 2004, 2005, 2006, 2007
; Steven L. Willoughby, Aloha, Oregon, USA.  All Rights Reserved.
;
; -*- -*- -* -*- -*- -*- -*- -*- -* -*- -*- -*- -*- -*- -* -*- -*- -*- -*- -*-
;
; SSR state register bits
;
;==============================================================================
; SSR STATE BITS      
;==============================================================================
;                     ___7______6______5______4______3______2______1______0__
; SSR_STATE          |      |      |SLICE |PRIV_ |SLEEP |DRAIN |PRE_  |TEST_ |
;                    |INCYC |PRECYC| _UPD | MODE |_MODE |_TR   |PRIV  |MODE  |
;                    |______|______|______|______|______|______|______|______|
; SSR_STATE2         |TEST_ |TEST_ |TEST_ |ALL_  |PRIV_ |INHIBI|MSB_  |LITER |
;                    |PAUSE |UPD   |BUTTON|OFF   |FORBID|T_OUTP|ESC   |AL_ESC|
;                    |______|______|______|______|______|UT____|______|______|
;
INCYC		EQU	7
PRECYC		EQU	6
SLICE_UPD	EQU	5
PRIV_MODE	EQU	4
SLEEP_MODE	EQU	3
DRAIN_TR	EQU	2
PRE_PRIV	EQU	1
TEST_MODE	EQU 	0

TEST_PAUSE	EQU	7
TEST_UPD	EQU	6
TEST_BUTTON	EQU	5
ALL_OFF		EQU	4
PRIV_FORBID	EQU	3
INHIBIT_OUTPUT	EQU	2
MSB_ESC		EQU	1
LITERAL_ESC	EQU	0
