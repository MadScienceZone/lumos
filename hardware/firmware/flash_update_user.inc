;
; To use the flash loader module, you need to edit this
; include file to suit your application.
;
IF LUMOS_ARCH == "4685"
FLASH_UPDATE_START_ADDR	EQU	0x17000 ; Start of the flash loader code
FLASH_UPDATE_LAST_BLK	EQU	0x16FC0 ; Last block number we're allowed to change
FLASH_UPDATE_ROM_END	EQU	0x16FFF ; End of zone which we're allowed to change
ELSE
 IF LUMOS_ARCH == "14K50"
FLASH_UPDATE_START_ADDR	EQU	0x03000 ; Start of the flash loader code
FLASH_UPDATE_LAST_BLK	EQU	0x02FC0 ; Last block number we're allowed to change
FLASH_UPDATE_ROM_END	EQU	0x02FFF ; End of zone which we're allowed to change
 ELSE
  ERROR "Bad architecture switch in flash_update_user.inc"
 ENDIF
ENDIF

;                                                                        _
; This is a kludge that needs to be cleaned up.  We need to know where T/R is for
; the board we're using.  The main Lumos code has logic for this which should be
; visible here. For right now, we're hard coding this for a standalone Lumos board.
;						           _
IF LUMOS_ARCH == "4685"
HAS_T_R			EQU	1		; RB0 is T/R output
PLAT_T_R		EQU	LATB
PORT_T_R		EQU	PORTB
TRIS_T_R		EQU	TRISB
BIT_T_R			EQU	0
PLAT_RED	EQU	LATE
PLAT_YELLOW	EQU	LATE
PLAT_GREEN	EQU	LATE
PLAT_ACTIVE	EQU	LATA
BIT_RED		EQU	2
BIT_YELLOW	EQU	1
BIT_GREEN	EQU	0
BIT_ACTIVE	EQU	5
TRIS_RED	EQU	TRISE
TRIS_YELLOW	EQU	TRISE
TRIS_GREEN	EQU	TRISE
TRIS_ACTIVE	EQU	TRISA
ELSE
 IF LUMOS_ARCH == "14K50"
HAS_T_R			EQU	1		; RB0 is T/R output
PLAT_T_R		EQU	LATB
PORT_T_R		EQU	PORTB
TRIS_T_R		EQU	TRISB
BIT_T_R			EQU	6
PLAT_RED	EQU	LATC
PLAT_YELLOW	EQU	LATC
PLAT_GREEN	EQU	LATC
PLAT_ACTIVE	EQU	LATC
BIT_RED		EQU	6
BIT_YELLOW	EQU	3
BIT_GREEN	EQU	4
BIT_ACTIVE	EQU	5
TRIS_RED	EQU	TRISC
TRIS_YELLOW	EQU	TRISC
TRIS_GREEN	EQU	TRISC
TRIS_ACTIVE	EQU	TRISC
 ELSE
  ERROR "Bad architecture switch in flash_update_user.inc"
 ENDIF
ENDIF
