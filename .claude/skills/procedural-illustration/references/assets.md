# Vendored assets, sources and licences

Rebuilt by `scripts/build_assets.py` (downloads to `~/.cache/pi`); committed so a figure never
needs the network.

| Asset | Source | Licence |
| --- | --- | --- |
| `/assets/img/flags/<iso3>.svg` (blog, 243 files, ~2.3 MB, loaded only when used) | flag-icons 7.6.0 (npm), 4:3 flags renamed to ISO 3166-1 alpha-3, plus `euu` (EU), `asean`, `uno` (UN), `gb-eng`, `gb-sct`, `gb-wls`, `gb-nir`, `xkx` | MIT, `LICENSE.txt` beside them |
| `assets/icons.json` (2,124 icons + search tags) | lucide-static 1.82.0 | ISC, `assets/LICENSE-lucide.txt` |
| `assets/geo/world-110m.json`, `world-50m.json` | world-atlas 2.0.2 (TopoJSON of Natural Earth admin-0) | ISC; Natural Earth is public domain |
| `assets/geo/admin1-<ISO3>.json` | Natural Earth 10m admin-1 states and provinces, simplified (Douglas-Peucker, 0.07% of the country's diagonal), ids are ISO 3166-2 | public domain |
| `assets/geo/cities.json` | Natural Earth 10m populated places: every place of 100,000+ people and every capital (4,170) | public domain |
| `assets/countries.json` | Natural Earth admin-0 50m: ISO alpha-2, alpha-3, numeric, name, region, income group, label point | public domain |
| `assets/metrics.json` | glyph widths of the blog's DM Sans (400-700) and DM Mono (400, 500), measured in Chromium at 10-40px | measurements of OFL fonts |

Admin-1 files ship for IDN, CHN, AUS, MYS, JPN, KOR, USA, IND, VNM, THA, PHL, CAN, NZL, DEU.
Another country: `python3 scripts/build_assets.py admin1 <ISO3>`.

Known limits:
- **Indonesia** in Natural Earth has 33 provinces (before 2012's Kalimantan Utara and the 2022
  Papua split): say so in the figure's note when a province map is used, or merge the data to
  the old provinces.
- **China**: Hong Kong, Macau and Taiwan are separate admin-0 units in Natural Earth. Draw them
  with `Map(add=[('world-50m', ['HKG', 'MAC', 'TWN'])])`. Disputed borders follow Natural
  Earth's de facto lines; the blog draws no claim lines.
- City names are Natural Earth's English names; an Indonesian label is written in the spec.
