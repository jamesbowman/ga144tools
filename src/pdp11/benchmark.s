        .globl _pdpmain
_pdpmain:
        mov     $65535,r0
        clr     r1
        mfpi    $0x1111
delay:
        dec     r0
        cmp     $0,r0
        bne     delay
        mfpi    $0x2222
        br      _pdpmain
