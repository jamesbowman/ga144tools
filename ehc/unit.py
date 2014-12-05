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
        assert recv("WEST") == x

def dryrun(load, send, recv):
    # load("b01.ga", verbose = 1)
    b = 0
    while True:
        load("b%02d.ga" % b)
        if b == 2:
            print recv('NORTH')
            break
        b = recv("WEST")
        print 'next', b
        # for i in range(8): print 'r%d  ' % i, (recv("WEST"))

if __name__ == '__main__':
    # v = draw.Viz(g.active())
    # v.render("pictures/%s.png" % sys.argv[2])

    ser = serial.Serial(sys.argv[1], 460800)

    g = GA144()
    def load1(sourcefile, verbose = 0):
        ser.setRTS(0)   # Reboot by dropping RTS
        ser.setRTS(1)
        g.__init__()
        g.log = lambda a,b:None
        g.loadprogram('fixture.ga')
        g.node['508'].load(open(sourcefile).read())
        if verbose:
            print "\n".join(g.node['508'].listing)
            print
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

    node1tests = [
        trivial,
        packer,
        # dryrun,
    ]
    for t in node1tests:
        print t.__name__
        t(load1, send, recv)

    g.loadprogram('ram.ga')
    ser.setRTS(0)   # Reboot by dropping RTS
    ser.setRTS(1)
    g.download(sys.argv[1], 460800, listen = False)
    send("OTHER", ~101)
    print recv("OTHER")
