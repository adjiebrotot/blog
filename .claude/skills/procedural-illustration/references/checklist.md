# The presentation checklist (21 items)

Every figure answers all 21 before it is published. `check.py` runs during `render.py`:
**AUTO** items are proved from the drawing; **REVIEW** items need an answer in the spec's
`review={...}` (a missing answer is an ERROR) and a look at the sheet. The engine's defaults
already satisfy most AUTO items; the checker catches what a spec overrides.

| # | Question | How it is met | Check |
| --- | --- | --- | --- |
| 1 | Is the data source stated on or near the chart? | `source=` prints "Source: ..." under the drawing. A diagram of the author's own reasoning says so in `review['source']`. | AUTO: ERROR if missing |
| 2 | Are labels spelled right and units clear? | The checker lists every label per language (REVIEW: proofread it). Units go in the subtitle or the axis unit label ("Rp trillion", "Index, 2019 = 100"), or on each value (`fmt={'unit': '%'}`). | AUTO: WARN with no unit anywhere (`review['units']` for unitless figures such as a flowchart) |
| 3 | Consistent decimals? | `fmt={'dp': n}` per series; `fmt.dp_for(values)` picks the most any value needs. Tick decimals follow the step. Never "10.0%, 15%, 3.456%". | AUTO: ERROR on mixed decimals in a component's value labels |
| 4 | Is the text large enough on every screen? | Two layouts drawn at about 1:1: wide 720 (desktop column 732px), narrow 280 (a 390px phone). Minimum 13px wide, 12.5px narrow; the checker reports the smallest size on 360, 390 and 430px phones. | AUTO: ERROR under the minimum |
| 5 | Repeated or redundant text removed? | Title and subtitle live once, above. The unit is said once (axis label or subtitle), not on every tick. | AUTO: ERROR if subtitle = title; WARN when the same label is drawn 3+ times |
| 6 | Decorative elements removed? | The engine draws flat fills only. 3D only when a third dimension is data (`charts-3d`). Icons only as units or tile markers. | AUTO: ERROR on any gradient, filter or shadow |
| 7 | Is the title clear and impactful? | A "power" title that states the finding, or a plain descriptive one for a neutral reference figure; under ~90 characters. | AUTO: length; REVIEW: read it |
| 8 | Informative subtitle or caption? | Metric, unit, period, definition ("Share of the labour force with no paid work at all"). `note=` for a caveat that changes the reading. | AUTO: WARN if missing (charts) |
| 9 | Labels, ticks and gridlines sized and spaced? | Ticks are thinned until they never touch; labels are placed by `place()` away from text, marks and data lines; line-end labels are spread apart. | AUTO: ERROR on overlapping text; WARN when a data line runs through a label |
| 10 | Balanced spacing? | Components size themselves; the card pads 1rem. | AUTO: ERROR when anything leaves the frame; WARN on extreme height/width |
| 11 | Is a legend necessary? | Direct labels by default (line ends, bar values, flags, slope ends). A key only for a stacked bar, a choropleth or a unit chart's "one icon = ...". | AUTO: WARN on a key without `review['legend']` |
| 12 | Notable spikes, dips or outliers labelled? | `annotate=[...]` on bars and lines, `bands=` for periods (the pandemic), `ref=` for a base or average. | REVIEW: `review['outliers']` |
| 13 | Axes scaled honestly? | Bars and areas always start at zero (enforced by `scale.Linear`). A line may start elsewhere only with `y={'zero': False}`, a stated base (index = 100) and a reason. | AUTO: ERROR on a non-zero axis without `review['axis']` |
| 14 | Data ordered on purpose? | `sort='desc'` for rankings, chronological for time, grouped for categories; say which and why. | AUTO: ERROR on horizontal bars or units without `review['order']` |
| 15 | Intentional colour scheme? | Roles: `hl` the subject, `a` the peer group, `base` the context, `s1`-`s5` for equal series, `seq`/`div` ramps for maps. | AUTO: WARN with more than 4 data colours |
| 16 | Contrast and colour blindness checked? | Every role is checked against the card in both themes: text 4.5:1 (`*-ink` roles), marks 3:1; pairs are compared under protan, deutan and tritan simulation. Direct labels, dashes and markers back colour up. | AUTO: ERROR for low-contrast text; WARN for pairs under dE 12 without `review['cvd']` |
| 17 | Style guide followed? | Fonts are the page's (DM Sans, DM Mono for figures); colours are tokens; corners and line weights are the tool's. | AUTO: ERROR on a hard-coded colour |
| 18 | Transparent, no cherry-picking? | Full series, stated crops, the same base for every country, a `note=` for a break in a series. | REVIEW: `review['transparency']` |
| 19 | The right chart type? | `references/chart-chooser.md`. | REVIEW: `review['type']` |
| 20 | Tailored to the audience? | Blog readers are general readers: plain words, units spelled out, no jargon on the figure (an abbreviation in a label is avoided or spelled out, since tooltips do not reach inside SVG). | REVIEW: `review['audience']` |
| 21 | Does it make sense out of context? | Title + subtitle + labels + source tell the whole story; `alt=` says what it shows and its point, in each language. | REVIEW: `review['standalone']`; AUTO: ERROR without alt |

## Reading the sheet (what the checker cannot see)

- Does the eye land on the subject first? If not, the colours or the order are wrong.
- Would a reader who skips the post get the same point as the title? (item 21)
- Is anything crowded on the phone layout that is fine on desktop? Fix the narrow layout
  (fewer labels, `narrow_orient`, shorter label text), never shrink text under the minimum.
- In the dark theme, does every colour still separate from its neighbour?
