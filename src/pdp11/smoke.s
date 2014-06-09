        .text
        .even

        .globl _pdpmain
_pdpmain:
        mov     $0x8017,r0
        mfpi    r0
        asl     r0
        mfpi    r0
hang:   br      hang
