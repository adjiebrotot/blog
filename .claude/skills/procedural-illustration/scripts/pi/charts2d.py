"""2D charts: bars, lines and areas, scatter, dumbbell, slope, donut.

Every component labels its data directly (no legend unless asked), formats every number in
the figure's language with one precision per series, keeps bars on a zero baseline, and lays
itself out again for the narrow layout (fewer ticks, wrapped labels, vertical bars turned
horizontal when the categories do not fit). See subskills/charts-2d/SKILL.md.
"""
import math

from . import fmt, metrics
from .figure import Component, tr
from .scale import Linear, Band, nice_step
from .tokens import ink
from .canvas import NOTE

TICK = {'w': 13, 'n': 12.5}
LABEL = {'w': 13.5, 'n': 13}
VALUE = {'w': 13.5, 'n': 13}


def make_fmt(spec, values=()):
    """spec: None, a callable f(v, lang), or a dict: dp, unit ('%' or ' days'), prefix ('Rp'),
    money ('Rp', 'A$'...), compact ('short'/'long'), sign. dp defaults to what the data needs."""
    if callable(spec):
        return spec
    spec = dict(spec or {})
    dp = spec.get('dp', fmt.dp_for(values))
    unit, prefix, sign = spec.get('unit', ''), spec.get('prefix', ''), spec.get('sign', False)
    if spec.get('money'):
        return lambda v, lang: fmt.money(v, spec['money'], dp, lang, spec.get('compact'), sign) + tr(unit, lang)
    if spec.get('compact'):
        return lambda v, lang: prefix + fmt.compact_number(v, dp, lang, spec['compact']) + tr(unit, lang)
    return lambda v, lang: prefix + fmt.number(v, dp, lang, sign) + tr(unit, lang)


def place(c, x, y, text, size, weight=400, fill='ink', prefs=('right', 'above', 'below', 'left'),
          gap=6, max_w=None, halo=True, avoid_marks=True, kind='note'):
    """Put a label near (x, y) in the first free spot of `prefs`; returns the box."""
    lines = metrics.wrap(text, max_w, size, weight) if max_w else str(text).split('\n')
    w = max(metrics.width(l, size, weight) for l in lines)
    h = size * 1.25 * (len(lines) - 1) + size
    cand = {
        'right': (x + gap, y - h / 2, 'start'), 'left': (x - gap - w, y - h / 2, 'end'),
        'above': (x - w / 2, y - gap - h, 'middle'), 'below': (x - w / 2, y + gap, 'middle'),
        'above-right': (x + gap * 0.5, y - gap - h, 'start'), 'above-left': (x - gap * 0.5 - w, y - gap - h, 'end'),
        'below-right': (x + gap * 0.5, y + gap, 'start'), 'below-left': (x - gap * 0.5 - w, y + gap, 'end'),
    }
    chosen = None
    for p in prefs:
        bx, by, anc = cand[p]
        box = (bx, by, bx + w, by + h)
        if box[0] < 0 or box[2] > c.W or box[1] < 0:
            continue
        if not c.hits(box, 3, marks=avoid_marks):
            chosen = (p, bx, by, anc)
            break
    if chosen is None:
        p = prefs[0]
        bx, by, anc = cand[p]
        bx = min(max(bx, 0), c.W - w)
        chosen = (p, bx, by, anc)
    p, bx, by, anc = chosen
    tx = bx if anc == 'start' else bx + w if anc == 'end' else bx + w / 2
    return c.text(tx, by, '\n'.join(lines), size, weight, fill, anc, 'top', halo=halo, kind=kind)


def _ov(a, b, pad=0.5):
    return min(a[2], b[2]) - max(a[0], b[0]) > pad and min(a[3], b[3]) - max(a[1], b[1]) > pad


def spread(items, lo, hi, gap):
    """items: list of [y, h]; push apart so no two overlap, kept within lo..hi. In place."""
    items.sort(key=lambda t: t[0])
    for _ in range(60):
        moved = False
        for i in range(1, len(items)):
            a, b = items[i - 1], items[i]
            need = (a[1] + b[1]) / 2 + gap
            if b[0] - a[0] < need:
                d = (need - (b[0] - a[0])) / 2
                a[0] -= d
                b[0] += d
                moved = True
        for t in items:
            t[0] = min(max(t[0], lo + t[1] / 2), hi - t[1] / 2)
        if not moved:
            break
    return items


def x_ticks_fit(c, xs, labels, size, min_gap=10):
    """Thin a list of x tick labels until neighbours never touch; keeps first and last."""
    n = len(xs)
    idx = list(range(n))
    fits = lambda keep: all(
        xs[b] - xs[a] >= metrics.width(labels[a], size) / 2 + metrics.width(labels[b], size) / 2 + min_gap
        for a, b in zip(keep, keep[1:]))
    # first choice: an even step that lands on both the first and the last label
    best = None
    for step in range(1, n):
        if fits(idx[::step]):
            best = best or step
            if (n - 1) % step == 0:
                # an even step that lands on both ends, unless it throws away far more labels
                return idx[::step] if step <= best * 2 else idx[::best]
    for step in range(1, n):
        if fits(idx[::step]):
            return idx[::step]
    return [idx[0], idx[-1]]


