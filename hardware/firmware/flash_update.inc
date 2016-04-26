;	
; vim:set syntax=pic ts=8:
		LIST N=86
;@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
;@@                                                                         @@
;@@                                                                         @@
;@@ @@@@@  @       @@@    @@@   @   @                                       @@
;@@ @      @      @   @  @   @  @   @    FLASH ROM UPDATE LOADER            @@
;@@ @      @      @   @  @      @   @                                       @@
;@@ @@@@   @      @@@@@   @@@   @@@@@    1.0                                @@
;@@ @      @      @   @      @  @   @                                       @@
;@@ @      @      @   @  @   @  @   @                                       @@
;@@ @      @@@@@  @   @   @@@   @   @                                       @@
;@@                                                                         @@
;@@ Copyright (c) 2013 by Steven L. Willoughby, Aloha, Oregon, USA.  All    @@
;@@ Rights Reserved.                                                        @@
;@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
;
#include "flash_update_bits.inc"
; 
;==============================================================================
; PUBLIC ENTRY POINTS
;==============================================================================
;
	EXTERN	FLASH_UPDATE_START
	EXTERN	FLASH_UPDATE_END
	EXTERN	FLASH_UPDATE_BOOT
	EXTERN	FLASH_UPDATE_NEXT_BLOCK
