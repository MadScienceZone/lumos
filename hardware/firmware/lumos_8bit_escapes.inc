;
; Sending 8-bit data bytes in our 7-bit protocol
; (in data bytes, in other words) requires this
; escaping mechanism:
;   If high bit set, send $7E + low 7 bits
;   Literal $7E is sent as $7F + $7E
;   Literal $7F is sent as $7F + $7F
; 
; Other interesting cases inferred from the above:
;   $FE is sent as $7E + $7E
;   $FF is sent as $7E + $7F
;
; This calls the SIO_WRITE_W entry point, so the bank
; will shift as a result.
;
SND8BIT	MACRO	VALUE
	MOVLW	VALUE
	SEND_8_BIT_W
	ENDM

S8B_LABEL SET	1
SEND_8_BIT_W MACRO
	MOVWF	EIGHTBITSIOBUF, ACCESS
	MOVLW	0x7F				; sending literal $7F?
	CPFSEQ	EIGHTBITSIOBUF, ACCESS
	BRA	S8B_CHK_7E#v(S8B_LABEL)
	CALL	SIO_WRITE_W			; send $7F to escape first
	MOVLW	0x7F				; then the literal $7F itself.
	CALL	SIO_WRITE_W			
	BRA	S8B_END#v(S8B_LABEL)
S8B_CHK_7E#v(S8B_LABEL):
	MOVLW	0x7E				; sending literal $7E?
	CPFSEQ	EIGHTBITSIOBUF, ACCESS
	BRA	S8B_CHK_MSB#v(S8B_LABEL)
	MOVLW	0x7F				; send $7F to escape first
	CALL	SIO_WRITE_W
	MOVLW	0x7E				; then the literal $7E itself.
	CALL	SIO_WRITE_W
	BRA	S8B_END#v(S8B_LABEL)
S8B_CHK_MSB#v(S8B_LABEL):
	BTFSS	EIGHTBITSIOBUF, 7, ACCESS	; MSB set?
	BRA	S8B_SEND_NORMAL#v(S8B_LABEL)
	MOVLW	0x7E				; send $7E to escape first
	CALL	SIO_WRITE_W
	BCF	EIGHTBITSIOBUF, 7, ACCESS	; clear MSB and (fall-thru to) send it.
S8B_SEND_NORMAL#v(S8B_LABEL):
	MOVF	EIGHTBITSIOBUF, W, ACCESS	; send byte
	CALL	SIO_WRITE_W	
S8B_END#v(S8B_LABEL):
S8B_LABEL ++
	ENDM

