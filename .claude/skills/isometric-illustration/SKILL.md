---
name: isometric-illustration
description: Draw an isometric illustration for a post on this blog in code, not with an image model. Blocky people and the places and machines around them (a market, a station, an office, a food stall, a power plant, a substation, a street, a house, a city block) on a 30-degree grid, with ink outlines in the blog's palette and exact 3D layering, published as a matched pair of SVGs for the dark and light themes (plus an optional looping GIF and a WebP card). Use when Adjie asks for an isometric picture, scene, diagram or animation, or when a post needs a picture of a place or a system with several people or objects, exact counts or layout, or a version for each theme. For one person doing one action in a soft hand-drawn style, use wikihow-illustration instead.
---

# Isometric illustration

Drawn with code. `scripts/iso.py` is an isometric engine. A scene is a Python `build(s)` in
`_illustrations/<prefix>-iso-<subject>.py` (Jekyll skips folders that start with `_`, so it
stays in git, unpublished). `scripts/render.py` draws it once per theme from the same
geometry, checks the layering and publishes the pair. No API key, no cost, and the picture
can be changed and redrawn exactly.

```
brief -> plan on the grid -> _illustrations/<name>.py -> render.py --out (look, fix, repeat)
      -> render.py --publish [--card] -> <figure class="iso-art"> in the post
```

## Which illustration skill

| | wikihow-illustration | isometric-illustration |
|---|---|---|
| Shows | one person doing one action, mid-shot | a place or a system: several people, buildings, machines, flows |
| Made by | an image model (needs a key, costs money) | code in this skill (free, exact, editable) |
| Output | one WebP on its own pale background | an SVG pair that follows the reader's theme; GIF and WebP card optional |
| Words in the picture | a word or two allowed | none: labels go in the caption or the prose |
| Best for | a step, a habit, a feeling | how something works, where things are, how many, a before and after |

## The look (non-negotiable)

- **Grid first.** Every scene sits on the isometric lattice (30-degree axes, no perspective).
  `box`, `tile` and `poly` snap to a 1/20 sub-grid, so edges sit on lattice lines and
  decimal measures (0.6, 1.35) stay exact. Details go on faces with `face_mark`, never as
  loose 2D shapes.
- **Characters** are blocky adults about 3.7 heads tall: a cube head with a painted face,
  hair painted on the head plus a thin hair volume, a neck, shoulders wider than the head,
  arms with hands that reach the upper thigh, two legs and shoes. Use `s.person()`; every
  option is in `references/characters.md`. Vary skin, hair and outfit across a crowd, and
  use local dress where it fits the post (batik, hijab).
- **Objects carry detail**, not bare boxes: goods on shelves, price tags, doors and windows,
  bogies, transformer fins, lit windows. Aim for 2 to 4 marks on each face the eye lands on.
- **Sketch finish:** an ink outline on every face with a slight fixed wobble (it does not
  flicker in GIFs), three-tone shading (top lightest, right darkest), no gradients, glows or
  textures.
- **Palette** = the blog's design tokens only, by role name (`references/palette.md`).
- **No text in the art.** Signs use bars and dots. One pair serves both languages; the
  words live in the alt text and the caption.

## Themes

The blog's dark theme is the default `:root`; light is `:root.light`, a class set before
first paint. So the art ships as two files and CSS in `assets/css/blog.css` shows the one
that matches (see `references/blog-embed.md`).

| | dark (default) | light (`:root.light`) |
|---|---|---|
| page ground (`--bg`) | `#0F1728` | `#F0F4FF` |
| SVG background | transparent | transparent |
| outline | near-black `#060A14` | navy `#14203A` |
| "white" objects | mid slate `#3A4B6B` (never near-white) | `#FFFFFF` |
| shadows | black 35% | navy 10% |

The floor is one tonal step off `--bg`, so the scene sits in the page. Lit windows
(`!light_on`) stay warm in both themes.

## Layering: how it works

Every primitive is its own sortable unit: each box of a person (shoe, leg, torso, arm,
hand, head, hair), each bench part, each lattice member and each piece of cable. For every
pair of units whose drawings overlap on screen the renderer decides who is in front: if
their 3D bounding boxes are separated on x, y or z, the one that ends first is behind;
otherwise it intersects their projected faces and compares the depth of the two surfaces
in the overlap. The pairs are topologically sorted. This is exact for anything that does
not pass through anything else, including people next to each other, people on benches,
diagonal lines, wires, roofs and cylinders.

The author's part:

1. **Nothing passes through anything.** `render.py` lists every pair of boxes that pass
   through each other (a shin through a bench seat, a pillar through its base plate, a
   person sunk into a platform), and `--publish` refuses while any remain. Move or trim the
   part; touching is fine. A thing standing on a surface starts exactly at its top.
2. **People keep clear.** Leave about 0.05 between a person and furniture. Walkers in an
   animation each keep their own lane (lanes 1.0 or more apart) and never walk through a
   pillar, a bench or each other.
3. **Cables use `s.wire(a, b, sag)`**, which splits them into short pieces. Lattice members
   may be single lines: lines that only meet at a joint never fight.
4. **`s.group()` only for small props whose parts really interpenetrate** (goods inside a
   translucent cart basket). A group sorts as one unit, so keep it small.
