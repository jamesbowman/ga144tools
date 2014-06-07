# crt0 for GA144 soft PDP11
#
# The first 8 locations of memory are the registers R0-R7
# This crt0 saves a few words by putting the initialization
# code at 0 also - it is clobbered as soon as the real
# program runs.
        .text
        .even
        mfpi    $0x5555         # Write 5555 to debug
        mfpi    $0xaaaa         # Write aaaa to debug
        jmp     _pdpmain        # That is main
#        jmp     silly
        .word 64                # Initial SP
        .word 0                 # Initial PC

# silly:
#         jsr     pc,tell
#         jmp     silly
# 
# tell:
#         mfpi    $10101
#         mfpi    sp
#         mfpi    62
#         rts     pc
# hang:   br hang
# 
#         clr r0
# loop:
#         mfpi    r0
#         add     $1,r0
#         cmp     r0,$10
#         bne     loop
#         br      cold

#         mov 11(sp),100(sp)
#         bpt
#         bpt
