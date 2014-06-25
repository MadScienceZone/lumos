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
#define LUMOS_CHIP_QSCC         0x45	; Private code; custom hardware
#define LUMOS_CHIP_QSRC         0x46	; Private code; custom hardware
;
; Un-comment one of these to select board type for this ROM image:
;
;#define LUMOS_CHIP_TYPE		LUMOS_CHIP_MASTER
;#define LUMOS_CHIP_TYPE		LUMOS_CHIP_SLAVE
;#define LUMOS_CHIP_TYPE		LUMOS_CHIP_STANDALONE
;#define LUMOS_CHIP_TYPE		LUMOS_CHIP_4CHANNEL
;#define LUMOS_CHIP_TYPE		LUMOS_CHIP_QSCC
#define LUMOS_CHIP_TYPE		LUMOS_CHIP_QSRC
;
;
;
#define LUMOS_ZC		0x55
#define LUMOS_INTERNAL		0x58

 IF LUMOS_CHIP_TYPE == LUMOS_CHIP_MASTER || LUMOS_CHIP_TYPE == LUMOS_CHIP_SLAVE
  #define LUMOS_SLICE_TIMER LUMOS_ZC
 ELSE
  IF LUMOS_CHIP_TYPE == LUMOS_CHIP_STANDALONE || LUMOS_CHIP_TYPE == LUMOS_CHIP_4CHANNEL || LUMOS_CHIP_TYPE == LUMOS_CHIP_QSCC || LUMOS_CHIP_TYPE == LUMOS_CHIP_QSRC
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
  #define QSCC_PORT         (0)
 ELSE
  IF LUMOS_CHIP_TYPE == LUMOS_CHIP_SLAVE
   #define ROLE_MASTER      (0)
   #define ROLE_SLAVE       (1)
   #define ROLE_STANDALONE  (0)
   #define NUM_CHANNELS     (.48)
   #define QSCC_PORT        (0)
  ELSE
   IF LUMOS_CHIP_TYPE == LUMOS_CHIP_STANDALONE
    #define ROLE_MASTER     (0)
    #define ROLE_SLAVE      (0)
    #define ROLE_STANDALONE (1)
    #define NUM_CHANNELS    (.24)
    #define QSCC_PORT       (0)
   ELSE
    IF LUMOS_CHIP_TYPE == LUMOS_CHIP_4CHANNEL
     #define ROLE_MASTER     (0)
     #define ROLE_SLAVE      (0)
     #define ROLE_STANDALONE (1)
     #define NUM_CHANNELS    (.4)
     #define QSCC_PORT       (0)
    ELSE
     IF LUMOS_CHIP_TYPE == LUMOS_CHIP_QSCC
      #define ROLE_MASTER     (0)
      #define ROLE_SLAVE      (0)
      #define ROLE_STANDALONE (1)
      #define NUM_CHANNELS    (.14)
      #define QSCC_PORT       (1)
     ELSE
      IF LUMOS_CHIP_TYPE == LUMOS_CHIP_QSRC
       #define ROLE_MASTER     (0)
       #define ROLE_SLAVE      (0)
       #define ROLE_STANDALONE (1)
       #define NUM_CHANNELS    (.20)
       #define QSCC_PORT       (1)
      ELSE
       ERROR "Invalid LUMOS_CHIP_TYPE"
      ENDIF
     ENDIF
    ENDIF
   ENDIF
  ENDIF
 ENDIF

#define LUMOS_ARCH_4685  (0x4685)
#define LUMOS_ARCH_14K50 (0x1450)

 IF LUMOS_CHIP_TYPE == LUMOS_CHIP_MASTER || LUMOS_CHIP_TYPE == LUMOS_CHIP_SLAVE || LUMOS_CHIP_TYPE == LUMOS_CHIP_STANDALONE || LUMOS_CHIP_TYPE == LUMOS_CHIP_QSCC || LUMOS_CHIP_TYPE == LUMOS_CHIP_QSRC
  #define LUMOS_ARCH LUMOS_ARCH_4685
  PROCESSOR 18F4685
  #include <p18f4685.inc>
 ELSE
  IF LUMOS_CHIP_TYPE == LUMOS_CHIP_4CHANNEL
   #define LUMOS_ARCH LUMOS_ARCH_14K50
   PROCESSOR 18F14K50
   #include <p18f14k50.inc>
  ELSE
   ERROR "Invalid LUMOS_CHIP_TYPE"
  ENDIF
 ENDIF

; set DMX_ENABLED to 1 to include the experimental DMX-handling code.
#define DMX_ENABLED 0
;
; The following public symbols can be used after this file is
; included (and this file should be included everywhere before
; anything else is included, and in lieu of PROCESSOR directives
; or #includes which bring in processor-specific bits--this file
; will do that for you):
;
; LUMOS_CHIP_TYPE:  Will be one of the following, to show what the intent
;	            of the target chip will be and what its particular 
;                   I/O pin assignments are, role in the overall circuit, etc.
;		    (use the ROLE_* values where possible, though, in your logic)
;
;	LUMOS_CHIP_MASTER	- 48-channel (2-CPU) controller, master CPU
;	LUMOS_CHIP_SLAVE	- 48-channel (2-CPU) controller, slave CPU
;	LUMOS_CHIP_STANDALONE	- 24-channel (1-CPU) controller, sole CPU
;	LUMOS_CHIP_4CHANNEL	- 4-channel  (1-CPU) controller, sole CPU
;       LUMOS_CHIP_QSCC         - private configuration for custom hardware
;       LUMOS_CHIP_QSRC         - private configuration for custom hardware
;
; LUMOS_SLICE_TIMER: Will be one of the following, to specify where the PWM
;		    slice timer sync pulse is coming from:
;
;	LUMOS_ZC	- Hardware zero-crossing detector to PIC interrupt pin
;	LUMOS_INTERNAL	- Internal timing system (using PIC timer module)
;
; LUMOS_ARCH:       Will be one of the following, to show what PIC device
;		    is targeted, strictly to determine chip-specific details,
;                   not how Lumos is using it.
;
;	"14K50"	    	- The PIC18F14K50
;	"4685"      	- The PIC18F4685
;
; ROLE_MASTER		- (bool) true if this chip is the master in master/slave arrangement
; ROLE_SLAVE		- (bool) true if this chip is the slave in master/slave arrangement
; ROLE_STANDALONE	- (bool) true if this is the only chip, must run entire board function
; NUM_CHANNELS		- (int) number of output SSR channels
#endif
