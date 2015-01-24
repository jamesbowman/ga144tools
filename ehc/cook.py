import sys
import re
import copy
import array
from ga144 import GA144
from heapq import heappush, heappop, heapify
from collections import defaultdict

# RAM controller command codes. Negative value means LOAD_BLOCK
DO_READ = 0     # then addr
DO_WRITE = 1    # then addr, val

class CodeBuf:
    def __init__(self):
        self.cc = []            # all generated code
        self.insn = []          # current insn
        self.afters = []        # words after the current insn
        self.a = None

    def flush(self):
        if self.insn:
            self.cc.append(8*" " + " ".join(self.insn))
            self.cc += self.afters
        self.insn = []
        self.afters = []

    def op(self, o):
        assert o in "; ex jump call unext next if -if @p @+ @b @ !p !+ !b ! +* 2* 2/ - + and or drop dup pop over a . push b! a!".split()

        slot3 = "; unext @p !p +* + dup .".split()
        if len(self.insn) == 3:
            if o in slot3:
                self.insn.append(o)
                self.flush()
                return
            else:
                self.flush()
        self.insn.append(o)
        if len(self.insn) == 4:
            self.flush()

    def ops(self, oo):
        [self.op(o) for o in oo.split()]

    def jz(self, dst):
        if len(self.insn) > 1:
            self.flush()
        self.insn.append("if " + dst)
        self.flush()

    def jp(self, dst):
        if len(self.insn) > 1:
            self.flush()
        self.insn.append("-if " + dst)
        self.flush()

    def jump(self, dst):
        if len(self.insn) > 1:
            self.flush()
        self.insn.append("jump " + dst)
        self.flush()

    def label(self, l):
        self.flush()
        self.cc.append(': ' + l)

    def lit(self, v):
        if v == 0:
            self.ops('dup dup or')
        else:
            self.afters.append(12*" " + str(v))
            self.op("@p")

    def ra(self, reg):
        if reg == 'sp':
            return self.ra('r6')
        assert reg[0] == 'r', "Expected register, got '%s'" % reg
        if self.a != reg:
            self.a = reg
            self.lit('07' + reg[1])
            self.op('a!')

    def src(self, s):
        """ Read T from source specified by s """
        if s[0] == '$':
            self.lit(int(s[1:], 0))
        elif s == '(sp)+':
            self.lit(DO_READ)
            self.op('!b')
            self.lit(2)
            self.ra('r6')
            self.ops('@ dup !b . + ! @b')
        else:
            m = re.match('\((..)\)', s)
            if m:
                self.lit(DO_READ)
                self.op('!b')
                self.ra(m.group(1))
                self.ops('@ !b @b')
            else:
                m = re.match('([0-9]+)\((..)\)', s)
                if m:
                    self.lit(DO_READ)
                    self.op('!b')
                    self.lit(int(m.group(1), 0))
                    self.ra(m.group(2))
                    self.ops('@ . + !b @b')
                else:
                    self.ra(s)
                    self.op('@')

    def dst(self, s):
        """ Write T to destination specified by s """
        if re.match('\(..\)\+', s):
            self.lit(DO_WRITE)
            self.op('!b')
            self.lit(2)
            self.ra(s[1:3])
            self.ops('@ dup !b . + ! !b')
        elif re.match('-\(..\)', s):
            self.lit(DO_WRITE)
            self.op('!b')
            self.lit(-2)
            self.ra(s[2:4])
            self.ops('@ . + dup ! !b !b')
        else:
            m = re.match('\((..)\)', s)
            if m:
                self.lit(DO_WRITE)
                self.op('!b')
                self.ra(m.group(1))
                self.ops('@ !b !b')
            else:
                m = re.match('([0-9]+)\((..)\)', s)
                if m:
                    self.lit(DO_WRITE)
                    self.op('!b')
                    self.lit(int(m.group(1), 0))
                    self.ra(m.group(2))
                    self.ops('@ . + !b !b')
                else:
                    self.ra(s)
                    self.op('!')

    def finish(self):
        self.lit(7)
        self.lit(070)
        self.ops('a! push')
        self.flush()
        self.ops('@+ !b unext')
        self.flush()
        self.jump('0xa9')

    def finish(self):
        self.flush()
        self.jump('SOUTH')


