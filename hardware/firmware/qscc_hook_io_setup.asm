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
; This hooks into the Lumos device initialization code which sets up I/O pins.
; We want them arranged differently than the Lumos controllers do, but we put
; the QuizShow code here to keep the Lumos product clean and separate.
; 
	IF LUMOS_CHIP_TYPE != LUMOS_CHIP_QSCC && LUMOS_CHIP_TYPE != LUMOS_CHIP_QSRC
	 ERROR "qscc_hook_io_setup only used for QS*C systems"
	ENDIF

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
	                  	; PORT A: 
		; XX------	; crystal oscillator pins
		; --000000	; always inputs
	CLRF	PORTA, ACCESS	;
	CLRF	LATA, ACCESS	;
				; PORT B:
		; 00000000	; outputs off
	CLRF	PORTB, ACCESS	;
	CLRF	LATB, ACCESS	;
				; PORTC:
		; XX------	; UART pins
		; --00-000	; I/O pins -> 0
		; ----0---	; T/R to receive
	CLRF	PORTC, ACCESS	;
	CLRF	LATC, ACCESS	;
				; PORTD:
		; 00000000	; [CC] data port
		; 00000000	; [RC] I/O pins
	CLRF	PORTD, ACCESS	; 
	CLRF	LATD, ACCESS	;
				; PORTE:
		; XXXXX000	; outputs to 0
	CLRF	PORTE, ACCESS	;
	CLRF	LATE, ACCESS	;
	;
	; I/O direction bits
	;
	IF LUMOS_CHIP_TYPE == LUMOS_CHIP_QSCC
	 ;     7 6 5 4 3 2 1 0
  	 ; RA  X X I I I I I I	buttons ABCDXL
	 ; RB  O O O O O O O O 	lights ABCDF[RGBW]
	 ; RC  X X O O O O O O  controls and lights
	 ; RD  O O O O O O O O  score data port
	 ; RE  X X X X X O O O  LART lights
	 ;
	 SETF	TRISA, ACCESS
	 CLRF	TRISB, ACCESS
	 MOVLW	b'11000000'
	 MOVWF	TRISC, ACCESS
	 CLRF   TRISD, ACCESS
	 CLRF	TRISE, ACCESS
	ELSE
 	 IF LUMOS_CHIP_TYPE == LUMOS_CHIP_QSRC
	  ;     7 6 5 4 3 2 1 0
  	  ; RA  X X I I I I I I	buttons 
	  ; RB  O O O O O O O O lights 
	  ; RC  X X I I O O O O lights/buttons
	  ; RD  O O O I O O O I lights/buttons
	  ; RE  X X X X X O O O lights
	  ;
	  SETF	TRISA, ACCESS
	  CLRF	TRISB, ACCESS
	  MOVLW	b'11110000'
	  MOVWF	TRISC, ACCESS
	  MOVLW	b'00010001'
	  MOVWF	TRISD, ACCESS
	  CLRF	TRISE, ACCESS
         ELSE
          ERROR "LUMOS_CHIP_TYPE not set correctly"
	 ENDIF
	ENDIF
