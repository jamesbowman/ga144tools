import math
import cairo

class Viz:
    def __init__(self, hot = {}):
        self.surface = cairo.ImageSurface(cairo.FORMAT_RGB24, 1280, 720)
        self.ctx = cairo.Context(self.surface)
        self.hot = hot

    def rect(self, x, y, w, h):
        ctx = self.ctx

        ctx.move_to(x, y)
        ctx.line_to(x + w, y)
        ctx.line_to(x + w, y + h)
        ctx.line_to(x, y + h)
        ctx.close_path()

    def xy(self, r, c):
        return (60 + c * 65, 600 - r * 80)

    def center(self, r, c):
        return (60 + c * 65 + (55.0 / 2), 600 - r * 80 + (70.0 / 2))

    def cell(self, r, c, label):
        (x, y) = self.xy(r, c)
        ctx = self.ctx

        (w, h) = (55, 70)

        self.rect(x, y, w, h)
        ctx.fill()

        ctx.save()
        ctx.set_line_width(4)
        ctx.set_line_join(cairo.LINE_JOIN_ROUND)
        self.rect(x, y, w, h)
        ctx.stroke()
        ctx.set_source_rgba(1, 1, 1, 0.1)
        self.rect(x, y, w, h)
        ctx.stroke()

        (_, _, tw, th, _, _) = ctx.text_extents(label)
        ctx.set_source_rgba(1, 1, 1, 0.5)
        ctx.move_to(x + ((w - tw) / 2), y + ((h + th) / 2))
        ctx.show_text(label)
        ctx.restore()

    def render(self, pngfile):
        ctx = self.ctx

        ctx.select_font_face("helvetica")
        ctx.set_font_size(20)

        for r in range(8):
            for c in range(18):
                label = "%d%02d" % (r, c)
                if label in self.hot:
                    ctx.set_source_rgb(0, .3, .1)
                else:
                    ctx.set_source_rgb(0, .0, .1)
                self.cell(r, c, label)

        if 0:
            ctx.set_source_rgb(1, 1, 1)
            ctx.move_to(*self.center(7, 8))
            ctx.line_to(*self.center(7, 9))
            ctx.stroke()
        self.surface.write_to_png(pngfile)

if __name__ == '__main__':
    g = Viz()
    g.render("out.png")
