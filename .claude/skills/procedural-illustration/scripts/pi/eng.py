"""Engineering diagrams: single-line diagrams (SLD) with power-flow labels and animated flow,
ported from MM-ify's sld.py to SVG and the blog's tokens. Schematics stay abstract: no sag,
no shadows. For a hanging conductor in an elevation, `catenary()` gives the real curve.
See subskills/engineering/SKILL.md.

    sld = SLD(width=12, height=7)          # the drawing in grid units
    @sld.build
    def _(s, lang):                        # s draws in grid units; y grows downwards
        s.bus((0, 1), (12, 1), label='150 kV')
        s.wire([(2, 1), (2, 4)]); s.breaker((2, 2)); t = s.transformer((2, 4.6))
        s.flow((2, 1.2), (2, 3.6))         # animated dashes along a branch
    fig.add(sld)

Conductors first, then symbols (filled with the card colour, so they mask the line under them).
"""
import math

from .figure import Component, tr
from .charts2d import TICK, LABEL


def catenary(a, b, c=30.0, n=40):
    """Points of a hanging cable between a and b (y up), parameter c = H/w (larger = tighter)."""
    (x1, y1), (x2, y2) = a, b
    if abs(x2 - x1) < 1e-9:
        return [a, b]
    xm = (x1 + x2) / 2
    # shift so both ends sit on y = c*cosh((x-x0)/c) + k
    dx = x2 - x1
    x0 = xm - c * math.asinh((y2 - y1) / (2 * c * math.sinh(dx / (2 * c))))
    k = y1 - c * math.cosh((x1 - x0) / c)
    return [(x1 + dx * i / n, c * math.cosh((x1 + dx * i / n - x0) / c) + k) for i in range(n + 1)]


