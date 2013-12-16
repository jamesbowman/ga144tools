import sys
from ga144 import GA144
import array

class Memloader(GA144):
    def __init__(self, ramcontents):
        GA144.__init__(self)
        # self.poststream = ramcontents
        ds = array.array('H', open(sys.argv[2]).read()).tolist()
        self.poststream = [0x0ae, self.node['708'].symbols['SOUTH'], len(ds)] + ds

        self.loadprogram("memload.ga")
        self.download(sys.argv[1], 460800, listen = False)

if __name__ == '__main__':
    g = Memloader([947])
