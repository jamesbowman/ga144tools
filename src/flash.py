import time
import sys
import array
import struct

import serial

from ga144 import GA144

class FlashReader(GA144):
    def __init__(self, port, dumpfile, length):
        du = open(dumpfile, "wb")
        length = int(length, 0)
        print 'length', length
        GA144.__init__(self)
        self.loadprogram("flashread.ga")
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
    def __init__(self, port, args):
        GA144.__init__(self)
        writername = "flashwrite.ga"
        if "--winbond" in args:
            writername = "flashwrite-winbond.ga"
            args.remove("--winbond")
        flashfile = args[0]
        self.loadprogram(writername)
        # print "\n".join(self.node['705'].listing)

        im = open(flashfile, "rb")
        offset = 0
        ser = serial.Serial(port, 460800)
        while True:
            sector = im.read(4096)
            if len(sector) == 0:
                break
            print "%4dK " % (offset / 1024),
            payload = [offset / 64] + array.array('H', sector).tolist()
            self.stow(payload)
            self.send(ser)
            ser.read(8)
            print "OK"
            offset += 4096

    def recites(self):
        # Return the recite nodes, in head-to-tail order
        return [n for n in self.order if 'recite' in self.node[n].attr][::-1]

    def stow(self, payload):
        C = 61
        assert (61 * len(self.recites())) >= len(payload)
        for i,n in zip(range(0, len(payload), C), self.recites()):
            self.node[n].load_pgm[3:] = payload[i:i + C]

if __name__ == '__main__':
    port = sys.argv[1]
    op = sys.argv[2]
    if op == 'read':
        FlashReader(port, *sys.argv[3:])
    elif op == 'write':
        FlashWriter(port, sys.argv[3:])
    else:
        print "unknown operation '%s'" % op
        sys.exit(1)
