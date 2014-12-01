Eagle library

  http://esaid.free.fr/tutoriel_arrayforth/Ga144_pcb/Ga144/GA144_SRAM_IS2/GA144/

RAM http://www.cypress.com/?docID=45536 takes ~4nJ per access (2.2e-3 amp * 1.8 volt * 1e-6s)

http://www.greenarraychips.com/home/documents/greg/WP003-100617-msp430.pdf: one instruction is 7 pJ

For at Atmega 1.8V at 1MHz, 360 pJ per instruction
0.2e-3 amp * 1.8 volt * 1e-6s in picojoules

For the Arduino 5V at 16MHz, 5000 pJ per instruction
16e-3 amp * 5 volt * (1/16e6)s in picojoules

http://gadgetmakersblog.com/power-consumption-arduinos-atmega328-microcontroller/



1.8V DC-DC: http://www.diodes.com/datasheets/AP6015.pdf

128Kx16 SRAM: CY62137FV18LL
256Kx16 SRAM: CY62147EV18

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

Board:
  1.8V vccio
Mandelbrot:
  480 x 272 x 30 = 255ns per sample, 3.9 MHz
  Each multiply is 72ns, 256 multiplies, 18432ns
  So need 72 nodes

00000 Completion (jump) Address
00000 Transfer (store) Address
00007 Transfer Size in words
      Data words


Byte coded

unary operators:
  get
  put
  push
  pop
  lit4
  not
  neg
  inc
  dec
nullary:
  return
  call
  dup

Polyforth:

  : asd 1000 for 1000 for 0 drop next next ;
  takes about 3 seconds.
  IIRC a 16 MHx Novix takes less than 1 second for this, and most 8 bit processors are some tens of seconds.

    1000
a:  1000
b:  0       \ inner is 6 insns, 100ns each, 600ns. total 600ms
    drop
    1-
    dup
    0=
    0branch b
    drop
    0branch a
    drop


    1000
    0
    do
a   0
    1000
    do
b   0     \ inner is 3 insns, 50ns each, 150ns. total 150ms
    drop
    loop b
    loop a









ZZ
