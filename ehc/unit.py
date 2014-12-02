import sys
import time
import struct
import serial
from ga144 import GA144

def trivial(load, send, recv):
    load("trivial.ga")

    for i in range(4):
        send('NORTH', 100)
        assert 100 == recv('EAST')
        send('EAST', 200)
        assert 200 == recv('SOUTH')
        send('SOUTH', 300)
        assert 300 == recv('WEST')
        send('WEST', 400)
        assert 400 == recv('NORTH')

def packer(load, send, recv):
    load("packer.ga")
    for x in (0, 511, 512, 513, 0x3ffff, 0x35555):
        send("EAST", x >> 9)
        send("EAST", x & 511)
        print hex(recv("WEST"))

def dryrun(load, send, recv):
    load("b00.ga")
    print hex(recv("EAST"))
    print hex(recv("EAST"))
    print hex(recv("EAST"))

if __name__ == '__main__':
    # v = draw.Viz(g.active())
    # v.render("pictures/%s.png" % sys.argv[2])

    ser = serial.Serial(sys.argv[1], 460800)

    g = GA144()
    def load(sourcefile):
        ser.setRTS(0)   # Reboot by dropping RTS
        ser.setRTS(1)
        g.__init__()
        g.log = lambda a,b:None
        g.loadprogram('fixture.ga')
        g.node['508'].load(open(sourcefile).read())
        ser.write(g.async())
        ser.flush()
        # print "\n".join(g.node['608'].listing)

    def xfer(addr, din):
        # print hex(din), addr
        ser.write(g.sget([din, addr]))
        s = ser.read(4)
        (v, ) = struct.unpack("<I", s)
        assert (v & 0xff) == 0xa5
        return (v >> 8) & 0x3ffff
    dirs = {
        "OTHER" : 999,
        "NORTH" : 608,
        "EAST"  : 509,
        "SOUTH" : 408,
        "WEST"  : 507}
    def send(node, din):
        xfer(0x20000 | dirs[node], din)
    def recv(node):
        return xfer(dirs[node], 0)

    t0 = time.time()

    tests = [
        trivial,
        packer,
        # dryrun,
    ]
    for t in tests:
        t(load, send, recv)
        print t.__name__
        print "\n".join(g.node['508'].listing)
