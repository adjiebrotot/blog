# What came from MM-ify, and what changed

MM-ify draws Mott MacDonald-branded graphics with matplotlib, Pillow and three.js. This skill
keeps its method and swaps its brand and output for the blog's.

| MM-ify | Here | Why |
| --- | --- | --- |
| Draw in code, never with an image generator; values exact | same | exact numbers, editable, free |
| `mm_brand.py` palette (MM Purple, Turquoise...) and `text_on()` | `tokens.py` roles read from `blog.css`, `ink()` for text on colour | the blog's design system, both themes |
| matplotlib figure -> PNG/SVG | hand-written SVG, inline, real text, two layouts | follows the theme toggle, readable on phones, translatable, accessible |
| Proxima Nova -> Arial | DM Sans / DM Mono from the page, widths measured in `metrics.json` | the blog's fonts; labels laid out without a browser |
| `callout()`, `bracket()`, `arrow()` (open 90-degree heads, right-angled leaders) | `canvas.callout`, `leader`, `bracket`, `arrow` | kept: they are good annotation |
| `brand_shape()` / `text_box()` corners (square, round, chamfer) | `canvas.box(corners=...)`, `shape_path` | kept, with the blog's 9px radius |
| `donut()`, `style_chart_axes()` | `Donut`, the charts in `charts2d.py` | extended to the full chart set and the checklist |
| `sld.py` (single-line diagrams) | `eng.SLD` | kept for engineering posts |
| `animate.py` Flow GIF / SMIL | `.pi-flow` CSS dashes on edges and conductors | no GIF needed; stops for reduced motion |
| `catenary()` | `eng.catenary` | kept |
| `iso.py` scenes, `elevation.py`, `mesh3d.py` + three.js, `equipment3d.py` | not ported: scenes belong to `isometric-illustration`; 3D graphs are `iso3d.py`; interactive 3D comes from a tool embed (`brotools-embed`, Plotly gl3d) | one skill per job; no 600 KB viewer in a post |
| "No title, subtitle or source unless asked" | title, subtitle and source are required | a blog figure must stand alone (checklist 1, 7, 8, 21) |
| "Not to scale" note | `note=` when proportions are indicative | same idea, in the figure's note line |
| Quality checklist (6 lines) | the 21-item checklist with `check.py` | enforced, not only listed |
