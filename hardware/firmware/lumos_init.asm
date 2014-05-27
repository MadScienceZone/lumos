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
; Copyright (c) 2012, 2014 by Steven L. Willoughby, Aloha, Oregon, USA.  All Rights
; Reserved.  Released under the terms and conditions of the Open Software
; License, version 3.0.
;
; Portions based on earlier code copyright (c) 2004, 2005, 2006, 2007
; Steven L. Willoughby, Aloha, Oregon, USA.  All Rights Reserved.
;
; -*- -*- -* -*- -*- -*- -*- -*- -* -*- -*- -*- -*- -*- -* -*- -*- -*- -*- -*-
;
; Device initialization code.  See lumos_main.asm for hardware implementation
; details.
;
;
#include "lumos_config.inc"
		RADIX		DEC
;
;==============================================================================
; CONFIGURATION FUSES
;==============================================================================
;
 IF LUMOS_ARCH == LUMOS_ARCH_14K50
;
;	18F14K50 fuses
;
	CONFIG	CPUDIV=NOCLKDIV		; No CPU clock divide [NOCLKDIV,CLKDIV[234]]
	CONFIG  USBDIV=OFF		; USB clock from OSC oscillator block
	CONFIG	FOSC=HS			; Oscillator selection [LP,XT,HS,ERCCLKOUT,ECCLKOUTH,ECH,ERC,IRC,IRCCLKOUT,ECCLKOUTM,ECM,ECCLKOUTL,ECL]
	CONFIG	PLLEN=ON		; Oscillator x4
	CONFIG	PCLKEN=ON		; Primary clock enabled
	CONFIG	FCMEN=OFF		; Fail-safe clock monitor off
	CONFIG  IESO=OFF		; no oscillator switchover
	CONFIG	PWRTEN=OFF		; no power-up timer
	CONFIG	BOREN=OFF		; no brown-out reset
	CONFIG	WDTEN=ON		; watchdog timer enabled
	CONFIG	WDTPS=16384		; Watchdog timer postscale 1:16K (~65.5s) [1,2,4,8,...,32768]
	CONFIG	HFINTOSC=OFF		; System clock waits for HFINTOSC to stabilize
	CONFIG	MCLRE=ON		; /MCLR pin is for /MCLR, not I/O
	CONFIG	STVREN=ON		; enable stack over/under-flow reset
	CONFIG	LVP=OFF			; disable low-voltage programming mode
	CONFIG	BBSIZ=OFF		; 1kW boot block [OFF=1k,ON=2k]
	CONFIG	CP0=OFF, CP1=OFF	; no code protection on pages 0, 1
	CONFIG	CPB=OFF, CPD=OFF	; ... nor on boot block and data EEPROM
	CONFIG	WRT0=OFF, WRT1=OFF	; ... nor table writes
	CONFIG	WRTB=OFF, WRTD=OFF	; ... nor boot block, EEPROM
	CONFIG	EBTRB=OFF		; Bootblk ($00000-$007FF) unprotected TBL RD
	CONFIG	EBTR0=OFF		; Block 0 ($00800-$03FFF) unprotected TBL RD
	CONFIG	EBTR1=OFF		; Block 1 ($04000-$07FFF) unprotected TBL RD
;
;
 ELSE
  IF LUMOS_ARCH == LUMOS_ARCH_4685
;
;	18F4685 fuses
;
;	CONFIG	OSC=HS		; OSC is HS mode (4-20MHz)
	CONFIG	OSC=HSPLL	; PLL mode (10MHz xtal -> 40MHz clock)
	CONFIG	IESO=OFF	; no OSC switchover mode
	CONFIG	FCMEN=OFF	; no failsafe clock monitor
	CONFIG	PWRT=OFF	; power-up timer disabled
	CONFIG	BOREN=OFF	; no brown-out reset
	CONFIG	WDT=ON		; watchdog timer enabled
;	CONFIG 	WDTPS=1024	; watchdog 1:1,024 postscaler (~4s)
;	CONFIG	WDTPS=8192	; watchdog 1:8,192 postscaler (~32.8s)
	CONFIG	WDTPS=16384	; watchdog 1:16,384 postscaler (~65.5s)
