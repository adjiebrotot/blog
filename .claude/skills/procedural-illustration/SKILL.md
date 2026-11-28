---
name: procedural-illustration
description: Draw a data figure for a post on this blog in code, in the blog's design system, instead of a Mermaid block or a screenshot. Charts (bars, columns, lines, areas, scatter, dumbbell, slope, donut), infographics (icon unit charts, stacked towers, waffles, stat tiles, size comparisons, timelines), flowcharts and cycles, maps (world, provinces of 14 countries, cities, choropleths, routes), 3D graphs (isometric bars, surfaces, unit blocks) and engineering single-line diagrams, each as one inline SVG per layout (desktop and phone) that follows the reader's light or dark theme, with real text, country flags, a source line, a data table and a 21-point presentation checklist enforced by a checker. Use when a post needs a chart, graph, diagram, map, flowchart, infographic or visualisation of numbers, when Adjie asks to make a chart "presentable", to add flags, to replace a Mermaid chart, or when a plan lists a figure. For a picture with people or places use isometric-illustration or editorial-illustration; for an interactive chart from a tool use brotools-embed.
---

# Procedural illustration

Data figures drawn with code, in the same design system as the tool site's charts: the
blog's tokens (`assets/css/blog.css`, copied from `../tool/dark.css` and `light.css`), DM Sans,
the tool's line colours (`--line-a` to `--line-e`), flat fills, a hairline grid, direct
labels. One spec file makes the figure in both languages and both layouts; the checker
proves it is readable before it can be published. No API key, no cost, exact numbers.

