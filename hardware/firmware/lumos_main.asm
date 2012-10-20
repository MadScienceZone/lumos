; XXX XXX XXX ** KILL BROADCAST ADDR IDEA ** it's not going to work XXX XXX XXX
; XXX review logic flow for each chip type
; XXX check all BRA $+x values after assembly
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
; -*- -*- -* -*- -*- -*- -*- -*- -*- -*- -*- -*- -*- -*- -* -*- -*- -*- -*- -*-
;
; Main implementation module.
;
	PROCESSOR 	18F4685
	RADIX		DEC
#include <p18f4685.inc>
#include "lumos_init.inc"
#include "serial-io.inc"

; Works on Lumos 48-Channel controller boards 48CTL-3-1 with retrofit
; and 24SSR-DC-1.0.3 boards.
;
; N.B. THE BOARD SELECT BITS IN LUMOS_CONFIG.INC MUST BE SELECTED
; FOR THE TARGET CONFIGURATION!  EACH ROM IS DIFFERENT!
;
; Target Microcontroller is PIC18F4685, Q=40MHz (100nS instruction cycle)
; (Original was designed for PIC16F777 and PIC16F877A; you must upgrade
; the uC to a PIC18F4685 AND retrofit some parts on the old board as
; follows:
;    Replace X0 and X1 with 10 MHz crystals.
;    Interface off-board reset button to ground J5 and J6 pin 3 when pressed.
;    Interface off-board option button to ground J5 pin 5 when pressed.
;    Install a 10K pull-up resistor between J5 pin 5 and +5V.
;    (Optional) /PWRCTL output to P/S available on J5 pin 4.
;    Option button should only be attached to the master microcontroller.
;    Both need their own reset buttons.
;
; Serial control (RS-232 or RS-485) at 19.2kbps by default.
; Configurable from 300 to 250000.
;
;=============================================================================
; DIAGNOSTICS
;-----------------------------------------------------------------------------
;
; The front panel LEDs provide the following indications of status.  
;
; A  G  Y  R
; C  R  E  E
; T  N  L  D PHASE MEANING
; ---------- ----- -------
; .  .  .  . BOOT  Never started into boot sequence
; .  .  .  * BOOT  Halted during EEPROM setup
; .  .  *  * BOOT  Halted during EEPROM write operation
; .  .  *  . BOOT  Halted during EEPROM read / system init
; .  *  *  . BOOT  Halted during system initialization
; .  *  .  . BOOT  Initialized but main loop or timing system non-functional
;** ** ** ** RUN   Factory defaults restored (then reboots)
; . (*) .  . RUN   Normal operations
; ! (*) X  X RUN   Received command for this unit
; X  X  !  X RUN   Master/Slave communications
; X  X  X  * RUN   Command error
; X  X  * ** RUN   Communications error (framing error)
; X  X ** ** RUN   Communications error (overrun error)
; X  X (*)** RUN   Communications error (buffer full error)
; . () () () SLEEP Sleep Mode
; .  .  .  * HALT  System Halted normally
; ?  ?  ? ** HALT  Fatal error (exact error displayed on other LEDs)
;
; .=off  *=steady (*)=slowly fading on/off X=don't care
; ()=slow flash **=rapid flash !=blink/fade once
;
;=============================================================================
; IMPLEMENTATION NOTES
;-----------------------------------------------------------------------------
;
; The SSR controller firmware consists of a number of somewhat independent 
; subsystems:
; 
; START
;	Initializes the microcontroller, starts up the required peripherals,
;	indicates the device ID on the front panel, and enters the main loop
;
; SIO
;	Handles all serial I/O operations in the background (interrupt-driven)
;	so the rest of the code only needs to be concerned with higher-level
;	reads and writes.  Buffers hold 256 characters each of input and output.
;
; ISR
;	The interrupt service routine manages a set of counters and timers:
;       1. At each AC line zero-crossing point, we reset a two-stage waveform
;	   slicing timing chain which governs the ability for the SSRs to dim
;	   incandescent lamps plugged into them; 
;	2. For DC boards, we run a 120 Hz timer which provides approximately
;	   the same time base since those boards have no zero-crossing detection;
;	3. Each front panel LED has a counter for how long their current 
;          status is to be held, to allow a human to have enough time to 
;          see the LED before it would be extinguished. (This is less explicit
;          now than the previous major firmware version.  The LEDs are now simply
;	   treated just like extra SSR lines, so they use the same code to manage
;          them.)
;
; MAIN_LOOP
;	Manages the display of the front panel LEDs
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
;                     ___7______6______5______4______3______2______1______0__
; Broadcast Command: |      |                    |                           |
;                    |   1  |    Command code    |            15             |
;                    |______|______|______|______|______|______|______|______|
;
; All units recognize address 1111 (15) as a "broadcast" address (all units
; respond to CERTAIN commands addressed to this target).  It's possible to address
; a unit as #15, but you won't be able to send those certain commands to it exclusively.
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
; from 0-127
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
; Commands recognized:
;
;   COMMAND  CODE  BITS
; # BLACKOUT 0     1000aaaa
;   ON_OFF   1     1001aaaa 0scccccc		Turn channel <c> on (<s>=1) or off (<s>=0)
; ^ SET_LVL  2     1010aaaa 0hcccccc 0vvvvvvv    Set dimmer level <v>:<h> on channel <c>
; ^ BULK_UPD 3     1011aaaa 0mcccccc ...		Bulk-upload multiple channel levels
;   RAMP_LVL 4     1100aaaa 0dcccccc ...         Ramp channel <c> smoothly up (<d>=1) or down
;            5     1101aaaa                      Reserved for future use
;            6     1110aaaa                      Reserved for future use
;   EXTENDED 7     1111aaaa                      Extended command, decoded further in next byte
;@# SLEEP    7+0   1111aaaa 00000000 01011010 01011010  Put unit to sleep
;@# WAKE     7+1   1111aaaa 00000001 01011010 01011010  Take unit out of sleep mode
; # SHUTDOWN 7+2   1111aaaa 00000010 01011000 01011001  Take unit completely offline
; < QUERY    7+3   1111aaaa 00000011 00100100 01010100  Report device status
; ! DEF_SEQ  7+4   1111aaaa 00000100 0iiiiiii ...       Define sequence <i>
;   EXEC_SEQ 7+5   1111aaaa 00000101 0iiiiiii           Execute sequence <i> (0=stop)
;   DEF_SENS 7+6   1111aaaa 00000110 ...                Define sensor trigger
;   MSK_SENS 7+7   1111aaaa 00000111 0000ABCD           Mask inputs (1=enable, 0=disable)
; ! CLR_SEQ  7+8   1111aaaa 00001000 01000011 01000001  Erase all stored sequences
;            7+9   1111aaaa 00001001                    Reserved for future use
;             :        :        :                           :     :     :    : 
;            7+30  1111aaaa 00011110                    Reserved for future use                 
;   OUT_RPLY 7+31  1111aaaa 00011111 ...                Reply to QUERY command_________________ 
;   IC_TXDAT 7+32  11110000 00100000 0nnnnnnn (...)*<n>+1 00011011 data -> serial port INTERNAL
;   IC_LED   7+33  11110000 00100001 00GGGYYY 00000RRR             LED Control         ////////
;   IC_HALT  7+34  11110000 00100010                               CPU Halt            ////////
;            7+35  11110000 00100011                    Reserved for new commands      ////////
;             :        :        :                           :     :   :      :         ////////
;            7+63  11110000 00111111                    Reserved for new commands______////////
;*! CF_PHASE 7+64  1111aaaa 010000pp 0ppppppp 01010000 01001111   Phase offset=<p>       CONFIG
;*! CF_ADDR  7+96  1111aaaa 0110AAAA 01001001 01000001 01000100   Change address to <A>  //////
;*  CF_NOPRV 7+112 1111aaaa 01110000                              Leave privileged mode  //////
;*  CF_CONF  7+113 1111aaaa 01110001 ...                          Configure device       //////
;*! CF_BAUD  7+114 1111aaaa 01110010 0bbbbbbb 00100110            Set baud rate to <b>   //////
;*! CF_RESET 7+115 1111aaaa 01110011 00100100 01110010            Reset factory defaults //////
;*           7+116 1111aaaa 01110100                     Reserved for future config cmd  //////
;*                     :        :                            :     :     :      :    :   //////
;*           7+127 1111aaaa 01111111                     Reserved for future config cmd__//////
;
; Payloads for many-byte commands
;
; BULK_UPD:  0mcccccc 0nnnnnnn (0vvvvvvv)*<n> 01010110 (0hhhhhhh)*[(<n>+6)/7] 01010101
;             |                               \_____________________________/
;             |_______________________________________________| if <m>=1
;
;	Updates <n> channels starting at <c>, giving <v> values for each as per SET_LVL.
;	If <m>=1, then the LSBs are given, packed into 7-bit values with bit 6 corresponding
;	to the first output channel, bit 5 is the next, and so on.
;
; RAMP_LVL:  0dcccccc 0sssssss 0ttttttt   Channel <c> up/down in <s>+1 steps every <t>+1/120 sec
;
; DEF_SEQ:   0iiiiiii 0nnnnnnn (...)*<n> 01000100 01110011  Define sequence <i> of length <n>
;                                                            0 is boot sequence, 1-63 is EEPROM
;                                                            64-127 is RAM.
;
; DEF_SENS:  0owE00SS 0IIIIIII 0iiiiiii 0PPPPPPP 00111100
;	Defines the trigger for sensor <S> (00=A, 01=B, 10=C, 11=D), where the event triggers
;	when sensor input goes low (<E>=0) or high (<E>=1).  When triggered, sequence <I>
;	initially, then continues playing sequence <i> (once if <O>=1, else while the sensor
;	remains active if <W>=1, else forever until forced to stop), then sequence <P> is
;	played at the end of the event.
;
; IC_LED:    00GGGYYY 00000RRR
;	each 3 bits decode as:
;		000 steady off	001 steady on
;		010 slow fade	011 fast fade
;		100 slow flash	101 fast flash
;		11x no change
;
; CF_CONF:   0ABCDdcc 0ccccccc 0m111010 00111101
;	Configure sensor lines ABCD as 1=sensor inputs or 0=LED outputs,
;	DMX mode if <d>=1, with Lumos channel 0 at DMX channel <c>+1,
; 	device resolution is high (256) if <m>=1, else low (128).
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
; Response packet from QUERY command (30 bytes):
;    1111aaaa 00011111 0ABCDdcc 0ccccccc 0ABCDqsf 0ABCDmpp 0ppppppp 
;        \__/           \__/|\_________/  \__/|||  \__/|\_________/  
;          |              | |   |           | |||   |  |      `--phase
;          `--reporting   | |   `--DMX      | |||   |  `--resolution
;              unit addr  | |      channel  | |||   `--active
;                         | |               | ||`--mem full?
;                         | `--DMX mode?    | |`--sleeping?
;                         `--configured     | `--config mode?
;                                           `--masks
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
;    00110011
;
;
; Legend:
;   @ Unit may automatically take this action
;   # Broadcast-capable command (all units respond to address 15)
;   * Privileged configuration-mode command
;   ! Permanent effect (written to EEPROM)
;   ^ Affected by unit resolution mode
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
;-----------------------------------------------------------------------------
; State Machine Details
;
; Normally sits at state 0 (Idle) where it pretty much spins free waiting
; for the start of a command to come along.
;       ______________________________________________________,
;       |                                                     |
;  _____V____      __________                                 |
; | 0 |      |    | 1 |      |                                |
; |___|      |--->|___|      |                                |
; |   IDLE   |<---| ON_OFF   |                                | 
; |__________|  ch|__________|                                |
;       |          __________      ___                        |
;       |         | 2 |      |ch  |   |v                      |
;       |-------->|___|      |--->| 3 |---------------------->|
;       |         | SET_LVL  |    |___|                       |
;       |         |__________|                                |
;       |          __________      ___      ___               |
;       |         | 5 |      |ch  |   |s   |   |t             |
;       |-------->|___|      |--->| 7 |--->| 8 |------------->|
;       |         | RAMP_LVL |    |___|    |___|              |
;       |         |__________|                                |
;       |          __________                  __________     |
;       |         | 4 |      |ch              | 6 | Wait |    |
;       |-------->|___|      |--------------->|___|  for |--->|
;       |         | BULK_UPD |                | Sentinel |    |
;  _____V____     |__________|                |__________|    |
; | 9 |      |                                      ^         |
; |___|      |______________________________________|         |
; | Extended |                                                |
; |__________|                                                |
;       |          __________      ___                        |
;       |         |   |      |GY  |   |R                      |
;       |-------->|___|      |--->|   |---------------------->|
;       |         | IC_LED   |    |___|                       |
;       |         |__________|                                |
;       |          __________                                 |
;       |         |   |      |i                               |
;       |-------->|___|      |------------------------------->|
;       |         | EXEC_SEQ |                                |
;       |         |__________|                                |
;       |          __________                                 |
;       |         |   |      |m                               |
;       `-------->|___|      |--------------------------------'
;                 | MSK_SENS |    
;                 |__________|              
;
;-----------------------------------------------------------------------------
; System Timing Notes
;
; The system has some fairly specific real-time timing requirements in order
; to function properly.  The main external event we're synchronized to is the
; point where the AC waveform crosses the 0V line (the "zero crossing" point).
;
; An optoisolator on the controller board is connected to the AC input of the
; transformer and sends a positive-logic pulse to the INT pin of the micro-
; controller every time the AC line crosses 0V.  (Actually, the leading edge
; will slightly lead the zero crossing point and the trailing edge will 
; slightly lag behind it.)  So we enter our ISR once every 1/120 sec 
; (assuming US-standard 60Hz power).  For reference, this is 0.00833333 sec 
; or enough time for 41,666.666 instructions to be executed between each 
; interrupt.
;
; Slices  Time/slice  Instructions/slice
;   1     0.00833333  83,333.333
;  32     0.00026042   2,604.167
;  64     0.00013021   1,302.083
; 128     0.00006510     651.042
; 132     0.00006313     631.313	128 levels + 2 on each end
; 260     0.00003205     320.513	256 levels + 2 on each end
;
; (Revised; earlier versions of this firmware used 64 levels on the dimmers
; --which are probably too many--and this didn't allow enough time for the 
; main loop to run, so we backed it off to 32 here.  We will only run into
; trouble now if all--or most--channels are set to the same level, since 
; that one slice may run slightly over its allotted time, but the next slice
; will be shorter as a result and we'll catch back up within a tiny fraction
; of a cycle.)
;
; We divide the half-wave into "slices".  We need a minimum of 32 slices
; to get 32 levels of dimmer control, but we should add at least one on either
; end in case our timing's slightly off between the ZC points and the free-
; running timer.  For good measure, let's throw in a couple more to allow for
; pin settling times, minimum turn-on times for the triacs and just to be
; paranoid.  So let's say 38 slices per half-wave.  This is good, because it
; means that each dimmer level is 1/38th brightness, with the lowest setting 
; (other than off) being a minimum of 7/38ths, which means we don't waste
; several dimmer levels below the threshold for an incandescent filament to
; even be visibly on at all.
;
; At 260 slices per ZC, each slice is 0.00003205128205128205 seconds.
; We set TMR2's period register to 159, with a 1:2 postscaler and no prescaler.
; That gives us a timer interrupt every 320 clock ticks, or every .000032 seconds.
; That's 320 instruction cycles worth of work we can pack into these cycles.
; Most of the work per cycle takes about 1/3 that much, so this should be ok.
;
SLICE_TMR_PERIOD	EQU	0x9F
;
; For standalone DC boards, we don't have a zero-crossing input so we set up
; our own 120 Hz timing signal by running TMR0 with a 1:2 prescaler for 
; 41,666 clock ticks (i.e., running the timer from $5D3D-$FFFF).
;
			IF LUMOS_SLICE_TIMER == LUMOS_INTERNAL
CYCLE_TMR_PERIOD	 EQU	0x5D3D
			ENDIF
;
; In the previous (prototype) version of this controller, we took the ZC
; signal from the *secondary* side of the transformer, which meant that it
; was possible for that to be out of phase with the actual AC ZC event, so
; the "phase delay" feature of the event handling code was written to 
; compensate for this.  Now that we sample the AC line directly, we set 
; this delay to a constant value and that should be good.  We left the 
; capability in here, though, to account for any need for adjustment which
; may turn up due to component tolerances, propagation delays, or similar
; things.  We correct for any phase offset by adding a software delay
; from 0-511 (although really only 0-260 make much sense) slices between the ZC
; interrupt and the start of the dimmer cycle of 260 slices.  (The other 4 
; slices are idle (not active) slices.) 
;
; The value for PHASE_OFFSET should be chosen to start the cycle one or two
; slices into the actual half-wave.  So if there is no phase difference at all
; between sides of the transformer, PHASE_OFFSET should be 2.
;
; Here's the timeline:
;
;                    REAL                               REAL
;                     ZC                                 ZC
;    |................|..|...............|....|....|.....|..|..............
;    |phase delay------->|               |phase delay------>|
;    |                   |working slices----->|    |        |working slices-->
;    |                                   |    |idle|
;   INT                                 INT
;   (ZC)                                (ZC)
;
; Of course, in the current design, there is no phase shift across
; the transformer, so we'd have the trivial case of PHASE_OFFSET=2 (2 just to
; allow a little fudge room with the free-running slice timer which is not
; *quite* an even factor of the half-wave time):
;
;    REAL                         REAL
;     ZC                           ZC
;    .|..|....................|....|..|.................|
;     |->|                    |    |->|                 |
;     |  |working slices----->|    |  |working slices-->|
;     |  |                    |idle|  |                 |
;    INT                          INT
;
; Since the free-running slice timer isn't exactly in sync with the ZC timing,
; we'll start our working slices some variable fraction of 1/38th of a half-cycle
; each time.  This will cause a "wobble" in brightness level of not more than 
; 1/260th brightness level (something less than one brightness increment), which
; ought to be difficult or impossible to notice by looking at an incandescent
; light load.  This is one reason why PHASE_OFFSET should be set to allow 1-2
; idle slices before we start turning on SSRs.
;
; On ZC interrupt, we set CUR_PRE to PHASE_OFFSET and set <PRECYC>.
; On TMR2 interrupt, if SSR_STATE<PRECYC>, decrement CUR_PRE.
;   if zero, clear SSR_STATE<PRECYC>, set CUR_SLICE to 32, set <INCYC>,<DIM_START>.
;   if SSR_STATE<INCYC>, decrement CUR_SLICE; if zero, set DIM_END, clr INCYC; else set SLICE_UPD
; 
; In main polling loop:
;   if DIM_START: turn on "on" SSRs, clear DIM_START
;   if SLICE_UPD: turn on SSR == CUR_SLICE for SSRs with SSRDIM set; clear SLICE_UPD
;   if DIM_END:   turn off all except SSR_ON, clear DIM_END
;
; PRECYC INCYC SLICE_UPD  CUR_PRE CUR_SLICE
;    0     x       x         x       x
;    1     x       x         4       x       <--zc
;    1     x       x         3       x
;    1     x       x         2       x
;    1     x       x         1       x
;    0     1     1-->0       0      255      SSR@255/on turned on
;    0     1     1-->0       0      254      SSR@254    turned on
; ...
;    0     1     1-->0       0       2       SSR@2     turned on
;    0     1     1-->0       0       1       SSR@1     turned on
;    0     0     1-->0       0       0       all non-on turned off
;    0     0       0         0       0       idle...
; ...
;    1     0       0         4       0       <--zc
; 
;
;=============================================================================
; HARDWARE DESCRIPTION
;-----------------------------------------------------------------------------
;
;  PIC18F4685 Microcontroller I/O pin assignments:
;
; 24-CH   48-CH          ________   _________         48-CH   24-CH
; BOARD:  BOARD:        |o       \_/         |        BOARD:  BOARD:
; /RESET  /RESET -->  1 | /MCLR RE3  PGD RB7 | 40 --> /PWRCTL /PWRCTL
; /SSR23  /SSR16 <--  2 | RA0        PGC RB6 | 39 <-- /OPTION /OPTION
; /SSR22  /SSR14 <--  3 | RA1        PGM RB5 | 38 --> /SSR15  /SSR00
; /SSR21  /SSR12 <--  4 | RA2            RB4 | 37 --> /SSR13  /SSR01
; /SSR20  /SSR10 <--  5 | RA3            RB3 | 36 --> /SSR11  /SSR02
; /SSR19  /SSR08 <--  6 | RA4       INT2 RB2 | 35 --> /SSR09  /SSR03
; ACT    ACT*LED <--  7 | RA5       INT1 RB1 | 34 --> /SSR07  /SSR04 _
; GRN    GRN LED <--  8 | RE0       INT0 RB0 | 33 <-- ZC INT  -->  T/R
; YEL    YEL LED <--  9 | RE1            VDD | 32 --- +5V       
; RED    RED LED <-- 10 | RE2            VSS | 31 --- GND      
;            +5V --- 11 | VDD            RD7 | 30 --> /SSR17  /SSR05
;            GND --- 12 | VSS            RD6 | 29 --> /SSR06  /SSR06
;           xtal --- 13 | OSC            RD5 | 28 --> /SSR05  /SSR07
;             +----- 14 | OSC            RD4 | 27 --> /SSR18  /SSR08
; /SSR18  /SSR04 <-- 15 | RC0         RX RC7 | 26 <-- Serial RxD
; /SSR17  /SSR19 <-- 16 | RC1         TX RC6 | 25 --> Serial TxD
; /SSR16  /SSR03 <-- 17 | RC2            RC5 | 24 --> /SSR02  /SSR09
; /SSR15  /SSR01 <-- 18 | RC3            RC4 | 23 --> /SSR00  /SSR10
; /SSR14  /SSR23 <-- 19 | RD0            RD3 | 22 --> /SSR22  /SSR11
; /SSR13  /SSR21 <-- 20 | RD1            RD2 | 21 --> /SSR20  /SSR12
;                       |____________________|
;                  _
; *pin 7 goes to T/R on the slave controller instead of the LED.
;
;
; The outputs from the controller board are on a 26-bin ribbon cable
; header with this pinout:
;
;                               _________
;                       SSR23  |  1 |  2 |  SSR00
;                       SSR22  |  3 |  4 |  SSR01
;                       SSR21  |  5 |  6 |  SSR02
;                       SSR20  |  7 |  8 |  SSR03
;                       SSR19  |  9 | 10 |  SSR04
;                       SSR18  | 11 | 12 |  SSR05
;                       SSR17  | 13 | 14 |  SSR06
;                         GND  | 15 | 16 |  +5V
;                       SSR16  | 17 | 18 |  SSR07
;                       SSR15  | 18 | 20 |  SSR08
;                       SSR14  | 21 | 22 |  SSR09
;                       SSR13  | 23 | 24 |  SSR10
;                       SSR12  |_25_|_26_|  SSR11
;
;
; Communications are via RS-485 serial network using an 8p8c modular
; connector with this pinout:
;
;  ________
; |12345678|	1- Return Data          5- Data A (+)
; |        |	2- Return Data          6- Cable Check OUT
; |___  ___|	3- Cable Check IN   	7- Data GND 
;    |__|	4- Data B (-)		8- Return Data GND
;
; CC is a cable check indicator.  A signal is sent out on pin 1, expected to be connected
; to pin 2 at the terminator, so end-to-end continuity of the cable connections can
; be verified.  Note that the controllers themselves do nothing with the CC signal other
; than pass those pins straight through; it is available however for something at the 
; host side to verify cable integrity.
;
; Data A/B is the twisted pair for the RS-485 data between the host PC and controllers.
;
; Return Data A/B is only implemented if a full duplex RS-485 network is implemented
; (an option for some boards but not the default case).  This is dedicated for controllers
; sending data back to the host PC.  If using half-duplex, the same data pair is used
; for both sending and receiving, and the host PC needs to switch to receive mode
; when a controller is asked to report back.
;
;
; Termination at the end of the loop should be provided with a plug
; wired as:
; 
;     3 ------------ 6
; 
;     1 ---/\/\/---- 2 <--(if full duplex)
;         120 ohms
; 
;     4 ---/\/\/---- 5
;         120 ohms
; 
;
; ========================================================================
; PROGRAM MEMORY MAP
; ______________________________________________________________________________
;
;         _________________ ___
; $00000 | RESET Vector    | V_RST
; $00007 |_________________|___
; $00008 | High Int Vector | V_INT_H
; $00017 |_________________|___
; $00018 | High Int Vector | V_INT_L
; $0001F |_________________|
; $00020 |/////////////////|
; $000FF |/////////////////|___
; $00100 | Boot code       | _BOOT
;        |.................|___
;        | Interrupt hand- | _INT
;        |  lers           |      
;        |/////////////////|
; $007FF |/////////////////|___
; $00800 | Mainline code   | _MAIN
;        |.................|___
;    ??? | Device init     | LUMOS_CODE_INIT
;        |_________________|___
;    ??? | Serial I/O      | _SIO_CODE
;        | Module          |
;        |_________________|___
;        |/////////////////|
;        |/////////////////|
;        |/////////////////|
;        |/////////////////|
;        |/////////////////|___
; $14000 | EEPROM defaults | _MAIN_EEPROM_TBL
;
;; $14000 |CMD state machine| _MAIN_LOOKUPS
;;        |transition tables|
;;        |.................|___
;; $14100 |Command dispatch | _MAIN_DISPATCH
;;        |table (lower 1/2)|   
;;        |.................|___
;; $14200 |(upper 1/2)      | _MAIN_DIS2
;;        |.................|___
;; $14300 |Glyph bitmaps    | _RBRD_GLYPHS
;;        |                 |   
;;        |                 |   
;;        |                 |   
;; $146FF |                 |   
;;        |.................|___
;;    ??? |String constants | _MAIN_STRINGS
;;        |_________________|
;;        |/////////////////|
;;        |/////////////////|
;;        |/////////////////|___
; $15000 |Serial I/O Mod   | _SIO_LOOKUP_TABLES
;        |lookup tables    |
; $17FFF |_________________|___
;        |/////////////////|
;        |/////////////////|
;$1FFFFF |/////////////////|___
;
_MAIN_EEPROM_TBL	EQU	0x14000
;
;
; ========================================================================
; DATA MEMORY MAP
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
; $580 |                 |
;      |_________________|___ ___ ___ ___ ___ ___ ___ ___
; $600 | Stored sequences| _SEQ_DATA         BANK 6
;      | (1792 bytes)    |
;              .
;              .                 
;              .                
;      |                 |
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
; $005 |______________|     $015 |       |      |
; $006 |______________|       .          .
; $007 |______________|       .          .
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
_EEPROM	CODE_PACK	0xF00000
	DE	0xFF		; 000: 0xFF constant
	DE	SIO_19200	; 001: baud rate default
	DE	0x00		; 002: default device ID
	DE	0x00, 0x02	; 003: default phase offset
	DE	0x00, 0x00, 0x00; 005: reserved
	DE	0x00, 0x00, 0x00; 008: reserved
	DE	0x00, 0x00, 0x00; 00B: reserved
	DE	0x00            ; 00E: reserved
	DE	0x42		; 00F: sentinel