# ── Bars ───────────────────────────────────────────────────────────────────
class Bars(Component):
    """Bars with direct value labels.

    items: [{'label': str|dict, 'value': n, 'role': 'hl'|'a'|'base'|..., 'flag': 'IDN',
             'note': str|dict, 'text': override value text}]  (for group/stack: 'values': [..])
    orient: 'h' (ranked categories, long names) or 'v' (time or few categories).
    series: for mode 'group' or 'stack', [{'name': str|dict, 'role': ...}] (labelled directly
            on the first bar group when it fits, else a key line above).
    fmt: value format (make_fmt). axis: draw the value axis and gridlines (default: v yes, h no).
    sort: 'desc' / 'asc' / None (keep the given order: say why in review['order']).
    ref: [{'value': n, 'label': str|dict}] reference lines (an average, a target).
    annotate: [{'at': index or label, 'text': str|dict, 'head': str|dict}] notes on a bar.
    unit: the value axis' unit label (v bars), e.g. {'en': 'Rp trillion', 'id': 'Rp triliun'}.
    narrow_orient: orientation in the narrow layout (default: 'h' when v columns would be cramped).
    """

    def __init__(self, items, orient='h', mode='single', series=None, fmt=None, axis=None, sort=None,
                 ref=(), annotate=(), unit=None, domain=None, narrow_orient=None, row=None, label_w=None,
                 x_title=None, value_inside=False):
        self.items = list(items)
        if sort:
            key = lambda it: it.get('value', sum(it.get('values', [0])))
            self.items.sort(key=key, reverse=(sort == 'desc'))
        self.orient, self.mode, self.series = orient, mode, series or []
        vals = [v for it in self.items for v in ([it['value']] if 'value' in it else it['values'])]
        self.fmt = make_fmt(fmt, vals)
        self.axis, self.ref, self.annotate = axis, list(ref), list(annotate)
        self.unit, self.domain, self.narrow_orient = unit, domain, narrow_orient
        self.row, self.label_w, self.x_title, self.value_inside = row, label_w, x_title, value_inside
        self.legend = mode != 'single'

    def _total(self, it):
        if 'value' in it:
            return it['value']
        return sum(it['values']) if self.mode == 'stack' else max(it['values'])

    def table(self, lang):
        if self.mode == 'single':
            return (['', ''], [[tr(it['label'], lang), it.get('text') and tr(it['text'], lang) or self.fmt(it['value'], lang)]
                               for it in self.items])
        head = [''] + [tr(s['name'], lang) for s in self.series]
        return head, [[tr(it['label'], lang)] + [self.fmt(v, lang) for v in it['values']] for it in self.items]

    def value_labels(self):
        return [self.fmt(it['value'], 'en') for it in self.items if 'value' in it]

    def draw(self, c, lang, y):
        orient = self.orient
        if c.narrow and orient == 'v':
            if self.narrow_orient:
                orient = self.narrow_orient
            else:
                bw = (c.W - 40) / max(1, len(self.items))
                longest = max(metrics.width(tr(it['label'], lang), TICK['n']) for it in self.items)
                if bw < 26 or (longest > bw * 1.9 and len(self.items) > 4):
                    orient = 'h'
        if self.mode != 'single':
            y = self._key(c, lang, y)
        return self._h(c, lang, y) if orient == 'h' else self._v(c, lang, y)

    def _key(self, c, lang, y):
        x = 0
        size = LABEL[c.layout] - 0.5
        for s in self.series:
            name = tr(s['name'], lang)
            w = 12 + 5 + metrics.width(name, size) + 14
            if x + w > c.W and x > 0:
                x, y = 0, y + size * 1.6
            c.rect(x, y + 1, 12, 12, fill=s.get('role', 's1'), rx=3, mark=False)
            c.text(x + 17, y + 7, name, size, 400, 'label', kind='legend')
            x += w
        return y + size * 1.6 + 6

    # horizontal
    def _h(self, c, lang, y0):
        L = c.layout
        size, vsize = LABEL[L], VALUE[L]
        flag_h = 13 if L == 'w' else 12
        has_flag = any(it.get('flag') for it in self.items)
        max_lw = self.label_w or (c.W * (0.36 if L == 'n' else 0.3))
        labels = []
        for it in self.items:
            lab = tr(it['label'], lang)
            wt = 700 if it.get('role') == 'hl' else 400
            lines = metrics.wrap(lab, max_lw - (flag_h * 4 / 3 + 6 if has_flag else 0), size, wt)
            labels.append((lines, wt))
        lw = max(max(metrics.width(l, size, wt) for l in ls) for ls, wt in labels)
        fw = (flag_h * 4 / 3 + 6) if has_flag else 0
        x_bar = min(lw, max_lw) + fw + 10
        texts = [it.get('text') and tr(it['text'], lang) or self.fmt(self._total(it), lang) for it in self.items]
        vw = max(metrics.width(t, vsize, 700) for t in texts) + 8
        x_end = c.W - vw
        vals = [self._total(it) for it in self.items]
        lo = min(0, min(vals))
        hi = max(vals) if not self.domain else self.domain[1]
        sc = Linear(lo, hi, x_bar, x_end, zero=True, nice=bool(self.axis))
        nl = [len(ls) for ls, _ in labels]
        has_note = [bool(it.get('note')) for it in self.items]
        notes_under = {}
        for a in self.annotate:
            i = a['at'] if isinstance(a['at'], int) else [tr(it['label'], 'en') for it in self.items].index(a['at'])
            nl_ = metrics.wrap(tr(a['text'], lang), x_end - x_bar, TICK[L])
            notes_under[i] = nl_
        rowh = self.row or (26 if L == 'w' else 24)
        bh = rowh * 0.58
        y = y0
        if self.axis:
            y += 20
        ys = []
        for i, it in enumerate(self.items):
            extra = (nl[i] - 1) * size * 1.2 + (size if has_note[i] else 0)
            h = max(rowh, rowh + extra * 0.85)
            if i in notes_under:
                h += len(notes_under[i]) * TICK[L] * 1.25 + 2
            ys.append((y, h))
            y += h
        y_end = y
        if self.axis:
            for t in sc.ticks():
                X = sc(t)
                c.line(X, y0 + 16, X, y_end, stroke='grid', sw=1)
                c.text(X, y0 + 6, fmt.tick(t, sc.step, lang), TICK[L], 400, 'label', 'middle', kind='tick')
        for ref in self.ref:
            X = sc(ref['value'])
            c.line(X, y0 + (16 if self.axis else 0), X, y_end, stroke='ink', sw=1.25, dash='4 3')
        for i, it in enumerate(self.items):
            ry, rh = ys[i]
            if i in notes_under:
                rh -= len(notes_under[i]) * TICK[L] * 1.25 + 2
            cy = ry + rh / 2
            role = it.get('role', 'base')
            lines, wt = labels[i]
            note = tr(it.get('note'), lang)
            block_h = len(lines) * size * 1.2 + (size if note else 0)
            ty = cy - block_h / 2 + size * 0.6
            lab_fill = 'ink' if role == 'hl' or wt == 700 else 'label'
            lx = x_bar - 10 - fw
            c.text(lx, ty - size * 0.6, '\n'.join(lines), size, wt, lab_fill, 'end', 'top', lh=1.2)
            if note:
                nb = c.text(lx, ty - size * 0.6 + len(lines) * size * 1.2, note, NOTE[L], 400,
                            'label', 'end', 'top', kind='note')
                c.texts[-1]['row_note'] = True
            if it.get('flag'):
                c.flag(it['flag'], x_bar - 6 - flag_h * 4 / 3, cy - flag_h / 2, flag_h)
            if self.mode == 'stack':
                x = sc(0)
                for s, v in zip(self.series, it['values']):
                    c.rect(x, cy - bh / 2, sc(v) - sc(0), bh, fill=s.get('role', 's1'),
                           tip=f'{tr(it["label"], lang)}, {tr(s["name"], lang)}: {self.fmt(v, lang)}')
                    x += sc(v) - sc(0)
                end = x
            elif self.mode == 'group':
                k = len(it['values'])
                gh = bh * 1.4 / k
                for j, (s, v) in enumerate(zip(self.series, it['values'])):
                    yy = cy - bh * 0.7 + j * gh
                    c.bar(sc(0), yy, sc(v) - sc(0), gh - 1, fill=s.get('role', 's1'), r=2,
                          tip=f'{tr(it["label"], lang)}, {tr(s["name"], lang)}: {self.fmt(v, lang)}')
                    c.text(sc(v) + 5, yy + gh / 2, self.fmt(v, lang), vsize - 1, 400, ink(s.get('role', 's1')),
                           'start', 'middle', kind='value')
                end = None
            else:
                v = it['value']
                x0, x1 = sc(min(0, v)), sc(max(0, v))
                c.bar(x0, cy - bh / 2, max(x1 - x0, 1.5), bh, fill=role, r=3, round_end='right' if v >= 0 else 'left',
                      tip=f'{tr(it["label"], lang)}: {texts[i]}')
                end = x1
            if end is not None:
                vfill = 'ink' if role in ('hl',) else 'label'
                if self.value_inside and end - sc(0) > metrics.width(texts[i], vsize, 700) + 12:
                    c.text(end - 6, cy, texts[i], vsize, 700, 'bg', 'end', 'middle', kind='value')
                else:
                    c.text(end + 6, cy, texts[i], vsize, 700 if role == 'hl' else 500, vfill, 'start', 'middle',
                           kind='value', halo=True)
            if i in notes_under:
                c.text(x_bar, cy + bh / 2 + 4, '\n'.join(notes_under[i]), TICK[L], 400, 'label', 'start', 'top',
                       kind='note', lh=1.25)
        for ref in self.ref:
            X = sc(ref['value'])
            place(c, X, y_end + 2, tr(ref['label'], lang), TICK[L], 500, 'ink', prefs=('below',), gap=4)
        return max(y_end, c.maxy) + 2

    # vertical
    def _v(self, c, lang, y0):
        L = c.layout
        tsize = TICK[L]
        vals = [self._total(it) for it in self.items]
        dom_hi = self.domain[1] if self.domain else max(vals)
        dom_lo = self.domain[0] if self.domain else min(0, min(vals))
        top = y0 + (30 if self.unit else 10) + VALUE[L] + 4
        plot_h = 250 if L == 'w' else 210
        bottom = top + plot_h
        sc = Linear(dom_lo, dom_hi, bottom, top, zero=True, ticks=4 if L == 'n' else 5)
        tick_txt = [fmt.tick(t, sc.step, lang) for t in sc.ticks()]
        show_axis = self.axis if self.axis is not None else True
        left = (max(metrics.width(t, tsize) for t in tick_txt) + 8) if show_axis else 0
        b = Band(range(len(self.items)), left, c.W, inner=0.28 if L == 'w' else 0.22, outer=0.1)
        if self.unit:
            c.text(0, y0 + 6, tr(self.unit, lang), tsize, 400, 'label', 'start', 'middle', kind='axis')
        if show_axis:
            for t, tt in zip(sc.ticks(), tick_txt):
                Y = sc(t)
                c.line(left, Y, c.W, Y, stroke='axis' if t == 0 else 'grid', sw=1.25 if t == 0 else 1)
                c.text(left - 8, Y, tt, tsize, 400, 'label', 'end', 'middle', kind='tick')
        else:
            c.line(0, sc(0), c.W, sc(0), stroke='axis', sw=1.25)
        for ref in self.ref:
            Y = sc(ref['value'])
            c.line(left, Y, c.W, Y, stroke='ink', sw=1.25, dash='4 3')
        texts = []
        for i, it in enumerate(self.items):
            role = it.get('role', 'a')
            x = b(i)
            if self.mode == 'stack':
                yv = sc(0)
                for s, v in zip(self.series, it['values']):
                    h = sc(0) - sc(v)
                    c.rect(x, yv - h, b.bw, h, fill=s.get('role', 's1'),
                           tip=f'{tr(it["label"], lang)}, {tr(s["name"], lang)}: {self.fmt(v, lang)}')
                    yv -= h
                vt = it.get('text') and tr(it['text'], lang) or self.fmt(sum(it['values']), lang)
                texts.append((b.mid(i), yv, vt, 'ink'))
            elif self.mode == 'group':
                k = len(it['values'])
                gw = b.bw / k
                for j, (s, v) in enumerate(zip(self.series, it['values'])):
                    c.bar(x + j * gw, sc(v), gw - 1, sc(0) - sc(v), fill=s.get('role', 's1'), round_end='top', r=2,
                          tip=f'{tr(it["label"], lang)}, {tr(s["name"], lang)}: {self.fmt(v, lang)}')
            else:
                v = it['value']
                vt = it.get('text') and tr(it['text'], lang) or self.fmt(v, lang)
                c.bar(x, min(sc(v), sc(0)), b.bw, abs(sc(0) - sc(v)), fill=role,
                      round_end='top' if v >= 0 else 'bottom', r=3, tip=f'{tr(it["label"], lang)}: {vt}')
                texts.append((b.mid(i), sc(v) if v >= 0 else sc(v) + VALUE[L] + 10, vt,
                              'ink' if role == 'hl' else 'label', role == 'hl'))
        # value labels: all when they fit, else only highlighted, first, last, max and min
        size = VALUE[L]
        fits = all(metrics.width(t[2], size, 600) <= b.step - 3 for t in texts)
        keep = set(range(len(texts)))
        if not fits:
            size = VALUE[L] - 0.5
            fits = all(metrics.width(t[2], size, 600) <= b.step - 3 for t in texts)
        if not fits:
            hv = [self._total(it) for it in self.items]
            keep = {0, len(texts) - 1, hv.index(max(hv)), hv.index(min(hv))}
            keep |= {i for i, it in enumerate(self.items) if it.get('role') == 'hl' or it.get('label_value')}
        for i, t in enumerate(texts):
            if i in keep:
                hl = len(t) > 4 and t[4]
                # a halo keeps a label legible where it overhangs a taller neighbour on a phone
                c.text(t[0], t[1] - 6, t[2], size, 700 if hl else 600, t[3], 'middle', 'bottom', kind='value',
                       halo=True)
        # category labels (thinned on the narrow layout when they collide)
        labs = [tr(it['label'], lang) for it in self.items]
        xs = [b.mid(i) for i in range(len(self.items))]
        keep_x = x_ticks_fit(c, xs, labs, tsize, 6)
        wrap_w = b.step * 1.0
        for i in keep_x:
            lab = labs[i]
            lines = metrics.wrap(lab, max(wrap_w, metrics.width(max(lab.split(), key=len), tsize) + 1), tsize)
            hl = self.items[i].get('role') == 'hl'
            c.text(xs[i], bottom + 7, '\n'.join(lines), tsize, 600 if hl else 400, 'ink' if hl else 'label',
                   'middle', 'top', kind='tick', lh=1.15)
            if self.items[i].get('flag'):
                c.flag(self.items[i]['flag'], xs[i] - 8.7, bottom + 9 + len(lines) * tsize * 1.15 + 2, 13)
        if self.x_title:
            c.text(c.W / 2, c.maxy + 8, tr(self.x_title, lang), tsize, 400, 'label', 'middle', 'top', kind='axis')
        for ref in self.ref:
            Y = sc(ref['value'])
            place(c, c.W - 2, Y, tr(ref['label'], lang), tsize, 500, 'ink', prefs=('above-left', 'below-left'), gap=4)
        for a in self.annotate:
            i = a['at'] if isinstance(a['at'], int) else [tr(it['label'], 'en') for it in self.items].index(a['at'])
            X, Y = b.mid(i), sc(self._total(self.items[i])) - VALUE[L] - 10
            prefs = a.get('prefs', ('above', 'above-left', 'above-right', 'left', 'right'))
            bx = place(c, X, Y, tr(a['text'], lang), tsize, 400, 'label', prefs=prefs, max_w=c.W * (0.3 if L == 'w' else 0.55),
                       gap=8)
        return c.maxy + 2


