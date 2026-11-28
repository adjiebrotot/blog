#!/usr/bin/env python3
"""Rebuild the vendored assets of the procedural-illustration skill.

Run only to refresh or extend them; the results are committed, so a normal figure never
needs the network. Downloads go to a cache folder (default: $PI_CACHE or ~/.cache/pi).

    python3 build_assets.py all                 # everything below
    python3 build_assets.py flags               # assets/img/flags/<iso3>.svg in the blog (flag-icons, MIT)
    python3 build_assets.py icons               # assets/icons.json (Lucide, ISC)
    python3 build_assets.py world               # assets/geo/world-110m.json, world-50m.json (world-atlas, ISC; Natural Earth, public domain)
    python3 build_assets.py countries           # assets/countries.json (ISO codes, names, regions, label points)
    python3 build_assets.py cities              # assets/geo/cities.json (Natural Earth populated places)
    python3 build_assets.py admin1 IDN CHN ...  # assets/geo/admin1-<ISO3>.json (Natural Earth 10m states/provinces, simplified)

Sources and licences: references/assets.md.
"""
import io, json, math, os, re, shutil, subprocess, sys, tarfile, urllib.request

SKILL = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BLOG = os.path.abspath(os.path.join(SKILL, '..', '..', '..'))
ASSETS = os.path.join(SKILL, 'assets')
CACHE = os.environ.get('PI_CACHE', os.path.expanduser('~/.cache/pi'))
NE = 'https://raw.githubusercontent.com/nvkelso/natural-earth-vector/master/geojson/'
ADMIN1_DEFAULT = ['IDN', 'CHN', 'AUS', 'MYS', 'JPN', 'KOR', 'USA', 'IND', 'VNM', 'THA', 'PHL',
                  'CAN', 'NZL', 'DEU']


def fetch(url, name=None):
    os.makedirs(CACHE, exist_ok=True)
    path = os.path.join(CACHE, name or url.rsplit('/', 1)[-1])
    if not os.path.exists(path):
        print('  fetching', url)
        with urllib.request.urlopen(url, timeout=600) as r, open(path, 'wb') as f:
            shutil.copyfileobj(r, f)
    return path


def npm_package(name, version):
    """Download an npm tarball and return the folder it unpacks to."""
    url = f'https://registry.npmjs.org/{name}/-/{name.split("/")[-1]}-{version}.tgz'
    tgz = fetch(url)
    out = os.path.join(CACHE, f'{name.replace("/", "_")}-{version}')
    if not os.path.isdir(out):
        with tarfile.open(tgz) as t:
            t.extractall(out, filter='data')
    return os.path.join(out, 'package')


def ne(name):
    return json.load(open(fetch(NE + name + '.geojson')))


# ── ISO codes ──────────────────────────────────────────────────────────────
def iso_table():
    """iso2 -> iso3 and per-country facts from Natural Earth admin-0 (50m)."""
    rows = {}
    for f in ne('ne_50m_admin_0_countries')['features']:
        p = f['properties']
        a2 = p['ISO_A2'] if p['ISO_A2'] != '-99' else p['ISO_A2_EH']
        a3 = p['ISO_A3'] if p['ISO_A3'] != '-99' else p['ISO_A3_EH']
        if a3 == '-99':
            a3 = p['ADM0_A3']
        if a2 == '-99':
            a2 = None
        rows[a3] = {
            'iso2': a2, 'iso3': a3, 'n3': None if p['ISO_N3_EH'] == '-99' else p['ISO_N3_EH'],
            'name': p['NAME'], 'name_long': p['NAME_LONG'], 'continent': p['CONTINENT'],
            'region': p['REGION_UN'], 'subregion': p['SUBREGION'],
            'income': p['INCOME_GRP'], 'label': [round(p['LABEL_X'], 3), round(p['LABEL_Y'], 3)],
            'ne_a3': p['ADM0_A3'],
        }
    return rows


