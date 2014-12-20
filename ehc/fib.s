	.text

	.even
	.globl _fib
_fib:
	mov r2, -(sp)
	mov r3, -(sp)
	mov 06(sp), r0
	mov r0, r1
	dec r1
	tst r0
	beq L_4
	mov $01, r0
	clr r2
	br L_3
L_9:
	mov r0, r2
	mov r3, r0
L_3:
	mov r0, r3
	add r2, r3
	dec r1
	cmp r1,$-01
	bne L_9
L_2:
	mov (sp)+, r3
	mov (sp)+, r2
	rts pc
L_4:
	clr r0
	br L_2
	.even
	.globl _Main
_Main:
	mov r2, -(sp)
	mov r3, -(sp)
	mov $-01, r1
	clr r2
	mov $01, r0
	br L_12
L_13:
	mov r0, r2
	mov r3, r0
L_12:
	mov r0, r3
	add r2, r3
	dec r1
	bne L_13
	mov (sp)+, r3
	mov (sp)+, r2
	rts pc
