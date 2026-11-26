# Extending the character rig (`scripts/people.py`)

Read this before adding a pose, a hair style, an outfit, a held thing or a face to the
people. `characters.md` is how to *use* `Scene.person()`; this is how the rig is made and
how to add to it without breaking the look. Most additions are one table row or one short
function.

## Map of `people.py`

| section | holds | you edit it to add |
|---|---|---|
| measures | `CF, CS` (body centre line), hip, knee, shoulder, head heights, `HEAD` (the head's rings), outfit groups (`SHORT_SLEEVES`, `TUCKED`, `OPEN_FRONT`, `LONG_HEM`) | an outfit that is tucked, short-sleeved or long-hemmed |
| helpers | vectors, `Xf` (affine maps: `move`, `pitch`, `scale`), `ik`, `rring`/`hring` (rounded rings), `head_dims`, `keys` | rarely |
| `Rig` | `tube`, `chain`, `ball`, `solid`, `box`, `paint`, `cover` | rarely |
| poses | `WHOLE` + `_pose()` (whole-body poses), `ARM_POSES` (arm poses, a table) | a pose |
| the person | `draw()`: builds the parts in order, pushes the pose frames | a new body part |
| legs, shoes | `_leg`, `_shoe` | trousers, shoe shapes |
| torso, garments | `_torso` (the trousers' seat, the top's shell, the skirt), `_outfit` (painted details), `_apron`, `_hood`, `_drape` | an outfit, a garment |
| arms, hands | `_arm` (sleeve segments), `_hand` | sleeve styles, gestures |
| head, hair | `_head`, `HAIR_STYLES` (a table) + its volume functions (`_long`, `_bun`, ...), `_hijab`, `_hat` | a hair style, a hat |
| face | `_face` (the features), `rig_nose` | an expression, a feature |
| held things | `_held` | something held or carried |

A new option for `Scene.person()` also goes in its signature and the dict it passes on
(`scripts/iso.py`, `Scene.person`), in the options table of `characters.md`, and in a row of
`scripts/examples/characters.py`.

## Space and frames

- **Body space**, at `h = 1`: `f` forward (where the person faces), `s` sideways towards the
  viewer, `z` up; the origin is the back corner of the standing footprint, the floor is
  `z = 0`. The centre line is `f = CF = 0.16`, `s = CS = 0.30`. Everything is written in body
  space; the rig maps it to the world for every facing and size, mirrored when it must be.
- **The near side is `+s`, always** (`facing` r and l show it; ul and ur too, from behind).
  Spend detail on the near side and the front; the far side is mostly hidden.
- **Frames** are pushed with `with rig.xf(X):`, X applied first. `draw()` pushes: the pose's
  `root` (lifts a jump, turns a body onto its back or side), then `U` (the pelvis drop and the
  upper body's lean, about the hips) for the torso, neck and head, then the head frame `H`
  (nod, children's bigger head), in which **head space** has its origin at the middle of the
  chin's level: `f` from the head's centre (the face plane at `FACE_F = 0.33`), `s` from the
  centre line, `z` from the chin (eyes 0.355, brows 0.45, crown `HEAD_H = 0.72`).
- **What moves where on screen:** `+f` goes to the lower right (facing r), `+s` to the lower
  left, `+z` up. So a near arm raised forward or sideways passes in front of the face: raise
  arms up and slightly back (`-f`).

## The building blocks (all on `rig`, in the current frame)

| call | draws | notes |
|---|---|---|
| `tube(segs)` | segments `(A, rA, B, rB, mat, endA, endB)` | rounded, tapered, three-tone; one sortable unit. Ends: `r` round, `f` flat seam (no line), `h` flat with a hem line, `o` an opening (hem line, dark inside when it faces the viewer) |
| `chain([(p, r), ...], mat)` | a one-colour tube through points | hair locks, ponytails, a hood, the neck |
| `ball(p, r, mat)` | a sphere | a bun, a curl, a hair tie, a wheel |
| `solid(rings, mat, top=, bottom=)` | a loft through rings of points | faceted, shaded by normal. `mat` may be a list, one per band. Returns the faces, for `paint` and `cover` |
| `hring(cf, cs, z, front, back, hw, rf, rb, m)` | a horizontal rounded ring | `m` 1 = chamfered (8 sides), 2 = rounder (12). `rring` is the same in any plane |
| `head_dims(z)` | the head's ring at height z | build hair, hats and scarves from it plus a thickness, so they hug the head |
| `box(c, ea, eb, ec, ha, hb, hc, mat)` | a cuboid on any axes | held things |
| `paint(faces, chart, shapes)` | 2D shapes projected onto every facet that looks that way | charts: `front` (s, z), `back` (s, z), `side` (f, z), `top` (f, s), in the current frame's coordinates. Shapes as `Scene.face_mark` (`rect`, `poly`, `line`, `ell`, `ring`, `arc`). Clipped to each facet, so a pattern runs on round a curved surface; shapes off a facet are dropped |
| `cover(faces, zlo, zhi, mat)` | the band `zlo(angle) < z < zhi(angle)` round a solid | hairlines, beards, a scarf's edge. `zlo`/`zhi` are functions of the angle round the vertical axis (0 = `+f`); build them with `keys((angle, z), ...)` |
| `ik(S, T, a, b, pole)` | the middle joint of a two-bone limb | the joint bends towards `pole` |

Colours are palette names, tones `("~", name, k)` (k < 1 darker, > 1 lighter), or `"!name"`
for paint that is not shaded by its facet (eye whites, hi-vis bands, a screen). Draw lips,
lids, creases in tones of the skin, not in new colours. Line widths in shapes are pixels at
unit 34 and scale with the drawn size.

## Recipes

### An arm pose
Add a row to `ARM_POSES`: `(wrist, elbow pole, hand direction, thumb direction, space[, swing])`,
written for the **near** arm (the far arm mirrors it). The near shoulder is at
`(CF, SO, 1.63)`, `SO = CS + 0.33`; the arm reaches 0.64 (a target further away gives a
straight arm). The pole is where the elbow points (usually back `-f`, out `+s`, or down).
`space` `"u"` moves with the leaning upper body, `"b"` stays in body space (a lap, a knee).
Body-space `z` starts at the person's `z`, which is the **seat top** when they sit, so a hand
on a table is not at the table's height in `"b"`: put it in `"u"` at the height it has for a
standing person (the hips drop 0.84 when sitting, so `"u"` z 1.37 lands on a 1.1 desk from a
0.6 seat; `type` does this). `swing` moves the wrist along `f` with `walk`. Give the arms different jobs with
`{"near": entry, "far": entry or "down"}`. Then add it to `pose` in `characters.md` and a
person in `characters.py`, and check it (below).

### A whole-body pose
Add its name to `WHOLE` and a branch in `_pose()` setting what differs from standing:
`dpel` (pelvis offset; sitting is `0.14 - HIP_Z`), `lean`, `nod`, `root` (an `Xf`: `move` for
a lift, or a matrix that turns the body, as `lie` and `sleep` do), `floor` (where the feet
stand, relative to `z`), `air`, `legs` (per side `True` = near: `ankle` target and knee
`pole`, or an explicit `knee`), `foot` (per side `(direction, up)` of the shoe), the default
arm pose, `shadow` and default `eyes`. Legs are solved by `ik` from the hips, so give ankle
targets the legs can reach (thigh 0.45 + shin 0.44). Add a `_shadow` case if the footprint
is unusual, and state its footprint in "Poses and space" in `characters.md`.

### A hair style
Add an entry to `HAIR_STYLES` (the comment above it lists the fields): the hairline as
`(angle, height)` keys (copy `SIDE` for an ordinary sideburn and ear), the cap's thickness
and fringe, the crown strands, and an `extra` function for any volume. An extra function
`fn(rig, o, t, m)` draws in head space with `chain`, `ball` and `solid`; build shells from
`head_dims(z) + t` so they follow the head, and keep the face open (front at most
`FACE_F - 0.07`). If the style hides the ears add it to `HAIR_COVERED_EARS`; a hat or scarf
goes in `own` instead of a cap.

### An outfit
1. Shape: if it is tucked, short-sleeved, open at the front or long-hemmed, add its name to
   `TUCKED`, `SHORT_SLEEVES`, `OPEN_FRONT` or `LONG_HEM`; the torso shell, hem and sleeves
   follow.
2. Details: add a branch to `_outfit()` that appends shapes to `F` (front), `B` (back), `S`
   (near side) and `T` (top) in body coordinates: `CS` is the middle of the chest, `hem` the
   bottom of the top, 1.77 the shoulders' top. Patterns that should run all round (stripes,
   motifs) go on all three of F, S and B.
3. Separate garments (an apron, a hood, a drape) are their own `solid` or `chain` in front
   of or around the body: see `_apron`, `_hood`, `_drape`.
4. Sleeve patterns are tube segments in `_arm()` (see stripes).

### A face, an expression, a feature
`_face()` builds a list of shapes in the front chart of head space and paints them once.
Gate fine detail on `o["_lod"]` (0 small, 1 normal, 2 close-up) so small people stay clean.
A new `eyes` or `mouth` value is a new branch there plus a line in `characters.md`.

### Something held or carried
`_held()` gets both hands (`w` wrist, `d` hand direction, `palm`, `tip`) and builds the
thing with `rig.box`, `rig.tube` or `rig.solid` between or below them.

## Rules that keep it looking right

- **Draw every body part through `rig`**, never `sc.box` or `sc.poly` directly: `rig` puts it
  in the person's soft outline group, so there is ink only on the outer silhouette, a thin
  shade line where one part passes in front of another, and no line where parts meet at the
  same depth. A part outside the group gets a full border and looks pasted on.
- **Joins:** a limb's end may sit inside a solid (a thigh in the hips, an arm in the
  shoulder, the neck in the head). A shell may contain what it covers (the hair cap over the
  crown, the shirt over the trousers' waistband). Two solids that cross without one
  containing the other will sort wrongly: move one.
- **A step of more than about 0.03 between two surfaces makes a line**; less reads as one
  piece. Use that on purpose: the fringe overhangs to show its edge, the hijab's shell sits
  just behind the face.
- **Facets cost file size.** Use `m=1` rings unless the part is the focus (heads use `m=2`
  from the middle detail level), skip parts that are always hidden, and prefer `paint` to new
  geometry for small things. A person is about 60 to 150 drawn parts.
- **Paint goes under the contour lines.** The renderer draws a facet's fill, then its paint,
  then its lines; do not work around that by drawing outlines as paint.

## Checking a change

1. **The person alone, from all four sides, both themes, large:**
   ```sh
   python3 .claude/skills/isometric-illustration/scripts/sheet.py person --kw pose="'kneel'" --kw hair_style="'bun'" --unit 80 --out <scratchpad>/iso
   ```
   Look at the face, the hands, where the new part meets the body, and the outline.
2. **The character sheet** (`scripts/examples/characters.py`, unit 40), zoomed into the new
   row and its neighbours, in both themes.
3. **A scene at its real size** (`render.py scripts/examples/street_corner.py`, unit 20 to 26):
   small people should stay clean, not fuzzy.
4. **When you only reorganise code**, render the character sheet before and after and
   compare the SVGs: they should be byte-identical.
