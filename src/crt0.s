        .text

        .even
        .word 10000
        .word 10001
        .word 10002
        .word 10003
        .word 10004
        .word 10005
        .word 10006
        .word 16
label:
        add $100,r0
        mfpi r0
        mfpi r1
        mfpi r2
        mfpi r3
        mfpi r4
        mfpi r5
        mfpi r6
        mfpi r7
        jmp label

        mov 11(sp),100(sp)
