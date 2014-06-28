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
        add     $(-0xdec8+0x947),r0

        mov     $947,r1
        mov     $10,r2
        mul     r2,r1
        mfpi    r2

        mfpi    r0                      # Should be 0947

table:  .word   0xc055
        .word   947
        .word   0x8721
        .word   table