;	CONFIG	WDTPS=32768	; watchdog 1:32,768 postscaler (~131s)
	CONFIG	MCLRE=ON	; /MCLR pin is for /MCLR, not I/O
	CONFIG 	LPT1OSC=OFF	; TMR1 is high-power
	CONFIG	PBADEN=OFF	; PORTB pins digital, not A/D on power-up
	CONFIG	DEBUG=OFF	; background debugger disabled; RB<7:6> I/O
	CONFIG	XINST=OFF	; extended instruction set/addressing modes OFF
	CONFIG	BBSIZ=1024	; boot block = 1,024 words
	CONFIG	LVP=OFF		; low-voltage programming DISABLED
	CONFIG	STVREN=ON	; enable stack over/under-flow reset
				; turn off write protection and code protection
	CONFIG	CP0=OFF, CP1=OFF, CP2=OFF, CP3=OFF, CP4=OFF, CP5=OFF
	CONFIG	CPB=OFF, CPD=OFF	
	CONFIG	WRT0=OFF, WRT1=OFF, WRT2=OFF, WRT3=OFF, WRT4=OFF, WRT5=OFF
	CONFIG	WRTB=OFF, WRTC=OFF, WRTD=OFF
	CONFIG	EBTRB=OFF	; Bootblk ($00000-$007FF) unprotected TBL RD
	CONFIG	EBTR0=OFF	; Block 0 ($00800-$03FFF) unprotected TBL RD
	CONFIG	EBTR1=OFF	; Block 1 ($04000-$07FFF) unprotected TBL RD
	CONFIG	EBTR2=OFF	; Block 2 ($08000-$0BFFF) unprotected TBL RD
	CONFIG	EBTR3=OFF	; Block 3 ($0C000-$0FFFF) unprotected TBL RD
	CONFIG	EBTR4=OFF	; Block 4 ($10000-$13FFF) unprotected TBL RD
	CONFIG	EBTR5=OFF	; Block 5 ($14000-$17FFF) unprotected TBL RD
; 
  ELSE
   ERROR "PIC Architecture setting not configured!"
  ENDIF
 ENDIF
; 
;==============================================================================
; PUBLIC ENTRY POINTS
;==============================================================================
LUMOS_CODE_INIT CODE
	GLOBAL	LUMOS_INIT
;
; LUMOS_INIT  (nil -> nil)
;
;	Initialize the CPU for the Lumos circuit
;
LUMOS_INIT:
	CLRWDT
;
; Oscillator Control
;
	MOVLW	b'01000000'	;
		; 0-------	; IDLEN: enter sleep mode on SLEEP
		; -100---- 	; IRCF:  internal osc (not used)
		; ----XX--	; not used (status bits)
		; ------00	; system clock from primary osc
	MOVWF	OSCCON, ACCESS
 IF LUMOS_ARCH == LUMOS_ARCH_14K50
  ERROR "Missing 14K50 initialization code"
 ENDIF
;
; Reset Control
;
	MOVLW	b'10011111'	;
		; 1-------	; use interrupt prioriries
		; -0------	; disable brown-out reset
		; --X-----	; 
		; ---1----	; RESET state clear
		; ----1---	; WDT state clear
		; -----1--	; Power-down detection clear
		; ------1-	; POR clear
		; -------1 	; BOR clear
	MOVWF	RCON, ACCESS
