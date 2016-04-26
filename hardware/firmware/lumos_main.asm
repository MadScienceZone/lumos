; OSCCON:SCS=00;HS;
; vim:set syntax=pic ts=8:
;
		LIST N=86
;@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
;@@                                                                         @@
;@@ @      @   @  @   @   @@@    @@@          LUMOS: LIGHT ORCHESTRATION    @@
;@@ @      @   @  @@ @@  @   @  @   @         SYSTEM FIRMWARE VERSION 3.1   @@ 
;@@ @      @   @  @ @ @  @   @  @                                           @@
;@@ @      @   @  @   @  @   @   @@@   @@@@@  FOR 24- AND 48-CHANNEL AC/DC  @@
;@@ @      @   @  @   @  @   @      @         LUMOS CONTROLLER UNITS        @@
;@@ @      @   @  @   @  @   @  @   @         BASED ON THE PIC18F4685 CHIP  @@
;@@ @@@@@   @@@   @   @   @@@    @@@                                        @@
;@@                                                                         @@
;@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
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
; Copyright (c) 2012, 2013, 2014 by Steven L. Willoughby, Aloha, Oregon, USA.  
; All Rights Reserved.  Released under the terms and conditions of the 
; Open Software License, version 3.0.
;
; Portions based on earlier code copyright (c) 2004, 2005, 2006, 2007
; Steven L. Willoughby, Aloha, Oregon, USA.  All Rights Reserved.
;
; -*- -*- -* -*- -*- -*- -*- -*- -*- -*- -*- -*- -*- -*- -* -*- -*- -*- -*- -*-
;
; Main implementation module.
;
#include "lumos_config.inc"
	RADIX	DEC
#include "lumos_init.inc"
#include "serial-io.inc"
	IF QSCC_PORT
#include "qscc_bits.inc"
#include "qscc_init.inc"
	 GLOBAL SSR_STATE
	 GLOBAL	S0_CMD0
	 GLOBAL	SSR_00_VALUE
	 GLOBAL	SSR_00_FLAGS
	 GLOBAL	SSR_00_STEP
	 GLOBAL	SSR_00_SPEED
	 GLOBAL	SSR_00_COUNTER
	 EXTERN QSCC_INIT
	 EXTERN QUIZSHOW_LCKTM
	ELSE
#include "flash_update.inc"
	ENDIF

; Works on Lumos 48-Channel controller boards 48CTL-3-1 with retrofit
; and 24SSR-DC-1.0.8 boards.
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
;    Both need reset signals.
;
; Serial control (RS-232 or RS-485) at 19.2kbps by default.
; Configurable from 300 to 250000 baud.
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
; . **  .  . RUN   Normal operations + privileged (config) mode enabled
; ! (*) X  X RUN   Received command for this unit
; X  X  !  X RUN   Master/Slave communications
; X  X  X  * RUN   Command error
; X  X  * ** RUN   Communications error (framing error)
; X  X ** ** RUN   Communications error (overrun error)
; X  X (*)** RUN   Communications error (buffer full error)
;** (*)**  . RUN   Internal error (exact error displayed on 2nd set of LEDs)*
; . () () () SLEEP Sleep Mode
; .  .  .  % HALT  System Halted normally
; ?  ?  ? ** HALT  Fatal error (exact error displayed on other LEDs)
;**  . ** ** HALT  Fatal error: reset/halt failure
;
; .=off  *=steady (*)=slowly fading on/off X=don't care
; ()=slow flash **=rapid flash !=blink/fade once (**)=rapid fade
; %=extra-slow flash
;
;
; *Internal error codes on 2nd LEDs (48-channel models only)
; A  G  Y  R
; C  R  E  E
; T  N  L  D MEANING
; ---------- -------
;-- **  .  . dispatch table overrun
;--  X  .  * input validator failure
;-- ** ** ** reset failure
;--  X  . ** device/hardware problem
;--  X  .(*) internal command error
;--  . **  . unknown/other error class
;-- 
;
; Error codes retrieved from query command
; 01  Command decode error (dispatch overrun)
; 02  Input validator failed to deal with bad value (channel number range for SET_LVL)
; 03  Input validator failed to deal with bad value (channel number range for BULK_UPD)
; 04  Input validator failed to deal with bad value (BULK_UPD data block scan)
; 05  Command decode error (dispatch overrun in S6 final command execution)
; 06  Input validator failed to deal with bad value (channel number range for RAMP_LVL)
; 07  Command decode error (dispatch overrun in S9 internal command execution)
; 08  Command decode error (illegal state transition in S10 for IC_TXDAT/IC_TXSTA)
; 09  Command impossible to carry out on this hardware (chip without T/R tried to take control of bus)
; 0A  Illegal internal command sent from master chip (invalid packet in S11 IC_TXDAT/IC_TXSTA)
; 0B  Command decode error (illegal state transition in S11 for IC_TXDAT/IC_TXSTA)
; 0C  Command decode error (illegal state transition in S12 for IC_LED)
; 0D  Command decode error (illegal state transition in S13 for IC_LED)
; 0E  Command decode error (extended dispatch overrun)
; 0F  Illegal internal command sent from master chip (received raw QUERY packet)
; 10  Could not determine device type                                  _
; 11  Command impossible to carry out on this hardware (chip without T/R tried to release control of bus)
; 12  Internal inter-CPU command executed on wrong class hardware
; 
; 20  Unrecognized command received or command arguments incorrect
; 21  Attempt to invoke privileged command from normal run mode
; 22  Command not yet implemented
; 23  Command received before previous one completed (previous command aborted)
; 70  CPU failed to reset with new configuration (execution bounds check)
; 71  CPU failed to halt when requested (execution bounds check)
;
; OPTION BUTTON:
; 
; Pres and hold the option button to enter field setup mode.  The lights will
; flash rapidly to signal this mode change.  Release the button and wait.  
; The lights will remain steady.  This enables the privileged 
; (configuration) command mode, allowing the Lumos unit to receive device 
; configuration commands from the host PC.
;
; Press the button again to enter self-test mode.  The LEDs will chase
; once to signal this mode.  In this mode, serial communication to the
; unit will be ignored.  Each output channel in turn will be turned on 
; for one second. The dimmer is NOT used, only fully on/fully off.  The
; LEDs on the top board will show the least-significant 4 bits of the
; output channel currently on.  If present, the bottom board's LEDs will
; show the most significant bits.
; 
; Pressing the button in this mode causes the cycle to pause on the current
; output channel until the button is pressed again to resume the cycle.
; 
; Pressing and holding the button will exit option mode and return to
; regular (but still privileged) run mode.  The host PC can issue a command
; to drop privileged mode, or the RESET button may be pressed to reset the
; system completely which includes disabling privileged mode.
; 
; ---TOP*---  --BOT--
; A  G  Y  R  G  Y  R
; C  R  E  E  R  E  E
; T  N  L  D  N  L  D  PHASE  MEANING
; -------------------  -----  -------
;** ** ** ** ** ** **  OPTION Entering option mode
; X **  X  X  X  X  X  OPTION Entered privileged run mode
;b3 b2 b1 b0 b5 b4 (*) OPTION Self-test mode (cycling)
;b3 b2 b1 b0 b5 b4  *  OPTION Self-test mode (paused)
;
; 24-channel models only have the top LEDs.  If sensors are installed
; in place of LEDs, some of these may not be present.
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
; FLASH_UPDATE
;	(flash_update.asm) Loader code to receive new firmware image over the
;	serial line and write it into the microcontroller's flash memory.
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
; Commands recognized:
;
;   COMMAND  CODE  BITS
;   BLACKOUT 0     1000aaaa
;   ON_OFF   1     1001aaaa 0scccccc		Turn channel <c> on (<s>=1) or off (<s>=0)
;   SET_LVL  2     1010aaaa 0hcccccc 0vvvvvvv    Set dimmer level <v>:<h> on channel <c>
;   BULK_UPD 3     1011aaaa 0mcccccc ...		Bulk-upload multiple channel levels
;   RAMP_LVL 4     1100aaaa Cdcccccc ...         Ramp channel <c> smoothly up (<d>=1) or down (<C>=1 cycle)
;            5     1101aaaa                      Reserved for future use
;            6     1110aaaa                      Reserved for future use
;   EXTENDED 7     1111aaaa                      Extended command, decoded further in next byte
; @ SLEEP    7+0   1111aaaa 00000000 01011010 01011010  Put unit to sleep
; @ WAKE     7+1   1111aaaa 00000001 01011010 01011010  Take unit out of sleep mode
;   SHUTDOWN 7+2   1111aaaa 00000010 01011000 01011001  Take unit completely offline
; < QUERY    7+3   1111aaaa 00000011 00100100 01010100  Report device status
;X! DEF_SEQ  7+4   1111aaaa 00000100 0iiiiiii ...       Define sequence <i>
;X  EXEC_SEQ 7+5   1111aaaa 00000101 0iiiiiii           Execute sequence <i> (0=stop)
;X  DEF_SENS 7+6   1111aaaa 00000110 ...                Define sensor trigger
;X  MSK_SENS 7+7   1111aaaa 00000111 0000ABCD           Mask inputs (1=enable, 0=disable)
;X! CLR_SEQ  7+8   1111aaaa 00001000 01000011 01000001  Erase all stored sequences
;   XPRIV    7+9   1111aaaa 00001001                    Forbid priviliged mode
;            7+10  1111aaaa 00001010                    Reserved for future use
;             :        :        :                           :     :     :    : 
;            7+29  1111aaaa 00011101                    Reserved for future use                 
;   OUT_NAK  7+30  1111aaaa 00011110                    QUERY NAK                               
;   OUT_RPLY 7+31  1111aaaa 00011111 ...                Reply to QUERY command_________________ 
;   IC_TXDAT 7+32  11110000 00100000 0nnnnnnn (...)*<n>+1 00011011 data -> serial port INTERNAL
;   IC_LED   7+33  11110000 00100001 00GGGYYY 00000RRR             LED Control         ////////
;   IC_HALT  7+34  11110000 00100010                               CPU Halt            ////////
;   IC_TXSTA 7+35  11110000 00100011 0nnnnnnn (...)*<n>+1 00011011 TXDAT + status+sent ////////
;            7+36  11110000 00100100                    Reserved for new commands      ////////
;             :        :        :                           :     :   :      :         ////////
;            7+63  11110000 00111111                    Reserved for new commands______////////
;*! CF_PHASE 7+64  1111aaaa 010000pp 0ppppppp 01010000 01001111   Phase offset=<p>       CONFIG
;*! CF_ADDR  7+96  1111aaaa 0110AAAA 01001001 01000001 01000100   Change address to <A>  ||||||
;*  CF_NOPRV 7+112 1111aaaa 01110000                              Leave privileged mode  ||||||
;*  CF_CONF  7+113 1111aaaa 01110001 ...                          Configure device       ||||||
;*! CF_BAUD  7+114 1111aaaa 01110010 0bbbbbbb 00100110            Set baud rate to <b>   ||||||
;*! CF_RESET 7+115 1111aaaa 01110011 00100100 01110010            Reset factory defaults ||||||
;*  CF_XPRIV 7+116 1111aaaa 01110100                              Forbid priviliged mode ||||||
;*  CF_FLROM 7+117 1111aaaa 01110101 00110011 01001100 00011100   Begin ROM update cycle ||||||
;*           7+118 1111aaaa 01110110                     Reserved for future config cmd  ||||||
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
; RAMP_LVL:  0dcccccc 0sssssss 0ttttttt   Channel <c> up/down in <s>+1 steps every <t>+1/120 sec
;
; DEF_SEQ:   0iiiiiii 0nnnnnnn (...)*<n+1> 01000100 01110011  Define sequence <i> of length <n+1>
;                                                             0 is boot sequence, 1-63 is EEPROM
;                                                             64-127 is RAM.
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
; CF_CONF:   0ABCDdcc 0ccccccc 00111010 00111101
;	Configure sensor lines ABCD as 1=sensor inputs or 0=LED outputs,
;	DMX mode if <d>=1, with Lumos channel 0 at DMX channel <c>+1.
;	
; CF_BAUD:   Values recognized:
;	00000000 ($00)        300 baud
;	00000001 ($01)        600
;	00000010 ($02)      1,200
;	00000011 ($03)      2,400
;	00000100 ($04)      4,800
;	00000101 ($05)      9,600
;	00000110 ($06)     19,200
;	00000111 ($07)     38,400
;	00001000 ($08)     57,600
;	00001001 ($09)    115,200
;	00001010 ($0A)    250,000
;	00001011 ($0B)    500,000
;	00001100 ($0C)  1,000,000
;	00001101 ($0D)  2,000,000
;	00001110 ($0E)  2,500,000
;	00001111 ($0F)  5,000,000
;	00010000 ($10) 10,000,000
;
;
; Response packet from QUERY command (37 bytes):
; note the ROM version byte also serves to indicate the format of the response
; bytes which follow.  If the query packet format changes, the ROM version byte
; MUST also change.
;
;    1111aaaa 00011111 00110001 0ABCDdcc 0ccccccc 0ABCDqsf 0ABCDXpp 0ppppppp 
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
; This version of the Lumos ROM does not send OUT_NAK packets.
;
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
;
;  __________ my   __________
; |17 |      |slot|18 |      |
; |___|      |--->|___|      |
; | DMX WAIT |<---| DMX UPD  |
; |__________| brk|__________|
;    ^  |nottype0       |done
;    |  V_______________V_____________________________________.
; brk|  |                                                     |
;  __|__V____      __________                                 |
; | 0 |      |    | 1 |      |                                |
; |___|      |--->|___|      |                                |
; |   IDLE   |<---| ON_OFF   |                                | 
; |__________|  ch|__________|                                |
;    ^  |          __________      ___                        |
;    |  |         | 2 |      |ch  |   |v                      |
;    |  |-------->|___|      |--->| 3 |---------------------->|
;    |  |         | SET_LVL  |    |___|                       |
;    |  |         |__________|                                |
;    |  |          __________      ___      ___               |
;    |  |         | 5 |      |ch  |   |s   |   |t             |
;    |  |-------->|___|      |--->| 7 |--->| 8 |------------->|
;    |  |         | RAMP_LVL |    |___|    |___|              |
;    |  |         |__________|                                |
;    |  |          __________                  __________     |
;    |  |         | 4 |      |ch              | 6 | Wait |    |
;    |  |-------->|___|      |--------------->|___|  for |--->|
;    |  |         | BULK_UPD |                | Sentinel |    |
;  __|__V____     |__________|                |__________|    |
; | 9 |      |                                      ^         |
; |___|      |                                      |         |
; | Extended |------------------------------------->|         |
; |__________|                                      |         |
;       |          __________                       |         |
;       |         |14 |      |i                     |         |
;       |-------->|___|      |----------------------'         |
;       |         | DEF_SEQ  |                                |
;       |         |__________|                                |
;       |          __________      ____                       |
;       |         |10 |      |N   |    |(done)                |
;       |-------->|___|      |--->| 11 |--------------------->|
;       |         | IC_TXDAT |    |____|                      |
;       |         | IC_TXSTA |                                |
;       |         |__________|                                |
;       |          __________      ____                       |
;       |         |12 |      |GY  |    |R                     |
;       |-------->|___|      |--->| 13 |--------------------->|
;       |         | IC_LED   |    |____|                      |
;       |         |__________|                                |
;       |          __________                                 |
;       |         |15 |      |i                               |
;       |-------->|___|      |------------------------------->|
;       |         | EXEC_SEQ |                                |
;       |         |__________|                                |
;       |          __________                                 |
;       |         |16 |      |m                               |
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
; or enough time for 83,333.333 instructions to be executed between each 
; interrupt.
;
; Slices  Time/slice (s)  Instructions/slice
;   1     0.00833333      83,333.333
;  32     0.00026042       2,604.167
;  64     0.00013021       1,302.083
; 128     0.00006510         651.042
; 132     0.00006313         631.313	128 levels + 2 on each end
; 260     0.00003205         320.513	256 levels + 2 on each end
;
; We divide the half-wave into "slices".  We need a minimum of 256 slices
; to get 256 levels of dimmer control, but we should add at least one on either
; end in case our timing's slightly off between the ZC points and the free-
; running timer.  For good measure, let's throw in a couple more to allow for
; pin settling times, minimum turn-on times for the triacs and just to be
; paranoid.  So let's say 260 slices per half-wave.  
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
; we'll start our working slices some variable fraction of 1/260th of a half-cycle
; each time.  This will cause a "wobble" in brightness level of not more than 
; 1/260th brightness level (something less than one brightness increment), which
; ought to be difficult or impossible to notice by looking at an incandescent
; light load.  This is one reason why PHASE_OFFSET should be set to allow 1-2
; idle slices before we start turning on SSRs.
;
; On ZC interrupt, we set CUR_PRE to PHASE_OFFSET and set <PRECYC>.
; On TMR2 interrupt, if SSR_STATE<PRECYC>, decrement CUR_PRE.
;   if zero, clear SSR_STATE<PRECYC>, set CUR_SLICE to 256, set <INCYC>,<DIM_START>.
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
; The 48-channel and 24-channel boards use the 18F4685 microcontroller 
; (LUMOS_ARCH == "4685"), while the 4-channel boards use the smaller
; 18F14K50 chip (LUMOS_ARCH == "14K50").
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
; |12345678|	1- Return Data Y (+)    5- Data A (+)
; |        |	2- Return Data Z (-)    6- Cable Check OUT
; |___  ___|	3- Cable Check IN   	7- Data GND 
;    |__|	4- Data B (-)		8- Return Data GND
;
; CC is a cable check indicator.  A signal is sent out by the host on pin 3, with the
; expectation that each controller will pass it on down the cable to the terminator
; which connects it to pin 6 and sends the signal back through the controllers to the
; host again.  Note that the controllers themselves do nothing with the CC signal other
; than pass those pins straight through; it is available however for something at the 
; host side to verify cable integrity.
;
; Data A/B is the twisted pair for the RS-485 data between the host PC and controllers.
;
; Return Data Y/Z is only implemented if a full duplex RS-485 network is implemented
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
;------------------------------------------------------------------------ 
;
;  PIC18F14K50 Microcontroller I/O pin assignments:
;
;         4-CH           ________   _________         4-CH
;         BOARD:        |o       \_/         |        BOARD: 
;            +5V ---  1 | Vdd            Vss | 20 --- GND    
;           XTAL ---  2 | OSC1       PGD RA0 | 19 --> /PWRCTL
;           XTAL ---  3 | OSC2       PGC RA1 | 18 <-- /OPTION
;          /MCLR -->  4 | /MCLR         Vusb | 17 
;    /A  ACT LED <->  5 | RC5            RC0 | 16 --> /SSR0
;        GRN LED <--  6 | RC4            RC1 | 15 --> /SSR1
;    /C  YEL LED <->  7 | RC3            RC2 | 14 --> /SSR2
;    /B  RED LED <->  8 | RC6            RB4 | 13 --> /SSR3
;    /D          -->  9 | RC7        RxD RB5 | 12 <-- RxD
;            TxD <-- 10 | RB7 TxD        RB6 | 11 --> T/R
;                       |____________________|
;
;
;
; ========================================================================
; PROGRAM MEMORY MAP
; ______________________________________________________________________________
; PIC18F14K50, 4-PORT BOARD
; 
;           ______________________________
; 00000000 | Restart vector               | V_RST
; 00000005 |______________________________|
; 00000006 |                              | .cinit
; 00000007 |______________________________|
; 00000008 | High-priority interrupt      | V_INT_H
;          | vector                       |
; 0000000D |______________________________|
;     :     ______________________________
; 00000018 | Low-priority interrupt       | V_INT_L
;          | vector                       |
; 0000001D |______________________________|
; 0000001E | Interrupt service routines   | _INT
; 000000A5 |______________________________|
;     :     ______________________________
; 00000100 | Cold-start boot loader:      | _BOOT
;          | initialize system            |
; 00000333 |______________________________|
; 00000334 | Serial I/O routines          | _SIO_CODE
; 000005C5 |______________________________|
;     :     ______________________________
; 00000800 | Mainline Lumos firmware      | _MAIN
;          | routines                     |
; 00001C4F |______________________________|
;     :     ______________________________
; 00002E00 | Factory default settings     | _EEPROM_DEFS_TBL
; 00002E0F |______________________________|
; 00002E10 | System initialization code   | LUMOS_CODE_INIT
;          | (called from boot code)      |
; 00002E97 |______________________________|
;     :     ______________________________
; 00002F00 |                              | .org_0
; 00002FBD |______________________________|
;     :     ______________________________
; 00002FE0 | Manufacturing information    | __SYS__
;          | (serial number)              |
; 00002FE1 |______________________________|
;     :     ______________________________
; 00003000 | Field firmware update        | _FLASH_UPD
;          | routine                      |
; 000032F5 |______________________________|
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
; $03000 $17000 |Flash Loader Code| _FLASH_UPDATE_LOADER
; $03FFF $17FFF |_________________|___
;               |/////////////////|
;               |/////////////////|
;$1FFFFF$1FFFFF |/////////////////|___
;
 IF LUMOS_ARCH == LUMOS_ARCH_4685
_MAIN_EEPROM_TBL	EQU	0x14000
_SYSTEM_MFG_DATA	EQU	0x16FF0
 ELSE
  IF LUMOS_ARCH == LUMOS_ARCH_14K50
_MAIN_EEPROM_TBL	EQU	0x02E00
_SYSTEM_MFG_DATA	EQU	0x02FE0
  ELSE
   ERROR "Invalid architecture switch"
  ENDIF
 ENDIF
;
;
; ========================================================================
;
; PIC18F14K50, 4-channel board:
;      ______________________________
; 000 | 000 ISR_TMPL_STATUS          | _ADATA
;     | 001 ISR_TMPL_BSR             |
;     | 002 ISR_TMPL_WREG            |
;     | 003 MY_ADDRESS               |
;     | 004 PHASE_OFFSETH            |
;     | 005 PHASE_OFFSETL            |
;     | 006 SSR_STATE                |
;     | 007 SSR_STATE2               |
;     | 008 DMX_SLOTH                |
;     | 009 DMX_SLOTL                |
;     | 00A YY_STATE                 |
;     | 00B YY_COMMAND               |
;     | 00C YY_CMD_FLAGS             |
;     | 00D YY_DATA                  |
;     | 00E YY_LOOKAHEAD_MAX         |
;     | 00F YY_LOOK_FOR              |
;     | 010 YY_BUF_IDX               |
;     | 011 YY_NEXT_STATE            |
;     | 012 YY_YY                    |
;     | 013 LAST_ERROR               |
;     | 014 CUR_PREH                 |
;     | 015 CUR_PRE                  |
;     | 016 CUR_SLICE                |
;     | 017 TARGET_SSR               |
;     | 018 OPTION_DEBOUNCE          |
;     | 019 OPTION_HOLD              |
;     | 01A TEST_CYCLE               |
;     | 01B TEST_SSR                 |
;     | 01C AUTO_OFF_CTRH            |
;     | 01D AUTO_OFF_CTRL            |
;     | 01E EIGHTBITSIOBUF           |
;     | 01F I                        |
;     | 020 J                        |
;     | 021 K                        |
;     | 022 KK                       |
;     | 023 TR_I                     |
; 023 |______________________________|
;  :   ______________________________
; 060 | 060 SSR_00_VALUE             | _SSR_DATA
;     | 068 SSR_00_FLAGS             |
;     | 070 SSR_00_STEP              |
;     | 078 SSR_00_SPEED             |
;     | 080 SSR_00_COUNTER           |
; 087 |______________________________|
; 088 | 088 YY_BUFFER                | _MAINDATA
; 0E1 |______________________________|
;  :   ______________________________
; 0E4 | 0E4 SIO_STATUS               | _SIO_VAR_DATA
;     | 0E5 SIO_INPUT                |
;     | 0E6 SIO_OUTPUT               |
;     | 0E7 TX_BUF_START             |
;     | 0E8 TX_BUF_END               |
;     | 0E9 RX_BUF_START             |
;     | 0EA RX_BUF_END               |
;     | 0EB TX_CHAR                  |
;     | 0EC SIO_X                    |
;     | 0ED SIO_TMPPC                |
;     | 0EE FSR1H_SAVE               |
;     | 0EF FSR1L_SAVE               |
;     | 0F0 B32__BIT                 |
;     | 0F1 B32__OUTCTR              |
;     | 0F2 B32__FSR0H               |
;     | 0F3 B32__FSR0L               |
;     | 0F4 B32__FSR1H               |
;     | 0F5 B32__FSR1L               |
;     | 0F6 B32__BCD_ASC             |
;     | 0FB B32__BIN                 |
; 0FE |______________________________|
;  :   ______________________________
; 100 | 100 TX_BUFFER                | _SIO_TXBUF_DATA
; 1FF |______________________________|
; 200 | 200 RX_BUFFER                | _SIO_RXBUF_DATA
; 2FF |______________________________|
;

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
; ------------------------------------------------------------------------
; DATA MEMORY MAP (14K50)
;
;       _________________ ___ ___ ___ ___ ___ ___ ___ ___
; $000 | global state,   | _ADATA            BANK 0
; $022 | ISR data, etc.  |                (ACCESS AREA)
;      |.................|
; $023 |                 |                   
;      |                 |                   
; $05F |_________________|...............................
; $060 | SSR state data  | _SSR_DATA         BANK 0
;      |                 |                (BANKED AREA)
; $07F |_________________|
; $088 | Parser buffer   | _MAINDATA
; $0E1 |.................|
; $0E2 |    [unused]     |
; $0E3 |_________________|
; $0E4 | Serial I/O mod  | _SIO_VAR_DATA
;      | variable space  |
; $0FF |_________________|___ ___ ___ ___ ___ ___ ___ ___
; $100 | Serial I/O TxD  | _SIO_TXBUF_DATA   BANK 1
;      | ring buffer     |
; $1FF |_________________|___ ___ ___ ___ ___ ___ ___ ___
; $200 | Serial I/O RxD  | _SIO_RXBUF_DATA   BANK 2
;      | ring buffer     |
; $2FF |_________________|___ ___ ___ ___ ___ ___ ___ ___
; $300 |/////////////////|///////////////////////////////
;      |/////////////////|
;              .
;              .                 
;              .                DOES NOT EXIST
;      |/////////////////|
;      |/////////////////|
; $EFF |/////////////////|///////////////////////////////
; $F00 |/////////////////|                   
; $F52 |/////////////////|
; $F53 | Special Function|
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
__SYS__	CODE_PACK	_SYSTEM_MFG_DATA
SYS_SNH	DE	0xA5	 	; Device serial number
SYS_SNL DE	0xA0

