import sys
import array
from ga144 import GA144
import draw

def renderall():
    import cairo
    surface = cairo.SVGSurface(open("out.svg", "w"), 72 * 18, 72 * 10)
    ctx = cairo.Context(surface)

    ctx.select_font_face("monospace")
    ctx.set_font_size(20)

    ctx.set_source_rgb(.5, .5, .5)
    ctx.paint()

    g.render(ctx, cairo)

    surface.finish()
    lines = list(open("out.svg"))
    
    part1 = ['<script xlink:href="SVGPan.js"/>\n',
             '<g id="viewport">\n']
    part2 = ["</g>\n"]

    lines = lines[:2] + part1 + lines[2:-1] + part2 + lines[-1:]
    open("out2.svg", "w").write("".join(lines))

if __name__ == '__main__':
    g = GA144()
    g.loadprogram("plumbing.ga")

    g.paint((.1, .0, 0))
    g.loadprogram("vm.ga")

    # Find the symbols in the core that are useful, pre-load them
    # into the fragment nodes
    for ucnode in ('407', '506', '607'):
        for p,v in g.node['508'].symbols.items():
            if p not in g.node[ucnode].symbols:
                g.node[ucnode].symbols[p] = v

    g.paint((.0, .1, 0))
    g.loadprogram("fragments.ga")

    # Load the program into node 509
    pn = g.node['509']
    pn.prefix = [pn.assemble(["jump", "WEST"])]
    binary = open(sys.argv[2]).read()
    assert len(binary) <= 120, "binary is too big (%d)" % len(binary)
    pn.load_pgm = array.array('H', binary).tolist()
    pn.listing = ["%05x" % x for x in pn.load_pgm]
    pn.bgcolor = (.1, .1, 0)

    # v = draw.Viz(g.active())
    # v.render("pictures/%s.png" % sys.argv[2])
    g.download(sys.argv[1], 460800)
    # renderall()