5. **Cycles.** The report says how many cyclic overlaps were broken. 0 is normal; 1 or 2
   where a cable crosses a member inside a lattice is harmless; more means parts pass
   through each other somewhere (the report names them).
6. **`face_mark` details stick to the face they are drawn on**: the box whose face holds the
   anchor point, or `on=<handle>` (every `box()` returns one) when two faces share a plane.

## Composition: what reads

- Back walls at x = 0 and y = 0, the front (+x, +y) open. Tall things at the back; a tall
  thing in front hides the scene.
- People stand in open foreground cells, not in aisles behind shelves.
- **Never park a solid object directly behind something see-through** (a lattice pylon, a
  fence, a glass roof): it reads as sitting inside it, even though it layers correctly. Move
  it sideways on screen (change x - y), not only further back.
- Faces show only when a person faces `r` or `l`; `ul` and `ur` show their back, for people
  walking away. Turn people towards the action or the reader.
- The scene is the subject: pick props native to the post's topic so the silhouette reads
  without labels (a food stall has a cart, stools and hanging snack packets; a substation has
  transformers, a gantry and a fence).
- Scale, 1 unit = about 0.7 m: person 2.5 tall, seat 0.6, table or desk 1.1, counter 1.3,
  door 3.0 x 1.3, one storey 4.2, car 6 x 2.6 x 2.1, train body 3.0 tall. People at
  `h=1.1` to `1.2` stay readable in a wide scene at unit 20; children are `h=0.6` to `0.8`.

## Workflow

1. **Brief.** In the post plan when the post goes through `ai-assisted-blog-post`: what the
   scene shows and why the post needs it, who is in it, the three to five props that make
   it read, still or animated, the section it goes in, and the alt text in each language.
2. **Plan on the grid.** Sketch the footprint in cells: x runs lower-right, y lower-left.
   Note heights against the scale above.
3. **Write `_illustrations/<prefix>-iso-<subject>.py`** with `TITLE`, `DESC`, `UNIT` and
   `build(s)` (or `build(s, t)` when animated), starting from the closest example in
   `scripts/examples/`:
   - `characters.py`: every hair style, outfit, facing, pose and held thing (the reference
     sheet; run it after changing the rig)
   - `supermarket.py`: a room diorama with walls, shelves of goods, fridge, crates, cart,
     checkout
   - `train_station.py`: an animated loop with a clipped moving train, portals, a glass
     canopy, benches and walkers in two lanes
   - `power_grid.py`: a plant, cooling towers, substation, lattice pylons, wires, houses
     with gable roofs, trees
   - `food_stall.py`: a small street scene with a cart, a striped canopy, goods inside a
     glass case (a `group`), a seller, a seated customer seen from behind, a child
4. **Render to the scratchpad:**
   ```sh
   python3 .claude/skills/isometric-illustration/scripts/render.py \
     _illustrations/<name>.py --out <scratchpad>/iso
   ```
   It prints the layering report and writes both SVGs, a preview of each, `<name>-pair.png`
   (both themes side by side) and `<name>-gridcheck.png` (the lattice over the art).
5. **Look before publishing.** Open the pair and the gridcheck. Crop and zoom into the busy
   spots: faces, hands and held things, people beside furniture, wires at pylons, cylinder
   bases. Check: 0 parts passing through each other; every face reads (eyes, mouth, hair);
   nothing important hides behind something tall; the dark version is as clear as the light
   one. Fix and render again.
6. **Publish.** Add `--publish` to copy the pair to `assets/img/` and print the `<figure>`
   to paste; write the alt text in the post's language on both images. If the scene is the
   post's lead picture, add `--card` for a light WebP card and put the `thumbnail:` and
   `share_image:` lines it prints in the front matter, then run `node _build/og.mjs`.
7. **Run the checks in `CLAUDE.md`** and commit the scene file with the SVGs (and the card).

## Animation

- Every motion is periodic in `t`: `x = a + ((t + phase) % 1) * span` and
  `walk = sin(2 * pi * (n * t + phase))` with n a whole number.
- Clip moving objects to a window and hide the ends in portals or buildings (`train()` in the
  station example).
- 24 to 36 frames at 12 fps; keep each GIF under about 1.5 MB. GIFs are flattened on the
  exact `--bg`, so place them only on the page ground. Pair every GIF with the still SVG for
  readers who prefer reduced motion (`references/blog-embed.md`).

## Primitives (`scripts/iso.py`)

`box` (returns a handle), `tile`, `shadow`, `poly` (shaded from its normal: roofs, gables),
`line`, `wire`, `cylinder` (with `bands`), `tower` (cooling tower), `cloud`, `face_mark`
(`rect`, `poly`, `line`, `ell`, `ring`, `arc` on the `r`, `l` or `t` face), `tree`, `bench`,
`person`, `group`, `tag` (names the parts made inside it in the report), `check`. Add new
props as functions in the scene file, and move them into `iso.py` once two scenes use them.

## Requirements

Python 3 with `cairosvg` and `Pillow` (`pip install cairosvg pillow` if missing). Nothing
else: no network, no key.

`references/related-work.md` notes what other isometric skills and engines exist and why
this one draws in code.
