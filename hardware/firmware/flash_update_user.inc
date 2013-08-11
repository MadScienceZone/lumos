;
; To use the flash loader module, you need to edit this
; include file to suit your application.
;
FLASH_UPDATE_START_ADDR	EQU	0x17000 ; Start of the flash loader code
FLASH_UPDATE_LAST_BLK	EQU	0x16FC0 ; Last block number we're allowed to change
FLASH_UPDATE_ROM_END	EQU	0x16FFF ; End of zone which we're allowed to change
;                                                                        _
; This is a kludge that needs to be cleaned up.  We need to know where T/R is for
; the board we're using.  The main Lumos code has logic for this which should be
; visible here. For right now, we're hard coding this for a standalone Lumos board.
;						           _
HAS_T_R			EQU	1		; RB0 is T/R output
PLAT_T_R		EQU	LATB
PORT_T_R		EQU	PORTB
TRIS_T_R		EQU	TRISB
BIT_T_R			EQU	0

