import re

import sys
import array
from ga144 import GA144
import draw

crib = {}
for r,rn in enumerate("r0 r1 r2 r3 r4 r5 sp pc".split()):
    for m,mn in enumerate("%s [%s+] [-%s] [[%s+]] [%s] [%s+X] byte[%s]".split()):
        crib[mn % rn] = (m << 3) | r
    
def asm1(pc, symbols, line):
  f = line.split()
  op = [
    '#',
    'MOV',
    'ADD',
    'SUB',
    'BIC',
    'XOR',
    'ASR',
    'ASL',
    'CMPU',
    'CMPS',
    'CALL',
    'BRA',
    'BEQ',
    'BNE',
    'BLT',
    'EMIT'].index(f[0].upper())
  if op == 0:
    return int(f[1], 0)
  if op <= 10:
    (dst, src) = f[1].split(',')
    return op | (crib[src] << 4) | (crib[dst] << 10)
  if op == 15:
    return op | (crib[f[1]] << 4)
  dst = symbols[f[1]]
  return op | (0xfff0 & ((dst - (pc + 2)) << 4))

benchmark = """
        emit [pc+]
         # 0x1111
        mov  r4,[pc+]
         # 1
        mov  r1,[pc+]
         # 0
inner:
        sub  r1,r4
        cmpu r1,r3
        bne inner
        emit [pc+]
          # 0x2222
again:
        bra again
"""

memorydump = """
        mov  [[pc+]],[pc+]
            # 7777
            # 38
        mov  r0,[pc+]
            # 0
dumper:
        emit [r0+]
        cmpu r0,[pc+]
            # 40
        bne dumper
again:
        bra again
"""

code = """
        mov     [-sp],r2
        call    pc,[pc+]
            # 10
        emit    sp
again:
        bra     again
func:
        emit    r0
        emit    r1
        emit    r2
        emit    r3
        emit    r4
        emit    sp
        emit    [sp]
        mov     pc,[sp+]
    
"""

def assemble(code):
    pgm = []
    symbols = {}
    for l in code.split('\n'):
        pc = 2 * len(pgm)
        if l.strip():
            if ':' in l:
                symbols[l.split(':')[0]] = pc
            else:
                pgm.append(asm1(pc, symbols, l))
    return pgm

if __name__ == '__main__':
    g = GA144()
    g.loadprogram("../pdp11/plumbing.ga")

    g.loadprogram("vm.ga")

    # Find the symbols in the core that are useful, pre-load them
    # into the fragment nodes
    for ucnode in ('507', ):
        for p,v in g.node['508'].symbols.items():
            if p not in g.node[ucnode].symbols:
                g.node[ucnode].symbols[p] = v

    g.loadprogram("fragments.ga")

    # Load the program into node 509
    pn = g.node['509']
    pn.prefix = [pn.assemble(["jump", "WEST"])]
    pn.load_pgm = assemble(code)
    print pn.load_pgm

    g.download(sys.argv[1], 460800)
