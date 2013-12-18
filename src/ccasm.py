import sys
from ga144 import GA144, Illegal
import array

if __name__ == '__main__':
    g = GA144()
    g.loadprogram("ccpu.ga")
    print
    n = g.node['107']
    print n.assemble("call EAST".split())
    pgm = []
    for i,l in enumerate(open(sys.argv[1])):
        o = l
        if '#' in l:
            l = l[:l.index('#')]
        else:
            l = l[:-1]
        l = l.strip().split()
        if l:
            if l[0] == ':':
                n.symbols[l[1]] = len(pgm)
            else:
                bin = n.assemble(l)
                if not n.is_literal(l):
                    if (bin >> 16) != 0x2:
                        raise Illegal, 'Illegal op "%s" for slot3' % l[0]
                print "%04x:  %05x  %s" % (i, bin, o)
                pgm.append(bin & 0xffff)
    open("bin", "wb").write(array.array('H', pgm).tostring())
