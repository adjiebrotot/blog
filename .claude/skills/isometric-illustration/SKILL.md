---
name: isometric-illustration
description: Draw an isometric illustration for a post on this blog in code, not with an image model. People (with detailed faces, clothes that sit on the body, and poses from walking to jumping, squatting, sitting and lying down) and the places and machines around them (a market, a station, an office, a food stall, a street, a power plant, a substation, a house, a city block) on a 30-degree grid, with ink outlines in the blog's palette and exact 3D layering, built object first (each object crafted on all sides from a library, then placed and turned in the scene) and published as a matched pair of SVGs for the dark and light themes (plus an optional looping GIF and a WebP card). Use when Adjie asks for an isometric picture, scene, diagram or animation, or when a post needs a picture of a place or a system with several people or objects, exact counts or layout, or a version for each theme. For one person doing one action, an editorial picture or drawn people on a photo, use editorial-illustration.
---

# Isometric illustration

Drawn with code, object first. Every thing in a picture (a bench, a cart, a shop house, a
pylon) is an **object**: built once in its own space, with detail on every side, checked
alone from four sides, then **placed** in the scene with a position and a turn. People
stand or sit on the **anchors** objects offer (a seat, a counter, an ATM), and cables run
between anchors. The parts of an object still sort one by one against everything around
them, so a placed object sits *in* the scene instead of being pasted on top of it.

`scripts/iso.py` is the engine, `scripts/models.py` the object library, `scripts/sheet.py`
draws objects alone, and `scripts/render.py` draws a scene file
`_illustrations/<prefix>-iso-<subject>.py` (Jekyll skips folders that start with `_`, so it
stays in git, unpublished), checks it and publishes the pair. No API key, no cost, and the
picture can be changed and redrawn exactly.

```
brief -> the objects (library, or new ones checked on sheet.py) -> arrange on the plan
      -> render.py --out (look, fix, repeat) -> render.py --publish [--card] -> the post
```

## Which illustration skill

