import sys
import re
import array
from ga144 import GA144

# RAM controller command codes
DO_READ = 0     # then addr
DO_WRITE = 1    # then addr, val
DO_BLOCK = 2    # then blocknum

class CodeBuf:
    def __init__(self):
        self.cc = []            # all generated code
        self.insn = []          # current insn
        self.afters = []        # words after the current insn

    def flush(self):
        if self.insn:
            self.cc.append(8*" " + " ".join(self.insn))
            self.cc += self.afters
        self.insn = []
        self.afters = []

    def op(self, o):
        assert o in "; ex jump call unext next if -if @p @+ @b @ !p !+ !b ! +* 2* 2/ - + and or drop dup pop over a . push b! a!".split()

        slot3 = "; unext @p !p +* + dup nop".split()
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

    def jump(self, dst):
        if len(self.insn) > 1:
            self.flush()
        self.insn.append("jump " + dst)
        self.flush()

    def label(self, l):
        self.flush()
        self.cc.append(': ' + l)

    def lit(self, v):
        self.afters.append(12*" " + str(v))
        self.op("@p")

    def ra(self, reg):
        assert reg[0] == 'r'
        self.lit('07' + reg[1])
        self.op('a!')

    def src(self, s):
        if s[0] == '$':
            self.lit(int(s[1:], 0))
        elif s == '(sp)+':
            self.lit(DO_READ)
            self.op('!b')
            self.lit(2)
            self.ra('r6')
            self.ops('@ dup !b . + ! @b')
        elif re.match('06\(sp\)', s):
            self.lit(DO_READ)
            self.op('!b')
            self.lit(6)
            self.ra('r6')
            self.ops('@ . + !b @b')
        else:
            self.ra(s)
            self.op('@')

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

    def convert(self, blocknums):
        cb = CodeBuf()
        cb.label('start')
        for l in self.code:
            ii = re.findall(r"[$\-\+()\w']+", l)
            print ii
            if ii[0] == 'clr':
                cb.ops('dup or')
                cb.ra(ii[1])
                cb.op('!')
            elif ii[0] == 'mov':
                (src, dst) = ii[1:]
                if dst == '-(sp)':
                    cb.src(src)
                    cb.lit(DO_WRITE)
                    cb.op('!b')
                    cb.lit(-2)
                    cb.ra('r6')
                    cb.ops('@ . + dup ! !b !b')
                else:
                    cb.src(src)
                    cb.ra(dst)
                    cb.op('!')
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
            elif ii[0] == 'emit':
                cb.src(ii[1])
                cb.lit('NORTH')
                cb.ops('a! !')
            else:
                assert 0, "Unrecognised %r" % ii

        if self.succ[0] == 'br':
            cb.lit(DO_BLOCK)
            cb.op('!b')
            cb.lit(blocknums[self.succ[1]])
        elif self.succ[0] == 'ifeq':
            (_, (a, b), yes, no) = self.succ
            cb.lit(DO_BLOCK)
            cb.op('!b')
            cb.src(a)
            cb.src(b)
            cb.op('or')
            cb.jz('L1')
            cb.lit(blocknums[yes])
            cb.jump('L2')
            cb.label('L1')
            cb.lit(blocknums[no])
            cb.label('L2')
        elif self.succ[0] == 'deceq':
            (_, (reg,), yes, no) = self.succ
            cb.lit(DO_BLOCK)
            cb.op('!b')
            cb.lit(-1)
            cb.ra(reg)
            cb.ops('@ . + dup !')
            cb.jz('L1')
            cb.lit(blocknums[yes])
            cb.jump('L2')
            cb.label('L1')
            cb.lit(blocknums[no])
            cb.label('L2')
        elif self.succ[0] == 'tst':
            (_, (reg,), yes, no) = self.succ
            cb.lit(DO_BLOCK)
            cb.op('!b')
            cb.ra(reg)
            cb.ops('@')
            cb.jz('L1')
            cb.lit(blocknums[yes])
            cb.jump('L2')
            cb.label('L1')
            cb.lit(blocknums[no])
            cb.label('L2')
        elif self.succ[0] == 'rts':
            cb.lit(DO_BLOCK)
            cb.op('!b')
            cb.src('r0')
            cb.lit('NORTH')
            cb.ops('a! !')
            cb.lit(0)
        else:
            assert 0, 'Bad succ %r' % (self.succ,)
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
        if line.startswith('.'):
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
        if l.split()[0] in ('bne', 'beq'):
            p0 = b[:i+1]
            p1 = b[i+1:]
            if p1:
                global scratch
                scratch += 1
                return [p0, ['X%d:' % scratch] + p1]
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
        last = body[-1].split()
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
        elif last[0] == 'rts':
            s = ('rts',)
            bb = body[:-1]
        else:
            s = ('br', succ)
            bb = body
        r[label] = BB(bb, s, body)
    return r

if __name__ == '__main__':
    pgm = psplit(open("fib.s"))
    pgm = sum([brbreak(b) for b in pgm], [])
    pgm = [uncolon(b) for b in pgm]
    pgm = blocks(pgm)
    labels = set(pgm.keys()) - set(['_Main'])
    print labels
    blocknums = dict([(b,i) for (i,b) in enumerate(['_Main'] + sorted(labels))])
    print blocknums
    print pgm
    print '---'

    ram = array.array('H', 8192 * [0])
    def loadblk(dst, prg):
        prg_s = []
        for p in prg:
            prg_s.append((p >> 9) & 511)
            prg_s.append(p & 511)
        d = [len(prg) - 1] + prg_s
        for i,d in enumerate(d):
            ram[256 * dst + i] = d

    g = GA144()
    n = g.node['108']

    for bname,b in pgm.items():
        bn = blocknums[bname]
        gg = open("g%d" % bn, "w")
        comment = ["BLOCK %d: converted from %s" % (bn, bname)]
        comment += b.source
        for c in comment:
            gg.write(r"\ " + c + "\n")
        gg.write('\n')
        gg.write(b.convert(blocknums))
        gg.close()
        print

        ga = "g%d" % bn
        n.load(open(ga).read())
        # Now n.prefix is the prefix, n.load_pgm is the RAM contents
        assert len(n.load_pgm) <= 56
        # Construct a bootstream
        print >> open("b%02d.lst" % bn, "w"), "\n".join(n.listing)
        r = [n.assemble("dup or dup".split()),
             n.assemble("push a! @p".split()),
             len(n.load_pgm) - 1,
             n.assemble(["push"]),
             n.assemble("@p !+ unext".split())] + n.load_pgm + n.prefix
        print ga, 'RAM', len(n.load_pgm), 'bootstream', len(r)
        loadblk(bn, r)
    open("ram", "w").write(ram.tostring())