;
; Interrupt Control
;
	MOVLW	b'00000000'	;
		; 0-------	; High-priority interrupts OFF
		; -0------	; Low-priority interrupts OFF
		; --0-----	; TMR0 int enable OFF
		; ---0----	; INT0 int enable OFF
		; ----0---	; PORTB int on change OFF
		; -----0--	; TMR0 int flag CLEAR
		; ------0-	; INT0 int flag CLEAR
		; -------0	; PORTB int on change flag CLEAR
	MOVWF	INTCON, ACCESS
	MOVLW	b'10110100'
		; 1-------	; PORTB pull-up OFF
		; -0------	; INT0 on falling edge
		; --1-----	; INT1 on rising edge
		; ---1----	; INT2 on rising edge
		; ----X-X-	; N/A
		; -----1--	; TMR0 = high priority
		; -------0	; PORTB IoC = low priority
	MOVWF	INTCON2, ACCESS
	MOVLW	b'00000000'
		; 0-------	; INT2 = low priority
		; -0------	; INT1 = low priority
		; --X--X--	; N/A
		; ---0----	; INT2 int enable OFF
		; ----0---	; INT1 int enable OFF
		; ------0-	; INT2 int flag CLEAR
		; -------0	; INT1 int flag CLEAR
	MOVWF	INTCON3, ACCESS
	MOVLW	b'00000000'
		; 0-------	; parallel slave R/W int OFF
		; -0------	; A/D converter int OFF
		; --0-----	; UART RX int OFF
		; ---0----	; UART TX int OFF
		; ----0---	; Synchronous int OFF
		; -----0--	; CCP1 int OFF
		; ------0-	; TMR2 int OFF
		; -------0	; TMR1 int OFF
	MOVWF	PIE1, ACCESS
	MOVLW	b'00000000'
		; 0-------	; OSC fail int OFF
		; -0------	; comparator int OFF
		; --X-----	; 
		; ---0----	; EEPROM write int OFF
		; ----0---	; bus collision int OFF
		; -----0--	; H/L voltage int OFF
		; ------0-	; TMR3 int OFF
		; -------0	; ECCP1 int OFF
	MOVWF	PIE2, ACCESS
	MOVLW	b'00000000'
		; 0-------	; CAN invalid RX int OFF
		; -0------	; CAN wakeup int OFF
		; --0-----	; CAN error int OFF
		; ---0----	; CAN TX buf 2 int OFF
		; ----0---	; CAN TX buf 1 int OFF 
		; -----0--	; CAN TX buf 0 int OFF
		; ------0-	; CAN RX buf 1 int OFF
		; -------0	; CAN RX buf 0 int OFF
	MOVWF	PIE3, ACCESS
	MOVLW	b'00000010'
		; 0-------	; Parallel slave port R/W int = low priority
		; -0------	; A/D converter int = low priority
		; --0-----	; UART RX int = low priority
		; ---0----	; UART TX int = low priority
		; ----0---	; Synchronous port = low priority
		; -----0--	; CCP1 int = low priority
		; ------1-	; TMR2 int = high priority
		; -------0	; TMR1 int = low priority
	MOVWF	IPR1, ACCESS
	MOVLW	b'00000000'
		; 0-------	; OSC fail int = low priority
		; -0------	; Comparator int = low priority
		; --X-----	; N/A
		; ---0----	; EEPROM write int = low priority
		; ----0---	; Bus collisions int = low priority
		; -----0--	; H/L voltage int = low priority
		; ------0-	; TMR3 int = low priority
		; -------0	; ECCP1 int = low priority
	MOVWF	IPR2, ACCESS
	MOVLW	b'00000000'
		; 0-------	; CAN RX error int = low priority
		; -0------	; CAN wakeup int = low priority
		; --0-----	; CAN bus err int = low priority
		; ---0----	; CAN TX buf2 int = low priority
		; ----0---	; CAN TX buf1 int = low priority
		; -----0--	; CAN TX buf0 int = low priority
		; ------0-	; CAN RX buf1 int = low priority
		; -------0	; CAN RX buf0 int = low priority
	MOVWF	IPR3, ACCESS



	CLRF	PIR1, ACCESS	; Clear all peripheral int flags
	CLRF	PIR2, ACCESS	; Clear all peripheral int flags
	CLRF	PIR3, ACCESS	; Clear all peripheral int flags
