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
        self.s = {}
        self.org = 1

    def append(self, frag):
        self.s[self.org] = frag
        bytesize = ((8 + 18 * len(frag) + 7) / 8)
        self.org += (bytesize + 63) / 64

    def resolve(self, (f, i)):
        # Resolve a forward reference
        print 'resolved', (f,i), 'to', self.org
        self.s[f][i] = self.org

def cleanup(s):
    for l in s:
        l = l.strip()
        if '\\' in l:
            l = l[:l.index('\\')]
        if '(' in l:
            l = l[:l.index('(')]
        if l:
            yield l

if __name__ == '__main__':
    # Pick up fixed symbols from nt.ga node 605
    g = ga144.GA144()
    g.loadprogram("nt.ga")

    print "\n".join(g.node['606'].listing)
    # Load R's symbols, and X's symbols
    # for use in the fragment source
    symbols = copy.copy(g.node['605'].symbols)
    symbols.update(g.node['606'].symbols)
    # print "\n".join(sorted(symbols))

    n = Node('605')
    n.chip = g
    prg = Program()

    listing = open("lst", "w")
    def lst(s):
        listing.write(s + "\n")

    c = []
    def process_code(c):
        n.symbols = symbols
        n.listing = []
        n.load("\n".join(c))

        lst("(fragment %d)" % prg.org)
        lst("\n".join(n.listing[1:]))
        pp = n.pump(None)
        bytesize = ((8 + 18 * len(pp) + 7) / 8)
        lst("%d bytes\n" % bytesize)
        return pp

    p1 = Popen(["m4", sys.argv[1]], stdout = PIPE)

    def code(c):
        if c:
            (kind, blockname) = c[0].split()
            assert kind == "CODE"
            symbols["_" + blockname] = prg.org
            lst("CODE _%s" % blockname)
            prg.append(process_code(c[1:]))

    for l in cleanup(p1.stdout):
        if '%FORTHLIKE%' in l:
            break
        if l.startswith("CODE") and c:
            code(c)
            c = []
        c.append(l)
    code(c)

    # From here on code uses the forth-like syntax
    cs = []
    c = []
    def newblock(c):
        if c:
            prg.append(process_code(c))
        return []
    for l in cleanup(p1.stdout):
        ww = l.split()
        if ww[0] == ":":
            assert cs == []
            c = newblock(c)
            lst(": %s" % ww[1])
            symbols["_" + ww[1]] = prg.org
            continue
        for w in ww:
            if re.match("^-?[0-9](x[[0-9a-f]+|[0-9]*)\.?$", w):
                if w.endswith('.'):
                    i = int(w[:-1], 0)
                    h = (i >> 18) & 0x3ffff
                    l = (i      ) & 0x3ffff
                    c.extend(["@p call LIT", str(l)])
                    c.extend(["@p call LIT", str(h)])
                else:
                    c.extend(["@p call LIT", w])
            elif w == ";":
                c.extend(["call DORETURN"])
                c = newblock(c)
            elif w == "begin":
                cs.append((prg.org, len(c) + 1))
                c.extend(["@p call GO", "0x3ffff"])
                c = newblock(c)
                prg.resolve(cs.pop())
                cs.append(prg.org)
            elif w == "again":
                c.extend(["@p call GO", str(cs.pop())])
                c = newblock(c)
            elif w == "if":
                cs.append((prg.org, len(c) + 2))
                cs.append((prg.org, len(c) + 1))
                c.extend([
                  "push @p @p",
                  "0x3ffff",
                  "0x3ffff",
                  "pop call IFELSE",
                  "@+",
                  ])
                c = newblock(c)
                prg.resolve(cs.pop())
            elif w == "then":
                cs.append((prg.org, len(c) + 1))
                c.extend(["@p call GO", "0x3ffff"])
                c = newblock(c)
                # CS: then then 
                prg.resolve(cs.pop())
                prg.resolve(cs.pop())
            elif w == "until":
                begin = str(cs.pop())
                cs.append((prg.org, len(c) + 1))
                c.extend([
                  "push @p @p",
                  "0x3ffff",
                  begin,
                  "pop call IFELSE",
                  "@+",
                  ])
                c = newblock(c)
                prg.resolve(cs.pop())
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

    # Put a copy of the 'boot' fragment at zero
    prg.s[0] = prg.s[symbols['_boot']]

    def bytecode(pp):
        bits = [1 & (pp[i / 18] >> (17 - (i % 18))) for i in range(18 * len(pp))]
        sbits = [x << (7 - (i % 8)) for i,x in enumerate(bits)]
        bytes = [sum(sbits[i:i+8]) for i in range(0, len(sbits), 8)]
        ab = array.array('B', [len(pp) - 1] + bytes).tostring()
        return ab.ljust((len(ab) + 63) & ~63, chr(0xff))

    s = [bytecode(prg.s[f]) for f in sorted(prg.s)]
    padsize = (len(s) + 4095) & ~4095
    s = "".join(s).ljust(padsize, chr(0xff))

    open("image", "wb").write(s)
