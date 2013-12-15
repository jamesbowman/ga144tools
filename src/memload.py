import sys
from ga144 import GA144

class Memloader(GA144):
    def __init__(self, ramcontents):
        GA144.__init__(self)
        # self.poststream = ramcontents
        ds = range(4000, 4026)
        self.poststream = [0x0ae, self.node['708'].symbols['SOUTH'], len(ds)] + ds

        self.loadprogram("memload.ga")
        self.download(sys.argv[1], 460800, listen = False)

if __name__ == '__main__':
    g = Memloader([947])
