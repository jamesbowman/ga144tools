import sys
from ga144 import GA144
from subprocess import Popen, PIPE

class Memloader(GA144):
    def __init__(self, ramcontents):
        GA144.__init__(self)
        # self.poststream = ramcontents
        ds = range(3000, 3010)
        self.poststream = [0x0ae, self.node['708'].symbols['SOUTH'], len(ds)] + ds

        self.loadprogram("memload.ga")

    def loadprogram(self, sourcefile):
        code = {}
        c = []
        # p1 = Popen(["m4", sourcefile], stdout = PIPE)
        # for l in p1.stdout:
        for l in open(sourcefile):
            if l[0] == '-':
                n = l.split()[1]
                c = []
                code[n] = c
            else:
                c.append(l)
        for n,c in sorted(code.items()):
            self.node[n].load("".join(c))
        self.download(sys.argv[1], 460800, listen = False)
        
if __name__ == '__main__':
    g = Memloader([947])