# ── Lines and areas ────────────────────────────────────────────────────────
class Line(Component):
    """Lines over an ordered x (years, dates as numbers, or categories), labelled at their ends.

    x: list of x values (numbers, or strings for categories). x_fmt: callable(x, lang) for ticks.
    series: [{'name': str|dict, 'values': [...], 'role': 'hl'|'a'|'base'|'s1'..., 'dash': '5 4',
              'width': 2.5, 'label': True, 'markers': 'end'|'all'|None, 'area': False}]
    y: {'domain': [lo, hi], 'zero': bool, 'fmt': {...}, 'unit': str|dict, 'ticks': n, 'step': s}
       A y axis that does not start at zero must say so: set 'zero': False AND give the reason
       in review['axis'] (check.py asks); index charts usually say 'index, 2019 = 100'.
    ref: [{'value': 100, 'label': {...}}] horizontal reference lines (the index base, a target).
    bands: [{'from': 2020, 'to': 2021, 'label': {...}}] shaded spans (a recession, the pandemic).
    annotate: [{'x': 2021, 'series': 1, 'text': {...}, 'head': {...}, 'prefs': [...]}]
    stack: True for a stacked area (series drawn cumulatively, filled).
    """

    def __init__(self, x, series, y=None, x_fmt=None, ref=(), bands=(), annotate=(), stack=False,
                 end_values=True, height=None, x_title=None, legend=False):
        self.x, self.series = list(x), series
        self.y = dict(y or {})
        self.cat = any(isinstance(v, str) for v in self.x)
        self.x_fmt = x_fmt or (lambda v, lang: str(v))
        self.ref, self.bands, self.annotate, self.stack = list(ref), list(bands), list(annotate), stack
        vals = [v for s in series for v in s['values'] if v is not None]
        self.fmt = make_fmt(self.y.get('fmt'), vals)
        self.end_values, self.height, self.x_title, self.legend = end_values, height, x_title, legend

    def table(self, lang):
        head = [''] + [tr(s['name'], lang) for s in self.series]
        rows = [[self.x_fmt(x, lang)] + [self.fmt(s['values'][i], lang) if s['values'][i] is not None else '–'
                                         for s in self.series] for i, x in enumerate(self.x)]
        return head, rows

    def value_labels(self):
        return [self.fmt(v, 'en') for s in self.series for v in s['values'] if v is not None]

    def draw(self, c, lang, y0):
        L = c.layout
        tsize = TICK[L]
        series = self.series
        cum = None
        if self.stack:
            cum, acc = [], [0] * len(self.x)
            for s in series:
                acc = [a + (v or 0) for a, v in zip(acc, s['values'])]
                cum.append(list(acc))
        allv = [v for s in (cum or [s['values'] for s in series]) for v in s if v is not None]
        lo, hi = self.y.get('domain', (min(allv), max(allv)))
        zero = self.y.get('zero', bool(self.stack))
        sc_tmp = Linear(lo, hi, 0, 1, zero=zero, ticks=self.y.get('ticks', 4 if L == 'n' else 5),
                        step=self.y.get('step'))
        tick_txt = [fmt.tick(t, sc_tmp.step, lang) for t in sc_tmp.ticks()]
        left = max(metrics.width(t, tsize) for t in tick_txt) + 8
        # end labels: name + last value, in the series' text colour
        size = LABEL[L]
        ends = []
        for i, s in enumerate(series):
            if s.get('label', True) is False:
                continue
            last = max(j for j, v in enumerate(s['values']) if v is not None)
            v = (cum[i] if cum else s['values'])[last]
            name = tr(s['name'], lang)
            val = self.fmt(s['values'][last], lang) if self.end_values else ''
            ends.append({'i': i, 'last': last, 'v': v, 'name': name, 'val': val})
        maxw = c.W * (0.27 if L == 'w' else 0.34)
        for e in ends:
            e['lines'] = metrics.wrap(e['name'], maxw, size, 600) + ([e['val']] if e['val'] else [])
            e['w'] = max(metrics.width(l, size, 600) for l in e['lines'])
            e['h'] = len(e['lines']) * size * 1.2
        right_w = (max(e['w'] for e in ends) + 12) if ends else 8
        right = c.W - right_w
        top = y0 + (30 if self.y.get('unit') else 10)
        ph = self.height or (300 if L == 'w' else 230)
        bottom = top + ph
        sy = Linear(lo, hi, bottom, top, zero=zero, ticks=self.y.get('ticks', 4 if L == 'n' else 5),
                    step=self.y.get('step'))
        if self.cat:
            b = Band(range(len(self.x)), left, right, inner=0, outer=0.5)
            sx = lambda i: b.mid(i)
            X = [sx(i) for i in range(len(self.x))]
        else:
            xlo, xhi = min(self.x), max(self.x)
            pad = (right - left) * 0.02
            sx = lambda v: left + pad + (v - xlo) / ((xhi - xlo) or 1) * (right - left - 2 * pad)
            X = [sx(v) for v in self.x]
        # unit label above the y ticks
        if self.y.get('unit'):
            c.text(0, y0 + 6, tr(self.y['unit'], lang), tsize, 400, 'label', 'start', 'middle', kind='axis')
        # bands
        for bd in self.bands:
            i0 = self.x.index(bd['from']) if bd['from'] in self.x else None
            x0 = X[i0] if i0 is not None else sx(bd['from'])
            x1 = X[self.x.index(bd['to'])] if bd['to'] in self.x else sx(bd['to'])
            c.rect(x0, top, x1 - x0, bottom - top, fill='base-soft', mark=False)
            if bd.get('label'):
                c.text((x0 + x1) / 2, top + 4, tr(bd['label'], lang), tsize, 500, 'label', 'middle', 'top',
                       max_w=max(x1 - x0 + 30, 60), kind='note')
        # grid and ticks
        for t, tt in zip(sy.ticks(), tick_txt if sy.step == sc_tmp.step else [fmt.tick(t, sy.step, lang) for t in sy.ticks()]):
            Y = sy(t)
            c.line(left, Y, right, Y, stroke='axis' if t == 0 else 'grid', sw=1.25 if t == 0 else 1)
            c.text(left - 8, Y, tt, tsize, 400, 'label', 'end', 'middle', kind='tick')
        if not sy.zero_based:
            c.line(left, bottom, right, bottom, stroke='axis', sw=1.25)
        refs_to_label = []
        for ref in self.ref:
            Y = sy(ref['value'])
            c.line(left, Y, right, Y, stroke='ink', sw=1.25, dash='5 4')
            refs_to_label.append((Y, ref))
        # x ticks
        xl = [self.x_fmt(v, lang) for v in self.x]
        keep = x_ticks_fit(c, X, xl, tsize)
        for i in keep:
            c.line(X[i], bottom, X[i], bottom + 4, stroke='axis', sw=1)
            c.text(X[i], bottom + 8, xl[i], tsize, 400, 'label', 'middle', 'top', kind='tick')
        if self.x_title:
            c.text((left + right) / 2, bottom + 8 + tsize + 8, tr(self.x_title, lang), tsize, 400, 'label', 'middle',
                   'top', kind='axis')
        # areas then lines (context first, highlighted last so it sits on top)
        order = sorted(range(len(series)), key=lambda i: {'hl': 3, 'a': 2}.get(series[i].get('role'), 1))
        for i in order:
            s = series[i]
            vals = cum[i] if cum else s['values']
            pts = [(X[j], sy(v)) for j, v in enumerate(vals) if v is not None]
            role = s.get('role', f's{i + 1}')
            if self.stack or s.get('area'):
                base = [(X[j], sy(cum[i - 1][j]) if (cum and i > 0) else sy(max(sy.lo, 0) if zero else sy.lo))
                        for j, v in enumerate(vals) if v is not None]
                c.polygon(pts + base[::-1], fill=role + '-soft' if role in ('hl', 'a', 'base') else role,
                          op=None if role in ('hl', 'a', 'base') else 0.35)
            w = s.get('width', 2.75 if role == 'hl' else 2.25 if role in ('a', 's1') else 2)
            c.polyline(pts, stroke=role, sw=w, dash=s.get('dash'), data=True)
            mk = s.get('markers', 'end')
            idx = range(len(pts)) if mk == 'all' else ([len(pts) - 1] if mk == 'end' else [])
            for j in idx:
                c.circle(pts[j][0], pts[j][1], 3.5 if role == 'hl' else 3, fill=role, stroke='bg', sw=1.5)
            if mk != 'all':
                for j, (px, py) in enumerate(pts):
                    jj = [k for k, v in enumerate(vals) if v is not None][j]
                    c.add(f'<circle cx="{px:.1f}" cy="{py:.1f}" r="7" style="fill:transparent">'
                          f'<title>{tr(s["name"], lang)}, {self.x_fmt(self.x[jj], lang)}: {self.fmt(s["values"][jj], lang)}</title></circle>')
        for Y, ref in refs_to_label:
            if ref.get('label'):
                place(c, ref.get('at_x', right) if not ref.get('at') else X[self.x.index(ref['at'])], Y,
                      tr(ref['label'], lang), tsize, 500, 'ink',
                      prefs=('above-left', 'below-left', 'above-right', 'below-right'), gap=4, kind='note')
        # end labels, spread so they never collide
        items = [[sy(e['v']), e['h'], e] for e in ends]
        spread(items, top - 4, bottom + 4, 4)
        for yy, h, e in items:
            role = series[e['i']].get('role', f's{e["i"] + 1}')
            lx = right + 10
            ey = sy(e['v'])
            if abs(yy - ey) > 3:
                c.polyline([(X[e['last']] + 4, ey), (lx - 3, yy)], stroke=role, sw=1, cap='butt')
            yt = yy - h / 2
            name_lines = e['lines'][:-1] if e['val'] else e['lines']
            c.text(lx, yt, '\n'.join(name_lines), size, 600, ink(role), 'start', 'top', lh=1.2, kind='label')
            if e['val']:
                c.text(lx, yt + len(name_lines) * size * 1.2, e['val'], size, 700, ink(role), 'start', 'top',
                       kind='value')
        # annotations
        for a in self.annotate:
            j = self.x.index(a['x'])
            si = a.get('series', 0)
            v = (cum[si] if cum else series[si]['values'])[j]
            px, py = X[j], sy(v)
            role = series[si].get('role', 's1')
            c.circle(px, py, 4, fill='bg', stroke=role, sw=2)
            prefs = a.get('prefs', ('below', 'above', 'below-right', 'above-right', 'below-left', 'above-left'))
            maxw = a.get('max_w', 150 if L == 'w' else 120)
            text = tr(a['text'], lang)
            if a.get('head'):
                text = tr(a['head'], lang) + '\n' + text
            place(c, px, py, text, tsize, 400, 'ink', prefs=prefs, gap=10, max_w=maxw)
        return c.maxy + 2


