"""The drawing surface: SVG elements painted by role, with every text box recorded.

One Canvas is one layout (wide or narrow) in one language. Components draw on it; the
checks read what it recorded (text boxes, sizes, colours, the drawn extent) to prove the
figure is readable: no text overlaps, nothing leaves the frame, no text below the minimum
size, no hard-coded colour.

Units are CSS px at the layout's design width (720 wide, 280 narrow): the figure is drawn at
about 1:1 in the blog column, so a 13 here is 13px on the page.
"""
import html, json, math, os
from contextlib import contextmanager

from . import metrics
from .tokens import paint

MIN_TEXT = {'w': 13, 'n': 12.5}   # smallest text allowed per layout (checklist item 4)
# A row note (a caveat under a name: "Base salary only") is set smaller than the data label on
# purpose, so it reads as a qualifier, not as data.
MIN_NOTE = {'w': 11.5, 'n': 11}
NOTE = MIN_NOTE
ICONS = None
COUNTRIES = None
ASSETS = os.path.join(os.path.dirname(__file__), '..', '..', 'assets')


def _n(v):
    """Short number for SVG output."""
    r = round(v, 1)
    return str(int(r)) if r == int(r) else str(r)


def esc(s):
    return html.escape(str(s), quote=True)


def countries():
    global COUNTRIES
    if COUNTRIES is None:
        COUNTRIES = json.load(open(os.path.join(ASSETS, 'countries.json'), encoding='utf-8'))
    return COUNTRIES


def icon_markup(name):
    global ICONS
    if ICONS is None:
        ICONS = json.load(open(os.path.join(ASSETS, 'icons.json'), encoding='utf-8'))
    if name in GLYPHS:
        return None
    if name not in ICONS['icons']:
        near = [k for k in ICONS['icons'] if name in k][:8]
        raise KeyError(f'no icon {name!r}; close: {near} (scripts/icons.py --search WORD)')
    return ICONS['icons'][name]


