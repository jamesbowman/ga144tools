import sys
import ga144
import array
import copy

class Node(ga144.Node):
    def aline(self, l):
        return self.assemble(l.split())

    def pump(self, path):
        # print 'pump', self.name
        r = []
        if path:
            next = {
                'NORTH' : lambda: self.n,
                'EAST'  : lambda: self.e,
                'SOUTH' : lambda: self.s,
                'WEST'  : lambda: self.w}[path[0]]()
            downstream = next.pump(path[1:])
            r += [self.assemble("@p dup a! @p".split()),
                  self.assemble(["call", path[0]]),
                  len(downstream) - 1,
                  self.assemble("push !".split()),
                  self.assemble("@p ! unext".split())] + downstream
        # print self.name, self.load_pgm
        self.prefix = self.prefix[:-1]
        if not self.load_pgm:
            r += self.prefix
        else:
            r += ([self.aline("a dup dup @p"),
                   len(self.load_pgm) - 1,
                   self.aline("push or a!"),
                   self.aline("@p !+ unext")] + self.load_pgm)
            r += self.prefix
        return r

if __name__ == '__main__':
    n = Node('605')
    symbols = copy.copy(n.symbols)
    s = [None]

    c = []
    def process_block(b):
        if not b:
            return []
        blockname = c[0].split()[-1]
        symbols[blockname] = len(s)

        n.symbols = symbols
        n.load("".join(c[1:]))

        print "\n".join(n.listing)
        print n.prefix
        pp = n.pump(None)
        print 'pump'
        print "\n".join(["%05x" % p for p in pp])
        bits = [1 & (pp[i / 18] >> (17 - (i % 18))) for i in range(18 * len(pp))]
        sbits = [x << (7 - (i % 8)) for i,x in enumerate(bits)]
        bytes = [sum(sbits[i:i+8]) for i in range(0, len(sbits), 8)]
        print len(bytes), bytes
        ab = array.array('B', [len(pp) - 1] + bytes).tostring()
        return [ab[i:i+64].ljust(64) for i in range(0, len(ab), 64)]

    for l in open(sys.argv[1]):
        if l.startswith("BLOCK"):
            s += process_block(c)
            c = []
        c.append(l)
    s += process_block(c)

    s[0] = s[-1]

    s = "".join(s).ljust(4096, chr(0xff))
    open("image", "w").write(s)