# ── Scatter ────────────────────────────────────────────────────────────────
class Scatter(Component):
    """Two measures per item. points: [{'x','y','label','role','flag','r','show_label'}].
    Label only the points the story needs (role 'hl' or show_label True); the rest stay quiet.
    x, y: {'title': ..., 'fmt': {...}, 'domain': [...], 'zero': bool}. trend: draw a least-squares line."""

    def __init__(self, points, x, y, trend=False, quadrants=None, size=None):
        self.points, self.xs, self.ys = points, dict(x), dict(y)
        self.trend, self.quadrants, self.size = trend, quadrants, size
        self.fx = make_fmt(self.xs.get('fmt'), [p['x'] for p in points])
        self.fy = make_fmt(self.ys.get('fmt'), [p['y'] for p in points])

    def table(self, lang):
        return ([tr(self.ys.get('label', ''), lang) or '', tr(self.xs.get('title', 'x'), lang),
                 tr(self.ys.get('title', 'y'), lang)],
                [[tr(p.get('label', ''), lang), self.fx(p['x'], lang), self.fy(p['y'], lang)] for p in self.points])

    def draw(self, c, lang, y0):
        L = c.layout
        ts = TICK[L]
        xs = [p['x'] for p in self.points]
        ys = [p['y'] for p in self.points]
        sxt = Linear(*self.xs.get('domain', (min(xs), max(xs))), 0, 1, zero=self.xs.get('zero', False),
                     ticks=3 if L == 'n' else 5)
        syt = Linear(*self.ys.get('domain', (min(ys), max(ys))), 0, 1, zero=self.ys.get('zero', False),
                     ticks=4 if L == 'n' else 5)
        ytxt = [fmt.tick(t, syt.step, lang) for t in syt.ticks()]
        left = max(metrics.width(t, ts) for t in ytxt) + 8
        top = y0 + 22
        ph = self.size or (320 if L == 'w' else 260)
        bottom = top + ph
        sx = Linear(sxt.lo, sxt.hi, left + 6, c.W - 10, zero=False, nice=False, step=sxt.step)
        sy = Linear(syt.lo, syt.hi, bottom, top, zero=False, nice=False, step=syt.step)
        c.text(0, y0 + 6, tr(self.ys.get('title', ''), lang), ts, 400, 'label', 'start', 'middle', kind='axis')
        for t, tt in zip(sy.ticks(), ytxt):
            c.line(left, sy(t), c.W, sy(t), stroke='axis' if t == 0 else 'grid', sw=1)
            c.text(left - 8, sy(t), tt, ts, 400, 'label', 'end', 'middle', kind='tick')
        xt = sx.ticks()
        xl = [fmt.tick(t, sx.step, lang) for t in xt]
        for i in x_ticks_fit(c, [sx(t) for t in xt], xl, ts):
            c.line(sx(xt[i]), top, sx(xt[i]), bottom, stroke='axis' if xt[i] == 0 else 'grid', sw=1)
            c.text(sx(xt[i]), bottom + 8, xl[i], ts, 400, 'label', 'middle', 'top', kind='tick')
        c.text(c.W, bottom + 8 + ts + 8, tr(self.xs.get('title', ''), lang), ts, 400, 'label', 'end', 'top', kind='axis')
        if self.trend:
            n = len(xs)
            mx, my = sum(xs) / n, sum(ys) / n
            k = sum((a - mx) * (b - my) for a, b in zip(xs, ys)) / (sum((a - mx) ** 2 for a in xs) or 1)
            x0, x1 = sx.lo, sx.hi
            c.line(sx(x0), sy(my + k * (x0 - mx)), sx(x1), sy(my + k * (x1 - mx)), stroke='axis', sw=1.5, dash='5 4')
        order = sorted(self.points, key=lambda p: {'hl': 2, 'a': 1}.get(p.get('role'), 0))
        for p in order:
            role = p.get('role', 'base')
            r = p.get('r', 5.5 if role == 'hl' else 4.5)
            c.circle(sx(p['x']), sy(p['y']), r, fill=role, stroke='bg', sw=1.2,
                     tip=f'{tr(p.get("label", ""), lang)}: {self.fx(p["x"], lang)}, {self.fy(p["y"], lang)}')
        for p in sorted(self.points, key=lambda p: p.get('role') != 'hl'):
            if p.get('role') == 'hl' or p.get('show_label'):
                role = p.get('role', 'base')
                place(c, sx(p['x']), sy(p['y']), tr(p['label'], lang), LABEL[L], 600 if role == 'hl' else 400,
                      ink(role) if role != 'base' else 'label', prefs=('right', 'left', 'above', 'below'), gap=8,
                      kind='label')
        return c.maxy + 2