# Solid pictograms for unit charts and infographics (24 x 24 grid, filled, square-ish ends).
# Lucide icons are outlines; a count of things reads better in solid shapes.
GLYPHS = {
    'phone': 'M7 1.5h10a2.5 2.5 0 0 1 2.5 2.5v16a2.5 2.5 0 0 1-2.5 2.5H7A2.5 2.5 0 0 1 4.5 20V4A2.5 2.5 0 0 1 7 1.5Zm2.5 1.6a.7.7 0 0 0 0 1.4h5a.7.7 0 0 0 0-1.4ZM12 18.3a1.3 1.3 0 1 0 0 2.6 1.3 1.3 0 0 0 0-2.6Z',
    'person': 'M12 1.5a3.6 3.6 0 1 1 0 7.2 3.6 3.6 0 0 1 0-7.2ZM8.2 10h7.6a2.7 2.7 0 0 1 2.7 2.7V17h-2.6v5.5H8.1V17H5.5v-4.3A2.7 2.7 0 0 1 8.2 10Z',
    'house': 'M12 2 22.5 11h-3v11h-5.2v-6.5H9.7V22H4.5V11h-3Z',
    'building': 'M4 2h11v5h5v15H4Zm3 3v2h2V5Zm4 0v2h2V5ZM7 9v2h2V9Zm4 0v2h2V9Zm5 1v2h2v-2ZM7 13v2h2v-2Zm4 0v2h2v-2Zm5 1v2h2v-2ZM9 18v4h4v-4Z',
    'coin': 'M12 2a10 10 0 1 1 0 20 10 10 0 0 1 0-20Zm0 3.2a6.8 6.8 0 1 0 0 13.6 6.8 6.8 0 0 0 0-13.6Zm0 2.3a4.5 4.5 0 1 1 0 9 4.5 4.5 0 0 1 0-9Z',
    'banknote': 'M1.5 5.5h21v13h-21Zm3 2.5a2 2 0 0 1-1 1.7v4.6a2 2 0 0 1 1 1.7h15a2 2 0 0 1 1-1.7V9.7a2 2 0 0 1-1-1.7ZM12 8.6a3.4 3.4 0 1 1 0 6.8 3.4 3.4 0 0 1 0-6.8Z',
    'day': 'M3 4.5h18v17.5H3Zm2.5 5v10h13v-10ZM7 1.5h2.5v4.5H7Zm7.5 0H17v4.5h-2.5ZM8 12h3v3H8Z',
    'bag': 'M8 7V6a4 4 0 0 1 8 0v1h4.5l1 15h-19l1-15Zm2.4 0h3.2V6a1.6 1.6 0 0 0-3.2 0Z',
    'car': 'M5.5 6h13l2.5 6.2h1v6.3h-2.2a2.6 2.6 0 0 1-5.2 0H9.4a2.6 2.6 0 0 1-5.2 0H2v-6.3h1Zm1.8 2.4-1.5 3.8h12.4l-1.5-3.8Z',
    'bowl': 'M2 10.5h20a10 10 0 0 1-6 9.2V22H8v-2.3a10 10 0 0 1-6-9.2Zm5-7c1.6 1.5 0 3 1.4 5H7c-1.2-1.8.3-3.4-1.2-4.8Zm4.5-1c1.6 1.5 0 3.5 1.4 6h-1.6c-1.2-2.2.3-4-1.2-5.6Zm4.5 1c1.6 1.5 0 3 1.4 5h-1.4c-1.2-1.8.3-3.4-1.2-4.8Z',
    'bolt': 'M13.5 1.5 4 13.5h6.5L9 22.5 20 9.5h-6.6Z',
    'drop': 'M12 1.5s7.5 8.2 7.5 13a7.5 7.5 0 0 1-15 0c0-4.8 7.5-13 7.5-13Z',
    'tree': 'M12 1.5 19.5 12h-3l4 6h-7v4.5h-3V18h-7l4-6h-3Z',
    'box': 'M12 1.5 21.5 6v12L12 22.5 2.5 18V6Zm0 2.6L6.2 6.8 12 9.5l5.8-2.7Z',
    'plane': 'M10.5 2h3l.5 7.5 8 4.5v2.5l-8-2.2-.4 4.9 2.9 2.1V23L12 21.7 7.5 23v-1.7l2.9-2.1-.4-4.9-8 2.2V14l8-4.5Z',
    'train': 'M6 2h12a2.5 2.5 0 0 1 2.5 2.5v11A2.5 2.5 0 0 1 18 18h-.4l2.4 4h-2.8l-2.4-4H9.2l-2.4 4H4l2.4-4H6a2.5 2.5 0 0 1-2.5-2.5v-11A2.5 2.5 0 0 1 6 2Zm0 3v5h12V5Zm1.5 7.5a1.5 1.5 0 1 0 0 3 1.5 1.5 0 0 0 0-3Zm9 0a1.5 1.5 0 1 0 0 3 1.5 1.5 0 0 0 0-3Z',
    'square': 'M2 2h20v20H2Z',
    'circle': 'M12 2a10 10 0 1 1 0 20 10 10 0 0 1 0-20Z',
}


