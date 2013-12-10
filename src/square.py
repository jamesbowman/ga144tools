import sys
from ga144 import GA144

# Output a square wave on node 708's pin 1.
# The frequency is about 20 MHz.

prg708 = """
    @p a!
        io
: again
    @p
        2
    !
    @p
        3
    !
    jump again
"""

if __name__ == '__main__':
    g = GA144()
    g.node['708'].load(prg708)
    g.download(sys.argv[1])
