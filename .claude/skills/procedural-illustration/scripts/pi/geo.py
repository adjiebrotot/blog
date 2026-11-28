"""Maps drawn from vendored geodata: the world (Natural Earth via world-atlas), provinces and
states of 14 countries, and 4,000 cities. No tiles, no network. See subskills/geo/SKILL.md.

    Map(base='admin1:CHN', projection='albers', highlight={'CN-BJ': 'hl', ...},
        labels=[{'id': 'CN-BJ', 'text': {'en': 'Beijing'}}], context='world-50m')

base: 'world-110m' | 'world-50m' | 'admin1:<ISO3>' | a path to a GeoJSON file.
ids: world features use ISO alpha-3 ('IDN'); admin1 features use ISO 3166-2 ('ID-JK', 'CN-SH');
     `Map.ids('admin1:IDN')` lists them with names.
highlight: {id: role} paints regions; `values` + `bins` makes a choropleth (sequential `seq1..5`
     or diverging `div1..5` ramp) with its key drawn under the map (a choropleth needs a key).
context: a second, quieter base drawn underneath (neighbouring countries around a province map).
points: [{'lonlat': (lon, lat) | 'city': 'Surabaya', 'label': ..., 'role': 'hl', 'r': 4}]
routes: [{'from': (lon, lat) | city, 'to': ..., 'role': 'a', 'dashed': False, 'bend': 0.2}]
bounds: (lon0, lat0, lon1, lat1) to crop; default: the extent of the highlighted or base features.
add: [('world-50m', ['HKG', 'MAC'])] draws features of another base as regions of this one
     (Natural Earth keeps Hong Kong, Macau and Taiwan out of China's admin-1 file).
"""
import json, math, os

from .figure import Component, tr
from .charts2d import TICK, LABEL, make_fmt
from . import metrics, fmt as F

GEO = os.path.join(os.path.dirname(__file__), '..', '..', 'assets', 'geo')
_cache = {}


# ── data ───────────────────────────────────────────────────────────────────
def _topo_features(topo, obj):
    t = topo.get('transform')
    arcs = []
    for arc in topo['arcs']:
        x = y = 0
        pts = []
        for p in arc:
            if t:
                x += p[0]
                y += p[1]
                pts.append((x * t['scale'][0] + t['translate'][0], y * t['scale'][1] + t['translate'][1]))
            else:
                pts.append(tuple(p))
        arcs.append(pts)

    def ring(idx):
        out = []
        for i in idx:
            a = arcs[i] if i >= 0 else arcs[~i][::-1]
            out += a if not out else a[1:]
        return out

    feats = []
    for g in topo['objects'][obj]['geometries']:
        if g['type'] == 'Polygon':
            polys = [[ring(r) for r in g['arcs']]]
        elif g['type'] == 'MultiPolygon':
            polys = [[ring(r) for r in p] for p in g['arcs']]
        else:
            continue
        feats.append({'id': g.get('id'), 'properties': g.get('properties', {}), 'polys': polys})
    return feats


def load(base):
    if base in _cache:
        return _cache[base]
    if base.startswith('world-'):
        topo = json.load(open(os.path.join(GEO, base + '.json')))
        feats = _topo_features(topo, 'countries')
        cs = json.load(open(os.path.join(GEO, '..', 'countries.json'), encoding='utf-8'))
        by_n3 = {v['n3']: k for k, v in cs.items() if v.get('n3')}
        by_name = {v['name']: k for k, v in cs.items()}
        for f in feats:
            f['id'] = by_n3.get(f['id']) or by_name.get(f['properties'].get('name')) or f['properties'].get('name')
            f['properties']['label'] = cs.get(f['id'], {}).get('label')
    else:
        path = os.path.join(GEO, f'admin1-{base.split(":")[1]}.json') if base.startswith('admin1:') else base
        gj = json.load(open(path, encoding='utf-8'))
        feats = []
        for f in gj['features']:
            g = f['geometry']
            polys = g['coordinates'] if g['type'] == 'MultiPolygon' else [g['coordinates']]
            feats.append({'id': f.get('id') or f['properties'].get('code'), 'properties': f['properties'],
                          'polys': [[[tuple(p) for p in r] for r in poly] for poly in polys]})
    _cache[base] = feats
    return feats


def cities():
    if 'cities' not in _cache:
        d = json.load(open(os.path.join(GEO, 'cities.json'), encoding='utf-8'))
        _cache['cities'] = [dict(zip(d['fields'], r)) for r in d['rows']]
    return _cache['cities']


