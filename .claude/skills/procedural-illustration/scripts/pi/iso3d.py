"""3D graphs in isometric projection, drawn flat (no perspective, no gradients, no glow).

Use 3D only when a third dimension carries data (checklist item 6): a value over two
categories (Bars3D), a quantity over a plane (Surface3D), or a volume that should be felt
(Blocks3D: piles of unit cubes). Faces are the role colour; the right face is darkened and the
top lightened with the theme's shade and light tokens, the way MM-ify shades its isometrics.
For an interactive 3D chart, embed a tool chart instead (brotools-embed; Plotly gl3d).
See subskills/charts-3d/SKILL.md.
"""
import math

from . import metrics
from .figure import Component, tr
from .charts2d import make_fmt, TICK, LABEL, VALUE
from .scale import nice_step
from .tokens import ink

C30, S30 = math.cos(math.radians(30)), math.sin(math.radians(30))


def iso(x, y, z, k, ox, oy):
    return ox + (x - y) * C30 * k, oy + (x + y) * S30 * k - z * k


def _face(c, pts, role, overlay=None, stroke='bg', sw=0.8):
    c.polygon(pts, fill=role, stroke=stroke, sw=sw)
    if overlay:
        c.polygon(pts, fill=overlay)


def box(c, x, y, z, dx, dy, dz, role, k, ox, oy, sw=0.8):
    P = lambda a, b, h: iso(a, b, h, k, ox, oy)
    top = [P(x, y, z + dz), P(x + dx, y, z + dz), P(x + dx, y + dy, z + dz), P(x, y + dy, z + dz)]
    left = [P(x, y + dy, z), P(x + dx, y + dy, z), P(x + dx, y + dy, z + dz), P(x, y + dy, z + dz)]
    right = [P(x + dx, y, z), P(x + dx, y + dy, z), P(x + dx, y + dy, z + dz), P(x + dx, y, z + dz)]
    _face(c, left, role, None, sw=sw)
    _face(c, right, role, 'shade', sw=sw)
    _face(c, top, role, 'light', sw=sw)
    xs = [p[0] for p in top + left + right]
    ys = [p[1] for p in top + left + right]
    c.marks.append((min(xs), min(ys), max(xs), max(ys)))
    return top


