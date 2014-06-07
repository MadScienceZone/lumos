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
; Based on Lumos controller firmware 3.0, PWD-2 firmware (particularly 
; readerboard controls), and previous Quizshow hardware designs.  All of the
; above are copyright (c) Steven L. Willoughby, All Rights Reserved.
;
; ************                                                           /\
; * WARNING! *    EXPERIMENTAL DESIGN FOR EDUCATIONAL PURPOSES          /  \
; * WARNING! *                USE AT YOUR OWN RISK!                    / !  \
; ************                                                        /______\
; 
; PLEASE READ AND BE SURE YOU UNDERSTAND THE FOLLOWING SAFETY WARNINGS:
;
; THIS FIRMWARE AND THE ACCOMPANYING HARDWARE AND CONTROLLING SOFTWARE ARE
; EXPERIMENTAL "HOBBYIST" DESIGNS AND ARE NOT INTENDED FOR GENERAL CONSUMER USE
; OR FOR ANY APPLICATION WHERE THERE IS ANY POSSIBILITY OF RISK OF INJURY,
; PROPERTY DAMAGE, OR ANY OTHER SITUATION WHERE ANY FAILURE OF THE FIRMWARE,
; SOFTWARE AND/OR HARDWARE COULD RESULT IN HARM TO ANYONE OR ANYTHING.  
;
; THIS FIRMWARE, SOFTWARE, AND/OR HARDWARE ARE NOT INTENDED NOR RECOMMENDED 
; FOR APPLICATIONS INVOLVING LIFE SUPPORT OR SAFETY-CRITICAL SYSTEMS, RUNNING 
; FIREWORKS/PYROTECHNIC DISPLAYS, ETC.  
;
; BY OBTAINING AND USING THIS FIRMWARE, AND/OR ACCOMPANYING HARDWARE AND/OR 
; CONTROLLING SOFTWARE, YOU AGREE TO THESE CONDITIONS AND THAT TO THE FULLEST 
; EXTENT OF APPLICABLE LAW, THE ABOVE-LISTED ITEMS AND ALL ACCOMPANYING 
; DOCUMENTATION AND OTHER MATERIALS ARE PROVIDED TO YOU AS-IS, WITHOUT WARRANTY 
; OF ANY KIND, EXPRESSED OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE IMPLIED
; WARRANTIES OF MERCHANTABILITY OR FITNESS FOR ANY PARTICULAR PURPOSE.  YOU 
; FURTHER AGREE TO DEFEND, INDEMNIFY, AND HOLD BLAMELESS, THE AUTHOR, STEVEN 
; L. Willoughby AND ANY OF HIS AGENTS AND ASSOCIATES ASSISTING WITH THIS WORK, 
; FROM ANY DAMAGES DIRECT OR INCIDENTAL ARISING FROM THE USE OF, OR INABILITY 
; TO USE, THE ABOVE-LISTED PRODUCTS.
; 
;
; Copyright (c) 2014 by Steven L. Willoughby, Aloha, Oregon, USA.  
; All Rights Reserved.  Quiz Show portions are unreleased trade secret
; information.
;
; Based on previous works by the same author, some of which are released
; under the Open Software License, version 3.0, which portions are available
; separately for free download.
;
; -*- -*- -* -*- -*- -*- -*- -*- -*- -*- -*- -*- -*- -*- -* -*- -*- -*- -*- -*-
;
; Main implementation module.
;
#include "lumos_config.inc"
#include "lumos_set_ssr.inc"
#include "quizshow_config.inc"
#include "qscc_hook_main_pins.inc"
	RADIX		DEC
;#include "serial-io.inc"