_EEPROM_DEFS_TBL CODE_PACK _MAIN_EEPROM_TBL
DEFAULT_TBL:
	DB	0xFF			; $000: constant $FF
	DB	SIO_19200		; $001: 19200 baud
	DB	0x00			; $002: device ID=0
	DB	0x00, 0x02		; $003: phase offset=2
	DB	0x00, 0x00, 0x00, 0x00	; $005-$008
	DB	0x00, 0x00, 0x00, 0x00	; $009-$00C
	DB 	0x00, 0x00		; $00D-$00E
	DB	0x42			; $00F: constant $42

EEPROM_SETTINGS_LEN	EQU	.16
EEPROM_USER_START	EQU	0x010	
EEPROM_USER_END		EQU	0x3FF
;
; ========================================================================
; DEVICES USED
;
; TMR0    120 Hz interrupt source (for boards without zero-crossing detector)
; TMR1
; TMR2    Dimmer slice timer (1/260 of a 120 Hz half-cycle)
; TMR3
; UART	  SIO module
;=============================================================================
;
;
;-----------------------------------------------------------------------------
; I/O PORT ASSIGNMENTS
;-----------------------------------------------------------------------------
;
;          7   6   5   4   3   2   1   0
; PORT RA --- --- ACT /08 /10 /12 /14 /16    48-Board AC/DC master
; PORT RA --- --- T/R /08 /10 /12 /14 /16    48-Board AC/DC slave
; PORT RA --- --- ACT /19 /20 /21 /22 /23    24-Board DC    standalone
;          <OSC>   O   O   O   O   O   O
;
;          7   6   5   4   3   2   1   0
; PORT RB /PS /OP /15 /13 /11 /09 /07 ---    48-Board AC/DC master
;          O   I   O   O   O   O   O  INT
; PORT RB /PS --- /15 /13 /11 /09 /07 ---    48-Board AC/DC slave
;          O   O   O   O   O   O   O  INT
; PORT RB /PS /OP /00 /01 /02 /03 /04 T/R    24-Board DC    standalone
;          O   I   O   O   O   O   O   O 
;
;          7   6   5   4   3   2   1   0
; PORT RC --- --- /02 /00 /01 /03 /19 /04    48-Board AC/DC master/slave
; PORT RC --- --- /09 /10 /15 /16 /17 /18    24-Board DC    standalone
;          <I/O>   O   O   O   O   O   O
;
;          7   6   5   4   3   2   1   0
; PORT RD /17 /06 /05 /18 /22 /20 /21 /23    48-Board AC/DC master/slave
; PORT RD /05 /06 /07 /08 /11 /12 /13 /14    24-Board DC    standalone
;          O   O   O   O   O   O   O   O
;
;          7   6   5   4   3   2   1   0
; PORT RE --- --- --- --- --- RED YEL GRN    All boards
;                              O   O   O
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
; SSR_STATE          |      |      |SLICE |PRIV_ |                           |
;                    |INCYC |PRECYC| _UPD | MODE |                           |
;                    |______|______|______|______|______|______|______|______|
; YY_STATE           |                                                       |
;                    |                      Parser State                     |
;                    |______|______|______|______|______|______|______|______|
; YY_COMMAND         |                                                       |
;                    |                      Command Code                     |
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
; SSR_00_FLAGS       | FADE | FADE | FADE_|      |      |      |      |      |
;                    | _UP  | _DOWN| CYCLE|      |      |      |      |      |
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
; SSR_STATE holds the execution state of the controller, including our
; main timing chain flags.
;
INCYC		EQU	7	; 1-------  We are in a dimmer cycle now
PRECYC		EQU	6	; -1------  We are in the pre-cycle countdown
SLICE_UPD	EQU	5	; --1-----  Slice update needs to be done
PRIV_MODE	EQU	4	; ---1----  We are in privileged (config) mode
;
; SSR_FLAGS words for each output show state information about those
; channels.
;
FADE_UP		EQU	7	; 1-------  This channel is fading up
FADE_DOWN	EQU	6	; -1------  This channel is fading down
FADE_CYCLE	EQU	5	; --1-----  This channel is fading up<-->down
BIT_FADE_UP	EQU	0x80
BIT_FADE_DOWN	EQU	0x40
BIT_FADE_CYCLE	EQU	0x20
;
; TARGET_SSR has these flags:
;                     _______________________________________________________
; TARGET_SSR         |NOT_MY|INVALI|                                         |
;                    | _SSR |D_SSR |    SSR number for current command       |
;                    |______|______|______|______|______|______|______|______|
;
NOT_MY_SSR	EQU	7
INVALID_SSR	EQU	6
TARGET_SSR_MSK	EQU	0x3F


		IF LUMOS_CHIP_TYPE==LUMOS_CHIP_MASTER || LUMOS_CHIP_TYPE==LUMOS_CHIP_STANDALONE
HAS_ACTIVE	 EQU	1
PLAT_ACTIVE	 EQU	LATA
BIT_ACTIVE	 EQU	5

PORT_OPTION	 EQU	PORTB
BIT_OPTION	 EQU	6

 		 IF LUMOS_CHIP_TYPE==LUMOS_CHIP_STANDALONE
HAS_T_R		  EQU	1
PLAT_T_R	  EQU	LATB
BIT_T_R		  EQU	0
		 ELSE
HAS_T_R		  EQU	0
 		 ENDIF

		ELSE
 		 IF LUMOS_CHIP_TYPE==LUMOS_CHIP_SLAVE
HAS_T_R		  EQU	1
HAS_ACTIVE	  EQU	0
PLAT_T_R	  EQU	LATA
BIT_ACT		  EQU	5
 		 ELSE
  		  ERROR "LUMOS_CHIP_TYPE invalid"
   		 ENDIF
		ENDIF

PLAT_PWR_ON	EQU	LATB
BIT_PWR_ON	EQU	7

PLAT_RED	EQU	LATE
PLAT_YELLOW	EQU	LATE
PLAT_GREEN	EQU	LATE
BIT_RED		EQU	2
BIT_YELLOW	EQU	1
BIT_GREEN	EQU	0
 
		IF LUMOS_CHIP_TYPE==LUMOS_CHIP_STANDALONE
PLAT_0		 EQU	LATB
PLAT_1		 EQU	LATB
PLAT_2		 EQU	LATB
PLAT_3		 EQU	LATB
PLAT_4		 EQU	LATB
PLAT_5		 EQU	LATD
PLAT_6		 EQU	LATD
PLAT_7		 EQU	LATD
PLAT_8		 EQU	LATD
PLAT_9		 EQU	LATC
PLAT_10		 EQU	LATC
PLAT_11		 EQU	LATD
PLAT_12		 EQU	LATD
PLAT_13		 EQU	LATD
PLAT_14		 EQU	LATD
PLAT_15		 EQU	LATC
PLAT_16		 EQU	LATC
PLAT_17		 EQU	LATC
PLAT_18		 EQU	LATC
PLAT_19		 EQU	LATA
PLAT_20		 EQU	LATA
PLAT_21		 EQU	LATA
PLAT_22		 EQU	LATA
PLAT_23		 EQU	LATA

BIT_0		 EQU	5
BIT_1		 EQU	4
BIT_2		 EQU	3
BIT_3		 EQU	2
BIT_4		 EQU	1
BIT_5		 EQU	7
BIT_6		 EQU	6
BIT_7		 EQU	5
BIT_8		 EQU	4
BIT_9		 EQU	5
BIT_10		 EQU	4
BIT_11		 EQU	3
BIT_12		 EQU	2
BIT_13		 EQU	1
BIT_14		 EQU	0
BIT_15		 EQU	3
BIT_16		 EQU	2
BIT_17		 EQU	1
BIT_18		 EQU	0
BIT_19		 EQU	4
BIT_20		 EQU	3
BIT_21		 EQU	2
BIT_22		 EQU	1
BIT_23		 EQU	0
		ELSE
 		 IF LUMOS_CHIP_TYPE==LUMOS_CHIP_MASTER || LUMOS_CHIP_TYPE==LUMOS_CHIP_SLAVE
PLAT_0		  EQU	LATC
PLAT_1		  EQU	LATC
PLAT_2		  EQU	LATC
PLAT_3		  EQU	LATC
PLAT_4		  EQU	LATC
PLAT_5		  EQU	LATD
PLAT_6		  EQU	LATD
PLAT_7		  EQU	LATB
PLAT_8		  EQU	LATA
PLAT_9		  EQU	LATB
PLAT_10		  EQU	LATA
PLAT_11		  EQU	LATB
PLAT_12		  EQU	LATA
PLAT_13		  EQU	LATB
PLAT_14		  EQU	LATA
PLAT_15		  EQU	LATB
PLAT_16		  EQU	LATA
PLAT_17		  EQU	LATD
PLAT_18		  EQU	LATD
PLAT_19		  EQU	LATC
PLAT_20		  EQU	LATD
PLAT_21		  EQU	LATD
PLAT_22		  EQU	LATD
PLAT_23		  EQU	LATD

BIT_0		  EQU	4
BIT_1		  EQU	3
BIT_2		  EQU	5
BIT_3		  EQU	2
BIT_4		  EQU	0
BIT_5		  EQU	5
BIT_6		  EQU	6
BIT_7		  EQU	1
BIT_8		  EQU	4
BIT_9		  EQU	2
BIT_10		  EQU	3
BIT_11		  EQU	3
BIT_12		  EQU	2
BIT_13		  EQU	4
BIT_14		  EQU	1
BIT_15		  EQU	5
BIT_16		  EQU	0
BIT_17		  EQU	7
BIT_18		  EQU	4
BIT_19		  EQU	1
BIT_20		  EQU	2
BIT_21		  EQU	1
BIT_22		  EQU	3
BIT_23		  EQU	0
		 ELSE
  		  ERROR "LUMOS_CHIP_TYPE invalid"
 		 ENDIF
		ENDIF
;
; THESE SSR LINES ARE NEGATIVE-LOGIC CONTROLLED!
; (0=ON, 1=OFF)
;

; In this version, we have an array of outputs mapped with 0-255 values
; and another block of flags, etc. in SSR_DATA_BANK.
; We include the panel LEDs here, too, so we can handle them like the 
; others as far as timed patterns and display refreshes and the like.
;
; Offsets for panel lights
;
SSR_LIGHTS	EQU	24	; first light ID (as opposed to SSR)
SSR_GREEN	EQU	24	; NOTE These are positive-logic, not negative like SSRs
SSR_YELLOW	EQU	25
SSR_RED		EQU	26
;
; Aliases for macro expansion (continues SSR numbering into these too)
;
PLAT_#v(SSR_RED) 	EQU	PLAT_RED
PLAT_#v(SSR_YELLOW) 	EQU	PLAT_YELLOW
PLAT_#v(SSR_GREEN) 	EQU	PLAT_GREEN
BIT_#v(SSR_RED)		EQU	BIT_RED
BIT_#v(SSR_YELLOW) 	EQU	BIT_YELLOW
BIT_#v(SSR_GREEN) 	EQU	BIT_GREEN
;
;
		IF HAS_ACTIVE
SSR_ACTIVE	 EQU	27
PLAT_#v(SSR_ACTIVE) EQU	PLAT_ACTIVE
BIT_#v(SSR_ACTIVE) EQU	BIT_ACTIVE
SSR_MAX		 EQU	27
		ELSE
SSR_MAX		 EQU	26
		ENDIF

WAIT_FOR_SENTINEL MACRO MAX_LEN, SENTINEL_VALUE, NEXT_STATE
	 MOVLW	MAX_LEN
	 MOVWF	YY_LOOKAHEAD_MAX, ACCESS
	 MOVLW	SENTINEL_VALUE
	 MOVWF	YY_LOOK_FOR, ACCESS
	 MOVLW	6			; -> state 6 (wait for end of packet)
	 MOVWF	YY_STATE, ACCESS
	 CLRF	YY_BUF_IDX, ACCESS	; empty readahead buffer
	 MOVLW	NEXT_STATE
	 MOVWF	YY_NEXT_STATE, ACCESS
	ENDM

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

SET_SSR_RAPID_FLASH MACRO IDX
	 SET_SSR_PATTERN IDX, 255, 255, 30, BIT_FADE_DOWN|BIT_FADE_CYCLE
	ENDM

SET_SSR_BLINK_FADE MACRO IDX
	 SET_SSR_PATTERN IDX, 255,   2,  1, BIT_FADE_DOWN
	ENDM

SET_SSR_SLOW_FLASH MACRO IDX
	; XXX need a sequence for this?
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


;==============================================================================
; BOOT BLOCK
;______________________________________________________________________________

;
; RESET VECTOR
;
V_RST	CODE	0x0000
	CLRWDT
	GOTO	START
;
; HIGH-PRIORITY INTERRUPT VECTOR
;
V_INT_H	CODE	0x0008
	CLRWDT
	GOTO	INT_HIGH
;
; LOW-PRIORITY INTERRUPT VECTOR
;
V_INT_L	CODE	0x0018
	CLRWDT
	GOTO	INT_LOW
;
; INITIALIZATION CODE
;
_BOOT	CODE	0x0100

S_FLASH:
	BSF	PLAT_RED, BIT_RED, ACCESS
	RCALL	DELAY_1_6_SEC
	BSF	PLAT_GREEN, BIT_GREEN, ACCESS
	RCALL	DELAY_1_6_SEC
	
	BCF	PLAT_RED, BIT_RED, ACCESS
	RCALL	DELAY_1_6_SEC
	BCF	PLAT_GREEN, BIT_GREEN, ACCESS
	RCALL	DELAY_1_6_SEC
	RETURN

D_FLASH:
	BSF	PLAT_RED, BIT_RED, ACCESS
	RCALL	DELAY_1_6_SEC
	BSF	PLAT_GREEN, BIT_GREEN, ACCESS
	RCALL	DELAY_1_6_SEC
	BSF	PLAT_YELLOW, BIT_YELLOW, ACCESS
	RCALL	DELAY_1_6_SEC
	BSF	PLAT_ACTIVE, BIT_ACTIVE, ACCESS
	RCALL	DELAY_1_6_SEC
	
	BCF	PLAT_RED, BIT_RED, ACCESS
	RCALL	DELAY_1_6_SEC
	BCF	PLAT_GREEN, BIT_GREEN, ACCESS
	RCALL	DELAY_1_6_SEC
	BCF	PLAT_YELLOW, BIT_YELLOW, ACCESS
	RCALL	DELAY_1_6_SEC
	BCF	PLAT_ACTIVE, BIT_ACTIVE, ACCESS
	RCALL	DELAY_1_6_SEC
	RETURN

START:
	CLRWDT
	CLRF	STKPTR, ACCESS		; clear stack error bits, set SP=0
	CALL	LUMOS_INIT
	CALL	D_FLASH
	CALL	SIO_INIT		; call after other TRIS bits set
	;
	; Get EEPROM settings
	;
	BSF	PLAT_RED, BIT_RED, ACCESS	; Panel: () () () R
	;
	; XXX Test sentinel values $000==$FF and $00F==$42.
	; XXX If they are not there, do a full factory reset of those
	; XXX settings to restore something that we know will work.
	;
	;
	; XXX Read values
	;
	CLRWDT
	CLRF	EEADRH, ACCESS		; EEPROM location $000
	CLRF	EEADR, ACCESS		; (note interrupts are still off now)
	BCF	EECON1, EEPGD, ACCESS	; select DATA EEPROM as target
	BCF	EECON1, CFGS, ACCESS
	BCF	EECON1, WREN, ACCESS	; disable writing
	BSF 	EECON1, RD, ACCESS	; initiate read operation
	MOVLW	0xFF			; 
	CPFSEQ	EEDATA, ACCESS		; byte == $FF?
	BRA	FACTORY_RESET		; if not, overwrite everything!
	MOVLW	0x0F			; try ending sentinel
	MOVWF	EEADR, ACCESS		; at $00F
	BSF	EECON1, RD, ACCESS
	MOVLW	0x42
	CPFSEQ	EEDATA, ACCESS		; byte == $42?
	BRA	FACTORY_RESET		; else, overwrite.
	;
	; Values checked out, so assume EEPROM is intact.
	; Read values into RAM variables and continue booting.
	;
	CLRWDT
	BCF	PIR2, EEIF, ACCESS	; clear interrupt flag
	BCF	PLAT_RED, BIT_RED, ACCESS	
	BSF	PLAT_YELLOW, BIT_YELLOW, ACCESS	; Panel: () () Y ()
	;
	BCF	EECON1, WREN, ACCESS	; Read (not write) access to memory
	BCF	EECON1, EEPGD, ACCESS	; Select access to DATA area
	BCF	EECON1, CFGS, ACCESS
	;
	CLRF	EEADRH, ACCESS
	MOVLW	1
	MOVWF	EEADR, ACCESS		; EEPROM location 0x001: baud rate
	BSF	EECON1, RD, ACCESS
	MOVF	EEDATA, W, ACCESS
	CALL	SIO_SET_BAUD_W
	;
	INCF	EEADR, F, ACCESS	; EEPROM location 0x002: device address
	BSF	EECON1, RD, ACCESS
	MOVFF	EEDATA, MY_ADDRESS
	;
	INCF	EEADR, F, ACCESS	; EEPROM location 0x003: phase offset MSB
	BSF	EECON1, RD, ACCESS
	MOVFF	EEDATA, PHASE_OFFSETH
	;
	INCF	EEADR, F, ACCESS	; EEPROM location 0x004: phase offset LSB
	BSF	EECON1, RD, ACCESS
	MOVFF	EEDATA, PHASE_OFFSETL
	;
	CLRF	EEADR, ACCESS	; Leave pointer at 0x000
	;
	BSF	PLAT_GREEN, BIT_GREEN, ACCESS	; Panel: () G Y ()
	;
	BCF	IPR1, TXIP, ACCESS	; TxD interrupt = low priority
	BCF	IPR1, RCIP, ACCESS	; RxD interrupt = low priority
	CLRWDT
	;
	; Initialize data structures
	;
	CLRF	SSR_STATE, ACCESS
	CLRF	YY_STATE, ACCESS
	BANKSEL	SSR_DATA_BANK
CH 	SET	0
	WHILE CH<=SSR_MAX
	 CLRF	SSR_00_VALUE+#v(CH), BANKED	; all SSRs OFF
	 CLRF	SSR_00_FLAGS+#v(CH), BANKED	; all SSR flags cleared
	 CLRF	SSR_00_STEP+#v(CH), BANKED
	 CLRF	SSR_00_SPEED+#v(CH), BANKED
	 CLRF	SSR_00_COUNTER+#v(CH), BANKED
CH	 ++
	ENDW
	;
	; Timer 0 for non-ZC boards
	;
	IF LUMOS_SLICE_TIMER == LUMOS_INTERNAL
	 CLRF	TMR0H, ACCESS
	 CLRF	TMR0L, ACCESS
	 BSF	INTCON2, TMR0IP, ACCESS	; set HIGH priority for timing
	 BSF	INTCON, TMR0IE, ACCESS	; enable timer 0 interrupts
	 BSF	T0CON, TMR0ON, ACCESS	; start timer 0 running
	ELSE
 	 IF LUMOS_SLICE_TIMER == LUMOS_ZC
	  BSF	INTCON, INT0IE, ACCESS	; enable ZC detect pin interrupt
 	 ELSE
  	  ERROR "LUMOS_SLICE_TIMER set incorrectly"
 	 ENDIF
	ENDIF
	;
	; Timer 2 for half-wave slice timing
	;
	MOVLW	SLICE_TMR_PERIOD	; set timer period
	MOVWF	PR2, ACCESS
	CLRF	TMR2, ACCESS		; reset timer
	BSF	IPR1, TMR2IP, ACCESS	; set HIGH priority for timing
	BSF	PIE1, TMR2IE, ACCESS	; enable timer 2 interrupts
	BSF	T2CON, TMR2ON, ACCESS	; start timer 2 running
	;
	BSF	PIE1, RCIE, ACCESS	; Enable RxD interrupts
	;
	; XXX setup SSR system state
	;
	BSF	INTCON, GIEH, ACCESS	; Enable high-priority interrupts
	BSF	INTCON, GIEL, ACCESS	; Enable low-priority interrupts
	; XXX more stuff here
	;
	; Launch mainline code
	;
	BCF	PLAT_YELLOW, BIT_YELLOW, ACCESS	; Panel: () G () ()
	BANKSEL	SSR_DATA_BANK
	CLRF	SSR_00_VALUE+SSR_GREEN, BANKED	; Green light cycles ~ 1/4 Hz
	SET_SSR_PATTERN SSR_GREEN, 0, 1, 1, BIT_FADE_UP|BIT_FADE_CYCLE
	GOTO	MAIN

FACTORY_RESET:
	CLRWDT
	;
	; write default configuration to EEPROM
	;
	BCF	INTCON, GIEH, ACCESS	; Disable high-priority interrupts
	BCF	INTCON, GIEL, ACCESS	; Disable low-priority interrupts
	CLRF	EEADRH, ACCESS		; EEPROM location 0x000
	CLRF	EEADR, ACCESS		; NOTE interrupts need to be OFF here!

	MOVLW	UPPER(DEFAULT_TBL)	; load lookup table pointer
	MOVWF	TBLPTRU, ACCESS
	MOVLW	HIGH(DEFAULT_TBL)
	MOVWF	TBLPTRH, ACCESS
	MOVLW	LOW(DEFAULT_TBL)
	MOVWF	TBLPTR, ACCESS

	BCF	EECON1, EEPGD, ACCESS	; select DATA EEPROM as target
	BCF	EECON1, CFGS, ACCESS
	BSF	EECON1, WREN, ACCESS	; enable writing

	MOVLW	EEPROM_SETTINGS_LEN
	MOVWF	I, ACCESS

FACTORY_RESET_LOOP:
	TBLRD	*+			; byte -> TABLAT
	MOVFF	TABLAT, EEDATA

	BCF	PIR2, EEIF, ACCESS	; clear interrupt flag
	MOVLW	0x55
	MOVWF	EECON2, ACCESS
	MOVLW	0xAA
	MOVWF	EECON2, ACCESS
	BSF	EECON1, WR, ACCESS	; start write cycle
	BSF	PLAT_YELLOW, BIT_YELLOW, ACCESS	; Panel: () () Y R
	BTFSS	PIR2, EEIF, ACCESS	; wait until write completes
	BRA	$-2
	CLRWDT
	BCF	PIR2, EEIF, ACCESS	; clear interrupt flag
	BCF	PLAT_YELLOW, BIT_YELLOW, ACCESS	; Panel: () () () R

	DECFSZ	I, F, ACCESS
	BRA	FACTORY_RESET_LOOP

	MOVLW	.16
	MOVWF	I, ACCESS

FACTORY_RESET_FLASH:
	IF HAS_ACTIVE
	 BSF	PLAT_ACTIVE, BIT_ACTIVE, ACCESS	; Panel: A G Y R
	ENDIF
	BSF	PLAT_GREEN, BIT_GREEN, ACCESS
	BSF	PLAT_YELLOW, BIT_YELLOW, ACCESS
	BSF	PLAT_RED, BIT_RED, ACCESS
	RCALL	DELAY_1_6_SEC
	IF HAS_ACTIVE
	 BCF	PLAT_ACTIVE, BIT_ACTIVE, ACCESS	; Panel: () () () ()
	ENDIF
	BCF	PLAT_GREEN, BIT_GREEN, ACCESS
	BCF	PLAT_YELLOW, BIT_YELLOW, ACCESS
	BCF	PLAT_RED, BIT_RED, ACCESS
	RCALL	DELAY_1_6_SEC
	DECFSZ	I, F, ACCESS
	BRA	FACTORY_RESET_FLASH

	RESET

DELAY_1_6_SEC:	; Approx 1/6 sec delay loop
	CLRWDT
	MOVLW	.8
	MOVWF	KK, ACCESS
	SETF	J, ACCESS
	SETF	K, ACCESS
	DECFSZ	K, F, ACCESS
	BRA	$-2
	DECFSZ	J, F, ACCESS
	BRA	$-.8
	DECFSZ	KK, F, ACCESS
	BRA	$-.14
	RETURN

;==============================================================================
; INTERRUPT HANDLERS
;______________________________________________________________________________
_INT	CODE
INT_LOW:
	MOVWF	ISR_TMPL_WREG, ACCESS	; Save W, status, and bank registers
	MOVFF	STATUS, ISR_TMPL_STATUS
	MOVFF	BSR, ISR_TMPL_BSR
	;
	; Serial I/O ready for transmit?
	;
INT_TX:
	BTFSS	PIR1, TXIF, ACCESS
	BRA	INT_TX_END
	CALL	SIO_SEND		; push next byte out
	BCF	PIR1, TXIF, ACCESS	; acknowledge interrupt
INT_TX_END:
	;
	; Serial I/O received a byte?
	;
INT_RX:
	BTFSS	PIR1, RCIF, ACCESS
	BRA	INT_RX_END
	CALL	SIO_RECV		; grab next byte
	BCF	PIR1, RCIF, ACCESS	; acknowledge interrupt
INT_RX_END:
	;
	; Finished with low-priority interrupts.
	; Clean up and go home.
	;
	MOVFF	ISR_TMPL_BSR, BSR
	MOVF	ISR_TMPL_WREG, W, ACCESS
	MOVFF	ISR_TMPL_STATUS, STATUS
	RETFIE

INT_HIGH:
	; High-priority interrupts automatically
	; save state (fast interrupt call)
	;
	; Zero-crossing start-of-cycle event signal
	;
INT_ZC:
	IF LUMOS_SLICE_TIMER==LUMOS_ZC
	 BTFSS	INTCON, INT0IF, ACCESS	; ZC signal asserted?
	 BRA	INT_ZC_END		; no, move along...
	 BCF	INTCON, INT0IF, ACCESS	; acknowledge interrupt
	ELSE
 	 IF LUMOS_SLICE_TIMER==LUMOS_INTERNAL
	  BTFSS	INTCON, TMR0IF, ACCESS	; 120 Hz timer expired?
	  BRA	INT_ZC_END		; no, move along...
	  MOVLW	HIGH(CYCLE_TMR_PERIOD)	; reset timer for another 1/120 sec.
	  MOVWF	TMR0H, ACCESS
	  MOVLW	LOW(CYCLE_TMR_PERIOD)
	  MOVWF	TMR0L, ACCESS
	  BCF	INTCON, TMR0IF, ACCESS	; acknowledge interrupt
 	 ELSE
  	  ERROR "LUMOS_SLICE_TIMER not set correctly"
 	 ENDIF
	ENDIF
	BSF	SSR_STATE, PRECYC, ACCESS	; mark start of pre-cycle countdown
	MOVFF	PHASE_OFFSETH, CUR_PREH
	MOVFF	PHASE_OFFSETL, CUR_PRE
INT_ZC_END:
	;
	; Start of cycle slice signal
	;
