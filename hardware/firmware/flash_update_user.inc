;
; To use the flash loader module, you need to edit this
; include file to suit your application.
;
FLASH_UPDATE_START	EQU	0x17000 ; Start of the flash loader code
FLASH_UPDATE_RST_VECTOR	EQU	_BOOT	; Production boot vector to use once firmware is loaded.
FLASH_UPDATE_ROM_START	EQU	0x00008 ; Start of zone which we're allowed to change
FLASH_UPDATE_ROM_END	EQU	0x16FFF ; End of zone which we're allowed to change