; Works on Software Alchemy Quiz Show QSCC and QSRC boards revision 4.0.
;
; N.B. THE BOARD SELECT BITS IN LUMOS_CONFIG.INC MUST BE SELECTED
; FOR THE TARGET CONFIGURATION!  EACH ROM IS DIFFERENT!
;
; Target Microcontroller is PIC18F4685, Q=40MHz (100nS instruction cycle)
;
; Serial control (RS-485) at 19.2kbps by default.
; Configurable from 300 to 250000 baud.
;
; OPTION BUTTON:
; XXX The Lumos controllers have an OPTION button which starts configuration
; XXX mode.  QS*C boards don't have those, so instead boot the unit while
; XXX holding down the A and D buttons (QSCC) or the L2 and L0 buttons (QSRC)
; XXX to enter configuration mode.
; 
;=============================================================================
; IMPLEMENTATION NOTES
;-----------------------------------------------------------------------------
;
; The QUIZSHOW controller firmware consists of a number of somewhat 
; independent subsystems:
; 
; LUMOS
;	The QSCC and QSRC boards are also Lumos SSR controllers which implement
;	most of the standard Lumos commands.  The various lights used by the
;	quiz show are mapped to Lumos channels.  The Lumos firmware is included
;	into the quizshow firmware, with some special switches enabled to adapt
;	it to this hardware.
;
; START
;	Initializes the microcontroller, starts up the required peripherals,
;	and enters the main loop
;
; SIO
;	Handles all serial I/O operations in the background (interrupt-driven)
;	so the rest of the code only needs to be concerned with higher-level
;	reads and writes.  Buffers hold 256 characters each of input and output.
;
; ISR
;	The interrupt service routine manages a set of counters and timers:
;	1. We run a 120 Hz timer which provides timing for the dimmers.
;
; MAIN_LOOP
;	Manages the display of the readerboards.
;	Updates the status of the SSR lines if it's time to do so
;	Receives a character from the serial line if one's waiting
;
; INTERPRETER
;	When a byte is received on the serial line, it is processed by
;	a small state machine.  The current state is held in YY_STATE (named
;	in honor of the venerable yacc).
;
;-----------------------------------------------------------------------------
; Command Protocol:
;                     ___7______6______5______4______3______2______1______0__
; Command Byte:      |      |                    |                           |
;                    |   1  |    Command code    |   Target device address   |
;                    |______|______|______|______|______|______|______|______|
;
; Any byte with its MSB set is the beginning of a command.  If the target 
; device matches this unit's address, the state machine kicks into gear and
; processes the command (which may require some following data bytes, all
; of which must have their MSB cleared).  Otherwise, the unit ignores the
; byte.
;
;                     ___7______6______5______4______3______2______1______0__
; Extended Command:  |      |                    |                           |
;                    |   1  |          7         |   Target device address   |
;                    |______|______|______|______|______|______|______|______|
;                    |      |                                                |
;                    |   0  |                  Command code                  |
;                    |______|______|______|______|______|______|______|______|
;
; The most common commands are given ID 0-6 so that they may be sent in as few
; bytes as possible (as few as a single byte), but we have more than 8 commands
; so we have an extended code.  If the command code is 7 (all bits set), then
; the following byte contains the actual command code which may be any value
; from 0-127.
;
;                     ___7______6______5______4______3______2______1______0__
; Data Byte:         |      |                                                |
;                    |   0  |                      Data                      |
;                    |______|______|______|______|______|______|______|______|
;
; Any byte with its MSB cleared is a data byte, and is ignored unless we're
; in the middle of interpreting a multi-byte command, in which case it's interpreted
; appropriately as data supporting the command being executed.  This way, other
; devices which share the same protocol format but not necessarily a compatible
; command set may safely know which bytes can be ignored without knowing the
; details of each other's command sets.
;
; Two special bytes are recognized:
;
;                     ___7______6______5______4______3______2______1______0__
; MSB Escape:        |      |                                                |
;                    |   0  |   1      1      1      1      1      1      0  |
;                    |______|______|______|______|______|______|______|______|
;
; If this ($7E) byte is received, it is ignored but the next byte received will
; have its MSB bit set.  This allows data bytes to have full 8-bit values without
; violating the communication protocol described above.  That second byte is not
; interpreted further.
;
;                     ___7______6______5______4______3______2______1______0__
; Literal Escape     |      |                                                |
;                    |   0  |   1      1      1      1      1      1      1  |
;                    |______|______|______|______|______|______|______|______|
;
; If this ($7F) byte is received, it is ignored but the next byte is accepted
; as-is without further interpretation.
;
; Specific Example Cases of interest:
; 	Sequence    Resulting byte
; 	$7E $7E     $FE
; 	$7E $7F     $FF
; 	$7F $7E     $7E
; 	$7F $7F     $7F
;
; A command byte (received with MSB already set) trumps all of the above.  It is
; taken as the start of a command and the escape sequence in progress is canceled.
;
; Commands recognized (L indicates Lumos commands):
;
;   COMMAND  CODE  BITS
;L  BLACKOUT 0     1000aaaa
;L  ON_OFF   1     1001aaaa 0scccccc		Turn channel <c> on (<s>=1) or off (<s>=0)
;L  SET_LVL  2     1010aaaa 0hcccccc 0vvvvvvv    Set dimmer level <v>:<h> on channel <c>
;L  BULK_UPD 3     1011aaaa 0mcccccc ...		Bulk-upload multiple channel levels
;L  RAMP_LVL 4     1100aaaa Cdcccccc ...         Ramp channel <c> smoothly up (<d>=1) or down (<C>=1 cycle)
;   SCAN_ST  5     1101aaaa                      Start scanning buttons
;   SCAN_Q   6     1110aaaa 0000000s             Read scan results / Stop
;   EXTENDED 7     1111aaaa                      Extended command, decoded further in next byte
;L@ SLEEP    7+0   1111aaaa 00000000 01011010 01011010  Put unit to sleep
;L@ WAKE     7+1   1111aaaa 00000001 01011010 01011010  Take unit out of sleep mode
;L  SHUTDOWN 7+2   1111aaaa 00000010 01011000 01011001  Take unit completely offline
;L< QUERY    7+3   1111aaaa 00000011 00100100 01010100  Report device status
;X! DEF_SEQ  7+4   1111aaaa 00000100 0iiiiiii ...       Define sequence <i>
;X  EXEC_SEQ 7+5   1111aaaa 00000101 0iiiiiii           Execute sequence <i> (0=stop)
;X! CLR_SEQ  7+8   1111aaaa 00001000 01000011 01000001  Erase all stored sequences
;L  XPRIV    7+9   1111aaaa 00001001                    Forbid priviliged mode
;            7+10  1111aaaa 00001010                    Reserved for future use
;             :        :        :                           :     :     :    : 
;            7+28  1111aaaa 00011100                    Reserved for future use                 
;   OUT_SCAN 7+29  1111aaaa 00011101			SCAN_Q reply
;L  OUT_NAK  7+30  1111aaaa 00011110                    QUERY NAK                               
;L  OUT_RPLY 7+31  1111aaaa 00011111 ...                Reply to QUERY command_________________ 
;   IC_***** 7+32  11110000 00100000			Reserved (Lumos internal)
;             :        :        :                           :     :   :      :         ////////
;            7+63  11110000 00111111                    Reserved for new commands______////////
;*! CF_PHASE 7+64  1111aaaa 010000pp 0ppppppp 01010000 01001111   Phase offset=<p>       CONFIG
;*! CF_ADDR  7+96  1111aaaa 0110AAAA 01001001 01000001 01000100   Change address to <A>  ||||||
;*  CF_NOPRV 7+112 1111aaaa 01110000                              Leave privileged mode  ||||||
;*  CF_CONF  7+113 1111aaaa 01110001 ...                          Configure device       ||||||
;*! CF_BAUD  7+114 1111aaaa 01110010 0bbbbbbb 00100110            Set baud rate to <b>   ||||||
;*! CF_RESET 7+115 1111aaaa 01110011 00100100 01110010            Reset factory defaults ||||||
;*  CF_XPRIV 7+116 1111aaaa 01110100                              Forbid priviliged mode ||||||
;*           7+117 1111aaaa 01110101                     Reserved for future config cmd  ||||||
;*                     :        :                            :     :     :      :    :   ||||||
;*           7+127 1111aaaa 01111111                     Reserved for future config cmd__||||||
;
; Legend:
;   X Not yet implemented; planned for future; subject to change
;   @ Unit may automatically take this action
;   * Privileged configuration-mode command
;   ! Permanent effect (written to EEPROM)
;   < Command generates response data (back to host)
;   a Device address (0-15)
;   b Baud rate code (0-127), but units may only define a small subset of those values
;   c Output channel (0-63, but unit may only support a lesser number)
;   d Direction: up (<d>=1) or down (<d>=0).
;   h High-res level bit (LSB of 8-bit value when in high-res mode)
;   m Mode (1=high-res, 0=low-res)
;   n Number of items affected
;   s Output state: 0=off, 1=on
;   v Value of dimmer (0-127) (most significant 7 bits of dimmer value)
;
; Payloads for many-byte commands
;
; BULK_UPD:  00cccccc 0nnnnnnn v0 v1 v2 ... vn 01010101
;	Updates <n>+1 channels starting at <c>, giving <v> values for each as per SET_LVL.
;
; RAMP_LVL:  Cdcccccc 0sssssss 0ttttttt   Channel <c> up/down in <s>+1 steps every <t>+1/120 sec
;
; DEF_SEQ:   0iiiiiii 0nnnnnnn (...)*<n+1> 01000100 01110011  Define sequence <i> of length <n+1>
;                                                             0 is boot sequence, 1-63 is EEPROM
;                                                             64-127 is RAM.
;
; CF_BAUD:   Values recognized:
;	00000000 ($00)	    300 baud
;	00000001 ($01)      600
;	00000010 ($02)    1,200
;	00000011 ($03)    2,400
;	00000100 ($04)    4,800
;	00000101 ($05)    9,600
;	00000110 ($06)   19,200
;	00000111 ($07)   38,400
;	00001000 ($08)   57,600
;	00001001 ($09)  115,200
;	00001010 ($0A)  250,000
;
;
; Response packet from QUERY command (37 bytes):
; note the ROM version byte also serves to indicate the format of the response
; bytes which follow.  If the query packet format changes, the ROM version byte
; MUST also change.
;
;    1111aaaa 00011111 00110000 0ABCDdcc 0ccccccc 0ABCDqsf 0ABCDXpp 0ppppppp 
;        \__/           \_/\__/  \__/|\_________/  \__/|||  \__/|\_________/  
;          |             maj |     | |   |           | |||   |  |      `--phase
;          `--reporting    minor   | |   `--DMX      | |||   |  `--config locked?
;              unit addr  rom      | |      channel  | |||   `--active
;                         vers.    | |               | ||`--mem full?
;                                  | `--DMX mode?    | |`--sleeping?
;                                  `--configured     | `--config mode?
;                                                    `--masks
;
;    0eeeeeee 0eeeeeee 0MMMMMMM 0MMMMMMM 0X0iiiii 0xxxxxxx 
;     \______________/  \______________/  | \___/  \_____/
;        `--EEPROM free    `--RAM free    |   |       `--executing seq.
;                                         |   `--device model
;                                         `--seq running?
;
;    0owE0000 0IIIIIII 0iiiiiii 0PPPPPPP	Sensor trigger info for A
;    0owE0001 0IIIIIII 0iiiiiii 0PPPPPPP	Sensor trigger info for B
;    0owE0010 0IIIIIII 0iiiiiii 0PPPPPPP	Sensor trigger info for C
;    0owE0011 0IIIIIII 0iiiiiii 0PPPPPPP	Sensor trigger info for D
;
;    0fffffff 0fffffff 000000pp 0ppppppp ssssssss ssssssss 00110011
;    \______/ \______/       \_________/ \______S/N______/
;        |        |               `--phase (channels 24-47)
;        |        `--fault code (channels 24-47)
;        `--fault code (channels 0-23)
;
; Response to SCAN_Q query commands:
; Note that the ROM version dictates these changes too, so if this format
; changes the ROM version MUST change (as reported in the QUERY response
; above).
;                               31       23       15       7      0
;    1111aaaa 00011101 0R0nnnnn tttttttt tttttttt tttttttt tttttttt ...
;        \__/           | \___/ \_________________________________/
;          |            |   |                    | (x n)
;          `--reporting | number of    0=not pressed yet
;              unit addr| buttons     >0=microseconds elapsed before press
;                       | reported
;                       0=scanning stopped
;                       1=scanner is still running
;                      
;    01010001 00101010 
;
; QSCC sends 6 buttons: X, L, A, B, C, D.
; QSRC sends 10 buttons: X0, L0, X1, L1, X2, L2, X3, L3, X4, L4.  
;
; Also note that the controller is allowed to send OUT_NAK packets to the
; host in response to QUERY commands.  This does not complete the exchange,
; but serves to ask the host to continue waiting if the device won't be able
; to reply to the QUERY for long enough that it risks a timeout.  The host
; is under no obligation to respect the OUT_NAK packets.
;
;   1111aaaa 00011110 
;
; A controller MUST never send data except in response to an explicit
; request from the host.  Controllers MUST immediately cease sending
; data upon receiving any bytes on the network (this indicates that
; the host is no longer waiting for a reply but has moved on to something
; else or is querying another device now).  No further data may be sent
; until again explicitly asked for.
;
;
;                     _______________________________________________________
; Channel ID:        |      |      |                                         |
;                    |  0   | ON   |               Channel ID                |
;                    |______|______|______|______|______|______|______|______|
; The ON bit <6> determines whether the channel is being turned on (1) or 
; off (0) for the "Set/clear single channel" command.  it is ignored when
; setting the channel to a specific dimmer value.
;
;=============================================================================
; HARDWARE DESCRIPTION
;-----------------------------------------------------------------------------
;
; The controllers use the PIC18F4685 microcontroller, and have identical
; circuit boards, although the assignment of I/O pins is very different
; between them.
;
;  PIC18F4685 Microcontroller I/O pin assignments:
;
; QSRC    QSCC           ________   _________         QSCC    QSRC 
; BOARD:  BOARD:        |o       \_/         |        BOARD:  BOARD:
; /RESET  /RESET -->  1 | /MCLR RE3  PGD RB7 | 40 --> /AL     /X1R   
; /L1     /L     -->  2 | RA0        PGC RB6 | 39 --> /BL     /X1G    
; /X2     /X     -->  3 | RA1        PGM RB5 | 38 --> /CL     /X1B   
; /L0     /D     -->  4 | RA2            RB4 | 37 --> /DL     /L1R  
; /X0     /C     -->  5 | RA3            RB3 | 36 --> /FR     /X2R  
; /X2     /B     -->  6 | RA4       INT2 RB2 | 35 --> /FG     /X2G   
; /L2     /A     -->  7 | RA5       INT1 RB1 | 34 --> /FB     /X2B    
; /L2R    /LY    <--  8 | RE0       INT0 RB0 | 33 --> /FW     /X4R     
; /L3R    /LG    <--  9 | RE1            VDD | 32 --- +5V       
; /L0R    /LR    <-- 10 | RE2            VSS | 31 --- GND      
;            +5V --- 11 | VDD            RD7 | 30 --> D7      /X3R  
;            GND --- 12 | VSS            RD6 | 29 --> D6      /X3G  
;           xtal --- 13 | OSC            RD5 | 28 --> D5      /X3B  
;             +----- 14 | OSC            RD4 | 27 --- D4 ->   /X4 <-
; /X0B    /XB    <-- 15 | RC0         RX RC7 | 26 <-- Serial RxD
; /X0G    /XG    <-- 16 | RC1         TX RC6 | 25 --> Serial TxD
; /X0R    /XR    <-- 17 | RC2            RC5 | 24 --- PS0 ->  /L4 <-
; T/R     T/R    <-- 18 | RC3            RC4 | 23 --- PS1 ->  /X3 <- 
; /L3 ->  D0 <-  --- 19 | RD0            RD3 | 22 --> D3      /X4G  
; /X4B    D1     <-- 20 | RD1            RD2 | 21 --> D2      /L4R  
;                       |____________________|
;
;
; ========================================================================
; PROGRAM MEMORY MAP
; ______________________________________________________________________________
;
; 14K50 4685    _________________ ___
; $00000 $00000 | RESET Vector    | V_RST
; $00007 $00007 |_________________|___
; $00008 $00008 | High Int Vector | V_INT_H
; $00017 $00017 |_________________|___
; $00018 $00018 | Low Int Vector  | V_INT_L
; $0001F $0001F |_________________|
; $00020 $00020 |/////////////////|
; $000FF $000FF |/////////////////|___
; $00100 $00100 | Boot code       | _BOOT
;               |.................|___
;               | Interrupt hand- | _INT
;               |  lers           |      
;               |/////////////////|
; $007FF $007FF |/////////////////|___
; $00800 $00800 | Mainline code   | _MAIN
;               |.................|___
;           ??? | Device init     | LUMOS_CODE_INIT
;               |_________________|___
;           ??? | Serial I/O      | _SIO_CODE
;               | Module          |
;               |_________________|___
;               |/////////////////|
;               |/////////////////|
;               |/////////////////|
;               |/////////////////|
;               |/////////////////|___
; $02E00 $14000 | EEPROM defaults | _MAIN_EEPROM_TBL
; $02EFF $14FFF |_________________|___
; $02F00 $15000 |Serial I/O Mod   | _SIO_LOOKUP_TABLES
;               |lookup tables    |
;        $150FF |_________________|___
;        $15100 |                 |
;               |                 |
; $02FEF $16FEF |_________________|___
; $02FF0 $16FF0 |System Mfg Data  | _SYSTEM_MFG_DATA
; $02FFF $16FFF |_________________|___
; $03000 $17000 |                 | 
; $03FFF $17FFF |_________________|___
;               |/////////////////|
;               |/////////////////|
;$1FFFFF$1FFFFF |/////////////////|___
;
;
; ========================================================================
; DATA MEMORY MAP (4685)
;
;       _________________ ___ ___ ___ ___ ___ ___ ___ ___
; $000 | global state,   | _ADATA            BANK 0
; $05F | ISR data, etc.  |                (ACCESS AREA)
;      |.................|...............................
; $060 |                 |                   
;      |_________________|___ ___ ___ ___ ___ ___ ___ ___
; $100 | Serial I/O TxD  | _SIO_TXBUF_DATA   BANK 1
;      | ring buffer     |
;      |_________________|___ ___ ___ ___ ___ ___ ___ ___
; $200 | Serial I/O RxD  | _SIO_RXBUF_DATA   BANK 2
;      | ring buffer     |
;      |_________________|___ ___ ___ ___ ___ ___ ___ ___
; $300 | Serial I/O mod  | _SIO_VAR_DATA     BANK 3
;      | variable space  |
;      |_________________|___ ___ ___ ___ ___ ___ ___ ___
; $400 | SSR state data  | _SSR_DATA         BANK 4
;      |                 |
;      |_________________|___ ___ ___ ___ ___ ___ ___ ___
; $500 | Parser buffer   | _MAINDATA         BANK 5
;      |.................|
; $5?? |                 |
;      |_________________|___ ___ ___ ___ ___ ___ ___ ___
; $600 | Stored sequences| _SEQ_DATA         BANK 6
;      | (1792 bytes)    |
;              .
;              .                 
;              .                
;      |                 |
;      |                 |
;      |_________________|___ ___ ___ ___ ___ ___ ___ ___
; $C00 | Quizshow Data   | _QUIZSHOW_DATA    BANK C
;      |                 |
;      |_________________|___ ___ ___ ___ ___ ___ ___ ___
; $D00 |                 |                   BANK D
;      | CAN special     |
;      | function        |___ ___ ___ ___ ___ ___ ___ ___
; $E00 | registers       |                   BANK E
;      | (not used for   |
;      | Lumos)          |___ ___ ___ ___ ___ ___ ___ ___
; $F00 |                 |                   BANK F
;      |                 |
; $F5F |.................|...............................
; $F60 | Special Function|                (ACCESS AREA)
;      | (device) regis- |
;      | ters            |
; $FFF |_________________|___ ___ ___ ___ ___ ___ ___ ___
;
; ========================================================================
; EEPROM MEMORY
;
;
;       ______________            ______________ 
; $000 |_0xFF_________|     $010 | Saved        |
; $001 |_Baud_Rate____|     $011 | Sequence     |
; $002 |_Device_ID____|     $012 | Storage      |
; $003 | Phase     MSB|     $013 |       |      |
; $004 |_Offset____LSB|     $014 |       |      |
; $005 |_DMX_Slot__MSB|     $015 |       |      |
; $006 |_DMX_Slot__LSB|       .          .
; $007 |_Sensor_cfg___|       .          .
; $008 |______________|       .          .
; $009 |______________|     $3F9 |       |      |
; $00A |______________|     $3FA |       |      |
; $00B |______________|     $3FB | (1008 |      |
; $00C |______________|     $3FC | bytes)|      |
; $00D |______________|     $3FD |       |      |
; $00E |______________|     $3FE |       |      |
; $00F |_0x42_________|     $3FF |_______V______|
;
;

