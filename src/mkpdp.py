import array
import sys
from ga144 import GA144
import draw

if __name__ == '__main__':
    g = GA144()
    g.loadprogram("pdp.ga")

    # Find the symbols in 608 that are useful
    publish = set(g.node['608'].symbols) - set(g.node['607'].symbols)
    # Load them into 607:
    for p,v in g.node['608'].symbols.items():
        if p not in g.node['607'].symbols:
            g.node['607'].symbols[p] = v

    g.loadprogram("pdpfrag.ga")

    pn = g.node['609']
    pn.prefix = [pn.assemble(["jump", "WEST"])]
    pn.load_pgm = array.array('H', open("binary").read()).tolist()

    # v = draw.Viz(g.active())
    # v.render("pictures/%s.png" % sys.argv[2])
    g.download(sys.argv[1], 460800)
