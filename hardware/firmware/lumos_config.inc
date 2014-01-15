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
; Copyright (c) 2012 by Steven L. Willoughby, Aloha, Oregon, USA.  All Rights
; Reserved.  Released under the terms and conditions of the Open Software
; License, version 3.0.
;
; Portions based on earlier code copyright (c) 2004, 2005, 2006, 2007
; Steven L. Willoughby, Aloha, Oregon, USA.  All Rights Reserved.
;
; -*- -*- -* -*- -*- -*- -*- -*- -* -*- -*- -*- -*- -*- -* -*- -*- -*- -*- -*-
;
; Configuration options.  Set these as desired and then re-assemble the
; code to produce the desired version of the ROM.
;
; 
;==============================================================================
; CONFIGURATION OPTIONS
;==============================================================================
#ifndef LUMOS_CONFIG_INC
#define LUMOS_CONFIG_INC
#define LUMOS_CHIP_MASTER	0x41	; 48-channel master CPU
#define LUMOS_CHIP_SLAVE	0x42	; 48-channel slave CPU
#define LUMOS_CHIP_STANDALONE	0x43	; 24-channel CPU
#define LUMOS_CHIP_4CHANNEL	0x44	; 4-channel CPU
;
; Un-comment one of these to select board type for this ROM image:
;
;#define LUMOS_CHIP_TYPE		LUMOS_CHIP_MASTER
;#define LUMOS_CHIP_TYPE		LUMOS_CHIP_SLAVE
;#define LUMOS_CHIP_TYPE		LUMOS_CHIP_STANDALONE
#define LUMOS_CHIP_TYPE			LUMOS_CHIP_4CHANNEL
;
;
;
#define LUMOS_ZC		0x55
#define LUMOS_INTERNAL		0x58

 IF LUMOS_CHIP_TYPE == LUMOS_CHIP_MASTER || LUMOS_CHIP_TYPE == LUMOS_CHIP_SLAVE
  #define LUMOS_SLICE_TIMER LUMOS_ZC
 ELSE
  IF LUMOS_CHIP_TYPE == LUMOS_CHIP_STANDALONE || LUMOS_CHIP_TYPE == LUMOS_CHIP_4CHANNEL
   #define LUMOS_SLICE_TIMER LUMOS_INTERNAL
  ELSE
   ERROR "LUMOS_CHIP_TYPE must be set to MASTER, SLAVE, 4CHANNEL, or STANDALONE"
  ENDIF
 ENDIF
 
 IF LUMOS_SLICE_TIMER != LUMOS_ZC && LUMOS_SLICE_TIMER != LUMOS_INTERNAL
  ERROR "LUMOS_SLICE_TIMER must be set to ZC or INTERNAL"
 ENDIF


 IF LUMOS_CHIP_TYPE == LUMOS_CHIP_MASTER
  #define ROLE_MASTER       (1)
  #define ROLE_SLAVE        (0)
  #define ROLE_STANDALONE   (0)
  #define NUM_CHANNELS      (.48)
 ELSE
  IF LUMOS_CHIP_TYPE == LUMOS_CHIP_SLAVE
   #define ROLE_MASTER      (0)
   #define ROLE_SLAVE       (1)
   #define ROLE_STANDALONE  (0)
   #define NUM_CHANNELS     (.48)
  ELSE
   IF LUMOS_CHIP_TYPE == LUMOS_CHIP_STANDALONE
    #define ROLE_MASTER     (0)
    #define ROLE_SLAVE      (0)
    #define ROLE_STANDALONE (1)
    #define NUM_CHANNELS    (.24)
   ELSE
    IF LUMOS_CHIP_TYPE == LUMOS_CHIP_4CHANNEL
     #define ROLE_MASTER     (0)
     #define ROLE_SLAVE      (0)
     #define ROLE_STANDALONE (1)
     #define NUM_CHANNELS    (.4)
    ELSE
     ERROR "Invalid LUMOS_CHIP_TYPE"
    ENDIF
   ENDIF
  ENDIF
 ENDIF

IF LUMOS_CHIP_TYPE == LUMOS_CHIP_MASTER || LUMOS_CHIP_TYPE == LUMOS_CHIP_SLAVE || LUMOS_CHIP_TYPE == LUMOS_STANDALONE
 #define LUMOS_ARCH "4685"
 PROCESSOR 18F4685
 #include <p18f4685.inc>
ELSE
 IF LUMOS_CHIP_TYPE == LUMOS_CHIP_4CHANNEL
  #define LUMOS_ARCH "14K50"
  PROCESSOR 18F14K50
  #include <p18f14k50.inc>
 ELSE
  ERROR "Invalid LUMOS_CHIP_TYPE"
 ENDIF
ENDIF
#endif
