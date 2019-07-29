.segment "ROM"
	LDX #$FF
	TXS
	LDA #$AA
	STA $0000
loop:	
	LDA $0000
	STA $FE60
	INC $0000
	JSR delay
	JMP loop


delay:
	LDA #$FF
	STA $0002
	LDA #$FF
	STA $0003
	LDA #$00
	TAX
delay_loop:	
	DEC $02
	CPX $02
	BNE delay_loop
	LDA #$FF
	STA $02
	DEC $03
	CPX $03
	BNE delay_loop
	RTS

.segment "VECTORS"
	.WORD $FF00
	.WORD $FF00
	.WORD $FF00
