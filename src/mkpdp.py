import array
import sys
from ga144 import GA144
import draw

if __name__ == '__main__':
    g = GA144()
    g.loadprogram("pdp.ga")

    # Find the symbols in the core that are useful, pre-load them
    # into the fragment nodes
    for ucnode in ('407', '506', '607'):
        for p,v in g.node['508'].symbols.items():
            if p not in g.node[ucnode].symbols:
                g.node[ucnode].symbols[p] = v

    g.loadprogram("pdpfrag.ga")

    pn = g.node['509']
    pn.prefix = [pn.assemble(["jump", "WEST"])]
    pn.load_pgm = array.array('H', open("binary").read()).tolist()

    # v = draw.Viz(g.active())
    # v.render("pictures/%s.png" % sys.argv[2])
    g.download(sys.argv[1], 460800)