; ========================================================================
; DEVICES USED
;
; TMR0 L  120 Hz interrupt source (for boards without zero-crossing detector)
; TMR1
; TMR2 L  Dimmer slice timer (1/260 of a 120 Hz half-cycle)
; TMR3 L  Break detector for DMX reception
; UART L  SIO module
;=============================================================================
;
;------------------------------------------------------------------------------
; Significant Registers (ACCESS BANK)
;------------------------------------------------------------------------------
;
;                     ___7______6______5______4______3______2______1______0__
; ISR_TMPL_STATUS    |                                                       |
;                    | Temporary storage for STATUS register in low-pri ISR  |
;                    |______|______|______|______|______|______|______|______|
; ISR_TMPL_BSR       |                                                       |
;                    | Temporary storage for BSR register in low-priority ISR|
;                    |______|______|______|______|______|______|______|______|
; ISR_TMPL_WREG      |                                                       |
;                    | Temporary storage for W register in low-priority ISR  |
;                    |______|______|______|______|______|______|______|______|
; MY_ADDRESS         |                           |                           |
;                    |                           |       Unit address        |
;                    |______|______|______|______|______|______|______|______|
; PHASE_OFFSETH      |                                                       |
;                    |               Phase offset value (MSB)                |
;                    |______|______|______|______|______|______|______|______|
; PHASE_OFFSETL      |                                                       |
;                    |               Phase offset value (LSB)                |
;                    |______|______|______|______|______|______|______|______|
; SSR_STATE          |      |      |SLICE |PRIV_ |SLEEP |DRAIN |PRE_  |TEST_ |
;                    |INCYC |PRECYC| _UPD | MODE |_MODE |_TR   |PRIV  |MODE  |
;                    |______|______|______|______|______|______|______|______|
; SSR_STATE2         |TEST_ |TEST_ |TEST_ |ALL_  |PRIV_ |INHIBI|MSB_  |LITER |
;                    |PAUSE |UPD   |BUTTON|OFF   |FORBID|T_OUTP|ESC   |AL_ESC|
;                    |______|______|______|______|______|UT____|______|______|
; DMX_SLOTH          |DMX_EN|DMX_  |DMX_  |                           |DMX Sl|
;                    |      |SPEED |FRAME |                           |ot MSB|
;                    |______|______|______|______|______|______|______|______|
; DMX_SLOTL          |                                                       |
;                    |       Starting DMX Slot Number - 1 (low 8 bits)       |
;                    |______|______|______|______|______|______|______|______|
; YY_STATE           |                                                       |
;                    |                      Parser State                     |
;                    |______|______|______|______|______|______|______|______|
; YY_COMMAND         |                                                       |
;                    |                      Command Code                     |
;                    |______|______|______|______|______|______|______|______|
; YY_CMD_FLAGS       |                                                       |
;                    |               Command-specific Flag Bits              |
;                    |______|______|______|______|______|______|______|______|
; YY_DATA            |                                                       |
;                    |                      Command Data                     |
;                    |______|______|______|______|______|______|______|______|
; YY_LOOKAHEAD_MAX   |                                                       |
;                    |               Maximum length for look-ahead           |
;                    |______|______|______|______|______|______|______|______|
; YY_LOOK_FOR        |                                                       |
;                    |               Sentinel value to search for            |
;                    |______|______|______|______|______|______|______|______|
; YY_BUF_IDX         |                                                       |
;                    |     Offset in YY_BUFFER where we will write next      |
;                    |______|______|______|______|______|______|______|______|
; YY_NEXT_STATE      |                                                       |
;                    |     State to transition to when YY_LOOK_FOR is found  |
;                    |______|______|______|______|______|______|______|______|
; YY_YY              |                                                       |
;                    |     General-purpose storage for use inside commands   |
;                    |______|______|______|______|______|______|______|______|
; LAST_ERROR         |                                                       |
;                    |  Last error code encountered (cleared when reported)  |
;                    |______|______|______|______|______|______|______|______|
; CUR_PREH           |                                                       |
;                    |         Pre-cycle count-down ticks left (MSB)         |
;                    |______|______|______|______|______|______|______|______|
; CUR_PRE            |                                                       |
;                    |         Pre-cycle count-down ticks left (LSB)         |
;                    |______|______|______|______|______|______|______|______|
; CUR_SLICE          |                                                       |
;                    |      Slice number within active portion of cycle      |
;                    |______|______|______|______|______|______|______|______|
; TARGET_SSR         |NOT_MY|INVALI|                                         |
;                    | _SSR |D_SSR |    SSR number for current command       |
;                    |______|______|______|______|______|______|______|______|
; OPTION_DEBOUNCE    |                                                       |
;                    |      Counter to debounce OPTION button presses        |
;                    |______|______|______|______|______|______|______|______|
; OPTION_HOLD        |                                                       |
;                    |      Counter for how long OPTION button is held       |
;                    |______|______|______|______|______|______|______|______|
; TEST_CYCLE         |                                                       |
;                    |        Count-down of ZC cycles until next step        |
;                    |______|______|______|______|______|______|______|______|
; TEST_SSR           |             |                                         |
;                    |             |  current SSR being tested               |
;                    |______|______|______|______|______|______|______|______|
; AUTO_OFF_CTRH      |                                                       |
;                    |         countdown register until auto-power-off (MSB) |
;                    |______|______|______|______|______|______|______|______|
; AUTO_OFF_CTRL      |                                                       |
;                    |         countdown register until auto-power-off (LSB) |
;                    |______|______|______|______|______|______|______|______|
; I                  |                                                       |
;                    |      General-purpose local counter variable           |
;                    |______|______|______|______|______|______|______|______|
; J                  |                                                       |
;                    |      General-purpose local counter variable           |
;                    |______|______|______|______|______|______|______|______|
; K                  |                                                       |
;                    |      General-purpose local counter variable           |
;                    |______|______|______|______|______|______|______|______|
; KK                 |                                                       |
;                    |      General-purpose local counter variable           |
;                    |______|______|______|______|______|______|______|______|
; TR_I               |                                                       |
;                    |      T/R delay timer delay counter                    |
;                    |______|______|______|______|______|______|______|______|
;
;
;------------------------------------------------------------------------------
; (SSR_DATA_BANK)
;------------------------------------------------------------------------------
;
; *** THE FOLLOWING BLOCKS *MUST* BE THE SAME SIZE AS EACH OTHER ***
;
;                     ___7______6______5______4______3______2______1______0__
; SSR_00_VALUE       |                                                       |
;                    | Brightness value of SSR #00 (00=off, ... FF=fully on) |
;                    |______|______|______|______|______|______|______|______|
;                    |                                                       |
;                    | Brightness value of SSR #01 (00=off, ... FF=fully on) |
;                    |______|______|______|______|______|______|______|______|
;                                                .
;                                                .
;                     ___________________________.___________________________
;                    |                                                       |
;                    | Brightness value of SSR #23 (00=off, ... FF=fully on) |
;                    |______|______|______|______|______|______|______|______|
;                    |                                                       |
;                    | Brightness value of Green   (00=off, ... FF=fully on) |
;                    |______|______|______|______|______|______|______|______|
;                    |                                                       |
;                    | Brightness value of Yellow  (00=off, ... FF=fully on) |
;                    |______|______|______|______|______|______|______|______|
;                    |                                                       |
;                    | Brightness value of Red     (00=off, ... FF=fully on) |
;                    |______|______|______|______|______|______|______|______|
;                    | IF MASTER/STANDALONE:                                 |
;                    | Brightness value of Active  (00=off, ... FF=fully on) |
;                    |______|______|______|______|______|______|______|______|
; SSR_00_FLAGS       | FADE | FADE | FADE_|MAX_OF|      |      |      |      |
;                    | _UP  | _DOWN| CYCLE|F_TIME|      |      |      |      |
;                    |______|______|______|______|______|______|______|______|
;                                                .
;                                                .
;                     ___________________________.___________________________
; SSR_00_STEP        |                                                       |
;                    |          Brightness increment (0..255)                |
;                    |______|______|______|______|______|______|______|______|
;                                                .
;                                                .
;                     ___________________________.___________________________
; SSR_00_SPEED       |                                                       |
;                    |          Cycles between each step (0..255)            |
;                    |______|______|______|______|______|______|______|______|
;                                                .
;                                                .
;                     ___________________________.___________________________
; SSR_00_COUNTER     |                                                       |
;                    |          Cycles until next step (0..255)              |
;                    |______|______|______|______|______|______|______|______|
;                                                .
;                                                .
;                                                .                           
;
	GLOBAL	QSCC_START
	GLOBAL	QSCC_MAIN
	GLOBAL	QSCC_CMD6_START
	GLOBAL	QS_STOP_SCANNER