class BB:
    def __init__(self, code, succ, source):
        self.code = code
        self.succ = succ
        self.source = source

    def __repr__(self):
        return "BLOCK:\n" + "".join(["    " + x + "\n" for x in self.code]) + repr(self.succ) + "\n"

    def add(self, c):
        self.code.append(c)

    def convert(self, this, blocknums):
        cb = CodeBuf()
        cb.label('start')
        for l in self.code:
            ii = re.findall(r"[$\-\+()\w']+", l)
            if ii[0] == 'clr':
                cb.ops('dup dup or')
                cb.dst(ii[1])
            elif ii[0] == 'mov':
                (src, dst) = ii[1:]
                cb.src(src)
                cb.dst(dst)
            elif ii[0] == 'add':
                (src, dst) = ii[1:]
                cb.src(src)
                cb.ra(dst)
                cb.ops('@ . + !')
            elif ii[0] == 'inc':
                cb.lit(1)
                cb.ra(ii[1])
                cb.ops('@ . + !')
            elif ii[0] == 'dec':
                cb.lit(-1)
                cb.ra(ii[1])
                cb.ops('@ . + !')
            elif ii[0] == 'asl':
                cb.ra(ii[1])
                cb.ops('@ 2* !')
            elif ii[0] == 'mfpi':
                cb.src(ii[1])
                cb.lit('NORTH')
                cb.ops('a! !')
                cb.a = None
            else:
                assert 0, "Unrecognised %r" % ii

        def binchoice(jumpop, yes, no):
            if 1 and yes == this:
                jumpop('L1')
                cb.jump('start')
                cb.label('L1')
                cb.lit(~blocknums[no])
                cb.label('L2')
            else:
                jumpop('L1')
                cb.lit(~blocknums[yes])
                cb.jump('L2')
                cb.label('L1')
                cb.lit(~blocknums[no])
                cb.label('L2')

        if self.succ[0] == 'br':
            cb.lit(~blocknums[self.succ[1]])
        elif self.succ[0] == 'ifeq':
            (_, (a, b), yes, no) = self.succ
            cb.src(a)
            if b == "$-01":
                cb.ops('- 2* 2*')
            else:
                cb.src(b)
                cb.ops('or 2* 2*')
            binchoice(cb.jz, no, yes)
        elif self.succ[0] == 'iflt':
            (_, (a, b), yes, no) = self.succ
            cb.src(a)
            cb.lit(65535)
            cb.op('and')
            if 1 and b.startswith('$'):
                cb.lit(~(int(b[1:], 0) & 65535))
            else:
                cb.src(b)
                cb.lit(65535)
                cb.ops('and -')
            cb.ops('. +')
            binchoice(cb.jp, no, yes)
        elif self.succ[0] == 'deceq':
            (_, (reg,), yes, no) = self.succ
            cb.lit(-1)
            cb.ra(reg)
            cb.ops('@ . + dup !')
            binchoice(cb.jz, yes, no)
        elif self.succ[0] == 'tst':
            (_, (src,), yes, no) = self.succ
            cb.src(src)
            binchoice(cb.jz, yes, no)
        elif self.succ[0] == 'jsr':
            cb.lit(blocknums[self.succ[1]]) # rts will invert bits
            cb.lit(DO_WRITE)
            cb.op('!b')
            cb.lit(-2)
            cb.ra('r6')
            cb.ops('@ . + dup ! !b !b')
            cb.lit(~blocknums[self.succ[2]])
        elif self.succ[0] == 'rts':
            cb.lit(DO_READ)
            cb.op('!b')
            cb.lit(2)
            cb.ra('r6')
            cb.ops('@ dup !b . + ! @b -')
            # cb.lit('NORTH'); cb.ops('a! dup !'); cb.a = None
        else:
            assert 0, 'Bad succ %r' % (self.succ,)
        # cb.lit('NORTH'); cb.ops('a! dup - !'); cb.a = None
        cb.op('!b')
        cb.finish()

        cb.flush()
        return "".join(s + "\n" for s in cb.cc)

def psplit(f):
    """ read the assembler source, split it into basic blocks on labels """
    r = []
    b = None
    for line in f:
        line = line.strip()
        if line.startswith('.') or line.startswith(';'):
            continue
        elif re.match("^[A-Za-z_0-9]*:", line):
            if b:
                r.append(b)
            b = [line]
        else:
            if b:
                b.append(line)
    if b:
        r.append(b)
    return r

scratch = 0
def brbreak(b):
    """ if block b has a branch, split it """
    for i,l in enumerate(b):
        if l.split()[0] in ('bne', 'beq', 'bgt', 'blt', 'jsr'):
            p0 = b[:i+1]
            p1 = b[i+1:]
            if p1:
                global scratch
                scratch += 1
                rest = brbreak(p1)
                rest[0] = ['X%d:' % scratch] + rest[0]
                return [p0] + rest
            else:
                return [p0]
    return [b]

def uncolon(b):
    return [b[0][:-1]] + b[1:]

