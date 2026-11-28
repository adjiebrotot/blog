#!/usr/bin/env python3
"""Find the names a spec needs, without opening the big asset files.

    python3 lookup.py icon phone          # Lucide icons and solid glyphs whose name or tags match
    python3 lookup.py flag korea          # ISO alpha-3 codes for flags (and whether the file exists)
    python3 lookup.py region IDN jawa     # admin-1 ids in assets/geo/admin1-IDN.json
    python3 lookup.py city surabaya       # a city's coordinates and population
    python3 lookup.py tokens              # every colour role, with its dark and light value
"""
import json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
A = os.path.join(HERE, '..', 'assets')
BLOG = os.path.abspath(os.path.join(HERE, '..', '..', '..', '..'))
sys.path.insert(0, HERE)


def main(a):
    kind, q = a[0], ' '.join(a[1:]).lower()
    if kind == 'icon':
        from pi.canvas import GLYPHS
        for g in GLYPHS:
            if q in g:
                print(f'{g:24} solid glyph')
        d = json.load(open(os.path.join(A, 'icons.json')))
        n = 0
        for name, tags in d['tags'].items():
            if q in name or any(q in t for t in tags):
                print(f'{name:24} {", ".join(tags[:6])}')
                n += 1
                if n > 40:
                    print('...')
                    break
    elif kind == 'flag':
        cs = json.load(open(os.path.join(A, 'countries.json'), encoding='utf-8'))
        for k, v in cs.items():
            if q in v['name'].lower() or q == k.lower() or q == (v.get('iso2') or '').lower():
                ok = os.path.exists(os.path.join(BLOG, 'assets', 'img', 'flags', k.lower() + '.svg'))
                print(f'{k:6} {v["name"]:32} flag {"yes" if ok else "NO"}')
    elif kind == 'region':
        iso, q = a[1].upper(), ' '.join(a[2:]).lower()
        gj = json.load(open(os.path.join(A, 'geo', f'admin1-{iso}.json'), encoding='utf-8'))
        for f in gj['features']:
            p = f['properties']
            if q in p['name'].lower() or q in (f['id'] or '').lower() or not q:
                print(f'{f["id"]:10} {p["name"]:28} {p["type"]}')
    elif kind == 'city':
        d = json.load(open(os.path.join(A, 'geo', 'cities.json'), encoding='utf-8'))
        for r in d['rows']:
            c = dict(zip(d['fields'], r))
            if q in c['name'].lower():
                print(f'{c["name"]:24} {c["iso3"]} {c["adm1"]:24} lon {c["lon"]:8} lat {c["lat"]:7} pop {c["pop"]:,}')
    elif kind == 'tokens':
        from pi.tokens import hexes, ROLES
        d, l = hexes('dark'), hexes('light')
        for r in ROLES:
            print(f'{r:10} dark {d[r]:22} light {l[r]}')


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print(__doc__)
    else:
        main(sys.argv[1:])