;------------------------------------------------------------------------------
; QUIZSHOW_DATA BANK
;------------------------------------------------------------------------------
;
;                     ___7______6______5______4______3______2______1______0__
; BTN_X0_TIME_T      |                                                       |
;                    |         Button press time (uS) <31:24>                |
;                    |______|______|______|______|______|______|______|______|
; BTN_X1_TIME_T      |                                                       |
;                    |         Button press time (uS) <31:24>                |
;                    |______|______|______|______|______|______|______|______|
;                                                :
;                     ___________________________:___________________________
; BTN_X0_TIME_U      |                                                       |
;                    |         Button press time (uS) <23:16>                |
;                    |______|______|______|______|______|______|______|______|
;                                                :
;                     ___________________________:___________________________
; BTN_X0_TIME_H      |                                                       |
;                    |         Button press time (uS) <15:8>                 |
;                    |______|______|______|______|______|______|______|______|
;                                                :
;                     ___________________________:___________________________
; BTN_X0_TIME_L      |                                                       |
;                    |         Button press time (uS) <7:0>                  |
;                    |______|______|______|______|______|______|______|______|
;                                                :
;                     ___________________________:___________________________
;
;      .
;      .	Ditto for L0, X1, L1, X2, L2, X3, L3, X4, L4		(QSRC)
;      .	Or... for L0, A, B, C, D				(QSCC)
;
QUIZSHOW_DATA	EQU	0xC00
_QUIZSHOW_DATA	UDATA	QUIZSHOW_DATA
BTN_X0_TIME_T	RES	N_BUTTONS	; button press times (bits 31-24)
BTN_X0_TIME_U	RES	N_BUTTONS	; button press times (bits 23-16)
BTN_X0_TIME_H	RES	N_BUTTONS	; button press times (bits 15-08)
BTN_X0_TIME_L	RES	N_BUTTONS	; button press times (bits 07-00)
BTN_X0_FLAGS	RES	N_BUTTONS	; button flags
BTN_X0_LOCKTMR	RES	N_BUTTONS	; number of 1/120 sec remaining in lock
QUIZSHOW_FLAGS	RES	1
_QUIZSHOW_CODE	CODE

