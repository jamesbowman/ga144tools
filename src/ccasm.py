import sys
from ga144 import GA144
import array

if __name__ == '__main__':
    g = GA144()
    g.loadprogram("ccpu.ga")
    print
    n = g.node['107']
    print n.assemble("call EAST".split())
    pgm = []
    for i,l in enumerate(open(sys.argv[1])):
        l = l[:-1]
        bin = n.assemble(l.split())
        print "%04x:  %05x  %s" % (i, bin, l)
        pgm.append(bin & 0xffff)
    open("bin", "wb").write(array.array('H', pgm).tostring())