class Bars3D(Component):
    """A value for each pair of two categories. rows (go back-left), cols (go back-right),
    values[r][c]; roles: a role per row or a {(r, c): role} map (default 'a', one 'hl' allowed).
    Labels: row names along the left base edge, column names along the right base edge, values on
    the bars that matter (`label`: 'all' | 'max' | [(r, c), ...])."""

    def __init__(self, rows, cols, values, roles=None, fmt=None, label='max', unit=None):
        self.rows, self.cols, self.values = rows, cols, values
        self.roles, self.label, self.unit = roles, label, unit
        self.fmt = make_fmt(fmt, [v for r in values for v in r])

    def table(self, lang):
        return [''] + [tr(x, lang) for x in self.cols], [[tr(r, lang)] + [self.fmt(v, lang) for v in row]
                                                          for r, row in zip(self.rows, self.values)]

    def value_labels(self):
        return [self.fmt(v, 'en') for r in self.values for v in r]

    def draw(self, c, lang, y0):
        L = c.layout
        nr, nc = len(self.rows), len(self.cols)
        vmax = max(v for r in self.values for v in r)
        lab_w = max(metrics.width(tr(t, lang), TICK[L]) for t in list(self.rows) + list(self.cols)) + 14
        H = 200 if L == 'w' else 160              # tallest bar, px
        hk_ratio = 1.0                            # bar height per value is set in px, independent of k
        # floor extent with k = 1: x from -nr*C30 to nc*C30, y from 0 to (nr+nc)*S30
        k = min((c.W - 2 * lab_w) / ((nr + nc) * C30), (90 if L == 'w' else 50))
        hk = H / vmax
        ox = lab_w + nr * C30 * k + ((c.W - 2 * lab_w) - (nr + nc) * C30 * k) / 2
        oy = y0 + H + 34
        bw = 0.62
        # back to front: larger x + y is nearer
        cells = sorted(((r, cc) for r in range(nr) for cc in range(nc)), key=lambda t: t[0] + t[1])
        # floor grid
        for r in range(nr + 1):
            c.polyline([iso(0, r, 0, k, ox, oy), iso(nc, r, 0, k, ox, oy)], stroke='grid', sw=1, cap='butt')
        for cc in range(nc + 1):
            c.polyline([iso(cc, 0, 0, k, ox, oy), iso(cc, nr, 0, k, ox, oy)], stroke='grid', sw=1, cap='butt')
        tops = {}
        for r, cc in cells:
            v = self.values[r][cc]
            role = 'a'
            if isinstance(self.roles, dict):
                role = self.roles.get((r, cc), 'a')
            elif self.roles:
                role = self.roles[r]
            dz = v * hk / k
            top = box(c, cc + (1 - bw) / 2, r + (1 - bw) / 2, 0, bw, bw, dz, role, k, ox, oy)
            tops[(r, cc)] = (top, role)
        # labels on the two front edges, outside the floor: rows on the right edge, columns on the left
        for r in range(nr):
            x, y = iso(nc, r + 0.5, 0, k, ox, oy)
            c.text(x + 8, y + 8, tr(self.rows[r], lang), TICK[L], 500, 'label', 'start', 'middle', kind='tick')
        for cc in range(nc):
            x, y = iso(cc + 0.5, nr, 0, k, ox, oy)
            c.text(x - 8, y + 8, tr(self.cols[cc], lang), TICK[L], 400, 'label', 'end', 'middle', kind='tick')
        want = []
        if self.label == 'all':
            want = list(tops)
        elif self.label == 'max':
            want = [max(tops, key=lambda t: self.values[t[0]][t[1]])]
        elif isinstance(self.label, (list, tuple)):
            want = [tuple(t) for t in self.label]
        for t in want:
            top, role = tops[t]
            x = sum(p[0] for p in top) / 4
            y = min(p[1] for p in top)
            c.text(x, y - 5, self.fmt(self.values[t[0]][t[1]], lang), VALUE[L], 700, ink(role), 'middle', 'bottom',
                   halo=True, kind='value')
        if self.unit:
            c.text(0, y0 + 6, tr(self.unit, lang), TICK[L], 400, 'label', 'start', 'middle', kind='axis')
        return c.maxy + 2


class Surface3D(Component):
    """z over an x-y plane: grid[j][i] for x[i], y[j] (or f(x, y) with xs, ys). Cells painted back to
    front in five steps of the sequential ramp, with a key. axes: names of x, y and z."""

    def __init__(self, xs, ys, grid=None, f=None, axes=('x', 'y', 'z'), fmt=None, bins=None):
        self.xs, self.ys = list(xs), list(ys)
        self.grid = grid or [[f(x, y) for x in self.xs] for y in self.ys]
        self.axes = axes
        vals = [v for r in self.grid for v in r]
        self.fmt = make_fmt(fmt, vals)
        lo, hi = min(vals), max(vals)
        self.bins = bins or [lo + (hi - lo) * i / 5 for i in range(1, 5)]
        self.lo, self.hi = lo, hi

    def draw(self, c, lang, y0):
        L = c.layout
        nx, ny = len(self.xs), len(self.ys)
        span = (nx + ny - 2) * C30
        k = min((c.W - 90) / span, (300 if L == 'w' else 200) / ((nx + ny - 2) * S30))
        Hz = 150 if L == 'w' else 110
        hk = Hz / ((self.hi - self.lo) or 1)
        ox = 45 + (ny - 1) * C30 * k + ((c.W - 90) - span * k) / 2
        # lift the floor so the highest point of the surface sits just under y0
        Zp = lambda v: (v - self.lo) * hk
        tops = [(i + j) * S30 * k - Zp(self.grid[j][i]) for j in range(ny) for i in range(nx)]
        oy = y0 + 10 - min(tops + [0])
        Z = lambda v: (v - self.lo) * hk / k
        quads = []
        for j in range(ny - 1):
            for i in range(nx - 1):
                v = (self.grid[j][i] + self.grid[j][i + 1] + self.grid[j + 1][i] + self.grid[j + 1][i + 1]) / 4
                quads.append((i + j, i, j, v))
        for _, i, j, v in sorted(quads):
            pts = [iso(i, j, Z(self.grid[j][i]), k, ox, oy), iso(i + 1, j, Z(self.grid[j][i + 1]), k, ox, oy),
                   iso(i + 1, j + 1, Z(self.grid[j + 1][i + 1]), k, ox, oy), iso(i, j + 1, Z(self.grid[j + 1][i]), k, ox, oy)]
            n = sum(1 for t in self.bins if v >= t)
            c.polygon(pts, fill=f'seq{n + 1}', stroke='bg', sw=0.5)
        # floor outline and axis names
        fl = [iso(0, 0, 0, k, ox, oy), iso(nx - 1, 0, 0, k, ox, oy), iso(nx - 1, ny - 1, 0, k, ox, oy),
              iso(0, ny - 1, 0, k, ox, oy)]
        c.polyline(fl + [fl[0]], stroke='axis', sw=1, dash='3 3', cap='butt')
        x, y = iso(nx - 1, (ny - 1) / 2, 0, k, ox, oy)
        a, b = iso((nx - 1) / 2, ny - 1, 0, k, ox, oy)
        c.text(a - 6, b + 14, tr(self.axes[0], lang), TICK[L], 500, 'label', 'end', 'middle', kind='axis')
        c.text(x + 6, y + 14, tr(self.axes[1], lang), TICK[L], 500, 'label', 'start', 'middle', kind='axis')
        # key
        yk = c.maxy + 14
        w = min(52, (c.W - 120) / 5)
        c.text(0, yk + 5, tr(self.axes[2], lang), TICK[L], 500, 'label', 'start', 'middle', kind='legend')
        x0 = metrics.width(tr(self.axes[2], lang), TICK[L], 500) + 10
        for i in range(5):
            c.rect(x0 + i * w, yk, w - 2, 10, fill=f'seq{i + 1}', mark=False)
        for i, t in enumerate(self.bins):
            c.text(x0 + (i + 1) * w - 1, yk + 16, self.fmt(t, lang), TICK[L], 400, 'label', 'middle', 'top', kind='tick')
        return c.maxy + 2


