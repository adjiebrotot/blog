# Palette roles (from the blog's tokens in assets/css/blog.css)

Use these names as `mat`. Never hard-code a hex in a scene unless it is a one-off; if a
colour is needed twice, add it to BOTH palettes in `scripts/iso.py`. The two page grounds
are the blog's `--bg` (`#0F1728` dark, `#F0F4FF` light), so the art sits in the page.

| role | light | dark | use for |
|---|---|---|---|
| `_bg` | #F0F4FF | #0F1728 | page ground (= `--bg`); GIF and card backdrop only |
| `_ink` | #14203A | #060A14 | outlines (= light `--ink-line`; dark is near-black so it reads as a drawing, not a wireframe) |
| `ground` / `floor` / `panel` | #E3EAF7 / #FFFFFF / #DCE3F0 | #162033 / #1C2942 / #2C3A52 | floors, yards, slabs: one step off `--bg` |
| `white` | #FFFFFF | #3A4B6B | buildings, trains, fridges. In dark it stays mid-value, never near-white |
| `wall` | #FFFFFF | #2A3A5A | room walls (a step darker than `white` in dark) |
| `brand` / `blue` / `sky` / `pale` | #0052CC / #3A71C8 / #5A91E8 / #BFD5F7 | #2D67C7 / #2F5FA8 / #4A7BC8 / #36507E | the one brand hue in shades (about 10% of the area) |
| `gold` / `amber` | #F2B24C / #B45309 | #E0A94F / #B7712A | the warm opposite: highlights, safety lines |
| `teal` / `green` / `leaf` / `olive` | #4A9E87 / #8CC9A4 / #4F9E6E / #7D8B4E | #3E8A76 / #3F7A5F / #2F6B4C / #5A6638 | equipment, plants, a third hue |
| `coral` / `red` / `rose` / `purple` / `maroon` | #E66A6A / #E63939 / #C46A7E / #9B59B6 / #8E3B46 | #C85F5F / #C6382F / #A85F72 / #7E4C99 / #6E2E38 | sparing accents: clothes, goods |
| `metal` / `steel` | #AEB9CC / #6E7C8E | #4F5F7A / #3A4760 | structure, rails, pylons |
| `glass` / `light_on` / `screen` | #CFE0FA / #FFD28C / #9CC2F5 | #4A6A9E / #FFD28C / #7FA6E0 | windows; `light_on` stays warm in both so lit windows glow at night; `screen` for tablets |
| `wire` | #14203A | #8DA2C4 | conductors and thin cables (inverted, since `_ink` vanishes on dark) |
| `paper` / `shirt` | #FFFFFF / #F4F7FD | #B8C6DE / #9FB0CC | small light details: labels, collars, price tags (never large areas in dark) |
| `concrete` / `gravel` / `road` | #D3DBE8 / #C9D2E1 / #9AA6BA | #2A3954 / #24314A / #111A2C | yards, track ballast, roads |
| `wood` / `denim` / `khaki` / `navy` | #C98A4B / #4A6FA5 / #C9B48A / #14203A | #8A5A30 / #36507E / #8F7F5E / #2B3A5C | benches, crates, jeans, uniforms |
| `_face` | #14203A | #0B1220 | eyes, brows and mouths |
| `skin1`-`skin4`, `hair1`-`hair5`, `pants`, `shoe`, `blush` | | | characters: vary skin and hair across a crowd |

Shading: faces are the base colour times `_shade` (top lighter, left base, right darker).
Dark lifts the top more (1.18) so form reads under low light.

Ratio: roughly 60% ground and structure neutrals, 30% ink and white/wall, 10% hue.

Mark colours can also be `('~', name, k)` (the colour shaded by k, e.g. a darker seam) or
`'!name'` (emissive: not darkened on the side faces, for lit windows, screens and
reflective strips).
