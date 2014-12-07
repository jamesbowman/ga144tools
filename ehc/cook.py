import re
import array
from ga144 import GA144

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

def convert(filename):
    cb = CodeBuf()
    cb.lit('SOUTH')
    cb.op('b!')
    cb.label('start')
    for l in open(filename):
        ii = re.findall(r"[$\w']+", l)
        if ii[0] == 'clr':
            cb.ops('dup or')
            cb.ra(ii[1])
            cb.op('!')
        elif ii[0] == 'mov':
            (src, dst) = ii[1:]
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
        elif ii[0] == 'bne':
            (a, b, yes, no) = ii[1:]
            cb.lit(2)
            cb.op('!b')
            cb.src(a)
            cb.src(b)
            cb.op('or')
            cb.jz('L1')
            cb.lit(yes)
            cb.jump('L2')
            cb.label('L1')
            cb.lit(no)
            cb.label('L2')
            cb.op('!b')
            cb.finish()
        elif ii[0] == 'emit':
            cb.src(ii[1])
            cb.lit('NORTH')
            cb.ops('a! !')
        elif ii[0] == 'jmp':
            cb.lit(2)
            cb.op('!b')
            cb.lit(ii[1])
            cb.op('!b')
            cb.finish()
    cb.flush()
    return "".join(s + "\n" for s in cb.cc)

if __name__ == '__main__':
    ram = array.array('H', 1024 * [0])
    def loadblk(dst, prg):
        prg_s = []
        for p in prg:
            prg_s.append(p >> 9)
            prg_s.append(p & 511)
        d = [len(prg) - 1] + prg_s
        for i,d in enumerate(d):
            ram[256 * dst + i] = d

    g = GA144()
    n = g.node['108']

    for i in range(3):
        ga = "b%02d.ga" % i
        open(ga, "w").write(convert("b%02d" % i))
        n.load(open("b%02d.ga" % i).read())
        # print n.load_pgm
        # print n.prefix
        r = [n.assemble("dup or dup".split()),
             n.assemble("push a! @p".split()),
             len(n.load_pgm) - 1,
             n.assemble(["push"]),
             n.assemble("@p !+ unext".split())] + n.load_pgm + n.prefix
        print len(r), len(n.load_pgm)
        loadblk(i, r)
    open("ram", "w").write(ram.tostring())
