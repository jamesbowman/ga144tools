	.text

	.even
	.globl _fib
_fib:
	mov r2, -(sp)
	mov r3, -(sp)
	mov 06(sp), r1
	mov $01, r2
	clr r0
L_2:
	dec r1
	cmp r1,$-01
	beq L_5
	mov r2, r3
	add r0, r3
	mov r2, r0
	mov r3, r2
	br L_2
L_5:
	mov (sp)+, r3
	mov (sp)+, r2
	rts pc
	.even
	.globl _Main
_Main:
	mov $-01, -(sp)
	jsr pc, _fib
	add $02, sp
;# 17 "fib.c" 1
	mfpi r0
;# 0 "" 2
	rts pc
