	.file	"fib.c"
.text
	.balign 2
	.global	fib
fib:
; start of function
; framesize_regs:     0
; framesize_locals:   0
; framesize_outgoing: 0
; framesize:          0
; elim ap -> fp       2
; elim fp -> sp       0
; saved regs:(none)
	; start of prologue
	; end of prologue
	MOV.W	#1, R14
	MOV.W	#0, R13
.L2:
	ADD.W	#-1, R12
	CMP.W	#-1, R12 { JEQ	.L5
	MOV.W	R13, R15
	ADD.W	R14, R15
	MOV.W	R14, R13
	MOV.W	R15, R14
	BR	#.L2
.L5:
	MOV.W	R13, R12
	; start of epilogue
	RET
	.size	fib, .-fib
	.balign 2
	.global	Main
Main:
; start of function
; framesize_regs:     0
; framesize_locals:   0
; framesize_outgoing: 0
; framesize:          0
; elim ap -> fp       2
; elim fp -> sp       0
; saved regs:(none)
	; start of prologue
	; end of prologue
	MOV.W	#-1, R12
	CALL	#fib
 ; 17 "fib.c" 1
	output R12
 ; 18 "fib.c" 1
	output #2375
	; start of epilogue
	RET
	.size	Main, .-Main
	.ident	"GCC: (GNU) 5.0.0 20141216 (experimental)"