class Canvas:
    def __init__(self, W, layout='w', lang='en', pad=0):
        self.W, self.layout, self.lang = W, layout, lang
        self.narrow = layout == 'n'
        self.els, self.defs = [], []
        self.texts, self.marks, self.issues = [], [], []
        self.segs = []   # data line segments, so labels can keep off them
        self.minx = self.miny = 0.0
        self.maxx = float(W)
        self.maxy = 0.0
        self.H = None
        self._uid = 0
        self.idp = f'{layout}-'   # Figure sets a page-unique prefix; ids must never repeat on a page
        self.pad = pad

    # ── bookkeeping ────────────────────────────────────────────────────
    def uid(self, p='u'):
        self._uid += 1
        return f'{self.idp}{p}{self._uid}'

    def _extent(self, x0, y0, x1, y1):
        self.minx, self.miny = min(self.minx, x0), min(self.miny, y0)
        self.maxx, self.maxy = max(self.maxx, x1), max(self.maxy, y1)

    def add(self, s):
        self.els.append(s)

    @contextmanager
    def group(self, transform=None, cls=None, opacity=None, label=None):
        a = ''
        if transform:
            a += f' transform="{transform}"'
        if cls:
            a += f' class="{cls}"'
        if opacity is not None:
            a += f' opacity="{opacity}"'
        if label:
            a += f' aria-label="{esc(label)}"'
        self.add(f'<g{a}>')
        yield
        self.add('</g>')

    @staticmethod
    def style(fill=None, stroke=None, sw=None, dash=None, op=None, extra=''):
        s = []
        if fill is not None:
            s.append(f'fill:{paint(fill)}')
        if stroke is not None:
            s.append(f'stroke:{paint(stroke)}')
        if sw is not None:
            s.append(f'stroke-width:{_n(sw)}')
        if dash:
            s.append(f'stroke-dasharray:{dash}')
        if op is not None:
            s.append(f'opacity:{op}')
        if extra:
            s.append(extra)
        return f' style="{";".join(s)}"' if s else ''

    @staticmethod
    def _tip(tip):
        return f'<title>{esc(tip)}</title>' if tip else ''

    # ── shapes ─────────────────────────────────────────────────────────
    def rect(self, x, y, w, h, fill='base', stroke=None, sw=1, rx=0, tip=None, mark=True, op=None,
             dash=None):
        if w < 0:
            x, w = x + w, -w
        if h < 0:
            y, h = y + h, -h
        r = f' rx="{_n(rx)}"' if rx else ''
        st = self.style(fill, stroke, sw if stroke else None, dash, op)
        t = self._tip(tip)
        self.add(f'<rect x="{_n(x)}" y="{_n(y)}" width="{_n(w)}" height="{_n(h)}"{r}{st}>{t}</rect>'
                 if t else f'<rect x="{_n(x)}" y="{_n(y)}" width="{_n(w)}" height="{_n(h)}"{r}{st}/>')
        self._extent(x, y, x + w, y + h)
        if mark:
            self.marks.append((x, y, x + w, y + h))

    def bar(self, x, y, w, h, fill='base', round_end='right', r=3, tip=None):
        """A bar with only its free end rounded (the blog's bars: square at the baseline)."""
        if w <= 0 or h <= 0:
            return
        r = min(r, w / 2, h / 2)
        if round_end == 'right':
            d = f'M{_n(x)} {_n(y)}h{_n(w - r)}a{_n(r)} {_n(r)} 0 0 1 {_n(r)} {_n(r)}v{_n(h - 2 * r)}a{_n(r)} {_n(r)} 0 0 1 -{_n(r)} {_n(r)}h-{_n(w - r)}Z'
        elif round_end == 'top':
            d = f'M{_n(x)} {_n(y + h)}v-{_n(h - r)}a{_n(r)} {_n(r)} 0 0 1 {_n(r)} -{_n(r)}h{_n(w - 2 * r)}a{_n(r)} {_n(r)} 0 0 1 {_n(r)} {_n(r)}v{_n(h - r)}Z'
        elif round_end == 'bottom':
            d = f'M{_n(x)} {_n(y)}h{_n(w)}v{_n(h - r)}a{_n(r)} {_n(r)} 0 0 1 -{_n(r)} {_n(r)}h-{_n(w - 2 * r)}a{_n(r)} {_n(r)} 0 0 1 -{_n(r)} -{_n(r)}Z'
        elif round_end == 'left':
            d = f'M{_n(x + w)} {_n(y)}v{_n(h)}h-{_n(w - r)}a{_n(r)} {_n(r)} 0 0 1 -{_n(r)} -{_n(r)}v-{_n(h - 2 * r)}a{_n(r)} {_n(r)} 0 0 1 {_n(r)} -{_n(r)}Z'
        else:
            return self.rect(x, y, w, h, fill, tip=tip)
        self.path(d, fill=fill, tip=tip)
        self.marks.append((x, y, x + w, y + h))
        self._extent(x, y, x + w, y + h)

    def line(self, x1, y1, x2, y2, stroke='grid', sw=1, dash=None, cap='butt', op=None):
        st = self.style('none', stroke, sw, dash, op, f'stroke-linecap:{cap}' if cap != 'butt' else '')
        self.add(f'<line x1="{_n(x1)}" y1="{_n(y1)}" x2="{_n(x2)}" y2="{_n(y2)}"{st}/>')
        self._extent(min(x1, x2), min(y1, y2), max(x1, x2), max(y1, y2))

    def polyline(self, pts, stroke='s1', sw=2, fill='none', dash=None, join='round', cap='round',
                 op=None, cls=None, data=False):
        if len(pts) < 2:
            return
        if data:
            self.segs += list(zip(pts, pts[1:]))
        p = ' '.join(f'{_n(x)},{_n(y)}' for x, y in pts)
        st = self.style(fill, stroke, sw, dash, op, f'stroke-linejoin:{join};stroke-linecap:{cap}')
        c = f' class="{cls}"' if cls else ''
        self.add(f'<polyline points="{p}"{c}{st}/>')
        xs, ys = [q[0] for q in pts], [q[1] for q in pts]
        self._extent(min(xs), min(ys), max(xs), max(ys))

    def polygon(self, pts, fill='base', stroke=None, sw=1, op=None, tip=None, join='round'):
        p = ' '.join(f'{_n(x)},{_n(y)}' for x, y in pts)
        st = self.style(fill, stroke, sw if stroke else None, None, op,
                        f'stroke-linejoin:{join}' if stroke else '')
        t = self._tip(tip)
        self.add(f'<polygon points="{p}"{st}>{t}</polygon>' if t else f'<polygon points="{p}"{st}/>')
        xs, ys = [q[0] for q in pts], [q[1] for q in pts]
        self._extent(min(xs), min(ys), max(xs), max(ys))

    def path(self, d, fill='none', stroke=None, sw=1, dash=None, op=None, tip=None, cls=None,
             extra='', bbox=None):
        st = self.style(fill, stroke, sw if stroke else None, dash, op, extra)
        c = f' class="{cls}"' if cls else ''
        t = self._tip(tip)
        self.add(f'<path d="{d}"{c}{st}>{t}</path>' if t else f'<path d="{d}"{c}{st}/>')
        if bbox:
            self._extent(*bbox)

    def circle(self, cx, cy, r, fill='hl', stroke=None, sw=1.5, tip=None, op=None):
        st = self.style(fill, stroke, sw if stroke else None, None, op)
        t = self._tip(tip)
        self.add(f'<circle cx="{_n(cx)}" cy="{_n(cy)}" r="{_n(r)}"{st}>{t}</circle>' if t else
                 f'<circle cx="{_n(cx)}" cy="{_n(cy)}" r="{_n(r)}"{st}/>')
        self._extent(cx - r, cy - r, cx + r, cy + r)
        self.marks.append((cx - r, cy - r, cx + r, cy + r))

    # ── text ───────────────────────────────────────────────────────────
    def text(self, x, y, s, size=13, weight=400, fill='label', anchor='start', va='middle',
             halo=False, mono=False, max_w=None, lh=1.25, kind='label', check=True, italic=False,
             rotate=None, clamp=True):
        """Draw text; returns its box (x0, y0, x1, y1). `va` places the box: top, middle,
        bottom or baseline (of the first line). `max_w` wraps. kind: title, label, value,
        tick, note, axis, legend (for the checks)."""
        s = str(s)
        lines = metrics.wrap(s, max_w, size, weight, mono) if max_w else s.split('\n')
        w = max(metrics.width(l, size, weight, mono) for l in lines)
        h = size * lh * (len(lines) - 1) + size
        asc = size * 0.72   # cap height + a little: DM Sans' ascent above the baseline
        if va == 'top':
            y0 = y
        elif va == 'bottom':
            y0 = y - h
        elif va == 'baseline':
            y0 = y - asc
        else:
            y0 = y - h / 2
        base = y0 + asc + (size - asc) * 0.15
        x0 = x - (w / 2 if anchor == 'middle' else w if anchor == 'end' else 0)
        if clamp and not rotate:
            shift = max(0.0, -x0) - max(0.0, x0 + w - self.W)
            if shift:
                x += shift
                x0 += shift
        a = {'start': '', 'middle': ' text-anchor="middle"', 'end': ' text-anchor="end"'}[anchor]
        st = [f'fill:{paint(fill)}']
        if mono:
            st.append("font-family:'DM Mono',ui-monospace,monospace")
        if italic:
            st.append('font-style:italic')
        cls = ' class="halo"' if halo else ''
        tr = f' transform="rotate({_n(rotate)} {_n(x)} {_n(y)})"' if rotate else ''
        attrs = f'x="{_n(x)}" y="{_n(base)}" font-size="{_n(size)}"' + (
            f' font-weight="{weight}"' if weight != 400 else '') + a + cls + tr
        if len(lines) == 1:
            self.add(f'<text {attrs} style="{";".join(st)}">{esc(lines[0])}</text>')
        else:
            spans = ''.join(
                f'<tspan x="{_n(x)}" dy="{0 if i == 0 else _n(size * lh)}">{esc(l)}</tspan>'
                for i, l in enumerate(lines))
            self.add(f'<text {attrs} style="{";".join(st)}">{spans}</text>')
        box = (x0, y0, x0 + w, y0 + h)
        if rotate:
            cx, cy = x, y
            ang = math.radians(rotate)
            pts = [(bx, by) for bx in (box[0], box[2]) for by in (box[1], box[3])]
            rp = [(cx + (px - cx) * math.cos(ang) - (py - cy) * math.sin(ang),
                   cy + (px - cx) * math.sin(ang) + (py - cy) * math.cos(ang)) for px, py in pts]
            box = (min(p[0] for p in rp), min(p[1] for p in rp), max(p[0] for p in rp), max(p[1] for p in rp))
        self._extent(*box)
        if check:
            self.texts.append({'box': box, 'text': s, 'size': size, 'kind': kind, 'weight': weight})
        return box

    def hits(self, box, pad=3, marks=True, segs=True):
        """Does a box (inflated by pad) touch any text, mark or data line already drawn?"""
        b = (box[0] - pad, box[1] - pad, box[2] + pad, box[3] + pad)
        ov = lambda q: min(b[2], q[2]) > max(b[0], q[0]) and min(b[3], q[3]) > max(b[1], q[1])
        if any(ov(t['box']) for t in self.texts):
            return True
        if marks and any(ov(m) for m in self.marks):
            return True
        if segs:
            for (x1, y1), (x2, y2) in self.segs:
                if seg_box(x1, y1, x2, y2, b):
                    return True
        return False

    def measure(self, s, size=13, weight=400, mono=False):
        return metrics.width(s, size, weight, mono)

    def rich(self, x, y, parts, size=13, anchor='start', va='middle', halo=False, kind='label'):
        """One line in several styles: parts = [(text, weight, fill), ...]."""
        ws = [metrics.width(t, size, wt) for t, wt, _ in parts]
        total = sum(ws)
        x0 = x - (total / 2 if anchor == 'middle' else total if anchor == 'end' else 0)
        cx = x0
        boxes = []
        for (t, wt, fl), w in zip(parts, ws):
            boxes.append(self.text(cx, y, t, size, wt, fl, 'start', va, halo, kind=kind, check=False))
            cx += w
        box = (x0, min(b[1] for b in boxes), x0 + total, max(b[3] for b in boxes))
        self.texts.append({'box': box, 'text': ''.join(p[0] for p in parts), 'size': size, 'kind': kind,
                           'weight': 400})
        return box

    # ── pictures ───────────────────────────────────────────────────────
    def flag(self, code, x, y, h=12, tip=None):
        """A country flag (4:3) by ISO 3166 alpha-3 code ('IDN'), or EUU/ASEAN/UNO, with a hairline
        border so white flags still show on a white card. Returns the right edge."""
        code = code.upper()
        c = countries().get(code)
        if not c:
            raise KeyError(f'no flag for {code!r}; use an ISO 3166 alpha-3 code (assets/countries.json)')
        w = h * 4 / 3
        cid = self.uid('fc')
        self.defs.append(f'<clipPath id="{cid}"><rect x="{_n(x)}" y="{_n(y)}" width="{_n(w)}" height="{_n(h)}" rx="2"/></clipPath>')
        t = self._tip(tip or c['name'])
        self.add(f'<image href="/assets/img/flags/{code.lower()}.svg" x="{_n(x)}" y="{_n(y)}" width="{_n(w)}" '
                 f'height="{_n(h)}" preserveAspectRatio="xMidYMid slice" clip-path="url(#{cid})">{t}</image>')
        self.rect(x + 0.3, y + 0.3, w - 0.6, h - 0.6, fill='none', stroke='axis', sw=0.6, rx=2, mark=False)
        self._extent(x, y, x + w, y + h)
        return x + w

    def icon(self, name, x, y, size=24, color='label', sw=2, fill_color=None, tip=None):
        """A Lucide outline icon (scripts/icons.py --search) or a solid glyph from GLYPHS, drawn in
        the box (x, y, size, size). Outline icons keep a 2px line at 24px, scaled with the icon."""
        k = size / 24
        t = self._tip(tip)
        if name in GLYPHS:
            self.add(f'<path transform="translate({_n(x)} {_n(y)}) scale({k:.4f})" d="{GLYPHS[name]}" '
                     f'style="fill:{paint(fill_color or color)};fill-rule:evenodd">{t}</path>')
        else:
            inner = icon_markup(name)
            self.add(f'<g transform="translate({_n(x)} {_n(y)}) scale({k:.4f})" style="fill:none;'
                     f'stroke:{paint(color)};stroke-width:{sw};stroke-linecap:round;stroke-linejoin:round">'
                     f'{t}{inner}</g>')
        self._extent(x, y, x + size, y + size)
        self.marks.append((x, y, x + size, y + size))

    # ── annotation (ported from MM-ify: right-angled leaders, open 90-degree arrowheads) ──
    def arrow(self, pts, stroke='label', sw=1.5, head='end', size=7, dash=None, cls=None):
        """Polyline with open 90-degree arrowhead(s) joined to the stem."""
        self.polyline(pts, stroke=stroke, sw=sw, dash=dash, join='miter', cap='butt', cls=cls)
        ends = []
        if head in ('end', 'both'):
            ends.append((pts[-1], pts[-2]))
        if head in ('start', 'both'):
            ends.append((pts[0], pts[1]))
        for tip, prev in ends:
            dx, dy = tip[0] - prev[0], tip[1] - prev[1]
            L = math.hypot(dx, dy) or 1
            ux, uy = dx / L, dy / L
            a = (tip[0] - size * (ux - uy) * 0.7071 * 1.0, tip[1] - size * (uy + ux) * 0.7071)
            b = (tip[0] - size * (ux + uy) * 0.7071, tip[1] - size * (uy - ux) * 0.7071)
            self.polyline([a, tip, b], stroke=stroke, sw=sw, join='miter', cap='butt')

    def leader(self, anchor, to, stroke='label', sw=1, route='hv', dot=True):
        """A thin right-angled pointer line from a data point to its label (route 'hv': across
        then down, 'vh': down then across, 'straight')."""
        (ax, ay), (tx, ty) = anchor, to
        if route == 'hv':
            pts = [(ax, ay), (tx, ay), (tx, ty)] if abs(tx - ax) > 0.5 and abs(ty - ay) > 0.5 else [(ax, ay), (tx, ty)]
        elif route == 'vh':
            pts = [(ax, ay), (ax, ty), (tx, ty)] if abs(tx - ax) > 0.5 and abs(ty - ay) > 0.5 else [(ax, ay), (tx, ty)]
        else:
            pts = [(ax, ay), (tx, ty)]
        self.polyline(pts, stroke=stroke, sw=sw, join='miter', cap='butt')
        if dot:
            self.circle(ax, ay, 2.2, fill=stroke)
            self.marks.pop()

    def callout(self, anchor, at, text, size=13, weight=400, fill='ink', anchor_text='start',
                max_w=170, route='hv', head=None, stroke='label', va='middle', halo=True):
        """Label a point: a pointer line from `anchor` to `at` and the note beside it. `head` may
        hold a bold first line (the what) above the body (the why)."""
        self.leader(anchor, at, stroke=stroke, route=route)
        gap = 5
        tx = at[0] + (gap if anchor_text == 'start' else -gap if anchor_text == 'end' else 0)
        if head:
            b1 = self.text(tx, at[1], head, size, 700, fill, anchor_text, 'bottom' if va == 'middle' else va,
                           halo=halo, max_w=max_w, kind='note')
            b2 = self.text(tx, b1[3] + 1, text, size - 0.5, weight, 'label', anchor_text, 'top', halo=halo,
                           max_w=max_w, kind='note')
            return (min(b1[0], b2[0]), b1[1], max(b1[2], b2[2]), b2[3])
        return self.text(tx, at[1], text, size, weight, fill, anchor_text, va, halo=halo, max_w=max_w,
                         kind='note')

    def bracket(self, x, y0, y1, side='right', tick=6, stroke='label', sw=1):
        d = tick if side == 'right' else -tick
        self.polyline([(x - d, y0), (x, y0), (x, y1), (x - d, y1)], stroke=stroke, sw=sw, join='miter', cap='butt')

    def hbracket(self, x0, x1, y, side='top', tick=6, stroke='label', sw=1):
        d = tick if side == 'top' else -tick
        self.polyline([(x0, y + d), (x0, y), (x1, y), (x1, y + d)], stroke=stroke, sw=sw, join='miter', cap='butt')

    def box(self, x, y, w, h, text=None, fill='node', stroke='node-line', corners='rrrr', r=8, size=13,
            weight=500, color='ink', sw=1.2, align=None, pad=10, tip=None):
        """A text container (MM-ify's brand shape on the blog's corners). corners: one letter per
        corner from top-left clockwise: r round, s square, c 45-degree chamfer. Text is centred
        when it fits on 3 lines or fewer, else left-aligned (MM rule), always vertically centred."""
        d = shape_path(x, y, w, h, corners, r)
        self.path(d, fill=fill, stroke=stroke, sw=sw, tip=tip, bbox=(x, y, x + w, y + h))
        self.marks.append((x, y, x + w, y + h))
        if text:
            lines = metrics.wrap(text, w - 2 * pad, size, weight)
            al = align or ('middle' if len(lines) <= 3 else 'start')
            tx = x + w / 2 if al == 'middle' else x + pad
            self.text(tx, y + h / 2, '\n'.join(lines), size, weight, color, al, 'middle', kind='label')

    # ── output ─────────────────────────────────────────────────────────
    def svg(self, cls, title, desc, pad=2):
        H = self.H if self.H is not None else self.maxy + pad
        if self.minx < -0.5 or self.maxx > self.W + 0.5 or self.miny < -0.5:
            self.issues.append(('ERROR', f'drawing leaves the frame: x {self.minx:.0f}..{self.maxx:.0f} of 0..{self.W}, '
                                         f'top {self.miny:.0f}'))
        defs = f'<defs>{"".join(self.defs)}</defs>' if self.defs else ''
        tid, did = f'{cls}-t', f'{cls}-d'
        return (f'<svg class="{cls}" viewBox="0 0 {_n(self.W)} {_n(H)}" width="{_n(self.W)}" height="{_n(H)}" '
                f'role="img" aria-labelledby="{tid} {did}" xmlns="http://www.w3.org/2000/svg">'
                f'<title id="{tid}">{esc(title)}</title><desc id="{did}">{esc(desc)}</desc>{defs}'
                + ''.join(self.els) + '</svg>')


