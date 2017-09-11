import sys
import time
import struct
from subprocess import Popen, PIPE

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

class Illegal(Exception):
    pass

def portunion(pa, pb):
    return "".join([chr(max(ord(a), ord(b))) for (a,b) in zip(pa, pb)])

class Node():
    labels = {
        'io'   : 0x15d,
        'data' : 0x141,
        '---u' : 0x145,
        '--l-' : 0x175,
        '--lu' : 0x165,
        '-d--' : 0x115,
        '-d-u' : 0x105,
        '-dl-' : 0x135,
        '-dlu' : 0x125,
        'r---' : 0x1d5,
        'r--u' : 0x1c5,
        'r-l-' : 0x1f5,
        'r-lu' : 0x1e5,
        'rd--' : 0x195,
        'rd-u' : 0x185,
        'rdl-' : 0x1b5,
        'rdlu' : 0x1a5,
        #ROM
        'warm'     : 0xA9,
        'relay'    : 0xA1,
        '*.17'     : 0xB0,
        '*.'       : 0xB7,
        'triangle' : 0xCE,
        'clc'      : 0x2D3,
        '--u/mod'  : 0x2D5,
        '-u/mod'   : 0x2D6,
        'interp'   : 0xC4,
        'taps'     : 0xBC,
        'poly'     : 0xAA,
        'lsh'      : 0xD9,
        'rsh'      : 0xDB,
        '-dac'     : 0xBC,
        'boot'     : 0xAE,
    }

    def __init__(self, name):
        self.name = name
        self.symbols = {}
        self.symbols['lsh'] = 0xd9
        self.symbols['rsh'] = 0xdb
        self.symbols.update(self.labels)
        self.attr = {}
        self.listing = []
        row = int(name[0])
        col = int(name[1:3])
        if (row & 1) == 1:
            n = '---u'
            s = '-d--'
        else:
            n = '-d--'
            s = '---u'
        if (col & 1) == 0:
            w = '--l-'
            e = 'r---'
        else:
            w = 'r---'
            e = '--l-'

        for _n in (0,1):
            for _e in (0,1):
                for _s in (0,1):
                    for _w in (0,1):
                        port = '----'
                        name = []
                        if _n:
                            name.append('NORTH')
                            port = portunion(port, n)
                        if _e:
                            name.append('EAST')
                            port = portunion(port, e)
                        if _s:
                            name.append('SOUTH')
                            port = portunion(port, s)
                        if _w:
                            name.append('WEST')
                            port = portunion(port, w)
                        name = "_".join(name)
                        if port != '----':
                            self.symbols[name] = self.symbols[port]
        self.setpass(1)

    def toslot(self, code, slot):
        if (slot == 0) and (code & 3) != 0:
            raise Illegal, "Illegal opcode '%s' for slot 0" % mnemonics[code]
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

    def setpass(self, p):
        self.term = [self.pass0_term, self.pass1_term][p]
        self.lst = [lambda m: m, self.log][p]
        self.bad_dest = [self.bad_dest_0, self.bad_dest_1][p]

    def log(self, msg):
        # print msg
        self.listing.append(msg)

    def pass0_term(self, n):
        return 0

    def pass1_term(self, n):
        if n in self.symbols:
            return self.symbols[n]
        if '.' in n:
            # handle a symbol in another node e.g. "605.emit"
            (n, sym) = n.split('.')
            return self.chip.node[n].symbols[sym]
        else:
            return eval(n, self.symbols)

    def bad_dest_0(self, pc, dest, dm):
        return False
    def bad_dest_1(self, pc, dest, dm):
        return (dest & ~dm) != (pc & ~dm)

    def is_literal(self, sops):
        return len(sops) == 1 and sops[0] not in opcodes

    def assemble(self, sops, pc = None):
        if self.is_literal(sops):
            return self.term(sops[0])
        mask = 0
        for slot,mnem in zip((3, 2, 1, 0), sops + [".", ".", "."]) :
            uop = opcodes[mnem]
            mask |= self.toslot(uop, slot)
            if mnem in ("jump", "call", "next", "if", "-if"):
                if not slot in (3, 2, 1):
                    raise Illegal, "Illegal jump for slot %d" % slot
                dm = { 3: 0x3ff, 2: 0xff, 1: 0x7 }[slot]
                if pc is None and (dm == 0x7):
                    raise Illegal, "illegal jump to %#x for port execution" % (dest)
                dest = self.term(sops[-1])
                if pc is not None and self.bad_dest(pc, dest, dm):
                    raise Illegal, "jump to %#x out of range for slot %d" % (dest, slot)
                mask |= (dm & dest)
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

    load_pgm = None

    def isactive(self):
        return self.load_pgm is not None

    def load(self, prg, fragment=False):
        self.log('---------- ' + self.name + ' ----------')
        lines = [l for l in prg.split("\n") if l]
        last_prefix_word = []
        for p in (0, 1):
            self.setpass(p)
            prefix = []     # the prefix part of the node's program
            ops = []        # the loaded part of the node's program
            target = prefix
            BACKSLASH = "\\"
            for lineno, ol in enumerate(lines, 1):
                if p == 0 and BACKSLASH + ' attr:' in ol:
                    v = ol.split()
                    self.attr[v[2]] = v[3:]
                if BACKSLASH in ol:
                    l = ol[:ol.index(BACKSLASH)]
                else:
                    l = ol
                s = l.split()
                if s:
                    if s[0] == ":":
                        self.symbols[s[1]] = len(ops)
                        self.lst('%02x:           %s' % (len(ops), ol))
                        target = ops
                    else:
                        try:
                            opcode = self.assemble(s, pc = len(ops))
                        except Illegal, msg:
                            print l
                            print msg
                            sys.exit(1)
                        self.lst('%02x: %05x     %s' % (len(ops), opcode & 0x3ffff, ol))
                        if prefix is target:
                            last_prefix_word = s
                        target.append(opcode)
                else:
                    self.lst('%02x:           %s' % (len(ops), ol))
        if not fragment and 'jump' in last_prefix_word:
            self.prefix = prefix
        else:
            self.prefix = prefix + [self.assemble("jump 0".split())]
        self.load_pgm = ops
        self.bgcolor = (0, 0, .1)

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
        if not self.load_pgm:
            r += [self.assemble(";".split())]
        else:
            r += [self.assemble("@p a! @p".split()),
                  0,
                  len(self.load_pgm) - 1,
                  self.assemble(["push"]),
                  self.assemble("@p !+ unext".split())] + self.load_pgm
            r += self.prefix
        return r

    # These methods are all for rendering the node using Cairo

    def xy(self, r, c):
        return (60 + c * 65, 600 - r * 80)

    def rect(self, ctx, x, y, w, h):
        ctx.move_to(x, y)
        ctx.line_to(x + w, y)
        ctx.line_to(x + w, y + h)
        ctx.line_to(x, y + h)
        ctx.close_path()

    def center(self, r, c):
        return (60 + c * 65 + (55.0 / 2), 600 - r * 80 + (70.0 / 2))

    bgcolor = (0, 0, 0)
    def render(self, ctx, cairo):
        r = int(self.name[0])
        c = int(self.name[1:])

        (x, y) = self.xy(r, c)

        (w, h) = (55, 70)

        ctx.set_source_rgb(*self.bgcolor)
        self.rect(ctx, x, y, w, h)
        ctx.fill()

        ctx.save()
        ctx.set_line_width(4)
        ctx.set_line_join(cairo.LINE_JOIN_ROUND)
        self.rect(ctx, x, y, w, h)
        ctx.stroke()
        ctx.set_source_rgba(1, 1, 1, 0.1)
        self.rect(ctx, x, y, w, h)
        ctx.stroke()

        (_, _, tw, th, _, _) = ctx.text_extents(self.name)
        ctx.set_source_rgba(1, 1, 1, 0.4)
        ctx.move_to(x + ((w - tw) / 2), y + th)
        ctx.show_text(self.name)

        if 1:
            ctx.set_source_rgba(1, 1, 1, 1)
            ctx.set_font_size(0.3)
            for i,l in enumerate(self.listing[1:]):
                ctx.move_to(x + 4, y + th + 0.5 * i)
                ctx.show_text(l)

        ctx.restore()

