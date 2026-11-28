# Infographics

`Units`, `Waffle`, `Stats`, `Compare`, `Timeline` (`scripts/pi/infographic.py`). An
infographic makes a number felt, but stays a chart: one icon is one fixed amount, a tower's
height and an area are proportional to the value, and the number is always written too.
Gallery: `units-grid`, `units-stack`, `waffle`, `stats`, `compare`, `timeline`.

## Units: counts as icons or towers

```python
Units(rows, icon='phone', per=1, key={'en': '= 1 working day', 'id': '...'}, arrange='grid'|'stack',
      cols={'w': 20, 'n': 10}, fmt=None, unit={'en': ' days', 'id': ' hari'})
row: {'label', 'value', 'role', 'flag', 'note', 'text'}
```

- **grid**: rows of icons, `cols` per line; one row per item, label and flag on the left
  (wide) or above (narrow), the count on the right. A fractional last icon is clipped to its
  share. Choose `per` so the largest row is 20 to 120 icons.
- **stack**: one tower per item, slabs piled like phones or banknotes on a table, every tenth
  ticked on the left scale; the top slab shows its face. Towers sit side by side on one
  baseline, so heights compare like columns. Best for 2 to 5 items whose counts differ a lot
  ("104 days in Jakarta, 12 in Perth").
- The key line states the unit with the icon: "[icon] = 1 working day". A unit chart needs it
  (`review['legend']`: "the unit must be stated").
- Icons: the solid glyphs (`phone`, `person`, `house`, `building`, `coin`, `banknote`, `day`,
  `bag`, `car`, `bowl`, `bolt`, `drop`, `tree`, `box`, `plane`, `train`) read best in a
  count; any Lucide icon works (`scripts/lookup.py icon <word>`). Never a brand logo or a
  product's likeness: a phone is a generic phone, even when the post names a model.

## Waffle

`Waffle(parts, rest={...})`: 100 squares, one per percent, filled bottom-up. One or two shares
the reader should count ("59 in 100 workers"). The labels sit beside (wide) or under (narrow).

## Stats

`Stats(tiles)`: two to four big numbers with a label and optional icon: `{'value': {...},
'label': {...}, 'role', 'icon', 'note'}`. The value is text you write (already formatted per
language). Use as a summary at the top of a section, not instead of a chart the post needs.

## Compare

`Compare(items, shape='square'|'circle')`: two to four amounts as shapes whose **area** is
proportional to the value, bottom-aligned, value above, name below.

## Timeline

`Timeline(events, positions=None)`: `{'date', 'text', 'role'}`; wide: one horizontal line,
labels alternating above and below; narrow: a vertical list. `positions` (0 to 1) spaces
events by real time instead of evenly; then check the labels do not collide.

## Pitfalls

- A row with 300 icons is a texture, not a count: raise `per`.
- Do not mix units in one figure (days in one row, weeks in another).
- Colour: the subject `hl`, others `a` or `base`; the empty part `base-soft`.