class Blocks3D(Component):
    """Volumes made of unit cubes, side by side: items [{'label', 'value' (cubes), 'role'}].
    Cubes fill a `base` x `base` layer, then stack. Use to make a large count physical
    (tonnes of rice, years of wages); always write the number too."""

    def __init__(self, items, base=5, fmt=None, unit=None, key=None):
        self.items, self.base, self.unit, self.key = items, base, unit, key
        self.fmt = make_fmt(fmt, [i['value'] for i in items])

    def table(self, lang):
        return ['', ''], [[tr(i['label'], lang), self.fmt(i['value'], lang)] for i in self.items]

    def value_labels(self):
        return [self.fmt(i['value'], 'en') for i in self.items]

    def draw(self, c, lang, y0):
        L = c.layout
        n = len(self.items)
        b = self.base
        layers = [math.ceil(i['value'] / (b * b)) for i in self.items]
        slot = c.W / n
        k = min(slot / (2 * b * C30) * 0.82, 16 if L == 'w' else 11)
        top_h = max(layers) * k
        base_y = y0 + top_h + b * S30 * k * 2 + 34
        if self.key:
            c.text(0, y0 + 6, tr(self.key, lang), TICK[L], 500, 'label', 'start', 'middle', kind='legend')
        for idx, it in enumerate(self.items):
            role = it.get('role', 'a')
            ox = slot * idx + slot / 2
            oy = base_y - b * S30 * k * 2
            v = int(round(it['value']))
            cubes = []
            for m in range(v):
                z = m // (b * b)
                r = m % (b * b)
                cubes.append((r % b, r // b, z))
            for x, y, z in sorted(cubes, key=lambda t: (t[2], t[0] + t[1])):
                box(c, x, y, z, 1, 1, 1, role, k, ox, oy, sw=0.6)
            c.text(ox, base_y + 10, tr(it['label'], lang), LABEL[L], 600 if role == 'hl' else 500,
                   'ink' if role == 'hl' else 'label', 'middle', 'top', max_w=slot - 6)
            topy = oy - math.ceil(v / (b * b)) * k - 8
            c.text(ox, topy - 4, self.fmt(it['value'], lang) + (tr(self.unit, lang) or ''), VALUE[L] + 1, 700,
                   ink(role), 'middle', 'bottom', halo=True, kind='value')
        return c.maxy + 2