class _S:
    """Grid-unit drawing proxy on a canvas."""

    def __init__(self, c, u, ox, oy, lang):
        self.c, self.u, self.ox, self.oy, self.lang = c, u, ox, oy, lang
        self.sw = 1.8

    def P(self, p):
        return self.ox + p[0] * self.u, self.oy + p[1] * self.u

    def bus(self, a, b, label=None, role='ink'):
        (x1, y1), (x2, y2) = self.P(a), self.P(b)
        self.c.line(x1, y1, x2, y2, stroke=role, sw=4.5)
        if label:
            self.c.text(x1, y1 - 8, tr(label, self.lang), LABEL[self.c.layout], 700, 'ink', 'start', 'bottom')

    def wire(self, pts, role='ink', dashed=False):
        self.c.polyline([self.P(p) for p in pts], stroke=role, sw=self.sw, dash='5 4' if dashed else None,
                        join='miter', cap='butt')

    def flow(self, a, b, role='a'):
        """Moving dashes along a conductor (direction a -> b), stopped for reduced motion."""
        self.c.polyline([self.P(a), self.P(b)], stroke=role, sw=3, cls='pi-flow', cap='butt')

    def node(self, p, r=3.5):
        x, y = self.P(p)
        self.c.circle(x, y, r, fill='ink')

    def breaker(self, p, closed=True, label=None, s=0.42):
        x, y = self.P(p)
        h = s * self.u
        self.c.rect(x - h / 2, y - h / 2, h, h, fill='bg', stroke='ink', sw=self.sw)
        if not closed:
            self.c.line(x - h / 2, y + h / 2, x + h / 2, y - h / 2, stroke='ink', sw=self.sw)
        self._lab(x - h, y, label)

    def disconnector(self, p, closed=True, label=None, s=0.42):
        x, y = self.P(p)
        h = s * self.u * 0.8
        self.c.rect(x - h * 0.5, y - h, h, 2 * h, fill='bg', mark=False)
        self.c.line(x - h * 0.35, y - h, x + h * 0.35, y - h, stroke='ink', sw=self.sw)
        tip = (x, y - h) if closed else (x + h * 0.6, y - h * 0.8)
        self.c.line(x, y + h, tip[0], tip[1], stroke='ink', sw=self.sw)
        self._lab(x - h, y, label)

    def earth(self, p, s=0.42):
        x, y = self.P(p)
        h = s * self.u
        for i, f in enumerate((1.0, 0.65, 0.3)):
            self.c.line(x - h * 0.5 * f, y + i * h * 0.2, x + h * 0.5 * f, y + i * h * 0.2, stroke='ink', sw=self.sw)

    def transformer(self, p, r=0.4, label=None, horizontal=False, side='left'):
        """Two overlapping circles; returns the two terminals in grid units."""
        x, y = self.P(p)
        R = r * self.u
        off = R * 0.6
        cs = [(x - off, y), (x + off, y)] if horizontal else [(x, y - off), (x, y + off)]
        for cx, cy in cs:
            self.c.circle(cx, cy, R, fill='bg')
        for cx, cy in cs:
            self.c.circle(cx, cy, R, fill='none', stroke='ink', sw=self.sw)
        self._lab(x - R * 1.1, y, label, side, R * 2.2)
        if horizontal:
            return (p[0] - (off + R) / self.u, p[1]), (p[0] + (off + R) / self.u, p[1])
        return (p[0], p[1] - (off + R) / self.u), (p[0], p[1] + (off + R) / self.u)

    def generator(self, p, r=0.42, label=None):
        x, y = self.P(p)
        R = r * self.u
        self.c.circle(x, y, R, fill='bg', stroke='ink', sw=self.sw)
        pts = [(x - R * 0.55 + i * R * 1.1 / 30, y - R * 0.28 * math.sin(2 * math.pi * i / 30)) for i in range(31)]
        self.c.polyline(pts, stroke='ink', sw=self.sw)
        self._lab(x - R * 1.1, y, label)
        return (p[0], p[1] - r)

    def load(self, p, label=None, s=0.4):
        x, y = self.P(p)
        h = s * self.u
        self.c.polygon([(x - h * 0.45, y), (x + h * 0.45, y), (x, y + h)], fill='ink')
        self._lab(x - h * 0.6, y + h * 0.5, label)

    def grid_infeed(self, p, label=None, s=0.7, side='left'):
        x, y = self.P(p)
        h = s * self.u
        self.c.rect(x - h / 2, y - h * 0.6, h, h * 0.6, fill='bg', stroke='ink', sw=self.sw)
        for i in range(1, 4):
            self.c.line(x - h / 2 + i * h / 4, y - h * 0.6, x - h / 2 + (i - 1) * h / 4, y, stroke='ink', sw=1)
        self._lab(x - h * 0.6, y - h * 0.3, label, side, h * 1.2)

    def ct(self, p, r=0.16):
        x, y = self.P(p)
        self.c.circle(x, y, r * self.u, fill='none', stroke='ink', sw=self.sw)

    def flow_label(self, p, lines, up=True, role='ink'):
        """Power-flow values with a direction triangle per line: lines = ['75 MW', '23 Mvar']."""
        x, y = self.P(p)
        size = TICK[self.c.layout]
        for i, t in enumerate(lines):
            yy = y + i * size * 1.35
            d = 1 if up else -1
            self.c.polygon([(x, yy - d * 4), (x - 4, yy + d * 3), (x + 4, yy + d * 3)], fill=role)
            self.c.text(x + 8, yy, tr(t, self.lang), size, 500, role if role in ('ink', 'label') else role + '-ink',
                        'start', 'middle', kind='value')

    def text(self, p, s, anchor='start', weight=500, role='label'):
        x, y = self.P(p)
        self.c.text(x, y, tr(s, self.lang), TICK[self.c.layout], weight, role, anchor, 'middle')

    def _lab(self, x, y, label, side='left', reach=0):
        if label:
            if side == 'right':
                self.c.text(x + reach + 4, y, tr(label, self.lang), TICK[self.c.layout], 400, 'label', 'start', 'middle')
            else:
                self.c.text(x - 4, y, tr(label, self.lang), TICK[self.c.layout], 400, 'label', 'end', 'middle')


class SLD(Component):
    """A single-line diagram drawn in grid units and scaled to each layout. `narrow_width` lets a
    wide diagram keep a usable scale on a phone by drawing a different arrangement: give
    `build(s, lang, narrow)` and branch on `narrow`."""

    def __init__(self, width=12, height=6, margin=(70, 24), narrow_size=None):
        self.width, self.height, self.margin = width, height, margin
        self.narrow_size = narrow_size or (width, height)
        self.fn = None

    def build(self, fn):
        self.fn = fn
        return fn

    def draw(self, c, lang, y0):
        gw, gh = (self.narrow_size if c.narrow else (self.width, self.height))
        mx, my = self.margin if not c.narrow else (min(self.margin[0], 44), min(self.margin[1], 20))
        u = (c.W - mx - 10) / gw
        s = _S(c, u, mx, y0 + my, lang)
        try:
            self.fn(s, lang, c.narrow)
        except TypeError:
            self.fn(s, lang)
        return max(c.maxy, y0 + my + gh * u) + 2