# ── Dumbbell (two values per row) and Slope (two moments) ──────────────────
class Dumbbell(Component):
    """rows: [{'label', 'a', 'b', 'flag', 'role'}]; names: ({'en': '2015'}, {'en': '2025'}) for the two ends,
    labelled once above the first row. roles: (role of a, role of b)."""

    def __init__(self, rows, names, roles=('base', 'hl'), fmt=None, sort=None):
        self.rows = sorted(rows, key=lambda r: r['b'] - r['a'], reverse=(sort == 'desc')) if sort else rows
        self.names, self.roles = names, roles
        self.fmt = make_fmt(fmt, [r[k] for r in rows for k in 'ab'])

    def table(self, lang):
        return [''] + [tr(n, lang) for n in self.names], [[tr(r['label'], lang), self.fmt(r['a'], lang),
                                                           self.fmt(r['b'], lang)] for r in self.rows]

    def draw(self, c, lang, y0):
        L = c.layout
        size = LABEL[L]
        has_flag = any(r.get('flag') for r in self.rows)
        fw = 23 if has_flag else 0
        lw = max(metrics.width(tr(r['label'], lang), size, 700 if r.get('role') == 'hl' else 400) for r in self.rows)
        lw = min(lw, c.W * 0.32)
        x0 = lw + fw + 12
        vals = [r[k] for r in self.rows for k in 'ab']
        vw = max(metrics.width(self.fmt(v, lang), VALUE[L], 600) for v in vals) + 8
        sc = Linear(min(vals), max(vals), x0 + vw, c.W - vw, zero=False, nice=False)
        rowh = 30 if L == 'w' else 28
        y = y0 + 26
        first = True
        for r in self.rows:
            cy = y + rowh / 2
            hl = r.get('role') == 'hl'
            c.text(x0 - 10 - fw, cy, tr(r['label'], lang), size, 700 if hl else 400, 'ink' if hl else 'label', 'end',
                   max_w=c.W * 0.32, kind='label')
            if r.get('flag'):
                c.flag(r['flag'], x0 - 6 - 17.3, cy - 6.5, 13)
            xa, xb = sc(r['a']), sc(r['b'])
            c.line(xa, cy, xb, cy, stroke='axis', sw=3 if hl else 2, cap='round')
            ra, rb = self.roles
            c.circle(xa, cy, 5.5, fill=ra, stroke='bg', sw=1.2)
            c.circle(xb, cy, 6 if hl else 5.5, fill=rb, stroke='bg', sw=1.2)
            left_first = xa <= xb
            c.text((xa if left_first else xb) - 9, cy, self.fmt(r['a'] if left_first else r['b'], lang), VALUE[L] - 0.5,
                   400, 'label', 'end', kind='value')
            c.text((xb if left_first else xa) + 9, cy, self.fmt(r['b'] if left_first else r['a'], lang), VALUE[L] - 0.5,
                   700 if hl else 600, ink(rb) if left_first else 'label', 'start', kind='value')
            if first:
                c.text(xa, y0 + 8, tr(self.names[0], lang), TICK[L], 500, ink(ra) if ra != 'base' else 'label',
                       'middle', kind='legend')
                c.text(xb, y0 + 8, tr(self.names[1], lang), TICK[L], 600, ink(rb), 'middle', kind='legend')
                first = False
            y += rowh
        return c.maxy + 2


