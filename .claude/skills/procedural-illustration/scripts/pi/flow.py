"""Flowcharts, processes, cycles and branches, laid out for the wide and the narrow column.

    Flow(nodes=[Node('a', {'en': 'State owns the land'}, col=0, row=0, role='start'), ...],
         edges=[Edge('a', 'b'), Edge('c', 'f', text={...}, dashed=True, role='hl')],
         cycle={'ids': ['b', 'c', 'd', 'e'], 'cx': 0.58, 'r': 118})

Placement, wide layout: a grid (`col`, `row`; fractions allowed) or a cycle (the listed ids go
round a circle clockwise from the top, consecutive cycle edges are drawn as arcs). Narrow
layout: one column in node order; an edge to a later node that is not the next one runs
down the right lane, an edge back up runs up the left lane, so nothing crosses a box.

Node roles: 'node' (default), 'key' (the step the figure is about), 'start' (a filled entry
point), 'hl' / 'warn' (a risk or failure path; warn is dashed), 'muted', 'plain' (no box).
Edges: open 90-degree arrowheads (MM-ify), solid; dashed for a possibility rather than a rule;
`animate=True` moves dashes along the edge (CSS, stopped for reduced motion).
See subskills/flowchart/SKILL.md.
"""
import math

from . import metrics
from .figure import Component, tr
from .charts2d import TICK, LABEL

ROLE = {
    'node': ('node', 'node-line', 'ink', 500, None),
    'key': ('a-soft', 'a', 'ink', 600, None),
    'start': ('a', 'a', 'bg', 600, None),
    'hl': ('hl-soft', 'hl', 'ink', 600, None),
    'warn': ('hl-soft', 'hl', 'ink', 500, '5 4'),
    'muted': ('base-soft', 'base-soft', 'label', 400, None),
    'plain': ('none', None, 'ink', 500, None),
}


class Node:
    def __init__(self, id, text, col=0, row=0, role='node', w=None, sub=None, icon=None, corners='rrrr',
                 near=None, gap=None):
        """near=('b', 'l'): on the wide layout, sit beside node b: 'l', 'r', 't', 'b' or a corner 'tl',
        'tr', 'bl', 'br' (beyond the box diagonally). Use it to hang an entry or a branch on a cycle."""
        self.id, self.text, self.col, self.row, self.role = id, text, col, row, role
        self.near, self.gap = near, gap
        self.w, self.sub, self.icon, self.corners = w, sub, icon, corners
        self.box = None


class Edge:
    def __init__(self, a, b, text=None, dashed=False, role=None, sides=None, animate=False, bend=0):
        self.a, self.b, self.text, self.dashed, self.role = a, b, text, dashed, role
        self.sides, self.animate, self.bend = sides, animate, bend


