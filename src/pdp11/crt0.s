# crt0 for GA144 soft PDP11
#
# The first 8 locations of memory are the registers R0-R7
# This crt0 saves a few words by putting the initialization
# code at 0 also - it is clobbered as soon as the real
# program runs.
        .text
        .even
        mfpi    $0x5555         # Write 5555 to debug
        jmp     _pdpmain        # That is main
        .word 0
        .word 0
        .word 64                # Initial SP
        .word 0                 # Initial PC

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
# hang:   br hang