class Slope(Component):
    """Two columns (before, after), one line per item, labelled at both ends.
    rows: [{'label', 'a', 'b', 'role', 'flag'}]; names: (left heading, right heading)."""

    def __init__(self, rows, names, fmt=None, height=None):
        self.rows, self.names, self.height = rows, names, height
        self.fmt = make_fmt(fmt, [r[k] for r in rows for k in 'ab'])

    def table(self, lang):
        return [''] + [tr(n, lang) for n in self.names], [[tr(r['label'], lang), self.fmt(r['a'], lang),
                                                           self.fmt(r['b'], lang)] for r in self.rows]

    def draw(self, c, lang, y0):
        L = c.layout
        size = LABEL[L]
        vals = [r[k] for r in self.rows for k in 'ab']
        top, ph = y0 + 30, self.height or (300 if L == 'w' else 260)
        sc = Linear(min(vals), max(vals), top + ph, top, zero=False, nice=False)
        lab = lambda r, k: (tr(r['label'], lang) + ' ' if k == 'b' else '') + self.fmt(r[k], lang) + (
            ' ' + tr(r['label'], lang) if k == 'a' and False else '')
        lw = max(metrics.width(f'{tr(r["label"], lang)}  {self.fmt(r["a"], lang)}', size, 600) for r in self.rows)
        rw = max(metrics.width(f'{self.fmt(r["b"], lang)}  {tr(r["label"], lang)}', size, 600) for r in self.rows)
        xa, xb = min(lw + 10, c.W * 0.4), max(c.W - rw - 10, c.W * 0.6)
        c.text(xa, y0 + 8, tr(self.names[0], lang), TICK[L], 600, 'label', 'middle', kind='legend')
        c.text(xb, y0 + 8, tr(self.names[1], lang), TICK[L], 600, 'label', 'middle', kind='legend')
        c.line(xa, top - 6, xa, top + ph + 6, stroke='grid')
        c.line(xb, top - 6, xb, top + ph + 6, stroke='grid')
        order = sorted(self.rows, key=lambda r: {'hl': 2, 'a': 1}.get(r.get('role'), 0))
        for r in order:
            role = r.get('role', 'base')
            c.line(xa, sc(r['a']), xb, sc(r['b']), stroke=role, sw=2.75 if role == 'hl' else 1.75, cap='round')
            c.circle(xa, sc(r['a']), 3.5, fill=role)
            c.circle(xb, sc(r['b']), 3.5, fill=role)
        for k, x, anc in (('a', xa - 8, 'end'), ('b', xb + 8, 'start')):
            items = [[sc(r[k]), size * 1.1, r] for r in self.rows]
            spread(items, top - 10, top + ph + 10, 2)
            for yy, h, r in items:
                role = r.get('role', 'base')
                t = (f'{tr(r["label"], lang)}  {self.fmt(r["a"], lang)}' if k == 'a'
                     else f'{self.fmt(r["b"], lang)}  {tr(r["label"], lang)}')
                c.text(x, yy, t, size, 700 if role == 'hl' else 400, ink(role) if role != 'base' else 'label', anc,
                       kind='label')
        return c.maxy + 2