_EEPROM	CODE_PACK	0xF00000
	DE	0xFF		; 000: 0xFF constant
	DE	SIO_19200	; 001: baud rate default
	DE	0x00    	; 002: default device ID
	DE	0x00, 0x02	; 003: default phase offset
	DE	0x00, 0x00      ; 005: default DMX=0 (disabled, ch=1)
	DE	0x00  		; 007: default sensors (disabled)
	DE	0x00, 0x00	; 008: reserved
	DE	0x00, 0x00, 0x00; 00A: reserved
	DE	0x00, 0x00      ; 00D: reserved
	DE	0x42		; 00F: sentinel

EE_START	EQU	0x000
EE_BAUD		EQU	0x001
EE_DEV_ID	EQU	0x002
EE_PHASE_H	EQU	0x003
EE_PHASE_L	EQU	0x004
EE_DMX_H	EQU	0x005
EE_DMX_L	EQU	0x006
EE_SENSOR_CFG	EQU	0x007
EE_RESERVED_8	EQU	0x008
EE_RESERVED_9	EQU	0x009
EE_RESERVED_A	EQU	0x00A
EE_RESERVED_B	EQU	0x00B
EE_RESERVED_C	EQU	0x00C
EE_RESERVED_D	EQU	0x00D
EE_RESERVED_E	EQU	0x00E
EE_END        	EQU	0x00F

_EEPROM_DEFS_TBL CODE_PACK _MAIN_EEPROM_TBL
DEFAULT_TBL:
	DB	0xFF			; $000: constant $FF
	DB	SIO_19200		; $001: 19200 baud
	DB	0x00			; $002: device ID=0
	DB	0x00, 0x02		; $003: phase offset=2
	DB	0x00, 0x00            	; $005: DMX slot=0 (disabled, ch=1)
	DB	0x00  			; $007: no sensors configured
	DB 	0x00, 0x00, 0x00	; $008-$00A
	DB 	0x00, 0x00, 0x00, 0x00	; $00B-$00E
	DB	0x42			; $00F: constant $42

EEPROM_SETTINGS_LEN	EQU	.16
EEPROM_USER_START	EQU	0x010	
EEPROM_USER_END		EQU	0x3FF
;
; ========================================================================
; DEVICES USED
;
; TMR0    120 Hz interrupt source (for boards without zero-crossing detector)
; TMR1    Button press timer (free-running 1MHz clock)
; TMR2    Dimmer slice timer (1/260 of a 120 Hz half-cycle)
; TMR3	  Break detector for DMX reception
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
; PORT RA /////// --- --- --- /// /OP /PS     4-Board DC
;         ///////  <OSC>   I  ///  I   O
;
;          7   6   5   4   3   2   1   0
; PORT RB /PS /OP /15 /13 /11 /09 /07 ---    48-Board AC/DC master
;          O   I   O   O   O   O   O  INT
; PORT RB /PS --- /15 /13 /11 /09 /07 ---    48-Board AC/DC slave
;          O   O   O   O   O   O   O  INT
; PORT RB /PS /OP /00 /01 /02 /03 /04 T/R    24-Board DC    standalone
;          O   I_  O   O   O   O   O   O 
; PORT RB --- T/R --- /03 ///////////////     4-Board DC
;         <O>  O  <I>  O  ///////////////
;
;          7   6   5   4   3   2   1   0
; PORT RC --- --- /02 /00 /01 /03 /19 /04    48-Board AC/DC master/slave
; PORT RC --- --- /09 /10 /15 /16 /17 /18    24-Board DC    standalone
;          <I/O>   O   O   O   O   O   O
; PORT RC /D  RED ACT GRN YEL /02 /01 /00     4-Board DC
;          I   O   O   O   O   O   O   O
;
;          7   6   5   4   3   2   1   0
; PORT RD /17 /06 /05 /18 /22 /20 /21 /23    48-Board AC/DC master/slave
; PORT RD /05 /06 /07 /08 /11 /12 /13 /14    24-Board DC    standalone
;         ///////////////////////////////     4-Board DC
;          O   O   O   O   O   O   O   O
;
;          7   6   5   4   3   2   1   0
; PORT RE --- --- --- --- --- RED YEL GRN    All boards
;         ///////////////////////////////     4-Board DC
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
#include "lumos_ssr_state.inc"

; YY_CMD_FLAGS holds various command flag bits
;
YCF_RAMP_CYCLE	EQU	7	; 1-------  Ramp should cycle now
				; -XXXXXXX  Unassigned
;
; DMX_SLOTH contains these flags and the high-order bit of the DMX channel
;
	IF DMX_ENABLED
DMX_EN		EQU	7	; 1-------  DMX mode enabled
DMX_SPEED	EQU	6	; -1------  UART at DMX speed now
DMX_FRAME	EQU	5	; --1-----  Start of frame detected
;            			; ---XXXX-  Reserved
DMX_BIT8	EQU	0	; -------1  MSB of DMX channel
	ENDIF

;
; TARGET_SSR has these flags:
;                     _______________________________________________________
; TARGET_SSR         |NOT_MY|INVALI|                                         |
;                    | _SSR |D_SSR |    SSR number for current command       |
;                    |______|______|______|______|______|______|______|______|
;
NOT_MY_SSR	EQU	7
INVALID_SSR	EQU	6		; MUST be bit 6
TARGET_SSR_MSK	EQU	0x3F


;
; CHIP-SPECIFIC PORT/PIN MAPPINGS
;
; 48-Channel board (master CPU)
;
		IF LUMOS_CHIP_TYPE == LUMOS_CHIP_MASTER
PORT_RX		 EQU	PORTC
BIT_RX		 EQU	7

HAS_T_R		 EQU	0
HAS_ACTIVE	 EQU	1
HAS_SENSORS	 EQU	1
HAS_OPTION	 EQU	1
HAS_STATUS_LEDS	 EQU	1
HAS_POWER_CTRL	 EQU	1

TRIS_SENS_A	 EQU	TRISE	; Sensor A == RED LED
PORT_SENS_A	 EQU	PORTE	; Sensor A == RED LED
BIT_SENS_A	 EQU	2	; Sensor A == RED LED
TRIS_SENS_B	 EQU	TRISE	; Sensor B == GREEN LED
PORT_SENS_B	 EQU	PORTE	; Sensor B == GREEN LED
PLAT_SENS_B	 EQU	LATE	; Sensor B == GREEN LED
BIT_SENS_B	 EQU	0	; Sensor B == GREEN LED
TRIS_SENS_C	 EQU	TRISA	; Sensor C == ACTIVE LED
PORT_SENS_C	 EQU	PORTA	; Sensor C == ACTIVE LED
BIT_SENS_C	 EQU	5	; Sensor C == ACTIVE LED
TRIS_SENS_D	 EQU	TRISE	; Sensor D == YELLOW LED
PORT_SENS_D	 EQU	PORTE	; Sensor D == YELLOW LED
BIT_SENS_D	 EQU	1	; Sensor D == YELLOW LED

PLAT_ACTIVE	 EQU	LATA
PLAT_RED	 EQU	LATE
PLAT_YELLOW	 EQU	LATE
PLAT_GREEN	 EQU	LATE
BIT_ACTIVE	 EQU	5
BIT_RED		 EQU	2
BIT_YELLOW	 EQU	1
BIT_GREEN	 EQU	0

PORT_OPTION	 EQU	PORTB
BIT_OPTION	 EQU	6

PLAT_PWR_ON	 EQU	LATB
BIT_PWR_ON	 EQU	7

PLAT_0		 EQU	LATC
PLAT_1		 EQU	LATC
PLAT_2		 EQU	LATC
PLAT_3		 EQU	LATC
PLAT_4		 EQU	LATC
PLAT_5		 EQU	LATD
PLAT_6		 EQU	LATD
PLAT_7		 EQU	LATB
PLAT_8		 EQU	LATA
PLAT_9		 EQU	LATB
PLAT_10		 EQU	LATA
PLAT_11		 EQU	LATB
PLAT_12		 EQU	LATA
PLAT_13		 EQU	LATB
PLAT_14		 EQU	LATA
PLAT_15		 EQU	LATB
PLAT_16		 EQU	LATA
PLAT_17		 EQU	LATD
PLAT_18		 EQU	LATD
PLAT_19		 EQU	LATC
PLAT_20		 EQU	LATD
PLAT_21		 EQU	LATD
PLAT_22		 EQU	LATD
PLAT_23		 EQU	LATD

BIT_0		 EQU	4
BIT_1		 EQU	3
BIT_2		 EQU	5
BIT_3		 EQU	2
BIT_4		 EQU	0
BIT_5		 EQU	5
BIT_6		 EQU	6
BIT_7		 EQU	1
BIT_8		 EQU	4
BIT_9		 EQU	2
BIT_10		 EQU	3
BIT_11		 EQU	3
BIT_12		 EQU	2
BIT_13		 EQU	4
BIT_14		 EQU	1
BIT_15		 EQU	5
BIT_16		 EQU	0
BIT_17		 EQU	7
BIT_18		 EQU	4
BIT_19		 EQU	1
BIT_20		 EQU	2
BIT_21		 EQU	1
BIT_22		 EQU	3
BIT_23		 EQU	0

SSR_LIGHTS	 EQU	24	; first light ID (as opposed to SSR)
		ELSE
 		 IF LUMOS_CHIP_TYPE == LUMOS_CHIP_SLAVE
;
; 48-Channel Board (slave CPU)
;
PORT_RX		  EQU	PORTC
BIT_RX		  EQU	7

HAS_T_R		  EQU	1
HAS_ACTIVE	  EQU	0
HAS_SENSORS	  EQU	0
HAS_OPTION	  EQU	0
HAS_STATUS_LEDS	  EQU	1
HAS_POWER_CTRL	  EQU	1

PLAT_T_R	  EQU	LATA
PORT_T_R	  EQU	PORTA
TRIS_T_R	  EQU	TRISA
BIT_T_R		  EQU	5

PLAT_RED	  EQU	LATE
PLAT_YELLOW	  EQU	LATE
PLAT_GREEN	  EQU	LATE

BIT_RED		  EQU	2
BIT_YELLOW	  EQU	1
BIT_GREEN	  EQU	0

PLAT_PWR_ON	  EQU	LATB
BIT_PWR_ON	  EQU	7

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

SSR_LIGHTS  	  EQU	24	; first light ID (as opposed to SSR)
		 ELSE
		  IF LUMOS_CHIP_TYPE == LUMOS_CHIP_STANDALONE
;
; 24-Channel board (Standalone CPU)
;
PORT_RX		   EQU	PORTC
BIT_RX		   EQU	7

HAS_T_R		   EQU	1
HAS_ACTIVE	   EQU	1
HAS_SENSORS	   EQU	1
HAS_OPTION	   EQU	1
HAS_STATUS_LEDS	   EQU	1
HAS_POWER_CTRL	   EQU	1

TRIS_SENS_A	   EQU	TRISE	; Sensor A == RED LED
PORT_SENS_A	   EQU	PORTE	; Sensor A == RED LED
BIT_SENS_A	   EQU	2	; Sensor A == RED LED
TRIS_SENS_B	   EQU	TRISE	; Sensor B == GREEN LED
PORT_SENS_B	   EQU	PORTE	; Sensor B == GREEN LED
PLAT_SENS_B	   EQU	LATE	; Sensor B == GREEN LED
BIT_SENS_B	   EQU	0	; Sensor B == GREEN LED
TRIS_SENS_C	   EQU	TRISA	; Sensor C == ACTIVE LED
PORT_SENS_C	   EQU	PORTA	; Sensor C == ACTIVE LED
BIT_SENS_C	   EQU	5	; Sensor C == ACTIVE LED
TRIS_SENS_D	   EQU	TRISE	; Sensor D == YELLOW LED
PORT_SENS_D	   EQU	PORTE	; Sensor D == YELLOW LED
BIT_SENS_D	   EQU	1	; Sensor D == YELLOW LED

PLAT_T_R	   EQU	LATB
PORT_T_R	   EQU	PORTB
TRIS_T_R	   EQU	TRISB
BIT_T_R		   EQU	0

PLAT_ACTIVE	   EQU	LATA
PLAT_RED	   EQU	LATE
PLAT_YELLOW	   EQU	LATE
PLAT_GREEN	   EQU	LATE
BIT_ACTIVE	   EQU	5
BIT_RED		   EQU	2
BIT_YELLOW	   EQU	1
BIT_GREEN	   EQU	0

PORT_OPTION	   EQU	PORTB
BIT_OPTION	   EQU	6

PLAT_PWR_ON	   EQU	LATB
BIT_PWR_ON	   EQU	7

PLAT_0		   EQU	LATB
PLAT_1		   EQU	LATB
PLAT_2		   EQU	LATB
PLAT_3		   EQU	LATB
PLAT_4		   EQU	LATB
PLAT_5		   EQU	LATD
PLAT_6		   EQU	LATD
PLAT_7		   EQU	LATD
PLAT_8		   EQU	LATD
PLAT_9		   EQU	LATC
PLAT_10		   EQU	LATC
PLAT_11		   EQU	LATD
PLAT_12		   EQU	LATD
PLAT_13		   EQU	LATD
PLAT_14		   EQU	LATD
PLAT_15		   EQU	LATC
PLAT_16		   EQU	LATC
PLAT_17		   EQU	LATC
PLAT_18		   EQU	LATC
PLAT_19		   EQU	LATA
PLAT_20		   EQU	LATA
PLAT_21		   EQU	LATA
PLAT_22		   EQU	LATA
PLAT_23		   EQU	LATA

BIT_0		   EQU	5
BIT_1		   EQU	4
BIT_2		   EQU	3
BIT_3		   EQU	2
BIT_4		   EQU	1
BIT_5		   EQU	7
BIT_6		   EQU	6
BIT_7		   EQU	5
BIT_8		   EQU	4
BIT_9		   EQU	5
BIT_10		   EQU	4
BIT_11		   EQU	3
BIT_12		   EQU	2
BIT_13		   EQU	1
BIT_14		   EQU	0
BIT_15		   EQU	3
BIT_16		   EQU	2
BIT_17		   EQU	1
BIT_18		   EQU	0
BIT_19		   EQU	4
BIT_20		   EQU	3
BIT_21		   EQU	2
BIT_22		   EQU	1
BIT_23		   EQU	0

SSR_LIGHTS	   EQU	24	; first light ID (as opposed to SSR)
		  ELSE
    		   IF LUMOS_CHIP_TYPE == LUMOS_CHIP_4CHANNEL
;
; 4-Channel Board (Mini Standalone CPU)
;
PORT_RX		    EQU	PORTB
BIT_RX		    EQU	5

HAS_T_R		    EQU	1
HAS_ACTIVE	    EQU	1
HAS_SENSORS	    EQU	1
HAS_OPTION	    EQU	1
HAS_STATUS_LEDS	    EQU	1
HAS_POWER_CTRL	    EQU	0

TRIS_SENS_A	    EQU	TRISC	; Sensor A == ACTIVE LED
PORT_SENS_A	    EQU	PORTC	; Sensor A == ACTIVE LED
BIT_SENS_A	    EQU	5	; Sensor A == ACTIVE LED
TRIS_SENS_B	    EQU	TRISC	; Sensor B == RED LED
PORT_SENS_B	    EQU	PORTC	; Sensor B == RED LED
PLAT_SENS_B	    EQU	LATC 	; Sensor B == RED LED
BIT_SENS_B	    EQU	6	; Sensor B == RED LED
TRIS_SENS_C	    EQU	TRISC	; Sensor C == YELLOW LED
PORT_SENS_C	    EQU	PORTC	; Sensor C == YELLOW LED
BIT_SENS_C	    EQU	3	; Sensor C == YELLOW LED
TRIS_SENS_D	    EQU	TRISC	; Sensor D
PORT_SENS_D	    EQU	PORTC	; Sensor D
BIT_SENS_D	    EQU	7	; Sensor D

PLAT_T_R	    EQU	LATB
PORT_T_R	    EQU	PORTB
TRIS_T_R	    EQU	TRISB
BIT_T_R		    EQU	6

PLAT_ACTIVE	    EQU	LATC
PLAT_RED	    EQU	LATC
PLAT_YELLOW	    EQU	LATC
PLAT_GREEN	    EQU	LATC
BIT_ACTIVE	    EQU	5
BIT_RED		    EQU	6
BIT_YELLOW	    EQU	3
BIT_GREEN	    EQU	4

PORT_OPTION	    EQU	PORTA
BIT_OPTION	    EQU	1

PLAT_PWR_ON	    EQU	LATA	; This doesn't actually reach the hardware
BIT_PWR_ON	    EQU	0	; but it's harmless to set the bit.

PLAT_0		    EQU	LATC
PLAT_1		    EQU	LATC
PLAT_2		    EQU	LATC
PLAT_3		    EQU	LATB

BIT_0		    EQU	0
BIT_1		    EQU	1
BIT_2		    EQU	2
BIT_3		    EQU	4

SSR_LIGHTS	    EQU	4	; first light ID (as opposed to SSR)
                   ELSE
		    IF QSCC_PORT
		     #include "qscc_hook_main_pins.inc"
                    ELSE
     		     ERROR "Invalid platform select"
		    ENDIF
   		   ENDIF
  		  ENDIF
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
			IF	HAS_STATUS_LEDS
SSR_GREEN	 	 EQU	SSR_LIGHTS+0	; NOTE These are positive-logic, not negative like SSRs
SSR_YELLOW	 	 EQU	SSR_LIGHTS+1
SSR_RED		 	 EQU	SSR_LIGHTS+2
;
;
; Aliases for macro expansion (continues SSR numbering into these too)
;
PLAT_#v(SSR_RED) 	 EQU	PLAT_RED
PLAT_#v(SSR_YELLOW) 	 EQU	PLAT_YELLOW
PLAT_#v(SSR_GREEN) 	 EQU	PLAT_GREEN
BIT_#v(SSR_RED)		 EQU	BIT_RED
BIT_#v(SSR_YELLOW) 	 EQU	BIT_YELLOW
BIT_#v(SSR_GREEN) 	 EQU	BIT_GREEN
;
;
		 	 IF HAS_ACTIVE
SSR_ACTIVE	  	  EQU	SSR_LIGHTS+3
PLAT_#v(SSR_ACTIVE) 	  EQU	PLAT_ACTIVE
BIT_#v(SSR_ACTIVE) 	  EQU	BIT_ACTIVE
SSR_MAX		  	  EQU	SSR_LIGHTS+3
		 	 ELSE
SSR_MAX		  	  EQU	SSR_LIGHTS+2
		 	 ENDIF
			ENDIF

			IF HAS_STATUS_LEDS
OUTPUT_CHAN_MAX		 EQU	SSR_LIGHTS-1
			ELSE
OUTPUT_CHAN_MAX		 EQU	SSR_MAX
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

ERR_CLASS_OVERRUN	EQU	1	; ID dispatch overrun
ERR_CLASS_IN_VALID	EQU	2	; Input validation failure
ERR_CLASS_FATAL_RESET	EQU	3	; reset failure
ERR_CLASS_DEVICE	EQU	4	; hardware issue
ERR_CLASS_INT_COMMAND	EQU	5	; internal command invalid
ERR_BUG	MACRO	ERR_CODE, ERR_CLASS
	 MOVLW	ERR_CODE
	 MOVWF	LAST_ERROR, ACCESS
	 IF HAS_ACTIVE
	  SET_SSR_RAPID_FLASH SSR_ACTIVE
	 ENDIF
	 IF HAS_STATUS_LEDS
	  SET_SSR_RAPID_FLASH SSR_YELLOW
	  IF ERR_CLASS == ERR_CLASS_FATAL_RESET
	   SET_SSR_RAPID_FLASH SSR_RED
	   SET_SSR_OFF SSR_GREEN
	  ELSE
	   SET_SSR_OFF SSR_RED
	  ENDIF
	 ENDIF
	 IF ROLE_MASTER
	  ; Send extra flags to slave
	  MOVLW	0xF0
	  CALL	SIO_WRITE_W
	  MOVLW	0x21
	  CALL	SIO_WRITE_W
	  IF ERR_CLASS == ERR_CLASS_OVERRUN
     	   MOVLW B'00101000'
	   CALL	SIO_WRITE_W
	   MOVLW B'00000000'
	  ELSE
  	   IF ERR_CLASS == ERR_CLASS_IN_VALID
	    MOVLW B'00111000'
	    CALL SIO_WRITE_W
	    MOVLW B'00000001'
	   ELSE
	    IF ERR_CLASS == ERR_CLASS_FATAL_RESET
	     MOVLW B'00101101'
	     CALL SIO_WRITE_W
	     MOVLW B'00000101'
	    ELSE
             IF ERR_CLASS == ERR_CLASS_DEVICE
	      MOVLW B'00111000'
	      CALL SIO_WRITE_W
	      MOVLW B'00000101'
	     ELSE
	      IF ERR_CLASS == ERR_CLASS_INT_COMMAND
	       MOVLW B'00111000'
	       CALL SIO_WRITE_W
	       MOVLW B'00000110'
	      ELSE
	       MOVLW B'00000101'
	       CALL  SIO_WRITE_W
	       MOVLW B'00000000'
	      ENDIF
	     ENDIF
	    ENDIF
	   ENDIF
	  ENDIF
	  CALL SIO_WRITE_W
	 ENDIF
	 CLRF	YY_STATE, ACCESS
	 RETURN
	ENDM

#include "lumos_set_ssr.inc"
#include "lumos_8bit_escapes.inc"

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
	IF HAS_STATUS_LEDS
	 BSF	PLAT_RED, BIT_RED, ACCESS
	 RCALL	DELAY_1_6_SEC
	 BSF	PLAT_GREEN, BIT_GREEN, ACCESS
	 RCALL	DELAY_1_6_SEC
	
	 BCF	PLAT_RED, BIT_RED, ACCESS
	 RCALL	DELAY_1_6_SEC
	 BCF	PLAT_GREEN, BIT_GREEN, ACCESS
	 RCALL	DELAY_1_6_SEC
	ENDIF
	RETURN

D_FLASH:
	IF HAS_STATUS_LEDS
	 BSF	PLAT_RED, BIT_RED, ACCESS
	 RCALL	DELAY_1_12_SEC
	 BSF	PLAT_GREEN, BIT_GREEN, ACCESS
	 RCALL	DELAY_1_12_SEC
	 BSF	PLAT_YELLOW, BIT_YELLOW, ACCESS
	 RCALL	DELAY_1_12_SEC
	 IF HAS_ACTIVE
	  BSF	PLAT_ACTIVE, BIT_ACTIVE, ACCESS
	  RCALL	DELAY_1_12_SEC
	 ENDIF
	
	 BCF	PLAT_RED, BIT_RED, ACCESS
	 RCALL	DELAY_1_12_SEC
	 BCF	PLAT_GREEN, BIT_GREEN, ACCESS
	 RCALL	DELAY_1_12_SEC
	 BCF	PLAT_YELLOW, BIT_YELLOW, ACCESS
	 RCALL	DELAY_1_12_SEC
	 IF HAS_ACTIVE
	  BCF	PLAT_ACTIVE, BIT_ACTIVE, ACCESS
	  RCALL	DELAY_1_12_SEC
	 ENDIF
	ENDIF
	RETURN

