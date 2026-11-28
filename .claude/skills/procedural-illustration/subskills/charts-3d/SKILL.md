# 3D graphs

`Bars3D`, `Surface3D`, `Blocks3D` (`scripts/pi/iso3d.py`): isometric (30 degrees, no
perspective), flat role colours, the right face darkened and the top lightened with the
theme's `shade` and `light` tokens (MM-ify's multiply shading). Gallery: `bars3d`, `surface`,
`blocks`.

**Use 3D only when the third dimension is data** (checklist item 6). A 3D bar for one
category, a 3D pie, a tilted donut are decoration and are refused. First ask whether a 2D form
reads better: a grouped bar or a heat table for two categories, small-multiple lines for a
surface. 3D earns its place when the shape of the whole is the point (load peaks across seasons
and hours; interest rising with rate and term together; a pile of rice as a volume).

## Components

- `Bars3D(rows, cols, values, roles=None, fmt=None, label='max'|'all'|[(r, c)])`: a value for
  each pair of two categories. Rows are labelled on the front-right edge, columns on the
  front-left edge. Label only the values the story needs; the data table has all.
- `Surface3D(xs, ys, grid=None, f=None, axes=(x, y, z names), bins=None)`: a quantity over a
  plane, painted in five steps of the sequential ramp with a key.
- `Blocks3D(items, base=5, unit=, key=)`: unit cubes filling `base x base` layers. One cube =
  one stated amount (`key='One cube = 10 kg'`).

## Interactive 3D

A rotatable chart belongs to the tool site: embed it with `brotools-embed` (the embed viewer
draws Plotly `gl3d`). MM-ify's three.js viewer is not used on the blog.
