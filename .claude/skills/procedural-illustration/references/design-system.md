# Design system for figures

The blog's tokens come from the tool site (`../tool/dark.css`, `light.css`,
`_ref/design-reference.md` there, "Charts & Graphs"); `assets/css/blog.css` copies them and adds
the `--pi-*` roles below. A figure paints only with roles, so one SVG follows the reader's
theme (`:root` dark by default, `:root.light`). `python3 scripts/lookup.py tokens` prints every
role with both values.

## Colour roles

| Role | Dark | Light | Use |
| --- | --- | --- | --- |
| `hl` | #F05252 | #E63939 | **the subject**: Indonesia, the series the title is about, the bad outcome. One per figure, usually |
| `a` | #5A91E8 | #3A71C8 | the comparison group (other ASEAN countries, the alternative) |
| `base` | #6B7A94 | #7F8BA0 | context: everything the reader should see but not dwell on |
| `hl-soft`, `a-soft`, `base-soft` | tints | tints | areas under a line, bands (a period), boxes in a flowchart, the empty part of a unit chart |
| `s1` ... `s5` | the tool's `--line-a` ... `--line-e` | | equal series with no subject (several cities, several fuels). In this order |
| `gold`, `teal` | `--gold`, `--accent2` | | a third accent when hl/a/base are taken (a target, a forecast) |
| `pos`, `neg` | `--positive-em`, `--negative-em` | | gains and losses, surplus and deficit |
| `seq1` ... `seq5` | dark navy to light blue | pale to deep blue | a choropleth or a heat scale: low to high |
| `div1` ... `div5` | red, grey, blue | | a diverging scale around a midpoint |
| `land`, `land-ctx`, `land-line` | | | map regions, the quieter countries around them, borders (the card colour) |
| `node`, `node-line` | | | flowchart boxes |
| `ink`, `label`, `grid`, `axis`, `bg` | `--text`, `--chart-text`, `--chart-grid`, axis grey, `--panel` | | text, secondary text and ticks, gridlines, baselines, the card |
| `shade`, `light` | translucent | | the right and top faces of 3D boxes (MM-ify's multiply shading) |
| `<role>-ink` | | | text in a series colour (`hl-ink`, `a-ink`, `s1-ink`...): the same hue at 4.5:1 or more on the card |

Rules: text in a series colour uses its `-ink` role (`tokens.ink(role)` picks it); a filled
box with text on it uses `start` (filled `a`, text `bg`) or a `-soft` fill with `ink` text.
Ratio: most of the figure is `base`, `grid` and text; `hl` covers the least area and gets the
eye first.

## Type

DM Sans from the page (the SVG inherits it), tabular figures for every number. Sizes in px at
the layout's design width (wide 720, narrow 280, both drawn about 1:1):

| Text | Wide | Narrow | Weight |
| --- | --- | --- | --- |
| title, subtitle | HTML above the drawing (1rem bold, 0.82rem muted) | same | |
| labels (categories, line ends) | 13.5 | 13 | 400; the subject 700 |
| values on marks | 13.5 | 13 | 500-700 |
| ticks, notes, keys | 13 | 12.5 | 400 |
| big numbers (stats, donut centre) | 28-30 | 24-26 | 700 |
| source, note | HTML under the drawing (0.75rem muted) | same | |

Sentence case everywhere, no italics in a figure, left-aligned notes, centred text only in
boxes of three lines or fewer (MM-ify rule).

## Marks and lines

- Bars: square at the baseline, 3px round at the free end (`canvas.bar`); 58% of the row.
- Lines: 2.75px for `hl`, 2.25px for `a`/`s1`, 2px others; round joins; a dot at the end.
- Grid: 1px `grid`, horizontal only for columns and lines; the zero line 1.25px `axis`.
- Reference lines: 1.25px `ink`, dashed 5-4, labelled once.
- Pointer lines (MM-ify): thin, straight, right-angled, with a 2px dot on the data point.
- Arrows (MM-ify): open 90-degree heads joined to the stem, 1.6px.
- Boxes: 9px corners (the blog's `--radius-sm` family); `corners='rrsc'` mixes round, square
  and cut corners per corner like the MM shapes.
- Flags: 4:3, 2px corners, a hairline `axis` border so white flags show on a white card.
- 3D faces: role fill; right face darkened with `shade`, top lightened with `light`.

## The figure card

`.pi` and `.hbar` share it: `--pi-bg` (the panel), a 1px border, 14px corners, 1rem padding
(0.75rem on phones). Inside: the figcaption (title, subtitle), `.pi-art` (the two SVGs; a
container query shows `.pi-w` at 520px and wider, `.pi-n` below), the source line, a folded
data table. Animated edges use `.pi-flow` (CSS dashes, stopped for reduced motion).
