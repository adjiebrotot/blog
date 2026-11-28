# 2D charts

`Bars`, `Line`, `Scatter`, `Dumbbell`, `Slope`, `Donut` (`scripts/pi/charts2d.py`) and the
`hbar` include. They follow the tool site's Chart.js look (hairline horizontal grid, muted
ticks, `--line-a...e` series colours, rounded bar ends) without its legend: data is labelled
where it is drawn. Gallery: `bars-h`, `bars-v`, `bars-stack`, `line`, `area`, `scatter`,
`dumbbell`, `slope`, `donut`.

## Bars

```python
Bars(items, orient='h'|'v', mode='single'|'group'|'stack', series=None, fmt=None, axis=None,
     sort=None, ref=(), annotate=(), unit=None, domain=None, narrow_orient=None, value_inside=False)
item: {'label': {...}, 'value': n | 'values': [...], 'role': 'hl'|'a'|'base'|..., 'flag': 'IDN',
       'note': {...}, 'text': {...}}
```

- **Horizontal** for categories with names (countries, provinces, companies): flag, name,
  bar, value. Sort by value (`sort='desc'`) unless the order means something; answer
  `review['order']`. The subject is `role: 'hl'` (bold name, red bar); its peer group `a`;
  the rest `base`.
- **Vertical** (columns) for years or a few short categories. The value sits on each column;
  on the phone layout, when values do not fit, only the first, last, highest, lowest and
  highlighted ones stay (the data table has all). Columns that cannot fit on a phone turn
  into rows by themselves; `narrow_orient='v'` keeps columns (years read better left to right).
- `ref=[{'value': 5.7, 'label': {...}}]` draws a dashed reference line (an average, a legal cap).
- `annotate=[{'at': index or English label, 'text': {...}}]`: a note under a row (h) or above a
  column (v), for the spike the post discusses (item 12).
- `mode='stack'`/`'group'` need `series=[{'name', 'role'}]`; they draw a key line, so give
  `review['legend']`. Prefer two simple charts to a grouped one with 4+ series.
- Bars always start at zero. A negative value grows the other way from the zero line.

## The `hbar` include (long country rankings)

For 10 or more countries, the HTML bar chart reflows better than any SVG: names wrap, rows
stay 1:1 on every screen. Data in `_data/charts.json` (title, sub, source per language; the figure shows only "Source:
References" as a link, the `source` text is provenance for editors; rows
with `c` = ISO alpha-3, `g` = hl/asean/oecd/avg/na, `w` = width %, `v` = value text per
language, optional `note`, a caveat drawn smaller than the name, `flag`). Flags come from the row's code; `"flag": false` or a
non-country code (OECD) leaves an aligned blank. `{% include hbar.html id="..." %}`. Country
names per language: `_data/countries.yml` (add a country there when a chart needs it). Keep
`w` proportional to the value (`w = value / max * 100`), one precision per chart.

## Line (and areas)

```python
Line(x, series, y={'domain': [lo, hi], 'zero': bool, 'fmt': {...}, 'unit': {...}, 'step': s, 'ticks': n},
     x_fmt=None, ref=(), bands=(), annotate=(), stack=False, end_values=True, height=None)
series item: {'name': {...}, 'values': [...], 'role': 'hl', 'dash': '5 4', 'markers': 'end'|'all'|None, 'area': False}
```

- Each line is named at its end, with its last value, in its colour; labels are pushed apart
  when lines end close together, with a thin connector.
- Context lines `base`, the subject `hl` (drawn last, on top). Two to five lines; more is a
  small-multiple job (several figures).
- An **index** (2019 = 100) compares unlike series: give `ref=[{'value': 100, 'label': ...}]`
  and say the base in the unit label. A non-zero y axis needs `zero: False` and
  `review['axis']`; the checker refuses it otherwise (item 13).
- `bands=[{'from': 2020, 'to': 2021, 'label': {...}}]` shades a period that explains a dip.
- `annotate=[{'x': 2021, 'series': 1, 'text': {...}}]` circles a point and places its note
  where it does not touch a line or a label.
- `stack=True` draws stacked areas (zero-based); each band named at the right with its own
  value (not the cumulative one).
- Missing values are `None`; the line skips them.

## Scatter

`Scatter(points, x={'title', 'fmt', 'domain', 'zero'}, y={...}, trend=False)`; points
`{'x', 'y', 'label', 'role', 'show_label'}`. Label the subject (`hl`) and the two or three
points the text mentions; leave the rest unlabelled (their names are in the data table and
the hover titles). A trend line is dashed and only drawn when the post discusses the
relationship.

## Dumbbell and Slope

`Dumbbell(rows, names=(before, after), roles=('base', 'hl'))`: the gap between two values per
row, the two moments named once above the first row. `Slope(rows, names)`: two columns, one
line per item, labels at both ends; use when ranks cross.

## Donut

`Donut(parts, centre={'value', 'label'})`: 2 to 5 parts of one whole; the key number in the
hole; parts listed beside it (no pointer lines across the ring). More parts: use bars.

## Pitfalls

- A label wider than the layout wraps; if it wraps into 3 lines on the phone, shorten the
  label (an `{'en': 'S. Korea'}` is fine) rather than shrinking it.
- Do not repeat the unit on every value when the subtitle says it, except `%` and `x`, which
  read as part of the number.
- Abbreviations inside the figure get no tooltip: spell them out or keep them to ones the post
  defines right next to the figure.
