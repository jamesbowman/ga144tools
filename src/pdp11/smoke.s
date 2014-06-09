        .text
        .even

        .globl _pdpmain
_pdpmain:
        mov     $table,r1
        mov     (r1)+,r0
        asl     r0                      # Should be 80aa
        add     (r1)+,r0                # Should be 845d
        sub     (r1)+,r0                # Should be fd3c
        add     @0(r1),r0               # Should be bd91
        asr     r0                      # Should be dec8
        sub     $(0xdec8+1),r0

        mfpi    r0                      # Should be ffff
hang:   br      hang

table:  .word   0xc055
        .word   947
        .word   0x8721
        .word   table