def build_countries():
    rows = iso_table()
    # Groups the flag set draws, kept beside the countries so a chart can flag a bloc row.
    rows['EUU'] = {'iso2': 'eu', 'iso3': 'EUU', 'name': 'European Union', 'group': True}
    rows['ASEAN'] = {'iso2': 'asean', 'iso3': 'ASEAN', 'name': 'ASEAN', 'group': True}
    rows['UNO'] = {'iso2': 'un', 'iso3': 'UNO', 'name': 'United Nations', 'group': True}
    out = os.path.join(ASSETS, 'countries.json')
    json.dump(dict(sorted(rows.items())), open(out, 'w'), ensure_ascii=False, separators=(',', ':'))
    print('countries.json', len(rows))


def build_flags():
    pkg = npm_package('flag-icons', '7.6.0')
    rows = json.load(open(os.path.join(ASSETS, 'countries.json'))) if os.path.exists(
        os.path.join(ASSETS, 'countries.json')) else iso_table()
    by2 = {r['iso2'].lower(): k for k, r in rows.items() if r.get('iso2')}
    extra = {'gb-eng': 'GB-ENG', 'gb-sct': 'GB-SCT', 'gb-wls': 'GB-WLS', 'gb-nir': 'GB-NIR', 'xk': 'XKX'}
    dst = os.path.join(BLOG, 'assets', 'img', 'flags')
    os.makedirs(dst, exist_ok=True)
    n = 0
    for fn in sorted(os.listdir(os.path.join(pkg, 'flags', '4x3'))):
        code = fn[:-4]
        iso3 = by2.get(code) or extra.get(code)
        if not iso3:
            continue
        svg = open(os.path.join(pkg, 'flags', '4x3', fn), encoding='utf-8').read()
        svg = re.sub(r'<\?xml[^>]*>\s*', '', svg)
        svg = re.sub(r'<!--.*?-->', '', svg, flags=re.S)
        svg = re.sub(r'>\s+<', '><', svg).strip()
        open(os.path.join(dst, iso3.lower() + '.svg'), 'w', encoding='utf-8').write(svg)
        n += 1
    shutil.copy(os.path.join(pkg, 'LICENSE'), os.path.join(dst, 'LICENSE.txt'))
    print('flags', n, '->', dst)


def build_icons():
    pkg = npm_package('lucide-static', '1.82.0')
    nodes = json.load(open(os.path.join(pkg, 'icon-nodes.json')))
    tags = json.load(open(os.path.join(pkg, 'tags.json')))
    out = {}
    for name, items in nodes.items():
        parts = []
        for tag, attrs in items:
            a = ' '.join(f'{k}="{v}"' for k, v in attrs.items() if k != 'key')
            parts.append(f'<{tag} {a}/>')
        out[name] = ''.join(parts)
    json.dump({'_license': 'Lucide, ISC licence (references/assets.md)', 'icons': out,
               'tags': {k: v for k, v in tags.items() if k in out}},
              open(os.path.join(ASSETS, 'icons.json'), 'w'), separators=(',', ':'))
    shutil.copy(os.path.join(pkg, 'LICENSE'), os.path.join(ASSETS, 'LICENSE-lucide.txt'))
    print('icons', len(out))


def build_world():
    pkg = npm_package('world-atlas', '2.0.2')
    for res in ('110m', '50m'):
        shutil.copy(os.path.join(pkg, f'countries-{res}.json'), os.path.join(ASSETS, 'geo', f'world-{res}.json'))
    shutil.copy(os.path.join(pkg, 'LICENSE'), os.path.join(ASSETS, 'geo', 'LICENSE-world-atlas.txt'))
    print('world-110m.json, world-50m.json')


def build_cities():
    rows = []
    for f in ne('ne_10m_populated_places_simple')['features']:
        p = f['properties']
        cap = 2 if p['adm0cap'] else (1 if p['featurecla'] == 'Admin-1 capital' else 0)
        if p['pop_max'] < 100000 and not cap:
            continue
        rows.append([p['name'], p['adm0_a3'], p['adm1name'], round(p['longitude'], 3),
                     round(p['latitude'], 3), int(p['pop_max']), cap])
    rows.sort(key=lambda r: -r[5])
    json.dump({'fields': ['name', 'iso3', 'adm1', 'lon', 'lat', 'pop', 'cap'], 'rows': rows},
              open(os.path.join(ASSETS, 'geo', 'cities.json'), 'w'), ensure_ascii=False,
              separators=(',', ':'))
    print('cities', len(rows))