def city(name, iso3=None):
    for c in cities():
        if c['name'].lower() == name.lower() and (not iso3 or c['iso3'] == iso3):
            return c
    raise KeyError(f'no city {name!r} in assets/geo/cities.json (100k+ people or a capital)')


# ── projections (lon, lat in degrees -> x, y, y down) ──────────────────────
def projection(kind, lon0=0.0, lat0=0.0, parallels=(25.0, 47.0)):
    r = math.radians
    if kind == 'mercator':
        return lambda lo, la: (r(lo - lon0), -math.log(math.tan(math.pi / 4 + r(max(-85, min(85, la))) / 2)))
    if kind == 'equirect':
        k = math.cos(r(lat0))
        return lambda lo, la: (r(lo - lon0) * k, -r(la))
    if kind == 'equal-earth':
        A1, A2, A3, A4 = 1.340264, -0.081106, 0.000893, 0.003796
        M = math.sqrt(3) / 2

        def ee(lo, la):
            l, p = r(lo - lon0), r(la)
            th = math.asin(M * math.sin(p))
            t2 = th * th
            t6 = t2 * t2 * t2
            x = 2 * math.sqrt(3) * l * math.cos(th) / (3 * (9 * A4 * t6 * t2 + 7 * A3 * t6 + 3 * A2 * t2 + A1))
            y = th * (A1 + A2 * t2 + t6 * (A3 + A4 * t2))
            return x, -y
        return ee
    if kind in ('albers', 'lambert'):
        p1, p2 = r(parallels[0]), r(parallels[1])
        n = (math.sin(p1) + math.sin(p2)) / 2
        C = math.cos(p1) ** 2 + 2 * n * math.sin(p1)
        rho0 = math.sqrt(C - 2 * n * math.sin(r(lat0))) / n

        def al(lo, la):
            th = n * r(lo - lon0)
            rho = math.sqrt(max(0.0, C - 2 * n * math.sin(r(la)))) / n
            return rho * math.sin(th), -(rho0 - rho * math.cos(th))
        return al
    raise ValueError(f'unknown projection {kind}')


def _bbox_ll(feats):
    xs, ys = [], []
    for f in feats:
        for poly in f['polys']:
            for p in poly[0]:
                xs.append(p[0])
                ys.append(p[1])
    return min(xs), min(ys), max(xs), max(ys)


def _area(ring):
    a = 0
    for (x1, y1), (x2, y2) in zip(ring, ring[1:] + ring[:1]):
        a += x1 * y2 - x2 * y1
    return a / 2