;
; I/O PORT SETUP
;
 	IF QSCC_PORT
	 #include "qscc_hook_io_setup.asm"
 	ELSE
	 MOVLW	b'00111100'
		; XX------	; N/A
		; --1111--	; no channel selected
		; ------0-	; A/D converter idle
		; -------0	; A/D converter OFF
	 MOVWF	ADCON0, ACCESS
	 MOVLW	b'00001111'
		; XX------	; N/A
		; --00----	; voltage reference = AVss, AVdd
		; ----1111	; all I/O pins digital
	 MOVWF	ADCON1, ACCESS
	 CLRF	ADCON2, ACCESS	; not needed since we're not using A/D	
	 CLRF	CVRCON, ACCESS	; turn off comparator voltage reference
				;
	 MOVLW 	b'00011111'	; PORT A: 
		; XX------	; crystal oscillator pins
		; --0-----	; T/R pin to RECEIVE mode / ACT light OFF
		; ---11111	; SSR pins HIGH (relays off)
	 MOVWF	PORTA, ACCESS	; 
	 MOVWF	LATA, ACCESS
	 MOVLW	b'10111110' 	; PORT B:
		; 1-------	; PWRCTL set HIGH (power supply OFF)
		; -X------	; OPTION button
		; --11111-	; SSR pins HIGH (relays off)
		; -------0	; T/R to RECEIVE (standalone board; input on others)
	 MOVWF	PORTB, ACCESS
	 MOVWF	LATB, ACCESS
	 MOVWF	b'00111111'	; PORTC:
		; XX------	; serial I/O pins
		; --111111	; SSR pins HIGH (relays off)
	 MOVWF	PORTC, ACCESS
	 MOVWF	LATC, ACCESS
	 SETF	PORTD, ACCESS	; PORTD: SSR pins HIGH (relays off)
	 SETF	LATD, ACCESS
	 CLRF	PORTE, ACCESS	; PORTE: LEDs LOW (off)
	 CLRF	LATE, ACCESS

				;    bit 7 6 5 4 3 2 1 0
	 MOVLW	b'11100000' 	; PORTA  X X I O O O O O  all outputs except LEDs (may be sensors)
	 MOVWF	TRISA, ACCESS
 	 IF LUMOS_CHIP_TYPE==LUMOS_CHIP_MASTER
	  MOVLW	b'01000001'	; PORTB  O I O O O O O I  <6> option, <0> INT; rest outputs
	  MOVWF	TRISB, ACCESS
  	 ELSE
  	  IF LUMOS_CHIP_TYPE==LUMOS_CHIP_SLAVE
	   MOVLW b'00000001'	; PORTB  O X O O O O O I  <0> INT; rest outputs
	   MOVWF TRISB, ACCESS
          ELSE
           IF LUMOS_CHIP_TYPE==LUMOS_CHIP_STANDALONE
	    MOVLW b'01000000'	; PORTB  O I O O O O O O  <6> option; rest outputs
	    MOVWF TRISB, ACCESS
           ELSE
    	    ERROR "LUMOS_CHIP_TYPE not set correctly"
           ENDIF
          ENDIF
         ENDIF
	 MOVLW	b'11000000'	; <7:6> is serial; rest are output
	 MOVWF	TRISC, ACCESS
	 CLRF 	TRISD, ACCESS	; PORTD  O O O O O O O O  all outputs
	 MOVLW	b'00000111'
	 MOVWF	TRISE, ACCESS	; PORTE  X X X X X 1 1 1  all inputs (for now, may be sensors)
	ENDIF
;
; Timers
;
	MOVLW	b'00010000'
		; 0-------	; TMR0 off
		; -0------	; TMR0 16 bits, not 8
		; --0-----	; TMR0 clock source from system clock
		; ---1----	; TMR0 triggered on falling edge
		; ----0---	; TMR0 does use prescaler
		; -----000	; TMR0 prescaler=1:2
	MOVWF	T0CON, ACCESS
	CLRF	TMR0H, ACCESS
	CLRF	TMR0L, ACCESS	; reset TMR0 
	MOVLW	b'10000000'
		; 1-------	; TMR1 read/write 16 bits at a time
		; -X------	; N/A
		; --00----	; TMR1 prescaler = 1:1
		; ----0---	; TMR1 oscillator power off
		; -----00-	; TMR1 uses system clock (Fosc/4)
		; -------0	; TMR1 off
	MOVWF	T1CON, ACCESS
	CLRF	TMR1H, ACCESS	; (written with low byte)
	CLRF	TMR1L, ACCESS	; reset TMR1
	MOVLW	b'00001000'
		; X-------	; N/A
		; -0001---	; TMR2 postscaler = 1:2
		; -----0--	; TMR2 off
		; ------00	; TMR2 prescaler = 1:1
	MOVWF	T2CON, ACCESS
	CLRF	TMR2, ACCESS	; reset TMR2 counter
	CLRF	PR2, ACCESS	; clear TMR2 period
	MOVLW	b'10000000'	
		; 1-------	; TMR3 read 16 bits at a time
		; -0--0---	; TMR1 is source for ECCP1/CCP1
		; --00----	; TMR3 prescaler = 1:1
		; -----00-	; TMR3 from system clock (Fosc/4)
		; -------0	; TMR3 off
	MOVWF	T3CON, ACCESS
	CLRF	TMR3H, ACCESS	; (written with low byte)
	CLRF	TMR3L, ACCESS	; clear TMR3

;
; Misc peripherals
;
	CLRF	HLVDCON, ACCESS	; turn off high/low voltage detection
	MOVLW	b'00100000'
		; 001XXXXX 	; set CAN module to disable/sleep mode
		; ----0000	; no interrupts
	MOVWF	CANSTAT, ACCESS
	CLRF	CCP1CON, ACCESS	; disable CCP1
	CLRF	ECCP1CON, ACCESS; disable ECCP1
	CLRF	CMCON, ACCESS	; comparator not used
;
; Enable watchdog timer
;
	MOVLW	b'00000001'
		; XXXXXXX1	; WDT ON
	MOVWF	WDTCON, ACCESS
;
; Ready for other module initialization, etc.
;
	RETURN
	END