# ── simplification (Douglas-Peucker on each ring, in degrees) ──────────────
def _dp(pts, tol):
    if len(pts) < 3:
        return pts
    keep = [False] * len(pts)
    keep[0] = keep[-1] = True
    stack = [(0, len(pts) - 1)]
    while stack:
        a, b = stack.pop()
        ax, ay = pts[a]
        bx, by = pts[b]
        dx, dy = bx - ax, by - ay
        L = math.hypot(dx, dy) or 1e-12
        best, idx = -1, None
        for i in range(a + 1, b):
            px, py = pts[i]
            d = abs(dy * px - dx * py + bx * ay - by * ax) / L
            if d > best:
                best, idx = d, i
        if idx is not None and best > tol:
            keep[idx] = True
            stack += [(a, idx), (idx, b)]
    return [p for p, k in zip(pts, keep) if k]


def simplify_geom(g, tol, nd=3):
    def ring(r):
        # A closed ring starts and ends on one point: split it at the vertex farthest from
        # the start so Douglas-Peucker has a real chord to measure against.
        far = max(range(len(r)), key=lambda i: (r[i][0] - r[0][0]) ** 2 + (r[i][1] - r[0][1]) ** 2)
        s = _dp(r[:far + 1], tol)[:-1] + _dp(r[far:], tol)
        if len(s) < 4:
            return None
        return [[round(x, nd), round(y, nd)] for x, y in s]

    polys = g['coordinates'] if g['type'] == 'MultiPolygon' else [g['coordinates']]
    out = []
    for poly in polys:
        rings = [ring(r) for r in poly]
        if rings and rings[0]:
            out.append([r for r in rings if r])
    return {'type': 'MultiPolygon', 'coordinates': out}


def build_admin1(codes):
    feats = ne('ne_10m_admin_1_states_provinces')['features']
    for code in codes:
        sel = [f for f in feats if f['properties']['adm0_a3'] == code]
        if not sel:
            print('admin1: no features for', code)
            continue
        xs = [c[0] for f in sel for c in _coords(f['geometry'])]
        ys = [c[1] for f in sel for c in _coords(f['geometry'])]
        diag = math.hypot(max(xs) - min(xs), max(ys) - min(ys))
        tol = diag * 0.0007
        out = []
        for f in sel:
            p = f['properties']
            g = simplify_geom(f['geometry'], tol)
            if not g['coordinates']:
                continue
            out.append({'type': 'Feature', 'id': p['iso_3166_2'] or p['adm1_code'],
                        'properties': {'name': p['name'], 'name_local': p['name_local'],
                                       'type': p['type_en'], 'code': p['iso_3166_2'],
                                       'postal': p['postal'], 'region': p['region'],
                                       'label': [round(p['longitude'], 3), round(p['latitude'], 3)]},
                        'geometry': g})
        path = os.path.join(ASSETS, 'geo', f'admin1-{code}.json')
        json.dump({'type': 'FeatureCollection', 'source': 'Natural Earth 10m admin-1 (public domain), simplified',
                   'features': out}, open(path, 'w'), ensure_ascii=False, separators=(',', ':'))
        print(f'admin1-{code}.json', len(out), f'{os.path.getsize(path) // 1024} KB')


def _coords(g):
    polys = g['coordinates'] if g['type'] == 'MultiPolygon' else [g['coordinates']]
    for poly in polys:
        for r in poly:
            yield from r


if __name__ == '__main__':
    what = sys.argv[1] if len(sys.argv) > 1 else 'all'
    os.makedirs(os.path.join(ASSETS, 'geo'), exist_ok=True)
    if what in ('countries', 'all'):
        build_countries()
    if what in ('flags', 'all'):
        build_flags()
    if what in ('icons', 'all'):
        build_icons()
    if what in ('world', 'all'):
        build_world()
    if what in ('cities', 'all'):
        build_cities()
    if what in ('admin1', 'all'):
        build_admin1(sys.argv[2:] or ADMIN1_DEFAULT)
