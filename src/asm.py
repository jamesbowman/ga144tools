import sys
from ga144 import GA144

if __name__ == '__main__':
    g = GA144()
    g.loadprogram(sys.argv[2])
    g.download(sys.argv[1], 460800)