# ── Donut ──────────────────────────────────────────────────────────────────
class Donut(Component):
    """Shares of one whole (2 to 5 parts; more belongs in bars). parts: [{'label','value','role'}],
    centre: {'value': str|dict, 'label': str|dict} for the key number in the hole."""

    def __init__(self, parts, centre=None, fmt=None, thickness=0.34):
        self.parts, self.centre, self.thickness = parts, centre, thickness
        total = sum(p['value'] for p in parts)
        self.total = total
        self.fmt = make_fmt(fmt or {'dp': 0, 'unit': '%'}, [p['value'] / total * 100 for p in parts])

    def table(self, lang):
        return ['', '%'], [[tr(p['label'], lang), self.fmt(p['value'] / self.total * 100, lang)] for p in self.parts]

    def draw(self, c, lang, y0):
        L = c.layout
        R = 110 if L == 'w' else 92
        cx = R + 10 if L == 'w' else c.W / 2
        cy = y0 + R + 6
        r_in = R * (1 - self.thickness)
        a = -math.pi / 2
        mids = []
        for p in self.parts:
            frac = p['value'] / self.total
            b = a + frac * 2 * math.pi
            large = 1 if b - a > math.pi else 0
            pts = lambda r, t: (cx + r * math.cos(t), cy + r * math.sin(t))
            (x1, y1), (x2, y2) = pts(R, a), pts(R, b)
            (x3, y3), (x4, y4) = pts(r_in, b), pts(r_in, a)
            d = (f'M{x1:.1f} {y1:.1f}A{R} {R} 0 {large} 1 {x2:.1f} {y2:.1f}L{x3:.1f} {y3:.1f}'
                 f'A{r_in:.1f} {r_in:.1f} 0 {large} 0 {x4:.1f} {y4:.1f}Z')
            c.path(d, fill=p.get('role', 'base'), stroke='bg', sw=2,
                   tip=f'{tr(p["label"], lang)}: {self.fmt(frac * 100, lang)}', bbox=(cx - R, cy - R, cx + R, cy + R))
            mids.append((a + b) / 2)
            a = b
        if self.centre:
            c.text(cx, cy - 4, tr(self.centre['value'], lang), 30 if L == 'w' else 26, 700, 'ink', 'middle', 'bottom',
                   kind='value')
            c.text(cx, cy + 2, tr(self.centre['label'], lang), TICK[L], 400, 'label', 'middle', 'top',
                   max_w=r_in * 1.6, kind='label')
        # labels: a swatch list beside the ring (wide) or under it (narrow); no leaders across the ring
        size = LABEL[L]
        x0, y = (cx + R + 36, y0 + 10) if L == 'w' else (0, cy + R + 16)
        vw = max(metrics.width(self.fmt(p['value'] / self.total * 100, lang), size + (2 if L == 'w' else 0), 700)
                 for p in self.parts)
        if L == 'w':
            total_h = len(self.parts) * (size * 1.3 + 12)
            y = max(y0 + 4, cy - total_h / 2)
        for p in self.parts:
            role = p.get('role', 'base')
            vs = size + (2 if L == 'w' else 0)
            c.rect(x0, y + vs * 0.5 - 6, 12, 12, fill=role, rx=3, mark=False)
            c.text(x0 + 20, y + vs * 0.5, self.fmt(p['value'] / self.total * 100, lang), vs, 700,
                   ink(role) if role != 'base' else 'ink', 'start', 'middle', kind='value')
            b2 = c.text(x0 + 20 + vw + 8, y + vs * 0.5, tr(p['label'], lang), size, 400, 'label', 'start', 'middle',
                        max_w=c.W - x0 - 30 - vw)
            y = b2[3] + 12
        return c.maxy + 2