| | editorial-illustration | isometric-illustration |
|---|---|---|
| Shows | one person doing one action (wikiHow), people in a real place (live-action hybrid), or the section's point: a metaphor, a caricature, a mood, a slogan (Tempo, Summer flat, Renaissance collage, propaganda poster) | a place or a system: several people, buildings, machines, flows |
| Made by | an image model (needs a key, costs money) | code in this skill (free, exact, editable) |
| Output | one WebP that carries its own background, in one of six styles | an SVG pair that follows the reader's theme; GIF and WebP card optional |
| Words in the picture | a short quoted phrase at most (a poster's slogan) | none: labels go in the caption or the prose |
| Best for | a step, a habit, a feeling, satire, an argument, a big theme, a social card | how something works, where things are, how many, a before and after |

## The look (non-negotiable)

- **Grid first.** Scenes sit on the isometric lattice (30-degree axes, no perspective).
  Placing points and scene boxes snap to a 1/20 sub-grid; objects keep their own exact
  measures for fine detail.
- **Objects carry craft**: goods on shelves, doors, windows and sills, wheels, lights, seams,
  vents. Every face that can be turned into view gets 2 to 4 marks. A bare box is unfinished.
- **Characters** are adults about 3.5 heads tall with rounded, tapered limbs, a faceted head
  with a painted face (eye whites, irises, lids, brows, a modelled nose, lips, ears), hair
  with volume, and clothes that sit on the body (sleeves with hems, a shirt over or tucked into
  the trousers, a hijab draped over the shoulders). Joints bend, so people can walk, run,
  jump, squat, kneel, sit on a seat or the floor, and lie down (`references/characters.md`).
  Vary skin, hair and outfit; use local dress where it fits (batik, hijab).
- **Sketch finish:** an ink outline with a slight fixed wobble, three-tone shading (top
  lightest, right darkest), no gradients, glows or textures.
- **Borders follow the form, not the construction.** A thing modelled from several boxes but
  meant as one piece (a hijab, a head of hair, an arm, a tree's crown, a cushion) goes inside
  `with s.outline():` (`m.outline()` in an object): the ink runs only round its outer
  silhouette and where it meets other things, and its own seams and creases are left to the
  shading. Hard, separate parts (bench slats, a car's cabin, shoes) keep their own borders.
  A person is one soft outline group (`outline(key, soft=True)`): ink on the outer
  silhouette only, a thin line in a darker shade of its own colour where one part passes in
  front of another, and no line where hair, garments and skin meet.
- **Palette** = the blog's design tokens, by role name (`references/palette.md`).
- **No text in the art.** Signs use bars and dots. One pair serves both languages.

## Themes

The blog's dark theme is the default `:root`; light is `:root.light`, a class set before
first paint. So the art ships as two files and CSS in `assets/css/blog.css` shows the one that
matches (`references/blog-embed.md`).

| | dark (default) | light (`:root.light`) |
|---|---|---|
| page ground (`--bg`) | `#0F1728` | `#F0F4FF` |
| SVG background | transparent | transparent |
| outline | near-black `#060A14` | navy `#14203A` |
| "white" objects | mid slate `#3A4B6B` (never near-white) | `#FFFFFF` |
| shadows | black 35% | navy 10% |

## Workflow

1. **Brief.** In the post plan when the post goes through `ai-assisted-blog-post`: what the
   scene shows and why the post needs it, the objects that make it read, who is in it and
   what they do, still or animated, the section it goes in, the alt text in each language.
2. **Objects.** List every object the scene needs and take each from the library
   (`references/models.md`; `sheet.py --catalog` draws them all). For one the library lacks,
   build it as a function in the scene file, or in `models.py` if other posts will reuse it,
   following the conventions in `references/models.md`. Draw it alone from four sides:
   ```sh
   python3 .claude/skills/isometric-illustration/scripts/sheet.py _illustrations/<name>.py:<model> --out <scratchpad>/iso
   ```
   Look at both themes and all four sides, fix it until every face reads and the sheet
   reports 0 parts passing through each other. Only then use it.
   For a person the library lacks (a pose, a hair style, an outfit, a held thing), extend the
   rig in `scripts/people.py` following `references/people-rig.md`, and check it alone:
   `sheet.py person --kw pose="'kneel'" --unit 80 --out <scratchpad>/iso`.
3. **Arrange.** Sketch the layout in cells (x runs lower right, y lower left; back walls at
   x = 0 and y = 0, the front open). Write `build(s)` in
   `_illustrations/<prefix>-iso-<subject>.py` with `TITLE`, `DESC` and `UNIT`: the ground,
   then `s.place(model, x, y, rot=...)` for each object (rot 0 shows its front at the lower
   right, 90 at the lower left), then people with `s.person_at(obj.anchor("seat"), ...)` or
   `s.person(...)`, then cables between anchors. Start from the closest example in
   `scripts/examples/`:
   - `street_corner.py`: shop houses, an ATM, a house, a food cart, a bench, a car and a
     scooter, people on anchors (the showcase for the library)
   - `supermarket.py`: a room (floor and walls in the scene) with placed shelves, fridge,
     crates, counter and trolley
   - `food_stall.py`: a small scene; a mirrored, turned cart; a seat turned to face it
   - `power_grid.py`: an object made in the scene file (`plant_building`), library power
     objects, wires from anchor to anchor
   - `train_station.py`: an animated loop; scene-made train and canopy, library benches
   - `characters.py`: every hair style, outfit, facing, arm pose, whole-body pose (run, jump,
     squat, kneel, floor, lie, sleep) and held thing
4. **Render to the scratchpad:**
   ```sh
   python3 .claude/skills/isometric-illustration/scripts/render.py _illustrations/<name>.py --out <scratchpad>/iso
   ```
   It prints the layering report and writes both SVGs, `<name>-pair.png` (both themes),
   `<name>-plan.png` (a top-down map of every object, person and anchor on the grid, for
   spacing and turning) and `<name>-gridcheck.png`.
5. **Look before publishing.** The plan first: objects where you meant them, people clear of
   each other, nobody standing in a doorway or on a kerb. Then the pair, zoomed into the busy
   spots: faces, hands and held things, people at objects, wires at pylons. `check()` lists
   boxes that pass through each other, not people: look yourself that no limb goes through a
   table, a counter or another person. 0 parts passing
   through each other; every object turned so its detailed side shows; nothing important
   hidden behind something tall; dark as clear as light. Fix and render again.
6. **Publish.** `--publish` copies the pair to `assets/img/` and prints the `<figure>` to
   paste; write the alt text in the post's language on both images. If the scene is the
   post's lead picture, add `--card` and put the `thumbnail:` and `share_image:` lines it
   prints in the front matter, then mark the card's focus box (step 7) before
   `node _build/og.mjs`.
7. **Mark the card's focus box (mandatory for every `--card`).** The post cards, social card
   and share poster crop the card to other shapes around its box in `_data/focus.yml`. Follow
   `.claude/skills/editorial-illustration/references/focus-box.md` exactly: `--publish --card`
   prints the line to fill in; name the subject in its comment (the person or machine the
   scene is about, such as the cashier at the till or the transformer), box it alone, look at
   every crop with `python3 _build/focus.py --preview <scratchpad>/focus`, and finish when
   `python3 _build/focus.py` says OK. A scene drawn wide with its subject in a corner needs
   the box most; never box the whole scene.
8. **Run the checks in `CLAUDE.md`** and commit the scene file with the SVGs (and the card with its focus line),
   plus `models.py` if you added an object there.

## Layering: how it works

Every primitive is its own sortable unit, including each part of a placed object or a
person. For every pair whose drawings overlap on screen the renderer decides who is in front:
if their 3D bounding boxes are separated on x, y or z, the one that ends first is behind;
otherwise it intersects their projected faces and compares the depth of the two surfaces in
the overlap. The pairs are topologically sorted. This is exact for anything that does not
pass through anything else.

The author's part:

1. **Nothing passes through anything**, inside an object or between objects. `render.py` and
   `sheet.py` list every pair of boxes that pass through each other, and `--publish` refuses
   while any remain. Touching is fine: a thing resting on another starts exactly at its top.
2. **People keep clear**: about 0.05 from furniture, about 1 unit between people side by
   side; anchors already leave the right room. Walkers in an animation keep their own lane.
3. **Cables use `s.wire(a, b, sag)`**, split into short pieces; lattice members may be single
   lines (lines meeting at a joint never fight).
4. **`group()` only for contents inside something see-through** (goods behind glass, in a
   wire basket): a group sorts as one unit, so it stays small.
5. **Cycles.** The report says how many cyclic overlaps were broken. 0 is normal; 1 to 3 where
   a cable crosses a lattice member or a wheel meets a fender are harmless; more means parts
   pass through each other somewhere (the report names them).

## Composition: what reads

- Tall things at the back; a tall thing in front hides the scene.
- Turn objects so their detailed side faces the viewer (rot 0 or 90). Turn them away (180,
  270) only when what matters is behind them, such as the screen of a desk seen from the
  user's side.
- **Never park a solid object directly behind something see-through** (a pylon, a fence, a
  glass roof): it reads as sitting inside it. Move it sideways on screen (change x - y).
- Anyone under a roof or canopy is hidden by it in this view: keep people at the open sides,
  as the anchors do.
- Faces show only when a person faces `r` or `l`; `ul` and `ur` show their back, for people
  walking away or using something.
- The scene is the subject: pick objects native to the post's topic so the silhouette reads
  without labels.
- Scale, 1 unit = about 0.7 m: person 2.5, seat 0.6, desk 1.1, counter 1.3, door 3.0 x 1.3,
  storey 2.8, car 3.8 x 1.7 x 1.6, train body 3.0. People at `h=1.1` to `1.2` stay readable
  in a wide scene at unit 20; children are `h=0.6` to `0.8`.

## Animation

- Every motion is periodic in `t`: `x = a + ((t + phase) % 1) * span` and
  `walk = sin(2 * pi * (n * t + phase))` with n a whole number.
- Clip moving objects to a window and hide the ends in portals or buildings (`train()` in the
  station example).
- 24 to 36 frames at 12 fps; keep each GIF under about 1.5 MB. GIFs are flattened on the exact
  `--bg`, so place them only on the page ground. Pair every GIF with the still SVG for readers
  who prefer reduced motion (`references/blog-embed.md`).

## API (`scripts/iso.py`)

Scene and objects draw with the same calls: `box` (returns a handle), `tile`, `shadow`,
`shadow_poly`, `poly` (with `inside=` to draw only while facing the viewer), `line`, `wire`,
`tube` (rounded, tapered segments: limbs, pipes, hoses, a ball), `cylinder` (with `bands`),
`tower`, `cloud`, `mark(handle, face, shapes)` (`face_mark` is the older form by world
coordinates), `outline` (one border round several parts; `new_outline()` gives a key to join
parts made in different places; `soft=True` for the three line weights a person uses),
`group`, `tag`. Scenes add `place`, `person`, `person_at`,
`person_center`, `tree`, `bench`, `check`, `plan_svg`; objects add `anchor` and nested
`place`. `scripts/models.py` holds the library and the helpers `wheel` and `around`;
`scripts/people.py` holds the character rig.

## Requirements

Python 3 with `cairosvg` and `Pillow` (`pip install cairosvg pillow` if missing). Nothing
else: no network, no key.

`references/related-work.md` notes what other isometric skills and engines exist and why
this one draws in code.
