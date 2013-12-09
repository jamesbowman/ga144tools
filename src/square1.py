import sys
from ga144 import GA144

# Output a square wave on node 708's pin 1.
# The frequency is about 20 MHz.

prg708 = """
    @p a! @p @p     \ a points to the io port
        io
        2           \ stack literal 2 and 3
        3
    over over over  \ replicate 2,3 all down the stack
    over over over
    over over
: again
    !  jump again   \ write top-of-stack to io port
"""

if __name__ == '__main__':
    g = GA144()
    g.node['708'].load(prg708)
    g.download(sys.argv[1])