INT_TMR2:
	BTFSS	PIR1, TMR2IF, ACCESS		; has timer expired?
	BRA	INT_TMR2_END			; no, move along...
	BTFSS	SSR_STATE, PRECYC, ACCESS	; are we in pre-cycle countdown?
	BRA	INT_TMR2_NEXT			; no, signal next update run
	DECFSZ	CUR_PRE, F, ACCESS		; count down
	BRA	INT_TMR2_DONE
	TSTFSZ	CUR_PREH, ACCESS		; high-order byte
	BRA	INT_TMR2_MSB
	BCF	SSR_STATE, PRECYC, ACCESS	; END pre-cycle
	BSF	SSR_STATE, INCYC, ACCESS	; BEGIN active cycle
	SETF	CUR_SLICE, ACCESS		; initial slice value 0xFF (will count down to 0x00)
INT_TMR2_NEXT:
	BTFSC	SSR_STATE, INCYC, ACCESS	; if we're in active dimmer cycle now,
	BSF	SSR_STATE, SLICE_UPD, ACCESS	; then signal next update run
INT_TMR2_DONE:
	BCF	PIR1, TMR2IF, ACCESS		; acknowledge interrrupt
INT_TMR2_END:

	RETFIE	FAST

INT_TMR2_MSB:
	DECF	CUR_PREH, F, ACCESS		; tick down MSB, start another loop
	SETF	CUR_PRE, ACCESS
	BRA	INT_TMR2_DONE

;==============================================================================
; ACCESS DATA BANK
;______________________________________________________________________________
_ADATA	UDATA_ACS	0x000
ISR_TMPL_STATUS	RES	1
ISR_TMPL_BSR	RES	1
ISR_TMPL_WREG	RES	1
;ISR_TMPH_STATUS	RES	1
;ISR_TMPH_BSR	RES	1
;ISR_TMPH_WREG	RES	1
MY_ADDRESS	RES	1
PHASE_OFFSETH	RES	1
PHASE_OFFSETL	RES	1
SSR_STATE	RES	1		; major state/timing flags
YY_STATE 	RES	1
YY_COMMAND 	RES	1
YY_DATA    	RES	1
YY_LOOKAHEAD_MAX RES	1
YY_LOOK_FOR	RES	1
YY_BUF_IDX 	RES	1
YY_NEXT_STATE	RES	1
YY_YY		RES	1
CUR_PREH	RES	1
CUR_PRE		RES	1
CUR_SLICE	RES	1
TARGET_SSR	RES	1
I               RES	1
J               RES	1
K               RES	1
KK              RES	1

;==============================================================================
; DATA BANK 4
;______________________________________________________________________________
SSR_DATA_BANK	EQU	0x400
_SSR_DATA	UDATA	SSR_DATA_BANK
;
; *** THE FOLLOWING BLOCKS *MUST* BE THE SAME SIZE AS EACH OTHER ***
; and in fact, that size must be SSR_BLOCK_LEN.  THEY MUST ALSO be
; in this order, due to some optimizations that occur in the code.
;
SSR_BLOCK_LEN	EQU	SSR_MAX+1
SSR_00_VALUE	RES	SSR_BLOCK_LEN	; each SSR value 0x00-FF
SSR_00_FLAGS	RES	SSR_BLOCK_LEN
SSR_00_STEP	RES	SSR_BLOCK_LEN
SSR_00_SPEED	RES	SSR_BLOCK_LEN
SSR_00_COUNTER	RES	SSR_BLOCK_LEN

;==============================================================================
; DATA BANK 5: MAIN CODE DATA STORAGE
;______________________________________________________________________________
MAIN_DATA	EQU	0x500
_MAINDATA	UDATA	MAIN_DATA
YY_BUF_LEN	EQU	.128
YY_BUFFER	RES	YY_BUF_LEN

;==============================================================================
; DATA BANKS 6-: SEQUENCE STORAGE
;______________________________________________________________________________
SEQ_DATA	EQU	0x600
_SEQ_DATA	UDATA	SEQ_DATA

;==============================================================================
; MAINLINE CODE
;______________________________________________________________________________
_MAIN	CODE	0x0800
MAIN:
	CLRWDT
	BTFSC	SSR_STATE, SLICE_UPD, ACCESS
	RCALL	UPDATE_SSR_OUTPUTS

	BANKSEL	SIO_DATA_START
	BTFSC	SIO_STATUS, SIO_FERR, BANKED
	RCALL	ERR_SERIAL_FRAMING
	NOP

	BANKSEL	SIO_DATA_START
	BTFSC	SIO_STATUS, SIO_ORUN, BANKED
	RCALL	ERR_SERIAL_OVERRUN
	NOP

	BANKSEL	SIO_DATA_START
	BTFSC	SIO_STATUS, RXDATA_FULL, BANKED
	RCALL	ERR_SERIAL_FULL
	NOP

	BANKSEL	SIO_DATA_START
	BTFSC	SIO_STATUS, RXDATA_QUEUE, BANKED
	RCALL	RECEIVE_COMMAND
	NOP

	BRA	MAIN
	

ERR_SERIAL_FRAMING:
	BANKSEL	SIO_STATUS
	BCF	SIO_STATUS, SIO_FERR, BANKED
	SET_SSR_RAPID_FLASH SSR_RED
	SET_SSR_STEADY SSR_YELLOW
	RETURN
	
ERR_SERIAL_OVERRUN:
	BANKSEL	SIO_STATUS
	BCF	SIO_STATUS, SIO_ORUN, BANKED
	SET_SSR_RAPID_FLASH SSR_RED
	SET_SSR_RAPID_FLASH SSR_YELLOW
	RETURN

ERR_SERIAL_FULL:
	SET_SSR_RAPID_FLASH SSR_RED
	SET_SSR_SLOW_FADE SSR_YELLOW
	; XXX clear input buffer and reset state machine
	RETURN

ERR_COMMAND:
	SET_SSR_STEADY SSR_RED
	CLRF	YY_STATE, ACCESS	; reset state machine
	RETURN

RECEIVE_COMMAND:
CMD_BIT	EQU	7

	CLRWDT
	;
	; We just received a byte.  The state machine dictates what
	; we do with the byte we just got.
	;
	; State:	Byte:
	; [0] IDLE	DATA: ignore
	;		CMD for someone else: ignore
	;		store command, then decode it.
	;
	CALL	SIO_GETCHAR_W
	CLRWDT
	BANKSEL	SIO_DATA_START
	BTFSS	SIO_INPUT, CMD_BIT, BANKED
	BRA	DATA_BYTE		; it's a data byte
	;
	; ok, so it's a command. are we still waiting for another
	; command to complete?  If so, abort it and start over.
	; otherwise, get to work.
	;
	MOVF	YY_STATE, W, ACCESS
	BZ	INTERP_START	 
	;
	; ERROR: We hadn't finished with the last command yet, and here we
	; have another one!  (Yes, even if it's someone else's command, that
	; still means ours is apparently abandoned.)
	;
	RCALL	ERR_COMMAND		; let user know
	
INTERP_START:
	;
	; Start of a new command.
	;
	BANKSEL	SIO_DATA_START
	CLRWDT
	;
	; Is it ours?
	;
	IF NOT ROLE_SLAVE		; the slave chip has no address and sees no other commands
	 MOVF	SIO_INPUT, W, BANKED
	 ANDLW	0x0F
	 CPFSEQ	MY_ADDRESS, ACCESS
	 RETURN	; not my problem.
	ENDIF
	;
	; ok, so it's OUR command.  We're at state 0,
	; so let's decode it and go from here.
	;
	; === STATE 0 ===
	; New command byte received
	;
	; CMD 0 (BLACKOUT): exec -> 0
	; CMD 1 (ON_OFF): -> 1
	; CMD 2 (SET_LVL): -> 2
	; CMD 3 (BULK_UPD): -> 4
	; CMD 4 (RAMP_LVL): -> 5
	; CMD 5 ERROR -> 0
	; CMD 6 ERROR -> 0
	; CMD 7 (EXTENDED) -> 9
	;
	IF HAS_ACTIVE
	 SET_SSR_BLINK_FADE SSR_ACTIVE	; activity indicator
	ENDIF
	IF ROLE_SLAVE
	 SET_SSR_BLINK_FADE SSR_YELLOW	; slave activity indicator
	ENDIF
	SWAPF	SIO_INPUT, W, BANKED
	ANDLW	0x07
	BNZ	S0_CMD1

S0_CMD0:
	;
	; BLACKOUT:
	;
	;   ___7______6______5______4______3______2______1______0__
	;  |      |                    |                           |
	;  |   1  |          0         |   Target device address   | SIO_INPUT
	;  |______|______|______|______|______|______|______|______|
	;  |                                  |          0         |
	;  |                                  |   (Command code)   | W
	;  |______|______|______|______|______|______|______|______|
	;
	BANKSEL	SSR_DATA_BANK
CH 	SET	0
	WHILE CH<=SSR_MAX
	 CLRF	SSR_00_VALUE+#v(CH), BANKED	; all SSRs OFF
	 CLRF	SSR_00_FLAGS+#v(CH), BANKED	; all SSR flags cleared
	 CLRF	SSR_00_STEP+#v(CH), BANKED
	 CLRF	SSR_00_SPEED+#v(CH), BANKED
	 CLRF	SSR_00_COUNTER+#v(CH), BANKED
CH	 ++
	ENDW

	IF ROLE_MASTER
	 MOVLW	0x80		; Pass this command on to the other 
	 CALL	SIO_WRITE_W	; processor too
	 SET_SSR_BLINK_FADE SSR_YELLOW	; slave activity indicator
	ENDIF
	RETURN

S0_CMD1:
	MOVWF	YY_COMMAND, ACCESS	; save command byte in YY_COMMAND
	DECFSZ	WREG, W, ACCESS
	BRA	S0_CMD2
	; ON_OFF:
	MOVLW	1
	MOVWF	YY_STATE, ACCESS	; -> state 1 (wait for channel)
	RETURN

S0_CMD2:
	; SET_LEVEL
	DECFSZ	WREG, W, ACCESS
	BRA	S0_CMD3
	MOVLW	2
	MOVWF	YY_STATE, ACCESS	; -> state 2 (wait for channel)
	RETURN

S0_CMD3:
	; BULK_UPD
	DECFSZ	WREG, W, ACCESS
	BRA	S0_CMD4
	MOVLW	4
	MOVWF	YY_STATE, ACCESS	; -> state 4 (wait for channel)
	RETURN

S0_CMD4:
	; RAMP_LVL
	DECFSZ	WREG, W, ACCESS
	BRA	S0_CMD5
	MOVLW	5
	MOVWF	YY_STATE, ACCESS	; -> state 5 (wait for channel)
	RETURN

S0_CMD5:
	; Unimplemented Command
	DECFSZ	WREG, W, ACCESS
	BRA	S0_CMD6
	BRA	ERR_COMMAND

S0_CMD6:
	; Unimplemented Command
	DECFSZ	WREG, W, ACCESS
	BRA	S0_CMD7
	BRA	ERR_COMMAND

S0_CMD7:
	; Extended commands
	DECFSZ	WREG, W, ACCESS
	BRA	S0_CMD_ERR
	MOVLW	9
	MOVWF	YY_STATE, ACCESS	; -> state 9 (decode extended command)
	RETURN

S0_CMD_ERR:
	; BUG: We really shouldn't have arrived here!
	BRA	ERR_COMMAND		; XXX bug really
	
DATA_BYTE:
	CLRWDT
	;
	; Data byte:  If we're at state 0, we aren't expecting
	; this, so just ignore it. 
	;
	MOVF	YY_STATE, W, ACCESS
	BNZ	S1_DATA
	RETURN
	;
	; We're collecting data, so add this to the pile, depending
	; on where the state machine is now.
	;
S1_DATA:
	;
	; STATE 1: collect channel number for ON_OFF command
	;          and execute.
	;
	MOVFF	SIO_INPUT, YY_DATA;		Save data byte in YY_DATA
	DECFSZ	WREG, W, ACCESS
	BRA	S2_DATA
	;
	; ON_OFF:
	;
	;   ___7______6______5______4______3______2______1______0__
	;  |      |                    |                           |
	;  |   1  |          1         |   Target device address   | YY_COMMAND
	;  |______|______|______|______|______|______|______|______|
	;  |      |0=off |                                         |
	;  |   0  |1=on  |           Channel ID (0-47)             | YY_DATA
	;  |______|______|______|______|______|______|______|______|
	;
	RCALL	XLATE_SSR_ID
	BTFSC	TARGET_SSR, INVALID_SSR, ACCESS
	BRA	ERR_COMMAND				; SSR number out of range
	BTFSC	TARGET_SSR, NOT_MY_SSR, ACCESS
	BRA	PASS_DOWN_ON_OFF
	BTFSC	YY_DATA, 6, ACCESS
	CLRF	YY_STATE, ACCESS			; reset command state
	BRA	ON_OFF_ON
	CLRF	WREG, ACCESS
	BRA	SSR_OUTPUT_VALUE			; set value off and return

ON_OFF_ON:
	SETF	WREG, ACCESS
	BRA	SSR_OUTPUT_VALUE			; set value on and return
	
PASS_DOWN_ON_OFF:
	IF ROLE_MASTER
	 MOVLW	0x90
	 CALL	SIO_WRITE_W
	 MOVF	TARGET_SSR, W, ACCESS
	 ANDLW	0x3F
	 BTFSC	YY_DATA, 6, ACCESS
	 BSF    WREG, 6, ACCESS
	 CALL 	SIO_WRITE_W
	 SET_SSR_BLINK_FADE SSR_YELLOW	; slave activity indicator
	ELSE
	 BRA	ERR_COMMAND
	ENDIF

S2_DATA:
	DECFSZ	WREG, W, ACCESS
	BRA	S3_DATA
	; SET_LVL channel byte
	RCALL	XLATE_SSR_ID
	BTFSC	TARGET_SSR, INVALID_SSR, ACCESS
	BRA	ERR_COMMAND
	BTFSC	YY_DATA, 6, ACCESS	; preserve bit 6 (LSB of value)
	BSF	TARGET_SSR, 6, ACCESS
	INCF	YY_STATE, F, ACCESS	; -> state 3 (wait for level byte)
	RETURN

S3_DATA:
	; SET_LVL value byte
	DECFSZ	WREG, W, ACCESS
	BRA	S4_DATA
	;
	; SET_LVL:
	;
	;   ___7______6______5______4______3______2______1______0__
	;  |      |                    |                           |
	;  |   1  |          2         |   Target device address   | YY_COMMAND
	;  |______|______|______|______|______|______|______|______|
	;  |NOT_MY|Value |                                         |
	;  | _SSR |LSB   |           Channel ID (0-47)             | TARGET_SSR
	;  |______|______|______|______|______|______|______|______|
	;  |      |                                                |
	;  |   0  |            Value MSBs (0-127)                  | YY_DATA
	;  |______|______|______|______|______|______|______|______|
	;
	BTFSC	TARGET_SSR, NOT_MY_SSR, ACCESS
	BRA	PASS_DOWN_SET_LVL
	BCF	STATUS, C, ACCESS			; move LSB -> CARRY
	BTFSC	TARGET_SSR, 6, ACCESS
	BSF	STATUS, C, ACCESS
	RLCF	YY_DATA, W, ACCESS			; Shift LSB into value byte
	CLRF	YY_STATE, ACCESS			; reset state (end of command)
	MOVF	YY_DATA, W, ACCESS
	BRA	SSR_OUTPUT_VALUE			; set SSR to 8-bit YY_DATA value

PASS_DOWN_SET_LVL:
	IF ROLE_MASTER
	 MOVLW	0xA0
	 CALL	SIO_WRITE_W
	 BCF	TARGET_SSR, 7, ACCESS
	 MOVF	TARGET_SSR, W, ACCESS
	 CALL	SIO_WRITE_W
	 MOVF	YY_DATA, W, ACCESS
	 CALL	SIO_WRITE_W
	 CLRF	YY_STATE, ACCESS
	 SET_SSR_BLINK_FADE SSR_YELLOW	; slave activity indicator
	 RETURN
	ELSE
	 BRA	ERR_COMMAND			; XXX bug?
	ENDIF

S4_DATA:
	DECFSZ	WREG, W, ACCESS
	BRA	S5_DATA
	; BULK_UPD, received channel byte
	RCALL	XLATE_SSR_ID
	BTFSC	TARGET_SSR, INVALID_SSR, ACCESS
	BRA	ERR_COMMAND
	BTFSC	YY_DATA, 6, ACCESS	; preserve bit 7 (resolution flag)
	BSF	TARGET_SSR, 6, ACCESS
	WAIT_FOR_SENTINEL .57, 0b01010101, 0	; -> S6.0 when sentinel found
	RETURN

S5_DATA:
	DECFSZ	WREG, W, ACCESS
	BRA	S6_DATA
	; RAMP_LVL received channel number
	RCALL	XLATE_SSR_ID
	BTFSC	TARGET_SSR, INVALID_SSR, ACCESS
	BRA	ERR_COMMAND
	BTFSC	YY_DATA, 6, ACCESS	; preserve bit 6 (direction flag)
	BSF	TARGET_SSR, 6, ACCESS
	MOVLW	7
	MOVWF	YY_STATE, ACCESS	; -> state 7 (wait for step count)
	RETURN
	

