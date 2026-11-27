# Engineering diagrams

`SLD` and `catenary` (`scripts/pi/eng.py`), ported from MM-ify's `sld.py`. For the blog's
engineering posts: how a substation, a feeder or a plant connects, and where power flows.
Gallery: `sld`.

```python
sld = SLD(width=10, height=6, margin=(70, 24), narrow_size=None)

@sld.build
def _(s, lang, narrow):          # grid units, y grows downwards
    s.bus((1, 1.4), (9, 1.4), label='150 kV')
    s.wire([(5, 1.4), (5, 3.0)]); s.breaker((5, 2.1), label='CB')
    t = s.transformer((5, 3.5), label='60 MVA', side='right')   # returns its two terminals
    s.flow((5, 1.6), (5, 2.9))   # animated dashes, direction a -> b
    s.flow_label((5.5, 2.1), ['48 MW', '12 Mvar'], up=False, role='a')
fig.add(sld)
```

Symbols: `bus`, `wire` (dashed for a normally open link), `node`, `breaker` (closed or open),
`disconnector`, `earth`, `transformer` (two circles), `generator`, `load` (arrowhead),
`grid_infeed` (hatched box), `ct`, `flow_label` (values with a direction triangle), `text`.

## Rules (from MM-ify)

- Schematics stay abstract: straight conductors, no sag, no shadows. Draw conductors first,
  then symbols (they are filled with the card colour and mask the line under them).
- Values exactly as the source gives them; one `flow_label` per branch; active power in `a`,
  reactive power, if shown, in `gold`.
- Labels sit beside the symbol (`side='left'|'right'`), never across a conductor. A narrow
  layout uses the same grid smaller: keep a diagram to about 10 x 7 units, or branch on
  `narrow` and draw it in a taller arrangement (`narrow_size=(w, h)`).
- A physical drawing (an elevation, a span) uses `catenary(a, b, c)` for every flexible
  conductor: jumpers c 8-12 m, strung spans 40-80 m, cables 3-6 m (MM-ify realism rule), and a
  "Not to scale" `note=` when proportions are indicative.
