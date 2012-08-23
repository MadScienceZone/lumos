;;; vim:set syntax=pic ts=8:
;
		LIST n=90
;@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
;@@                                                                         @@
;@@     @   @@@    @@@   @@@@@  @          48-Channel SSR Controller Board  @@
;@@    @@  @   @  @   @    @    @          Firmware Version 2.0.2           @@
;@@   @ @  @   @  @        @    @                                           @@
;@@  @  @   @@@   @        @    @          For use with controller hardware @@
;@@ @@@@@  @   @  @        @    @          revision 3.1 (boards marked as   @@
;@@     @  @   @  @   @    @    @          "48CTL-3-1")                     @@
;@@     @   @@@    @@@     @    @@@@@                                       @@
;@@                                                                         @@
;@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
;
; Copyright (c) 2004, 2005, 2006, 2007 Steven L. Willoughby, Aloha, Oregon, 
; USA.  All Rights Reserved.
;
; $Header: /usr/local/cvsroot/ssr/firmware/48ctlrom.asm,v 1.4 2007/12/18 07:12:48 steve Exp $
;
; Target Microcontroller is PIC16F877A and/or PIC16F777, Q=20MHz
;  (200nS instruction cycle) (The master MUST be an 877A, the slave MAY
;  be either.)
; Serial control (RS-485) at 19.2kbps
;
; @@XXX
; @@XXX There are two versions of this program, one for each MCU on 
; @@XXX the controller board.  Both versions ("master" and "slave") 
; @@XXX are merged into this single source file, with "@@" markers 
; @@XXX showing where each version diverges from the common code.  
; @@XXX Also, the "slave" version may be generated for either the
; @@XXX PIC16F877A or PIC16F777 processor.  Source lines marked with
; @@XXX @@P=xxx@@ will ONLY be included in processor xxx (where xxx
; @@XXX is either "877" or "777").
; @@XXX Lines marked with "@@XXX" are excluded from all versions.
; @@XXX (The majority of the firmware is the same between the two 
; @@XXX chips.)  Specifically:
; @@XXX
; @@--MASTER--@@
; *** THIS IS THE MASTER MCU FIRMWARE CODE.
; *** IT MUST BE FLASHED INTO U2 (THE UPPER MCU CHIP ON THE BOARD).
; *** This chip receives all the serial commands, determines which are
; *** addressed to this controller unit, and either acts on the commands
; *** directly or passes them down to the slave MCU to be acted upon by
; *** it.
; *** ** THIS CODE MUST RUN ON A PIC16F877A MICROCONTROLLER ** @@P=877@@
; *** ** WARNING! WARNING! WARNING! ************************** @@P=777@@
; *** ** WARNING! WARNING! WARNING! ************************** @@P=777@@
; *** ** ***************************************************** @@P=777@@
; *** DO NOT USE THIS VERSION OF THE FIRMWARE!  IT WAS SOME-** @@P=777@@
; *** HOW CONFIGURED FOR THE PIC16F777 PROCESSOR, WHICH CAN-** @@P=777@@
; *** NOT FUNCTION AS THE MASTER CPU ON THIS BOARD! ********** @@P=777@@
; *** ** ***************************************************** @@P=777@@
; *** ** WARNING! WARNING! WARNING! ************************** @@P=777@@
; *** ** WARNING! WARNING! WARNING! ************************** @@P=777@@
; @@--SLAVE--@@
; *** THIS IS THE SLAVE MCU FIRMWARE CODE.
; *** IT MUST BE FLASHED INTO U3 (THE LOWER MCU CHIP ON THE BOARD).
; *** This chip acts upon commands received from the master MCU.  It is
; *** also in control of the RS-485 transceiver mode (although in this
; *** version it leaves it set to RECEIVE mode all the time.)  It would
; *** also be the chip to transmit over the RS-485 bus, but again, this
; *** version never actually does that.
; *** THIS VERSION OF THE FILE MUST BE RUN ON A PIC16F877A *** @@P=877@@
; *** THIS VERSION OF THE FILE MUST BE RUN ON A PIC16F777  *** @@P=777@@
; @@--END--@@
; @@XXX (Common code continues from this point...)
;
;=============================================================================
; HARDWARE DESCRIPTION
;-----------------------------------------------------------------------------
;
;  PIC16F777/877A Microcontroller I/O pin assignments:
;                        ________   _________
;                       |o       \_/         |
;     Vpp /RESET -->  1 | /MCLR      PGD/RB7 | 40 <-> PGD
;         /SSR16 <--  2 | RA0        PGC/RB6 | 39 <-- PGC
;         /SSR14 <--  3 | RA1            RB5 | 38 --> /SSR15     
;         /SSR12 <--  4 | RA2            RB4 | 37 --> /SSR13     
;         /SSR10 <--  5 | RA3            RB3 | 36 --> /SSR11     
;         /SSR08 <--  6 | RA4 (OD)       RB2 | 35 --> /SSR09     
;        ACT LED <--  7 | RA5            RB1 | 34 --> /SSR07     
;        GRN LED <--  8 | RE0        INT/RB0 | 33 <-- ZC INT
;        YEL LED <--  9 | RE1    PIC     VDD | 32 --- +5V       
;        RED LED <-- 10 | RE2    16F     VSS | 31 --- GND      
;            +5V --- 11 | VDD    877A    RD7 | 30 --> /SSR17  
;            GND --- 12 | VSS     or     RD6 | 29 --> /SSR06 
;           xtal --- 13 | OSC    777     RD5 | 28 --> /SSR05
;             +----- 14 | OSC            RD4 | 27 --> /SSR18     
;         /SSR04 <-- 15 | RC0         RX/RC7 | 26 <-- Serial RxD
;         /SSR19 <-- 16 | RC1         TX/RC6 | 25 --> Serial TxD
;         /SSR03 <-- 17 | RC2            RC5 | 24 --> /SSR02       
;         /SSR01 <-- 18 | RC3            RC4 | 23 --> /SSR00      
;         /SSR23 <-- 19 | RD0            RD3 | 22 --> /SSR22     
;         /SSR21 <-- 20 | RD1            RD2 | 21 --> /SSR20    
;                       |____________________|
; 
; Note that the '877A can be used for either master or slave, but the '777
; can ONLY be used for the slave processor.
;
;-----------------------------------------------------------------------------
; I/O PORT ASSIGNMENTS
;-----------------------------------------------------------------------------
;
; @@--MASTER--@@
;          7   6   5   4   3   2   1   0
; PORT RA --- --- ACT /08 /10 /12 /14 /16
;          <OSC>   O   O   O   O   O   O
; @@--SLAVE--@@
;          7   6   5_  4   3   2   1   0
; PORT RA --- --- T/R /08 /10 /12 /14 /16
;          <OSC>   O   O   O   O   O   O
; @@--END--@@
;
; PORT RB --- --- /15 /13 /11 /09 /07 ---
;          <PGM>   O   O   O   O   O  INT
;
; PORT RC --- --- /02 /00 /01 /03 /19 /04
;          <I/O>   O   O   O   O   O   O
;
; PORT RD /17 /06 /05 /18 /22 /20 /21 /23
;          O   O   O   O   O   O   O   O
;
; PORT RE --- --- --- --- --- RED YEL GRN
;                              O   O   O
;
;
; THESE SSR LINES ARE NEGATIVE-LOGIC CONTROLLED!
; (0=ON, 1=OFF)
;
;=============================================================================
; MEMORY MAP (At least the parts we directly care about)
;-----------------------------------------------------------------------------
;
;-----------------------------------------------------------------------------
; ALL BANKS
;-----------------------------------------------------------------------------
;
;
;                     __7___.__6___.__5___.__4___.__3___.__2___.__1___.__0___ 
; $000 INDF          |                                                       |
;                    |  Access register indirect [FSR]                       |
;                    |______|______|______|______|______|______|______|______|
; $002 PCL           |                                                       |
;                    |                         PC<7:0>                       |
;                    |______|______|______|______|______|______|______|______|
; $003 STATUS        |      |      |      |  __  |  __  |      |      |      |
;                    | IRP  |  RP1 |  RP0 |  TO  |  PD  |  Z   |  DC  |  C   |
;                    |______|______|______|______|______|______|______|______|
; $004 FSR           |                                                       |
;                    |  Address of target of INDF pseudo-register            |
;                    |______|______|______|______|______|______|______|______|
; $00A PCLATH        |////////////////////|                                  |
;                    |////////////////////|      PC<12:8> latch register     |
;                    |////////////////////|______|______|______|______|______|
; $00B INTCON        |      |      |      |      |      |      |      |      |
;                    | GIE  | PEIE |TMR0IE| INTE | RBIE |TMR0IF| INTF | RBIF |
;                    |______|______|______|______|______|______|______|______|
; $070 W_TEMP        |                                                       |
;                    |  Temporary storage for W during int service routine   |
;                    |______|______|______|______|______|______|______|______|
; $071 STATUS_TEMP   |                                                       |
;                    |  Temporary storage for STATUS during ISR              |
;                    |______|______|______|______|______|______|______|______|
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
; ISR
;	The interrupt service routine manages a set of counters and timers:
;       1. At each AC line zero-crossing point, we reset a two-stage waveform
;	   slicing timing chain which governs the ability for the SSRs to dim
;	   incandescent lamps plugged into them; 
;	2. Each front panel LED has a counter for how long their current 
;          status is to be held, to allow a human to have enough time to 
;          see the LED before it would be extinguished.
;
; MAIN_LOOP
;	Manages the display of the front panel LEDs
;	Updates the status of the SSR lines if it's time to do so
;	Receives a character from the serial line if one's waiting
;
; INTERPRETER
;	When a byte is received on the serial line, it is processed by
;	a small state machine.  The current state is held in SSR_STATE<2:0>.
;
;-----------------------------------------------------------------------------
; Command Protocol:
;                     _______________________________________________________
; Command Byte:      |      |                    |                           |
;                    |  1   |    Command code    |   Target device address   |
;                    |______|______|______|______|______|______|______|______|
;
; Any byte with its MSB set is the beginning of a command.  If the target 
; device matches this unit's address, the state machine kicks into gear and
; processes the command (which may require some following data bytes, all
; of which must have their MSB cleared).  Otherwise, the unit ignores the
; byte.
;
; Any byte with its MSB cleared is a data byte, and is ignored unless we're
; in the middle of interpreting a multi-byte command.
;
; Commands recognized:
; 	0: All channels off
;	1: Set/clear single channel (requires channel ID byte)
;	2: Set channel to value (requires channel ID and value bytes)
;	3: Reserved
;	4: Reserved
;	5: Reserved
;	6: Reserved
;	7: Administrative command (follow-on byte further decodes):
;          00pppppp Set phase offset=p and display on LEDs
;	   010baaaa Set device address=aaaa; b=a<0>
;          01100000 Shutdown device
;          01100001 Disable administrative commands
;          01100010 Reserved
;             .         .
;             .         .
;             .         .
;          01101111 Reserved
;          0111xxxx Internal commands MASTER->SLAVE:
;                   011100xx  Reserved
;                   011101yr  Display RED and/or YEL LED 2S
;                   01111gyr  HALT with <g><y><r> displayed on LEDs
;                    
;                     _______________________________________________________
; Channel ID:        |      |      |                                         |
;                    |  0   | ON   |               Channel ID                |
;                    |______|______|______|______|______|______|______|______|
; The ON bit <6> determines whether the channel is being turned on (1) or 
; off (0) for the "Set/clear single channel" command.  it is ignored when
; setting the channel to a specific dimmer value.
;
;                     _______________________________________________________
; Dimmer Value:      |      |      |      |                                  |
;                    |  0   |   x  |   x  | Brightness level (0=off, 31=on)  |
;                    |______|______|______|______|______|______|______|______|
;
;-----------------------------------------------------------------------------
; State Machine Details
;
; Normally sits at state 0 (Idle) where it pretty much spins free waiting
; for the start of a command to come along.
;  ___________________
; | 4 | ADMIN         |
; |___| Waiting for   |
; |     Sub-command   |
; |___________________|
;         ^  |
;         |  |
;         |  |
;         |  |
;  _______|__V________                   _________________
; | 0 | IDLE          |                 | 1 | SETCHAN     |
; |___|               |---------------->|___| Waiting for |
; |                   |<----------------|     Channel byte|
; |___________________|<-------+        |_________________|
;           |                  |
;           |                  |
;           |                  |
;           |                  |
;  _________V_________         |         _________________
; | 2 | DIMCHAN1      |        +--------| 3 | DIMCHAN2    |
; |___| Waiting for   |---------------->|___| Waiting for |
; |     Channel byte  |                 |     Value byte  |
; |___________________|                 |_________________|
;
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
; At 38 slices per ZC, each slice is 0.000219298245614 seconds.
; The closest match to this is 0.0002192 sec (a timer value of 137 at 1:8 scale)
; so we're really getting about 38.01703 slices in a half-cycle.
; This works out to around 1,096 instructions per slice, which is more than 
; adequate but can get tight if all the channels are at the same dimmer settings,
; but it works well enough.  
; We have to be able to handle an incoming byte on the serial port and update all
; the SSRs once in that many instructions.
;
; These times will vary based on what commands are being parsed, the combination
; of SSRs on, off, dim, or at what brightness level, but a general idea is:
;
;    ROUTINE   IDLE  BUSY (total instruction cycles)
;     ISR              46
;     LEDs       12    16
;     SIO Poll    6    17
;     Parser     10     7, 23, 64, up to 129+
;     SSR Upd    22   373 up to 1,141+
;
; So when nothing at all is happening, we only need around 40 instruction
; cycles (0.000008 sec) per slice (3.6% of the available slice time) to run
; an idle main loop iteration.
;
; The overhead of some of the loops and subroutines can be eliminated by
; flattening them into lots of repetitive cut-and-paste inline code.  We do
; have the available program memory to do that, and gain some significant 
; runtime performance.  For now, we will keep it less efficient but more
; maintainable until we need that performance.
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
; from 0-255 (although really only 0-40 make much sense) slices between the ZC
; interrupt and the start of the dimmer cycle of 32 slices.  (The other 6 
; slices are idle (not active) slices.)
;
; The value for PHASE_OFFSET should be chosen to start the cycle one or two
; slices into the actual half-wave.  So if there is no phase difference at all
; between sides of the transformer, PHASE_OFFSET shoud be started at 2.
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
; 1/38th brightness level (something less than one brightness increment), which
; ought to be difficult or impossible to notice by looking at an incandescent
; light load.  This is one reason why PHASE_OFFSET should be set to allow 1-2
; idle slices before we start turning on SSRs.
;
; On ZC interrupt, we set CUR_PRE to PHASE_DELAY and set <PRECYC>.
; On TMR2 interrupt, if SSR_STATE<PRECYC>, decrement CUR_PRE.
;   if zero, clear SSR_STATE<PRECYC>, set CUR_SLICE to 32, set <INCYC>,<DIM_START>.
;   if SSR_STATE<INCYC>, decrement CUR_SLICE; if zero, set DIM_END, clr INCYC; else set SLICE_UPD
; 
; In main polling loop:
;   if DIM_START: turn on "on" SSRs, clear DIM_START
;   if SLICE_UPD: turn on SSR == CUR_SLICE for SSRs with SSRDIM set; clear SLICE_UPD
;   if DIM_END:   turn off all except SSR_ON, clear DIM_END
;
; PRECYC INCYC SLICE_UPD DIM_START DIM_END CUR_PRE CUR_SLICE
;    0     x       x         x        x       x       x
;    1     x       x         x        x       4       x       <--zc
;    1     x       x         x        x       3       x
;    1     x       x         x        x       2       x
;    1     x       x         x        x       1       x
;    0     1     1-->0     1-->0      x       0      31       SSR@31/on turned on
;    0     1     1-->0       0        x       0      30       SSR@30    turned on
;    0     1     1-->0       0        x       0      29       SSR@29    turned on
; ...
;    0     1     1-->0       0        x       0       2       SSR@2     turned on
;    0     1     1-->0       0        x       0       1       SSR@1     turned on
;    0     0     1-->0       0      1-->0     0       0       all non-on turned off
;    0     0       0         0        0       0       0       idle...
; ...
;    1     0       0         0        0       4       0       <--zc
; 
;
; We're apparently leaving the call stack half-empty worst-case.
; =============================================================================
;
; Startup LED sequence:
;  --- *set up I/O ports, TRIS bits
;  GYR flash quickly 5 times -- indicates restart of CPU
;  G-- [M] indicates MASTER
;  --R [S] indicates 877A SLAVE
;  -YR [S] indicates 777 SLAVE
;      *set up EEPROM
;      (2s)
;      *start transmitter
;  --- (2s)
;  -Y- flash YEL 1x == ROM ID v2.0
;  --- (2s)
;  G-R [M] GRN steady, flash RED for device ID
;  --- (2s)
;  --R (1s)
;      *set up serial port, interrupt options, etc.
;      (2s)
;      *start receiver
;  --- (.25s)
;  -Y- *slave waits for master
;      *master waits 1s then transmits
;  -YR RED steady, flash YEL MSN of PO
;  -YR YEL steady, flash RED LSN of PO
;  --- 
;  GY- GRN blinking slowly => run state
;
;  
;  
;  
; =============================================================================
;
		PROCESSOR 16F877A	; @@P=877@@
		PROCESSOR 16F777 	; @@P=777@@
#include <p16f877a.inc>			; @@P=877@@
#include <p16f777.inc>			; @@P=777@@
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