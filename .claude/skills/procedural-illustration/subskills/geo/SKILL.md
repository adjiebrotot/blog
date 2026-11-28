# Maps

`Map` (`scripts/pi/geo.py`): vendored Natural Earth geometry, no tiles, no network. Gallery:
`map-admin1` (highlighted provinces with labels), `map-world` (choropleth with a key).

```python
Map(base='world-110m'|'world-50m'|'admin1:<ISO3>'|path.geojson, projection='mercator',
    highlight={id: role}, values={id: n}, bins=[...], ramp='seq'|'div', value_fmt=None, key=None,
    labels=[{'id' | 'lonlat', 'text', 'prefs', 'callout', 'size'}],
    points=[{'lonlat' | 'city', 'label', 'role', 'r'}], routes=[{'from', 'to', 'role', 'dashed', 'bend'}],
    context='world-50m', add=[('world-50m', ['HKG', 'MAC', 'TWN'])], bounds=(lon0, lat0, lon1, lat1),
    height={'w': 480, 'n': 380})
```

## Choose

| Map | Projection | Notes |
| --- | --- | --- |
| the world | `equal-earth` | areas true; crop Antarctica with `bounds=(-170, -58, 180, 84)` |
| Indonesia, the tropics | `mercator` | `admin1:IDN` (33 provinces, see assets.md) with `context='world-50m'` |
| China, Australia, the US, mid latitudes | `albers` | parallels default to the bounds' sixths; China `bounds=(73, 17, 135, 54)` |
| a city region | `equirect` | with points and routes |

Ids: world features by ISO alpha-3 (`IDN`), admin-1 by ISO 3166-2 (`ID-JK`, `CN-SH`);
`scripts/lookup.py region IDN jawa` lists them. Cities by name (`'city': 'Surabaya'`, from
`assets/geo/cities.json`, places of 100k+).

## Rules

- The base land is quiet (`land`), the context countries quieter (`land-ctx`), borders are the
  card colour; only the regions that carry the story get a role (`a` for "visited", `hl` for
  the subject). MM-ify's map rule: a 20% base with colour highlights.
- **Highlight** for membership (visited, member, affected): no key; label each highlighted
  region directly. **Choropleth** (`values` + `bins`) for a measure: 4 to 5 bins with round
  edges, a key under the map with `key=` naming the unit, and the data table. Sequential ramp
  for "more", diverging for "above or below a midpoint".
- Labels go on the region's label point when they fit, otherwise beside it with a pointer
  line (`callout=True` forces it). Small regions (Beijing, Shanghai, Hong Kong) usually need
  the pointer. On the phone layout the map is narrow: label fewer regions, or list them in the
  subtitle and let colour plus the data table carry the rest.
- Never draw disputed claim lines; the geometry is Natural Earth's de facto borders.
- Hong Kong, Macau and Taiwan: `add=[('world-50m', ['HKG', 'MAC', 'TWN'])]` on a China map.
