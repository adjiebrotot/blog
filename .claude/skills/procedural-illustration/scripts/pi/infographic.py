"""Infographics: counts you can see. Unit (pictogram) charts, stacked towers, waffles, stat
tiles, size comparisons and timelines. See subskills/infographic/SKILL.md.

The honest-picture rules hold here too: one icon is one fixed amount (said in the key line),
a tower's height is proportional to its value, a compared area is proportional to its value
(never its side), and every count is also written as a number.
"""
import math

from . import metrics
from .figure import Component, tr
from .charts2d import make_fmt, LABEL, VALUE, TICK, place
from .tokens import ink


class Units(Component):
    """A count drawn as icons (one icon = `per` units) or as a stacked tower of slabs.

    rows: [{'label': str|dict, 'value': n, 'role': 'hl'|'a'|'base', 'flag': 'IDN', 'note': str|dict}]
    icon: a solid glyph ('phone', 'person', 'house', 'coin', 'day', 'banknote', 'bowl', ...) or any
          Lucide icon name (outline).
    per: the amount one icon stands for (1 day, 1 million people). key: the sentence that says so,
         e.g. {'en': '= 1 working day', 'id': '= 1 hari kerja'}; drawn once, with the icon, above.
    arrange: 'grid' (rows of icons, `cols` per line: {'w': 20, 'n': 10}) or 'stack' (one tower per
             row, slabs piled up like phones on a table, side by side, every 10th slab ticked).
    value_text: per-row override; fmt: number format of the count.
    """

    def __init__(self, rows, icon='square', per=1, key=None, arrange='grid', cols=None, fmt=None,
                 unit=None, slab=None, cap_icon=True, tick_every=10):
        self.rows, self.icon, self.per, self.key = rows, icon, per, key
        self.arrange, self.cols = arrange, cols or {'w': 20, 'n': 10}
        self.fmt = make_fmt(fmt, [r['value'] for r in rows])
        self.unit, self.slab, self.cap_icon, self.tick_every = unit, slab, cap_icon, tick_every
        self.orient = 'h' if arrange == 'grid' else 'v'

    def table(self, lang):
        return ['', tr(self.unit, lang) or ''], [[tr(r['label'], lang), self.value(r, lang)] for r in self.rows]

    def value(self, r, lang):
        if r.get('text'):
            return tr(r['text'], lang)
        return self.fmt(r['value'], lang) + (tr(self.unit, lang) or '')

    def value_labels(self):
        return [self.fmt(r['value'], 'en') for r in self.rows]

    def _key(self, c, lang, y):
        if not self.key:
            return y
        s = 18 if c.layout == 'w' else 16
        if self.arrange == 'stack':
            self._slab(c, 0, y + s / 2 - 3, s * 1.4, 'base')
            x = s * 1.4 + 8
        else:
            c.icon(self.icon, 0, y, s, color='base', fill_color='base')
            x = s + 6
        c.text(x, y + s / 2, tr(self.key, lang), LABEL[c.layout], 500, 'label', kind='legend')
        return y + s + 14

    def draw(self, c, lang, y0):
        y = self._key(c, lang, y0)
        return self._grid(c, lang, y) if self.arrange == 'grid' else self._stack(c, lang, y)

    def _grid(self, c, lang, y):
        L = c.layout
        cols = self.cols[L] if isinstance(self.cols, dict) else self.cols
        size = LABEL[L]
        narrow = L == 'n'
        lw = 0 if narrow else min(max(metrics.width(tr(r['label'], lang), size, 700) for r in self.rows) + 30,
                                  c.W * 0.24)
        vw = 0 if narrow else max(metrics.width(self.value(r, lang), VALUE[L] + 2, 700) for r in self.rows) + 12
        area = c.W - lw - vw
        step = area / cols
        s = step * 0.84
        for r in self.rows:
            role = r.get('role', 'base')
            hl = role == 'hl'
            n = r['value'] / self.per
            full, frac = int(n), n - int(n)
            if narrow:
                b = c.text(0, y, tr(r['label'], lang), size, 700, 'ink' if hl else 'label', 'start', 'top')
                x_after = b[2]
                if r.get('flag'):
                    c.flag(r['flag'], b[2] + 6, b[1] + 0.5, 12)
                    x_after += 22
                c.text(c.W, y, self.value(r, lang), VALUE[L] + 1, 700, ink(role) if role != 'base' else 'ink', 'end', 'top',
                       kind='value')
                y += size + 8
                gx = 0
            else:
                gx = lw
            rows_n = math.ceil(n / cols) if n else 1
            for i in range(full + (1 if frac > 0.04 else 0)):
                cx = gx + (i % cols) * step
                cy = y + (i // cols) * step
                if i < full:
                    c.icon(self.icon, cx, cy, s, color=role, fill_color=role,
                           tip=None)
                else:  # the last, partial icon: clip it to its share of the width
                    cid = c.uid('uc')
                    c.defs.append(f'<clipPath id="{cid}"><rect x="{cx:.1f}" y="{cy:.1f}" width="{s * frac:.1f}" '
                                  f'height="{s:.1f}"/></clipPath>')
                    c.add(f'<g clip-path="url(#{cid})">')
                    c.icon(self.icon, cx, cy, s, color=role, fill_color=role)
                    c.add('</g>')
                    c.icon(self.icon, cx, cy, s, color='base-soft', fill_color='base-soft')
            block_h = rows_n * step
            if not narrow:
                cy = y + min(block_h, step) / 2
                lb = c.text(lw - 32 - 10 if any(rr.get('flag') for rr in self.rows) else lw - 10, y + s / 2,
                            tr(r['label'], lang), size, 700 if hl else 400, 'ink' if hl else 'label', 'end',
                            max_w=lw - 44)
                if r.get('flag'):
                    c.flag(r['flag'], lw - 32, y + s / 2 - 6.5, 13)
                c.text(c.W - vw + 10, y + s / 2, self.value(r, lang), VALUE[L] + 2, 700,
                       ink(role) if role != 'base' else 'ink', 'start', kind='value')
                if r.get('note'):
                    c.text(lw - 10, lb[3] + 2, tr(r['note'], lang), TICK[L], 400, 'label', 'end', 'top', max_w=lw - 12,
                           kind='note')
            y += block_h + (16 if not narrow else 14)
        return c.maxy + 2

    def _slab(self, c, x, y, w, role, cap=False):
        """One unit lying flat, seen slightly from above: a thin body and a lighter top face."""
        t = self.slab or 3.2
        d = min(w * 0.18, 7)
        c.polygon([(x, y), (x + d, y - d * 0.55), (x + w + d, y - d * 0.55), (x + w, y)],
                  fill=role + '-soft' if role in ('hl', 'a', 'base') else role, stroke='bg', sw=0.6)
        c.rect(x, y, w, t, fill=role, mark=False)

    def _stack(self, c, lang, y0):
        L = c.layout
        n = len(self.rows)
        maxv = max(r['value'] for r in self.rows)
        t = self.slab or (3.0 if L == 'w' else 2.6)
        gap_label = 50
        col_w = min(120 if L == 'w' else 74, (c.W - 40) / n * 0.62)
        step = (c.W - 30) / n
        units_max = maxv / self.per
        top = y0 + VALUE[L] + 26
        bottom = top + units_max * t
        for i, r in enumerate(self.rows):
            role = r.get('role', 'base')
            x = 30 + i * step + (step - col_w) / 2
            units = r['value'] / self.per
            k = int(math.floor(units + 1e-9))
            frac = units - k
            yb = bottom
            for j in range(k):
                c.rect(x, yb - t, col_w, t - 0.6, fill=role, mark=False, rx=0.8)
                yb -= t
            if frac > 0.05:
                c.rect(x, yb - t * frac, col_w * 1, t * frac - 0.4, fill=role, mark=False)
                yb -= t * frac
            # the top unit seen from above: the stack's cap
            d = min(col_w * 0.16, 9)
            c.polygon([(x, yb), (x + d, yb - d * 0.6), (x + col_w + d, yb - d * 0.6), (x + col_w, yb)],
                      fill=role + '-soft' if role in ('hl', 'a', 'base') else role, stroke=role, sw=1)
            c.polygon([(x + col_w, yb), (x + col_w + d, yb - d * 0.6), (x + col_w + d, bottom - d * 0.6),
                       (x + col_w, bottom)], fill=role, op=0.55)
            if self.cap_icon and self.icon:
                s = min(d * 1.6, 14)
            c.marks.append((x, yb - d, x + col_w + d, bottom))
            # every tenth unit ticked on the left, so the count can be read off the tower
            if self.tick_every and i == 0:
                for m in range(self.tick_every, int(units_max) + 1, self.tick_every):
                    yy = bottom - m * t
                    c.line(4, yy, 24, yy, stroke='grid', sw=1)
                    if m % (self.tick_every * (5 if units_max > 60 else 2)) == 0:
                        c.text(0, yy, str(m), TICK[L], 400, 'label', 'start', 'middle',
                               kind='tick')
            c.text(x + col_w / 2 + d / 2, yb - d - 6, self.value(r, lang), VALUE[L] + (3 if L == 'w' else 1), 700,
                   ink(role) if role != 'base' else 'ink', 'middle', 'bottom', kind='value')
            hl = role == 'hl'
            lb = c.text(x + col_w / 2, bottom + 10, tr(r['label'], lang), LABEL[L], 700 if hl else 500,
                        'ink' if hl else 'label', 'middle', 'top', max_w=step - 6)
            if r.get('flag'):
                c.flag(r['flag'], x + col_w / 2 - 8.7, lb[3] + 5, 13)
            if r.get('note'):
                c.text(x + col_w / 2, (lb[3] + (22 if r.get('flag') else 4)), tr(r['note'], lang), TICK[L], 400,
                       'label', 'middle', 'top', max_w=step - 6, kind='note')
        c.line(0, bottom + 0.5, c.W, bottom + 0.5, stroke='axis', sw=1.25)
        return c.maxy + 2


class Waffle(Component):
    """A 10 x 10 grid of 100 squares, one per percent. parts: [{'label', 'value' (percent), 'role'}],
    the remainder drawn in base-soft. Use for one or two shares of a whole that readers should count."""

    def __init__(self, parts, fmt=None, rest=None):
        self.parts, self.rest = parts, rest
        self.fmt = make_fmt(fmt or {'dp': 0, 'unit': '%'}, [p['value'] for p in parts])

    def table(self, lang):
        return ['', '%'], [[tr(p['label'], lang), self.fmt(p['value'], lang)] for p in self.parts]

    def value_labels(self):
        return [self.fmt(p['value'], 'en') for p in self.parts]

    def draw(self, c, lang, y0):
        L = c.layout
        side = 240 if L == 'w' else min(220, c.W)
        cell = side / 10
        cells = []
        for p in self.parts:
            cells += [p.get('role', 'hl')] * int(round(p['value']))
        cells += ['base-soft'] * (100 - len(cells))
        for i, role in enumerate(cells):
            col, row = i % 10, i // 10
            c.rect(col * cell + 1, y0 + (9 - row) * cell + 1, cell - 2, cell - 2, fill=role, rx=2, mark=False)
        c.marks.append((0, y0, side, y0 + side))
        x, y = (side + 28, y0 + 6) if L == 'w' else (0, y0 + side + 16)
        for p in self.parts + ([{'label': self.rest, 'value': 100 - sum(q['value'] for q in self.parts),
                                 'role': 'base-soft'}] if self.rest else []):
            role = p.get('role', 'hl')
            b = c.text(x, y, self.fmt(p['value'], lang), 28 if L == 'w' else 24, 700,
                       ink(role) if role not in ('base-soft',) else 'label', 'start', 'top', kind='value')
            b2 = c.text(x, b[3] + 4, tr(p['label'], lang), LABEL[L], 400, 'label', 'start', 'top',
                        max_w=c.W - x - 4)
            y = b2[3] + 16
        return c.maxy + 2


class Stats(Component):
    """Big-number tiles: [{'value': str|dict, 'label': str|dict, 'role', 'icon', 'note'}]. Two to four.
    Wide: one row; narrow: two columns (or one, `narrow_cols`)."""

    def __init__(self, tiles, narrow_cols=2):
        self.tiles, self.narrow_cols = tiles, narrow_cols

    def table(self, lang):
        return ['', ''], [[tr(t['label'], lang), tr(t['value'], lang)] for t in self.tiles]

    def draw(self, c, lang, y0):
        L = c.layout
        n = len(self.tiles)
        cols = n if L == 'w' else min(self.narrow_cols, n)
        gap = 12
        w = (c.W - gap * (cols - 1)) / cols
        vs = 30 if L == 'w' else 24
        y = y0
        row_h = 0
        heights = []
        for i, t in enumerate(self.tiles):
            col = i % cols
            if col == 0 and i:
                y += row_h + gap
                row_h = 0
            x = col * (w + gap)
            role = t.get('role', 'a')
            pad = 12
            ty = y + pad
            if t.get('icon'):
                c.icon(t['icon'], x + pad, ty, 22, color=role, fill_color=role)
                ty += 30
            b = c.text(x + pad, ty, tr(t['value'], lang), vs, 700, ink(role) if role != 'base' else 'ink', 'start',
                       'top', max_w=w - 2 * pad, kind='value', lh=1.1)
            b2 = c.text(x + pad, b[3] + 6, tr(t['label'], lang), LABEL[L], 400, 'label', 'start', 'top',
                        max_w=w - 2 * pad, lh=1.3)
            bottom = b2[3]
            if t.get('note'):
                b3 = c.text(x + pad, b2[3] + 4, tr(t['note'], lang), TICK[L], 400, 'label', 'start', 'top',
                            max_w=w - 2 * pad, kind='note')
                bottom = b3[3]
            h = bottom - y + pad
            heights.append((x, y, h, role))
            row_h = max(row_h, h)
        # tiles of a row share the tallest height; drawn behind the text
        tiles = []
        for x, yy, h, role in heights:
            rh = max(hh for xx, y2, hh, _ in heights if y2 == yy)
            tiles.append(f'<rect x="{x:.1f}" y="{yy:.1f}" width="{w:.1f}" height="{rh:.1f}" rx="10" '
                         f'style="fill:var(--pi-node);stroke:var(--pi-node-line);stroke-width:1"/>')
        c.els[:0] = tiles
        return max(yy + max(hh for xx, y2, hh, _ in heights if y2 == yy) for x, yy, h, role in heights) + 2


class Compare(Component):
    """Two to four amounts as squares whose AREA is proportional to the value, bottom-aligned,
    labelled with value and name. items: [{'label', 'value', 'role', 'text', 'flag'}]."""

    def __init__(self, items, fmt=None, shape='square'):
        self.items, self.shape = items, shape
        self.fmt = make_fmt(fmt, [i['value'] for i in items])

    def table(self, lang):
        return ['', ''], [[tr(i['label'], lang), self.fmt(i['value'], lang)] for i in self.items]

    def value_labels(self):
        return [self.fmt(i['value'], 'en') for i in self.items]

    def draw(self, c, lang, y0):
        L = c.layout
        maxv = max(i['value'] for i in self.items)
        n = len(self.items)
        maxside = min(200 if L == 'w' else 150, (c.W - 16 * (n - 1)) / n * (1.6 if n > 1 else 1))
        sides = [maxside * math.sqrt(i['value'] / maxv) for i in self.items]
        total = sum(sides) + 16 * (n - 1)
        scale = min(1.0, c.W / total)
        sides = [s * scale for s in sides]
        x = (c.W - (sum(sides) + 16 * (n - 1))) / 2
        top = y0 + 34
        base = top + max(sides)
        for it, s in zip(self.items, sides):
            role = it.get('role', 'base')
            if self.shape == 'circle':
                c.circle(x + s / 2, base - s / 2, s / 2, fill=role)
            else:
                c.rect(x, base - s, s, s, fill=role, rx=4)
            c.text(x + s / 2, base - s - 6, it.get('text') and tr(it['text'], lang) or self.fmt(it['value'], lang),
                   VALUE[L] + 2, 700, ink(role) if role != 'base' else 'ink', 'middle', 'bottom', kind='value')
            c.text(x + s / 2, base + 8, tr(it['label'], lang), LABEL[L], 500, 'label', 'middle', 'top',
                   max_w=max(s + 16, 70))
            x += s + 16
        return c.maxy + 2


class Timeline(Component):
    """Dated events on one line: [{'date': str|dict, 'text': str|dict, 'role'}]. Wide: horizontal,
    labels alternating above and below; narrow: vertical, text to the right."""

    def __init__(self, events, positions=None):
        self.events, self.positions = events, positions

    def table(self, lang):
        return ['', ''], [[tr(e['date'], lang), tr(e['text'], lang)] for e in self.events]

    def draw(self, c, lang, y0):
        L = c.layout
        n = len(self.events)
        if L == 'w':
            mid = y0 + 90
            x0, x1 = 20, c.W - 20
            pos = self.positions or [i / max(1, n - 1) for i in range(n)]
            c.line(x0, mid, x1, mid, stroke='axis', sw=2)
            slot = (x1 - x0) / max(1, n - 1) * 1.8
            for i, (e, p) in enumerate(zip(self.events, pos)):
                x = x0 + p * (x1 - x0)
                role = e.get('role', 'a')
                c.circle(x, mid, 6, fill=role, stroke='bg', sw=2)
                up = i % 2 == 0
                c.line(x, mid + (-8 if up else 8), x, mid + (-26 if up else 26), stroke='axis', sw=1)
                anc = 'start' if i == 0 else 'end' if i == n - 1 else 'middle'
                if up:
                    b = c.text(x, mid - 30, tr(e['text'], lang), TICK[L], 400, 'label', anc, 'bottom', max_w=slot)
                    c.text(x, b[1] - 3, tr(e['date'], lang), LABEL[L], 700, ink(role), anc, 'bottom', kind='value')
                else:
                    b = c.text(x, mid + 30, tr(e['date'], lang), LABEL[L], 700, ink(role), anc, 'top', kind='value')
                    c.text(x, b[3] + 3, tr(e['text'], lang), TICK[L], 400, 'label', anc, 'top', max_w=slot)
        else:
            y = y0 + 6
            c_x = 8
            first = y
            for e in self.events:
                role = e.get('role', 'a')
                c.circle(c_x, y + 8, 5.5, fill=role, stroke='bg', sw=2)
                b = c.text(c_x + 16, y, tr(e['date'], lang), LABEL[L], 700, ink(role), 'start', 'top', kind='value')
                b2 = c.text(c_x + 16, b[3] + 3, tr(e['text'], lang), TICK[L], 400, 'label', 'start', 'top',
                            max_w=c.W - c_x - 18)
                last = y + 8
                y = b2[3] + 14
            c.els.insert(0, f'<line x1="{c_x}" y1="{first + 8}" x2="{c_x}" y2="{last}" '
                            f'style="stroke:var(--pi-axis);stroke-width:2"/>')
        return c.maxy + 2