class Flow(Component):
    def __init__(self, nodes, edges, cycle=None, node_w=None, row_gap=None, centre=None):
        self.nodes, self.edges, self.cycle = nodes, edges, cycle
        self.node_w, self.row_gap, self.centre = node_w, row_gap, centre
        self.by = {n.id: n for n in nodes}

    def table(self, lang):
        return None

    # ── sizes ──────────────────────────────────────────────────────────
    def _measure(self, n, lang, max_w, size):
        weight = ROLE[n.role][3]
        lines = metrics.wrap(tr(n.text, lang), max_w - 24, size, weight)
        w = max(metrics.width(l, size, weight) for l in lines) + 24 + (26 if n.icon else 0)
        h = len(lines) * size * 1.25 + 18
        if n.sub:
            sl = metrics.wrap(tr(n.sub, lang), max_w - 24, size - 1.5)
            w = max(w, max(metrics.width(l, size - 1.5) for l in sl) + 24)
            h += len(sl) * (size - 1.5) * 1.25 + 2
        return lines, min(max(w, 60), max_w), h

    def _draw_node(self, c, n, lang, x, y, w, h, size):
        fill, stroke, txt, weight, dash = ROLE[n.role]
        n.box = (x, y, x + w, y + h)
        if n.role != 'plain':
            from .canvas import shape_path
            c.path(shape_path(x, y, w, h, n.corners, 9), fill=fill, stroke=stroke, sw=1.4, dash=dash,
                   bbox=n.box)
        c.marks.append(n.box)
        tx = x + w / 2
        lines = metrics.wrap(tr(n.text, lang), w - 24 - (26 if n.icon else 0), size, weight)
        sub = metrics.wrap(tr(n.sub, lang), w - 24, size - 1.5) if n.sub else []
        th = len(lines) * size * 1.25 + (len(sub) * (size - 1.5) * 1.25 + 2 if sub else 0)
        ty = y + (h - th) / 2
        if n.icon:
            c.icon(n.icon, x + 12, y + h / 2 - 10, 20, color=stroke or 'label')
            c.marks.pop()
            tx += 13
        b = c.text(tx, ty, '\n'.join(lines), size, weight, txt, 'middle', 'top', lh=1.25)
        if sub:
            c.text(tx, b[3] + 2, '\n'.join(sub), size - 1.5, 400, 'label' if txt == 'ink' else txt, 'middle', 'top',
                   lh=1.25, kind='note')

    # ── layout ─────────────────────────────────────────────────────────
    def draw(self, c, lang, y0):
        return self._narrow(c, lang, y0) if c.narrow else self._wide(c, lang, y0)

    def _wide(self, c, lang, y0):
        size = LABEL['w']
        cyc = self.cycle or {}
        cids = cyc.get('ids', [])
        grid = [n for n in self.nodes if n.id not in cids and not n.near]
        near = [n for n in self.nodes if n.near]
        ncols = max([n.col for n in grid] + [0]) + 1
        cellw = c.W / ncols if grid else c.W
        nw = self.node_w or min(cellw * 0.86, 230)
        meas = {n.id: self._measure(n, lang, n.w or nw, size) for n in self.nodes}
        gap = self.row_gap or 44
        rows = sorted({n.row for n in grid})
        row_y, y = {}, y0
        for r in rows:
            row_y[r] = y
            y += max(meas[n.id][2] for n in grid if n.row == r) + gap
        for n in grid:
            lines, w, h = meas[n.id]
            w = n.w or max(w, min(nw, 150))
            rh = max(meas[m.id][2] for m in grid if m.row == n.row)
            x = (n.col + 0.5) * cellw - w / 2
            x = min(max(x, 0), c.W - w)
            self._draw_node(c, n, lang, x, row_y[n.row] + (rh - h) / 2, w, h, size)
        if cids:
            k = len(cids)
            R = cyc.get('r', 120)
            cx = cyc.get('cx', 0.5) * c.W
            maxh = max(meas[i][2] for i in cids)
            cy = y0 + cyc.get('cy', R + maxh / 2 + 4)
            for i, nid in enumerate(cids):
                ang = math.radians(-90 + i * 360 / k)
                n = self.by[nid]
                lines, w, h = meas[nid]
                w = n.w or w
                px, py = cx + R * math.cos(ang), cy + R * math.sin(ang)
                self._draw_node(c, n, lang, px - w / 2, py - h / 2, w, h, size)
            if self.centre:
                c.text(cx, cy, tr(self.centre, lang), TICK['w'], 600, 'label', 'middle', 'middle',
                       max_w=R * 1.1, kind='note')
        pending = list(near)
        for _ in range(len(pending) + 1):   # a node may hang on another hanging node
            for n in list(pending):
                ref = self.by[n.near[0]]
                if ref.box is None:
                    continue
                lines, w, h = meas[n.id]
                w = n.w or w
                x0, ry0, x1, ry1 = ref.box
                g = n.gap or 40
                side = n.near[1]
                cx, cy = (x0 + x1) / 2, (ry0 + ry1) / 2
                x = {'l': x0 - g - w, 'r': x1 + g, 't': cx - w / 2, 'b': cx - w / 2,
                     'tl': x0 - w * 0.6, 'bl': x0 - w * 0.6, 'tr': x1 - w * 0.4, 'br': x1 - w * 0.4}[side]
                y = {'l': cy - h / 2, 'r': cy - h / 2, 't': ry0 - g - h, 'b': ry1 + g,
                     'tl': ry0 - g - h, 'tr': ry0 - g - h, 'bl': ry1 + g, 'br': ry1 + g}[side]
                x = min(max(x, 0), c.W - w)
                self._draw_node(c, n, lang, x, y, w, h, size)
                pending.remove(n)
        for e in self.edges:
            self._edge_wide(c, e, lang, cids)
        top = min(n.box[1] for n in self.nodes if n.box)
        if top < y0:   # something hung above the first row: move everything down
            dy = y0 - top
            c.els.insert(0, f'<g transform="translate(0 {dy:.1f})">')
            c.els.append('</g>')
            for t in c.texts:
                b = t['box']
                t['box'] = (b[0], b[1] + dy, b[2], b[3] + dy)
            c.marks = [(m[0], m[1] + dy, m[2], m[3] + dy) for m in c.marks]
            c.miny = y0
            c.maxy += dy
        return c.maxy + 2

    def _edge_wide(self, c, e, lang, cids):
        A, B = self.by[e.a], self.by[e.b]
        role = e.role or 'label'
        dash = '5 4' if e.dashed else None
        cls = 'pi-flow' if e.animate else None
        if A.id in cids and B.id in cids and (cids.index(B.id) - cids.index(A.id)) % len(cids) == 1:
            return self._arc(c, e, lang, cids, role, dash, cls)
        ax0, ay0, ax1, ay1 = A.box
        bx0, by0, bx1, by1 = B.box
        acx, acy, bcx, bcy = (ax0 + ax1) / 2, (ay0 + ay1) / 2, (bx0 + bx1) / 2, (by0 + by1) / 2
        g = 3
        if e.sides:
            pts = self._ports(A.box, B.box, e.sides)
        elif by0 >= ay1 - 1 and abs(acx - bcx) < 2:
            pts = [(acx, ay1 + g), (bcx, by0 - g)]
        elif by0 >= ay1 + 8:
            # down: out of the bottom, across in the gap, into the top
            my = (ay1 + by0) / 2
            pts = [(acx, ay1 + g), (acx, my), (bcx, my), (bcx, by0 - g)] if abs(acx - bcx) > 2 else [(acx, ay1 + g), (bcx, by0 - g)]
        elif bx0 >= ax1:
            pts = [(ax1 + g, acy), (bx0 - g, bcy)] if abs(acy - bcy) < 2 else [(ax1 + g, acy), ((ax1 + bx0) / 2, acy), ((ax1 + bx0) / 2, bcy), (bx0 - g, bcy)]
        elif bx1 <= ax0:
            pts = [(ax0 - g, acy), (bx1 + g, bcy)] if abs(acy - bcy) < 2 else [(ax0 - g, acy), ((ax0 + bx1) / 2, acy), ((ax0 + bx1) / 2, bcy), (bx1 + g, bcy)]
        else:
            pts = self._straight(A.box, B.box)
        c.arrow(pts, stroke=role, sw=1.6, dash=dash, cls=cls)
        self._label(c, e, lang, pts, role)

    def _ports(self, a, b, sides):
        def port(box, s):
            x0, y0, x1, y1 = box
            return {'t': ((x0 + x1) / 2, y0 - 3), 'b': ((x0 + x1) / 2, y1 + 3), 'l': (x0 - 3, (y0 + y1) / 2),
                    'r': (x1 + 3, (y0 + y1) / 2)}[s]
        p, q = port(a, sides[0]), port(b, sides[1])
        if sides[0] in 'lr' and sides[1] in 'lr':
            mx = max(p[0], q[0]) + 24 if sides == 'rr' else min(p[0], q[0]) - 24 if sides == 'll' else (p[0] + q[0]) / 2
            return [p, (mx, p[1]), (mx, q[1]), q]
        if sides[0] in 'tb' and sides[1] in 'tb':
            my = (p[1] + q[1]) / 2
            return [p, (p[0], my), (q[0], my), q]
        if sides[0] in 'tb':
            return [p, (p[0], q[1]), q]
        return [p, (q[0], p[1]), q]

    def _straight(self, a, b):
        ac = ((a[0] + a[2]) / 2, (a[1] + a[3]) / 2)
        bc = ((b[0] + b[2]) / 2, (b[1] + b[3]) / 2)

        def clip(box, p, q):  # where segment p->q leaves box (p inside)
            best = 1.0
            for t in [i / 200 for i in range(201)]:
                x, y = p[0] + (q[0] - p[0]) * t, p[1] + (q[1] - p[1]) * t
                if not (box[0] - 4 <= x <= box[2] + 4 and box[1] - 4 <= y <= box[3] + 4):
                    return (x, y)
            return q
        return [clip(a, ac, bc), clip(b, bc, ac)]

    def _arc(self, c, e, lang, cids, role, dash, cls):
        A, B = self.by[e.a], self.by[e.b]
        cyc = self.cycle
        xs = [(self.by[i].box[0] + self.by[i].box[2]) / 2 for i in cids]
        ys = [(self.by[i].box[1] + self.by[i].box[3]) / 2 for i in cids]
        k = len(cids)
        # circle through the node centres (the layout put them on one)
        cx = sum(xs) / k if k > 2 else xs[0]
        cy = sum(ys) / k
        R = cyc.get('r', 120)
        a0 = math.atan2(ys[cids.index(A.id)] - cy, xs[cids.index(A.id)] - cx)
        a1 = math.atan2(ys[cids.index(B.id)] - cy, xs[cids.index(B.id)] - cx)
        if a1 <= a0:
            a1 += 2 * math.pi
        inside = lambda box, x, y: box[0] - 5 <= x <= box[2] + 5 and box[1] - 5 <= y <= box[3] + 5
        s, t = a0, a1
        while s < a1 and inside(A.box, cx + R * math.cos(s), cy + R * math.sin(s)):
            s += 0.01
        while t > s and inside(B.box, cx + R * math.cos(t), cy + R * math.sin(t)):
            t -= 0.01
        n = max(6, int((t - s) * 30))
        pts = [(cx + R * math.cos(s + (t - s) * i / n), cy + R * math.sin(s + (t - s) * i / n)) for i in range(n + 1)]
        c.arrow(pts, stroke=role, sw=1.6, dash=dash, cls=cls)
        self._label(c, e, lang, pts, role)

    def _label(self, c, e, lang, pts, role):
        if not e.text:
            return
        from .charts2d import place
        segs = list(zip(pts, pts[1:]))
        (x1, y1), (x2, y2) = max(segs, key=lambda s: math.dist(*s))
        mx, my = (x1 + x2) / 2, (y1 + y2) / 2
        vertical = abs(x2 - x1) < abs(y2 - y1)
        prefs = ('right', 'left', 'above', 'below') if vertical else ('above', 'below', 'right', 'left')
        place(c, mx, my, tr(e.text, lang), TICK[c.layout], 500, 'hl-ink' if role == 'hl' else 'label', prefs=prefs,
              gap=7, max_w=170 if c.layout == 'w' else 130, kind='note')

    # ── narrow: one column, side lanes for skips and returns ───────────
    def _narrow(self, c, lang, y0):
        size = LABEL['n']
        lane = 22
        x0, w = lane, c.W - 2 * lane
        y = y0
        order = [n.id for n in self.nodes]
        extra = {}
        for e in self.edges:   # room under a box for the label of an edge that skips down the lane
            ia, ib = order.index(e.a), order.index(e.b)
            if e.text and ib > ia + 1:
                lines = metrics.wrap(tr(e.text, lang), w * 0.7, TICK['n'], 500)
                extra[e.a] = extra.get(e.a, 0) + len(lines) * TICK['n'] * 1.25 + 8
        for i, n in enumerate(self.nodes):
            lines, ww, h = self._measure(n, lang, w, size)
            self._draw_node(c, n, lang, x0, y, w, h, size)
            y += h + 30 + extra.get(n.id, 0)
        lanes_l, lanes_r = 0, 0
        for e in self.edges:
            A, B = self.by[e.a], self.by[e.b]
            ia, ib = order.index(e.a), order.index(e.b)
            role = e.role or 'label'
            dash = '5 4' if e.dashed else None
            cls = 'pi-flow' if e.animate else None
            if ib == ia + 1:
                pts = [(c.W / 2, A.box[3] + 3 + extra.get(A.id, 0)), (c.W / 2, B.box[1] - 3)]
                c.arrow(pts, stroke=role, sw=1.6, dash=dash, cls=cls)
                if e.text:
                    from .charts2d import place
                    place(c, c.W / 2, (A.box[3] + B.box[1]) / 2, tr(e.text, lang), TICK['n'], 500,
                          'hl-ink' if role == 'hl' else 'label', prefs=('right', 'left'), gap=8, max_w=w / 2 - 10,
                          kind='note')
            elif ib < ia:   # back up the left lane
                lanes_l += 1
                lx = lane - 8 * lanes_l
                ya, yb = (A.box[1] + A.box[3]) / 2, (B.box[1] + B.box[3]) / 2
                c.arrow([(A.box[0] - 3, ya), (lx, ya), (lx, yb), (B.box[0] - 3, yb)], stroke=role, sw=1.6, dash=dash, cls=cls)
            else:           # skip forward down the right lane
                lanes_r += 1
                rx = c.W - lane + 8 * lanes_r
                ya, yb = (A.box[1] + A.box[3]) / 2, (B.box[1] + B.box[3]) / 2
                pts = [(A.box[2] + 3, ya), (rx, ya), (rx, yb), (B.box[2] + 3, yb)]
                c.arrow(pts, stroke=role, sw=1.6, dash=dash, cls=cls)
                if e.text:
                    # the label sits under the source box, inside the column, pointing at the lane
                    c.text(c.W - lane - 6, A.box[3] + 6, tr(e.text, lang), TICK['n'], 500,
                           'hl-ink' if role == 'hl' else 'label', 'end', 'top', max_w=w * 0.7, kind='note', halo=True)
        return c.maxy + 2