class Map(Component):
    def __init__(self, base='world-110m', projection='mercator', highlight=None, values=None, bins=None,
                 ramp='seq', value_fmt=None, labels=(), points=(), routes=(), context=None, bounds=None,
                 lon0=None, lat0=None, parallels=None, height=None, key=None, only=None, pad=0.04,
                 drop_small=0.6, add=()):
        self.base, self.proj_kind = base, projection
        self.highlight, self.values, self.bins, self.ramp = highlight or {}, values, bins, ramp
        self.vfmt = make_fmt(value_fmt, list((values or {}).values()))
        self.labels, self.points, self.routes = list(labels), list(points), list(routes)
        self.context, self.bounds, self.height, self.key, self.only = context, bounds, height, key, only
        self.lon0, self.lat0, self.parallels, self.pad, self.drop_small = lon0, lat0, parallels, pad, drop_small
        self.add = list(add)   # [('world-50m', ['HKG', 'MAC'])]: features of another base drawn as part of this one

    @staticmethod
    def ids(base):
        return [(f['id'], f['properties'].get('name')) for f in load(base)]

    def table(self, lang):
        if self.values:
            names = {f['id']: f['properties'].get('name') for f in load(self.base)}
            return ['', ''], [[names.get(k, k), self.vfmt(v, lang)] for k, v in
                              sorted(self.values.items(), key=lambda kv: -kv[1])]
        return None

    def _ll(self, p):
        if isinstance(p, str):
            c = city(p)
            return c['lon'], c['lat']
        if isinstance(p, dict):
            c = city(p['city'], p.get('iso3'))
            return c['lon'], c['lat']
        return p

    def draw(self, c, lang, y0):
        L = c.layout
        feats = list(load(self.base))
        for base, ids in self.add:
            feats += [f for f in load(base) if f['id'] in ids]
        if self.only:
            feats = [f for f in feats if f['id'] in self.only]
        b = self.bounds or _bbox_ll([f for f in feats if f['id'] in self.highlight] or feats)
        lon0 = self.lon0 if self.lon0 is not None else (b[0] + b[2]) / 2
        lat0 = self.lat0 if self.lat0 is not None else (b[1] + b[3]) / 2
        par = self.parallels or (b[1] + (b[3] - b[1]) / 6, b[3] - (b[3] - b[1]) / 6)
        P = projection(self.proj_kind, lon0, lat0, par)
        # fit the bounds to the width; height follows the shape (capped)
        corners = [P(lo, la) for lo in (b[0], (b[0] + b[2]) / 2, b[2]) for la in (b[1], (b[1] + b[3]) / 2, b[3])]
        x0, x1 = min(p[0] for p in corners), max(p[0] for p in corners)
        yA, yB = min(p[1] for p in corners), max(p[1] for p in corners)
        padx, pady = (x1 - x0) * self.pad, (yB - yA) * self.pad
        x0, x1, yA, yB = x0 - padx, x1 + padx, yA - pady, yB + pady
        Wd = c.W
        maxh = (self.height or {}).get(L) if isinstance(self.height, dict) else self.height
        maxh = maxh or (480 if L == 'w' else 380)
        k = min(Wd / (x1 - x0), maxh / (yB - yA))
        mw, mh = (x1 - x0) * k, (yB - yA) * k
        ox, oy = (Wd - mw) / 2, y0
        proj = lambda lo, la: (ox + (P(lo, la)[0] - x0) * k, oy + (P(lo, la)[1] - yA) * k)
        self._proj = proj
        clip = c.uid('mc')
        c.defs.append(f'<clipPath id="{clip}"><rect x="{ox:.1f}" y="{oy:.1f}" width="{mw:.1f}" height="{mh:.1f}"/></clipPath>')
        c.add(f'<g clip-path="url(#{clip})">')
        if self.context:
            ctx = load(self.context)
            d = self._paths(ctx, proj, (ox, oy, ox + mw, oy + mh))
            c.path(d, fill='land-ctx', stroke='bg', sw=0.6, extra='stroke-linejoin:round')
        # regions: grouped by paint so the output stays small
        groups = {}
        bins = self.bins
        for f in feats:
            role = self.highlight.get(f['id'])
            if role is None and self.values is not None:
                v = self.values.get(f['id'])
                if v is not None:
                    i = sum(1 for t in bins if v >= t)
                    role = f'{self.ramp}{min(5, i + 1)}' if self.ramp == 'seq' else f'div{min(5, i + 1)}'
            groups.setdefault(role or 'land', []).append(f)
        view = (ox, oy, ox + mw, oy + mh)
        for role in sorted(groups, key=lambda r: r != 'land'):
            d = self._paths(groups[role], proj, view, keep_small=(role != 'land'))
            c.path(d, fill=role, stroke='land-line', sw=0.9 if role != 'land' else 0.7, extra='stroke-linejoin:round')
        c.add('</g>')
        c._extent(ox, oy, ox + mw, oy + mh)
        # routes, points, labels
        for rt in self.routes:
            a, bb = proj(*self._ll(rt['from'])), proj(*self._ll(rt['to']))
            bend = rt.get('bend', 0.18)
            mx, my = (a[0] + bb[0]) / 2, (a[1] + bb[1]) / 2
            dx, dy = bb[0] - a[0], bb[1] - a[1]
            cxp, cyp = mx - dy * bend, my + dx * bend
            pts = [((1 - t) ** 2 * a[0] + 2 * (1 - t) * t * cxp + t * t * bb[0],
                    (1 - t) ** 2 * a[1] + 2 * (1 - t) * t * cyp + t * t * bb[1]) for t in [i / 24 for i in range(25)]]
            c.arrow(pts, stroke=rt.get('role', 'a'), sw=1.8, dash='5 4' if rt.get('dashed') else None,
                    head='end' if rt.get('arrow', True) else None)
        for pt in self.points:
            x, y = proj(*self._ll(pt.get('lonlat') or pt.get('city')))
            role = pt.get('role', 'ink')
            c.circle(x, y, pt.get('r', 3.5), fill=role, stroke='bg', sw=1.2)
        from .charts2d import place
        for pt in self.points:
            if not pt.get('label'):
                continue
            x, y = proj(*self._ll(pt.get('lonlat') or pt.get('city')))
            role = pt.get('role', 'ink')
            place(c, x, y, tr(pt['label'], lang), LABEL[L] - (0.5 if L == 'n' else 0), 600 if role == 'hl' else 500,
                  'ink', prefs=pt.get('prefs', ('right', 'left', 'above', 'below', 'above-right', 'below-right')),
                  gap=6, halo=True, avoid_marks=False, kind='label')
        byid = {f['id']: f for f in feats}
        pending = []
        for lb in self.labels:
            if lb.get('lonlat'):
                ll = lb['lonlat']
            else:
                f = byid[lb['id']]
                ll = f['properties'].get('label') or self._centroid(f)
            x, y = proj(*ll)
            text = tr(lb['text'], lang)
            size = lb.get('size', LABEL[L] - (0.5 if L == 'n' else 0))
            w = metrics.width(text, size, 600)
            box = (x - w / 2, y - size / 2, x + w / 2, y + size / 2)
            if lb.get('callout') or c.hits(box, 2, marks=False, segs=False) or box[0] < 0 or box[2] > c.W:
                pending.append((x, y, text, size, lb))
            else:
                c.text(x, y, text, size, 600, 'ink', 'middle', 'middle', halo=True, kind='label')
        for x, y, text, size, lb in pending:   # crowded: try around the point, with a pointer line
            prefs = lb.get('prefs', ('right', 'left', 'above', 'below', 'above-right', 'below-right',
                                     'above-left', 'below-left'))
            from .charts2d import place as _p
            bx = _p(c, x, y, text, size, 600, 'ink', prefs=prefs, gap=lb.get('gap', 14), halo=True,
                    avoid_marks=False, kind='label')
            tx = bx[0] if bx[0] > x else bx[2] if bx[2] < x else (bx[0] + bx[2]) / 2
            ty = (bx[1] + bx[3]) / 2 if (bx[0] > x or bx[2] < x) else (bx[3] if bx[3] < y else bx[1])
            c.line(x, y, tx + (-2 if tx > x else 2 if tx < x else 0), ty, stroke='ink', sw=0.9)
            c.circle(x, y, 2, fill='ink')
            c.marks.pop()
        if self.values is not None and self.bins:
            self._key(c, lang, oy + mh + 12)
        return c.maxy + 2

    def _centroid(self, f):
        best = max((poly[0] for poly in f['polys']), key=lambda r: abs(_area(r)))
        a = _area(best) or 1e-9
        cx = sum((x1 + x2) * (x1 * y2 - x2 * y1) for (x1, y1), (x2, y2) in zip(best, best[1:] + best[:1])) / (6 * a)
        cy = sum((y1 + y2) * (x1 * y2 - x2 * y1) for (x1, y1), (x2, y2) in zip(best, best[1:] + best[:1])) / (6 * a)
        return cx, cy

    def _paths(self, feats, proj, view, keep_small=False):
        out = []
        vx0, vy0, vx1, vy1 = view
        for f in feats:
            for poly in f['polys']:
                for ri, ring in enumerate(poly):
                    pts = []
                    for lo, la in ring:
                        x, y = proj(lo, la)
                        if not pts or abs(x - pts[-1][0]) + abs(y - pts[-1][1]) > 0.45:
                            pts.append((x, y))
                    if len(pts) < 3:
                        continue
                    xs, ys = [p[0] for p in pts], [p[1] for p in pts]
                    if max(xs) < vx0 - 5 or min(xs) > vx1 + 5 or max(ys) < vy0 - 5 or min(ys) > vy1 + 5:
                        continue
                    if not keep_small and (max(xs) - min(xs)) < self.drop_small and (max(ys) - min(ys)) < self.drop_small:
                        continue
                    if any(abs(b[0] - a[0]) > (vx1 - vx0) * 0.5 for a, b in zip(pts, pts[1:])):
                        continue  # a ring that wraps the antimeridian would streak across the map
                    out.append('M' + 'L'.join(f'{x:.1f} {y:.1f}' for x, y in pts) + 'Z')
        return ''.join(out)

    def _key(self, c, lang, y):
        L = c.layout
        n = len(self.bins) + 1
        w = min(52 if L == 'w' else (c.W - 8) / n, 60)
        for i in range(n):
            role = f'{self.ramp}{min(5, i + 1)}'
            c.rect(i * w, y, w - 2, 10, fill=role, mark=False)
        for i, t in enumerate(self.bins):
            c.text((i + 1) * w - 1, y + 16, self.vfmt(t, lang), TICK[L], 400, 'label', 'middle', 'top', kind='tick')
        if self.key:
            c.text(n * w + 10 if L == 'w' else 0, y + 5 if L == 'w' else y + 36, tr(self.key, lang), TICK[L], 400,
                   'label', 'start', 'middle' if L == 'w' else 'top', kind='legend')
