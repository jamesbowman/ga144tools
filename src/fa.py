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

tags = {
    '#returns'  : 0x080,
    '#inline'   : 0x100,
}

class Program:
    def __init__(self):
        self.s = {}
        self.org = 1

    def append(self, frag, flags = 0):
        self.s[self.org] = (flags, frag)
        bytesize = ((8 + 18 * len(frag) + 7) / 8)
        self.org += (bytesize + 63) / 64

    def resolve(self, (f, i)):
        # Resolve a forward reference
        # print 'resolved', (f,i), 'to', self.org, 'was', self.s[f][1][i]
        assert self.s[f][1][i] == 0x3ffff
        self.s[f][1][i] = self.org

    def binary(self):
        def bytecode((flags, pp)):
            bits = [1 & (pp[i / 18] >> (17 - (i % 18))) for i in range(18 * len(pp))]
            sbits = [x << (7 - (i % 8)) for i,x in enumerate(bits)]
            bytes = [sum(sbits[i:i+8]) for i in range(0, len(sbits), 8)]
            wl = len(pp) - 1
            if pp.datablock:
                size=[]
            else:
                assert 0 <= wl < 64
                size=[(0xff & flags) | wl]
            ab = array.array('B', size + bytes).tostring()
            return ab.ljust((len(ab) + 63) & ~63, chr(0xff))

        s = [bytecode(self.s[f]) for f in sorted(self.s)]
        padsize = (len(s) + 4095) & ~4095
        s = "".join(s).ljust(padsize, chr(0xff))
        return s

class Block(list):
    def __init__(self, obj=None, datablock=None):
        super( Block, self ).__init__( obj or [] )
        self.datablock=False
        if type(obj) is Block:
            self.datablock = obj.datablock
        if datablock is not None:
            self.datablock = datablock

def cleanup(s):
    for l in s:
        l = l.strip()
        if '\\' in l:
            l = l[:l.index('\\')]
        if '(' in l:
            l = l[:l.index('(')]
        if l:
            yield l