BTN_FLG_LOCKED	EQU	2		; -----1--	Button locked out
BTN_FLG_MASKED	EQU	1		; ------1-	Button ignored
BTN_FLG_PRESSED	EQU	0		; -------1	Button pressed already

QS_FLAG_SCANNING EQU	0		; -------1	Scanner running
;
; Clear all button timers and states
;
CLEAR_BUTTONS MACRO FULL_RESET
	BANKSEL	QUIZSHOW_DATA
CB_IDX	SET	0
	WHILE	CB_IDX < N_BUTTONS
	 CLRF	BTN_X0_TIME_T+CB_IDX, BANKED
	 CLRF	BTN_X0_TIME_U+CB_IDX, BANKED
	 CLRF	BTN_X0_TIME_H+CB_IDX, BANKED
	 CLRF	BTN_X0_TIME_L+CB_IDX, BANKED
	 IF FULL_RESET
	  CLRF	BTN_X0_FLAGS+CB_IDX, BANKED
	  CLRF	BTN_X0_LOCKTMR+CB_IDX, BANKED
	 ELSE
	  BCF	BTN_X0_FLAGS+CB_IDX, BTN_FLG_PRESSED, BANKED
	 ENDIF
CB_IDX	 ++
	ENDW
	ENDM
		 
;
; Startup code (on top of what LUMOS_START does), right before the main loop
; is launched.
;
QSCC_START:
	CLRWDT
	CLRF	QUIZSHOW_FLAGS, BANKED
	CLEAR_BUTTONS 1
	CLRWDT
	SET_SSR_SLOW_FADE 0
	RETURN
;
; Main loop code (in addition to Lumos' main loop code)
;
	EXTERN	SSR_00_VALUE
	EXTERN	SSR_00_FLAGS
	EXTERN	SSR_00_STEP
	EXTERN	SSR_00_SPEED
	EXTERN	SSR_00_COUNTER

QSCC_MAIN:
	CLRWDT
	RETURN

;
; Start scanning for button presses
;
; Resets all button timers and debounce circuits, starts scanning
; This is stopped via the QS_QUERY command.
; This is a global command, only recognized when sent to address 15.
;
QSCC_CMD6_START:
	CLRWDT
	CLEAR_BUTTONS 0
	BSF	QUIZSHOW_FLAGS, QS_FLAG_SCANNING
	; XXX start timer
	; XXX light up non-masked buttons
	RETURN

QS_STOP_SCANNER:
	CLRWDT
	BCF	QUIZSHOW_FLAGS, QS_FLAG_SCANNING
	; XXX stop timer
	; XXX extinguish non-masked buttons
	RETURN

	END