S6_DATA:
	DECFSZ	WREG, W, ACCESS
	BRA	S7_DATA
	;
	; State 6: Wait for Sentinel
	;
	; In this state, the machine is looking ahead in the data stream
	; for a sentinel pattern.  The pattern is selected by YY_LOOK_FOR
	; and must be seen in the next YY_LOOKAHEAD_MAX bytes (which will be destructively
	; altered here).  If the sentinel is not recognized before YY_LOOKAHEAD_MAX runs
	; out, we abort on ERR_COMMAND.
	;
	; Once it's recognized, we move to YY_NEXT_STATE immediately.
	;
	; In order to do this, we buffer up the input received in YY_BUFFER.  This is
	; a YY_BUF_LEN-byte memory space aligned on a data bank boundary where YY_BUF_LEN
	; is not more than 256 (currently it's 128).  We will record the character at
	; YY_BUFFER[YY_BUF_IDX++] and stop if YY_BUF_IDX > YY_LOOKAHEAD_MAX.
	;
	CLRWDT
	MOVF	YY_DATA, W, ACCESS		; Is this the sentinel we're looking for?
	CPFSEQ	YY_LOOK_FOR, ACCESS
	BRA	S6_KEEP_LOOKING
	;
	; We have a packet, now switch on YY_NEXT_STATE to decode and execute
	; the completed command.
	;
	MOVF	YY_NEXT_STATE, W, ACCESS
	BNZ	S6_1_DATA
	;
	; S6.0: Complete BULK_UPD command (from state 5)
	;
	; BULK_UPD:
	;
	;   ___7______6______5______4______3______2______1______0__
	;  |      |                    |                           |
	;  |   1  |          3         |   Target device address   | YY_COMMAND
	;  |______|______|______|______|______|______|______|______|
	;  |NOT_MY|0=low |                                         |
	;  | _SSR |1=high|           Channel ID (0-47)             | TARGET_SSR
	;  |______|______|______|______|______|______|______|______|
	;  |      |                                                |
	;  |   0  |           Number of channels - 1 (0-47)        | YY_BUFFER+0
	;  |______|______|______|______|______|______|______|______|
	;  |      |                                                |
	;  |   0  |           Value for SSR #c                     | YY_BUFFER+1
	;  |______|______|______|______|______|______|______|______|
	;  |      |                                                |
	;  |   0  |           Value for SSR #c+1                   | YY_BUFFER+2
	;  |______|______|______|______|______|______|______|______|
	;				.
	;				.
	; IF LOW RES:			.
	;   _______________________________________________________
	;  |      |                                                |
	;  |   0  |           Value for SSR #c+n-1                 | YY_BUFFER+n
	;  |______|______|______|______|______|______|______|______|
	;                                                       <-- YY_BUF_IDX == n+1
	;
	; ELSE:      
	;   _______________________________________________________
	;  |      |                                                |
	;  |   0  |           Value for SSR #c+n-1                 | YY_BUFFER+n
	;  |______|______|______|______|______|______|______|______|
	;  |      |                                                |
	;  |   0  |                   $56                          | YY_BUFFER+n+1
	;  |______|______|______|______|______|______|______|______|
	;  |      |LSB   |LSB   |LSB   |LSB   |LSB   |LSB   |LSB   |
	;  |   0  |Ch#c  |Ch#c+1|Ch#c+2|Ch#c+3|Ch#c+4|Ch#c+5|Ch#c+6| YY_BUFFER+n+2
	;  |______|______|______|______|______|______|______|______|
	;  |      |LSB   |LSB   |LSB   |LSB   |LSB   |LSB   |LSB   |
	;  |   0  |Ch#c+7|Ch#c+8|Ch#c+9|Chc+10|Chc+11|Chc+12|Chc+13| YY_BUFFER+n+3
	;  |______|______|______|______|______|______|______|______|
	;				.
	;				.
	;              		 	.
	;   _______________________________________________________
	;  |      |LSB   |LSB   |LSB   |LSB   |LSB   |LSB   |LSB   |
	;  |   0  |      |      |      |      |      |      |      | YY_BUFFER+n+1+
	;  |______|______|______|______|______|______|______|______|    int((n+6)/7)
	;                                                        <-- YY_BUF_IDX = n+1+
	;                                                               int((n+6)/7)
	;
	CLRF	YY_STATE, ACCESS		; go ahead and signal end of command parsing
	;					; now so we can just RETURN when done.
	; Calculate expected data lengths
	;
	LFSR	0, YY_BUFFER			
	INCF	INDF0, F, ACCESS		; fix it so that YY_BUFFER[0] is N, not N-1
	MOVF	TARGET_SSR, W, ACCESS		; start
	ANDLW	0x3F
	ADDWF	INDF0, W, ACCESS		; start + N
	SUBLW	NUM_CHANNELS			; start + N > NUM_CHANNELS? 
	BNC	ERR_COMMAND			; YES: bad command - reject it!
	;
	; Do we have all the bytes yet?  (Or did a data byte happen to equal our sentinel?)
	;
	MOVF 	INDF0, W, ACCESS		; W=N
	CPFSGT	YY_BUF_IDX, ACCESS		; if IDX > N, we're done.
	RETURN					; otherwise, go back and wait for more data
	;
	; Do we have the correct packet ending?
	;
	BTFSC	TARGET_SSR, 6, ACCESS		; 1=highres, 0=lowres
	BRA	S6_0_CHK_HR
	INCF	INDF0, W, ACCESS		; Low-res bounds check:
	CPFSEQ	YY_BUF_IDX, ACCESS		; Should see IDX == N+1 if the packet is complete
	BRA	ERR_COMMAND			; and correctly terminated
	;
	; start bulk update of channels
	;
	; Remember that since the protocol specifies that we get N-1 in the length field,
	; we will always have at least 1 channel to change.  (Thre's no way to specify a
	; BULK_UPD command to change 0 channels.)
	;
	; Does the target range of channels lie entirely within the slave chip's 
	; range?  If so, just pass the whole command down to it, with starting SSR
	; number translated down to its range...
	;
	BTFSS	TARGET_SSR, NOT_MY_SSR, ACCESS
	BRA	S6_0_UPDATE_MSB
	IF ROLE_MASTER
	 CLRWDT
	 MOVLW	0xB0				; command code
	 CALL	SIO_WRITE_W
	 MOVF	TARGET_SSR, W, ACCESS		; starting channel
	 CALL	SIO_WRITE_W
	 LFSR	0, YY_BUFFER			; now write YY_BUFFER[0..YY_BUF_IDX-1]
S6_0_PD_ALL:
	 MOVF	POSTINC0, W, ACCESS
	 CALL	SIO_WRITE_W
	 DECFSZ YY_BUF_IDX, F, ACCESS
	 BRA	S6_0_PD_ALL
	 MOVLW	0x55				; and finally the trailing sentinel byte $55.
	 CALL	SIO_WRITE_W
	 RETURN
	ELSE
	 BRA	ERR_COMMAND			; XXX bug really
	ENDIF

S6_0_UPDATE_MSB:
	;
	; Copy the bytes directly into SSR registers
	;
	CLRWDT
	LFSR	0, YY_BUFFER			; FSR0 points to each source data byte to copy
	LFSR	1, SSR_00_VALUE			; FSR1 points to each destination SSR control block
	LFSR	2, SSR_00_FLAGS			; FSR2 points to the SSR flag blocks
	MOVF	TARGET_SSR, W, ACCESS		; Move in to first SSR in target range
	ANDLW	0x3F
	ADDWF	FSR1L, F, ACCESS		
	ADDWF	FSR2L, F, ACCESS
	IF ROLE_MASTER
	 SUBLW	.24
	 MOVWF	KK, ACCESS			; KK=24-start (max # of channels on OUR chip)
	ENDIF
	MOVFF	POSTINC0, I			; K=I=N counter		(I = *FSR0++)
	MOVFF	I, K				; (We'll use K for the LSB update later)

S6_0_UPDATE_NEXT:
	CLRF	POSTINC2, ACCESS		; clear SSR flags 
	MOVFF	POSTINC0, INDF1 		; set SSR	(*fsr1++ = *fsr0++ << 1)
	RLNCF	POSTINC1, F, ACCESS
	IF ROLE_MASTER
	 DCFSNZ	KK, F, ACCESS
	 BRA	S6_0_PASS_DOWN_MSB		; ran out of KK, send rest to slave chip
	ENDIF
	DECFSZ	I, F, ACCESS
	BRA	S6_0_UPDATE_NEXT
	RETURN

	IF ROLE_MASTER
S6_0_PASS_DOWN_MSB:
	 DCFSNZ	I, F, ACCESS			; we left before I-- happened
	 RETURN					; already out of data to send; don't bother the slave
	 MOVLW	0xB0				; Start command to slave with I remaining values
	 CALL	SIO_WRITE_W			
	 CLRW 					; target SSR always 0 in this case
	 BTFSC	TARGET_SSR, 6, ACCESS		; but keep the resolution bit
	 BSF	WREG, 6, ACCESS
	 CALL	SIO_WRITE_W			
	 DECF	I, W, ACCESS			; I channels left for slave to update, protocol wants I-1
	 CALL 	SIO_WRITE_W
S6_0_PD_NEXT_MSB:
	 MOVF	POSTINC0, W, ACCESS
	 CALL	SIO_WRITE_W			; ... write I bytes of values ...
	 DECFSZ	I, F, ACCESS
	 BRA	S6_0_PD_NEXT_MSB
	 MOVLW	0x55				; sentinel $55 after bytes
	 CALL	SIO_WRITE_W
	 RETURN
	ENDIF

;
; given N and starting channel C,
; if C >= 24 then pass down BULK_UPD C-24 and done.
; if N+C < 24 then A=N, do update
; else set A = N-(N+C-24) = -C+24 = 24-C, do update
; update: decr A,N  when A runs out, switch to pass down mode until N runs out
;
;
; XXX note
;   N: result negative (2s comp)
;  OV: overflow into sign bit occurred
;   Z: result zero
;  DC: carry into bit 4   for SUB, DC = ~DBORROW
;   C: carry into bit 8   for SUB, C = ~BORROW
;
; SUBLW k  or SUBWF k,d,a
;  W <- k-W   d <- k-W
;
; k<W	 ~C
; k<=W	 ~C ||  Z
; k>W	  C && ~Z
; k>=W	  C
; k==W	  Z
; k!=W   ~Z
;
;
S6_0_CHK_HR:					; High-res bounds check:
	CLRF	I, ACCESS			; I=Number of LSB bytes=int((N+6)/7)
	CLRF	J, ACCESS			; J=capacity of I bytes
S6_0_INCR:
	INCF	I, F, ACCESS			; next byte; I++, J+=7
	MOVLW	7
	ADDWF	J, F, ACCESS
	MOVF	INDF0, W, ACCESS		; W=N
	SUBWF	J, W, ACCESS			; J < N? keep counting
	BNC	S6_0_INCR
	;
	; I is now the number of LSB bytes, INDF0 is N (# channels), 
	; our intermediate sentinel $56 should be at N+1, total data 
	; length should be N+1+I
	;
	INCF	INDF0, W, ACCESS		; J = W = N+1
	MOVWF	J, ACCESS
	ADDWF	FSR0L, F, ACCESS		; move pointer to YY_BUFFER[N+1]
	MOVLW	0x56
	CPFSEQ	INDF0, ACCESS			; sentinel byte correct for high-res block?
	BRA	ERR_COMMAND			; NO, abort command
	MOVF	J, W, ACCESS			; W = N+1
	ADDWF	I, W, ACCESS			; W = N+1+I
	CPFSEQ	YY_BUF_IDX, ACCESS		; packet size must == N+1+I
	BRA	ERR_COMMAND			; or else we abort here
	RCALL	S6_0_UPDATE_MSB			; set all the MSBs first
	;
	; Update all the LSBs
	; At this point: K=N, FSR0->sentinel.  Or should...
	;
	; Inside this block, we'll use YY_YY as temporary storage for the
	; LSB collector for sending bulk updates to the slave chip.  Here
	; it maps like this:
	;
	;                     ___7______6______5______4______3______2______1______0__
	; YY_YY              |S6_NOT|LSB   |LSB   |LSB   |LSB   |LSB   |LSB   |LSB   |
	;                    |_INIT |#0    |#1    |#2    |#3    |#4    |#5    |#6    |
	;                    |______|______|______|______|______|______|______|______|
	;
	; Flags defined here:
	;			  76543210
S6_NOT_INIT	EQU	7	; 1-------  1 if not yet prepared to collect bits
	;
	;
	CLRWDT
	IF ROLE_MASTER
	 CLRF	YY_YY, ACCESS			; initial state: not yet handling slave's data
	 BSF	YY_YY, 7, ACCESS
	ENDIF
	IF ROLE_SLAVE
	 MOVLW	0x55				; the slave will see $55 for BOTH sentinels
	ELSE
	 MOVLW	0x56
	ENDIF
	CPFSEQ	POSTINC0, ACCESS		; now FSR0->first block of bits
	BRA	ERR_COMMAND			; XXX really a bug, I think
	LFSR	1, SSR_00_VALUE	
	MOVF	TARGET_SSR, W, ACCESS		; Move FSR1 to first SSR in target range
	ANDLW	0x3F
	ADDWF	FSR1L, F, ACCESS		
	IF ROLE_MASTER
	 SUBLW	.24				; KK = 24-start (max # of channels on OUR chip)
	 MOVWF	KK, ACCESS
	ENDIF

S6_0_UPDATE_LSB:
X	SET	6
	WHILE	X >= 0
	 IF ROLE_MASTER
	  BTFSC YY_YY, 7, ACCESS		; if we're packing up for the slave:
	  BRA	S6_0_LSB_A#v(X)			;   (if not, skip down there a bit...)
	  RRNCF I, F, ACCESS			; shift bit position
	  BTFSS	I, 7, ACCESS			; if we wrap around to bit 7 again, we filled up the block.
	  BRA	S6_0_LSB_B#v(X)
	  MOVF	YY_YY, W, ACCESS		; ship out the completed byte
	  CALL	SIO_WRITE_W
	  CLRF 	YY_YY, ACCESS
	  RRNCF	I, F, ACCESS
S6_0_LSB_B#v(X):
	  MOVF	I, W, ACCESS
	  BTFSC	INDF0, #v(X), ACCESS		; set bit in I if source bit is set
	  IORWF YY_YY, F, ACCESS
	  BRA	S6_0_LSB_C#v(X)
	 ENDIF
S6_0_LSB_A#v(X):				; NOT packing up for the slave, just updating locally
	 BTFSC	INDF0, #v(X), ACCESS		; If the source bit is set,
	 BSF	POSTINC1, 0, ACCESS		; set the LSB of the target SSR and move on to the next one.
	 IF ROLE_MASTER
S6_0_LSB_C#v(X):
	  BTFSS	YY_YY, 7, ACCESS		; If we've already handled this, stop counting KK.
	  BRA S6_0_LSB_#v(X)
	  DECFSZ KK, F, ACCESS			; If we've run out of channels for this chip,
	  BRA	S6_0_LSB_#v(X)
	  CLRF	YY_YY, ACCESS		 	; Start building up packed bytes to send to the slave.
	  MOVLW	0x80
	  MOVWF	I, ACCESS			; I = bitmask to set in packed byte
S6_0_LSB_#v(X):
	 ENDIF
	 DCFSNZ	K, F, ACCESS			; Stop if we've set K bits already
	 BRA	S6_0_DONE
X	 --
	ENDW
	INCF	FSR0L, F, ACCESS		; advance to next byte full of LSB bits
	BRA	S6_0_UPDATE_LSB
	;
	; if we're packing up a byte for the slave (YY_YY<7> clear),
	; AND we were in the middle of one of them (I<7> clear),
	; we need to ship out the last byte in the sequence
	;
S6_0_DONE:
	IF ROLE_MASTER
	 BTFSC	YY_YY, 7, ACCESS		; packing up for slave
	 BRA	S6_0_NO_FLUSH
	 BTFSC	I, 7, ACCESS			; pending output
	 BRA	$+6
	 MOVF	YY_YY, W, ACCESS
	 CALL	SIO_WRITE_W
	 MOVLW	0x55				; add sentinel to output
	 CALL	SIO_WRITE_W
S6_0_NO_FLUSH:
	ENDIF
	CLRF	YY_STATE, ACCESS
	RETURN

S6_1_DATA:
	BRA	ERR_COMMAND			; XXX should be bug

S6_RESTART:
	; We stopped too early -- resume now
	RETURN

S6_KEEP_LOOKING:
	MOVF	YY_BUF_IDX, W, ACCESS		; Have we reached our limit (idx >= max)?
	CPFSGT	YY_LOOKAHEAD_MAX, ACCESS	; 
	BRA	ERR_COMMAND			; Yes:  Abort here and ignore data to next cmd
	LFSR	0, YY_BUFFER			; No: Save character in buffer and keep waiting
	MOVF	YY_BUF_IDX, W, ACCESS
	ADDWF	FSR0L, F, ACCESS
	MOVFF	YY_DATA, INDF0
	INCF	YY_BUF_IDX, W, ACCESS
	RETURN

S7_DATA:
	DECFSZ	WREG, W, ACCESS
	BRA	S8_DATA
	; RAMP_LVL recieved step count
	INCF	YY_DATA, W, ACCESS		; step count - 1 sent in protocol
	MOVWF	YY_YY, ACCESS			; actual step count saved in YY_YY (1-128)
	INCF	YY_STATE, F, ACCESS		; -> state 8 (wait for time interval byte)
	RETURN
	
S8_DATA:
	DECFSZ	WREG, W, ACCESS
	BRA	S9_DATA
	INCF	YY_DATA, F, ACCESS
	;
	; RAMP_LVL:
	;
	;   ___7______6______5______4______3______2______1______0__
	;  |      |                    |                           |
	;  |   1  |          4         |   Target device address   | YY_COMMAND
	;  |______|______|______|______|______|______|______|______|
	;  |NOT_MY|0=down|                                         |
	;  | _SSR |1=up  |           Channel ID (0-23)             | TARGET_SSR
	;  |______|______|______|______|______|______|______|______|
	;  |                                                       |
	;  |              Steps between update (1-128)             | YY_YY
	;  |______|______|______|______|______|______|______|______|
	;  |      |                                                |
	;  |             update every n/120 sec (1-128)            | YY_DATA
	;  |______|______|______|______|______|______|______|______|
	;
	BTFSC	TARGET_SSR, NOT_MY_SSR, ACCESS
	BRA	S8_PASS_DOWN_RAMP_LVL
	LFSR	0, SSR_00_FLAGS
	MOVF	TARGET_SSR, W, ACCESS
	ANDLW	0x3F
	ADDWF	FSR0L, F, ACCESS
	CLRF	INDF0, ACCESS
	BTFSC	TARGET_SSR, 6, ACCESS		; this is cheaper than branching :)
	BSF	INDF0, FADE_UP, ACCESS
	BTFSS	TARGET_SSR, 6, ACCESS
	BSF	INDF0, FADE_DOWN, ACCESS
	MOVLW	SSR_BLOCK_LEN
	ADDWF	FSR0L, F, ACCESS		; jump to this SSR's step byte
	MOVFF	YY_YY, INDF0
	ADDWF	FSR0L, F, ACCESS		; jump to this SSR's speed byte
	MOVFF	YY_DATA, INDF0
	ADDWF	FSR0L, F, ACCESS		; jump to this SSR's counter byte
	MOVFF	YY_DATA, INDF0
	CLRF	YY_STATE, ACCESS
	RETURN

S8_PASS_DOWN_RAMP_LVL:
	;
	; Hand off RAMP_LVL command to slave chip.
	;
	IF ROLE_MASTER
	 MOVLW 	0xC0				; command byte
	 CALL	SIO_WRITE_W
	 MOVF	TARGET_SSR, W, ACCESS
	 BCF	TARGET_SSR, 7, ACCESS
	 CALL	SIO_WRITE_W			; channel + direction
	 DECF	YY_YY, W, ACCESS		; steps - 1
	 CALL	SIO_WRITE_W
	 DECF	YY_DATA, W, ACCESS		; speed - 1
	 CALL	SIO_WRITE_W
	 RETURN
	ENDIF
	BRA	ERR_COMMAND			; XXX bug really
	
S9_DATA:
	DECFSZ	WREG, W, ACCESS
	BRA	S10_DATA
	;
	; State 9:  Extended command code received; decode further
	;
	;   ___7______6______5______4______3______2______1______0__
	;  |      |                    |                           |
	;  |   1  |          7         |   Target device address   | YY_COMMAND
	;  |______|______|______|______|______|______|______|______|
	;  |                                                       |
	;  |               Extended Command Code                   | YY_DATA   
	;  |______|______|______|______|______|______|______|______|
	;
	; Extended commands decode like this:
	;	01xxxxxx	privileged configuration commands
	;	010----- 	CF_PHASE command (remaining bits are data)
	;	0110----	CF_ADDR command (remaining bits are data)
	;	01110--- 	other CF_* commands (remaining bits are command number)
	;       001-----	IC_* internal (mater->slave) commands
	;	000-----	Regular extended commands
	;        
	BTFSC	YY_DATA, 6, ACCESS
	BRA	S9_PRIV_CMD

S9_PRIV_CMD:
	; received privileged configuration command  	; 01xxxxxx
	;
	; Anything from here down requires the privilege bit to be set.
	;
	BTFSS	SSR_STATE, PRIV_MODE, ACCESS
	BRA	ERR_COMMAND			; XXX any other flags?
	;
	; decode which command this is
	;
	BTFSS	YY_DATA, 5, ACCESS
	BRA	S9_CF_PHASE				; 010xxxxx
	BTFSS	YY_DATA, 4, ACCESS
	BRA	S9_CF_ADDR				; 0110xxxx
	; other priv commands              		; 0111xxxx
	MOVLW	0x0F
	ANDWF	YY_DATA, W, ACCESS
	BNZ	S9_PRIV_1

S9_PRIV_0:
	;
	; CF_NOPRV:
	;
	;   ___7______6______5______4______3______2______1______0__
	;  |      |                    |                           |
	;  |   1  |          7         |   Target device address   | YY_COMMAND
	;  |______|______|______|______|______|______|______|______|
	;  |      |      |      |                                  |
	;  |   0  |   1  |   1  |   1  |             0             | YY_DATA
	;  |______|______|______|______|______|______|______|______|
	;
	;
	BCF	SSR_STATE, PRIV_MODE, ACCESS
	CLRF	YY_STATE, ACCESS
	RETURN

S9_PRIV_1:
	DECFSZ	WREG, W, ACCESS
	BRA	S9_PRIV_2
	;
	; CF_CONF command recognized.  Expect packet of 4 more bytes...
	;
	WAIT_FOR_SENTINEL 4, 0b00111101, 1	; -> S6.1 when sentinel found
	RETURN

S9_PRIV_2:
	DECFSZ	WREG, W, ACCESS
	BRA	S9_PRIV_3
	;
	; CF_BAUD command recognized.  Expect packet of 2 more bytes...
	;
	WAIT_FOR_SENTINEL 2, 0b00100110, 2	; -> S6.2 when sentinel found
	RETURN

S9_PRIV_3:
	DECFSZ	WREG, W, ACCESS
	BRA	S9_PRIV_4
	;
	; CF_RESET command recognized.  Expect packet of 2 more bytes...
	;
	WAIT_FOR_SENTINEL 2, 0b01110010, 3	; -> S6.3 when sentinel found
	RETURN

S9_PRIV_4:
	BRA	ERR_COMMAND

S9_CF_PHASE:
	WAIT_FOR_SENTINEL 3, 0b01001111, 4	; -> S6.4 when sentinel found
	RETURN

S9_CF_ADDR:
	WAIT_FOR_SENTINEL 3, 0b01000100, 5	; -> S6.5 when sentinel found
	RETURN
	
S10_DATA:
	DECFSZ	WREG, W, ACCESS
	BRA	S11_DATA
	
S11_DATA:
	DECFSZ	WREG, W, ACCESS
	BRA	S12_DATA
	
S12_DATA:
	DECFSZ	WREG, W, ACCESS
	BRA	S13_DATA
	
S13_DATA:
	DECFSZ	WREG, W, ACCESS
	BRA	S14_DATA
	
S14_DATA:
	DECFSZ	WREG, W, ACCESS
	BRA	S15_DATA
	
S15_DATA:
	DECFSZ	WREG, W, ACCESS
	BRA	S16_DATA
	
S16_DATA:
	; Or this WOULD be state 16, except there isn't one!
	; Any state >15 lands here.  Handle the exception and
	; abort the command being processed.
	;
	; XXX flag internal error
	CLRF	YY_STATE, ACCESS
	RETURN

SSR_OUTPUT_VALUE:
	;
	; Change an SSR's output value.  This does the same thing
	; as SET_SSR_VALUE, except the other one is a macro we can
	; only use at runtime with constant SSR IDs (but more efficiently)
	; while this works at runtime.
	;
	; Changes the output value of TARGET_SSR to the W register.
	; Uses FSR0 register and KK.
	;
	CLRWDT
	BCF	TARGET_SSR, 7, ACCESS
	BCF	TARGET_SSR, 6, ACCESS
	MOVWF	KK, ACCESS
	LFSR	0, SSR_0_VALUE
	MOVF	TARGET_SSR, W, ACCESS		; ssr value -> [ssr0 + target]
	ADDWF	FSR0L, F, ACCESS
	MOVFF	KK, INDF0
	MOVLW	SSR_BLOCK_LEN
	ADDWF	FSR0L, F, ACCESS
	CLRF	INDF0				; clear flags
	ADDWF	FSR0L, F, ACCESS
	CLRF	INDF0				; clear step
	ADDWF	FSR0L, F, ACCESS
	CLRF	INDF0				; clear speed
	ADDWF	FSR0L, F, ACCESS
	CLRF	INDF0				; clear counter
	RETURN
	
XLATE_SSR_ID:
	;
	; Move YY_DATA -> TARGET_SSR
	; setting flag bits as appropriate
	;   _______________________________________________________
	;  |             |                                         |
	;  |             |           Channel ID (0-47)             | YY_DATA
	;  |______|______|______|______|______|______|______|______|    |
	;  |NOT_MY|INVALI|                                         |    V
	;  | _SSR |D_SSR |           Channel ID (0-23)             | TARGET_SSR
	;  |______|______|______|______|______|______|______|______|
	;
	; If INVALID_SSR=1, the ID cannot possibly be right for the device; disregard all other bits
	; If NOT_MY_SSR=1, this channel exists on the slave chip; Channel ID has been adjusted to that CPU.
	; Else, Channel ID is for this chip and is in range [0,23].
	;
	CLRWDT
	MOVLW	0x3F
	ANDWF	YY_DATA, W, ACCESS
	MOVWF	TARGET_SSR, ACCESS
	MOVLW	.23
	CPFSGT	TARGET_SSR, ACCESS
	RETURN
	IF ROLE_MASTER
	 MOVLW	.24
	 SUBWF	TARGET_SSR, F, ACCESS
	 CPFSLT	TARGET_SSR, ACCESS
	ENDIF
	BSF	TARGET_SSR, INVALID_SSR, ACCESS
	BSF	TARGET_SSR, NOT_MY_SSR, ACCESS
	RETURN

UPDATE_SSR_OUTPUTS:
	CLRWDT
	BANKSEL	SSR_DATA_BANK
	BCF	SSR_STATE, SLICE_UPD, ACCESS
	MOVF	CUR_SLICE, W, ACCESS	; is this the last cycle?
	BZ	UPDATE_MINIMUM_LEVEL
	;
	; For maximum speed in this tight loop, we save time by 
	; unrolling all the tests and output settings into a flat
	; instruction sequence (via assembly-time macro) instead of
	; using a run-time loop or subroutines to calculate the bits
	; and ports for each.  (Like we used to in the previous version.)
	;
X 	SET	0
	WHILE X <= SSR_MAX
	 CPFSEQ	SSR_00_VALUE+#v(X), BANKED	; is this SSR set to our slice value?
	 BRA	$+4
 	 IF X >= SSR_LIGHTS
	  BSF	PLAT_#v(X), BIT_#v(X), ACCESS	; turn on light
 	 ELSE
	  BCF	PLAT_#v(X), BIT_#v(X), ACCESS	; turn on SSR
 	 ENDIF
X	 ++
	ENDW
	DECF	CUR_SLICE, F, ACCESS
	RETURN

UPDATE_MINIMUM_LEVEL:
	;
	; turn off every output that isn't set to be fully on
	; and handle ramping up/down
	;
X 	SET	0
	WHILE X <= SSR_MAX
 	 COMF	SSR_00_VALUE+#v(X), W, BANKED	; is this set to maximum?
	 BZ	$+4
  	 IF X >= SSR_LIGHTS
	  BCF	PLAT_#v(X), BIT_#v(X), ACCESS	; turn off light
 	 ELSE
	  BSF	PLAT_#v(X), BIT_#v(X), ACCESS	; turn off SSR
 	 ENDIF

	 BTFSS	SSR_00_FLAGS+#v(X), FADE_UP, BANKED
	 BRA	TRY_DOWN_#v(X)
	 DECFSZ	SSR_00_COUNTER+#v(X), F, BANKED		; delay to next step
	 BRA	END_FADE_#v(X)
	 MOVFF	SSR_00_SPEED+#v(X), SSR_00_COUNTER+#v(X)
	 MOVF	SSR_00_STEP+#v(X), W, BANKED
	 ADDWF	SSR_00_VALUE+#v(X), F, BANKED
	 BNC 	END_FADE_#v(X)
	 SETF	SSR_00_VALUE+#v(X), BANKED		; reached max value
	 BCF	SSR_00_FLAGS+#v(X), FADE_UP, BANKED	; stop fading
	 BTFSC	SSR_00_FLAGS+#v(X), FADE_CYCLE, BANKED	; cycle back?
	 BSF	SSR_00_FLAGS+#v(X), FADE_DOWN, BANKED	
	 BRA	END_FADE_#v(X)

TRY_DOWN_#v(X):
	 BTFSS	SSR_00_FLAGS+#v(X), FADE_DOWN, BANKED
	 BRA	END_FADE_#v(X)
	 DECFSZ	SSR_00_COUNTER+#v(X), F, BANKED		; delay
	 BRA	END_FADE_#v(X)
	 MOVFF	SSR_00_SPEED+#v(X), SSR_00_COUNTER+#v(X); reset delay
	 MOVF	SSR_00_STEP+#v(X), W, BANKED
	 SUBWF	SSR_00_VALUE+#v(X), F, BANKED
	 BC 	END_FADE_#v(X)
	 CLRF	SSR_00_VALUE+#v(X), BANKED		; reached min value
	 BCF	SSR_00_FLAGS+#v(X), FADE_DOWN, BANKED	; stop fading
	 BTFSC	SSR_00_FLAGS+#v(X), FADE_CYCLE, BANKED	; cycle back?
	 BSF	SSR_00_FLAGS+#v(X), FADE_UP, BANKED

END_FADE_#v(X):
X	 ++
	ENDW
	BCF	SSR_STATE, INCYC, ACCESS	; shut down slice processing until next ZC
	RETURN



; DMX512 RECEIVER CODE
; Based on Microchip Application Note AN1076
;

;
; Wait for start of packet
;
DMX_WAIT_FOR_SYNC:
	BTFSC	PIR1, RCIF, ACCESS
	MOVF	RCREG, W, ACCESS	; throw away received bytes until start of frame
	BTFSS	RCSTA, FERR, ACCESS	; wait until frame error
	BRA	DMX_WAIT_FOR_SYNC
	MOVF	RCREG, W, ACCESS	; clear receive buffer
DMX_WAIT_FOR_START:
	BTFSS	PIR1, RCIF, ACCESS
	BRA	DMX_WAIT_FOR_START	; wait for actual characters to start
	BTFSC	RCSTA, FERR, ACCESS	; and break to end
	BRA	DMX_WAIT_FOR_START
	MOVF	RCREG, W, ACCESS
	ANDLW	0xFF			; test byte just read, should be 0x00
	BNZ	DMX_WAIT_FOR_SYNC	; done here, come back when ready for next packet

	; XXX now loop over bytes, aborting on FERR (indicates packet was short)
	; or when your data have been received.

	

	END
;;;;;;;; EVERYTHING BELOW THIS POINT IS OLD ;;;;;;;;;;;;
#if 0
;-----------------------------------------------------------------------------
; ALL BANKS
;-----------------------------------------------------------------------------
;
;
;                     __7___.__6___.__5___.__4___.__3___.__2___.__1___.__0___ 
; $072 I             |                                                       |
;                    |  General-purpose data counter                         |
;                    |______|______|______|______|______|______|______|______|
; $073 J             |                                                       |
;                    |  General-purpose data counter                         |
;                    |______|______|______|______|______|______|______|______|
; $074 K             |                                                       |
;                    |  General-purpose data counter                         |
;                    |______|______|______|______|______|______|______|______|
; $075 X             |                                                       |
;                    |  General-purpose data register                        |
;                    |______|______|______|______|______|______|______|______|
; $076 Y             |                                                       |
;                    |  General-purpose data register                        |
;                    |______|______|______|______|______|______|______|______|
; $077 PCLATH_TEMP   |                                                       |
;                    |  Temporary storage for PCLATH during ISR              |
;                    |______|______|______|______|______|______|______|______|
; $078               |      |      |      |      |      |      |      |      |
;                    |      |      |      |      |      |      |      |      |
;                    |______|______|______|______|______|______|______|______|
;
;       .                                        .
;       .                                        .
;       .                                        .
;
;                     _______________________________________________________
; $07F               |      |      |      |      |      |      |      |      |
;                    |      |      |      |      |      |      |      |      |
;                    |______|______|______|______|______|______|______|______|
;
;
;-----------------------------------------------------------------------------
; BANK 0
;-----------------------------------------------------------------------------
;                     __7___.__6___.__5___.__4___.__3___.__2___.__1___.__0___ 
; $001 TMR0          |                                                       |
;   (bank 2 too)     |                                                       |
;                    |______|______|______|______|______|______|______|______|
; @@--MASTER--@@
; $005 PORTA         |/////////////|      | _____| _____| _____| _____| _____|
;                    |/////////////| ACT  | SSR08| SSR10| SSR12| SSR14| SSR16|
;                    |/////////////|______|______|______|______|______|______|
; @@--SLAVE--@@
; $005 PORTA         |/////////////|   _  | _____| _____| _____| _____| _____|
;                    |/////////////| T/R  | SSR08| SSR10| SSR12| SSR14| SSR16|
;                    |/////////////|______|______|______|______|______|______|
; @@--END--@@
; $006 PORTB         |/////////////| _____| _____| _____| _____| _____|//////|
;   (bank 2 too)     |/////////////| SSR15| SSR13| SSR11| SSR09| SSR07|//////|
;                    |/////////////|______|______|______|______|______|//////|
; $007 PORTC         |/////////////| _____| _____| _____| _____| _____| _____|
;                    |/////////////| SSR02| SSR00| SSR01| SSR03| SSR19| SSR04|
;                    |/////////////|______|______|______|______|______|______|
; $008 PORTD         | _____| _____| _____| _____| _____| _____| _____| _____|
;                    | SSR17| SSR06| SSR05| SSR18| SSR22| SSR20| SSR21| SSR23|
;                    |______|______|______|______|______|______|______|______|
; $009 PORTE         |//////////////////////////////////|      |      |      |
;                    |//////////////////////////////////| RED  | YEL  | GRN  |
;                    |//////////////////////////////////|______|______|______|
; $00C PIR1          |      |      |      |      |      |      |      |      |
;                    |PSPIF | ADIF | RCIF | TXIF |SSPIF |CCP1IF|TMR2IF|TMR1IF|
;                    |______|______|______|______|______|______|______|______|
; $00D PIR2          |      |      |      |      |      |      |      |      |
;                    |      | CMIF |      | EEIF |BCLIF |      |      |CCP2IF|
;                    |______|______|______|______|______|______|______|______|
; $00E TMR1L         |                                                       |
;                    | Holding register for LSB of TMR1 register             |
;                    |______|______|______|______|______|______|______|______|
; $00F TMR1H         |                                                       |
;                    | Holding register for MSB of TMR1 register             |
;                    |______|______|______|______|______|______|______|______|
; $010 T1CON         |//////|      |             |T1    |______|      |      |
;                    |//////|T1RUN |  T1CKPS1,0  |OSCEN |T1SYNC|TMR1CS|TMR1ON|
;                    |//////|______|______|______|______|______|______|______|
; $011 TMR2          |                                                       |
;                    | Timer2 module register                                |
;                    |______|______|______|______|______|______|______|______|
; $012 T2CON         |//////|                           |      |             |
;                    |//////|       TOUTPS3,2,1,0       |TMR2ON|  T2CKPS1,0  |
;                    |//////|______|______|______|______|______|______|______|
; $018 RCSTA         |      |      |      |      |      |      |      |      |
;                    | SPEN |  RX9 | SREN | CREN |ADDEN | FERR | OERR | RX9D |
;                    |______|______|______|______|______|______|______|______|
; $019 TXREG         |                                                       |
;                    | AUSART transmit data register                         |
;                    |______|______|______|______|______|______|______|______|
; $01A RCREG         |                                                       |
;                    | AUSART receive data register                          |
;                    |______|______|______|______|______|______|______|______|
; $01F ADCON0        |      |      |      |      |      |      |//////|      |
;                    | ADCS1| ADCS0| CHS2 | CHS1 | CHS0 |  GO  |//////| ADON |
;                    |______|______|______|______|______|______|//////|______|
;
; General-purpose data files
;                     _______________________________________________________
; $020 SSR00_VAL     |      |      |      |                                  |
;                    |SSR_ON|SSRDIM|      | Dim value (0=off .. 31=full on)  |
;                    |______|______|______|______|______|______|______|______|
; $021 SSR01_VAL     |      |      |      |                                  |
;                    |SSR_ON|SSRDIM|      | Dim value (0=off .. 31=full on)  |
;                    |______|______|______|______|______|______|______|______|
;
;       .                                        .
;       .                                        .
;       .                                        .
;
;                     _______________________________________________________
; $037 SSR23_VAL     |      |      |      |                                  |
;                    |SSR_ON|SSRDIM|      | Dim value (0=off .. 31=full on)  |
;                    |______|______|______|______|______|______|______|______|
; @@--MASTER--@@
; $038 PORTA_BUF     |/////////////|      | _____| _____| _____| _____| _____|
;                    |/////////////| ACT  | SSR08| SSR10| SSR12| SSR14| SSR16|
;                    |/////////////|______|______|______|______|______|______|
; @@--SLAVE--@@
; $038 PORTA_BUF     |/////////////|   _  | _____| _____| _____| _____| _____|
;                    |/////////////| T/R  | SSR08| SSR10| SSR12| SSR14| SSR16|
;                    |/////////////|______|______|______|______|______|______|
; @@--END--@@
; $039 PORTB_BUF     |/////////////| _____| _____| _____| _____| _____|//////|
;                    |/////////////| SSR15| SSR13| SSR11| SSR09| SSR07|//////|
;                    |/////////////|______|______|______|______|______|//////|
; $03A PORTC_BUF     |/////////////| _____| _____| _____| _____| _____| _____|
;                    |/////////////| SSR02| SSR00| SSR01| SSR03| SSR19| SSR04|
;                    |/////////////|______|______|______|______|______|______|
; $03B PORTD_BUF     | _____| _____| _____| _____| _____| _____| _____| _____|
;                    | SSR17| SSR06| SSR05| SSR18| SSR22| SSR20| SSR21| SSR23|
;                    |______|______|______|______|______|______|______|______|
; $03C PORTE_BUF     |//////////////////////////////////|      |      |      |
;                    |//////////////////////////////////| RED  | YEL  | GRN  |
;                    |//////////////////////////////////|______|______|______|
; $03D PHASE_OFFSET  |                                                       |
;                    |  Number of slices to delay from ZC int to slice 0     |
;                    |______|______|______|______|______|______|______|______|
; $03E SSR_ID        |      |      |      |                                  |
;                    |MY_SSR|ILLSSR|      |  Local device offset from SSR00  |
;                    |______|______|______|______|______|______|______|______|
; $03F FLASH_CT      |                                                       |
;                    |  Value to be flashed on an LED                        |
;                    |______|______|______|______|______|______|______|______|
; $040 DEVICE_ID     |///////////////////////////|                           |
;                    |///////////////////////////| This device's ID number   |
;                    |///////////////////////////|______|______|______|______|
; $041 GRN_TMR       |  If SSR_STATE<GRNEN>                                  |
;                    |  Number of 1/120sec until green LED flips state       |
;                    |______|______|______|______|______|______|______|______|
; $042 YEL_TMR       |  If SSR_STATE<YELEN>                                  |
;                    |  Number of 1/120sec until yellow LED turns off        |
;                    |______|______|______|______|______|______|______|______|
; $043 RED_TMR       |  If SSR_STATE<REDEN>                                  |
;                    |  Number of 1/120sec until red LED turns off           |
;                    |______|______|______|______|______|______|______|______|
; $044 SSR_STATE     |      |      |      |      |      |                    |
;                    |INCYC |PRECYC|REDEN |YELEN |GRNEN |       STATE        |
;                    |______|______|______|______|______|______|______|______|
; $045 CUR_SLICE     |  If SSR_STATE<INCYC>                                  |
;                    |  Current slice (counts down) of AC half-wave          |
;                    |______|______|______|______|______|______|______|______|
; $046 CUR_PRE       |  If SSR_STATE<PRECYC>                                 |
;                    |  Countdown from ZC interrupt to start of AC half-wave |
;                    |______|______|______|______|______|______|______|______|
; $047 RX_BYTE       |                                                       |
;                    |  Received byte from serial network                    |
;                    |______|______|______|______|______|______|______|______|
; $048 SSR_STATE2    |SLICE |DIM_  |DIM_  |      |      |      |      |      |
;                    |_UPD  |START |END   |REDOFF|YELOFF|GRNBLK|SSRUPD| TXQUE|
;                    |______|______|______|______|______|______|______|______|
; $049 DATA_BUF      |                                                       |
;                    |  Holding area for data of command being parsed        |
;                    |______|______|______|______|______|______|______|______|
; $04A ACT_TMR       |  If SSR_STATE3<ACTEN>                                 |
;                    |  Number of 1/120sec until ACT LED turns off           |
;                    |______|______|______|______|______|______|______|______|
; $04B SSR_STATE3    |      |      |      |      |      |      |      |      |
;                    |      |      |      |      |      |ACTEN |ACTOFF|PRIVEN|
;                    |______|______|______|______|______|______|______|______|
; $04C               |      |      |      |      |      |      |      |      |
;                    |      |      |      |      |      |      |      |      |
;                    |______|______|______|______|______|______|______|______|
; $04D               |      |      |      |      |      |      |      |      |
;                    |      |      |      |      |      |      |      |      |
;                    |______|______|______|______|______|______|______|______|
; $04E TXBUF_QUEUE   |                           |                           |
;                    |             5             | Addr of next byte to queue|
;                    |______|______|______|______|______|______|______|______|
; $04F TXBUF_SEND    |                           |                           |
;                    |             5             | Addr of next byte to send |
;                    |______|______|______|______|______|______|______|______|
; $050 TXBUF         |                                                       |
;                    |  Transmitter output buffer (byte 1 of 16)             |
;                    |______|______|______|______|______|______|______|______|
;
;       .                                        .
;       .                                        .
;       .                                        .
;
;                     _______________________________________________________
; $05F               |                                                       |
;                    |  Transmitter output buffer (byte 16 of 16)            |
;                    |______|______|______|______|______|______|______|______|
; $060               |      |      |      |      |      |      |      |      |
;                    |      |      |      |      |      |      |      |      |
;                    |______|______|______|______|______|______|______|______|
;
;       .                                        .
;       .                                        .
;       .                                        .
;
;                     _______________________________________________________
; $06F               |      |      |      |      |      |      |      |      |
;                    |      |      |      |      |      |      |      |      |
;                    |______|______|______|______|______|______|______|______|
;
;-----------------------------------------------------------------------------
; BANK 1
;-----------------------------------------------------------------------------
;
;                     __7___.__6___.__5___.__4___.__3___.__2___.__1___.__0___ 
; $085 TRISA         |                                                       |
;                    | Port A tri-state bitmask (1=input, 0=output)          |
;                    |______|______|______|______|______|______|______|______|
; $086 TRISB         |                                                       |
;  (Bank 3 too)      | Port B tri-state bitmask (1=input, 0=output)          |
;                    |______|______|______|______|______|______|______|______|
; $087 TRISC         |                                                       |
;                    | Port C tri-state bitmask (1=input, 0=output)          |
;                    |______|______|______|______|______|______|______|______|
; $088 TRISD         |                                                       |
;                    | Port D tri-state bitmask (1=input, 0=output)          |
;                    |______|______|______|______|______|______|______|______|
; $089 TRISE         |      |      |      | PSP  |//////|                    |
;                    |  IBF | OBF  | IBOV | MODE |//////| Port E tri-state   |
;                    |______|______|______|______|//////|______|______|______|
; $08C PIE1          |      |      |      |      |      |      |      |      |
;                    |PSPIE | ADIE | RCIE | TXIE |SSPIE |CCP1IE|TMR2IE|TMR1IE|
;                    |______|______|______|______|______|______|______|______|
; $08D PIE2          |      |      |      |      |      |      |      |      |
;                    |      | CMIE |      | EEIE |BCLIE |      |      |CCP2IE|
;                    |______|______|______|______|______|______|______|______|
; $092 PR2           |                                                       |
;                    | Timer 2 period register                               |
;                    |______|______|______|______|______|______|______|______|
; $098 TXSTA         |      |      |      |      |//////|      |      |      |
;                    | CSRC |  TX9 | TXEN | SYNC |//////| BRGH | TRMT | TX9D |
;                    |______|______|______|______|//////|______|______|______|
; $099 SPBRG         |                                                       |
;                    | Baud Rate Generator Value                             |
;                    |______|______|______|______|______|______|______|______|
; $09F ADCON1        |      |      |//////|//////|      |      |      |      |
;                    | ADFM | ADCS2|//////|//////| PCFG3| PCFG2| PCFG1| PCFG0|
;                    |______|______|//////|//////|______|______|______|______|
; $0AD               |      |      |      |      |      |      |      |      |
;                    |      |      |      |      |      |      |      |      |
;                    |______|______|______|______|______|______|______|______|
;
;       .                                        .
;       .                                        .
;       .                                        .
;
;                     _______________________________________________________
; $0EF               |      |      |      |      |      |      |      |      |
;                    |      |      |      |      |      |      |      |      |
;                    |______|______|______|______|______|______|______|______|
;
;-----------------------------------------------------------------------------
; BANK 2
;-----------------------------------------------------------------------------
;
;                     __7___.__6___.__5___.__4___.__3___.__2___.__1___.__0___ 
; $101 TMR0          |                                                       |
;   (bank 0 too)     | Timer0 module register                                |
;                    |______|______|______|______|______|______|______|______|
; $106 PORTB         |/////////////| _____| _____| _____| _____| _____|//////|
;   (bank 0 too)     |/////////////| SSR15| SSR13| SSR11| SSR09| SSR07|//////|
;                    |/////////////|______|______|______|______|______|//////|
; $10C EEDATA        |                                                       |
;                    | EEPROM Data register (LSB)                            |
;                    |______|______|______|______|______|______|______|______|
; $10D EEADR         |                                                       |
;                    | EEPROM Address register (LSB)                         |
;                    |______|______|______|______|______|______|______|______|
; $10E EEDATH        |/////////////|                                         |
;                    |/////////////| EEPROM Data register (MSB)              |
;                    |/////////////|______|______|______|______|______|______|
; $10F EEADRH        |////////////////////|                                  |
;                    |////////////////////| EEPROM Address register (MSB)    |
;                    |////////////////////|______|______|______|______|______|
; $120               |      |      |      |      |      |      |      |      |
;                    |      |      |      |      |      |      |      |      |
;                    |______|______|______|______|______|______|______|______|
;
;       .                                        .
;       .                                        .
;       .                                        .
;
;                     _______________________________________________________
; $16F               |      |      |      |      |      |      |      |      |
;                    |      |      |      |      |      |      |      |      |
;                    |______|______|______|______|______|______|______|______|
;
;-----------------------------------------------------------------------------
; BANK 3
;-----------------------------------------------------------------------------
;
;                     __7___.__6___.__5___.__4___.__3___.__2___.__1___.__0___ 
; $181 OPTION_REG    | ____ |      |      |      |      |                    |
;                    | RBPU |INTEDG| T0CS | T0SE | PSA  |      PS2,1,0       |
;                    |______|______|______|______|______|______|______|______|
; $186 TRISB         |                                                       |
;  (Bank 1 too)      | Port B tri-state bitmask (1=input, 0=output)          |
;                    |______|______|______|______|______|______|______|______|
; $18C EECON1        |      |      |      |      |      |      |      |      |
;                    |EEPGD |      |      |      |WRERR | WREN |  WR  |  RD  |
;                    |______|______|______|______|______|______|______|______|
; $18D EECON2        |                                                       |
;                    | EEPROM Control Register (magic register)              |
;                    |______|______|______|______|______|______|______|______|
; $1A0               |      |      |      |      |      |      |      |      |
;                    |      |      |      |      |      |      |      |      |
;                    |______|______|______|______|______|______|______|______|
;
;       .                                        .
;       .                                        .
;       .                                        .
;
;                     _______________________________________________________
; $1EF               |      |      |      |      |      |      |      |      |
;                    |      |      |      |      |      |      |      |      |
;                    |______|______|______|______|______|______|______|______|
;
;
;
		PROCESSOR 16F877A	; @@P=877@@
		PROCESSOR 16F777 	; @@P=777@@
#include <p16f877a.inc>			; @@P=877@@
#include <p16f777.inc>			;: @@P=777@@
		__CONFIG	_CONFIG1, _CP_ALL & _DEBUG_OFF & _VBOR_2_0 & _BOREN_1 & _MCLR_ON & _PWRTE_ON & _WDT_ON & _HS_OSC ; @@P=777@@
		__CONFIG	_CONFIG2, _BORSEN_1 & _IESO_OFF & _FCMEN_OFF ; @@P=777@@
		__CONFIG	_CP_ALL & _DEBUG_OFF & _WRT_HALF & _CPD_OFF & _LVP_OFF & _BODEN_ON & _PWRTE_OFF & _WDT_ON & _HS_OSC ; @@P=877@@
;
;==============================================================================
; CONSTANTS
;==============================================================================
;
; Flash rates for various LED displays
;
GRN_BLINK_RATE	EQU	.255		; x 1/120s flash rate for green led
ACT_RX_LEN	EQU	.60  		; x 1/120s active led for Rx data
RED_ORERR_LEN	EQU	.120		; x 1/120s red for data overrun
RED_CMDERR_LEN	EQU	.240		; x 1/120s red for cmd error
YEL_CMDERR_LEN	EQU	.240		; x 1/120s yellow for cmd error
SLV_TX_LEN	EQU	.30		; x 1/120s red for Tx to slave
SLV_RX_LEN	EQU	.30		; x 1/120s red for Rx from master
SLV_LED_LEN	EQU	.240		; x 1/120s LED display time
;
;==============================================================================
; COMMAND BYTES
;==============================================================================
;                     ___7______6______5______4______3______2______1______0__
; Command Byte:      |      |                    |                           |
;                    |  1   |    Command code    |   Target device address   |
;                    |______|______|______|______|______|______|______|______|
;
CMD_BIT		EQU	7		; X------- Type (cmd=1; data=0)
CMD_SW_MASK	EQU	b'00000111'	; -----XXX Nybble-swapped Command code mask
CMD_MASK	EQU	b'01110000'	; -XXX---- Command code mask
CMD_ADDR_MASK	EQU	b'00001111'	; ----XXXX Device address mask
;
;                     ___7______6______5______4______3______2______1______0__
; Channel ID:        |      |      |                                         |
;                    |  0   | ON   |               Channel ID                |
;                    |______|______|______|______|______|______|______|______|
;
CMD_CHAN_ON	EQU	6		; -X------ Channel fully on?
CMD_CHAN_MASK	EQU	b'00111111'	; --XXXXXX Channel ID mask
;
;                     ___7______6______5______4______3______2______1______0__
; Dimmer Value:      |      |      |      |                                  |
;                    |  0   |   x  |   x  | Brightness level (0=off, 31=on)  |
;                    |______|______|______|______|______|______|______|______|
;
CMD_DIM_MASK	EQU	b'00011111'	; ---XXXXX Dimmer value mask
;
;                     ___7______6______5______4______3______2______1______0__
; Set Phase Command: |      |      |      |                                  |
;                    |  0   |   0  |  Phase offset level (0-63)              |
;                    |______|______|______|______|______|______|______|______|
;
CMD_AD_PH_MASK	EQU	b'00111111'	; --XXXXXX phase offset value mask
;
;                     ___7______6______5______4______3______2______1______0__
; Set ID Command:    |      |      |      |      |                           |
;                    |  0   |   1  |   0  | ad<0>| New device address (ad)   |
;                    |______|______|______|______|______|______|______|______|
;
CMD_AD_ID_CHK	EQU	4		; ---X---- Must == <0> bit
CMD_AD_ID_MASK	EQU	b'00001111'	; ----XXXX Device ID mask
;
;                     ___7______6______5______4______3______2______1______0__
; Misc. Admin Cmds:  |      |      |      |      |                           |
;                    |  0   |   1  |   1  |   0  |        command ID         |
;                    |______|______|______|______|______|______|______|______|
;
CMD_AD_CMD_MASK	EQU	b'00001111'	; ----XXXX sub-command mask
;
;                     ___7______6______5______4______3______2______1______0__
; Slave Commands:    |      |      |      |      |                           |
;                    |  0   |   1  |   1  |   1  |    command / data bits    |
;                    |______|______|______|______|______|______|______|______|
;
;      Reserved for future commands:                 0      0      x      x
;      Display yellow/red pattern for 2s:            0      1     YEL    RED
;      Display green/yellow/red pattern, HALT:       1     GRN    YEL    RED
;
CMD_AD_SLAVE	EQU	4		; ---X---- slave command?
CMD_AD_S_HALT	EQU	3		; ----X--- halt w/LED pattern
CMD_AD_S_GRN	EQU	2		; -----X-- green LED lit?
CMD_AD_S_YEL	EQU	1		; ------X- yellow LED lit?
CMD_AD_S_RED	EQU	0		; -------X red LED lit?


;
;==============================================================================
; EEPROM
;==============================================================================
;
; These locations in the EEPROM data area are used for persistent storage
; of important data values:
;
;                     ___7______6______5______4______3______2______1______0__
; $00  EE_IDLE       |      |      |      |      |      |      |      |      |
;                    |   1  |   1  |   1  |   1  |   1  |   1  |   1  |   1  |
;                    |______|______|______|______|______|______|______|______|
; $01  EE_DEV_ID     |///////////////////////////|                           |
;                    |///////////////////////////| This device's ID number   |
;                    |///////////////////////////|______|______|______|______|
; $02  EE_PHASE      |                                                       |
;                    |  Phase offset value                                   |
;                    |______|______|______|______|______|______|______|______|
;
;
EE_IDLE		EQU	0x00		; EEPROM address of 0xff byte (per '877 errata) @@P=877@@
EE_DEV_ID	EQU	0x01		; EEPROM address of device ID                   @@P=877@@
EE_PHASE	EQU	0x02		; EEPROM address of phase offset                @@P=877@@
;                                                @@P=877@@
; Default values when chip is flashed:           @@P=877@@
;                                                @@P=877@@
EEPROM_DEFAULTS	ORG	0x2100		;        @@P=877@@
EE_DEF_IDLE	DE	0xFF		;        @@P=877@@
EE_DEF_DEV_ID	DE	0x00		;        @@P=877@@
EE_DEF_PHASE	DE	0x02		;        @@P=877@@
;
;==============================================================================
; REGISTERS
;==============================================================================
;
; Bits and registers used by the firmware
;
;------------------------------------------------------------------------------
; All Banks
;------------------------------------------------------------------------------
;
W_TEMP		EQU	0x070		; Storage for W during ISR
STATUS_TEMP	EQU	0x071		; Storage for STATUS during ISR
I		EQU	0x072		; General-purpose data counter
J		EQU	0x073		; General-purpose data counter
K		EQU	0x074		; General-purpose data counter
X		EQU	0x075		; General-purpose data register
Y		EQU	0x076		; General-purpose data register
PCLATH_TEMP	EQU	0x077		; Storage for PCLATH during ISR
;
;------------------------------------------------------------------------------
; Bank 0
;------------------------------------------------------------------------------
;
; Output Ports mapped to SSR outputs and LEDs.  These have a physical port
; register (e.g., PORTA), writing to which drives the outputs from the chip.
; A buffer register (e.g., PORTA_BUF) mirrors the layout of PORTA, and is 
; where our routines update the bits before they're pushed out to the actual
; I/O port.
;
; We define the mappings between logical signals like /SSR08 and the 
; registers and bit positions in memory here.
;
;                     ___7______6______5______4______3______2______1______0__
; @@--MASTER--@@
; $005 PORTA         |/////////////|      | _____| _____| _____| _____| _____|
; $038 PORTA_BUF     |/////////////| ACT  | SSR08| SSR10| SSR12| SSR14| SSR16|
; @@--SLAVE--@@
; $005 PORTA         |/////////////|   _  | _____| _____| _____| _____| _____|
; $038 PORTA_BUF     |/////////////| T/R  | SSR08| SSR10| SSR12| SSR14| SSR16|
; @@--END--@@
;                    |/////////////|______|______|______|______|______|______|
;
PORTA_BUF	EQU	0x038

;@@--MASTER--@@
PORT_ACT	EQU	PORTA
PBUF_ACT	EQU	PORTA_BUF
BIT_ACT		EQU	5
;@@--SLAVE--@@
PORT_TRSEL	EQU	PORTA
PBUF_TRSEL	EQU	PORTA_BUF
BIT_TRSEL	EQU	5
;@@--END--@@
PORT_08		EQU	PORTA
PORT_10		EQU	PORTA
PORT_12		EQU	PORTA
PORT_14		EQU	PORTA
PORT_16		EQU	PORTA

PBUF_08		EQU	PORTA_BUF
PBUF_10		EQU	PORTA_BUF
PBUF_12		EQU	PORTA_BUF
PBUF_14		EQU	PORTA_BUF
PBUF_16		EQU	PORTA_BUF

BIT_08		EQU	4
BIT_10		EQU	3
BIT_12		EQU	2
BIT_14		EQU	1
BIT_16		EQU	0
;
;                     ___7______6______5______4______3______2______1______0__
; $006 PORTB         |/////////////| _____| _____| _____| _____| _____|//////|
; $039 PORTB_BUF     |/////////////| SSR15| SSR13| SSR11| SSR09| SSR07|//////|
;                    |/////////////|______|______|______|______|______|//////|
;
PORTB_BUF	EQU	0x039

PORT_15		EQU	PORTB
PORT_13		EQU	PORTB
PORT_11		EQU	PORTB
PORT_09		EQU	PORTB
PORT_07		EQU	PORTB

PBUF_15		EQU	PORTB_BUF
PBUF_13		EQU	PORTB_BUF
PBUF_11		EQU	PORTB_BUF
PBUF_09		EQU	PORTB_BUF
PBUF_07		EQU	PORTB_BUF

BIT_15		EQU	5
BIT_13		EQU	4
BIT_11		EQU	3
BIT_09		EQU	2
BIT_07		EQU	1
;
;                     ___7______6______5______4______3______2______1______0__
; $007 PORTC         |/////////////| _____| _____| _____| _____| _____| _____|
; $03A PORTC_BUF     |/////////////| SSR02| SSR00| SSR01| SSR03| SSR19| SSR04|
;                    |/////////////|______|______|______|______|______|______|
;
PORTC_BUF	EQU	0x03A

PORT_02		EQU	PORTC
PORT_00		EQU	PORTC
PORT_01		EQU	PORTC
PORT_03		EQU	PORTC
PORT_19		EQU	PORTC
PORT_04		EQU	PORTC

PBUF_02		EQU	PORTC_BUF
PBUF_00		EQU	PORTC_BUF
PBUF_01		EQU	PORTC_BUF
PBUF_03		EQU	PORTC_BUF
PBUF_19		EQU	PORTC_BUF
PBUF_04		EQU	PORTC_BUF

BIT_02		EQU	5
BIT_00		EQU	4
BIT_01		EQU	3
BIT_03		EQU	2
BIT_19		EQU	1
BIT_04		EQU	0
;
;                     ___7______6______5______4______3______2______1______0__
; $008 PORTD         | _____| _____| _____| _____| _____| _____| _____| _____|
; $03B PORTD_BUF     | SSR17| SSR06| SSR05| SSR18| SSR22| SSR20| SSR21| SSR23|
;                    |______|______|______|______|______|______|______|______|
;
PORTD_BUF	EQU	0x03B

PORT_17		EQU	PORTD
PORT_06		EQU	PORTD
PORT_05		EQU	PORTD
PORT_18		EQU	PORTD
PORT_22		EQU	PORTD
PORT_20		EQU	PORTD
PORT_21		EQU	PORTD
PORT_23		EQU	PORTD

PBUF_17		EQU	PORTD_BUF
PBUF_06		EQU	PORTD_BUF
PBUF_05		EQU	PORTD_BUF
PBUF_18		EQU	PORTD_BUF
PBUF_22		EQU	PORTD_BUF
PBUF_20		EQU	PORTD_BUF
PBUF_21		EQU	PORTD_BUF
PBUF_23		EQU	PORTD_BUF

BIT_17		EQU	7
BIT_06		EQU	6
BIT_05		EQU	5
BIT_18		EQU	4
BIT_22		EQU	3
BIT_20		EQU	2
BIT_21		EQU	1
BIT_23		EQU	0
;
;                     ___7______6______5______4______3______2______1______0__
; $009 PORTE         |//////////////////////////////////|      |      |      |
; $03C PORTE_BUF     |//////////////////////////////////| RED  | YEL  | GRN  |
;                    |//////////////////////////////////|______|______|______|
;
PORTE_BUF	EQU	0x03C

PORT_RED	EQU	PORTE
PORT_YEL	EQU	PORTE
PORT_GRN	EQU	PORTE

PBUF_RED	EQU	PORTE_BUF
PBUF_YEL	EQU	PORTE_BUF
PBUF_GRN	EQU	PORTE_BUF

BIT_RED		EQU	2
BIT_YEL		EQU	1
BIT_GRN		EQU	0

PORT_LEDS	EQU	PORTE
MASK_RED_YEL	EQU	0x06	; RED, YEL on; GRN off
MASK_ALL_LEDS	EQU	0x07	; RED, YEL, GRN on
MASK_NO_LEDS	EQU	0x00	; all off
;
; SSR Value buffers.
; These hold the current dimmer values for the SSR circuit outputs.
; The bits are interpreted as:
;
;  SSR_ON SSRDIM VALUE
;     0      0     x     Channel completely "off"
;     0      1     n     Channel dimmed to level n
;     1      x     x     Channel completely "on" (no dimmer control)
;
;
;                     ___7______6______5______4______3______2______1______0__
; $020 SSR00_VAL     |      |      |//////|                                  |
;                    |SSR_ON|SSRDIM|//////| Dim value (0=off .. 31=full on)  |
;                    |______|______|//////|______|______|______|______|______|
; $021 SSR01_VAL     |      |      |//////|                                  |
;                    |SSR_ON|SSRDIM|//////| Dim value (0=off .. 31=full on)  |
;                    |______|______|//////|______|______|______|______|______|
;
;       .                                        .
;       .                                        .
;       .                                        .
;
;                     _______________________________________________________
; $037 SSR23_VAL     |      |      |//////|                                  |
;                    |SSR_ON|SSRDIM|//////| Dim value (0=off .. 31=full on)  |
;                    |______|______|//////|______|______|______|______|______|
;
SSR_ON		EQU	7		; X------- SSR ON (no dim)
SSRDIM		EQU	6		; -X------ SSR dim
SSRVAL_RESV	EQU	5		; --X----- Reserved bit
SSRVAL_MASK	EQU	b'00011111'	; ---XXXXX SSR dimmer value

SSR00_VAL	EQU	0x020
SSR01_VAL	EQU	0x021
SSR02_VAL	EQU	0x022
SSR03_VAL	EQU	0x023
SSR04_VAL	EQU	0x024
SSR05_VAL	EQU	0x025
SSR06_VAL	EQU	0x026
SSR07_VAL	EQU	0x027
SSR08_VAL	EQU	0x028
SSR09_VAL	EQU	0x029
SSR10_VAL	EQU	0x02A
SSR11_VAL	EQU	0x02B
SSR12_VAL	EQU	0x02C
SSR13_VAL	EQU	0x02D
SSR14_VAL	EQU	0x02E
SSR15_VAL	EQU	0x02F
SSR16_VAL	EQU	0x030
SSR17_VAL	EQU	0x031
SSR18_VAL	EQU	0x032
SSR19_VAL	EQU	0x033
SSR20_VAL	EQU	0x034
SSR21_VAL	EQU	0x035
SSR22_VAL	EQU	0x036
SSR23_VAL	EQU	0x037
;
; The master CPU reads this value from EEPROM when booting up, and sends
; it to the slave CPU.  From there, they both use this RAM location to
; hold the value during runtime.
;
;                     ___7______6______5______4______3______2______1______0__
; $03D PHASE_OFFSET  |                                                       |
;                    |  Number of slices to delay from ZC int to slice 0     |
;                    |______|______|______|______|______|______|______|______|
;
PHASE_OFFSET	EQU	0x03D
;
; The SSR handling routines fill in this register when receiving a command
; targeted to a single channel.
;
;                     ___7______6______5______4______3______2______1______0__
; $03E SSR_ID        |      |      |//////|                                  |
;                    |MY_SSR|ILLSSR|//////|  Local device offset from SSR00  |
;                    |______|______|//////|______|______|______|______|______|
;
SSR_ID		EQU	0x03E

MY_SSR		EQU	7		; X------- Is this SSR for this CPU?
ILLSSR      	EQU	6		; -X------ Channel ID is illegal
SSR_ID_RESV 	EQU	5		; --X----- Reserved bit
SSR_DEV_MASK	EQU	b'00011111'	; ---XXXXX Mask for local SSR ID
;
; This is used primarily for the POST LED effects which flash a value
; on the LEDs.  This is the parameter to the function which handles that.
;
;                     ___7______6______5______4______3______2______1______0__
; $03F FLASH_CT      |                                                       |
;                    |  Value to be flashed on an LED                        |
;                    |______|______|______|______|______|______|______|______|
;
FLASH_CT	EQU	0x03F
;
;                     ___7______6______5______4______3______2______1______0__
; $040 DEVICE_ID     |///////////////////////////|                           |
;                    |///////////////////////////| This device's ID number   |
;                    |///////////////////////////|______|______|______|______|
;
; We copy the device ID from EEPROM to this location, where we can compare
; it more easily during runtime.  Note that it's also aligned with the device
; ID field in command bytes.
;
;@@--MASTER--@@
DEVICE_ID	EQU	0x040

DEVICE_ID_MASK	EQU	b'00001111'	; ----XXXX Mask for device ID value
;@@--END--@@
;
; LED Timers
;
; These hold the time remaining for a lit LED until it is scheduled to be
; turned off.  The units are 1/120 sec (i.e., number of ZC interrupts).
;
GRN_TMR		EQU	0x041		; Green LED time until FLIPS STATE
YEL_TMR		EQU	0x042		; Yellow LED time until turns off
RED_TMR		EQU	0x043		; Red LED time until turns off
;@@--MASTER--@@
ACT_TMR		EQU	0x04A		; Active LED time until turns off
;@@--END--@@
;
; State machine value and some misc. operating flags.
;
;                     ___7______6______5______4______3______2______1______0__
; $044 SSR_STATE     |      |      |      |      |      |                    |
;                    |INCYC |PRECYC|REDEN |YELEN |GRNEN |       STATE        |
;                    |______|______|______|______|______|______|______|______|
;
SSR_STATE	EQU	0x044

INCYC		EQU	7		; X------- In an active ZC cycle?
PRECYC		EQU	6		; -X------ Between int and start of cycle?
REDEN		EQU	5		; --X----- Red LED off timer active
YELEN		EQU	4		; ---X---- Yellow LED off timer active
GRNEN		EQU	3		; ----X--- Green LED flip timer active
STATE2		EQU	2		; -----X-- Bit 2 of state value
STATE1		EQU	1		; ------X- Bit 1 of state value
STATE0		EQU	0		; -------X Bit 0 of state value
SSR_STATE_MASK	EQU	b'00000111'	; -----XXX Mask for state value
;
; Cycle/slice timers
;
CUR_SLICE	EQU	0x045		; current slice number (counts down)
CUR_PRE		EQU	0x046		; pre-slice number (counts down)
;
; Communications buffers
;
RX_BYTE		EQU	0x047		; byte last received from serial port
DATA_BUF	EQU	0x049		; holding area for command data
;
; More operating flags
;
;                     ___7______6______5______4______3______2______1______0__
; $048 SSR_STATE2    |SLICE |DIM_  |DIM_  |      |      |      |      |      |
;                    |_UPD  |START |END   |REDOFF|YELOFF|GRNBLK|SSRUPD| TXQUE|
;                    |______|______|______|______|______|______|______|______|
; $04B SSR_STATE3    |//////////////////////////////////|      |      |      |
;                    |//////////////////////////////////|ACTEN |ACTOFF|PRIVEN|
;                    |//////////////////////////////////|______|______|______|
;
SSR_STATE2	EQU	0x048

SLICE_UPD	EQU	7		; X------- Ready to update current slice?
DIM_START	EQU	6		; -X------ First dimmer cycle?
DIM_END		EQU	5		; --X----- Last dimmer cycle?
REDOFF		EQU	4		; ---X---- Red LED timer expired, turn off
YELOFF		EQU	3		; ----X--- Yellow LED timer expired, turn off
GRNBLK		EQU	2		; -----X-- Green LED timer expired, blink it
SSRUPD		EQU	1		; ------X- Queued SSR update operation
TXQUE		EQU	0		; -------X Something in transmit queue

SSR_STATE3	EQU	0x04B

SSR_STATE3_RES7	EQU	7		; X------- Reserved bit
SSR_STATE3_RES6	EQU	6		; -X------ Reserved bit
SSR_STATE3_RES5	EQU	5		; --X----- Reserved bit
SSR_STATE3_RES4	EQU	4		; ---X---- Reserved bit
SSR_STATE3_RES3	EQU	3		; ----X--- Reserved bit
ACTEN		EQU	2		; -----X-- Active LED timer active
ACTOFF		EQU	1		; ------X- Active LED timer expired, turn off
PRIVEN		EQU	0		; -------X Privileged commands enabled
;
; Serial Transmitter Ring Buffer
;
; We maintain a buffer of 16 output bytes waiting to be sent out of the
; serial port.  We empty this buffer in an interrupt-driven routine so
; the processing of incoming data isn't stalled while waiting for the
; UART to be idle.  XXX interrupt-driven??? not directly. XXX
;
; This needs to be arranged so that the table is a power of two in length
; and aligned in memory so that it starts on an even boundary of its 
; length.  In other words, we can take a pointer P into the table,
; and ((P & TXBUF_MASK) | TXBUF) will yield a valid pointer within
; that space, with proper wraparound in either direction.
;
;                     ___7______6______5______4______3______2______1______0__
; $04E TXBUF_QUEUE   |                           |                           |
;                    |             5             | Addr of next byte to queue|
;                    |______|______|______|______|______|______|______|______|
; $04F TXBUF_SEND    |                           |                           |
;                    |             5             | Addr of next byte to send |
;                    |______|______|______|______|______|______|______|______|
; $050 TXBUF         |                                                       |
;                    |  Transmitter output buffer (byte 1 of 16)             |
;                    |______|______|______|______|______|______|______|______|
;
;       .                                        .
;       .                                        .
;       .                                        .
;
;                     _______________________________________________________
; $05F               |                                                       |
;                    |  Transmitter output buffer (byte 16 of 16)            |
;                    |______|______|______|______|______|______|______|______|
;
TXBUF_QUEUE	EQU	0x04E
TXBUF_SEND	EQU	0x04F
TXBUF		EQU	0x050
TXBUF_MASK	EQU	b'00001111'	; mask off table index
;
;-----------------------------------------------------------------------------
; Banks 1-3
;-----------------------------------------------------------------------------
;
; Nothing defined in these banks.
;

;=============================================================================
; VECTORED ENTRY POINTS
;=============================================================================
RESTART_VECTOR	ORG	0x0000
		GOTO	INIT

INT_VECTOR	ORG	0x0004
		GOTO	ISR

;==============================================================================
; JUMP TABLES
;
; We collect these here so they are all within the $00xx range.  Otherwise
; it's a constant battle to keep the PCLATH register right as the code changes
; and moves these tables around across page boundaries.
;==============================================================================
;
; State 0 Command Dispatch Table
;  Given command in RX_BYTE<6:4>, branch to command #0-#7.
;  Errors (undefined commands) branch to CMD_ERROR.
;
STATE_0_CMD_TBL	CLRWDT
		CLRF	PCLATH			
		SWAPF	RX_BYTE, W		
		ANDLW	CMD_SW_MASK
		ADDWF	PCL, F			
		GOTO	CMD_0			
		GOTO	CMD_1			
		GOTO	CMD_2			
		GOTO	CMD_ERROR
		GOTO	CMD_ERROR
		GOTO	CMD_ERROR
		GOTO	CMD_ERROR
		GOTO	CMD_7
		GOTO	FAULT     		; shouldn't happen, but still.
;
; Received data byte dispatch function.  
; When receiving a data byte, what happens next
; depends on the state of the parser's state machine.
; This jump table branches to the appropriate handler
; for each state.
;
; In the case of state 0, we just return to the
; original caller, ignoring the byte.
;
DATA_BYTE_TBL	CLRWDT				; We received a data byte
		CLRF	PCLATH			; We're in $00xx address range
		MOVF	SSR_STATE, W		; decode state bits
		ANDLW	SSR_STATE_MASK
		ADDWF	PCL, F
		RETURN				; [0] ignore data
		GOTO	DATA_STATE_1		; [1] handler
		GOTO	DATA_STATE_2		; [2] handler
		GOTO	DATA_STATE_3		; [3] handler
		GOTO	DATA_STATE_4		; [4] handler
		GOTO	FAULT_1			; [5] illegal state
		GOTO	FAULT_1			; [6] illegal state
		GOTO	FAULT_1			; [7] illegal state
		GOTO	FAULT     		; shouldn't happen, but still.
;
; Administrative Command Dispatch Table
; Dispatch the processing of admin commands, based on value
; of RX_BYTE.
;
CMD_ADMIN_TABLE	CLRWDT
		CLRF	PCLATH			;
		MOVF	RX_BYTE, W		; Get and store command
		ANDLW	b'00001111'		; sub-command mask
		ADDWF	PCL, F			
		GOTO	CMD_AD_SHUTDOWN		; 0=shutdown cpu
		GOTO	CMD_AD_DIS_PRIV		; 1=disable privs
		GOTO	CMD_ERROR		; 2=reserved 
		GOTO	CMD_ERROR		; 3=reserved 
		GOTO	CMD_ERROR		; 4=reserved 
		GOTO	CMD_ERROR		; 5=reserved 
		GOTO	CMD_ERROR		; 6=reserved 
		GOTO	CMD_ERROR		; 7=reserved 
		GOTO	CMD_ERROR		; 8=reserved 
		GOTO	CMD_ERROR		; 9=reserved 
		GOTO	CMD_ERROR		; A=reserved 
		GOTO	CMD_ERROR		; B=reserved 
		GOTO	CMD_ERROR		; C=reserved 
		GOTO	CMD_ERROR		; D=reserved 
		GOTO	CMD_ERROR		; E=reserved 
		GOTO	CMD_ERROR		; F=reserved 
		GOTO	FAULT     		; shouldn't happen, but still.
;		
;------------------------------------------------------------------------------
; SSR_Y_TO_PBUF
;   return specified SSR's port buffer's address
;
; Input:    Y=SSR channel (0-23)
; Output:   W=address of SSR's port buffer
; Context:  Any Bank
;------------------------------------------------------------------------------
;
; *** THIS CODE MUST BE ON ONE 256-BYTE PAGE ***
SSR_Y_TO_PBUF	CLRWDT
		CLRF	PCLATH		; Our jump table's code page
		MOVF	Y, W
		ANDLW	b'00011111'	; limit to 32 
		ADDWF	PCL, F		; jump to SSR # in table
		RETLW	PBUF_00
		RETLW	PBUF_01
		RETLW	PBUF_02
		RETLW	PBUF_03
		RETLW	PBUF_04
		RETLW	PBUF_05
		RETLW	PBUF_06
		RETLW	PBUF_07
		RETLW	PBUF_08
		RETLW	PBUF_09
		RETLW	PBUF_10
		RETLW	PBUF_11
		RETLW	PBUF_12
		RETLW	PBUF_13
		RETLW	PBUF_14
		RETLW	PBUF_15
		RETLW	PBUF_16
		RETLW	PBUF_17
		RETLW	PBUF_18
		RETLW	PBUF_19
		RETLW	PBUF_20
		RETLW	PBUF_21
		RETLW	PBUF_22
		RETLW	PBUF_23
		GOTO	FAULT		; FAULT 24
		GOTO	FAULT		; FAULT 25
		GOTO	FAULT		; FAULT 26
		GOTO	FAULT		; FAULT 27
		GOTO	FAULT		; FAULT 28
		GOTO	FAULT		; FAULT 29
		GOTO	FAULT		; FAULT 30
		GOTO	FAULT		; FAULT 31
		GOTO	FAULT		; FAULT 32 just to be paranoid
;		
;------------------------------------------------------------------------------
; SSR_Y_SET_MASK
;   return bitmask for SSR output in its I/O port
;   If you OR the bit with the port's value the channel is turned on.
;   If you want to get the bitmask for turning it off, see SSR_Y_CLR_MASK.
;
; Input:    Y=SSR channel (0-23)
; Output:   W=bitmask for SETTING the bit (IOR with current value)
; Context:  Any Bank
;------------------------------------------------------------------------------
;
; *** THIS CODE MUST BE ON ONE 256-BYTE PAGE ***
;
SSR_Y_SET_MASK	CLRWDT
		CLRF	PCLATH
		MOVF	Y, W
		ANDLW	b'00011111'	; limit to 32 
		ADDWF	PCL, F		; jump to SSR # in table
		RETLW	1 << BIT_00
		RETLW	1 << BIT_01
		RETLW	1 << BIT_02
		RETLW	1 << BIT_03
		RETLW	1 << BIT_04
		RETLW	1 << BIT_05
		RETLW	1 << BIT_06
		RETLW	1 << BIT_07
		RETLW	1 << BIT_08
		RETLW	1 << BIT_09
		RETLW	1 << BIT_10
		RETLW	1 << BIT_11
		RETLW	1 << BIT_12
		RETLW	1 << BIT_13
		RETLW	1 << BIT_14
		RETLW	1 << BIT_15
		RETLW	1 << BIT_16
		RETLW	1 << BIT_17
		RETLW	1 << BIT_18
		RETLW	1 << BIT_19
		RETLW	1 << BIT_20
		RETLW	1 << BIT_21
		RETLW	1 << BIT_22
		RETLW	1 << BIT_23
		GOTO	FAULT		; fault 24
		GOTO	FAULT		; fault 25
		GOTO	FAULT		; fault 26
		GOTO	FAULT		; fault 27
		GOTO	FAULT		; fault 28
		GOTO	FAULT		; fault 29
		GOTO	FAULT		; fault 30
		GOTO	FAULT		; fault 31
		GOTO	FAULT		; fault 32 just to be paranoid
;
;==============================================================================
; INTERRUPT SERVICE ROUTINE (ISR)
;
; Responsible for handling the timing and synchronization for the unit.
; 
; Context: Any Bank (restores original bank when finished)
; Affects: Various flag bits
; Also:    Restores status flags, PC and W when done
;
;==============================================================================
;
ISR		MOVWF	W_TEMP		; Save registers during interrupt
		SWAPF	STATUS, W	; This moves status w/o disturbing it
		MOVWF	STATUS_TEMP
		MOVF	PCLATH, W
		MOVWF	PCLATH_TEMP
		CLRF	PCLATH		; Force code page 0
		BANKSEL	INTCON		; (Bank 0)
		CLRWDT
;
; Poll interrupts to see who's asking for attention.
;
;------------------------------------------------------------------------------
; INT0 -- 1/120sec timer synchronized with AC half-wave zero-crossing point.
;
INT_INT0	BTFSS	INTCON, INTF		; INT0 line interrupt pending?
		GOTO	INT_TMR2		; no: try next vector
		BCF	INTCON, INTF		; yes: acknowledge interrupt

INT_YEL		BTFSC	SSR_STATE, YELEN	; Yellow timer on?
		DECFSZ	YEL_TMR, F		; yes: count it down one step
		GOTO	INT_RED
		BSF	SSR_STATE2, YELOFF	; done? queue LED turn off event
		BCF	SSR_STATE, YELEN	; ...and stop the timer

INT_RED		BTFSC	SSR_STATE, REDEN	; Red timer on?
		DECFSZ	RED_TMR, F		; yes: count it down one step
		GOTO	INT_GRN
		BSF	SSR_STATE2, REDOFF	; done? queue LED turn off event
		BCF	SSR_STATE, REDEN	; ...and stop the timer

INT_GRN		BTFSC	SSR_STATE, GRNEN	; Green timer on?
		DECFSZ	GRN_TMR, F		; yes: count it down one step
		GOTO	INT_ACT
		BSF	SSR_STATE2, GRNBLK	; done? queue LED flip event
		MOVLW	GRN_BLINK_RATE		; ...and reset timer for next blink
		MOVWF	GRN_TMR

INT_ACT		CLRWDT
;@@--MASTER--@@
		BTFSC	SSR_STATE3, ACTEN	; Active timer on?
		DECFSZ	ACT_TMR, F		; yes: count it down one step
		GOTO	INT_ZC
		BSF	SSR_STATE3, ACTOFF	; done? queue LED turn off event
		BCF	SSR_STATE3, ACTEN	; ...and stop the timer
;@@--END--@@
;
; Handle the cycle timers.
; We just hit a ZC interrupt, so let's start the pre-cycle now.
;
INT_ZC		BSF	SSR_STATE, PRECYC
		MOVF	PHASE_OFFSET, W
		MOVWF	CUR_PRE
;
;------------------------------------------------------------------------------
; TMR2 -- Timer #2 interrupt
; This is a free-running slice timer (about 38 per INT0)
;
INT_TMR2	CLRWDT
		BTFSS	PIR1, TMR2IF	; Timer 2 interrupt pending?
		GOTO	INT_END  	; no: try next vector
		BCF	PIR1, TMR2IF	; yes: acknowledge interrupt
;
; If in pre-cycle, count down to next real zero crossing event point
;
INT_PRECYC	BTFSC	SSR_STATE, PRECYC
		DECFSZ	CUR_PRE, F		
		GOTO	INT_NEXTSLICE		
;
; end of pre-cycle, start first real one
;
		BCF	SSR_STATE, PRECYC
		BSF	SSR_STATE, INCYC
		BSF	SSR_STATE2, DIM_START
		MOVLW	.32
		MOVWF	CUR_SLICE
;
; start of any active slice
;
INT_NEXTSLICE	BTFSC	SSR_STATE, INCYC
		DECFSZ	CUR_SLICE, F
		GOTO	INT_ENDSLICE
;
; last slice (#0)
;
		BSF	SSR_STATE2, DIM_END
		BCF	SSR_STATE, INCYC
;
; slice timing ends
;
INT_ENDSLICE	BSF	SSR_STATE2, SLICE_UPD
;
; end of ISR
;
INT_END		CLRWDT			; (Any Bank)
		MOVF	PCLATH_TEMP, W
		MOVWF	PCLATH
		SWAPF	STATUS_TEMP, W
		MOVWF	STATUS		; (Previous Bank Restored)
		SWAPF	W_TEMP, F
		SWAPF	W_TEMP, W
	
		RETFIE

;=============================================================================
; INIT: device initialization routines
;=============================================================================
INIT		CLRWDT
		BCF	INTCON, GIE	; disable all interrupts
		CLRF	PCLATH		; Program page 0
		BANKSEL	EECON1		; (Bank 3)               @@P=877@@
		BCF	EECON1, WREN	; disable EEPROM writes  @@P=877@@
;
; Initialize I/O ports by pre-filling with initial bits, then enabling
; outputs on pins which are supposed to be outputs
;
SETUP_PORTS	CLRWDT
		BANKSEL	PORTA		; (Bank 0)
		CLRF	PORTA		; ACT off, RCV mode, pins off
		CLRF	PORTB		; (Note that this would turn on
		CLRF	PORTC		; the SSRs if the ports were 
		CLRF	PORTD		; enabled yet).
		CLRF	PORTE		; LEDs off
		CALL	ALL_SSRS_OFF	; turn OFF SSR ports.
		CALL	UPDATE_PORTS	; push out bits to I/O ports.

		BANKSEL	TRISA			; (Bank 1)
		MOVLW	b'11000000'		; XXOOOOOO
		MOVWF	TRISA                   
;		MOVLW	b'10000000'
		MOVWF	TRISC			; Rx/Tx tri-stated here
		MOVLW	b'11000001'		; XXOOOOOI
		MOVWF	TRISB
		MOVLW	b'00000000'		; OOOOOOOO
		MOVWF	TRISD
		MOVWF	TRISE			; (also sets PORTD mode)
		MOVLW	b'00000110'		; All I/O pins DIGITAL	@@P=877@@
		MOVLW	b'00001111'		; All I/O pins DIGITAL  @@P=777@@
		MOVWF	ADCON1
;
; Flash LEDs for reset
;
		CLRWDT
		BANKSEL	PORT_LEDS		; (Bank 0)
		MOVLW	.5			; flash 5 times
		MOVWF	X
RESET_LEDS_NEXT	MOVLW	MASK_ALL_LEDS
		MOVWF	PORT_LEDS
		CALL	DELAY_FFLASH
		MOVLW	MASK_NO_LEDS
		MOVWF	PORT_LEDS
		CALL	DELAY_FFLASH
		DECFSZ	X, F
		GOTO	RESET_LEDS_NEXT
;
; Light green LED on the master and red LED on the slave
;
;@@--MASTER--@@
		BSF	PORT_GRN, BIT_GRN
;@@--SLAVE--@@
		BSF	PORT_RED, BIT_RED	; @@P=877@@
		NOP                  		; @@P=877@@
		MOVLW	MASK_RED_YEL		; @@P=777@@
		MOVWF	PORT_LEDS		; @@P=777@@
;@@--END--@@
		CLRF	ADCON0			; A/D Converter off


; INIT: set up EEPROM idle value
; The 16F877A Rev. B2 has a defect where the power-down current exceeds the
; published tolerances in some (unlikely) circumstances if the CPU enters sleep
; mode while the EEADR register points to an EEPROM location holding a value
; other than 0xFF.
;
; So we make sure that the EEPROM address register is always pointing to a 0xFF value
; when it's not busy doing anything else.
;
; But first, we'll make sure that a reserved EEPROM location holds a 0xFF value
; to start with. We do this every time since we don't /know/ the device was ever 
; initialized before, although most likely this value will already be right 
; (It /is/ EEPROM, after all!)
;
;
SETUP_EEPROM	CLRWDT			
		BANKSEL	EEADR		; @@P=877@@ (Bank 2)
		CLRF	EEDATH		; @@P=877@@ Clear high bits of data...
		CLRF	EEADRH		; @@P=877@@ ...and address
		MOVLW	EE_IDLE 	; @@P=877@@ Set target EEPROM location
		MOVWF	EEADR		; @@P=877@@
		MOVLW	0xFF		; @@P=877@@ Set value to be written
		MOVWF	EEDATA		; @@P=877@@
		BANKSEL	EECON1		; @@P=877@@ (Bank 3)
		BCF	EECON1, EEPGD	; @@P=877@@ Write to data memory, not flash RAM
		BSF	EECON1, WREN	; @@P=877@@ Enable EEPROM writing
		BCF	INTCON, GIE	; @@P=877@@ Disable interrupts
		MOVLW	0x55		; @@P=877@@ --Begin magic EEPROM write sequence--
		MOVWF	EECON2		; @@P=877@@
		MOVLW	0xAA		; @@P=877@@
		MOVWF	EECON2		; @@P=877@@ --End magic EEPROM write sequence--
		BSF	EECON1, WR	; @@P=877@@ Initiate write operation
		BCF	EECON1, WREN	; @@P=877@@ Disable EEPROM writing
		CLRWDT			; @@P=877@@
		BTFSC	EECON1, WR	; @@P=877@@ Wait for write to complete
		GOTO	$-1		; @@P=877@@
		BANKSEL	PIR2		; @@P=877@@ (Bank 0)
		BCF	PIR2, EEIF	; @@P=877@@ Clear "EEPROM written" interrupt flag
;
; INIT: read our device ID from EEPROM
;
; @@--MASTER--@@
SETUP_DEV_ID	CLRWDT
		BANKSEL	EEADR		; (Bank 2)
		CLRF	EEDATH		; @@P=877@@ Clear high bits of data...
		CLRF	EEADRH		; @@P=877@@ ...and address
		MOVLW	EE_DEV_ID	; Set target EEPROM location
		MOVWF	EEADR
		BANKSEL	EECON1		; (Bank 3)
		BCF	EECON1, EEPGD	; Select EEPROM data memory
		BSF	EECON1, RD	; Start read operation
		BANKSEL	EEDATA		; (Bank 2)
		MOVF	EEDATA, W	; W = device ID value
		BANKSEL	DEVICE_ID	; (Bank 0)
		MOVWF	DEVICE_ID
;
; INIT: read current phase offset from EEPROM
;
SETUP_PHASE	CLRWDT
		BANKSEL	EEADR		; (Bank 2)
		MOVLW	EE_PHASE	; Set target EEPROM location
		MOVWF	EEADR
		BANKSEL	EECON1		; (Bank 3)
		BCF	EECON1, EEPGD	; Select EEPROM data memory
		BSF	EECON1, RD	; Start read operation
		BANKSEL	EEDATA		; (Bank 2)
		MOVF	EEDATA, W	; W = device ID value
		BANKSEL	PHASE_OFFSET	; (Bank 0)
		MOVWF	PHASE_OFFSET
; @@--END--@@
;
; INIT: move EEPROM address to idle block
;
SETUP_EE_FF	CLRWDT			; @@P=877@@
		BANKSEL	EEADR		; @@P=877@@ (Bank 2)
		MOVLW	EE_IDLE		; @@P=877@@
		MOVWF	EEADR		; @@P=877@@

;----------------------------------------------------------------
; POST Light Displays
;
; Wait to allow master/slave light to be noticed,
; extinguish all lights, then flash ROM ID (yel),
; GRN+devID (red), then all off.
;----------------------------------------------------------------
POST_START	CALL	DELAY_2S
		BANKSEL	PORT_LEDS	; (Bank 0)               _
		CLRF	PORT_LEDS	; XXX also clears ACT, T/R
		;
		; Set baud-rate generator
		;
		BANKSEL	SPBRG		; (Bank 1)
		MOVLW	.64
		MOVWF	SPBRG		; 19,236 baud
		;
		; Enable serial transmitter
		;
		BANKSEL	TXSTA		; (Bank 1)
		CLRF	TXSTA
		BSF	TXSTA, BRGH	; High Baud Rate
		BANKSEL	RCSTA		; (Bank 0)
		CLRF	RCSTA
		BSF	RCSTA, SPEN	; Turn on USART
		BANKSEL TXSTA		; (Bank 1)
		BSF	TXSTA, TXEN	; Turn on serial transmitter
		BANKSEL	PORT_LEDS	; (Bank 0)
		CALL	DELAY_2S

POST_ROM_ID	MOVLW	.1		; 1=ROM 2.0
		CALL	FLASH_YEL	; Flash ROM ID
		CALL	DELAY_2S

;@@--MASTER--@@
POST_DEV_ID	BSF	PORT_GRN, BIT_GRN
		CALL	DELAY_250MS
		BANKSEL	DEVICE_ID	; (Bank 0)
		MOVF	DEVICE_ID, W
		CALL	FLASH_RED	; Flash Device ID
		BCF	PORT_GRN, BIT_GRN
		CALL	DELAY_2S
;@@--END--@@
POST_STAGE_1	BSF	PORT_RED, BIT_RED
		CALL	DELAY_1S
		;
		; Set up USART & misc. options
		;
		BANKSEL	OPTION_REG	     ; (Bank 1)
		BSF	OPTION_REG, NOT_RBPU ; No pull-up on PORTB
		BCF	OPTION_REG, INTEDG   ; Int on falling edge
		BCF	OPTION_REG, T0CS     ; TMR0 internal clock
		                             ; Prescaler on WDT, 1:128
		;
		; Initialiaze timer2 interrupt
		;
		CLRF	PIE1		; Also disables TXIE, RXIE
		BSF	PIE1, TMR2IE	; Timer 2 match Interrupt enabled
		CLRF	PIE2
;
; set slice timer (TMR2) to period of 137 at 1:8 scale, or 0.0002192 sec,
; which is just less than 1/38 half-cycle (i.e. 38x ZC interrupt rate
; at 60Hz)
;
		MOVLW	.137
		MOVWF	PR2

		;
		; Initialize serial port receiver
		;
		CALL	DELAY_2S	; Wait to be sure Tx going
		BANKSEL	RCSTA		; (Bank 0)
		BSF	RCSTA, CREN	; Enable receiver
		;
		; Enable INT0 interrupt
		;
		CLRF	INTCON
		BSF	INTCON, PEIE	; Peripheral Interrupts enabled
		BSF	INTCON, INTE	; INT0 enabled

		CLRF	T1CON		; Timer 1 OFF
		MOVLW	b'00001001'	; Timer 2 OFF, prescale 1:4 postscale 1:2
		MOVWF	T2CON
		CLRF	TMR2		; Reset Timer 2 value
		
POST_STAGE_2	BCF	PORT_RED, BIT_RED
		CALL	DELAY_250MS
		BSF	PORT_YEL, BIT_YEL

POST_PHASE_SYNC	CLRWDT
;
; @@--MASTER--@@
; Inform the slave MPU of the phase offset and start it running
;
		CALL	DELAY_1S
		BANKSEL	PHASE_OFFSET	; (Bank 0)
		MOVF	PHASE_OFFSET, W
		;CALL	SEND_W
		;CALL	FLUSH_SIO
		; SEND_W/FLUSH_SIO aren't ready yet.
		; send byte on our own
		CLRWDT
		BTFSS	PIR1, TXIF	; clear to send?
		GOTO	$-2		; no, wait for it.
		MOVWF	TXREG		; transmit value
		CALL	FLASH_PHASE
;
; @@--SLAVE--@@
; Meanwhile, in the slave, we hold until we receive the phase offset
; value, then store it and flash it on the display.
;
		BANKSEL	PHASE_OFFSET	; (Bank 0)
		CLRWDT
		BTFSS	PIR1, RCIF	; Wait for Rx byte
		GOTO	$-2
		MOVF	RCREG, W	; Get byte and store it
		MOVWF	PHASE_OFFSET
		CALL	FLASH_PHASE
;
; @@--END--@@
;
; Finally, start up the timer and enable interrupts, and enter
; the main program loop.
;
POST_FINAL	CLRWDT
		BANKSEL	TMR2		; (Bank 0)
		CLRF	PIR1		; Clear interrupt flags
		CLRF	PIR2		; Clear interrupt flags
		CLRF	INTCON		; Clear interrupt flags
		BSF	INTCON, PEIE	; Enable peripheral interrupts
		BSF	INTCON, INTE	; Enable INT0 interrupt
		CLRF	TMR2		; Clear timer value
		BSF	T2CON, TMR2ON	; Start timer running
          	BSF	PBUF_YEL, BIT_YEL

		CLRF	YEL_TMR		; Reset LED timer values
		CLRF	RED_TMR
;@@--MASTER--@@
		CLRF	ACT_TMR		
;@@--END--@@
		MOVLW	GRN_BLINK_RATE
		MOVWF	GRN_TMR

		CLRF	SSR_STATE
		CLRF	SSR_STATE2
		CLRF	SSR_STATE3
		CLRF	DATA_BUF
		CLRF	CUR_SLICE
		CLRF	CUR_PRE
		CLRF	RX_BYTE
		
		BSF	SSR_STATE, GRNEN
		BSF	SSR_STATE2, SSRUPD	; to make lights appear
		BSF	SSR_STATE3, PRIVEN

		MOVLW	TXBUF
		MOVWF	TXBUF_QUEUE
		MOVWF	TXBUF_SEND

		CALL	ALL_SSRS_OFF
		CALL	UPDATE_PORTS
;
; Assert that some important constants have the values they
; are assumed to have.  This is for critical things where
; the stability of the whole system is at stake.  For example,
; a bitmask which limits how far a jump table can go.
;
POST_ASSERTIONS	CLRWDT
		MOVLW	CMD_SW_MASK	
		SUBLW	.7
		BTFSS	STATUS, Z
		GOTO	ASSERT_FAIL
		MOVLW	SSR_STATE_MASK
		SUBLW	.7
		BTFSS	STATUS, Z
		GOTO	ASSERT_FAIL
		MOVLW	CMD_CHAN_MASK
		SUBLW	.63
		BTFSS	STATUS, Z
		GOTO	ASSERT_FAIL
		MOVLW	SSR_DEV_MASK
		SUBLW	.31
		BTFSC	STATUS, Z
		GOTO	ASSERT_PASS
ASSERT_FAIL	MOVLW	.3
		GOTO	FAULT
ASSERT_PASS 	BSF	INTCON, GIE	; Enable interrupts
		;
		; Fall-through
		;       |
		;       |
		;       V

;================================================================
; MAIN PROGRAM LOOP
;================================================================
;
; This code is run over and over as fast as we can manage.  It keeps the SSR
; logic updated (on cue from the interrupt-driven timing controls), polls for
; serial line input (which it also parses) and keeps the front panel LEDs
; happy.
;
MAIN_LOOP	CLRWDT
		BANKSEL	0			; (bank 0)
;
; Blink green LED every GRN_BLINK_RATE zero-crossings (1/120 sec)
; if SSR_STATE<GRNEN> set
;
MAIN_GREEN	BTFSS	SSR_STATE2, GRNBLK	; Time to blink green LED?
		GOTO	MAIN_YELLOW		; No...skip the following
		MOVLW	1<<BIT_GRN		; toggle green LED bit
		XORWF	PBUF_GRN, F
		BCF	SSR_STATE2, GRNBLK	; done, clear flag
		BSF	SSR_STATE2, SSRUPD

MAIN_YELLOW	BTFSS	SSR_STATE2, YELOFF	; Time to turn off yellow LED?
		GOTO	MAIN_YEL_PRV
		BCF	PBUF_YEL, BIT_YEL
		BCF	SSR_STATE2, YELOFF
		BSF	SSR_STATE2, SSRUPD

MAIN_YEL_PRV	BTFSS	SSR_STATE3, PRIVEN	; Force YEL on if privs enabled
		GOTO	MAIN_RED
		BSF	PBUF_YEL, BIT_YEL
		BSF	SSR_STATE2, SSRUPD

MAIN_RED	BTFSS	SSR_STATE2, REDOFF	; Time to turn off red LED?
		GOTO	MAIN_ACT
		BCF	PBUF_RED, BIT_RED
		BCF	SSR_STATE2, REDOFF
		BSF	SSR_STATE2, SSRUPD

MAIN_ACT	CLRWDT
; @@--MASTER--@@
		BTFSS	SSR_STATE3, ACTOFF	; Time to turn off active LED?
		GOTO	MAIN_PROCESS		; No: skip this
		BCF	PBUF_ACT, BIT_ACT
		BCF	SSR_STATE3, ACTOFF
		BSF	SSR_STATE2, SSRUPD
; @@--END--@@

MAIN_PROCESS	CALL	POLL_SIO		; process pending command byte
		CALL	SEND_SIO		; send outgoing bytes
		CALL	UPDATE_SSRS		; update the SSR lines

END_MAIN	GOTO	MAIN_LOOP

;------------------------------------------------------------------------------
; SEND_SIO
;  Serial output queue management.
;
; Context: Sets bank 0
; In:      Reads TXBUF
; Also:    Affects INDF, FSR, TXBUF*, SSR_STATE2<TXQUE>
;
; FLUSH_SIO     Drains the entire output buffer before returning (blocking)
; SEND_SIO      Sends at most one character (non-blocking; returns immediately
;               if the transmitter is still busy)
;
;------------------------------------------------------------------------------
FLUSH_SIO	CLRWDT
		BANKSEL	SSR_STATE2		; (Bank 0)
		BTFSS	SSR_STATE2, TXQUE
		RETURN
		CALL	SEND_SIO
		GOTO	FLUSH_SIO
		
SEND_SIO	CLRWDT
		BANKSEL	SSR_STATE2
; @@--MASTER--@@
		BTFSS	SSR_STATE2, TXQUE
		RETURN
		BTFSS	PIR1, TXIF	; is transmitter ready?
		RETURN			; no: wait for next pass
		BCF	STATUS, IRP	; FSR in bank 0/1
		MOVF	TXBUF_SEND, W	; yes: set pointer to data
		MOVWF	FSR
		MOVF	INDF, W		; send [FSR] to transmitter
		MOVWF	TXREG

		INCF	TXBUF_SEND, W	; bump pointer
		ANDLW	TXBUF_MASK	; wrap within table bounds
		IORLW	TXBUF
		MOVWF	TXBUF_SEND
		SUBWF	TXBUF_QUEUE, W		; is buffer empty now?
		BTFSC	STATUS, Z
		BCF	SSR_STATE2, TXQUE	; yes: clear tx flag

		BSF	PBUF_RED, BIT_RED	; flash red light
		MOVLW	SLV_TX_LEN
		MOVWF	RED_TMR
		BSF	SSR_STATE, REDEN
		BSF	SSR_STATE2, SSRUPD
; @@--SLAVE--@@
		BCF	SSR_STATE2, TXQUE	; can't Tx from slave
; @@--END--@@
		RETURN

;----------------------------------------------------------------
; SEND_W
;  Queue W to transmit on serial port.
;
; Context: Sets Bank 0
; In:      W=data to send
; Also:    Affects SSR_STATE2<TXQUE>, FSR, TXBUF*, X
;
; Traps Fault 2 if the buffer is full.  This is a fatal error!
; It probably doesn't need to be, but it's safer to err on
; the side of caution here.
;----------------------------------------------------------------

SEND_W		CLRWDT
		BANKSEL	SSR_STATE2		; (Bank 0)
		MOVWF	X			; save value
		BTFSS	SSR_STATE2, TXQUE	; Check for buffer overflow
		GOTO	SEND_W_OK		; Buffer empty; go ahead
		MOVF	TXBUF_SEND, W		; Compare pointers
		SUBWF	TXBUF_QUEUE, W		; If equal, buffer is full
		BTFSS	STATUS, Z
		GOTO	SEND_W_OK
		MOVLW	.2			; oops, buffer full
		GOTO	FAULT

SEND_W_OK	CLRWDT				; insert W into buffer
		BCF	STATUS, IRP		; FSR in bank 0/1
		MOVF	TXBUF_QUEUE, W
		MOVWF	FSR
		MOVF	X, W
		MOVWF	INDF
		INCF	TXBUF_QUEUE, W		; bump pointer
		ANDLW	TXBUF_MASK		; wrap within table bounds
		IORLW	TXBUF
		MOVWF	TXBUF_QUEUE
		BSF	SSR_STATE2, TXQUE	; flag non-empty buffer

		RETURN

;------------------------------------------------------------------------------
; POLL_SIO
;  Serial I/O handling.
;
; Reads incoming byte from the serial network and interprets it,
; executing the corresponding code to handle the command (assuming
; it's addressed to this unit).
;
; Context: Sets bank 0
;
; 1 start bit, 8 data bits, 1 stop bit, no parity, 19.2Kbaud
; when data received: PIR1<RCIF> set, interrupt raised if enabled
; (PIE1<RCIE>), byte received available in RCREG.  Reading from 
; RCREG clears it and the RCIF bit.  (Actually, RCREG is a 2-deep
; FIFO; if it fills up, RCSTA<OERR> (overrun) is raised.  If this
; happens, the I/O locks up and you must turn off and then back
; on the CREN bit.)
;
; Framing errors assert the RCSTA<FERR> bit.
;
; Note that at full speed, you'll get a character every ~.5mS so
; the polling loop has to be at least that fast. (about 2,500 
; instruction cycles between characters)
; 
DRAIN_SIO_IN	CLRWDT			; drain receiver
		BANKSEL PIR1		; (bank 0)
		BTFSS	PIR1, RCIF	; character received?
		RETURN			; no: stop
		;BCF	PIR1, RCIF	; yes: acknowledge...
		MOVF	RCREG, W	; ...read byte...
		GOTO	DRAIN_SIO_IN	; ...and repeat.

POLL_SIO	CLRWDT
		BANKSEL PIR1		; (bank 0)
		BTFSS	PIR1, RCIF	; character received?
		RETURN			; no--move along...

		;BCF	PIR1, RCIF	; acknowledge receipt

		BTFSC	RCSTA, OERR	; overrun error?
		GOTO	SIO_OVERRUN

		BTFSC	RCSTA, FERR	; framing error?
		GOTO	SIO_FRAMERR
		
		CLRWDT
		MOVF	RCREG,W
		MOVWF	RX_BYTE			; store received byte
;
; Parse the command stream.
; At this point, we've just received a data byte into RX_BYTE.  The 
; state of the parser state machine (SSR_STATE<STATE>) dictates what 
; we do with the byte we just got.
;
; State:	Byte:
; [0] IDLE	DATA: ignore
;		CMD for other: ignore
;		CMD 0: exec all channels off
;		CMD 1: store cmd; -> 1
;		CMD 2: store cmd; -> 2
;		CMD 3: exec error
;		CMD 4: exec error
;		CMD 5: exec error
;		CMD 6: exec error
;		CMD 7: -> 4
;
; [1] SETCHAN	CMD: error -> 0; rescan
;		DATA: exec set channel on/off -> 0
;
; [2] DIMCHAN1	CMD: error -> 0; rescan
;		DATA: store byte; -> 3
;
; [3] DIMCHAN2	CMD: error -> 0; rescan
;		DATA: exec set channel dim level -> 0
;
; [4] ADMIN     CMD: error -> 0; rescan
;               DATA: exec sub-command -> 0
;
; [5-7] UNDEF	HALT ON INTERNAL FAULT
;
CMD_PARSER	CLRWDT
		BTFSS	RX_BYTE, CMD_BIT	; is this a command byte?
		GOTO	DATA_BYTE		; no, go process data byte
;--------------------------------------------------------------------------
; RECEIVED COMMAND BYTE
;
; If we were still waiting for bytes to complete a command (state != 0),
; we abort the command with an error.  Otherwise, we act on the command
; if it's addressed to us.
;
		MOVF	SSR_STATE, W		; COMMAND BYTE:
		ANDLW	SSR_STATE_MASK		; --Error if state != 0
		BTFSS	STATUS, Z		;
		GOTO 	CMD_ABORT		;
;
; Received command in state 0 (idle).  If we're the master, we make sure
; the command is addressed to us, and ignore it if it's not.  If we are
; the slave, our commands all come from the master, so we just do them
; unconditionally.
;
; @@--MASTER--@@
		MOVLW	CMD_ADDR_MASK		; Mask off cmd address
		ANDWF	RX_BYTE, W
		SUBWF	DEVICE_ID, W
		BTFSS	STATUS, Z		; Is the command mine?
		RETURN				; nope
		
		MOVLW	ACT_RX_LEN		; Turn on active LED
		MOVWF	ACT_TMR
		BSF	SSR_STATE3, ACTEN
		BSF	PBUF_ACT, BIT_ACT
; @@--SLAVE--@@
		MOVLW	SLV_RX_LEN		; Flash red LED
		MOVWF	RED_TMR
		BSF	SSR_STATE, REDEN
		BSF	PBUF_RED, BIT_RED
; @@--END--@@
		BSF	SSR_STATE2, SSRUPD
		GOTO	STATE_0_CMD_TBL		; dispatch command from RX_BYTE
;
; COMMAND 0: 	ALL CHANNELS OFF
; 		1000aaaa
;			Set all device channels to OFF state
;
CMD_0		CALL	ALL_SSRS_OFF
		GOTO	PASS_DOWN
;
; COMMAND 1:	SET CHANNEL ON/OFF
;		1001aaaa ...
;		Wait for next byte
;
CMD_1		BSF	SSR_STATE, STATE0	; -> 1
		RETURN
;
; COMMAND 2:	SET CHANNEL DIMMER LEVEL
;		1010aaaa ...
;		Wait for next byte
;
CMD_2		BSF	SSR_STATE, STATE1	; -> 2
		RETURN
;
; COMMAND 7:	ADMINISTRATIVE COMMANDS
;		1011aaaa ...
;		Wait for next byte
;
CMD_7		BSF	SSR_STATE, STATE2	; -> 4
		RETURN
;		
;--------------------------------------------------------------------------
; RECEIVED DATA BYTE
;
; If we were not waiting for one (state zero), just ignore it.  It's some-
; one else's.  Otherwise, do what we were waiting for.
;
; Data byte handler dispatch based on state machine value.
;
DATA_BYTE	GOTO	DATA_BYTE_TBL		; Dispatch command from state
						; machine value.

FAULT_1		MOVLW	.1			; Fault code
		GOTO	FAULT			; Halt on error
;
; COMMAND 1:	SET CHANNEL ON/OFF
;		1001aaaa 0fvvvvvv
;		Set channel vvvvvv to on if f=1 or off if f=0
;
DATA_STATE_1	CLRWDT
		BANKSEL SSR_ID			; (bank 0)
		MOVF	RX_BYTE, W		; get channel id byte
		ANDLW	CMD_CHAN_MASK
		MOVWF	SSR_ID
		CALL	XLATE_SSR_ID		; get local SSR ID
		BTFSC	SSR_ID, ILLSSR		; is it a bad SSR?
		GOTO	CMD_ERROR
		BTFSS	SSR_ID, MY_SSR		; is it even my SSR?
		GOTO	PASS_CMD_1     		; nope

		CLRF	INDF			; clear dim, on, value
		BTFSC	RX_BYTE, CMD_CHAN_ON	; set ON if on bit set in cmd
		BSF	INDF, SSR_ON
		GOTO	CMD_RESET_STATE

PASS_CMD_1	CLRWDT				; not my SSR, send to slave CPU
; @@--MASTER--@@
		MOVLW	b'10010000'
		CALL	SEND_W
		MOVF	RX_BYTE, W
		CALL	SEND_W
		GOTO	CMD_RESET_STATE
; @@--SLAVE--@@
		GOTO	FAULT
; @@--END--@@

;
; Reset state machine (-> 0)
; This is usually the last step in any command execution.
;
CMD_RESET_STATE	CLRWDT
		MOVLW	~SSR_STATE_MASK
		ANDWF	SSR_STATE, F		; -> 0
		RETURN
;
; COMMAND 2:	SET CHANNEL DIMMER LEVEL
;		1010aaaa 0xvvvvvv ...
;		Wait for last byte
;
DATA_STATE_2	CLRWDT
		MOVF	RX_BYTE, W
		MOVWF	DATA_BUF		; store received byte
		BSF	SSR_STATE, STATE0	; -> 3
		RETURN
;
; COMMAND 2:	SET CHANNEL DIMMER LEVEL
;		1010aaaa 0xvvvvvv 0xxddddd
;		Set channel vvvvvv to dimmer level ddddd.
;
; note that setting value=0 or value=31 here is subtly different
; than just using the "set on/off" command.  This always engages
; the dimmer controls, although in theory a value of 0 should never
; get turned on, and a value of 31 should be pretty darn near fully
; on.
;
DATA_STATE_3	CLRWDT
		MOVF	DATA_BUF, W		; get requested channel
		ANDLW	CMD_CHAN_MASK
		MOVWF	SSR_ID
		CALL	XLATE_SSR_ID		; normalize channel ID
		BTFSC	SSR_ID, ILLSSR		; is it even valid?
		GOTO	CMD_ERROR
		BTFSS	SSR_ID, MY_SSR		; is it for me?
		GOTO	PASS_CMD_2		; no: pass to slave

		MOVF	RX_BYTE, W		; get dimmer value
		ANDLW	CMD_DIM_MASK
		MOVWF	INDF			; write to SSR value buffer
		BSF	INDF, SSRDIM		; set SSR channel flags
		BCF	INDF, SSR_ON
		GOTO	CMD_RESET_STATE
;
; If the channel is actually for the slave CPU, we need to send it
; over there.
;
PASS_CMD_2	CLRWDT
; @@--MASTER--@@
		MOVLW	b'10100000'
		CALL	SEND_W
		MOVF	DATA_BUF, W
		CALL	SEND_W
		MOVF	RX_BYTE, W
		CALL	SEND_W
		GOTO	CMD_RESET_STATE		
; @@--SLAVE--@@
		GOTO	FAULT
; @@--END--@@
;
; COMMAND 7:    ADMINISTRATIVE FUNCTIONS
;               1111aaaa 0xxxxxxx
;                        00pppppp set phase offset=p(*)
;                        010baaaa set device ID(*)
;                        01100000 shutdown(*)
;                        01100001 disable privileged commands
;                        011101yr (slave) red/yel 2s
;                        01111gyr (slave) halt with LED pattern
;        
DATA_STATE_4	CLRWDT
		BTFSS	RX_BYTE, 6		; -0------ set phase offset
		GOTO	CMD_SET_PHASE
		BTFSS	RX_BYTE, 5		; -10----- set device id
		GOTO	CMD_SET_DEV_ID
		BTFSS	RX_BYTE, 4		; -110---- admin commands
		GOTO	CMD_ADMIN
CMD_SLAVE_CTL	CLRWDT				; -111---- slave control commands
; @@--MASTER--@@
		GOTO	CMD_ERROR		; These can't come from outside
; @@--SLAVE--@@
		BTFSC	RX_BYTE, 3		; -1111--- HALT with LED pattern
		GOTO	CMD_SLV_HALT
		BTFSC	RX_BYTE, 2		; -11101-- Display LED pattern 2s
		GOTO	CMD_SLV_LEDS
		GOTO	CMD_ERROR		; -11100xx Reserved for future commands
;
; ADMIN: SLAVE: HALT     1111xxxx 01111gyr
; Display a pattern on the LEDs and halt
;
CMD_SLV_HALT	CLRWDT
		BCF	INTCON, GIE		; disable interrupts
		CALL	ALL_SSRS_OFF
		CLRF 	PORTE_BUF
		CALL	UPDATE_PORTS
		BTFSC	RX_BYTE, 2
		BSF	PBUF_GRN, BIT_GRN
		BTFSC	RX_BYTE, 1
		BSF	PBUF_YEL, BIT_YEL
		BTFSC	RX_BYTE, 0
		BSF	PBUF_RED, BIT_RED
		CALL	UPDATE_PORTS
CMD_SLV_STOP	CLRWDT
		GOTO	$-1
;
; ADMIN: SLAVE: LEDS     1111aaaa 011101yr
; Display a pattern on the yellow/red LEDs for 2s
;
CMD_SLV_LEDS	CLRWDT
		BTFSS	RX_BYTE, 1
		GOTO	CMD_SLV_LED_R
		MOVLW	SLV_LED_LEN
		MOVWF	YEL_TMR
		BSF	SSR_STATE, YELEN
		BSF	PBUF_YEL, BIT_YEL
		BSF	SSR_STATE2, SSRUPD
CMD_SLV_LED_R	BTFSS	RX_BYTE, 0
		GOTO	CMD_RESET_STATE
		MOVLW	SLV_LED_LEN
		MOVWF	RED_TMR
		BSF	SSR_STATE, REDEN
		BSF	PBUF_RED, BIT_RED
		BSF	SSR_STATE2, SSRUPD
		GOTO	CMD_RESET_STATE
; @@--END--@@
;
; ADMIN: SET PHASE       1111aaaa 00pppppp
; Set phase offset to p, reboot device
;
CMD_SET_PHASE	CLRWDT
		BTFSS	SSR_STATE3, PRIVEN	; not allowed if privs disabled
		GOTO	CMD_PRIV_ERROR
; @@--MASTER--@@
		MOVLW	b'11110000'		; pass down to slave, too
		CALL	SEND_W			; 
		CALL	PASS_DOWN 		; 
		CALL	FLUSH_SIO

		CLRWDT				; burn into EEPROM
		BANKSEL	EEADR			; (Bank 2)
		CLRF	EEDATH
		CLRF	EEADRH
		MOVLW	EE_PHASE
		MOVWF	EEADR
		BANKSEL	RX_BYTE			; (Bank 0)
		MOVF	RX_BYTE, W
		ANDLW	CMD_AD_PH_MASK
		BANKSEL	EEDATA			; (Bank 2)
		MOVWF	EEDATA
		BANKSEL	EECON1			; (Bank 3)
		BCF	EECON1, EEPGD		; Write to data memory
		BSF	EECON1, WREN		; Enable EEPROM writing
		BCF	INTCON, GIE
		MOVLW	0x55
		MOVWF	EECON2
		MOVLW	0xAA
		MOVWF	EECON2
		BSF	EECON1, WR
		BCF	EECON1, WREN
		CLRWDT
		BTFSC	EECON1, WR
		GOTO	$-1
		BANKSEL	PIR2			; (Bank 0)
		BCF	PIR2, EEIF
; @@--END--@@
		GOTO	RESTART_VECTOR		; Restart device from scratch
;
; ADMIN: SET DEVICE ID   1111aaaa 010baaaa
; Change this device's ID on the serial network
;
; as a check bit, b==a<0>.  So, to set the device
; to ID=2, send 1111aaaa 01000010; to set it
; to ID=5, send 1111aaaa 01010101.
;
CMD_SET_DEV_ID	CLRWDT
		BTFSS	SSR_STATE3, PRIVEN	; not allowed if privs disabled
		GOTO	CMD_PRIV_ERROR
;
; @@--MASTER--@@
;
; Verify check bit
;
		BTFSS	RX_BYTE, 0
		GOTO	CMD_SDI_0
		BTFSS	RX_BYTE, 4		; a<0>=1
		GOTO	CMD_ERROR		; but b=0: REJECT!
		GOTO	CMD_SDI_OK
CMD_SDI_0	BTFSC	RX_BYTE, 4		; a<0>=0
		GOTO	CMD_ERROR		; but b=1: REJECT!
;
; Write to DEVICE_ID and burn to EEPROM
;
CMD_SDI_OK	MOVF	RX_BYTE, W
		ANDLW	CMD_ADDR_MASK
		MOVWF	DEVICE_ID

		BCF	INTCON, GIE		; Clear interrupts
		CALL	ALL_SSRS_OFF		; Shut everything off
		CLRF	PORTE_BUF
		CALL	UPDATE_PORTS

		CLRWDT				; burn into EEPROM
		BANKSEL	EEADR			; (Bank 2)
		CLRF	EEDATH
		CLRF	EEADRH
		MOVLW	EE_DEV_ID
		MOVWF	EEADR
		BANKSEL	DEVICE_ID		; (Bank 0)
		MOVF	DEVICE_ID, W
		BANKSEL	EEDATA			; (Bank 2)
		MOVWF	EEDATA
		BANKSEL	EECON1			; (Bank 3)
		BCF	EECON1, EEPGD		; Write to data memory
		BSF	EECON1, WREN		; Enable EEPROM writing
		MOVLW	0x55
		MOVWF	EECON2
		MOVLW	0xAA
		MOVWF	EECON2
		BSF	EECON1, WR
		BCF	EECON1, WREN
		CLRWDT
		BTFSC	EECON1, WR
		GOTO	$-1
		BANKSEL	PIR2			; (Bank 0)
		BCF	PIR2, EEIF
;
; Display new ID on LEDs
;
		CLRWDT
		CALL	DELAY_2S
            	BSF	PORT_GRN, BIT_GRN
		CALL	DELAY_250MS
		BANKSEL	DEVICE_ID	; (Bank 0)
		MOVF	DEVICE_ID, W
		CALL	FLASH_RED	; Flash Device ID
		BCF	PORT_GRN, BIT_GRN
		CALL	DELAY_2S
;
; Resume operations
;
		BSF	INTCON, GIE
		GOTO	CMD_RESET_STATE	
; @@--SLAVE--@@
		GOTO	FAULT
; @@--END--@@
;
; ADMIN: MISC. ADMINISTRATIVE FUNCTIONS
;               1111aaaa 0110xxxx (function x (0-15))
;                        01100000 shutdown(*)
;                        01100001 disable privileged commands
; 
CMD_ADMIN	GOTO	CMD_ADMIN_TABLE

;
; ADMIN: SHUTDOWN
;
CMD_AD_SHUTDOWN	CLRWDT
		BTFSS	SSR_STATE3, PRIVEN	; not allowed if privs disabled
		GOTO	CMD_PRIV_ERROR
; @@--MASTER--@@
		MOVLW	b'11110000'
		CALL	SEND_W	
		CALL	PASS_DOWN
		CALL	FLUSH_SIO
; @@--END--@@
		BCF	INTCON, GIE		; turn off interrupts
		CALL	ALL_SSRS_OFF
		CLRF	PORTE_BUF
		CALL	UPDATE_PORTS
		CALL	DELAY_250MS
		BSF	PORT_YEL, BIT_YEL
		CALL	DELAY_1S
		BCF	PORT_YEL, BIT_YEL
		CALL	DELAY_250MS
		BSF	PORT_RED, BIT_RED
		CALL	DELAY_2S
		SLEEP
             	CLRWDT				; extra paranoia
		GOTO	$-1
;
; ADMIN: DISABLE PRIVILEGED FUNCTIONS
;
CMD_AD_DIS_PRIV	CLRWDT
; @@--MASTER--@@
		MOVLW	b'11110000'
		CALL	SEND_W
		CALL	PASS_DOWN
; @@--END--@@
		BCF	SSR_STATE3, PRIVEN
		BTFSS	SSR_STATE, YELEN
		BCF	PBUF_YEL, BIT_YEL
		BSF	SSR_STATE2, SSRUPD
		GOTO	CMD_RESET_STATE
;------------------------------------------------------------------------------
; ERROR HANDLING
;------------------------------------------------------------------------------
;
; CMD_PRIV_ERROR Received privileged command when not enabled
;
; CMD_ERROR	 Received invalid command; flash LED and ignore it
;
; CMD_ABORT	 Received invalid byte in command sequence; flash
;		 LED and re-parse received byte in case it might be
;		 a new command addressed to us
;
CMD_PRIV_ERROR	CLRWDT
; @@--MASTER--@@
; The diagnostic LEDs are on the slave side, so the
; master just commands the slave to display Y+R 2S
;
		MOVLW	b'11110000'
		CALL	SEND_W
		MOVLW	b'01110111'
		CALL	SEND_W
; @@--SLAVE--@@
; If we detected this in the slave, we can just
; handle it directly here.
		BSF	PBUF_YEL, BIT_YEL
		BSF	PBUF_RED, BIT_RED
		MOVLW	.240
		MOVWF	YEL_TMR
		MOVWF	RED_TMR
		BSF	SSR_STATE, YELEN
		BSF	SSR_STATE, REDEN
		BSF	SSR_STATE2, SSRUPD
; @@--END--@@
		GOTO	CMD_RESET_STATE

CMD_ERROR	CLRF	RX_BYTE			; clear byte so rescan==ignore
CMD_ABORT	CLRWDT
		BSF	PBUF_YEL, BIT_YEL
		MOVLW	YEL_CMDERR_LEN
		MOVWF	YEL_TMR
		BSF	SSR_STATE, YELEN
		BSF	SSR_STATE2, SSRUPD
		CALL	CMD_RESET_STATE		; -> 0
		GOTO	CMD_PARSER		; rescan byte
;
; Data overrun!  Panic!
;
SIO_OVERRUN	CLRWDT
		BCF	RCSTA, CREN		; shut down receiver
		CALL	DELAY_250MS		; for 250mS (maybe longer
		BSF	RCSTA, CREN		; than strictly necessary)
		MOVLW	RED_ORERR_LEN
		MOVWF	RED_TMR
		BSF	SSR_STATE, REDEN
		BSF	PBUF_RED, BIT_RED
		BSF	SSR_STATE2, SSRUPD
		GOTO	CMD_RESET_STATE
;
; Framing Error!  Don't Panic!  But flag as a command error, reset state
; machine, etc.
;
SIO_FRAMERR	GOTO	CMD_ERROR
;
;==============================================================================
; XLATE_SSR_ID
;  Translate the channel number to a local SSR number 0-23.
;
; Context: Sets Bank 0
; In:      SSR_ID=raw command
; Out:     SSR_ID=adjusted value, MY_SSR,ILLSSR flags
;          FSR=pointer to SSR value register
;
;==============================================================================
;
; Given a raw channel number in SSR_ID, convert it to the local
; SSR ID 0-23 and set the MY_SSR bit if this board has that SSR.
; Load FSR to point to that SSR's buffer
;
; Otherwise, clear MY_SSR and the other bits are undefined (in
; which case we should ignore the command and let the other board
; handle it).
;
; For this model, SSR ID 00-23 is for the master board,
; and SSR ID 24-47 is 00-23 on the slave board.
;
; If an illegal SSR ID is specified, ILLSSR is set.  In
; this case, disregard ALL OTHER BITS including MY_SSR.
;
XLATE_SSR_ID	CLRWDT
		BANKSEL	SSR_ID		; (bank 0)
		MOVLW	CMD_CHAN_MASK	; mask off just the channel
		ANDWF	SSR_ID, F	; (also clears MY_SSR and ILLSSR)
		MOVLW	.24		; subtract ch-24
		SUBWF	SSR_ID, W	; if ch<24, it is
; @@--MASTER--@@
		BTFSC	STATUS, C	; 
		RETURN                  ; return (not mine) if >= 24
; @@--SLAVE--@@
		BTFSS	STATUS, C	;
		GOTO	FAULT		; else...wait, we shouldn't see that!
            	CLRWDT			; slave continues checking...
		MOVWF	SSR_ID		; put adjusted channel back
		MOVLW	.24		; subtract 24 again
		SUBWF	SSR_ID, W	; just to be sure it was <48
		BTFSC	STATUS, C	; Skip if < 48
		BSF	SSR_ID, ILLSSR	; **flag as illegal SSR ID**
; @@--END--@@
		BSF	SSR_ID, MY_SSR	; it's mine!
		MOVF	SSR_ID, W
		ANDLW	CMD_CHAN_MASK	; calculate offset to SSR value register
		ADDLW	SSR00_VAL
		MOVWF	FSR             ; make FSR point to that register
		RETURN


;----------------------------------------------------------------
; PASS_DOWN
;  Pass received byte (in RX_BYTE) down to slave CPU.
;
; Context: Sets Bank 0
;
;----------------------------------------------------------------
PASS_DOWN	CLRWDT
		BANKSEL	RX_BYTE
; @@--MASTER--@@
		MOVF	RX_BYTE, W
		CALL	SEND_W
; @@--END--@@
		RETURN
		

;----------------------------------------------------------------
; FLASH_YEL
; FLASH_RED
;  Flash yellow or red LED a number of times
;
;  These write directly to the LED I/O port, so can only be 
;  used outside normal running mode (POST, etc).
;
;  Context: Bank 0
;  In:      W=flasher count
;  Also:    FLASH_CT I, J, K affected
;----------------------------------------------------------------
FLASH_YEL	CLRWDT
		BANKSEL	FLASH_CT	; (Bank 0)
		MOVWF	FLASH_CT
		CALL	FLASH_OFF_DELAY
		MOVF	FLASH_CT, F	; If already zero, stop
		BTFSC	STATUS, Z
		RETURN

NEXT_FLASH_YEL	BSF	PORT_YEL, BIT_YEL
		CALL	FLASH_ON_DELAY
		BCF	PORT_YEL, BIT_YEL
		CALL	FLASH_OFF_DELAY
		DECFSZ	FLASH_CT, F
		GOTO	NEXT_FLASH_YEL
		RETURN

FLASH_RED	CLRWDT
		BANKSEL	FLASH_CT	; (Bank 0)
		MOVWF	FLASH_CT
		CALL	FLASH_OFF_DELAY
		MOVF	FLASH_CT, F	; If already zero, stop
		BTFSC	STATUS, Z
		RETURN

NEXT_FLASH_RED	BSF	PORT_RED, BIT_RED
		CALL	FLASH_ON_DELAY
		BCF	PORT_RED, BIT_RED
		CALL	FLASH_OFF_DELAY
		DECFSZ	FLASH_CT, F
		GOTO	NEXT_FLASH_RED
		RETURN

;----------------------------------------------------------------
; FAULT
;  Register a fault condition and halt operations.
;
; Codes:
;  Value  A GY GYR  Meaning
;  000001 - -- --O  Illegal state machine value
;  000010 - -- -O-  TX buffer overflow
;  000011 - -- -OO  Assertion error in POST
;  (none) x xx OOO  Slave tried to pass cmd downstream
;  (none) x xx OOO  Any fault detected only in slave CPU
;  011000 - OO ---  Internal SSR index out of range (==24)
;     :      :
;  011111 - OO OOO  Internal SSR index out of range (==31)
; 
; Context: Sets Bank 0
; In:      W=fault code (0-63)
; Returns: never
;  
;----------------------------------------------------------------
FAULT		CLRWDT
		BANKSEL	INTCON
		BCF	INTCON, GIE	; disable interrupts
		CALL	ALL_SSRS_OFF	; kill outputs
		CLRF	PORTE_BUF	; reset T/R, LED outputs
		CALL	UPDATE_PORTS	; flush to output
;
; @@--MASTER--@@
;
; Send FAULT condition to slave CPU first.
; Bits <2:0> of the fault code are sent there to be displayed
; on its LEDs.
;   11111111 01111vvv -> slave

		MOVWF	X
		MOVLW	b'11111111'
		CALL	SEND_W
		MOVF	X, W
		ANDLW	b'00000111'	; mask off bits to send
		IORLW	b'01111000'	; add command code bits
		CALL	SEND_W
		CALL	FLUSH_SIO
;
; Display remaining 3 bits on ACT, GRN, YEL LEDs
;
		BTFSC	X, 5
		BSF	PBUF_ACT, BIT_ACT
		BTFSC	X, 4
		BSF	PBUF_GRN, BIT_GRN
		BTFSC	X, 3
		BSF	PBUF_YEL, BIT_YEL
;
; Flash red LED, effectively halting all other operations
;
FAULT_HALT	CLRWDT
		BSF	PBUF_RED, BIT_RED
		CALL	UPDATE_PORTS
		CALL	DELAY_500MS
		BCF	PBUF_RED, BIT_RED
		CALL	UPDATE_PORTS
		CALL	DELAY_500MS
		GOTO	FAULT_HALT
;
; @@--SLAVE--@@
;
; In the slave, we can't really report out faults so we'll
; just flash all our lights and halt.
;
FAULT_HALT	CLRWDT
		BSF	PBUF_RED, BIT_RED
		BSF	PBUF_YEL, BIT_YEL
		BSF	PBUF_GRN, BIT_GRN
		CALL	UPDATE_PORTS
		CALL	DELAY_500MS
		BCF	PBUF_RED, BIT_RED
		BCF	PBUF_YEL, BIT_YEL
		BCF	PBUF_GRN, BIT_GRN
		CALL	UPDATE_PORTS
		CALL	DELAY_500MS
		GOTO	FAULT_HALT
;
; @@--END--@@
;


;----------------------------------------------------------------
; FLASH_PHASE
;  Flash the phase offset value on the diagnostic LEDs.
;  Normal interrupt processing should be suspended during this
;  operation.
;
;  Properly turns off LEDs via port buffers, but then takes over
;  direct control of the LEDs like the POST-level commands do.
;  (this is called during POST as well)
;
; Context: Sets Bank 0
; In:      PHASE_OFFSET=phase
; Also:    I, J, K affected
;----------------------------------------------------------------
FLASH_PHASE	CLRWDT
		BANKSEL	PHASE_OFFSET	; (Bank 0)
		BCF	PBUF_GRN, BIT_GRN
		BCF	PBUF_YEL, BIT_YEL
		BCF	PBUF_RED, BIT_RED
		CALL	UPDATE_PORTS
		CALL	DELAY_2S
		BSF	PORT_RED, BIT_RED
		SWAPF	PHASE_OFFSET, W
		ANDLW	0x0F
		CALL	FLASH_YEL
		BCF	PORT_RED, BIT_RED
		CALL	DELAY_2S
		BSF	PORT_YEL, BIT_YEL
		MOVF	PHASE_OFFSET, W
		ANDLW	0x0F
		CALL	FLASH_RED
		BCF	PORT_YEL, BIT_YEL
		CALL	DELAY_2S
		RETURN
		
		

		

DELAY_1S        CLRWDT
FLASH_OFF_DELAY	MOVLW	.76
		MOVWF	I
		GOTO	ISPINNER

DELAY_500MS	CLRWDT
FLASH_ON_DELAY	MOVLW	.38
		MOVWF	I
		GOTO	ISPINNER

DELAY_2S	MOVLW	.152
		MOVWF	I
		GOTO	ISPINNER

DELAY_250MS	MOVLW	.19
		MOVWF	I
		GOTO	ISPINNER

DELAY_125MS	MOVLW	.10
		MOVWF	I
		GOTO	ISPINNER

; fash flasher value
DELAY_FFLASH	MOVLW	.5
		MOVWF	I
		GOTO	ISPINNER
		
;----------------------------------------------------------------
; ISPINNER
;  Delay for approximately I * 255 * 255 instructions.
;  I=19 is about 250mS
;  I=38 is about 500mS
;
; Context: ANY bank
; In:      I=delay
;
; Also:    J, K, W affected
;----------------------------------------------------------------
ISPINNER	CLRWDT
		MOVLW	.255
		MOVWF	J
ISP_NEXTJ	MOVLW	.255
		MOVWF	K
		DECFSZ	K,F
		GOTO	$-1
		DECFSZ	J,F
		GOTO	ISP_NEXTJ
		DECFSZ	I,F
		GOTO	ISPINNER
		RETURN

;------------------------------------------------------------------------------
; ALL_SSRS_OFF
;
; The fastest route to clearing all SSR channels
; call UPDATE_PORTS after this.
;
; Context: Sets Bank 0
; Also:    Affects W
;
;------------------------------------------------------------------------------
ALL_SSRS_OFF	CLRWDT
		BANKSEL	SSR00_VAL	; (Bank 0)
		CLRF	SSR00_VAL
		CLRF	SSR01_VAL
		CLRF	SSR02_VAL
		CLRF	SSR03_VAL
		CLRF	SSR04_VAL
		CLRF	SSR05_VAL
		CLRF	SSR06_VAL
		CLRF	SSR07_VAL
		CLRF	SSR08_VAL
		CLRF	SSR09_VAL
		CLRF	SSR10_VAL
		CLRF	SSR11_VAL
		CLRF	SSR12_VAL
		CLRF	SSR13_VAL
		CLRF	SSR14_VAL
		CLRF	SSR15_VAL
		CLRF	SSR16_VAL
		CLRF	SSR17_VAL
		CLRF	SSR18_VAL
		CLRF	SSR19_VAL
		CLRF	SSR20_VAL
		CLRF	SSR21_VAL
		CLRF	SSR22_VAL
		CLRF	SSR23_VAL
		MOVLW	b'00011111'
		IORWF	PORTA_BUF, F
		MOVLW	b'00111110'
		IORWF	PORTB_BUF, F
		MOVLW	b'00111111'
		IORWF	PORTC_BUF, F
		MOVLW	b'11111111'
		IORWF	PORTD_BUF, F
		RETURN

;----------------------------------------------------------------
; Port Control
;
; Registers PORTx_BUF hold the values we want to write to the
; output pins.  Calling UPDATE_PORTS does the actual writing.
;
; We do it this way to avoid the READ/MODIFY/WRITE effect 
; problems we'd have by fiddling with the I/O pins separately.
; Plus, this is more efficient if many pins are changing at
; once.
;
; UPDATE_PORTS
;  Context: Sets Bank 0
;  In:      PORTx_BUF
;  Also:    W affected
;----------------------------------------------------------------
UPDATE_PORTS	CLRWDT
		BANKSEL	PORTA		; (Bank 0)
		MOVF	PORTA_BUF, W
		MOVWF	PORTA
		MOVF	PORTB_BUF, W
		MOVWF	PORTB
		MOVF	PORTC_BUF, W
		MOVWF	PORTC
		MOVF	PORTD_BUF, W
		MOVWF	PORTD
		MOVF	PORTE_BUF, W
		MOVWF	PORTE
		RETURN
;
;=============================================================================
; SSR UPDATE LOOP
;
; Each slice we need to turn on some SSRs and off others.
; We use the SSR_STATE2<SLICE_UPD> flag to indicate that we
; haven't updated the SSR arrays yet in this slice.
;
; *****************************************************************************
; Main SSR update cycle.
;
; This is called repeatedly in the main loop.
; What we do here depends on the flag bits set by the background timing logic.
;
; DIM_START:  All SSRs marked as ON get turned on now
; DIM_END:    All SSRs *not* marked as ON get turned off now; ignore SLICE_UPD
; SLICE_UPD:  All SSRs under dimmer control whose value == CUR_SLICE get turned
;             on now
;
;
UPDATE_SSRS	CLRWDT
		BTFSS	SSR_STATE2, DIM_START	; at start of dimmer cycle?
		GOTO	UPDATE_END
;
; Start of a dimmer cycle (first active slice): turn on everything that is
; supposed to be on all the time (they won't be turned off again at all until
; they are marked as dimmed or off).
;
UPDATE_START	BCF	SSR_STATE2, DIM_START	; got the flag, thanks...
		MOVLW	.24			; Loop over our 24 SSRs...
		MOVWF	X			; X=loop counter 24->0
		CLRF	Y			; Y=SSR index 0->23
UPDATE_ST_LOOP	MOVF	Y, W
		CALL	SSR_SELECT_REG		; FSR=ssr control register
		BTFSS	INDF, SSR_ON		; is this SSR on? (not dimmed)
		GOTO	UPDATE_ST_NXT		; else, check next SSR...
		CALL	SSR_Y_TO_PBUF		; W=buffer for SSR bit
		BCF	STATUS, IRP		; FSR in bank 0/1
		MOVWF	FSR
		CALL	SSR_Y_CLR_MASK		; W=bitmask to clear SSR bit
		ANDWF	INDF, F			; clear the bit
		BSF	SSR_STATE2, SSRUPD	; Flag that a change was made
UPDATE_ST_NXT	INCF	Y, F			; bump counter and index
		DECFSZ	X, F
		GOTO	UPDATE_ST_LOOP
;
; End of a dimmer cycle (last active slice): don't bother turning on any
; SSRs with dimmer value zero (duh).  Instead, now is the time to actually
; turn off EVERYTHING which isn't supposed to be on steadily.
;
UPDATE_END	CLRWDT
		BTFSS	SSR_STATE2, DIM_END	; at end of dimmer cycle?
		GOTO	UPDATE_SLICE

		BCF	SSR_STATE2, DIM_END	; clear flag to do this
		BCF	SSR_STATE2, SLICE_UPD	; don't update for slice 0
		MOVLW	.24
		MOVWF	X
		CLRF	Y
UPDATE_EN_LOOP	MOVF	Y, W
		CALL	SSR_SELECT_REG		; FSR=ssr control register
		BTFSC	INDF, SSR_ON		; is this SSR not always on?
		GOTO	UPDATE_EN_NXT		; else, check next one...
		CALL	SSR_Y_TO_PBUF		; W=buffer for SSR bit
		BCF	STATUS, IRP		; FSR in bank 0/1
		MOVWF	FSR
		CALL	SSR_Y_SET_MASK
		IORWF	INDF, F			; set the bit
		BSF	SSR_STATE2, SSRUPD	; Flag that a change was made
UPDATE_EN_NXT	INCF	Y, F
		DECFSZ	X, F
		GOTO	UPDATE_EN_LOOP
;
; Any active dimmer cycle except the last one: CUR_SLICE holds the slice
; number we're processing, which starts at 63 and counts down to 0.  So
; we turn on any dimmer-controlled SSRs which have dimmer value equal to
; this slice number now.
;
UPDATE_SLICE	CLRWDT
		BTFSS	SSR_STATE2, SLICE_UPD	; are we supposed to update?
		GOTO	UPDATE_COMMIT		; no, move along...

		BCF	SSR_STATE2, SLICE_UPD	; got it, thanks...
		MOVLW	.24
		MOVWF	X
		CLRF	Y
UPDATE_SL_LOOP	MOVF	Y, W
		CALL	SSR_SELECT_REG
		BTFSS	INDF, SSRDIM 		; under dimmer control?
		GOTO	UPDATE_SL_NXT		; nope, try the next one...
		MOVLW	SSRVAL_MASK
		ANDWF	INDF, W
		SUBWF	CUR_SLICE, W
		BTFSS	STATUS, Z		; dimmer level == this slice?
		GOTO	UPDATE_SL_NXT		; nope, try the next one...
		CALL	SSR_Y_TO_PBUF
		BCF	STATUS, IRP		; FSR in bank 0/1
		MOVWF	FSR
		CALL	SSR_Y_CLR_MASK
		ANDWF	INDF, F
		BSF	SSR_STATE2, SSRUPD	; Flag that a change was made
UPDATE_SL_NXT	INCF	Y, F
		DECFSZ	X, F
		GOTO	UPDATE_SL_LOOP
;
; If any of the above routines were selected to actually do anyting with the
; I/O ports, commit any changes they made at this time.
;
UPDATE_COMMIT	CLRWDT
		BTFSC	SSR_STATE2, SSRUPD
		CALL	UPDATE_PORTS
		BCF	SSR_STATE2, SSRUPD
		RETURN 
;
;------------------------------------------------------------------------------
; SSR_SELECT_REG
;   Get SSR buffer address from SSR number in W
;
; Input:  W=SSR (0-23)
; Output: FSR=value register for SSR
;
; Context: Bank 0
;------------------------------------------------------------------------------
SSR_SELECT_REG	CLRWDT
		ANDLW	SSR_DEV_MASK		; limit to 32
		ADDLW	SSR00_VAL		; add offset
		MOVWF	FSR			; set as indirect reg
		BCF	STATUS, IRP		; FSR->Bank{0,1}
		RETURN
;		
;------------------------------------------------------------------------------
; SSR_Y_CLR_MASK
;   return inverse bitmask for SSR output in its I/O port
;   If you AND the bitmask with the port's value the channel is turned off.
;   If you want to get the bitmask for turning it on, see SSR_Y_SET_MASK.
;
; Input:    Y=SSR channel (0-23)
; Output:   W=bitmask for CLEARING the bit (AND with current value)
; Context:  Any Bank
;------------------------------------------------------------------------------
;;
SSR_Y_CLR_MASK	CALL	SSR_Y_SET_MASK
		XORLW	0xff
		RETURN

;==============================================================================
; Fine.
;==============================================================================
		
		END


;
; PRODUCT RELEASE NUMBERS
; Version 0.1 included 70 slices per half-wave cycle.
; Version 0.2 reduced this because we can't cram all the code into
; that short a run, and 32 levels of brightness is still more than
; enough.
; Version 0.3-0.6 were incremental development versions.
; Version 0.7 was the final prototype firmware.
; Version 0.8 began the first application to the 48SSR-3-1 boards.
; Version 1.0 was a special release based on 0.2 code (deprecated)
; Version 2.0 is the completely rewritten, full production 
; implementation for 48SSR-3-1 boards, based on version 0.8.
;
; DEVELOPMENT (CVS) SOURCE FILE REVISION NUMBERS
; $Log: 48ctlrom.asm,v $
; Revision 1.4  2007/12/18 07:12:48  steve
; completion point of release.
;
; Revision 1.3  2007/11/20 06:19:28  steve
; Corrected error in firmware, now appears to work as expected.  This is
; the 2.0 RC1 image.  (Ag)
;
; Revision 1.2  2007/11/19 22:27:58  steve
; updated master-slave code, misc. improvements; debugging
;
; Revision 1.1  2007/01/02 10:04:11  steve
; Initial revision
;
#endif