def tokenize(s):
    tokens = []
    while s:
        b, m, s = s.partition('s" ')
        tokens.extend([w.lower() for w in b.split()])
        if m == 's" ':
            tokens.append('s"')
            ss, _, s =  s.partition('"')
            tokens.append(ss)
    return tokens

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

    c = Block()
    def process_code(c):
        n.symbols = symbols
        n.listing = []
        n.load("\n".join(c))

        lst("(fragment %d)" % prg.org)
        lst("\n".join(n.listing[1:]))
        if c.datablock:
            pp = Block(map(int, c), True)
        else:
            pp = Block(n.pump(None))

        bytesize = ((8 + 18 * len(pp) + 7) / 8)
        lst("%d bytes (%d words)\n" % (bytesize, len(pp)))
        return pp

    p1 = Popen(["m4", sys.argv[1]], stdout = PIPE)

    def code(c):
        if c:
            c0s = c[0].split()
            kind = c0s[0]
            blockname = c0s[1]
            flags = sum([tags[ht] for ht in c0s[2:]])
            assert kind == "CODE"
            symbols["_" + blockname] = prg.org
            lst("CODE _%s" % blockname)
            x = process_code(Block(c[1:]))
            prg.append(x, flags)

    for l in cleanup(p1.stdout):
        if '%FORTHLIKE%' in l:
            break
        if l.startswith("CODE") and c:
            code(c)
            c = Block()
        c.append(l)
    code(c)

    # From here on code uses the forth-like syntax
    cs = []
    c = Block()
    def newblock(c, flags = 0):
        if c:
            prg.append(process_code(c), flags)
        return Block()
    HERE = 0
    variables = {}
    compilable = {
        "i": [
            "call -!",
            "pop pop over",
            "over push push",
            "over - . +" ],
        ">r": [
            "call TO_R",
            "@+" ],
        "r>": [
            "call -!",
            "@p !b @b",
            "  @+ !p", ],
    }
    for l in cleanup(p1.stdout):
        ww = tokenize(l)

        if ww[0] == "variable":
            variables[ww[1]] = HERE
            HERE += 2
            continue
        if ww[0] == ":":
            defining = ww[1]
            assert cs == []
            c = newblock(c)
            lst(": %s" % defining)
            symbols["_" + defining] = prg.org
            ww = ww[2:]

        ww_iter = iter(zip(ww, ww[1:]+[None]))
        for w, next_w in ww_iter:
            if next_w == "allot":
                HERE += int(w)
                next(ww_iter)
            elif next_w == ",":
                c.extend([w])
                next(ww_iter)
            elif w == 's"':
                s = next_w
                for char in reversed(s):
                    c.extend(["@p call LIT", str(ord(char))]) #TODO: can overflow words
                c.extend(["@p call LIT", str(len(s)-1)])
                next(ww_iter)
            elif re.match("^-?[0-9](x[[0-9a-f]+|[0-9]*)\.?$", w):
                if w.endswith('.'):
                    i = int(w[:-1], 0)
                    h = (i >> 18) & 0x3ffff
                    l = (i      ) & 0x3ffff
                    c.extend(["@p call LIT", str(l)])
                    c.extend(["@p call LIT", str(h)])
                else:
                    c.extend(["@p call LIT", w])
            elif w in variables:
                c.extend(["@p call LIT", str(variables[w])])
            elif w == ";":
                samefrag = symbols["_" + defining] == prg.org
                print "END OF", defining, samefrag
                flags = 0
                if samefrag:
                    flags |= (tags['#inline'] | tags['#returns'])
                else:
                    c.extend(["call DORETURN"])
                c = newblock(c, flags)
            elif w == "begin":
                cs.append((prg.org, len(c) + 1))
                c.extend(["@p call GO", "0x3ffff"])
                c = newblock(c)
                prg.resolve(cs.pop())
                cs.append(prg.org)

            elif w == "for":
                cs.append((prg.org, len(c) + 2))
                c.extend(["push @+", "@p call GO", "0x3ffff"])
                c = newblock(c)
                prg.resolve(cs.pop())
                cs.append(prg.org)
            elif w == "do":
                cs.append((prg.org, len(c) + 4))
                c.extend(["- @+ dup", "push . + ", "push @+", "@p call GO", "0x3ffff"])
                c = newblock(c)
                prg.resolve(cs.pop())
                cs.append(prg.org)

            elif w == "again":
                c.extend(["@p call GO", str(cs.pop())])
                c = newblock(c)
            elif w in ("if", "while"):
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
            elif w == "else":
                p = cs.pop()
                cs.append((prg.org, len(c) + 1))
                c.extend(["@p call GO", "0x3ffff"])
                c = newblock(c)
                prg.resolve(p)
            elif w == "then":
                cs.append((prg.org, len(c) + 1))
                c.extend(["@p call GO", "0x3ffff"])
                c = newblock(c)
                # CS: then then 
                prg.resolve(cs.pop())
                prg.resolve(cs.pop())
            elif w == "repeat":
                fin = cs.pop()
                begin = cs.pop()
                c.extend(["@p call GO", str(begin)])
                c = newblock(c)
                prg.resolve(fin)
            elif w == "until":
                begin = cs.pop()
                if begin == prg.org and len(c) < 20:
                    cs.append((prg.org, len(c) + 8))
                    c = Block(["a!", "jump begin2", ": begin", "@+", ": begin2"] + c)
                    c.extend([
                      "if begin",
                      "@+",
                      "@p call GO",
                      "0x3ffff",
                      "jump NORTH",
                      ])
                else:
                    cs.append((prg.org, len(c) + 1))
                    c.extend([
                      "push @p @p",
                      "0x3ffff",
                      str(begin),
                      "pop call IFELSE",
                      "@+",
                      ])
                c = newblock(c)
                prg.resolve(cs.pop())
            elif w in ("next", "loop"):
                begin = cs.pop()
                if begin == prg.org and len(c) < 20:
                    cs.append((prg.org, len(c) + 6))
                    c = Block( ["a! jump main", ": main"] + c )
                    c.extend([
                      "next main",
                      "@p call GO",
                      "0x3ffff",
                      "jump NORTH",
                      ])
                else:
                    cs.append((prg.org, len(c) + 1))
                    c.extend([
                      "@p @p",
                      "0x3ffff",
                      str(begin),
                      "next swap",
                      "drop call GO",
                      ])
                c = newblock(c)
                prg.resolve(cs.pop())
                if w == "loop":
                    c.extend(["pop drop"])
            elif w == "'":
                word = next(ww_iter)[0]
                if word in variables:
                    addr = variables[word]
                else:
                    addr = symbols['_' + word]
                c.extend(["@p call LIT", str(addr)])
            elif w == "data-block":
                c.datablock=True
            elif w in compilable:
                c.extend(compilable[w])
            else:
                (flags, code) = prg.s[symbols["_" + w]]
                if flags & 0x100:
                    c.extend([str(op) for op in code])
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
            if len(c) > 54 and not c.datablock:
                cs.append((prg.org, len(c) + 1))
                c.extend([
                  "@p call GO",
                  "0x3ffff",
                  ])
                c = newblock(c)
                if cs:
                    prg.resolve(cs.pop())


    # Put a copy of the 'boot' fragment at zero
    prg.s[0] = prg.s[symbols['_boot']]
    f = open("flash.el", "w")
    for n, c in prg.s.items():
        f.write("(_fragment {} {} {})\n".format( n, (0xff & c[0]) | len(c[1]), " ".join( map(str, c[1] ))))
    f.write( "(_boot {})\n".format( symbols['_boot'] ) )
    f.close()
    open("image", "wb").write(prg.binary())