Adapted from the MM-ify skill (Mott MacDonald's procedural graphics), with its brand swapped
for the blog's: what was kept and what changed is in `references/mm-ify-port.md`.

```
the data and its source -> pick the form (references/chart-chooser.md, the subskill)
  -> spec in _illustrations/<prefix>-pi-<subject>.py (copy from examples/)
  -> render.py --out (read every ERROR/WARN, look at the sheet, fix, repeat)
  -> render.py --publish -> {% include pi/<name>-<lang>.html %} in the post
```

## Which skill draws it

| The post needs | Skill |
| --- | --- |
| numbers shown as a chart, map, infographic, flow or diagram | **procedural-illustration** (this) |
| a chart a reader can change, or a tool's own result | `brotools-embed` (interactive, from the tool site) |
| a place or a system with people, buildings, machines | `isometric-illustration` |
| a mood, a metaphor, one person doing a step | `editorial-illustration` |
| a long ranked list of countries | this skill's `hbar` include (HTML, reflows at any width, flags) |

**Mermaid is no longer used for charts or flowcharts** on this blog: its defaults fail
items 3, 4, 9, 11 and 17 of the checklist. A sequence diagram or a Gantt chart may still use
Mermaid until this skill grows one.

## The subskills

Read the one that fits before writing a spec. Each has its components, recipes and pitfalls.

| Subskill | Draws | Components |
| --- | --- | --- |
| [`subskills/charts-2d`](subskills/charts-2d/SKILL.md) | comparisons, trends, relationships, shares | `Bars` (h, v, grouped, stacked), `Line` (lines, areas, stacked), `Scatter`, `Dumbbell`, `Slope`, `Donut`, and the `hbar` include |
| [`subskills/infographic`](subskills/infographic/SKILL.md) | counts made visible, key numbers, sequences in time | `Units` (icon grid, stacked tower), `Waffle`, `Stats`, `Compare`, `Timeline` |
| [`subskills/flowchart`](subskills/flowchart/SKILL.md) | processes, cycles, branches, cause and effect | `Flow`, `Node`, `Edge` |
| [`subskills/geo`](subskills/geo/SKILL.md) | where: highlighted regions, choropleths, cities, routes | `Map` |
| [`subskills/charts-3d`](subskills/charts-3d/SKILL.md) | a value over two dimensions, a surface, a volume | `Bars3D`, `Surface3D`, `Blocks3D` |
| [`subskills/engineering`](subskills/engineering/SKILL.md) | single-line diagrams, power flow, cables | `SLD`, `catenary` |

A figure may stack several components (`fig.add` twice), or draw freely on the canvas
(`@fig.draw`) with the primitives in `references/api.md` (text, bars, icons, flags, arrows,
pointer lines, brackets, text boxes with round, square or cut corners).

## The rules (non-negotiable)

1. **Data first, honestly.** Every number comes from the post's sources. The figure does not
   list them: `source='refs'` prints "Source: References", a link to the post's References
   section, where the full citations live (item 1). A figure of the author's own experience or
   reasoning (places visited, a diagram of an argument) has no source line at all; say so in
   `review['source']`. Show the whole series the post relies on; a crop or a
   non-zero axis is said on the chart and in `review` (items 13, 18). Never invent values; an
   example figure in `examples/` is labelled "not data" and never published.
2. **The title says the point** ("Indonesia's real wage is still below 2019"). The subtitle,
   if any, is short: the metric and unit ("Average wage over consumer prices, index, 2019 =
   100"). It never explains what the drawing already shows (the years on the axis, what the
   colours mean, which line is which) or anything self-explanatory, and never says anything
   about the interface (small screens, tables, tapping). No subtitle is better than a
   redundant one. Both are HTML above the drawing, so they wrap and translate.
   A row note (a caveat on one item: "Base salary only") is set smaller than the item's label,
   so it reads as a qualifier, not as data.
3. **Label the data directly.** Names at the line ends, values on the bars, flags beside
   countries; a key only when direct labels cannot work (a stacked bar, a choropleth).
4. **One story colour.** `hl` (red) is the subject; `a` (blue) its peers; `base` (grey) the
   context. Two to four data colours at most. Colours are roles, never hex
   (`references/design-system.md`); the checker rejects a hard-coded colour.
5. **Readable on a phone.** Every figure has a wide (720) and a narrow (280) layout drawn
   at about 1:1; nothing under 13px wide or 12.5px narrow; components re-flow (fewer ticks,
   wrapped labels, columns turned into rows, flowcharts into one column).
6. **No decoration.** No gradients, shadows, glows, 3D effects on 2D data, background
   pictures or clip art. Icons only where they carry the count (a unit chart) or name a tile.
7. **Both languages from one spec.** Every text is `{'en': ..., 'id': ...}`; numbers are
   written per language by `fmt` (9.0% / 9,0%, Rp1.2 trillion / Rp1,2 triliun). Indonesian
   text is written under the `bahasa-indonesia` skill like any other Indonesian on the blog.
8. **Accessible.** Each SVG has a `<title>` and the `alt` as `<desc>`; the figure has a data
   table under a "Data table" fold; every mark has a hover `<title>`; colour is never the only
   cue (names, values, dashes, positions carry it too).

The full checklist, with how each item is enforced: [`references/checklist.md`](references/checklist.md).

## Workflow

1. **Collect the data and the source** from the post (or the plan). Write the numbers into the
   spec exactly as the sources give them, rounded once, with one precision per series.
2. **Pick the form** with `references/chart-chooser.md` and open its subskill.
3. **Write the spec** in `_illustrations/<prefix>-pi-<subject>.py` (Jekyll ignores the
   folder): copy the nearest figure from `examples/gallery.py` (every component is there) or
   write YAML for a standard chart (`references/yaml-specs.md`). `<prefix>` is the post's
   prefix used by its other pictures (`gsl`, `cbf`, `kad`...). Fill in `review={...}`: the
   chart type and why, the audience, transparency, how it reads out of context, the notable
   points labelled, and where needed the order, the axis and the legend (the checker asks).
4. **Render to the scratchpad:**
   ```sh
   python3 .claude/skills/procedural-illustration/scripts/render.py _illustrations/<name>.py --out <scratchpad>/pi
   ```
   It prints the checklist per language (ERROR, WARN, REVIEW, OK) and writes
   `<name>-<lang>-sheet.png`: desktop and phone, dark and light. **Look at the sheet**: the
   checker proves sizes, overlaps, frame, decimals and contrast, not taste. Fix every ERROR and
   WARN, read every REVIEW line (it lists every label for proofreading), render again.
5. **Publish:** `render.py <spec> --publish` writes `_includes/pi/<name>-<lang>.html` (refused
   while an ERROR remains) and prints the line for the post:
   `{% include pi/<name>-<lang>.html %}`, on its own line with a blank line before and after.
   The prose around it points only at a figure in its own section (`check-references.py`),
   and no longer needs "the blue line is..." sentences: the figure labels itself.
6. **Run the blog's checks** (`CLAUDE.md`), commit the spec with the generated includes.
   Never edit a file in `_includes/pi/` by hand: change the spec and publish again.

## Files

| Path | What |
| --- | --- |
| `scripts/render.py` | render, check, preview sheet, publish |
| `scripts/pi/` | the engine: `figure`, `canvas` (primitives), `charts2d`, `infographic`, `flow`, `geo`, `iso3d`, `eng`, `fmt` (numbers per language), `scale`, `metrics` (DM Sans widths), `tokens` (roles, contrast, colour blindness), `check` (the checklist), `yamlspec` |
| `scripts/lookup.py` | find an icon, a flag code, a province id, a city, the colour roles |
| `scripts/preview.mjs` | the screenshot sheet (Playwright) |
| `scripts/build_assets.py` | rebuilds the vendored assets (flags, icons, maps, cities, metrics) |
| `assets/` | `icons.json` (2,124 Lucide icons, ISC), `countries.json` (ISO codes, names, regions), `geo/` (world 110m and 50m, admin-1 for 14 countries, 4,170 cities), `metrics.json` (font widths) |
| `/assets/img/flags/<iso3>.svg` (blog) | 243 country and bloc flags (flag-icons, MIT), served to readers |
| `examples/gallery.py` | one figure per component: the catalogue to copy from |
| `references/` | design system, checklist, chart chooser, API, YAML specs, assets and licences, MM-ify port notes |
