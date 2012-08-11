;
; To use the serial I/O module, you need to edit this
; include file to suit your application.
;
SIO_TX_BUFFER_START	EQU	0x100	; Starting address of 256-byte Tx buffer*
SIO_RX_BUFFER_START	EQU	0x200	; Starting address of 256-byte Rx buffer*
SIO_DATA_START		EQU	0x300	; Starting address for SIO module variable storage
SIO_TABLE_START		EQU	0x15000	; Starting ROM address for SIO module tables*
;
; * must be aligned to the start of a 256-byte bank.
;
