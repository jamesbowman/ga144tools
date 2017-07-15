import sys
from ga144 import GA144
import array
import struct
import itertools

class FlashReader(GA144):
    def __init__(self, port, dumpfile, length):
        du = open(dumpfile, "wb")
        length = int(length, 0)
        print 'length', length
        GA144.__init__(self)
        self.loadprogram("flash.ga")
        ser = self.download(port, 460800, listen = False)

        s = None
        while s != chr(0xa5):
            s = ser.read(1)
        print 'synced'
        d = s + ser.read(4 * (length/2 + 1))
        d = "".join([c for i,c in enumerate(d) if i%4 in (1,2)])

        print "Manufacturer: %02x" % ord(d[0])
        print "Device ID:    %02x" % ord(d[1])

        du.write(d[2:])

class FlashWriter(GA144):
    def __init__(self, port, flashfile):
        GA144.__init__(self)
        self.loadprogram("flashwrite.ga")
        print "\n".join(self.node['705'].listing)
        print self.node['704'].prefix
        print self.node['704'].load_pgm
        self.node['704'].load_pgm[5] = 0xdead
        ser = self.download(port, 460800, listen = True)
        # s = unpack(ser)
        # print "recv %02x %02x" % (next(s), next(s))

if __name__ == '__main__':
    port = sys.argv[1]
    op = sys.argv[2]
    if op == 'read':
        FlashReader(port, *sys.argv[3:])
    elif op == 'write':
        FlashWriter(port, *sys.argv[3:])
    else:
        print "unknown operation '%s'" % op
        sys.exit(1)