def shape_path(x, y, w, h, corners='rrrr', r=8):
    """Rectangle with each corner round (r), square (s) or chamfered (c), clockwise from top-left."""
    r = min(r, w / 2, h / 2)
    c = (corners + 'rrrr')[:4]
    pts = []

    def corner(kind, px, py, ax, ay, bx, by):
        # (px, py) is the corner; a is the incoming direction, b the outgoing.
        if kind == 's':
            return f'L{_n(px)} {_n(py)}'
        if kind == 'c':
            return f'L{_n(px - ax * r)} {_n(py - ay * r)}L{_n(px + bx * r)} {_n(py + by * r)}'
        return (f'L{_n(px - ax * r)} {_n(py - ay * r)}Q{_n(px)} {_n(py)} {_n(px + bx * r)} {_n(py + by * r)}')

    d = f'M{_n(x + (0 if c[0] == "s" else r))} {_n(y)}'
    d += corner(c[1], x + w, y, 1, 0, 0, 1)
    d += corner(c[2], x + w, y + h, 0, 1, -1, 0)
    d += corner(c[3], x, y + h, -1, 0, 0, -1)
    d += corner(c[0], x, y, 0, -1, 1, 0)
    return d + 'Z'


def seg_box(x1, y1, x2, y2, b):
    """Does the segment cross the box (x0, y0, x1, y1)? Liang-Barsky clipping."""
    dx, dy = x2 - x1, y2 - y1
    t0, t1 = 0.0, 1.0
    for p, q in ((-dx, x1 - b[0]), (dx, b[2] - x1), (-dy, y1 - b[1]), (dy, b[3] - y1)):
        if p == 0:
            if q < 0:
                return False
        else:
            r = q / p
            if p < 0:
                t0 = max(t0, r)
            else:
                t1 = min(t1, r)
            if t0 > t1:
                return False
    return True