class GA144:
    def __init__(self):
        self.node = {}
        for r in range(8):
            for c in range(18):
                id = "%d%02d" % (r, c)
                self.node[id] = Node(id)

        for r in range(7):
            for c in range(18):
                id = "%d%02d" % (r, c)
                self.node[id].n = self.node["%d%02d" % (r + 1, c)]
        for r in range(1,8):
            for c in range(18):
                id = "%d%02d" % (r, c)
                self.node[id].s = self.node["%d%02d" % (r - 1, c)]
        for r in range(0,8):
            for c in range(17):
                id = "%d%02d" % (r, c)
                self.node[id].e = self.node["%d%02d" % (r, c + 1)]
        for r in range(0,8):
            for c in range(1,18):
                id = "%d%02d" % (r, c)
                self.node[id].w = self.node["%d%02d" % (r, c - 1)]

        for n in self.node.values():
            n.chip = self

    def bootstream(self):
        r = []
        # path = ['SOUTH', 'SOUTH', 'SOUTH', 'SOUTH', 'SOUTH', 'SOUTH', 'SOUTH', 'WEST']
        # path = ['SOUTH', 'SOUTH', 'EAST', 'SOUTH', 'WEST', 'SOUTH', 'SOUTH', 'SOUTH', 'SOUTH', 'WEST']
        s6w = ['SOUTH'] * 6 + ['WEST']
        n6w = ['NORTH'] * 6 + ['WEST']
        path = (['EAST'] * 9 + ['SOUTH'] + (s6w + n6w) * 8 +
            s6w + ['NORTH'] * 7 + ['EAST'] * 7
        )
        ds = [self.node['708'].assemble("call EAST".split())] + self.node['709'].pump(path[1:])
        r += [0x0ae, self.node['708'].symbols['EAST'], len(ds)] + ds

        n708 = self.node['708'].load_pgm
        r += [0x000, 0, len(n708)] + n708
        # print 'path', len(path)
        r += self.poststream
        # print 'bootstream is', len(r), 'words'
        return r

    poststream = []

    def announce(self, msg):
        print ("  " + msg + "  ").center(40, "-")

    def sget(self, bs):
        """ bs is a list of 18-bit numbers. Return it formatted for async
        node 708's "sget" function """

        r = []
        for n in bs:
            r += [((n << 6) & 0xc0) | 0x2d,
                  ((n >> 2) & 0xff),
                  ((n >> 10) & 0xff)]
        return "".join([chr(c ^ 0xff) for c in r])

    def async(self):
        bs = self.bootstream()
        # print " ".join(["%05x" % x for x in bs])
        return self.sget(bs)

    paint_color = (0, 0, .1)
    def paint(self, color):
        self.paint_color = color

    def loadprogram(self, sourcefile):
        self.order = []
        code = {}
        c = []
        p1 = Popen("m4 " + sourcefile, stdout = PIPE, shell=True)
        log = open("log", "w")
        for l in p1.stdout:
        # for l in open(sourcefile):
            log.write(l)
            if l[0] == '-':
                n = l.split()[1]
                c = []
                code[n] = c
                self.order.append(n)
            else:
                c.append(l)
        for n,c in sorted(code.items()):
            self.node[n].load("".join(c))
            self.node[n].bgcolor = self.paint_color

    def active(self):
        return {id:n for (id,n) in self.node.items() if n.isactive()}

    def render(self, ctx, cairo):
        for n in self.node.values():
            n.render(ctx, cairo)

    def send(self, ser):
        ser.setRTS(0)   # Reboot by dropping RTS
        time.sleep(.01)
        ser.setRTS(1)
        # ser.dsrdtr = True
        ser.write(self.async())
        ser.flush()
        
    def download(self, port, speed, listen = True):
        import serial
        ser = serial.Serial(port, speed)
        self.send(ser)
        self.announce("DOWNLOAD COMPLETE")
        if not listen:
            time.sleep(0.1)
        t0 = time.time()
        if not listen:
            return ser
        while listen:
            s = ser.read(4)
            (v, ) = struct.unpack("<I", s)
            if (v & 0xff) == 0xa5:
                v >>= 8
                if 33 <= v < 127:
                    printable = "'%c'" % v
                else:
                    printable = ""
                print "[%.3f]" % (time.time() - t0),
                print "0x%05x  %d   %s" % (v & 0x3ffff, v & 0x3ffff, printable)
                if (v & 0xffff) == 0x1111:
                    t0 = time.time()
                if (v & 0xffff) == 0x2222:
                    # print 'took', time.time() - t0
                    print 'respond'
                    ser.write(self.sget([1]))
                    # ser.flush()
                if v == 0x00947:
                    return
                t0 = time.time()
