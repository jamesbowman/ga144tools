        .text
        .even

        .globl _pdpmain
_pdpmain:
        mov     $65535,r0
        mfpi    $0x1111                 # start timer
delay:
        dec     r0
        cmp     $0,r0
        bne     delay
        mfpi    $0x2222                 # stop timer
        br      _pdpmain