START:
	CLRWDT
	CLRF	STKPTR, ACCESS		; clear stack error bits, set SP=0
	CALL	LUMOS_INIT
	IF ! HAS_SENSORS && !QSCC_PORT
	 BCF	TRIS_SENS_A, BIT_SENS_A, ACCESS		; If this device can't possibly
	 BCF	TRIS_SENS_B, BIT_SENS_B, ACCESS		; support sensor inputs, enable outputs
	 BCF	TRIS_SENS_C, BIT_SENS_C, ACCESS		; on those pins early to let the LEDs
	 BCF	TRIS_SENS_D, BIT_SENS_D, ACCESS		; work ASAP.
	ENDIF
	IF 0
	;
	; Extra start-up delay to investigate boot bug
	;
	MOVLW	.10
	MOVWF	I, ACCESS
SSS_SSS:
	CLRWDT
	CALL	S_FLASH
	DECFSZ	I, F, ACCESS
	BRA	SSS_SSS
        ENDIF
	;
	CALL	D_FLASH
	CALL	SIO_INIT		; call after other TRIS bits set
	;
	; Get EEPROM settings
	;
	IF HAS_STATUS_LEDS
	 BSF	PLAT_RED, BIT_RED, ACCESS	; Panel: () () () R
	ENDIF
	;
	; Test sentinel values $000==$FF and $00F==$42.
	; If they are not there, do a full factory reset of those
	; settings to restore something that we know will work.
	;
	CLRWDT
        IF LUMOS_ARCH == LUMOS_ARCH_14K50
	 CLRF	EEADR, ACCESS		; (note interrupts are still off now)
	ELSE
	 CLRF	EEADRH, ACCESS		; EEPROM location $000
	 CLRF	EEADR, ACCESS		; (note interrupts are still off now)
        ENDIF
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
	IF HAS_STATUS_LEDS
	 BCF	PLAT_RED, BIT_RED, ACCESS	
	 BSF	PLAT_YELLOW, BIT_YELLOW, ACCESS	; Panel: () () Y ()
	ENDIF
	;
	BCF	EECON1, WREN, ACCESS	; Read (not write) access to memory
	BCF	EECON1, EEPGD, ACCESS	; Select access to DATA area
	BCF	EECON1, CFGS, ACCESS
	;
        IF LUMOS_ARCH != LUMOS_ARCH_14K50
	 CLRF	EEADRH, ACCESS
	ENDIF
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
	INCF	EEADR, F, ACCESS	; EEPROM location 0x005: DMX slot MSB
	BSF	EECON1, RD, ACCESS
	MOVFF	EEDATA, DMX_SLOTH
	;
	INCF	EEADR, F, ACCESS	; EEPROM location 0x006: DMX slot LSB
	IF DMX_ENABLED
	 BSF	EECON1, RD, ACCESS
	 MOVFF	EEDATA, DMX_SLOTL
	 BCF	DMX_SLOTH, DMX_SPEED, ACCESS	; clear flag (we're not running at DMX speed yet)
	ENDIF
	;
	INCF	EEADR, F, ACCESS	; EEPROM location 0x007: Sensor Configuration
	IF HAS_SENSORS
	 BSF	EECON1, RD, ACCESS
	 BTFSS	EEDATA, 3, ACCESS
	 BCF	TRIS_SENS_A, BIT_SENS_A, ACCESS
	 BTFSS	EEDATA, 2, ACCESS
	 BCF	TRIS_SENS_B, BIT_SENS_B, ACCESS
	 BTFSS	EEDATA, 1, ACCESS
	 BCF	TRIS_SENS_C, BIT_SENS_C, ACCESS
	 BTFSS	EEDATA, 0, ACCESS
	 BCF	TRIS_SENS_D, BIT_SENS_D, ACCESS
 	ENDIF
	;
	CLRF	EEADR, ACCESS	; Leave pointer at 0x000
	;
	IF HAS_STATUS_LEDS
	 BSF	PLAT_GREEN, BIT_GREEN, ACCESS	; Panel: () G Y ()
	ENDIF
	;
	BCF	IPR1, TXIP, ACCESS	; TxD interrupt = low priority
	BCF	IPR1, RCIP, ACCESS	; RxD interrupt = low priority
	CLRWDT
	;
	; Initialize data structures
	;
	CLRF	SSR_STATE, ACCESS
	CLRF	SSR_STATE2, ACCESS
	CLRF	YY_STATE, ACCESS
	;
	MOVLW	.128
	MOVWF	OPTION_DEBOUNCE, ACCESS
	CLRF	OPTION_HOLD, ACCESS
	SETF	AUTO_OFF_CTRH, ACCESS
	SETF	AUTO_OFF_CTRL, ACCESS
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
	IF HAS_STATUS_LEDS
	 BSF	PLAT_RED, BIT_RED, ACCESS	; Panel: () G Y R
	ENDIF
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
	IF HAS_STATUS_LEDS
	 BCF	PLAT_YELLOW, BIT_YELLOW, ACCESS	; Panel: () G () R
	ENDIF
	;
	; Timer 2 for half-wave slice timing
	;
	MOVLW	SLICE_TMR_PERIOD	; set timer period
	MOVWF	PR2, ACCESS
	CLRF	TMR2, ACCESS		; reset timer
	BSF	IPR1, TMR2IP, ACCESS	; set HIGH priority for timing
	BCF	PIR1, TMR2IF, ACCESS	; clear any pending interrupt
	BSF	PIE1, TMR2IE, ACCESS	; enable timer 2 interrupts
	BSF	T2CON, TMR2ON, ACCESS	; start timer 2 running
	;
	BSF	PIE1, RCIE, ACCESS	; Enable RxD interrupts
	;
	; Clear all interrupt flags and enable interrupts
	;
	CLRF	PIR1, ACCESS
	CLRF	PIR2, ACCESS
        IF LUMOS_ARCH != LUMOS_ARCH_14K50
	 CLRF	PIR3, ACCESS
	ENDIF
	BCF	INTCON, TMR0IF, ACCESS
	BCF	INTCON, INT0IF, ACCESS
	BSF	INTCON, GIEH, ACCESS	; Enable high-priority interrupts
	BSF	INTCON, GIEL, ACCESS	; Enable low-priority interrupts
	;
	; Check for factory reset jumper
	;  (short J11 pins 4 and 5, then power up device [or press reset].  When 
	;  all lights flash, pull the jumper away. device will restore factory 
	;  settings.)
	;                                                            ______
	; With the jumper in place, the OPTION input will follow the PWRCTL output.
	; If they start off unequal, we skip this check and don't disturb the power
	; supply logic at all.  Otherwise, we will flip our output a couple of times
	; and see that OPTION keeps pace, which indicates that the jumper is there.
	; we'll wait for the jumper to be pulled to avoid an infinite loop of resets,
	; and also to provide a way out (power off first and no reset will have happened).
	;
	CLRWDT
;	IF HAS_POWER_CTRL
;	 BCF	PLAT_PWR_ON, BIT_PWR_ON, ACCESS	; turn on power supply
;	ENDIF
;        IF LUMOS_ARCH == LUMOS_ARCH_14K50
;PORT_TEST_IN	EQU	PORT_SENS_A	; The 14K50 lacks a PWR_ON output pin, so we have to
;PLAT_TEST_OUT	EQU	PLAT_SENS_B	; pick on something else for the factory reset sensor
;BIT_TEST_IN	EQU	BIT_SENS_A	; (jumper the OPTION AND short A+B together when powered on)
;BIT_TEST_OUT	EQU	BIT_SENS_B
;TRIS_TEST_IN	EQU	TRIS_SENS_A
;TRIS_TEST_OUT	EQU	TRIS_SENS_B
;TRISTATE_TEST	EQU	1
;	ELSE
;PORT_TEST_IN	EQU	PORT_OPTION
;PLAT_TEST_OUT	EQU	PLAT_PWR_ON
;BIT_TEST_IN	EQU	BIT_OPTION
;BIT_TEST_OUT	EQU	BIT_PWR_ON
;TRISTATE_TEST	EQU	0
;	ENDIF
FACTORY_RESET_JUMPER_CHECK:
	IF HAS_FACTORY_RESET
	 IF FRST_TRISTATE_TEST				; set I/O bits for test mode
	  BCF	FRST_SENDER_T, FRST_SENDER_B, ACCESS	; sender = output
	  BSF	FRST_RECEIVER_T, FRST_RECEIVER_B, ACCESS; receiver = input
	 ENDIF
	 BCF	FRST_SENDER_P, FRST_SENDER_B, ACCESS	; send 0
	 RCALL	DELAY_1_12_SEC
	 BTFSC	FRST_RECEIVER_P, FRST_RECEIVER_B, ACCESS; receive 1? (default for buttons)
	 BRA	END_FRJC				; then we're done
	 ;
	 ; 0->0 !! We may have a jumpered connection.  Try flipping the bit
	 ;
	 CLRWDT					
	 BSF	FRST_SENDER_P, FRST_SENDER_B, ACCESS 	; send 1
	 RCALL	DELAY_1_12_SEC
	 BTFSS	FRST_RECEIVER_P, FRST_RECEIVER_B, ACCESS
	 BRA	END_FRJC				; received 0... someone must just be holding
	 ;						; down button L4 but it's not our jumper.
	 ; 1->1 !! Try again just to be sure...
	 ;
	 CLRWDT					
	 BCF	FRST_SENDER_P, FRST_SENDER_B, ACCESS 	; send 0
	 RCALL	DELAY_1_12_SEC
	 BTFSC	FRST_RECEIVER_P, FRST_RECEIVER_B, ACCESS
	 BRA	END_FRJC				; received 1... doesn't look like our jumper
	 ;
	 ; 0->0 again.. one more time just to be reeeeeeally sure.
	 ;
	 CLRWDT					
	 BSF	FRST_SENDER_P, FRST_SENDER_B, ACCESS 	; send 1
	 RCALL	DELAY_1_12_SEC
	 BTFSS	FRST_RECEIVER_P, FRST_RECEIVER_B, ACCESS
	 BRA	END_FRJC				; received 0... never mind
	 ;
	 ; After perhaps a bit too much caution, we're convinced there's a jumper there.
	 ; wait for it to go away now, then do the reset.
	 ;                                         
	 BSF	FRST_SENDER_P, FRST_SENDER_B, ACCESS 	; send 0 again and wait for jumper pull
	 BSF	FRST_SIG_A_P, FRST_SIG_A_B, ACCESS
	 BCF	FRST_SIG_B_P, FRST_SIG_B_B, ACCESS
	 BSF	FRST_SIG_C_P, FRST_SIG_C_B, ACCESS
FRJC_LOOP:
	 ;
	 ; signal factory reset is imminent by flashing lights
	 ; until we see the receiver go back to 1 (which is our pull-up
	 ; resistor grabbing the line again when the jumper isn't
	 ; there anymore).
	 ;
	 CLRWDT
	 RCALL	DELAY_1_12_SEC
	 BTG	FRST_SIG_A_P, FRST_SIG_A_B, ACCESS
	 BTG	FRST_SIG_B_P, FRST_SIG_B_B, ACCESS
	 BTG	FRST_SIG_C_P, FRST_SIG_C_B, ACCESS
	 BTFSS	FRST_RECEIVER_P, FRST_RECEIVER_B, ACCESS ; 0->1 transition is jumper pull
	 BRA	FRJC_LOOP
	 GOTO	FACTORY_RESET
	ENDIF
	
END_FRJC:
	IF QSCC_PORT
	 CALL	QSCC_START
	ENDIF
	;
	; Launch mainline code
	;
	BANKSEL	SSR_DATA_BANK
	IF HAS_STATUS_LEDS
	 BCF	PLAT_RED, BIT_RED, ACCESS	; Panel: () G () ()
	 CLRF	SSR_00_VALUE+SSR_GREEN, BANKED	; Green light cycles ~ 1/4 Hz
	 ;SET_SSR_PATTERN SSR_GREEN, 0, 1, 1, BIT_FADE_UP|BIT_FADE_CYCLE
	 SET_SSR_NORMAL_MODE SSR_GREEN
	ENDIF
	;	
	; If we're in DMX mode, change our baud rate to 250,000 bps
	;
	IF DMX_ENABLED
	 BTFSS	DMX_SLOTH, DMX_EN, ACCESS
	 GOTO	MAIN
	 MOVLW	SIO_250000
	 CALL	SIO_SET_BAUD_W
	 BSF	DMX_SLOTH, DMX_SPEED, ACCESS
	 IF HAS_STATUS_LEDS
	  ;SET_SSR_PATTERN SSR_GREEN, 0, 1, 3, BIT_FADE_UP|BIT_FADE_CYCLE
	  SET_SSR_DMX_MODE SSR_GREEN
	 ENDIF
	ENDIF
	GOTO	MAIN

BEGIN_EEPROM_READ MACRO START_ADDR
	 BCF	INTCON, GIEH, ACCESS	; Disable high-priority interrupts
	 BCF	INTCON, GIEL, ACCESS	; Disable low-priority interrupts
	 SET_EEPROM_ADDRESS START_ADDR	; NOTE interrupts need to be OFF here!
	 BCF	EECON1, EEPGD, ACCESS	; select DATA EEPROM as target
	 BCF	EECON1, CFGS, ACCESS
	 BCF	EECON1, WREN, ACCESS	; disable writing
	ENDM

BEGIN_EEPROM_WRITE MACRO START_ADDR
	 BCF	INTCON, GIEH, ACCESS	; Disable high-priority interrupts
	 BCF	INTCON, GIEL, ACCESS	; Disable low-priority interrupts
	 SET_EEPROM_ADDRESS START_ADDR	; NOTE interrupts need to be OFF here!
	 BCF	EECON1, EEPGD, ACCESS	; select DATA EEPROM as target
	 BCF	EECON1, CFGS, ACCESS
	 BSF	EECON1, WREN, ACCESS	; enable writing
	ENDM

END_EEPROM_READ MACRO			; THIS CANNOT CHANGE WREG
	 BSF	INTCON, GIEH, ACCESS	; Enable high-priority interrupts
	 BSF	INTCON, GIEL, ACCESS	; Enable low-priority interrupts
         IF LUMOS_ARCH != LUMOS_ARCH_14K50
	  CLRF	EEADRH, ACCESS
	 ENDIF
	 CLRF	EEADR, ACCESS
	ENDM
	
END_EEPROM_WRITE MACRO
	 BCF	EECON1, WREN, ACCESS	; disable writing
	 BSF	INTCON, GIEH, ACCESS	; Enable high-priority interrupts
	 BSF	INTCON, GIEL, ACCESS	; Enable low-priority interrupts
         IF LUMOS_ARCH != LUMOS_ARCH_14K50
	  CLRF	EEADRH, ACCESS
	 ENDIF
	 CLRF	EEADR, ACCESS
	ENDM

SET_EEPROM_ADDRESS MACRO ADDR
         IF LUMOS_ARCH != LUMOS_ARCH_14K50
	  MOVLW	HIGH(ADDR)		; NOTE interrupts need to be OFF here!
	  MOVWF	EEADRH, ACCESS
	 ENDIF
	 MOVLW	LOW(ADDR)
	 MOVWF	EEADR, ACCESS
	ENDM

EE_LL_XX    SET 0
WRITE_EEPROM_DATA MACRO
	 BCF	PIR2, EEIF, ACCESS	; clear interrupt flag
	 MOVLW	0x55
	 MOVWF	EECON2, ACCESS
	 MOVLW	0xAA
	 MOVWF	EECON2, ACCESS
	 BSF	EECON1, WR, ACCESS	; start write cycle
WRITE_EEPROM_LOOP#v(EE_LL_XX):
	 BTFSS	PIR2, EEIF, ACCESS	; wait until write completes
	 BRA	WRITE_EEPROM_LOOP#v(EE_LL_XX)
	 CLRWDT
	 BCF	PIR2, EEIF, ACCESS	; clear interrupt flag
EE_LL_XX    ++
	ENDM

WRITE_EEPROM_DATA_INC MACRO
	WRITE_EEPROM_DATA
	INCF	EEADR, F, ACCESS
	ENDM

WRITE_EEPROM_DATA_W MACRO
	MOVWF	EEDATA, ACCESS
	WRITE_EEPROM_DATA
	ENDM

WRITE_EEPROM_DATA_W_INC MACRO
	WRITE_EEPROM_DATA_W
	INCF	EEADR, F, ACCESS
	ENDM

READ_EEPROM_DATA MACRO
	BSF	EECON1, RD, ACCESS
	ENDM

READ_EEPROM_DATA_REG MACRO REGISTER
	READ_EEPROM_DATA
	MOVFF	EEDATA, REGISTER
	ENDM

READ_EEPROM_DATA_W MACRO
	READ_EEPROM_DATA
	MOVFF	EEDATA, WREG
	ENDM

READ_EEPROM_DATA_W_INC MACRO
	READ_EEPROM_DATA_W
	INCF	EEADR, F, ACCESS
	ENDM
	
FACTORY_RESET:
	CLRWDT
	;
	; write default configuration to EEPROM
	;
	BEGIN_EEPROM_WRITE EE_START
	MOVLW	UPPER(DEFAULT_TBL)	; load lookup table pointer
	MOVWF	TBLPTRU, ACCESS
	MOVLW	HIGH(DEFAULT_TBL)
	MOVWF	TBLPTRH, ACCESS
	MOVLW	LOW(DEFAULT_TBL)
	MOVWF	TBLPTR, ACCESS

	MOVLW	EEPROM_SETTINGS_LEN
	MOVWF	I, ACCESS

FACTORY_RESET_LOOP:
	TBLRD	*+			; byte -> TABLAT
	MOVFF	TABLAT, EEDATA
	IF HAS_STATUS_LEDS
	 BSF	PLAT_YELLOW, BIT_YELLOW, ACCESS	; Panel: () () Y R
	ENDIF
	WRITE_EEPROM_DATA_INC
	IF HAS_STATUS_LEDS
	 BCF	PLAT_YELLOW, BIT_YELLOW, ACCESS	; Panel: () () () R
	ENDIF

	DECFSZ	I, F, ACCESS
	BRA	FACTORY_RESET_LOOP
	END_EEPROM_WRITE

	MOVLW	.16
	MOVWF	I, ACCESS

	CLRWDT
	BCF	INTCON, GIEH, ACCESS	; Disable high-priority interrupts
	BCF	INTCON, GIEL, ACCESS	; Disable low-priority interrupts

FACTORY_RESET_FLASH:
	IF HAS_STATUS_LEDS
	 IF HAS_ACTIVE
	  BSF	PLAT_ACTIVE, BIT_ACTIVE, ACCESS	; Panel: A G Y R
	 ENDIF
	 BSF	PLAT_GREEN, BIT_GREEN, ACCESS
	 BSF	PLAT_YELLOW, BIT_YELLOW, ACCESS
	 BSF	PLAT_RED, BIT_RED, ACCESS
	 RCALL	DELAY_1_12_SEC
	 IF HAS_ACTIVE
	  BCF	PLAT_ACTIVE, BIT_ACTIVE, ACCESS	; Panel: () () () ()
	 ENDIF
	 BCF	PLAT_GREEN, BIT_GREEN, ACCESS
	 BCF	PLAT_YELLOW, BIT_YELLOW, ACCESS
	 BCF	PLAT_RED, BIT_RED, ACCESS
	 RCALL	DELAY_1_6_SEC
	 DECFSZ	I, F, ACCESS
	 BRA	FACTORY_RESET_FLASH
	ENDIF
	RESET

DELAY_1_12_SEC:	; Approx 1/12 sec delay loop
	CLRWDT
	MOVLW	.4
	MOVWF	KK, ACCESS
	BRA	D_1_6_KK

DELAY_1_6_SEC:	; Approx 1/6 sec delay loop
	CLRWDT
	MOVLW	.8
	MOVWF	KK, ACCESS
D_1_6_KK:
	SETF	J, ACCESS
D_1_6_J:
	SETF	K, ACCESS
D_1_6_K:
	DECFSZ	K, F, ACCESS
	BRA	D_1_6_K
	DECFSZ	J, F, ACCESS
	BRA	D_1_6_J
	DECFSZ	KK, F, ACCESS
	BRA	D_1_6_KK
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
	BSF	SSR_STATE2, TEST_UPD, ACCESS	; time for next test-mode countdown
	MOVFF	PHASE_OFFSETH, CUR_PREH
	MOVFF	PHASE_OFFSETL, CUR_PRE
	IF QSCC_PORT
	 #include "qscc_hook_120hz.asm"
	ENDIF
	;
	; handle OPTION button
	; increment hold counter if we see it pressed, decrement if not.
	;
	IF HAS_OPTION
	 COMF	OPTION_DEBOUNCE, W, ACCESS	; button fully on?
	 BZ	INT_ZC_OPTION_ON
	 TSTFSZ	OPTION_DEBOUNCE, ACCESS		; button fully off?
	 BRA	INT_ZC_OPTION_UNDEFINED
INT_ZC_OPTION_OFF:
	 TSTFSZ	OPTION_HOLD, ACCESS		; unless already at zero,
	 DECF	OPTION_HOLD, F, ACCESS		; decrement counter
	 BRA	INT_ZC_END_OPTION
INT_ZC_OPTION_ON:
	 INFSNZ	OPTION_HOLD, F, ACCESS		; increment counter
	 SETF	OPTION_HOLD, ACCESS		; but don't let it overflow
INT_ZC_OPTION_UNDEFINED:
	 ; If the button is still floating between on and off, don't
	 ; count it yet.  It needs to stay on or off for a while before
	 ; we count it toward the hold time.
INT_ZC_END_OPTION:
	ENDIF
INT_ZC_END:
	;
	; Start of cycle slice signal
	;
INT_TMR2:
	BTFSS	PIR1, TMR2IF, ACCESS		; has timer expired?
	BRA	INT_TMR2_END			; no, move along...
	;
	; debounce OPTION button
	;
	IF HAS_OPTION
	 BTFSC	PORT_OPTION, BIT_OPTION, ACCESS	; is option button triggered? (active-low)
	 BRA	INT_OPTION_OFF			
INT_OPTION_ON:
	 INFSNZ	OPTION_DEBOUNCE, F, ACCESS	; increment bounce counter
	 SETF	OPTION_DEBOUNCE, ACCESS		; but not too far - don't overflow
	 BRA	INT_OPTION_END
INT_OPTION_OFF:
	 TSTFSZ	OPTION_DEBOUNCE, ACCESS		; if not already at zero,
	 DECF	OPTION_DEBOUNCE, F, ACCESS	; decrement counter
INT_OPTION_END:
	ENDIF
	;
	; rest of cycle timing code
	;
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
	
	IF QSCC_PORT
	 #include "qscc_hook_isr.asm"
	ENDIF

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
SSR_STATE2	RES	1		; major state/timing flags
DMX_SLOTH	RES	1
DMX_SLOTL	RES	1
YY_STATE 	RES	1
YY_COMMAND 	RES	1
YY_CMD_FLAGS	RES	1
YY_DATA    	RES	1
YY_LOOKAHEAD_MAX RES	1
YY_LOOK_FOR	RES	1
YY_BUF_IDX 	RES	1
YY_NEXT_STATE	RES	1
YY_YY		RES	1
LAST_ERROR	RES	1
CUR_PREH	RES	1
CUR_PRE		RES	1
CUR_SLICE	RES	1
TARGET_SSR	RES	1
OPTION_DEBOUNCE	RES	1
OPTION_HOLD	RES	1
TEST_CYCLE	RES	1
TEST_SSR  	RES	1
AUTO_OFF_CTRH	RES	1
AUTO_OFF_CTRL	RES	1
EIGHTBITSIOBUF	RES	1		; buffer for 8-bit data adjustments
I               RES	1
J               RES	1
K               RES	1
KK              RES	1
TR_I		RES	1
;                      --
;                      35
;
		IF QSCC_PORT
		 #include "qscc_hook_access_bank.inc"
		ENDIF

;==============================================================================
; DATA BANK 4
;______________________________________________________________________________

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
_MAINDATA	UDATA	MAIN_DATA
YY_BUFFER	RES	YY_BUF_LEN

;==============================================================================
; DATA BANKS 6-: SEQUENCE STORAGE
;______________________________________________________________________________
SEQ_DATA	EQU	0x600			; XXX NOT on 14K50!!!
_SEQ_DATA	UDATA	SEQ_DATA

;==============================================================================
; MAINLINE CODE
;______________________________________________________________________________
_MAIN	CODE	0x0800
MAIN:
	CLRWDT
	IF QSCC_PORT
	 CALL	QSCC_MAIN
	ENDIF

	CLRWDT
	BTFSC	SSR_STATE, SLICE_UPD, ACCESS
	CALL	UPDATE_SSR_OUTPUTS

	; DMX mode: poll for framing error to start DMX frame reception
	IF DMX_ENABLED
	 BTFSS	DMX_SLOTH, DMX_EN, ACCESS
	 BRA	NOT_DMX
	 BANKSEL	SIO_DATA_START
	 BTFSS	SIO_STATUS, SIO_FERR, BANKED	; Did SIO code find a framing error first?
	 BRA	BRK_DET2			; No, check ourselves then
	 IF HAS_ACTIVE
          SET_SSR_BLINK_FADE SSR_ACTIVE
	 ENDIF
	 CALL	SIO_GETCHAR			; Yes, then read the byte we received
	 TSTFSZ	SIO_INPUT, BANKED		; ...  is the received byte all zeroes?
	 BRA	NOT_DMX				; No, must not really be a break then
	 BANKSEL	SIO_DATA_START
	 BCF	SIO_STATUS, SIO_FERR, BANKED	; Yes: clear the status and proceed
	 BRA	BRK_DET
BRK_DET2:
	 BTFSS	RCSTA, FERR, ACCESS
	 BRA	NOT_DMX
	 ; found framing error -- is it a break?
	 IF HAS_ACTIVE
	  SET_SSR_BLINK_FADE SSR_ACTIVE
	 ENDIF
	 MOVF	RCREG, W, ACCESS	; read byte, clear FERR, see if data all zeroes
	 BNZ	NOT_DMX			; no, must be line noise, carry on...
BRK_DET:
	;
	; BREAK DETECTED
	;
	; Now we start counting while we watch the RxD line for the 0->1 transition
	; If it took <56uS, we'll interpret it as noise.  Otherwise, it's a break and
	; the start of our DMX frame.  As a safety measure, if the break lasts longer
	; than ~8,000uS, we abandon the frame.
	; 
	 IF HAS_STATUS_LEDS
  	  SET_SSR_BLINK_FADE SSR_YELLOW
	 ENDIF
	 BCF	PIE1, RCIE, ACCESS	; Disable RxD interrupts for now
	 MOVLW	0xE0
	 MOVWF	TMR3H, ACCESS
	 MOVLW	0xC7
	 MOVWF	TMR3L, ACCESS		; $E0C7 is 7,992 away from overflowing and 56 away
					; from overflowing the LSB
	 BCF	PIR2, TMR3IF, ACCESS	; Clear overflow status bit
	 BCF	PIE2, TMR3IE, ACCESS	; Don't use as interrupt
	 BSF	T3CON, TMR3ON, ACCESS	; Start Timer 3 Running
	;
	; Watch the RxD line for a transition away from the break
	;
WATCH_BREAK:
	 CLRWDT
	 BTFSC	SSR_STATE, SLICE_UPD, ACCESS	; keep updating SSR outputs during this
	 CALL	UPDATE_SSR_OUTPUTS
	 BTFSC	PORT_RX, BIT_RX, ACCESS	; Is the line 0?
	 BRA	BREAK_CONFIRMED
	 BTFSS	PIR2, TMR3IF, ACCESS	; Did we exceed our limit?
	 BRA	WATCH_BREAK
	;
	; We've been holding too long, give up on the break signal.
	; 
	 BCF	T3CON, TMR3ON, ACCESS	; Shut down Timer 3
	 BSF	PIE1, RCIE, ACCESS	; Enable RxD interrupts again
	 BRA	BAD_BREAK

BREAK_CONFIRMED:
	;
	; Break over, reset UART and interpret frame
	;
	 IF HAS_STATUS_LEDS
 	  SET_SSR_BLINK_FADE SSR_RED
	 ENDIF
	 BCF	T3CON, TMR3ON, ACCESS	; Shut down Timer 3
	 BSF	PIE1, RCIE, ACCESS	; Enable RxD interrupts again
	 BCF	RCSTA, CREN, ACCESS
	 BSF	RCSTA, CREN, ACCESS
	 MOVLW	0xE0
	 MOVF	TMR3L, W, ACCESS	; Initiate 16-bit read of TMR3 register
	 CPFSEQ	TMR3H, ACCESS		; If MSB of Timer3 advanced, it was >56uS
	 BRA	START_DMX_FRAME		; and therefore the start of the frame
	;				; If not, it's noise and we interpret as "NOT_DMX"
	;	 | |
	;       _| |_
	;       \   /
	;        \ /
	;         V
	ENDIF
NOT_DMX:
	BANKSEL	SIO_DATA_START
	BTFSC	SIO_STATUS, SIO_FERR, BANKED
BAD_BREAK:
	RCALL	ERR_SERIAL_FRAMING

	BANKSEL	SIO_DATA_START
	BTFSC	SIO_STATUS, SIO_ORUN, BANKED
	RCALL	ERR_SERIAL_OVERRUN

	BANKSEL	SIO_DATA_START
	BTFSC	SIO_STATUS, RXDATA_FULL, BANKED
	RCALL	ERR_SERIAL_FULL

	BANKSEL	SIO_DATA_START
	BTFSS	SIO_STATUS, RXDATA_QUEUE, BANKED
	BRA	END_SERIAL_READ
	BTFSC	SSR_STATE, TEST_MODE, ACCESS
	BRA	TEST_MODE_BYPASS
	RCALL	RECEIVE_COMMAND
	BRA	END_SERIAL_READ
TEST_MODE_BYPASS:
	CALL	SIO_READ		; read and discard input while in test mode
END_SERIAL_READ:

	BTFSC	SSR_STATE, DRAIN_TR, ACCESS
	RCALL	DRAIN_TRANSMITTER

	BTFSC	SSR_STATE, TEST_MODE, ACCESS
	RCALL	DO_TEST_MODE

	IF HAS_OPTION
OPTION_HANDLER:
	 BTFSS	SSR_STATE, PRIV_MODE, ACCESS		; are we in privileged mode?
	 BRA	OPTION_PRE_PRIV				; no, check if we're in pre-priv...
                 					; -------------------------------------------------PRIV_MODE
	 BTFSS	SSR_STATE, PRE_PRIV, ACCESS		; PRIV_MODE+PRE_PRIV: transitioning to TEST mode
	 BRA	OPTION_PRIV_MODE			; just PRIV_MODE: skip down a bit...
	 TSTFSZ	OPTION_DEBOUNCE, ACCESS			; has button released yet?
	 BRA	END_OPTION_HANDLER			; no, keep waiting
	 BCF	SSR_STATE, PRE_PRIV, ACCESS		; yes: move to test mode now
	 BSF	SSR_STATE, TEST_MODE, ACCESS
	 MOVLW	.120
	 MOVWF	TEST_CYCLE, ACCESS
	 SETF	TEST_SSR, ACCESS			; initialize ssr index
	 CLRF	OPTION_HOLD, ACCESS
	 IF HAS_STATUS_LEDS
	  IF HAS_ACTIVE
	   SET_SSR_OFF SSR_ACTIVE
	  ENDIF
	  SET_SSR_OFF SSR_GREEN
	  SET_SSR_OFF SSR_YELLOW
	  SET_SSR_OFF SSR_RED
	 ENDIF
	 IF ROLE_MASTER
	  MOVLW	0xF0					; send to slave chip: F0 21 00000000 00000000
	  CALL	SIO_WRITE_W				; (all LEDs off)
	  MOVLW	0x21
	  CALL	SIO_WRITE_W
	  MOVLW	0x00
	  CALL	SIO_WRITE_W
	  MOVLW	0x00
	  CALL	SIO_WRITE_W
	 ENDIF
	 RCALL	S0_CMD0					; blackout all SSR outputs
	 BRA	END_OPTION_HANDLER

OPTION_PRIV_MODE:
	 COMF	OPTION_HOLD, W, ACCESS			; is option pressed ~2s?
	 BNZ	END_OPTION_HANDLER			; no
	 BSF	SSR_STATE, PRE_PRIV, ACCESS		; set PRE_PRIV (wait for button release)
	 BRA	END_OPTION_HANDLER

OPTION_PRE_PRIV:					
	 BTFSS	SSR_STATE, PRE_PRIV, ACCESS		; are we in pre-priv state?
	 BRA	OPTION_NORMAL				; no, must be normal operating mode.
	 TSTFSZ	OPTION_HOLD, ACCESS			; --------------------------------------------------PRE_PRIV
	 BRA	END_OPTION_HANDLER			; wait for button to be released ~2s
	 BCF	SSR_STATE, PRE_PRIV, ACCESS		; move to privileged run mode
	 BTFSC	SSR_STATE2, PRIV_FORBID, ACCESS		; unless we have privileges locked out now...
	 BRA	END_OPTION_HANDLER
	 BSF	SSR_STATE, PRIV_MODE, ACCESS		; turn on privileged mode
	 IF HAS_STATUS_LEDS
	  IF HAS_ACTIVE
	   SET_SSR_BLINK_FADE SSR_ACTIVE
	  ENDIF
	  SET_SSR_BLINK_FADE SSR_YELLOW
	  SET_SSR_BLINK_FADE SSR_RED
	 ENDIF
	 IF ROLE_MASTER
	  MOVLW	0xF0					; send to slave chip: F0 21 00101000 00000000
	  CALL	SIO_WRITE_W				; (rapid flash green, others off)
	  MOVLW 0x21
	  CALL	SIO_WRITE_W
	  MOVLW	0x28
	  CALL	SIO_WRITE_W
	  MOVLW	0x00
	  CALL	SIO_WRITE_W
	 ENDIF
	 IF DMX_ENABLED
	  CALL	DMX_EXIT_TEMPORARILY
	 ENDIF
	 BRA END_OPTION_HANDLER

OPTION_NORMAL:						; ----------------------------------------------------NORMAL
	 COMF	OPTION_HOLD, W, ACCESS			; has option been held full time?
	 BNZ	END_OPTION_HANDLER			; nope, move along...
	 BSF	SSR_STATE, PRE_PRIV, ACCESS		; yes, initiate pre-priv mode (wait for button release)
	 IF HAS_STATUS_LEDS
	  IF HAS_ACTIVE
	   SET_SSR_RAPID_FLASH SSR_ACTIVE
	  ENDIF
	  SET_SSR_RAPID_FLASH SSR_GREEN
	  SET_SSR_RAPID_FLASH SSR_YELLOW
	  SET_SSR_RAPID_FLASH SSR_RED
	 ENDIF
	 IF ROLE_MASTER
	  MOVLW	0xF0					; send to slave chip: F0 21 00101101 00000101
	  CALL	SIO_WRITE_W				; (rapid flash all LEDs)
	  MOVLW	0x21
	  CALL	SIO_WRITE_W
	  MOVLW	0x2D
	  CALL 	SIO_WRITE_W
	  MOVLW	0x05
	  CALL	SIO_WRITE_W
	 ENDIF
END_OPTION_HANDLER:
	ENDIF

	; OPTION button handler
	; normal: option held ~2s, -> init option mode
	; initopt: option released -> priv mode
	; priv: option held ~2s and release -> test mode
	; test: option press -> pause, wait for release
	; pause: option press -> wait for release, test

	BRA	MAIN
	
DRAIN_TRANSMITTER:
	IF HAS_T_R
	 BANKSEL SIO_DATA_START
	 BTFSC	SIO_STATUS, TXDATA_QUEUE, BANKED	; data still waiting in our output buffer?
	 RETURN
	 BTFSS	PIR1, TXIF, ACCESS			; data in transit into UART shift register?
	 RETURN
	 BTFSS	TXSTA, TRMT, ACCESS			; data being shifted out now?
	 RETURN
	 BCF	SSR_STATE, DRAIN_TR, ACCESS		; none of the above--shut down transmitter now
	 CALL	TR_OFF_DELAY
	 BCF	PLAT_T_R, BIT_T_R, ACCESS		
	 RETURN
	ELSE
	 ERR_BUG 0x11, ERR_CLASS_DEVICE
    	ENDIF

DRAIN_M_S_TX_BLOCKING:
	;
	; version of DRAIN_TRANSMITTER which is designed to clear
	; master->slave comms in critical situations.  Blocks until
	; the pending output is sent to the slave.
	;
	IF ROLE_MASTER
	 BANKSEL SIO_DATA_START
	 CLRWDT
DRAIN_M_S_DRAIN_SIO_QUEUE:
	 BTFSC	SIO_STATUS, TXDATA_QUEUE, BANKED
	 BRA	DRAIN_M_S_DRAIN_SIO_QUEUE
	 CLRWDT
DRAIN_M_S_DRAIN_UART_TX_BUF:
	 BTFSS	PIR1, TXIF, ACCESS
	 BRA	DRAIN_M_S_DRAIN_UART_TX_BUF
	 CLRWDT
DRAIN_M_S_DRAIN_UART_SHIFT_REG:
	 BTFSS	TXSTA, TRMT, ACCESS
	 BRA	DRAIN_M_S_DRAIN_UART_SHIFT_REG
	 CLRWDT
	 RETURN
	ELSE
	 ERR_BUG 0x12, ERR_CLASS_DEVICE
	ENDIF

DO_TEST_MODE:
	CLRWDT

	COMF	OPTION_DEBOUNCE, W, ACCESS	; is option button pressed?
	BNZ	TEST_NOT_PRESSED
	BSF	SSR_STATE2, TEST_BUTTON, ACCESS	; yes, keep waiting for it to be released
	BRA	TEST_MODE_1
TEST_NOT_PRESSED:
	TSTFSZ	OPTION_DEBOUNCE, ACCESS		; is option button fully off?
	BRA	TEST_MODE_1
	BTFSS	SSR_STATE2, TEST_BUTTON, ACCESS	; were we waiting for this button cycle event?
	BRA	TEST_MODE_1			; 
	;
	; OPTION button was pressed and then released.  Toggle pause state.
	;
	BCF	SSR_STATE2, TEST_BUTTON, ACCESS	; 
	BTG	SSR_STATE2, TEST_PAUSE, ACCESS  ;
	SETF	TEST_CYCLE, ACCESS		; reset cycle timer
	IF ROLE_MASTER				; MASTER  SLAVE           STANDALONE
	 MOVLW	0xF0				; A G Y R G Y R           A G Y R
	 CALL	SIO_WRITE_W			; b3b2b1b0b5b4(*)         b2b1b0(*)  run
	 MOVLW	0x21				;              *                 *   pause
	 CALL	SIO_WRITE_W
	 MOVLW	B'00111111'
	 CALL	SIO_WRITE_W
	 MOVLW	B'00000001'
	 BTFSS	SSR_STATE2, TEST_PAUSE, ACCESS
	 MOVLW	B'00000010'
	 CALL	SIO_WRITE_W
	ELSE
	 BTFSS	SSR_STATE2, TEST_PAUSE, ACCESS
	 BRA	TEST_NP_1
	 IF HAS_STATUS_LEDS
	  SET_SSR_STEADY SSR_RED
	 ENDIF
	 BRA	TEST_NP_2
TEST_NP_1:
	 IF HAS_STATUS_LEDS
	  SET_SSR_SLOW_FADE SSR_RED
	 ENDIF
TEST_NP_2:
	ENDIF
	
TEST_MODE_1:
	BTFSS	SSR_STATE2, TEST_PAUSE, ACCESS	; paused? 
	BTFSS	SSR_STATE2, TEST_UPD, ACCESS	; time to count down?
	RETURN					; either we're paused or not time to update; stop.
	
	BCF	SSR_STATE2, TEST_UPD, ACCESS	; clear flag about being time to update
	DECFSZ	TEST_CYCLE, F, ACCESS		; count down until time to change channels
	RETURN
	MOVLW	.120
	MOVWF	TEST_CYCLE, ACCESS		; reset counter time for next channel

	RCALL	S0_CMD0				; kill all outputs
	INCF	TEST_SSR, F, ACCESS		; jump to next SSR
	MOVLW	NUM_CHANNELS
	CPFSLT	TEST_SSR, ACCESS		; channel > last channel?
	CLRF	TEST_SSR, ACCESS		; cycle to 0 if exceeded our limit

	MOVLW	0x3F
	ANDWF	TEST_SSR, W, ACCESS		; keep to limits of channel number
	MOVWF	YY_DATA, ACCESS			; set up YY_DATA for ON_OFF call
	BSF	YY_DATA, 6, ACCESS		; turn on
	RCALL	ON_OFF_YY_DATA			; execute

	BANKSEL	SSR_DATA_BANK
	IF HAS_STATUS_LEDS
	 CLRF	SSR_00_VALUE + SSR_RED, BANKED
	 CLRF	SSR_00_VALUE + SSR_YELLOW, BANKED
	 CLRF	SSR_00_VALUE + SSR_GREEN, BANKED
	 IF HAS_ACTIVE
	  CLRF	SSR_00_VALUE + SSR_ACTIVE, BANKED
	 ENDIF
	ENDIF

	IF ROLE_MASTER					; MASTER----- SLAVE---      STANDALONE-
	 IF HAS_STATUS_LEDS
	  BTFSC	TEST_SSR, 2, ACCESS			; A  G  Y  R  G  Y  R       A  G  Y  R
	  SETF	SSR_00_VALUE + SSR_RED, BANKED		; b5 b4 b3 b2 b1 b0 (*)     b2 b1 b0 (*)
	  BTFSC	TEST_SSR, 3, ACCESS
	  SETF	SSR_00_VALUE + SSR_YELLOW, BANKED
	  BTFSC	TEST_SSR, 4, ACCESS
	  SETF	SSR_00_VALUE + SSR_GREEN, BANKED
	  IF HAS_ACTIVE
	   BTFSC TEST_SSR, 5, ACCESS
	   SETF	SSR_00_VALUE + SSR_ACTIVE, BANKED
	  ENDIF
	 ENDIF

	 MOVLW	0xF0					; send to slave chip: F0 21 00gggyyy 00000rrr
	 CALL	SIO_WRITE_W
	 MOVLW	0x21
	 CALL 	SIO_WRITE_W
	 CLRF	WREG, ACCESS
	 BTFSC	TEST_SSR, 1, ACCESS
	 BSF	WREG, 3, ACCESS
	 BTFSC	TEST_SSR, 0, ACCESS
	 BSF	WREG, 0, ACCESS
	 CALL	SIO_WRITE_W
	 MOVLW	0x02
	 CALL	SIO_WRITE_W
	ELSE
	 IF HAS_STATUS_LEDS
	  BTFSC	TEST_SSR, 0, ACCESS
	  SETF	SSR_00_VALUE + SSR_YELLOW, BANKED
	  BTFSC	TEST_SSR, 1, ACCESS
	  SETF	SSR_00_VALUE + SSR_GREEN, BANKED
	  IF HAS_ACTIVE
	   BTFSC TEST_SSR, 2, ACCESS
	   SETF	SSR_00_VALUE + SSR_ACTIVE, BANKED
	  ENDIF
	  SET_SSR_SLOW_FADE SSR_RED
	 ENDIF
	ENDIF

	RETURN

ERR_SERIAL_FRAMING:
	BANKSEL	SIO_DATA_START
	BCF	SIO_STATUS, SIO_FERR, BANKED
;	BTFSC	DMX_SLOTH, DMX_EN, ACCESS
;	BRA	START_DMX_FRAME
	IF HAS_STATUS_LEDS
	 SET_SSR_RAPID_FLASH SSR_RED
	 SET_SSR_STEADY SSR_YELLOW
	ENDIF
	RETURN
	IF DMX_ENABLED
START_DMX_FRAME:
	;
	; We're in DMX mode so a framing error (aka break) is really
	; not an error, but the start of our data frame!
	;
	 BSF	DMX_SLOTH, DMX_FRAME, ACCESS
	 IF HAS_STATUS_LEDS
	  SET_SSR_RAPID_FLASH SSR_YELLOW
	 ENDIF
	 RETURN
	ENDIF
	
ERR_SERIAL_OVERRUN:
	BANKSEL	SIO_DATA_START
	BCF	SIO_STATUS, SIO_ORUN, BANKED
	IF HAS_STATUS_LEDS
	 SET_SSR_RAPID_FLASH SSR_RED
	 SET_SSR_RAPID_FLASH SSR_YELLOW
	ENDIF
	RETURN

ERR_SERIAL_FULL:
	IF HAS_STATUS_LEDS
	 SET_SSR_RAPID_FLASH SSR_RED
	 SET_SSR_SLOW_FADE SSR_YELLOW
	ENDIF
	; clear input buffer and reset state machine
	CLRF	YY_STATE, ACCESS
	CALL	SIO_FLUSH_INPUT
	RETURN

ERR_CMD_INCOMPLETE:
	MOVLW	0x23
	MOVWF	LAST_ERROR, ACCESS
	IF HAS_STATUS_LEDS
	 SET_SSR_SLOW_FLASH SSR_RED
	ENDIF
	GOTO	ERR_ABORT
ERR_NOT_IMP:
	MOVLW	0x22
	MOVWF	LAST_ERROR, ACCESS
	IF HAS_STATUS_LEDS
	 SET_SSR_RAPID_FLASH SSR_RED
	ENDIF
	GOTO	ERR_ABORT
ERR_COMMAND:
	MOVLW	0x20
	MOVWF	LAST_ERROR, ACCESS
	IF HAS_STATUS_LEDS
	 SET_SSR_PATTERN SSR_RED, .255, .1, .32, BIT_FADE_DOWN
	ENDIF
ERR_ABORT:
	;SET_SSR_STEADY SSR_RED
	CLRF	YY_STATE, ACCESS	; reset state machine
	RETURN

RECEIVE_COMMAND:
CMD_BIT	EQU	7

	CLRWDT
	;
	; First of all, if we received a byte at all, that means
	; we're not the one expected to be talking anymore.
	; we should never see this while trying to output anything,
	; if everyone else is playing by the same rules,
	; but this is a fail-safe just in case.  In this case, we
	; will immediately shut up.
	;
	BSF	SSR_STATE2, INHIBIT_OUTPUT, ACCESS
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
	IF DMX_ENABLED
	 BTFSC	DMX_SLOTH, DMX_SPEED, ACCESS	; check if we're trying to read DMX now
	 GOTO	DMX_RECEIVED_BYTE
	ENDIF
	;
	CLRWDT
	BANKSEL	SIO_DATA_START
	BTFSS	SIO_INPUT, CMD_BIT, BANKED
	BRA	DATA_BYTE		; it's a data byte
	;
	; ok, so it's a command. are we still waiting for another
	; command to complete?  If so, abort it and start over.
	; otherwise, get to work.
	;
	BCF	SSR_STATE2, MSB_ESC, ACCESS	; cancel escape sequence if any
	BCF	SSR_STATE2, LITERAL_ESC, ACCESS
	MOVF	YY_STATE, W, ACCESS
	BZ	INTERP_START	 
	;
	; ERROR: We hadn't finished with the last command yet, and here we
	; have another one!  (Yes, even if it's someone else's command, that
	; still means ours is apparently abandoned.)
	;
	RCALL	ERR_CMD_INCOMPLETE		; let user know
	
INTERP_START:
	;
	; Start of a new command.
	;
	BANKSEL	SIO_DATA_START
	CLRWDT
	;
	; Is it ours?
	;
	IF QSCC_PORT
	 #include "qscc_hook_global_commands.asm"
 	ENDIF
	IF ! ROLE_SLAVE		; the slave chip has no address and sees no other commands
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
	IF ROLE_SLAVE && HAS_STATUS_LEDS
	 SET_SSR_BLINK_FADE SSR_YELLOW	; slave activity indicator
	ENDIF
	BANKSEL	SIO_DATA_START
	SWAPF	SIO_INPUT, W, BANKED
	ANDLW	0x07
	BZ	S0_CMD0
	GOTO	S0_CMD1		; can't do BNZ S0_CMD1 because it's too far away from here

S0_CMD0:
	;
	; BLACKOUT:
	;
	;   ___7______6______5______4______3______2______1______0__
	;  |      |                    |                           |
	;  |   1  |          0         |   Target device address   | SIO_INPUT
	;  |______|______|______|______|______|______|______|______|
	;  |                                  |          0         |
	;  |                 0                |   (Command code)   | W
	;  |______|______|______|______|______|______|______|______|
	;
	BANKSEL	SSR_DATA_BANK
CH 	SET	0
	WHILE CH <= OUTPUT_CHAN_MAX
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
	 IF HAS_STATUS_LEDS
	  SET_SSR_BLINK_FADE SSR_YELLOW	; slave activity indicator
	 ENDIF
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

; Turns out we don't need this here. We already trap CMD5 for the broadcast
; address, so we don't recognize it again here.  This forces it to be a
; broadcast-only command.
;	IF QSCC_PORT
;	 #include "qscc_hook_5_6.asm"
;	ELSE
S0_CMD5:
	 ; Unimplemented Command
	 DECFSZ	WREG, W, ACCESS
	 BRA	S0_CMD6
	 GOTO	ERR_NOT_IMP		; XXX RESERVED FOR FUTURE COMMAND XXX

S0_CMD6:
	 ; Unimplemented Command
	 DECFSZ	WREG, W, ACCESS
	 BRA	S0_CMD7
	 GOTO	ERR_NOT_IMP		; XXX RESERVED FOR FUTURE COMMAND XXX
;	ENDIF

S0_CMD7:
	; Extended commands
	DECFSZ	WREG, W, ACCESS
	BRA	S0_CMD_ERR
	MOVLW	9
	MOVWF	YY_STATE, ACCESS	; -> state 9 (decode extended command)
	RETURN

S0_CMD_ERR:
	; BUG: We really shouldn't have arrived here!
	ERR_BUG	0x01, ERR_CLASS_OVERRUN
	 
DATA_BYTE:
	CLRWDT
	;
	; Check for escape sequences
	;
	; in MSB mode? set this byte's MSB and skip down
	BTFSS	SSR_STATE2, MSB_ESC, ACCESS
	BRA	DB_CHK_LITERAL
	BSF	SIO_INPUT, 7, BANKED
	BCF	SSR_STATE2, MSB_ESC, ACCESS
	BRA	DB_HANDLER
DB_CHK_LITERAL:
	; no, how about in literal mode? if so, just pass through this byte
	BTFSS	SSR_STATE2, LITERAL_ESC, ACCESS
	BRA	DB_CHK_7E
	BCF	SSR_STATE2, LITERAL_ESC, ACCESS
	BRA	DB_HANDLER
DB_CHK_7E:
	; no, ok, then is this the start of an MSB escape?
	MOVLW	0x7E
	CPFSEQ	SIO_INPUT, BANKED
	BRA	DB_CHK_7F
	BSF	SSR_STATE2, MSB_ESC, ACCESS
	RETURN

DB_CHK_7F:
	; no, then maybe we're starting a literal escape?
	MOVLW	0x7F
	CPFSEQ	SIO_INPUT, BANKED
	BRA	DB_HANDLER
	BSF	SSR_STATE2, LITERAL_ESC, ACCESS
	RETURN
	
DB_HANDLER:
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
	;  |                                  |                    |
	;  |                0                 |          1         | YY_COMMAND
	;  |______|______|______|______|______|______|______|______|
	;  |      |0=off |                                         |
	;  |   0  |1=on  |           Channel ID (0-47)             | YY_DATA
	;  |______|______|______|______|______|______|______|______|
	;
ON_OFF_YY_DATA:
	CALL	XLATE_SSR_ID
	CLRF	YY_STATE, ACCESS			; reset command state
	BTFSC	TARGET_SSR, INVALID_SSR, ACCESS
	GOTO	ERR_COMMAND				; SSR number out of range
	BTFSC	TARGET_SSR, NOT_MY_SSR, ACCESS
	BRA	PASS_DOWN_ON_OFF
	BTFSC	YY_DATA, 6, ACCESS
	BRA	ON_OFF_ON
	CLRF	WREG, ACCESS
	GOTO	SSR_OUTPUT_VALUE			; set value off and return

ON_OFF_ON:
	SETF	WREG, ACCESS
	GOTO	SSR_OUTPUT_VALUE			; set value on and return
	
PASS_DOWN_ON_OFF:
	IF ROLE_MASTER
	 MOVLW	0x90
	 CALL	SIO_WRITE_W
	 MOVF	TARGET_SSR, W, ACCESS
	 ANDLW	0x3F
	 BTFSC	YY_DATA, 6, ACCESS
	 BSF    WREG, 6, ACCESS
	 SEND_8_BIT_W
	 ;CALL 	SIO_WRITE_W
	 IF HAS_STATUS_LEDS
	  SET_SSR_BLINK_FADE SSR_YELLOW	; slave activity indicator
	 ENDIF
	 RETURN
	ELSE
	 GOTO	ERR_COMMAND
	ENDIF

S2_DATA:
	DECFSZ	WREG, W, ACCESS
	BRA	S3_DATA
	; SET_LVL channel byte
	CALL	XLATE_SSR_ID
	BTFSC	TARGET_SSR, INVALID_SSR, ACCESS
	GOTO	ERR_COMMAND
	BTFSC	YY_DATA, 6, ACCESS	; preserve bit 6 (LSB of value)
	BSF	TARGET_SSR, 6, ACCESS	; Reuse bit 6 (INVALID_SSR) for this purpose now
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
	;  |                                  |                    |
	;  |                0                 |          2         | YY_COMMAND
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
	;XXX removed MOVF	YY_DATA, W, ACCESS
	GOTO	SSR_OUTPUT_VALUE			; set SSR to 8-bit YY_DATA value

PASS_DOWN_SET_LVL:
	IF ROLE_MASTER
	 MOVLW	0xA0
	 CALL	SIO_WRITE_W
	 BCF	TARGET_SSR, 7, ACCESS
	 MOVF	TARGET_SSR, W, ACCESS
	 SEND_8_BIT_W
	 ;CALL	SIO_WRITE_W
	 MOVF	YY_DATA, W, ACCESS
	 SEND_8_BIT_W
	 ;CALL	SIO_WRITE_W
	 CLRF	YY_STATE, ACCESS
	 IF HAS_STATUS_LEDS
	  SET_SSR_BLINK_FADE SSR_YELLOW	; slave activity indicator
	 ENDIF
	 RETURN
	ELSE
	 ERR_BUG 0x02, ERR_CLASS_IN_VALID
	ENDIF

S4_DATA:
	DECFSZ	WREG, W, ACCESS
	BRA	S5_DATA
	; BULK_UPD, received channel byte
	CALL	XLATE_SSR_ID
	BTFSC	TARGET_SSR, INVALID_SSR, ACCESS
	GOTO	ERR_COMMAND
	;BTFSC	YY_DATA, 6, ACCESS	; preserve bit 7 (resolution flag)
	;BSF	TARGET_SSR, 6, ACCESS	; (reusing the INVALID_SSR bit)
	WAIT_FOR_SENTINEL .57, B'01010101', 0	; -> S6.0 when sentinel found
	RETURN

S5_DATA:
	DECFSZ	WREG, W, ACCESS
	BRA	S6_DATA
	; RAMP_LVL received channel number
	CALL	XLATE_SSR_ID
	BTFSC	TARGET_SSR, INVALID_SSR, ACCESS
	GOTO	ERR_COMMAND
	BTFSC	YY_DATA, 6, ACCESS	; preserve bit 6 (direction flag)
	BSF	TARGET_SSR, 6, ACCESS	; (reusing the INVALID_SSR bit)
	CLRF	YY_CMD_FLAGS, ACCESS
	BTFSC	YY_DATA, 7, ACCESS	; bit 7: cycle flag -> YY_CMD_FLAGS
	BSF	YY_CMD_FLAGS, YCF_RAMP_CYCLE, ACCESS
	MOVLW	7
	MOVWF	YY_STATE, ACCESS	; -> state 7 (wait for step count)
	RETURN
	

S6_DATA:
	DECFSZ	WREG, W, ACCESS
	GOTO	S7_DATA
	;
	; State 6: Wait for Sentinel
	;
	; In this state, the machine is looking ahead in the data stream
	; for a sentinel pattern.  The pattern is terminated by the byte
	; YY_LOOK_FOR and must be seen in the next YY_LOOKAHEAD_MAX bytes.
	; If the sentinel is not recognized before YY_LOOKAHEAD_MAX runs
	; out, we abort on ERR_COMMAND.
	;
	; Once it's recognized, we move to YY_NEXT_STATE immediately.  This is
	; not a state here in the state machine, but a sub-case of state 6
	; to interpret the final packet.
	;
	; In order to do this, we buffer up the input received in YY_BUFFER.  This is
	; a YY_BUF_LEN-byte memory space aligned on a data bank boundary where YY_BUF_LEN
	; is not more than 256 (currently it's 200).  We will record the character at
	; YY_BUFFER[YY_BUF_IDX++] and stop if YY_BUF_IDX > YY_LOOKAHEAD_MAX.
	;
	CLRWDT
	MOVF	YY_DATA, W, ACCESS		; Is this the sentinel we're looking for?
	CPFSEQ	YY_LOOK_FOR, ACCESS
	GOTO	S6_KEEP_LOOKING
	;
	; We have a packet, now switch on YY_NEXT_STATE to decode and execute
	; the completed command.
	;
	MOVF	YY_NEXT_STATE, W, ACCESS
	BZ	S6_0_DATA
	GOTO	S6_1_DATA	; too far away for relative branch
	;
	; S6.0: Complete BULK_UPD command (from state 5)
	;
	;   ___7______6______5______4______3______2______1______0__
	;  |                                  |                    |
	;  |                0                 |          3         | YY_COMMAND
	;  |______|______|______|______|______|______|______|______|
	;  |NOT_MY|      |                                         |
	;  | _SSR |      |   c = Starting Channel ID (0-47)        | TARGET_SSR
	;  |______|______|______|______|______|______|______|______|
	;  |      |                                                |
	;  |   0  |      n = (Number of channels - 1) (0-47)       | YY_BUFFER+0
	;  |______|______|______|______|______|______|______|______|
	;  |                                                       |
	;  |                  Value for SSR #c                     | YY_BUFFER+1
	;  |______|______|______|______|______|______|______|______|
	;  |                                                       |
	;  |                  Value for SSR #c+1                   | YY_BUFFER+2
	;  |______|______|______|______|______|______|______|______|
	;				.
	;				.
	;              	                .
	;   _______________________________________________________
	;  |                                                       |
	;  |                  Value for SSR #c+n-1                 | YY_BUFFER+n
	;  |______|______|______|______|______|______|______|______|
	;                                                       <-- YY_BUF_IDX == n+1
	;
	;
	;
S6_0_DATA:
	CLRF	YY_STATE, ACCESS		; go ahead and signal end of command parsing
	;					; now so we can just RETURN when done.
	; Calculate expected data lengths
	;
	LFSR	0, YY_BUFFER			
	MOVF	TARGET_SSR, W, ACCESS		; start
	ANDLW	0x3F
	ADDWF	INDF0, W, ACCESS		; start + N-1      (N=#changed; N=n+1)
	INCF	WREG, W, ACCESS			; start + N
	SUBLW	NUM_CHANNELS			; start + N > NUM_CHANNELS? 
	BC	S6_0_DATA_N_OK			; NO: proceed
	GOTO	ERR_COMMAND			; YES: bad command - reject it!
	;
	; Do we have all the bytes yet?  (Or did a data byte happen to equal our sentinel?)
	;
S6_0_DATA_N_OK:
	INCF 	INDF0, W, ACCESS		; W=N
	CPFSGT	YY_BUF_IDX, ACCESS		; if IDX > N, we're done.
	GOTO	S6_KEEP_LOOKING			; otherwise, go back and wait for more data
	; XXX Don't do this.
	;INCF	INDF0, F, ACCESS		; fix it so that YY_BUFFER[0] is N, not N-1
	;
	; start bulk update of channels
	;
	; Remember that since the protocol specifies that we get N-1 in the length field,
	; we will always have at least 1 channel to change.  (There's no way to specify a
	; BULK_UPD command to change 0 channels.)
	;
	; Does the target range of channels lie entirely within the slave chip's 
	; range?  If so, just pass the whole command down to it, with starting SSR
	; number translated down to its range...
	;
	BTFSS	TARGET_SSR, NOT_MY_SSR, ACCESS
	BRA	S6_0_UPDATE_MASTER
	IF ROLE_MASTER
	 CLRWDT
	 IF HAS_STATUS_LEDS
	  SET_SSR_BLINK_FADE SSR_YELLOW		; slave activity indicator
	 ENDIF
	 MOVLW	0xB0				; command code
	 CALL	SIO_WRITE_W
	 MOVF	TARGET_SSR, W, ACCESS		; starting channel
	 SEND_8_BIT_W
	 LFSR	0, YY_BUFFER			; now write YY_BUFFER[0..YY_BUF_IDX-1]
S6_0_PD_ALL:
	 MOVF	POSTINC0, W, ACCESS
	 SEND_8_BIT_W
	 DECFSZ YY_BUF_IDX, F, ACCESS
	 BRA	S6_0_PD_ALL
	 MOVLW	0x55				; and finally the trailing sentinel byte $55.
	 CALL	SIO_WRITE_W
	 RETURN
	ELSE
	 ERR_BUG 0x03, ERR_CLASS_IN_VALID
	ENDIF

S6_0_UPDATE_MASTER:
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
	MOVFF	POSTINC0, I			; I=N counter		(I = *FSR0++ + 1)
	INCF	I, F, ACCESS			;                            \_____/
						;                               n
S6_0_UPDATE_NEXT:
	CLRF	POSTINC2, ACCESS		; clear SSR flags 	*fsr2++ = 0
	MOVFF	POSTINC0, INDF1 		; set SSR		*fsr1++ = *fsr0++
	INCF	FSR1L, F, ACCESS
	IF ROLE_MASTER				;
	 DCFSNZ	KK, F, ACCESS
	 BRA	S6_0_PASS_DOWN			; ran out of KK, send rest to slave chip
	ENDIF
	DECFSZ	I, F, ACCESS
	BRA	S6_0_UPDATE_NEXT
	RETURN

	IF ROLE_MASTER
S6_0_PASS_DOWN:
	 DCFSNZ	I, F, ACCESS			; we left before I-- happened
	 RETURN					; already out of data to send; don't bother the slave
	 IF HAS_STATUS_LEDS
	  SET_SSR_BLINK_FADE SSR_YELLOW		; slave activity indicator
	 ENDIF
	 MOVLW	0xB0				; Start command to slave with I remaining values
	 CALL	SIO_WRITE_W			
	 CLRF	WREG, ACCESS 			; target SSR always 0 in this case
	 SEND_8_BIT_W
	 DECF	I, W, ACCESS			; I channels left for slave to update, 
	 SEND_8_BIT_W 				;    protocol wants I-1
S6_0_PD_NEXT:
	 MOVF	POSTINC0, W, ACCESS
	 SEND_8_BIT_W
	 DECFSZ	I, F, ACCESS
	 BRA	S6_0_PD_NEXT
	 MOVLW	0x55				; sentinel $55 after bytes
	 CALL	SIO_WRITE_W
	 RETURN
	ENDIF
	RETURN


S6_1_DATA:
	DECFSZ	WREG, F, ACCESS
	BRA	S6_2_DATA
	;
	; S6.1: CF_CONF Command completed:
	;
	;   ___7______6______5______4______3______2______1______0__
	;  |                                  |                    |
	;  |                0                 |          7         | YY_COMMAND
	;  |______|______|______|______|______|______|______|______|
	;  |      |      |      |      |                           |
	;  |   0  |   1  |   1  |   1  |             1             | (not saved)
	;  |______|______|______|______|______|______|______|______|
	;  |      |    Sensors connected      |DMX   | DMX start   |  
	;  |   0  |   A      B      C      D  |MODE  | <8:7>       | YY_BUFFER+0
	;  |______|______|______|______|______|______|______|______|
	;  |      |                                                |
	;  |   0  |               DMX start <6:0>                  | YY_BUFFER+1
	;  |______|______|______|______|______|______|______|______|
	;  |      |                                                |
	;  |   0  |                   $3A                          | YY_BUFFER+2
	;  |______|______|______|______|______|______|______|______|
	;  |      |                                                |
	;  |   0  |                   $3B                          | YY_DATA
	;  |______|______|______|______|______|______|______|______|
	;
	; Validate inputs
	;
	MOVLW	3
	SUBWF	YY_BUF_IDX, W, ACCESS		; input bytes in packet
	BC	S6_1_VALID_1	
	GOTO	S6_KEEP_LOOKING			; input < 3? not done yet

S6_1_VALID_1:
	BZ	S6_1_VALID_2			; 
	GOTO	ERR_COMMAND			; input > 3? too big: reject

S6_1_VALID_2:
	LFSR	0, YY_BUFFER+2
	MOVF	POSTDEC0, W, ACCESS		; check 1st sentinel
	;ANDLW	0x3F
	SUBLW	0x3A
	BZ	S6_1_CONFIGURE
	GOTO	ERR_COMMAND

S6_1_CONFIGURE:
	MOVFF	POSTDEC0, DMX_SLOTL
	CLRF	DMX_SLOTH, ACCESS
	IF DMX_ENABLED
	 BTFSC	INDF0, 0, ACCESS
	 BSF	DMX_SLOTL, 7, ACCESS
	 BTFSC	INDF0, 1, ACCESS
	 BSF	DMX_SLOTH, DMX_BIT8, ACCESS
	 BTFSC	INDF0, 2, ACCESS
	 BSF	DMX_SLOTH, DMX_EN, ACCESS
	;
	; Save DMX settings to EEPROM
	;
	 BEGIN_EEPROM_WRITE EE_DMX_H
	 MOVFF	DMX_SLOTH, EEDATA
	 WRITE_EEPROM_DATA_INC
	 MOVFF	DMX_SLOTL, EEDATA
	 WRITE_EEPROM_DATA
	 END_EEPROM_WRITE
	ELSE
	 BEGIN_EEPROM_WRITE EE_DMX_H
	 CLRF EEDATA, ACCESS
	 WRITE_EEPROM_DATA_INC
	 CLRF EEDATA, ACCESS
	 WRITE_EEPROM_DATA
	 END_EEPROM_WRITE
	ENDIF
	;
	; Configure sensors
	;
	IF HAS_SENSORS
	 BSF	TRIS_SENS_A, BIT_SENS_A, ACCESS
	 BSF	TRIS_SENS_B, BIT_SENS_B, ACCESS
	 BSF	TRIS_SENS_C, BIT_SENS_C, ACCESS
	 BSF	TRIS_SENS_D, BIT_SENS_D, ACCESS
	 BTFSS	INDF0, 6, ACCESS			; A 
	 BCF	TRIS_SENS_A, BIT_SENS_A, ACCESS
	 BTFSS	INDF0, 5, ACCESS			; B 
	 BCF	TRIS_SENS_B, BIT_SENS_B, ACCESS
	 BTFSS	INDF0, 4, ACCESS			; C 
	 BCF	TRIS_SENS_C, BIT_SENS_C, ACCESS
	 BTFSS	INDF0, 3, ACCESS			; D 
	 BCF	TRIS_SENS_D, BIT_SENS_D, ACCESS
	 ;
	 ; Save these settings to EEPROM
	 ;
	 BEGIN_EEPROM_WRITE EE_SENSOR_CFG
	 RRNCF	INDF0, W, ACCESS
	 RRNCF	WREG, W, ACCESS
	 RRNCF	WREG, W, ACCESS
	 ANDLW	0x0f
	 MOVFF	WREG, EEDATA
	 WRITE_EEPROM_DATA
	 END_EEPROM_WRITE
	ENDIF

	CLRF	YY_STATE, ACCESS
	RETURN

S6_2_DATA:
	DECFSZ	WREG, F, ACCESS
	BRA	S6_3_DATA
	;
	; S6.2: CF_BAUD Command completed:
	;
	;   ___7______6______5______4______3______2______1______0__
	;  |                                  |                    |
	;  |                0                 |          7         | YY_COMMAND
	;  |______|______|______|______|______|______|______|______|
	;  |      |      |      |      |                           |
	;  |   0  |   1  |   1  |   1  |             2             | (not saved)
	;  |______|______|______|______|______|______|______|______|
	;  |      |                                                |  
	;  |   0  |              baud rate code                    | YY_BUFFER+0
	;  |______|______|______|______|______|______|______|______|
	;  |      |                                                |
	;  |   0  |                   $26                          | YY_DATA
	;  |______|______|______|______|______|______|______|______|
	;
	; Validate inputs
	;
	MOVLW	1
	SUBWF	YY_BUF_IDX, W, ACCESS		; input bytes in packet
	BC	S6_2_VALID1
	GOTO	S6_KEEP_LOOKING			; input < 1? not done yet

S6_2_VALID1:
	BZ	S6_2_VALID2
	GOTO	ERR_COMMAND			; input > 1? too big: reject

S6_2_VALID2:
	LFSR	0, YY_BUFFER
	MOVLW	0x11
	SUBWF	INDF0, W, ACCESS		; test baud rate in range [$00,$10]
	BNC	S6_2_SET_BAUD
	GOTO	ERR_COMMAND

S6_2_SET_BAUD:
	;
	; Change the baud rate in the slave first, or we'll
	; never be able to talk to it again...
	;
	; limit baud rate value 
	; XXX UPDATE THIS FOR CURRENT BAUD RATE LIST!
	MOVLW	0x0F
	ANDWF	INDF0, F, ACCESS
	IF ROLE_MASTER
	 IF HAS_STATUS_LEDS
	  SET_SSR_BLINK_FADE SSR_YELLOW	; slave activity indicator
	 ENDIF
	 MOVLW 	0xF0				; F0 72 <baud> 26  -> slave
	 CALL	SIO_WRITE_W
	 MOVLW 	0x72
	 CALL	SIO_WRITE_W
	 MOVF	INDF0, W, ACCESS
	 CALL	SIO_WRITE_W
	 MOVLW	0x26
	 CALL	SIO_WRITE_W
	 CALL	DRAIN_M_S_TX_BLOCKING		; wait for command to slave to be fully sent
	ENDIF					; before changing the UART speed on it.

	BEGIN_EEPROM_WRITE EE_BAUD
	MOVFF	INDF0, EEDATA			; save value permanently (address 001)
	WRITE_EEPROM_DATA
	END_EEPROM_WRITE
	MOVF	INDF0, W, ACCESS
	CALL	SIO_SET_BAUD_W
	CLRF	YY_STATE, ACCESS
	RETURN

S6_3_DATA:
	DECFSZ	WREG, F, ACCESS
	BRA	S6_4_DATA
	;
	; S6.3: CF_RESET Command completed:
	;
	;   ___7______6______5______4______3______2______1______0__
	;  |                                  |                    |
	;  |                0                 |          7         | YY_COMMAND
	;  |______|______|______|______|______|______|______|______|
	;  |      |      |      |      |                           |
	;  |   0  |   1  |   1  |   1  |             3             | (not saved)
	;  |______|______|______|______|______|______|______|______|
	;  |      |                                                |
	;  |   0  |                   $24                          | YY_BUFFER+0
	;  |______|______|______|______|______|______|______|______|
	;  |      |                                                |
	;  |   0  |                   $72                          | YY_DATA
	;  |______|______|______|______|______|______|______|______|
	;
	; Validate inputs
	;
	MOVLW	1
	SUBWF	YY_BUF_IDX, W, ACCESS		; input bytes in packet
	BC	S6_3_VALID	
	GOTO	S6_KEEP_LOOKING			; input < 1? not done yet

S6_3_VALID:
	BZ	S6_3_RESET
	GOTO	ERR_COMMAND			; input > 1? too big: reject

S6_3_RESET:
	LFSR	0, YY_BUFFER
	MOVLW	0x24
	CPFSEQ	INDF0, ACCESS
	GOTO	ERR_COMMAND
	GOTO	FACTORY_RESET			; we never return from here
	ERR_BUG	0x70, ERR_CLASS_FATAL_RESET	

S6_3_HALT:
	BRA	S6_3_HALT

S6_4_DATA:
	DECFSZ	WREG, F, ACCESS
	BRA	S6_5_DATA
	;
	; S6.4: CF_PHASE Command completed:
	;
	;   ___7______6______5______4______3______2______1______0__
	;  |                                  |                    |
	;  |                0                 |          7         | YY_COMMAND
	;  |______|______|______|______|______|______|______|______|
	;  |      |      |      |      |             | phase       |
	;  |   0  |   1  |   0  |   0  |   X      X  |  <8:7>      | YY_YY
	;  |______|______|______|______|______|______|______|______|
	;  |      |                                                |
	;  |   0  |               phase <6:0>                      | YY_BUFFER+0
	;  |______|______|______|______|______|______|______|______|
	;  |      |                                                |
	;  |   0  |                   $50                          | YY_BUFFER+1
	;  |______|______|______|______|______|______|______|______|
	;  |      |                                                |
	;  |   0  |                   $4F                          | YY_DATA
	;  |______|______|______|______|______|______|______|______|
	;
	; Validate inputs
	;
	MOVLW	2
	SUBWF	YY_BUF_IDX, W, ACCESS		; input bytes in packet
	BC	S6_4_VALID
	GOTO	S6_KEEP_LOOKING			; input < 2? not done yet

S6_4_VALID:
	BZ	S6_4_SET_PHASE
	GOTO	ERR_COMMAND			; input > 2? too big: reject

S6_4_SET_PHASE:
	LFSR	0, YY_BUFFER+1
	MOVLW	0x50
	CPFSEQ	POSTDEC0, ACCESS
	GOTO	ERR_COMMAND
	;
	; Set phase (and notify slave)
	;
	IF ROLE_MASTER
	 IF HAS_STATUS_LEDS
	  SET_SSR_BLINK_FADE SSR_YELLOW	; slave activity indicator
	 ENDIF
	 MOVLW	0xF0
	 CALL	SIO_WRITE_W
	 MOVF	YY_YY, W, ACCESS
	 SEND_8_BIT_W
	 ;CALL	SIO_WRITE_W
	 MOVF	INDF0, W, ACCESS
	 SEND_8_BIT_W
	 ;CALL	SIO_WRITE_W
	 MOVLW	0x50
	 CALL	SIO_WRITE_W
	 MOVLW	0x4F
	 CALL	SIO_WRITE_W
	ENDIF
	MOVFF	INDF0, PHASE_OFFSETL
	BTFSC	YY_YY, 0, ACCESS
	BSF	PHASE_OFFSETL, 7, ACCESS
	CLRF	PHASE_OFFSETH, ACCESS
	BTFSC	YY_YY, 1, ACCESS
	BSF	PHASE_OFFSETH, 0, ACCESS
	BEGIN_EEPROM_WRITE EE_PHASE_H
	MOVFF	PHASE_OFFSETH, EEDATA
	WRITE_EEPROM_DATA
	SET_EEPROM_ADDRESS EE_PHASE_L
	MOVFF	PHASE_OFFSETL, EEDATA
	WRITE_EEPROM_DATA
	END_EEPROM_WRITE
	CLRF	YY_STATE, ACCESS
	RETURN
	
S6_5_DATA:
	DECFSZ	WREG, F, ACCESS
	BRA	S6_6_DATA
	;
	; S6.5: CF_ADDR Command completed:
	;
	;   ___7______6______5______4______3______2______1______0__
	;  |                                  |                    |
	;  |                0                 |          7         | YY_COMMAND
	;  |______|______|______|______|______|______|______|______|
	;  |      |      |      |      |                           |
	;  |   0  |   1  |   1  |   0  |    new device address     | YY_YY      
	;  |______|______|______|______|______|______|______|______|
	;  |      |                                                |
	;  |   0  |                   $49                          | YY_BUFFER+0
	;  |______|______|______|______|______|______|______|______|
	;  |      |                                                |
	;  |   0  |                   $41                          | YY_BUFFER+1
	;  |______|______|______|______|______|______|______|______|
	;  |      |                                                |
	;  |   0  |                   $44                          | YY_DATA
	;  |______|______|______|______|______|______|______|______|
	;
	; Validate inputs
	;
	MOVLW	2
	SUBWF	YY_BUF_IDX, W, ACCESS		; input bytes in packet
	BC	S6_5_VALID
	GOTO	S6_KEEP_LOOKING			; input < 2? not done yet

S6_5_VALID:
	BZ	S6_5_ADDR
	GOTO	ERR_COMMAND			; input > 2? too big: reject

S6_5_ADDR:
	LFSR	0, YY_BUFFER+1
	MOVLW	0x41
	CPFSEQ	POSTDEC0, ACCESS
	GOTO	ERR_COMMAND
	MOVLW	0x49
	CPFSEQ	INDF0, ACCESS
	GOTO	ERR_COMMAND
	;
	; set address
	;
	MOVF	YY_YY, W, ACCESS
	ANDLW	0x0F
	MOVWF	MY_ADDRESS, ACCESS
	BEGIN_EEPROM_WRITE EE_DEV_ID
	MOVFF	MY_ADDRESS, EEDATA
	WRITE_EEPROM_DATA
	END_EEPROM_WRITE
	CLRF	YY_STATE, ACCESS
	RETURN

S6_6_DATA:
	DECFSZ	WREG, F, ACCESS
	BRA	S6_7_DATA
	;
	; S6.6: SLEEP Command completed:
	;
	;   ___7______6______5______4______3______2______1______0__
	;  |                                  |                    |
	;  |                0                 |          7         | YY_COMMAND
	;  |______|______|______|______|______|______|______|______|
	;  |      |      |      |      |                           |
	;  |   0  |   0  |   0  |   0  |             0             | (not saved)
	;  |______|______|______|______|______|______|______|______|
	;  |      |                                                |
	;  |   0  |                   $5A                          | YY_BUFFER+0
	;  |______|______|______|______|______|______|______|______|
	;  |      |                                                |
	;  |   0  |                   $5A                          | YY_DATA
	;  |______|______|______|______|______|______|______|______|
	;
	; Validate inputs
	;
	MOVLW	1
	SUBWF	YY_BUF_IDX, W, ACCESS		; input bytes in packet
	BC	S6_6_VALID
	GOTO	S6_KEEP_LOOKING			; input < 1? not done yet

S6_6_VALID:
	BZ	S6_6_SLEEP
	GOTO	ERR_COMMAND			; input > 1? too big: reject

S6_6_SLEEP:
	LFSR	0, YY_BUFFER
	MOVLW	0x5A
	CPFSEQ	INDF0, ACCESS
	GOTO	ERR_COMMAND
	CLRF 	YY_STATE, ACCESS
DO_CMD_SLEEP:
	BTFSC	SSR_STATE, PRIV_MODE, ACCESS	; don't sleep in priv mode
	RETURN
	;
	; Pass command to slave
	;
	IF ROLE_MASTER
	 IF HAS_STATUS_LEDS
	  SET_SSR_BLINK_FADE SSR_YELLOW	; slave activity indicator
	 ENDIF
	 MOVLW	0xF0
	 CALL	SIO_WRITE_W
	 CLRF	WREG, ACCESS
	 CALL 	SIO_WRITE_W
	 MOVLW	0x5A
	 CALL 	SIO_WRITE_W
	 MOVLW	0x5A
	 CALL 	SIO_WRITE_W
	ENDIF
	;
	; Tell power supply to sleep
	;
	IF HAS_POWER_CTRL
	 BSF	PLAT_PWR_ON, BIT_PWR_ON, ACCESS
	ENDIF
	IF HAS_STATUS_LEDS
	 SET_SSR_SLOW_FLASH SSR_GREEN
	 SET_SSR_SLOW_FLASH SSR_YELLOW
	 SET_SSR_SLOW_FLASH SSR_RED
	ENDIF
	BSF	SSR_STATE, SLEEP_MODE, ACCESS
	RETURN

S6_7_DATA:
	DECFSZ	WREG, F, ACCESS
	BRA	S6_8_DATA
	;
	; S6.7: WAKE Command completed:
	;
	;   ___7______6______5______4______3______2______1______0__
	;  |                                  |                    |
	;  |                0                 |          7         | YY_COMMAND
	;  |______|______|______|______|______|______|______|______|
	;  |      |      |      |      |                           |
	;  |   0  |   0  |   0  |   0  |             1             | (not saved)
	;  |______|______|______|______|______|______|______|______|
	;  |      |                                                |
	;  |   0  |                   $5A                          | YY_BUFFER+0
	;  |______|______|______|______|______|______|______|______|
	;  |      |                                                |
	;  |   0  |                   $5A                          | YY_DATA
	;  |______|______|______|______|______|______|______|______|
	;
	; Validate inputs
	;
	MOVLW	1
	SUBWF	YY_BUF_IDX, W, ACCESS		; input bytes in packet
	BC	S6_7_VALID
	GOTO	S6_KEEP_LOOKING			; input < 1? not done yet

S6_7_VALID:
	BZ	S6_7_WAKE
	GOTO	ERR_COMMAND			; input > 1? too big: reject

S6_7_WAKE:
	LFSR	0, YY_BUFFER
	MOVLW	0x5A
	CPFSEQ	INDF0, ACCESS
	GOTO	ERR_COMMAND
	CLRF 	YY_STATE, ACCESS

DO_CMD_WAKE:
	;
	; Pass command to slave
	;
	IF ROLE_MASTER
 	 IF HAS_STATUS_LEDS
	  SET_SSR_BLINK_FADE SSR_YELLOW	; slave activity indicator
	 ENDIF
	 MOVLW	0xF0
	 CALL	SIO_WRITE_W
	 MOVLW	0x01
	 CALL 	SIO_WRITE_W
	 MOVLW	0x5A
	 CALL 	SIO_WRITE_W
	 MOVLW	0x5A
	 CALL 	SIO_WRITE_W
	ENDIF
	;
	; Tell power supply to wake up
	;
	IF HAS_POWER_CTRL
	 BCF	PLAT_PWR_ON, BIT_PWR_ON, ACCESS
	ENDIF
	IF HAS_STATUS_LEDS
	 ;SET_SSR_SLOW_FADE SSR_GREEN
	 SET_SSR_NORMAL_MODE SSR_GREEN
	ENDIF
	; If in DMX mode, use slower green LED pattern
	IF DMX_ENABLED
	 BTFSS	DMX_SLOTH, DMX_SPEED, ACCESS
	 BRA	S6_8_X
	ENDIF
	IF HAS_STATUS_LEDS
	 ;SET_SSR_PATTERN SSR_GREEN, 0, 1, 3, BIT_FADE_UP|BIT_FADE_CYCLE
	 SET_SSR_DMX_MODE SSR_GREEN
	ENDIF
S6_8_X:
	IF HAS_STATUS_LEDS
	 SET_SSR_OFF SSR_YELLOW
	 SET_SSR_OFF SSR_RED
	ENDIF
	BCF	SSR_STATE, SLEEP_MODE, ACCESS
	SETF	AUTO_OFF_CTRH, ACCESS
	SETF	AUTO_OFF_CTRL, ACCESS
	RETURN

S6_8_DATA:
	DECFSZ	WREG, F, ACCESS
	BRA	S6_9_DATA
	;
	; S6.8: SHUTDOWN Command completed:
	;
	;   ___7______6______5______4______3______2______1______0__
	;  |                                  |                    |
	;  |                0                 |          7         | YY_COMMAND
	;  |______|______|______|______|______|______|______|______|
	;  |      |      |      |      |                           |
	;  |   0  |   0  |   0  |   0  |             2             | (not saved)
	;  |______|______|______|______|______|______|______|______|
	;  |      |                                                |
	;  |   0  |                   $58                          | YY_BUFFER
	;  |______|______|______|______|______|______|______|______|
	;  |      |                                                |
	;  |   0  |                   $59                          | YY_DATA
	;  |______|______|______|______|______|______|______|______|
	;
	; Validate inputs
	;
	MOVLW	1
	SUBWF	YY_BUF_IDX, W, ACCESS		; input bytes in packet
	BC	S6_8_VALID
	GOTO	S6_KEEP_LOOKING			; input < 1? not done yet

S6_8_VALID:
	BZ	S6_8_SHUTDOWN
	GOTO	ERR_COMMAND			; input > 1? too big: reject

S6_8_SHUTDOWN:
	LFSR	0, YY_BUFFER
	MOVLW	0x58
	CPFSEQ	INDF0, ACCESS
	GOTO	ERR_COMMAND
	;	
	; shutdown
	;
	GOTO	HALT_MODE

S6_9_DATA:
	DECFSZ	WREG, F, ACCESS
	BRA	S6_10_DATA
	;
	; S6.9: QUERY Command completed:
	;
	;   ___7______6______5______4______3______2______1______0__
	;  |                                  |                    |
	;  |                0                 |          7         | YY_COMMAND
	;  |______|______|______|______|______|______|______|______|
	;  |      |      |      |      |                           |
	;  |   0  |   0  |   0  |   0  |             3             | (not saved)
	;  |______|______|______|______|______|______|______|______|
	;  |      |                                                |
	;  |   0  |                   $24                          | YY_BUFFER+0
	;  |______|______|______|______|______|______|______|______|
	;  |      |                                                |
	;  |   0  |                   $54                          | YY_DATA
	;  |______|______|______|______|______|______|______|______|
	;
	; Validate inputs
	;
	MOVLW	1
	SUBWF	YY_BUF_IDX, W, ACCESS		; input bytes in packet
	BC	S6_9_VALID
	GOTO	S6_KEEP_LOOKING			; input < 1? not done yet

S6_9_VALID:
	BZ	S6_9_QUERY
	GOTO	ERR_COMMAND			; input > 1? too big: reject

S6_9_QUERY:
	LFSR	0, YY_BUFFER
	MOVLW	0x24
	CPFSEQ	INDF0, ACCESS
	GOTO	ERR_COMMAND
	;
	; return status of unit
	;
	IF ROLE_MASTER
	 IF HAS_STATUS_LEDS
	  SET_SSR_BLINK_FADE SSR_YELLOW	; slave activity indicator
	 ENDIF
	 MOVLW	0xF0			; initiate write-through IC_TXSTA command
	 CALL	SIO_WRITE_W		; to slave CPU
	 MOVLW	0x23
	 CALL	SIO_WRITE_W
	 MOVLW	.30			; write 31-byte packet
	 CALL	SIO_WRITE_W
	ELSE
	 IF ROLE_STANDALONE
	  CALL	TR_ON_DELAY
	  BSF	PLAT_T_R, BIT_T_R, ACCESS		; Fire up our transmitter now
	  BCF	SSR_STATE2, INHIBIT_OUTPUT, ACCESS	; Allow sending output
	 ELSE
	  ERR_BUG 0x0F, ERR_CLASS_INT_COMMAND
	 ENDIF
	ENDIF
	MOVF	MY_ADDRESS, W, ACCESS
	IORLW	0xF0
	IF ROLE_MASTER
	 BCF	WREG, 7, ACCESS
	ENDIF
	CALL	SIO_WRITE_W			; 00 start byte 			<1111aaaa>
	MOVLW	0x1F
	SEND_8_BIT_W				; 01 "reply to query" packet type 	<00011111>
	MOVLW	0x31
	SEND_8_BIT_W				; 02 ROM/format version 3.1		<00110001>
	CLRF	WREG, ACCESS
	IF HAS_SENSORS
	 BTFSC	TRIS_SENS_A, BIT_SENS_A, ACCESS	; If sensor A is enabled on this board,
	 BSF	WREG, 6, ACCESS			; set the Sc bit for that sensor.
	 BTFSC	TRIS_SENS_B, BIT_SENS_B, ACCESS	; and for sensor B
	 BSF	WREG, 5, ACCESS			; 
	 BTFSC	TRIS_SENS_C, BIT_SENS_C, ACCESS	; and for sensor C
	 BSF	WREG, 4, ACCESS			; 
	 BTFSC	TRIS_SENS_D, BIT_SENS_D, ACCESS	; and for sensor D
	 BSF	WREG, 3, ACCESS			; 
	ENDIF               			; W=0ABCD---  1=sensor configured; 0=LED
	IF DMX_ENABLED
	 BTFSC	DMX_SLOTH, DMX_EN, ACCESS
	 BSF	WREG, 2, ACCESS			;   0----d--  DMX enable bit
	 BTFSC	DMX_SLOTH, DMX_BIT8, ACCESS
	 BSF	WREG, 1, ACCESS			;   0-----c-  DMX channel bit 8
	 BTFSC	DMX_SLOTL, 7, ACCESS		; 
	 BSF	WREG, 0, ACCESS			;   0------c  DMX channel bit 7
	ENDIF
	SEND_8_BIT_W				; 03 sensor, DMX status            	<0ABCDdcc> 
	IF DMX_ENABLED
	 MOVF	DMX_SLOTL, W, ACCESS		;   0ccccccc  DMX channel bits 6:0
	 ANDLW	0x7F
	ELSE
	 CLRF	WREG, ACCESS
	ENDIF
	SEND_8_BIT_W				; 04 DMX status
	CLRF	WREG, ACCESS
	BTFSC	SSR_STATE, PRIV_MODE, ACCESS	; W=00000qs0
	BSF	WREG, 2, ACCESS
	BTFSC	SSR_STATE, SLEEP_MODE, ACCESS
	BSF	WREG, 1, ACCESS
	SEND_8_BIT_W
	;CALL	SIO_WRITE_W			; 05 masks, priv, sleep, mem full	<0ABCDqsf> XXX NOT ALL IMPLEMENTED
	CLRF	WREG, ACCESS
	IF HAS_SENSORS
	 MOVLW	0x78				; Initially set all sensors to 1
	 BTFSC	TRIS_SENS_A, BIT_SENS_A, ACCESS	; If that line is not a sensor... 
	 BTFSC	PORT_SENS_A, BIT_SENS_A, ACCESS ; Or the sensor is not pulled low...
	 BCF	WREG, 6, ACCESS			; Then clear the reported flag.
	 BTFSC	TRIS_SENS_B, BIT_SENS_B, ACCESS	
	 BTFSC	PORT_SENS_B, BIT_SENS_B, ACCESS 
	 BCF	WREG, 5, ACCESS			
	 BTFSC	TRIS_SENS_C, BIT_SENS_C, ACCESS	
	 BTFSC	PORT_SENS_C, BIT_SENS_C, ACCESS 
	 BCF	WREG, 4, ACCESS			
	 BTFSC	TRIS_SENS_D, BIT_SENS_D, ACCESS	
	 BTFSC	PORT_SENS_D, BIT_SENS_D, ACCESS 
	 BCF	WREG, 3, ACCESS			; W=0ABCD---  1=sensor active (low) 0=inactive (high)
	ENDIF
	BTFSC	SSR_STATE2, PRIV_FORBID, ACCESS
	BSF	WREG, 2, ACCESS			
	BTFSC	PHASE_OFFSETH, 0, ACCESS
	BSF	WREG, 1, ACCESS
	BTFSC	PHASE_OFFSETL, 7, ACCESS
	BSF	WREG, 0, ACCESS
	SEND_8_BIT_W
	;CALL	SIO_WRITE_W			; 06 active sensors, xpriv, phase<8:7>	<0ABCDXpp> XXX NOT ALL IMPLEMENTED
	MOVF	PHASE_OFFSETL, W, ACCESS
	BCF	WREG, 7, ACCESS
	SEND_8_BIT_W
	;CALL	SIO_WRITE_W			; 07 phase <6:0>			<0ppppppp>
	CLRF	WREG, ACCESS
	CALL	SIO_WRITE_W			; 08 eeprom memory free <14:7>		<0eeeeeee> XXX NOT IMPLEMENTED
	CLRF	WREG, ACCESS
	CALL	SIO_WRITE_W			; 09 eeprom memory free <6:0>		<0eeeeeee> XXX NOT IMPLEMENTED
	CLRF	WREG, ACCESS
	CALL	SIO_WRITE_W			; 10 RAM memory free <14:7>		<0MMMMMMM> XXX NOT IMPLEMENTED
	CLRF	WREG, ACCESS
	CALL	SIO_WRITE_W			; 11 RAM memory free <6:0>		<0MMMMMMM> XXX NOT IMPLEMENTED
	IF LUMOS_CHIP_TYPE == LUMOS_CHIP_MASTER
	 MOVLW	0x00
	ELSE
	 IF LUMOS_CHIP_TYPE == LUMOS_CHIP_STANDALONE
	  MOVLW 0x01
	 ELSE
	  IF LUMOS_CHIP_TYPE == LUMOS_CHIP_4CHANNEL
	   MOVLW 0x02
	  ELSE
	   IF LUMOS_CHIP_TYPE == LUMOS_CHIP_QSCC
	    MOVLW 0x03
	   ELSE
	    IF LUMOS_CHIP_TYPE == LUMOS_CHIP_QSRC
	     MOVLW 0x04
	    ELSE
	     ERROR "Invalid chip type selected"
	     ERR_BUG 0x10, ERR_CLASS_DEVICE
	    ENDIF
	   ENDIF
	  ENDIF
	 ENDIF
	ENDIF
	SEND_8_BIT_W
	;CALL	SIO_WRITE_W			; 12 sequence flag, device ID		<0X0iiiii> XXX NOT ALL IMPLEMENTED
	CLRF	WREG, ACCESS
	CALL	SIO_WRITE_W			; 13 executing sequence			<0xxxxxxx> XXX NOT IMPLEMENTED

	MOVLW	0x00
	CALL	SIO_WRITE_W			; 14 sensor A settings 			<0owE0000> XXX NOT IMPLEMENTED
	MOVLW	0x00
	CALL	SIO_WRITE_W			; 15 sensor A pre-sequence		<0IIIIIII> XXX NOT IMPLEMENTED
	MOVLW	0x00
	CALL	SIO_WRITE_W			; 16 sensor A sequence			<0iiiiiii> XXX NOT IMPLEMENTED
	MOVLW	0x00
	CALL	SIO_WRITE_W			; 17 sensor A post-sequence		<0PPPPPPP> XXX NOT IMPLEMENTED

	MOVLW	0x01
	CALL	SIO_WRITE_W			; 18 sensor B settings 			<0owE0001> XXX NOT IMPLEMENTED
	MOVLW	0x00
	CALL	SIO_WRITE_W			; 19 sensor B pre-sequence		<0IIIIIII> XXX NOT IMPLEMENTED
	MOVLW	0x00
	CALL	SIO_WRITE_W			; 20 sensor B sequence			<0iiiiiii> XXX NOT IMPLEMENTED
	MOVLW	0x00
	CALL	SIO_WRITE_W			; 21 sensor B post-sequence		<0PPPPPPP> XXX NOT IMPLEMENTED

	MOVLW	0x02
	CALL	SIO_WRITE_W			; 22 sensor C settings 			<0owE0010> XXX NOT IMPLEMENTED
	MOVLW	0x00
	CALL	SIO_WRITE_W			; 23 sensor C pre-sequence		<0IIIIIII> XXX NOT IMPLEMENTED
	MOVLW	0x00
	CALL	SIO_WRITE_W			; 24 sensor C sequence			<0iiiiiii> XXX NOT IMPLEMENTED
	MOVLW	0x00
	CALL	SIO_WRITE_W			; 25 sensor C post-sequence		<0PPPPPPP> XXX NOT IMPLEMENTED

	MOVLW	0x03
	CALL	SIO_WRITE_W			; 26 sensor D settings 			<0owE0011> XXX NOT IMPLEMENTED
	MOVLW	0x00
	CALL	SIO_WRITE_W			; 27 sensor D pre-sequence		<0IIIIIII> XXX NOT IMPLEMENTED
	MOVLW	0x00
	CALL	SIO_WRITE_W			; 28 sensor D sequence			<0iiiiiii> XXX NOT IMPLEMENTED
	MOVLW	0x00
	CALL	SIO_WRITE_W			; 29 sensor D post-sequence		<0PPPPPPP> XXX NOT IMPLEMENTED
	
	MOVF	LAST_ERROR, W, ACCESS
	CLRF	LAST_ERROR, ACCESS
	SEND_8_BIT_W
	;CALL	SIO_WRITE_W			; 30 fault code				<0fffffff>
	IF ROLE_MASTER
	 MOVLW	B'00011011'
	 CALL	SIO_WRITE_W			; 31 end of packet to slave chip
	ELSE
	 CLRF	WREG, ACCESS
	 CALL 	SIO_WRITE_W			; 31 (nil) slave fault code
	 CLRF	WREG, ACCESS	
	 CALL	SIO_WRITE_W			; 32 (nil) slave phase offset <8:7>
	 CLRF	WREG, ACCESS	
	 CALL	SIO_WRITE_W			; 33 (nil) slave phase offset <6:0>
	 MOVLW	UPPER(SYS_SNH)
	 MOVWF	TBLPTRU, ACCESS
	 MOVLW	HIGH(SYS_SNH)
	 MOVWF	TBLPTRH, ACCESS
	 MOVLW	LOW(SYS_SNH)
	 MOVWF	TBLPTRL, ACCESS
	 TBLRD*+
	 MOVF	TABLAT, W, ACCESS
	 SEND_8_BIT_W				; 34 Serial Number (MSB)
	 TBLRD*+
	 MOVF	TABLAT, W, ACCESS
	 SEND_8_BIT_W				; 35 Serial Number (LSB)
	 MOVLW	0x33
	 CALL	SIO_WRITE_W			; 36 sentinel at end of packet
	 BSF	SSR_STATE, DRAIN_TR, ACCESS	; schedule transmitter shut-down
	ENDIF
	CLRF	YY_STATE, ACCESS
	RETURN
	
S6_10_DATA:
	DECFSZ	WREG, F, ACCESS
	BRA	S6_11_DATA
	;
	; S6.10: DEF_SENS Command completed:
	;
	;   ___7______6______5______4______3______2______1______0__
	;  |                                  |                    |
	;  |                0                 |          7         | YY_COMMAND
	;  |______|______|______|______|______|______|______|______|
	;  |      |      |      |      |                           |
	;  |   0  |   0  |   0  |   0  |             6             | (not saved)
	;  |______|______|______|______|______|______|______|______|
	;  |      |    Trigger modes   |             |             |  
	;  |   0  | once | while|1=high|      0      |    sensor   | YY_BUFFER+0
	;  |______|______|______|______|______|______|______|______|
	;  |      |                                                |
	;  |   0  |           pre-trigger sequence ID              | YY_BUFFER+1
	;  |______|______|______|______|______|______|______|______|
	;  |      |                                                |
	;  |   0  |               trigger sequence ID              | YY_BUFFER+2
	;  |______|______|______|______|______|______|______|______|
	;  |      |                                                |
	;  |   0  |          post-trigger sequence ID              | YY_BUFFER+3
	;  |______|______|______|______|______|______|______|______|
	;  |      |                                                |
	;  |   0  |                   $3C                          | YY_DATA
	;  |______|______|______|______|______|______|______|______|
	;
	;
	MOVLW	4
	SUBWF	YY_BUF_IDX, W, ACCESS		; input bytes in packet
	BC	S6_10_VALID
	GOTO	S6_KEEP_LOOKING			; input < 4? not done yet

S6_10_VALID:
	BZ	S6_10_DEF_SENS
	GOTO	ERR_COMMAND			; input > 4? too big: reject

S6_10_DEF_SENS:
	LFSR	0, YY_BUFFER
	GOTO	ERR_NOT_IMP		; XXX
	
S6_11_DATA:
	DECFSZ	WREG, F, ACCESS
	BRA	S6_12_DATA
	;
	; S6.11: CLR_SEQ Command completed:
	;
	;   ___7______6______5______4______3______2______1______0__
	;  |                                  |                    |
	;  |                0                 |          7         | YY_COMMAND
	;  |______|______|______|______|______|______|______|______|
	;  |      |      |      |      |                           |
	;  |   0  |   0  |   0  |   0  |             8             | (not saved)
	;  |______|______|______|______|______|______|______|______|
	;  |      |                                                |
	;  |   0  |                   $43                          | YY_BUFFER
	;  |______|______|______|______|______|______|______|______|
	;  |      |                                                |
	;  |   0  |                   $41                          | YY_DATA
	;  |______|______|______|______|______|______|______|______|
	;
	; Validate inputs
	;
	MOVLW	1
	SUBWF	YY_BUF_IDX, W, ACCESS		; input bytes in packet
	BC	S6_11_VALID
	GOTO	S6_KEEP_LOOKING			; input < 1? not done yet

S6_11_VALID:
	BZ	S6_11_CLR_SEQ
	GOTO	ERR_COMMAND			; input > 1? too big: reject

S6_11_CLR_SEQ:
	LFSR	0, YY_BUFFER
	MOVLW	0x43
	CPFSEQ	INDF0, ACCESS
	GOTO	ERR_COMMAND
	GOTO	ERR_NOT_IMP		; XXX

S6_12_DATA:
	DECFSZ	WREG, F, ACCESS
	BRA	S6_13_DATA
	;
	; S6.12: DEF_SEQ Command completed:
	;
	;   ___7______6______5______4______3______2______1______0__
	;  |                                  |                    |
	;  |                0                 |          7         | YY_COMMAND
	;  |______|______|______|______|______|______|______|______|
	;  |      |      |      |      |                           |
	;  |   0  |   0  |   0  |   0  |             0             | (not saved)
	;  |______|______|______|______|______|______|______|______|
	;  |      |                                                |
	;  |   0  |               sequence number                  | YY_YY
	;  |______|______|______|______|______|______|______|______|
	;  |      |                                                |
	;  |   0  |             sequence length - 1 (N-1)          | YY_BUFFER+0
	;  |______|______|______|______|______|______|______|______|
	;  |      |                                                |
	;  |   0  |              byte #0                           | YY_BUFFER+1
	;  |______|______|______|______|______|______|______|______|
	;                              .
	;                              .
	;                              .
	;  _________________________________________________________
	;  |      |                                                |
	;  |   0  |              byte #N-1                         | YY_BUFFER+N
	;  |______|______|______|______|______|______|______|______|
	;  |      |                                                |
	;  |   0  |                   $44                          | YY_BUFFER+N+1
	;  |______|______|______|______|______|______|______|______|
	;  |      |                                                |
	;  |   0  |                   $73                          | YY_DATA
	;  |______|______|______|______|______|______|______|______|
	;
	; Validate inputs
	; first, do we even have a full packet yet?
	;
	MOVF	YY_BUF_IDX, W, ACCESS
	BNZ	S6_12_VALID
	GOTO	S6_KEEP_LOOKING			

S6_12_VALID:
	LFSR	0, YY_BUFFER
	INCF	INDF0, W, ACCESS
	INCF	WREG, W, ACCESS
	INCF	WREG, W, ACCESS		; W = (N-1)+3 = size our packet must be
	SUBWF	YY_BUF_IDX, W, ACCESS	; bytes read < W?
	BC	S6_12_VALID2
	GOTO	S6_KEEP_LOOKING		; yes, keep reading more

S6_12_VALID2:
	BZ	S6_12_DEF_SEQ
	GOTO	ERR_COMMAND		; if read too much, reject command

S6_12_DEF_SEQ:
	;
	; next, test sentinel
	;
	DECF	YY_BUF_IDX, W, ACCESS
	ADDWF	FSR0L, F, ACCESS
	MOVLW	0x44
	CPFSEQ	INDF0			; sentinel==$44?
	GOTO	ERR_COMMAND
	;
	; ok, define the sequence now
	;
	GOTO	ERR_NOT_IMP		; XXX
	
S6_13_DATA:
	DECFSZ	WREG, F, ACCESS
	BRA	S6_14_DATA
	;
	; S6.13: CF_FLROM Command completed:
	;
	;   ___7______6______5______4______3______2______1______0__
	;  |                                  |                    |
	;  |                0                 |          7         | YY_COMMAND
	;  |______|______|______|______|______|______|______|______|
	;  |      |      |      |      |                           |
	;  |   0  |   1  |   1  |   1  |             5             | (not saved)
	;  |______|______|______|______|______|______|______|______|
	;  |      |                                                |
	;  |   0  |                   $33                          | YY_BUFFER+0
	;  |______|______|______|______|______|______|______|______|
	;  |      |                                                |
	;  |   0  |                   $4C                          | YY_BUFFER+1
	;  |______|______|______|______|______|______|______|______|
	;  |      |                                                |
	;  |   0  |                   $1C                          | YY_DATA
	;  |______|______|______|______|______|______|______|______|
	;
	; Validate inputs
	;
	MOVLW	2
	SUBWF	YY_BUF_IDX, W, ACCESS		; input bytes in packet
	BZ	S6_13_VALID			; 2 bytes received (plus final)? good.
	GOTO	ERR_COMMAND			; otherwise, it's not right.
	;
	; next, test sentinel
	;
S6_13_VALID:
	LFSR	0, YY_BUFFER
	MOVLW	0x33
	CPFSEQ	POSTINC0
	GOTO	ERR_COMMAND
	MOVLW	0x4C
	CPFSEQ	INDF0
	GOTO	ERR_COMMAND
	;
	; ok, start updating the firmware!
	;
	IF !QSCC_PORT
	 GOTO	FLASH_UPDATE_START
	ELSE
	 GOTO	ERR_COMMAND
	ENDIF

S6_14_DATA:
	IF QSCC_PORT
	 #include "qscc_hook_s6_14.asm"
	ELSE
	 ERR_BUG 0x05, ERR_CLASS_OVERRUN
	ENDIF

S6_RESTART:
	; We stopped too early -- resume now
	RETURN					; 

S6_KEEP_LOOKING:
	MOVF	YY_BUF_IDX, W, ACCESS		; Have we reached our limit (idx >= max)?
	CPFSGT	YY_LOOKAHEAD_MAX, ACCESS	; (skip if MAX > bytes read so far)
	GOTO	ERR_COMMAND			; Yes:  Abort here and ignore data to next cmd
	LFSR	0, YY_BUFFER			; No: Save character in buffer and keep waiting
	MOVF	YY_BUF_IDX, W, ACCESS
	ADDWF	FSR0L, F, ACCESS
	MOVFF	YY_DATA, INDF0
	INCF	YY_BUF_IDX, F, ACCESS
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
	;  |                                  |                    |
	;  |                0                 |          4         | YY_COMMAND
	;  |______|______|______|______|______|______|______|______|
	;  |NOT_MY|0=down|                                         |
	;  | _SSR |1=up  |           Channel ID (0-23)             | TARGET_SSR
	;  |______|______|______|______|______|______|______|______|
	;  |                                                       |
	;  |              Steps between update (1-128)             | YY_YY
	;  |______|______|______|______|______|______|______|______|
	;  |                                                       |
	;  |             update every n/120 sec (1-128)            | YY_DATA
	;  |______|______|______|______|______|______|______|______|
	;  |YCF_  |                                                |
	;  |RAMP_ |                                                | YY_CMD_FLAGS
	;  |CYCLE_|______|______|______|______|______|______|______|
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
	BTFSC	YY_CMD_FLAGS, YCF_RAMP_CYCLE, ACCESS
	BSF	INDF0, FADE_CYCLE, ACCESS
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
	 IF HAS_STATUS_LEDS
	  SET_SSR_BLINK_FADE SSR_YELLOW	; slave activity indicator
	 ENDIF
	 MOVLW 	0xC0				; command byte
	 CALL	SIO_WRITE_W
	 BCF	TARGET_SSR, 7, ACCESS
	 BTFSC	YY_CMD_FLAGS, YCF_RAMP_CYCLE, ACCESS
	 BSF 	TARGET_SSR, 7, ACCESS
	 MOVF	TARGET_SSR, W, ACCESS
	 SEND_8_BIT_W
	 ;CALL	SIO_WRITE_W			; channel + direction
	 DECF	YY_YY, W, ACCESS		; steps - 1
	 SEND_8_BIT_W
	 ;CALL	SIO_WRITE_W
	 DECF	YY_DATA, W, ACCESS		; speed - 1
	 SEND_8_BIT_W
	 ;CALL	SIO_WRITE_W
	 CLRF	YY_STATE, ACCESS
	 RETURN
	ENDIF
	ERR_BUG	0x06, ERR_CLASS_IN_VALID
	
S9_DATA:
	DECFSZ	WREG, W, ACCESS
	BRA	S10_DATA
	;
	; State 9:  Extended command code received; decode further
	;
	;   ___7______6______5______4______3______2______1______0__
	;  |                                  |                    |
	;  |                0                 |          7         | YY_COMMAND
	;  |______|______|______|______|______|______|______|______|
	;  |                                                       |
	;  |               Extended Command Code                   | YY_DATA   
	;  |______|______|______|______|______|______|______|______|
	;
	; Extended commands decode like this:
	;	01xxxxxx	privileged configuration commands
	;	010----- 	CF_PHASE command (remaining bits are data)
	;	0110----	CF_ADDR command (remaining bits are data)
	;	0111---- 	other CF_* commands (remaining bits are command number)
	;       001-----	IC_* internal (mater->slave) commands
	;	000-----	Regular extended commands
	;        
	BTFSC	YY_DATA, 6, ACCESS
	BRA	S9_PRIV_CMD
	BTFSC	YY_DATA, 5, ACCESS
	BRA	S9_INTERNAL_CMD
	;
	; Regular extended commands
	;
	MOVF	YY_DATA, W, ACCESS
	BNZ	S9_X1_WAKE
S9_X0_SLEEP:
	WAIT_FOR_SENTINEL 2, B'01011010', 6	; -> S6.6 when sentinel found
	RETURN
S9_X1_WAKE:
	DECFSZ	WREG, W, ACCESS
	BRA	S9_X2_SHUTDOWN
	WAIT_FOR_SENTINEL 2, B'01011010', 7	; -> S6.7 when sentinel found
	RETURN
S9_X2_SHUTDOWN:
	DECFSZ	WREG, W, ACCESS
	BRA	S9_X3_QUERY
	WAIT_FOR_SENTINEL 2, B'01011001', .8	; -> S6.8 when sentinel found
	RETURN
S9_X3_QUERY:
	DECFSZ	WREG, W, ACCESS
	BRA	S9_X4_DEF_SEQ
	WAIT_FOR_SENTINEL 2, B'01010100', .9	; -> S6.9 when sentinel found
	RETURN
S9_X4_DEF_SEQ:
	DECFSZ	WREG, W, ACCESS
	BRA	S9_X5_EXEC_SEQ
	MOVLW	.14
	MOVWF	YY_STATE, ACCESS		; -> 14, wait to get I byte
	RETURN
S9_X5_EXEC_SEQ:
	DECFSZ	WREG, W, ACCESS
	BRA	S9_X6_DEF_SENS
	MOVLW	.15
	MOVWF	YY_STATE, ACCESS		; -> 15, wait to get I byte
	RETURN
S9_X6_DEF_SENS:
	DECFSZ	WREG, W, ACCESS
	BRA	S9_X7_MSK_SENS
	WAIT_FOR_SENTINEL 5, B'00111100', .10	; -> S6.10 when sentinel found
	RETURN
S9_X7_MSK_SENS:
	DECFSZ 	WREG, W, ACCESS
	BRA	S9_X8_CLR_SEQ
	MOVLW	.16
	MOVWF	YY_STATE, ACCESS		; -> 16, wait to get sensor byte
	RETURN
S9_X8_CLR_SEQ:
	DECFSZ	WREG, W, ACCESS
	BRA	S9_X9_XPRIV
	WAIT_FOR_SENTINEL 2, B'01000001', .11	; -> S6.11 when sentinel found
	RETURN
S9_X9_XPRIV:
	DECFSZ	WREG, W, ACCESS			
	BRA	S9_XA_ERR_COMMAND
	;
	; XPRIV:
	;
	;   ___7______6______5______4______3______2______1______0__
	;  |                                  |                    |
	;  |                0                 |          7         | YY_COMMAND
	;  |______|______|______|______|______|______|______|______|
	;  |      |      |      |                                  |
	;  |   0  |   0  |   0  |   0  |             9             | YY_DATA
	;  |______|______|______|______|______|______|______|______|
	;
	GOTO	CMD_XPRIV

S9_XA_ERR_COMMAND:
	IF QSCC_PORT
	 #include "qscc_hook_s9_xa.asm"
	ELSE
	 GOTO	ERR_COMMAND
	ENDIF

S9_INTERNAL_CMD:
	;
	; received internal command from master
	;
	IF !ROLE_SLAVE
	 GOTO 	ERR_COMMAND
	ELSE	; BEGIN SLAVE-SIDE INTERNAL COMMAND INTERPRETATION CODE--------
	MOVLW	0x1F			;				///////
	ANDWF	YY_DATA, W, ACCESS	;				///////
	BNZ	S9_1_IC_LED		;				///////
					;                               ///////
S9_0_IC_TXDAT:				;                               ///////
	;								///////
	; IC_TXDAT: Send byte stream to serial port			///////
	;								///////
	; wait for N byte to arrive, preserve command code in YY_COMMAND///////
	;								///////
	MOVFF	YY_DATA, YY_COMMAND	;				///////
	MOVLW	.10			;				///////
	MOVWF	YY_STATE, ACCESS	;				///////
	RETURN				;				///////
					;				///////
S9_1_IC_LED:				;				///////
	DECFSZ	WREG, W, ACCESS		;				///////
	BRA	S9_2_IC_HALT 		;				///////
	;				;				///////
	; IC_LED			;				///////
	; wait for GY byte to arrive.	;				///////
	;				;				///////
	MOVLW	.12			;				///////
	MOVWF	YY_STATE, ACCESS	;				///////
	RETURN				;				///////
					;				///////
S9_2_IC_HALT:				;				///////
	DECFSZ	WREG, W, ACCESS		;				///////
	BRA	S9_3_IC_TXSTA		;				///////
	;								///////
	; IC_HALT							///////
	;								///////
	; Close up shop.						///////
	;								///////
	IF HAS_ACTIVE			;				///////
	 SET_SSR_OFF SSR_ACTIVE		;				///////
	ENDIF				;				///////
	IF HAS_STATUS_LEDS
	 SET_SSR_OFF SSR_GREEN		; set LEDs for halt mode	///////
	 SET_SSR_OFF SSR_YELLOW		;				///////
	 SET_SSR_STEADY SSR_RED		;				///////
	ENDIF
	IF HAS_T_R			;                 _		///////
	 BCF	PLAT_T_R, BIT_T_R, ACCESS	; Clear T/R output	///////
	ENDIF				;				///////
	GOTO	HALT_MODE 		;				///////
					;				///////
S9_3_IC_TXSTA:				;				///////
	DECFSZ	WREG, W, ACCESS		;				///////
	BRA	S9_4_OVERRUN		;				///////
	;								///////
	; IC_TXSTA							///////
	; wait for N byte to arrive, preserve command code in YY_COMMAND///////
	; so we can tell if we're doing this or IC_TXDAT later.		///////
	;								///////
	MOVFF	YY_DATA, YY_COMMAND	;				///////
	MOVLW	.10			;				///////
	MOVWF	YY_STATE, ACCESS	;				///////
	RETURN				;				///////
					;				///////
S9_4_OVERRUN:				;				///////
	ERR_BUG	0x07, ERR_CLASS_OVERRUN	;				///////
	ENDIF	; END SLAVE-SIDE INTERNAL COMMAND INTERPRETATION CODE----------

	
S9_PRIV_CMD:
	; received privileged configuration command  	; 01xxxxxx
	;
	; Anything from here down requires the privilege bit to be set.
	;
	BTFSC	SSR_STATE, PRIV_MODE, ACCESS
	BRA	S9_DO_PRIV_CMD
	MOVLW	0x21
	MOVWF	LAST_ERROR, ACCESS
	GOTO	ERR_ABORT
S9_DO_PRIV_CMD:
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
	;  |                                  |                    |
	;  |                0                 |          7         | YY_COMMAND
	;  |______|______|______|______|______|______|______|______|
	;  |      |      |      |                                  |
	;  |   0  |   1  |   1  |   1  |             0             | YY_DATA
	;  |______|______|______|______|______|______|______|______|
	;
	;
	BCF	SSR_STATE, PRIV_MODE, ACCESS
	IF HAS_STATUS_LEDS
	 ;SET_SSR_SLOW_FADE SSR_GREEN
	 SET_SSR_NORMAL_MODE SSR_GREEN
	ENDIF
	IF DMX_ENABLED
	 BTFSS	DMX_SLOTH, DMX_SPEED, ACCESS
	 BRA	S9_PRIV_0X
	ENDIF
	IF HAS_STATUS_LEDS
	 ;SET_SSR_PATTERN SSR_GREEN, 0, 1, 3, BIT_FADE_UP|BIT_FADE_CYCLE
	 SET_SSR_DMX_MODE SSR_GREEN
	ENDIF

S9_PRIV_0X:
	IF ROLE_MASTER
	 IF HAS_STATUS_LEDS
	  SET_SSR_BLINK_FADE SSR_YELLOW	; slave activity indicator
	 ENDIF
	 MOVLW	0xF0					; send to slave chip: F0 21 00010111 00000111
	 CALL	SIO_WRITE_W
	 MOVLW	0x21
	 CALL	SIO_WRITE_W
	 MOVLW	0x17
	 CALL	SIO_WRITE_W
	 MOVLW	0x07
	 CALL	SIO_WRITE_W
	ENDIF
	CLRF	YY_STATE, ACCESS
	IF DMX_ENABLED
 	 CALL	DMX_RESUME
	ENDIF
	RETURN

S9_PRIV_1:
	DECFSZ	WREG, W, ACCESS
	BRA	S9_PRIV_2
	;
	; CF_CONF command recognized.  Expect packet of 4 more bytes...
	;
	WAIT_FOR_SENTINEL 4, B'00111101', 1	; -> S6.1 when sentinel found
	RETURN

S9_PRIV_2:
	DECFSZ	WREG, W, ACCESS
	BRA	S9_PRIV_3
	;
	; CF_BAUD command recognized.  Expect packet of 2 more bytes...
	;
	WAIT_FOR_SENTINEL 2, B'00100110', 2	; -> S6.2 when sentinel found
	RETURN

S9_PRIV_3:
	DECFSZ	WREG, W, ACCESS
	BRA	S9_PRIV_4
	;
	; CF_RESET command recognized.  Expect packet of 2 more bytes...
	;
	WAIT_FOR_SENTINEL 2, B'01110010', 3	; -> S6.3 when sentinel found
	RETURN

S9_PRIV_4:
	DECFSZ	WREG, W, ACCESS
	BRA	S9_PRIV_5
	;
	; CF_XPRIV:
	;
	;   ___7______6______5______4______3______2______1______0__
	;  |                                  |                    |
	;  |                0                 |          7         | YY_COMMAND
	;  |______|______|______|______|______|______|______|______|
	;  |      |      |      |                                  |
	;  |   0  |   1  |   1  |   1  |             4             | YY_DATA
	;  |______|______|______|______|______|______|______|______|
	;
	;
CMD_XPRIV:
	BSF	SSR_STATE2, PRIV_FORBID, ACCESS
	GOTO	S9_PRIV_0

S9_PRIV_5:
	DECFSZ	WREG, W, ACCESS
	BRA	S9_PRIV_6
	;
	; CF_FLROM command recognized.  Expect packet of 3 more bytes...
	;
	WAIT_FOR_SENTINEL 3, B'00011100', 13	; -> S6.13 when sentinel found
	RETURN

S9_PRIV_6:
	IF QSCC_PORT
	 #include "qscc_hook_s9_priv_6.asm"
	ELSE
	 GOTO	ERR_COMMAND
	ENDIF

S9_CF_PHASE:
	MOVFF	YY_DATA, YY_YY
	WAIT_FOR_SENTINEL 3, B'01001111', 4	; -> S6.4 when sentinel found
	RETURN

S9_CF_ADDR:
	MOVFF	YY_DATA, YY_YY
	WAIT_FOR_SENTINEL 3, B'01000100', 5	; -> S6.5 when sentinel found
	RETURN
	
S10_DATA:
	DECFSZ	WREG, W, ACCESS
	BRA	S11_DATA
	;
	; S10: IC_TXDAT / IC_TXSTA received N byte; time to loop
	; transmitting N bytes. First byte will have MSB set.
	;
	;   ___7______6______5______4______3______2______1______0__
	;  |      |                    |                           |
	;  |   1  |          7         |             0             | (not saved)
	;  |______|______|______|______|______|______|______|______|
	;  |SET   |      |      |      |    IC_TXDAT:   0          |
	;  |MSB?  |   0  |   1  |   0  |    IC_TXSTA:   3          | YY_COMMAND 
	;  |______|______|______|______|______|______|______|______|
	;  |                                                       |  
	;  |                Bytes to transmit  (N)                 | YY_YY
	;  |______|______|______|______|______|______|______|______|
	;  |      |                                                |
	;  |   0  |                 Data byte #0                   | (not yet received)
	;  |______|______|______|______|______|______|______|______|
	;                              .
	;                              .                                    
	;                              .
	;   _______________________________________________________
	;  |      |                                                |
	;  |   0  |                 Data byte #N-1                 | (not yet received)
	;  |______|______|______|______|______|______|______|______|
	;  |      |                                                |
	;  |   0  |                   $73                          | (not yet received)
	;  |______|______|______|______|______|______|______|______|
	;
	IF ROLE_SLAVE
	 BSF	YY_COMMAND, 7, ACCESS	; note need to set MSB in data stream
	 INCF	YY_STATE, F, ACCESS	; -> S11
	 MOVFF	YY_DATA, YY_YY		; Byte counter (N-1)
	 INCF	YY_YY, F, ACCESS	; Adjust to true byte count
	 CALL	TR_ON_DELAY
	 BSF	PLAT_T_R, BIT_T_R, ACCESS ; Assert bus master role by firing up the transmitter
	 RETURN
	ELSE
	 ERR_BUG 0x08, ERR_CLASS_OVERRUN
	ENDIF
	
S11_DATA:
	DECFSZ	WREG, W, ACCESS
	BRA	S12_DATA
	;
	; IC_TXDAT / IC_TXSTA
	; We're transmitting bytes as they come in until YY_YY is depleated.
	;
	IF ROLE_SLAVE		; BEGIN SLAVE-SIDE INTERNAL CMD CODE-----------
	 TSTFSZ	YY_YY, ACCESS			;			///////
	 BRA	S11_WRITE_NEXT_BYTE		;			///////
	 ;								///////
	 ; YY_YY is zero, the byte just received should be the sentinel.///////
	 ;								///////
	 MOVLW	0x73				;			///////	
	 CPFSEQ	YY_DATA, ACCESS			;			///////	
	 BRA	S11_BAD_SENTINEL		;			///////	
	 ;								///////
	 ; If we are processing IC_TXSTA, add our own six status bytes	///////
	 ; to the end of the output stream:				///////
	 ;								///////
	 ;								///////
	 ;   ___7______6______5______4______3______2______1______0__    ///////
	 ;  |      |                 fault code                     |  
	 ;  |   0  |           (to be cleared after this)           | LAST_ERROR  
	 ;  |______|______|______|______|______|______|______|______|
	 ;  |      |                                  | phase offset|
	 ;  |   0  |     unassigned, write as 0       |    <8:7>    | PHASE_OFFSET[HL]
	 ;  |______|______|______|______|______|______|______|______|
	 ;  |      |                                                |
	 ;  |   0  |           phase offset <6:0>                   | PHASE_OFFSETL
	 ;  |______|______|______|______|______|______|______|______|
	 ;  |      |                                                |
	 ;  |   0  |           serial number <13:7>                 | SYS_SNH
	 ;  |______|______|______|______|______|______|______|______|
	 ;  |      |                                                |
	 ;  |   0  |           serial number <6:0>                  | SYS_SNL      
	 ;  |______|______|______|______|______|______|______|______|
	 ;  |      |                                                |	///////
	 ;  |   0  |                   $33                          | 	///////
	 ;  |______|______|______|______|______|______|______|______|	///////
	 ;								///////
	 ;								///////
	 BTFSS	YY_COMMAND, 0, ACCESS		; doing IC_TXSTA?	///////
	 BRA	S11_END_TRANSMIT		; no, skip to end	///////
	 MOVF	LAST_ERROR, W, ACCESS		; yes, send our private	///////
	 SEND_8_BIT_W				;			///////
	 ;CALL	SIO_WRITE_W			; at the end of the     ///////
	 CLRF	LAST_ERROR, ACCESS		; stream 		///////
	 CLRF	WREG, ACCESS			;			///////
	 BTFSC	PHASE_OFFSETH, 0, ACCESS	;			///////
	 BSF	WREG, 1, ACCESS			;			///////
	 BTFSC	PHASE_OFFSETL, 7, ACCESS	;			///////
	 BSF	WREG, 0, ACCESS			;			///////
	 SEND_8_BIT_W				;			///////
	 ;CALL	SIO_WRITE_W			;			///////
	 MOVF	PHASE_OFFSETL, W, ACCESS	;			///////
	 BCF	WREG, 7, ACCESS			;			///////
	 SEND_8_BIT_W				;			///////
	 ;CALL	SIO_WRITE_W			;			///////
	 MOVLW	UPPER(SYS_SNH)			;			///////
	 MOVWF	TBLPTRU, ACCESS			;			///////
	 MOVLW	HIGH(SYS_SNH)			;			///////
	 MOVWF	TBLPTRH, ACCESS			;			///////
	 MOVLW	LOW(SYS_SNH)			;			///////
	 MOVWF	TBLPTRL, ACCESS			;			///////
	 TBLRD*+				;			///////
	 MOVF	TABLAT, W, ACCESS		;			///////
	 SEND_8_BIT_W				;			///////
	 TBLRD*+				;			///////
	 MOVF	TABLAT, W, ACCESS		;			///////
	 SEND_8_BIT_W				;			///////
	 MOVLW	0x33				;			///////
	 CALL	SIO_WRITE_W			;			///////
S11_END_TRANSMIT:				;			///////
	 ; we're done, shut down transmitter when data's all sent	///////
	 BSF	SSR_STATE, DRAIN_TR, ACCESS	;			///////
	 CLRF	YY_STATE, ACCESS		;			///////
	 RETURN					;			///////
						;			///////
S11_BAD_SENTINEL:				;			///////
 	 ERR_BUG 0x0A, ERR_CLASS_INT_COMMAND	;			///////
						;			///////
S11_WRITE_NEXT_BYTE:				;			///////
	 MOVF	YY_DATA, W, ACCESS		;			///////
	 BTFSS	YY_COMMAND, 7, ACCESS		; set the MSB of the    ///////
	 BRA	S11_WNB_1			; first byte we see 	///////
	 BSF	WREG, 7, ACCESS			;			///////
	 BCF	YY_COMMAND, 7, ACCESS		;			///////
	 CALL	SIO_WRITE_W			; send raw 1st byte     ///////
	 BRA	S11_END_1			;			///////
S11_WNB_1:					;			///////
	 SEND_8_BIT_W				; send escaped byte    	///////
	 ;CALL	SIO_WRITE_W			;			///////
S11_END_1:					;			///////
	 DECF	YY_YY, F, ACCESS		;			///////
	 RETURN					;			///////
	ELSE					;			///////
	 ERR_BUG 0x0B, ERR_CLASS_OVERRUN	;			///////
	ENDIF	; END SLAVE-SIDE INTERNAL COMMAND INTERPRETATION CODE----------
	
S12_DATA:
	DECFSZ	WREG, W, ACCESS
	BRA	S13_DATA
	;
	; IC_LED:  Received GY byte, store in YY_YY and wait for R byte.
	;
	IF ROLE_SLAVE
	 MOVFF	YY_DATA, YY_YY
	 INCF	YY_STATE, F, ACCESS		; -> S13
	 RETURN
	ELSE
	 ERR_BUG 0x0C, ERR_CLASS_OVERRUN
	ENDIF
	
S13_DATA:
	DECFSZ	WREG, W, ACCESS
	BRA	S14_DATA
	;
	; S13: IC_LED command received
	;
	;   ___7______6______5______4______3______2______1______0__
	;  |                                  |                    |
	;  |                0                 |          7         | YY_COMMAND
	;  |______|______|______|______|______|______|______|______|
	;  |      |      |      |      |                           |
	;  |   0  |   0  |   1  |   0  |             1             | (not saved)
	;  |______|______|______|______|______|______|______|______|
	;  |      |      |                    |                    |  
	;  |   0  |   0  |     green LED      |     yellow LED     | YY_YY
	;  |______|______|______|______|______|______|______|______|
	;  |      |                           |                    |
	;  |   0  |             0             |      red LED       | YY_DATA
	;  |______|______|______|______|______|______|______|______|
	;
	;
	IF ROLE_SLAVE
	 IF HAS_STATUS_LEDS
ALTER_LED_STATE MACRO COLOR
	  ;
	  ; Change LED state based on W:
	  ;   000  steady off    001  steady on
	  ;   010  slow fade     011  rapid fade
	  ;   100  slow flash    101  rapid flash
	  ;   11x  no change
	  ;
	  BNZ	ALTER_LED_#v(COLOR)_1
	  SET_SSR_OFF COLOR
	  BRA	ALTER_LED_#v(COLOR)_EXIT
ALTER_LED_#v(COLOR)_1:
	  DECFSZ WREG, W, ACCESS
	  BRA	ALTER_LED_#v(COLOR)_2
	  SET_SSR_STEADY COLOR
	  BRA	ALTER_LED_#v(COLOR)_EXIT
ALTER_LED_#v(COLOR)_2:
	  DECFSZ WREG, W, ACCESS
	  BRA	ALTER_LED_#v(COLOR)_3
	  SET_SSR_SLOW_FADE COLOR
	  BRA	ALTER_LED_#v(COLOR)_EXIT
ALTER_LED_#v(COLOR)_3:
	  DECFSZ WREG, W, ACCESS
	  BRA	ALTER_LED_#v(COLOR)_4
	  SET_SSR_RAPID_FADE COLOR
	  BRA	ALTER_LED_#v(COLOR)_EXIT
ALTER_LED_#v(COLOR)_4:
	  DECFSZ WREG, W, ACCESS
	  BRA	ALTER_LED_#v(COLOR)_5
	  SET_SSR_SLOW_FLASH COLOR
	  BRA	ALTER_LED_#v(COLOR)_EXIT
ALTER_LED_#v(COLOR)_5:
	  DECFSZ WREG, W, ACCESS
	  BRA	ALTER_LED_#v(COLOR)_EXIT
	  SET_SSR_RAPID_FLASH COLOR
	  ; fall-through: other bit patterns defined as "no change"
ALTER_LED_#v(COLOR)_EXIT:
	 ENDM
	 MOVLW	0x07
	 ANDWF	YY_YY, W, ACCESS
	 ALTER_LED_STATE SSR_YELLOW
	 MOVLW  0x38
	 ANDWF	YY_YY, W, ACCESS
	 RRNCF	WREG, W, ACCESS
	 RRNCF	WREG, W, ACCESS
	 RRNCF 	WREG, W, ACCESS
	 ALTER_LED_STATE SSR_GREEN
	 MOVLW	0x07
	 ANDWF	YY_DATA, W, ACCESS
	 ALTER_LED_STATE SSR_RED
	 ; and we're done.
	 ENDIF
	 CLRF	YY_STATE, ACCESS
	 RETURN
	ELSE
	 ERR_BUG 0x0D, ERR_CLASS_OVERRUN
	ENDIF
	
S14_DATA:
	DECFSZ	WREG, W, ACCESS
	BRA	S15_DATA
	;
	; DEF_SEQ: sequence number received, now we need
	; to collect the rest of the packet
	;
	MOVFF	YY_DATA, YY_YY		; sequence number in YY_YY
	WAIT_FOR_SENTINEL .131, B'01110011', .12	; S6.12 when sentinel found
	RETURN
	
S15_DATA:
	DECFSZ	WREG, W, ACCESS
	BRA	S16_DATA
	;
	; S15: EXEC_SEQ: execute sequence
	;
	;   ___7______6______5______4______3______2______1______0__
	;  |                                  |                    |
	;  |                0                 |          7         | YY_COMMAND
	;  |______|______|______|______|______|______|______|______|
	;  |      |      |      |      |                           |
	;  |   0  |   0  |   0  |   0  |             5             | (not saved)
	;  |______|______|______|______|______|______|______|______|
	;  |      |                                                |
	;  |   0  |         sequence number or 0 to stop           | YY_DATA
	;  |______|______|______|______|______|______|______|______|
	;
	GOTO	ERR_NOT_IMP		; XXX
	
S16_DATA:
	DECFSZ	WREG, W, ACCESS
	BRA	S17_DATA
	;
	; S16: MSK_SENS command received
	;
	;   ___7______6______5______4______3______2______1______0__
	;  |                                  |                    |
	;  |                0                 |          7         | YY_COMMAND
	;  |______|______|______|______|______|______|______|______|
	;  |      |      |      |      |                           |
	;  |   0  |   0  |   0  |   0  |             7             | (not saved)
	;  |______|______|______|______|______|______|______|______|
	;  |      |                    |      Sensors enabled      |
	;  |   0  |          0         |   A  |   B  |   C  |   D  | YY_DATA
	;  |______|______|______|______|______|______|______|______|
	;
	;
	GOTO	ERR_NOT_IMP		; XXX

S17_DATA:
	; Or this WOULD be state 17, except there isn't one!
	; Any state >16 lands here.  Handle the exception and
	; abort the command being processed.
	;
	IF QSCC_PORT
	 #include "qscc_hook_s17.asm"
	ELSE
	 ERR_BUG 0x0E, ERR_CLASS_OVERRUN
	ENDIF

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
	LFSR	0, SSR_00_VALUE
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
	 BRA	UPDATE_SSR_SKIP_#v(X)
 	 IF (X > OUTPUT_CHAN_MAX) || (QSCC_PORT)
	  BSF	PLAT_#v(X), BIT_#v(X), ACCESS	; turn on light
 	 ELSE
	  BCF	PLAT_#v(X), BIT_#v(X), ACCESS	; turn on SSR
 	 ENDIF
UPDATE_SSR_SKIP_#v(X):
X	 ++
	ENDW
	DECF	CUR_SLICE, F, ACCESS
	RETURN

UPDATE_MINIMUM_LEVEL:
	;
	; turn off every output that isn't set to be fully on
	; and handle ramping up/down
	;
	BANKSEL	SSR_DATA_BANK
	BSF	SSR_STATE2, ALL_OFF, ACCESS	
X 	SET	0
	WHILE X <= SSR_MAX
 	 COMF	SSR_00_VALUE+#v(X), W, BANKED	; is this set to maximum?
	 ;BZ	UPDATE_MIN_SKIP_#v(X)
	 BNZ	UPDATE_MIN_DIMMED_#v(X)
	 IF X <= OUTPUT_CHAN_MAX
	  BCF	SSR_STATE2, ALL_OFF, ACCESS	; "light fully on" means they aren't all off.  Clear the flag.
	 ENDIF
	 BRA	UPDATE_MIN_SKIP_#v(X)

UPDATE_MIN_DIMMED_#v(X):
  	 IF (X > OUTPUT_CHAN_MAX) || (QSCC_PORT)
	  BCF	PLAT_#v(X), BIT_#v(X), ACCESS	; turn off light
 	 ELSE
	  BSF	PLAT_#v(X), BIT_#v(X), ACCESS	; turn off SSR
	  TSTFSZ SSR_00_VALUE+#v(X), BANKED	; is this SSR fully off?
	  BCF	SSR_STATE2, ALL_OFF, ACCESS	; no, ergo they aren't ALL off now. clear the flag
 	 ENDIF
UPDATE_MIN_SKIP_#v(X):

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
	 BTFSS	SSR_00_FLAGS+#v(X), FADE_CYCLE, BANKED	; cycle back?
	 BRA	END_FADE_#v(X)
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
	 BTFSC	SSR_00_FLAGS+#v(X), MAX_OFF_TIME, BANKED; maximizing off-time?
	 SETF	SSR_00_COUNTER+#v(X), BANKED

END_FADE_#v(X):
X	 ++
	ENDW
	BCF	SSR_STATE, INCYC, ACCESS	; shut down slice processing until next ZC
	;
	; see if we should be asleep
	;
	BTFSS	SSR_STATE2, ALL_OFF, ACCESS
	BRA	BE_AWAKE_NOW
	DECFSZ	AUTO_OFF_CTRL, F, ACCESS	
	RETURN
	SETF	AUTO_OFF_CTRL, ACCESS
	DECFSZ	AUTO_OFF_CTRH, F, ACCESS
	RETURN
	; 
	; We've been idle too long.  Go to sleep now.
	;
	BTFSS	SSR_STATE, SLEEP_MODE, ACCESS
	CALL	DO_CMD_SLEEP
	RETURN
	
BE_AWAKE_NOW:
	;
	; we should be awake.  Make sure we are and reset counters
	;
	BTFSC	SSR_STATE, SLEEP_MODE, ACCESS
	CALL	DO_CMD_WAKE
	SETF	AUTO_OFF_CTRH, ACCESS
	SETF	AUTO_OFF_CTRL, ACCESS
	RETURN



; DMX512 RECEIVER CODE
; Based on Microchip Application Note AN1076
;

;
; If we have DMX mode running but need to shift to Lumos protocol
; (like entering config mode), we need to reset the baud rate to
; whatever is configured for non-DMX use.
;
	IF DMX_ENABLED
DMX_EXIT_TEMPORARILY:
	CLRWDT
	BTFSS	DMX_SLOTH, DMX_SPEED, ACCESS
	RETURN
	BEGIN_EEPROM_READ EE_BAUD
	READ_EEPROM_DATA_W
	END_EEPROM_READ
	IF ROLE_MASTER
	 ; Send F0 72 <baud> 26 -> slave CPU
	 MOVWF	I, ACCESS
	 MOVLW	0xF0
	 CALL	SIO_WRITE_W
	 MOVLW	0x72
	 CALL	SIO_WRITE_W
	 MOVF	I, W, ACCESS
	 CALL	SIO_WRITE_W
	 MOVLW	0x26
	 CALL	SIO_WRITE_W
	 CALL	DRAIN_M_S_TX_BLOCKING
	 MOVF	I, W, ACCESS
	ENDIF
	CALL	SIO_SET_BAUD_W
	BCF	DMX_SLOTH, DMX_SPEED, ACCESS	; no longer running at DMX speeds
	RETURN

DMX_RESUME:
	CLRWDT
	BTFSC	DMX_SLOTH, DMX_EN, ACCESS
	BTFSC	DMX_SLOTH, DMX_SPEED, ACCESS
	RETURN					; either not using DMX at all or already at speed
	IF ROLE_MASTER
	 ; Send F0 72 <baud> 26 -> slave CPU
	 MOVLW	0xF0
	 CALL	SIO_WRITE_W
	 MOVLW	0x72
	 CALL	SIO_WRITE_W
	 MOVLW	SIO_250000
	 CALL	SIO_WRITE_W
	 MOVLW	0x26
	 CALL	SIO_WRITE_W
	 CALL	DRAIN_M_S_TX_BLOCKING
	ENDIF
	MOVLW	SIO_250000
	CALL	SIO_SET_BAUD_W
	BSF	DMX_SLOTH, DMX_SPEED, ACCESS	; now at DMX speed
	RETURN
	
;
; Wait for start of packet
;
;DMX_WAIT_FOR_SYNC:
;	BTFSC	PIR1, RCIF, ACCESS
;	MOVF	RCREG, W, ACCESS	; throw away received bytes until start of frame
;	BTFSS	RCSTA, FERR, ACCESS	; wait until frame error
;	BRA	DMX_WAIT_FOR_SYNC
;	MOVF	RCREG, W, ACCESS	; clear receive buffer
;DMX_WAIT_FOR_START:
;	BTFSS	PIR1, RCIF, ACCESS
;	BRA	DMX_WAIT_FOR_START	; wait for actual characters to start
;	BTFSC	RCSTA, FERR, ACCESS	; and break to end
;	BRA	DMX_WAIT_FOR_START
;	MOVF	RCREG, W, ACCESS
;	ANDLW	0xFF			; test byte just read, should be 0x00
;	BNZ	DMX_WAIT_FOR_SYNC	; done here, come back when ready for next packet

	; XXX now loop over bytes, aborting on FERR (indicates packet was short)
	; or when your data have been received.

DMX_RECEIVED_BYTE:
	CLRWDT
	;
	; We just got a DMX byte.  IF DMX_FRAME is set, this is supposedly the start of
	; a new frame, so any previous frame in progress is aborted.  The state machine
	; in DMX mode is simply:
	;	00 IDLE;     waiting for start of frame
	;	17 DMX_WAIT; waiting for first slot for this device
	; 	18 DMX_UPD;  updating channels
	;
	BTFSS	DMX_SLOTH, DMX_FRAME, ACCESS
	BRA	DMX_NOT_FIRST
	BCF	DMX_SLOTH, DMX_FRAME, ACCESS	; clear start-of-frame signal
	;
	; Start of frame
	; The first byte received is in WREG.  If this is 0x00, we need to pay
	; attention to this frame.  Otherwise, it's something foreign we can ignore.
	;
	TSTFSZ	WREG, ACCESS
	BRA	DMX_WEIRD_FRAME
	MOVLW	0x17				; start of frame -> state 17
	MOVWF	YY_STATE, ACCESS
	MOVFF	DMX_SLOTL, YY_YY		; YY_COMMAND:YY_YY is the number of slots
	CLRF	YY_COMMAND, ACCESS		; to skip before we get to ours
	BTFSC	DMX_SLOTH, DMX_BIT8, ACCESS
	BSF	YY_COMMAND, 0, ACCESS
	RETURN

DMX_WEIRD_FRAME:
	IF HAS_STATUS_LEDS
	 SET_SSR_BLINK_FADE SSR_RED
	ENDIF
	CLRF	YY_STATE, ACCESS		; stay at state 0, wait for next frame.
	RETURN

DMX_NOT_FIRST:
	MOVWF	YY_DATA, ACCESS			; save input byte in YY_DATA
	MOVLW	0x17				; are we at state 17?
	CPFSEQ	YY_STATE, ACCESS
	BRA	DMX_18
	;
	; State 17: waiting for our slot to come up
	;
	IF HAS_STATUS_LEDS
	 SET_SSR_BLINK_FADE SSR_YELLOW
	ENDIF
	TSTFSZ	YY_YY, ACCESS			; count off another slot...
	BRA	DMX_ST_LSB
	BTFSS	YY_COMMAND, 0, ACCESS
	BRA	DMX_SLOT_REACHED
	BCF	YY_COMMAND, 0, ACCESS		; borrow 1 and roll over
DMX_ST_LSB:
	DECF	YY_YY, F, ACCESS
	RETURN

DMX_SLOT_REACHED:
	;
	; We have waited long enough, we're up now!
	;
	INCF	YY_STATE, F, ACCESS		; move state 17->18 (note YY_YY==0 now)

DMX_18:
	CLRWDT
	IF HAS_ACTIVE
	 SET_SSR_BLINK_FADE SSR_ACTIVE
	ENDIF
	MOVLW	0x18
	CPFSEQ	YY_STATE, ACCESS
	BRA	DMX_19
	;
	; State 18: updating slot value YY_DATA into channel YY_YY.
	;
	MOVFF	YY_DATA, YY_COMMAND
	MOVFF	YY_YY, YY_DATA
	INCF	YY_YY, F, ACCESS
	CALL	XLATE_SSR_ID
	BTFSC	TARGET_SSR, INVALID_SSR, ACCESS
	BRA	DMX_DONE
	MOVFF	YY_COMMAND, YY_DATA
	BTFSC	TARGET_SSR, NOT_MY_SSR, ACCESS
	BRA	DMX_PASS_DOWN_SET_LVL
	GOTO	SSR_OUTPUT_VALUE ; TARGET_SSR <- YY_DATA

DMX_PASS_DOWN_SET_LVL:
	IF ROLE_MASTER
	 MOVLW	0xA0
	 CALL	SIO_WRITE_W
	 BCF	TARGET_SSR, 7, ACCESS
	 BCF	TARGET_SSR, 6, ACCESS
	 BCF	STATUS, C, ACCESS
	 RRCF	YY_DATA, F, ACCESS
	 BTFSC	STATUS, C, ACCESS
	 BSF	TARGET_SSR, 6, ACCESS	; LSB of value
	 MOVF	TARGET_SSR, W, ACCESS
	 SEND_8_BIT_W
	 MOVF	YY_DATA, W, ACCESS
	 SEND_8_BIT_W
	 IF HAS_STATUS_LEDS
	  SET_SSR_BLINK_FADE SSR_YELLOW
	 ENDIF
	 RETURN
	ELSE
	 ERR_BUG 0x02, ERR_CLASS_IN_VALID
	ENDIF
	 
DMX_DONE:
	;
	; reached the end of our range of slots
	;
	CLRF	YY_STATE, ACCESS
	RETURN

DMX_19:
	;
	; unknown state!  Force return to idle state
	;
	CLRF	YY_STATE, ACCESS
	RETURN
	ENDIF
	
HALT_MODE:
	;
	; Shut down forever
	;
	CALL	S0_CMD0			; blackout SSR outputs
	BCF	INTCON, GIEH, ACCESS		; disable high-priority interrupts
	BCF	INTCON, GIEL, ACCESS		; disable low-priority interrupts
	IF HAS_STATUS_LEDS
	 BSF	PLAT_RED, BIT_RED, ACCESS	; set only RED light
	 BCF	PLAT_GREEN, BIT_GREEN, ACCESS
	 BCF	PLAT_YELLOW, BIT_YELLOW, ACCESS
	 IF HAS_ACTIVE
	  BCF	PLAT_ACTIVE, BIT_ACTIVE, ACCESS
	 ENDIF
	ENDIF
	MOVLW	b'01110011'			; Set oscillator mode for our long slumber
		; 0-------			; ~IDLEN enter SLEEP mode, not an idle mode
		; -111----			;  IRCF=7 select 8 MHz internal clock speed
		; ------11			;  SCS=3 system clock is now internal oscillator
	MOVWF	OSCCON, ACCESS
	BSF	WDTCON, SWDTEN, ACCESS		; make sure WDT is enabled
HALT_SLEEP:
	CLRWDT
	SLEEP
	; when we wake up from WDT, flashes red light briefly
	IF HAS_STATUS_LEDS
	 BSF	PLAT_RED, BIT_RED, ACCESS
	 CALL	DELAY_1_6_SEC			; 1/6 sec
	 BCF	PLAT_RED, BIT_RED, ACCESS
	ENDIF
	BRA	HALT_SLEEP


TR_ON_DELAY:
	SETF	TR_I, ACCESS
TR_ON_L CLRWDT
	DECFSZ	TR_I, F, ACCESS
	BRA	TR_ON_L
	RETURN

TR_OFF_DELAY:
	BRA	TR_ON_DELAY
	END


; pattern handling
; LEVEL STEP SPEED FLAGS
; 255   255   30   DN CYC	rapid flash
; 255     2    1   DN		blink fade
; 255   255   30   DN CYC MAX	slow flash
;   0     4    1   UP CYC	rapid fade
;   0     1    1   UP CYC	slow fade


