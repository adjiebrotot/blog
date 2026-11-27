# Which form shows it (checklist item 19)

Start from the relationship the post claims, not from the data's shape.

| The point is... | Use | Not |
| --- | --- | --- |
| how places or groups rank on one measure | `Bars` horizontal, sorted, flags (`hbar` include for 10+ countries) | a vertical bar chart with slanted names |
| one number per year (a stock, a total) | `Bars` vertical (columns) | a line with 5 points and no trend |
| a trend over time, or two to five trends compared | `Line`; an index (= 100) to compare unlike units | bars for 20+ years |
| a total and its parts over time | `Line(stack=True)` area or stacked `Bars` | a pie per year |
| change between two moments for several items | `Slope` (ranks matter) or `Dumbbell` (gaps matter) | two grouped bars per item |
| a relationship between two measures | `Scatter`, label only the points in the story | a dual-axis line |
| a share of one whole, 2 to 5 parts | `Donut` (key number in the hole) or `Waffle` (one share people should count) | a pie with 8 slices, 3D pie |
| a count made physical ("104 days of wages") | `Units`: icon grid, or a stacked tower when heights compare | a bar with a phone picture on it |
| two or three key numbers | `Stats` tiles | a chart with three bars |
| one amount many times another | `Compare` (area proportional) | a bigger icon scaled by its side |
| events in order | `Timeline` | a table of dates |
| a process, a loop, a cause and effect | `Flow` (grid, or `cycle=` for a loop) | prose bullets with arrows |
| where something is, or differs by region | `Map`: highlight, choropleth (with a key), points, routes | a table of provinces when the pattern is spatial |
| a value across two categories at once | a grouped bar or a heat table first; `Bars3D` only when the 3D view itself helps | 3D for one dimension |
| a quantity over a plane (rate x term) | `Surface3D`, or a small multiple of lines | a 3D chart for decoration |
| how a power system is connected, where power flows | `SLD` with flow labels | a block diagram with no symbols |

Audience (item 20): readers are curious generalists in Indonesia and abroad. Prefer the
plainer form, units in words, no acronym the post has not explained (and no abbreviation in a
figure without spelling it out: kramdown's tooltips do not reach inside SVG). Put the
technical detail in the data table and the note.
