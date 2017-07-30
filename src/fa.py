import sys
import ga144
import array
import copy
import re
from subprocess import Popen, PIPE

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

class Program:
    def __init__(self):
        self.s = [None]
        self.org = 1

    def append(self, frag):
        self.s.append(frag)
        self.org += 1

    def resolve(self, (f, i)):
        # Resolve a forward reference
        # print 'resolved', (f,i), 'to', self.org
        self.s[f][i] = self.org

if __name__ == '__main__':
    # Pick up fixed symbols from nt.ga node 605
    g = ga144.GA144()
    g.loadprogram("nt.ga")

    # Load R's symbols, and X's symbols
    # for use in the fragment source
    symbols = copy.copy(g.node['605'].symbols)
    symbols.update(g.node['606'].symbols)
    # print "\n".join(sorted(symbols))

    n = Node('605')
    prg = Program()

    listing = open("lst", "w")
    def lst(s):
        listing.write(s + "\n")

    c = []
    def process_code(c):
        n.symbols = symbols
        n.listing = []
        n.load("".join(c))

        lst("(fragment %d)" % prg.org)
        lst("\n".join(n.listing[1:]))
        pp = n.pump(None)
        bytesize = ((8 + 18 * len(pp)) / 8)
        lst("%d bytes\n" % bytesize)
        return pp

    def process_forth(src):
        cs = []
        c = []
        def newblock(c):
            if c:
                prg.append(process_code([l+"\n" for l in c]))
            return []
        for w in " ".join(src).split():
            if re.match("^-?[0-9](x[[0-9a-f]+|[0-9]*)$", w):
                c.extend(["@p call LIT", w])
            elif w == ";":
                c.extend(["call DORETURN"])
                c = newblock(c)
            elif w == "begin":
                c = newblock(c)
                cs.append(prg.org)
            elif w == "again":
                c.extend(["@p call GO", str(cs.pop())])
                c = newblock(c)
            else:
                cs.append((prg.org, len(c) + 1))
                c.extend([
                  "@p call TO_R",
                  "0x3ffff",
                  "@p call GO",
                  "_" + w,
                  ])
                c = newblock(c)
                if cs:
                    prg.resolve(cs.pop())
        if c:
            c = newblock(c)
        assert cs == []

    p1 = Popen(["m4", sys.argv[1]], stdout = PIPE)
    for l in p1.stdout:
        if l == "\n":
            continue
        if (l.startswith("CODE") or l.startswith("::")) and c:
            (kind, blockname) = c[0].split()
            symbols[blockname] = prg.org
            if kind == "CODE":
                lst("CODE %s" % blockname)
                prg.append(process_code(c[1:]))
            elif kind == "::":
                lst(":: %s" % blockname)
                process_forth(c[1:])
            c = []
        c.append(l)
    print 'cold at', symbols['_cold']
    prg.s[0] = process_code(c[1:])

    def bytecode(pp):
        bits = [1 & (pp[i / 18] >> (17 - (i % 18))) for i in range(18 * len(pp))]
        sbits = [x << (7 - (i % 8)) for i,x in enumerate(bits)]
        bytes = [sum(sbits[i:i+8]) for i in range(0, len(sbits), 8)]
        ab = array.array('B', [len(pp) - 1] + bytes).tostring()
        return ab.ljust((len(ab) + 63) & ~63, chr(0xff))

    s = [bytecode(pp) for pp in prg.s]
    s = "".join(s).ljust(4096, chr(0xff))

    open("image", "w").write(s)
