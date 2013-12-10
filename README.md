0
0
0
0
0
0
0
0
: fetch   call    ask
          call    -d--
          jmp     fetch
: ask     @b      dup     !       @p
          2
          .       +       !b      ;
: reg16   call    lit16
: rfetch  a       push    a!      @
          pop     a!      ;
: lit16   call    ask
          @       ;
: setpc   call    lit16
          !b      ;
: /8reg   2/      2/      2/      .
: &reg    p@      and     ;
          7
: binop   ( -- dst src1 src2 )
          call    ask
          @b      dup     call    &reg
          push    dup     call    /8reg
          push    call    /8reg
          pop     call    rfetch
          pop     jump    rfetch
: jsr     call    ask
          @b      call    sp      .
          dup     push    -       !
          !       pop     p@      .
          -2
          jmp     sp+
: ret     p@      call    sp
          2
          dup     !       call    sp+
          @       !b      ;
: sp      p@      drop    p@      ;
: sp+     +       p!      ;
0

; a points to IP
; b points to memory interface


: !16     -       !       !       ;
: @16     !       @       ;

ccpu - C/C++ for GA144
======================

Instruction set notes:

  http://www.colorforth.com/inst.htm

  http://www.colorforth.com/arith.htm

  http://www.intellasys.net/phpBB/viewforum.php?f=8

  http://www.colorforth.com/etherCode.htm

Eagle library

  http://esaid.free.fr/tutoriel_arrayforth/Ga144_pcb/Ga144/GA144_SRAM_IS2/GA144/

1.8V DC-DC: http://www.diodes.com/datasheets/AP6015.pdf

128Kx16 SRAM: CY62137FV18LL

CCPU for GA144

The gcc target is an 8-register 32-bit CPU "CCPU" with 16 bit instructions.
CCPU is a Von Neumann architecture with program and data in SRAM.
Target execution rate is limited by the 55ns SRAM to 18 MIPS.

CCPU is in nodes 007, 008, 009. The nodes have ~10 cycles to execute the instruction.
Instructions, fetched from SRAM, arrive on 007's parallel bus.
007 interprets the instruction.
The 8 registers use 16 cells in 007's RAM.


How many multiplications per second?
  144 * 666e6 / 36 = 2.6 billion
  650 * 480 = 282 multiplications/pixel

label     slot0   slot1   slot2   slot3
x!        @p      drop    !p      ;
x         @p      ;
                       100

\ double convention is for the lsw to be on top













: dnot    push    -       pop     -
          ;
: d2*     dup     +       push    dup
          +       pop     ;
: d2/     2/      2*      a!      +*
          a       ;
: dxor    a!      push    a       or
          a!      pop     or      a
          ;
: dand    a!      push    a       and
          a!      pop     and     a
          ;
: d+      a!      push    a       .
          +       a!      pop     .
          +       a       ;
: reg32   call    ask
          drop    @       2*      a!
          @+      @       ;
: lit32   call    ask
          drop    @
          call    ask
          drop    @       ;



00000 Completion (jump) Address
00000 Transfer (store) Address
00007 Transfer Size in words
      Data words
