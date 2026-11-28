# API reference

`from pi import *` (after `sys.path.insert(0, '.claude/skills/procedural-illustration/scripts')`;
`render.py` does this for a spec).

## Figure

```python
Figure(name, title, subtitle=None, source=None, note=None, alt=None, langs=('en', 'id'),
       layouts=(('w', 720), ('n', 280)), data_table=True, review=None, kind='chart', gap=18)
fig.add(component)        # stacked top to bottom, `gap` apart
@fig.draw                 # free drawing: def draw(c, lang): ... (return a height to fix it)
```

`source='refs'`: "Source: References" / "Sumber: Referensi", a link to the post's References
section (`chart_refs`, `chart_refs_id` in `_data/i18n.yml`). `None` for the author's own
experience or reasoning (with `review['source']`). A short written source (under 40 characters)
is allowed for a figure outside a post. `note`: the text only; the page adds "Note:" /
"Catatan:"; one short caveat that changes the reading.

`name` is the file name and page id: `<prefix>-pi-<subject>` (`gsl-pi-real-wages`). `kind`:
`chart`, `map`, `infographic`, `flow`, `engineering` (flow/engineering skip the unit and
outlier questions). Text values are `{'en': ..., 'id': ...}` or plain strings. `tr(v, lang)`
picks one.

## Canvas primitives (`c` in a draw function or a component)

| Call | Draws |
| --- | --- |
| `c.W`, `c.layout` ('w'/'n'), `c.narrow`, `c.lang` | the layout |
| `c.text(x, y, s, size, weight, fill, anchor, va, halo, max_w, kind)` | text (wraps at `max_w`), returns its box; `va` top/middle/bottom/baseline |
| `c.rich(x, y, [(text, weight, fill), ...])` | one line in several styles |
| `c.rect`, `c.bar(x, y, w, h, fill, round_end)`, `c.line`, `c.polyline(..., data=True)`, `c.polygon`, `c.path`, `c.circle` | shapes, painted by role; `data=True` registers a line labels must avoid |
| `c.flag('IDN', x, y, h)` | a flag, 4:3, returns its right edge |
| `c.icon(name, x, y, size, color)` | a Lucide outline icon or a solid glyph (`GLYPHS`: phone, person, house, building, coin, banknote, day, bag, car, bowl, bolt, drop, tree, box, plane, train, square, circle) |
| `c.arrow(pts, stroke, head='end'/'both'/'start')` | an open 90-degree arrow |
| `c.leader(anchor, to)`, `c.callout(anchor, at, text, head=)` | a right-angled pointer line, with its note |
| `c.bracket(x, y0, y1)`, `c.hbracket(x0, x1, y)` | a bracket over a range |
| `c.box(x, y, w, h, text, fill, stroke, corners='rrsc')` | a text container, MM-ify shape corners |
| `c.hits(box)` | does a box touch existing text, marks or data lines? |
| `place(c, x, y, text, size, prefs=('right', 'above', ...))` | put a label in the first free spot around a point |
| `spread(items, lo, hi, gap)` | push labels apart vertically |

## Formats (`pi.fmt`)

`number(v, dp, lang)`, `pct`, `money(v, 'Rp', dp, lang, compact='short'|'long')`,
`compact_number`, `dp_for(values)`, `tick(v, step, lang)`. In components pass
`fmt={'dp': 1, 'unit': '%', 'prefix': '', 'money': 'Rp', 'compact': 'long', 'sign': True}`
or a function `f(v, lang)`. The minus sign is a real minus (U+2212).

## Components

Signatures and options are in each class's docstring (`scripts/pi/*.py`) and in the
subskills; `examples/gallery.py` shows every one in use.
