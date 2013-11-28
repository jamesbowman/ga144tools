mnemonics = {
    0x00  : ";",
    0x01  : "ex",
    0x02  : "jump",
    0x03  : "call",
    0x04  : "unext",
    0x05  : "next",
    0x06  : "if",
    0x07  : "-if",
    0x08  : "@p",
    0x09  : "@+",
    0x0a  : "@b",
    0x0b  : "@",
    0x0c  : "!p",
    0x0d  : "!+",
    0x0e  : "!b",
    0x0f  : "!",
    0x10  : "+*",
    0x11  : "2*",
    0x12  : "2/",
    0x13  : "-",
    0x14  : "+",
    0x15  : "and",
    0x16  : "or",
    0x17  : "drop",
    0x18  : "dup",
    0x19  : "pop",
    0x1a  : "over",
    0x1b  : "a",
    0x1c  : ".",
    0x1d  : "push",
    0x1e  : "b!",
    0x1f  : "a!"
}
opcodes = dict([(name, op) for (op, name) in mnemonics.items()])

class Node():
    def toslot(self, code, slot):
        if slot in (2, 0):
            code ^= 0x15
        else:
            code ^= 0x0a
        if slot == 3:
            return code << 13
        elif slot == 2:
            return code << 8
        elif slot == 1:
            return code << 3
        else:
            return code >> 2

    def term(self, n):
        return int(n, 0)

    def assemble(self, sops):
        if len(sops) == 1 and sops[0] not in opcodes:
            return self.term(sops[0])
        mask = 0
        for slot,mnem in zip((3, 2, 1, 0), sops):
            uop = opcodes[mnem]
            mask |= self.toslot(uop, slot)
            if mnem in ("jump", "call"):
                mask |= self.term(sops[-1])
                break
        return mask

        uops = [opcodes[s] for s in sops]
        placed = sum([(u << (5 * (3 - i))) for (i, u) in enumerate(uops)])
        assert (placed & 3) == 0, "Illegal opcode for slot 3"
        return 0x15555 ^ (placed >> 2)

    def dis(self, opcode):
        assert (0 <= opcode <= 0x3ffff)
        op20 = (opcode ^ 0x15555) << 2
        uops = [(0x1f & (op20 >> i)) for i in (15, 10, 5, 0)]
        mnem = [mnemonics[u] for u in uops]
        if mnem[0] in ("call", "jump"):
            mnem[1:] = ["0x%03x" % (opcode & 0x1ff)]
        return mnem

    def load(self, prg):
        lines = [l for l in prg.split("\n") if l]
        ops = []
        for l in lines:
            opcode = self.assemble(l.split())
            ops.append(opcode)
            print '%05x     %s' % (opcode, l) # , self.dis(opcode)
        return ops

def async(bs):
    r = []
    for n in bs:
        r += [((n << 6) & 0xc0) | 0x2d,
              ((n >> 2) & 0xff),
              ((n >> 10) & 0xff)]
    return "".join([chr(c ^ 0xff) for c in r])

def bootstream(nn):
    return [0, 0, len(nn)] + nn
    
prg = """
    ; ; ; ;
    @b and @b +*
    + ! ;
    @b and !+ +
    @p a! @ .
    2* ! - ;
    @b and ! @p
    @p a! @ dup
    + and @b unext
    over and !b unext
    - 2* unext unext
    . . . @p
    ! ; ; ;
    @p a! . .
    @p ! . .
    @p ! . .
    jump 0
"""

prg = """
    @p a! . .
    0x15d
    @p ! . .
    2
    @p ! . .
    3
    jump 2
"""

n = Node()
c = n.load(prg)
print " ".join(["%05x" % x for x in c])
bs = bootstream(c)
print " ".join(["%05x" % x for x in bs])
print repr(async(bs))
print n.dis(0x134a9)
for i in range(8):
    code = 0x20000 | (i << 13)
    print '%05x' % code, n.dis(code)[0]