def blocks(pgm):
    r = {}
    labels = [b[0] for b in pgm]
    for (label,b,succ) in zip(labels, pgm, labels[1:] + [None]):
        print 'x', label, b, succ
        body = b[1:]
        if body:
            last = body[-1].split()
        else:
            last = (None, None)
        if last[0] == 'br':
            s = ('br', last[1], )
            bb = body[:-1]
        elif last[0] == 'bne':
            (cmp, args) = body[-2].split()
            aa = args.split(",")
            bb = body[:-2]
            if cmp == 'cmp':
                s = ('ifeq', aa, succ, last[1])
            elif cmp == 'dec':
                s = ('deceq', aa, last[1], succ)
            elif cmp == 'tst':
                s = ('tst', aa, last[1], succ)
            else:
                assert 0, "Unknown condition %r %r" % (body[-2], body[-1])
        elif last[0] == 'beq':
            (cmp, args) = body[-2].split()
            aa = args.split(",")
            bb = body[:-2]
            if cmp == 'cmp':
                s = ('ifeq', aa, last[1], succ)
            elif cmp == 'dec':
                s = ('deceq', aa, succ, last[1])
            elif cmp == 'tst':
                s = ('tst', aa, succ, last[1])
            else:
                assert 0, "Unknown condition %r %r" % (body[-2], body[-1])
        elif last[0] == 'jsr':
            s = ('jsr', succ, last[2])
            bb = body[:-1]
        elif last[0] == 'rts':
            s = ('rts',)
            bb = body[:-1]
        elif last[0] == 'bgt':
            (cmp, args) = body[-2].split()
            aa = args.split(",")
            bb = body[:-2]
            if cmp == 'cmp':
                s = ('iflt', aa, last[1], succ)
            else:
                assert 0
        else:
            s = ('br', succ)
            bb = body
        r[label] = BB(bb, s, body)
    return r

def encode(symb2freq):
    """Huffman encode the given dict mapping symbols to weights"""
    heap = [[wt, [sym, ""]] for sym, wt in symb2freq.items()]
    heapify(heap)
    while len(heap) > 1:
        lo = heappop(heap)
        hi = heappop(heap)
        for pair in lo[1:]:
            pair[1] = '0' + pair[1]
        for pair in hi[1:]:
            pair[1] = '1' + pair[1]
        heappush(heap, [lo[0] + hi[0]] + lo[1:] + hi[1:])
    return sorted(heappop(heap)[1:], key=lambda p: (len(p[-1]), p))

if __name__ == '__main__':
    pgm = psplit(open(sys.argv[1]))
    pgm = sum([brbreak(b) for b in pgm], [])
    pgm = [uncolon(b) for b in pgm]
    pgm = blocks(pgm)
    labels = set(pgm.keys()) - set(['_Main'])
    print labels
    blocknums = dict([(b,i) for (i,b) in enumerate(['_Main'] + sorted(labels))])
    print blocknums
    print pgm
    print '---'

    for l,n in pgm.items():
        if n.succ[0] == 'br':
            s = pgm[n.succ[1]]
            n.source = copy.copy(n.source + s.source)
            n.code += s.code
            n.succ = s.succ
    # sys.exit(1)

    ram = array.array('H', 8192 * [0])
    def loadblk(dst, prg):
        prg_s = []
        for p in prg:
            prg_s.append((p >> 2) & 65535)
            prg_s.append(p & 3)
        d = [len(prg) - 1] + prg_s
        for i,d in enumerate(d):
            ram[256 * dst + i] = d

    g = GA144()
    n = g.node['108']

    symb2freq = defaultdict(int)
    for bname,b in pgm.items():
        bn = blocknums[bname]
        gg = open("g%d" % bn, "w")
        comment = ["BLOCK %d: converted from %s" % (bn, bname)]
        comment += b.source
        for c in comment:
            gg.write(r"\ " + c + "\n")
        gg.write('\n')
        gg.write(b.convert(bname, blocknums))
        gg.close()

        ga = "g%d" % bn
        n.listing = []
        n.load(open(ga).read())
        # Now n.prefix is the prefix, n.load_pgm is the RAM contents
        print bname, b
        assert len(n.load_pgm) <= 56, "Takes %d" % len(n.load_pgm)
        # Construct a bootstream
        print >> open("%s.lst" % ga, "w"), "\n".join(n.listing)
        r = [n.assemble("dup or dup".split()),
             n.assemble("push a! @p".split()),
             len(n.load_pgm) - 1,
             n.assemble(["push"]),
             n.assemble("@p !+ unext ;".split())] + n.load_pgm + n.prefix[:-1] # trim off "jump 0"
        print ga, 'RAM', len(n.load_pgm), 'bootstream', len(r)
        loadblk(bn, r)
        for ch in r:
            # print '%05x %03x' % (0x3ffff & ch, 0xff & ch)
            # if ch in range(070, 100): ch -= 070
            symb2freq[ch] += 1
    open("ram", "w").write(ram.tostring())
    if 0:
        huff = encode(symb2freq)
        print "Symbol\tWeight\tHuffman Code"
        b = 0
        s = 0
        for symbol,code in huff:
            print "%s\t%s\t%s" % (symbol, symb2freq[symbol], code)
            s += symb2freq[symbol]
            b += symb2freq[symbol] * len(code)
        print s, "symbols."
        print "compressed from", 18 * s, "to", b, "bits", b / 16., "words"
        top63 = [s for _,s in sorted([(-f,s) for (s,f) in symb2freq.items()])][:63]
        n = sum(symb2freq.values())
        ntop63 = sum(symb2freq[s] for s in top63)
        nbits = ntop63 * 6 + (n - ntop63) * 24
        print 'Simple scheme,', nbits, nbits / 16, 'bytes=%d' % (nbits / 8)
        for s in set(symb2freq) - set(top63):
            print s,symb2freq[s]
