# Objects: the library and how to build one

Every scene is made of objects. An object is built once, in its own space, with care on
every side, then placed: `s.place(model, x, y, z, rot=0, mirror=False, scale=1, **options)`
returns an instance with `.anchors` and `.bb`. Its parts still sort one by one against the
rest of the scene, so a person sits *on* the bench and an arm passes *in front of* the
counter; the object is a group for building and arranging, not a single layer.

`python3 .claude/skills/isometric-illustration/scripts/sheet.py --catalog --out <dir>` draws the
whole library; `sheet.py <name> --out <dir>` draws one object from all four sides in both
themes. Look at the sheet before you use a new or changed object.

## The library (`scripts/models.py`)

Footprint is x by y by height at rot=0 with default options; the front faces +x.

| model | what | footprint | options | anchors |
|---|---|---|---|---|
| `bench` | Slatted park bench | 0.6 x 1.8 x 1.2 | length=1.8, seat=0.6, mat='wood', leg='steel' | seat x2 |
| `chair` | Chair | 0.6 x 0.6 x 1.2 | seat=0.6, mat='wood', cushion=None | seat |
| `stool` | Square stool | 0.5 x 0.5 x 0.6 | seat=0.55, mat='wood' | seat |
| `table` | Table | 0.9 x 1.4 x 1.1 | length=1.4, depth=0.9, height=1.1, mat='wood' | top |
| `desk_set` | A desk with a chair, an open laptop, a lamp, a mug and papers | 1.5 x 1.6 x 1.7 | length=1.6, mat='wood', chair_mat='navy' | top, knee, seat |
| `counter` | Shop counter along y | 0.9 x 2.5 x 1.8 | length=2.4, height=1.3, color='blue', top='paper', register=True | staff, customer x2 |
| `shelf` | Gondola shelf of goods along y, goods facing +x | 1.0 x 3.6 x 2.6 | length=3.6, tiers=3, height=2.6, seed=1, sides=1 |  |
| `fridge` | Drinks fridge with glass doors on the front (+x) | 1.2 x 2.4 x 3.0 | width=2.4, height=3.0, depth=1.2 |  |
| `crate` | Wooden crate of fruit | 0.9 x 1.2 x 0.7 | fruit='coral', length=1.2, depth=0.9, height=0.7, price=True |  |
| `trolley` | Shopping trolley, the handle at -x | 1.6 x 0.8 x 1.4 | items=('coral', 'gold', 'teal') | push |
| `food_cart` | Street food cart along y: a decorated customer side at +x, a big wheel on each long side, a glass case of food, a pot with steam and a striped canopy | 1.6 x 3.0 x 3.5 | length=2.6, color='coral', canopy=True | seller, seller_back, customer x2 |
| `atm` | ATM kiosk, screen to the front (+x) | 0.8 x 0.9 x 2.1 | color='brand' | user |
| `bin` | Litter bin | 0.6 x 0.6 x 0.8 | color='teal' |  |
| `plant` | Potted plant | 0.6 x 0.6 x 1.3 | size=1.0, pot='amber' |  |
| `tree` | Voxel tree, trunk at (0.55, 0.55) x size | 1.1 x 1.1 x 2.1 | kind='round', size=1.0, leaf='leaf' |  |
| `street_lamp` | Street lamp, the arm reaching +x | 1.0 x 0.3 x 3.6 | height=3.6 |  |
| `house` | House with a gable roof, the door on the front (+x) | 2.4 x 2.6 x 2.8 | width=2.4, depth=2.0, height=1.5, roof='coral', wall='white', lit=True | door |
| `shopfront` | Shop house: a glass shop front with goods and an awning on the front (+x), a sign band (bars, no text), windows and an air conditioner upstairs, a parapet | 3.3 x 3.3 x 6.2 | width=3.0, depth=2.6, floors=2, awning='coral', sign='brand', wall='white' | door, window |
| `car` | Car, its nose at +x | 3.8 x 2.0 x 1.6 | color='sky', length=3.8, width=1.7 |  |
| `motorbike` | Step-through scooter, the front wheel at +x | 1.8 x 0.7 x 1.2 | color='red' | rider |
| `pylon` | Lattice transmission tower, centred on (0.6, 0.6), arms along y | 1.5 x 2.6 x 7.1 | height=6.5, arms=(-1.0, 0.0, 1.0) | phase x3, peak |
| `transformer` | Oil transformer on a plinth: fins all round, a conservator tank and three bushings | 1.8 x 1.8 x 2.5 | color='teal' | bushing x3 |
| `gantry` | Substation line gantry, the beam along y | 0.2 x 3.9 x 4.2 | span=3.85, height=4.0, pegs=(-1.1, 0.0, 1.1) | peg x3 |
| `cooling_tower` | Hyperbolic cooling tower centred on (r0, r0), with steam | 4.0 x 4.0 x 8.8 | r0=2.0, r1=1.4, height=5.4, steam=True, color='white' |  |
| `chimney` | Striped stack centred on (0.75, 0.75) on a round footing | 1.5 x 1.5 x 8.8 | r=0.55, height=7.6, smoke=True |  |
| `solar_panel` | Solar panel on a frame, tilted up towards -x (the sun side) so its cells face the viewer when turned rot=180 | 1.1 x 2.0 x 1.2 | length=2.0, tilt=0.6 |  |
| `fence` | Mesh fence along y with posts | 0.1 x 4.0 x 1.0 | length=4.0, height=1.0, spacing=0.8 |  |
| `coin_stack` | A stack of coins centred on (0.25, 0.25) | 0.5 x 0.5 x 0.4 | coins=6, color='gold' |  |
| `cash_stack` | Bundles of banknotes with paper bands, slightly askew | 0.7 x 0.4 x 0.4 | bundles=4, color='green' |  |
| `piggy_bank` | Piggy bank, snout to the front (+x), a coin slot on top | 1.1 x 0.6 x 0.9 | color='rose' |  |
| `laptop` | Open laptop | 0.3 x 0.5 x 0.3 | color='steel' |  |

Helpers in `models.py`: `wheel(m, cx, cz, r, y0, y1, ...)` (a round wheel on an axle along
y; `wheel_part` places one with its axle along x), `around(m, part, fn)` (marks on several
faces, `fn(width, height, face)` returns the shapes for each).

## Placing

- `rot` turns an object about z in 90-degree steps: 0 front to +x (lower right), 90 to +y
  (lower left), 180 to -x and 270 to -y (both turned away from the viewer). With rot=90
  the object's own y axis runs along -x, so `place(m, X, Y, rot=90)` covers x from
  `X - length` to `X`: check the plan (`render.py` writes `<name>-plan.png`).
- `mirror=True` flips the object across its own x axis before turning it. With rot=90 its
  y axis then runs along +x, so it covers x from `X` to `X + length`.
- The placing point snaps to the scene grid; the object's own measures do not snap, so fine
  detail (a 0.02 inset, a 0.04 rail) stays exact.
- Objects can place objects (`desk_set` places a chair and a laptop): the parts' anchors
  become the whole's anchors.
- People go on anchors: `s.person_at(inst.anchor("seat", 1), **look)` stands or seats them
  centred on the spot, facing the anchor's way. Free people use `s.person(...)` as before.
- Wires run between anchors: `s.wire(a.anchor("phase", 0).p, b.anchor("phase", 0).p, sag)`.

## Building a new object

Write it as a function in the scene file (`_illustrations/<name>.py`), or in `models.py`
when other posts will want it. Follow the conventions, render its sheet, fix, then place it.

```python
def kiosk(m, color="brand"):
    """Newspaper kiosk, the window to the front (+x). 1.2 x 1.4 x 2.6.
    Anchor: 'seller' (inside, facing +x), 'customer' (facing -x)."""
    body = m.box(0, 0, 0, 1.2, 1.4, 2.2, "white", top="panel")
    m.mark(body, "front", [("rect", 0.15, 1.0, 1.1, 0.8, "glass"), ("rect", 0, 0, 1.4, 0.15, color)])
    for f in ("left", "right", "back"):                      # every side gets something
        m.mark(body, f, [("rect", 0, 0, 1.2 if f != "back" else 1.4, 0.15, color)])
    m.box(-0.1, -0.1, 2.2, 1.4, 1.6, 0.15, color)            # roof, sitting on the body
    m.anchor("seller", 0.5, 0.7, 0, "+x")
    m.anchor("customer", 1.6, 0.7, 0, "-x")
```

1. **Own space.** Origin at the footprint's back corner on the floor; the front faces +x.
   Keep the footprint in positive x and y where you can.
2. **Parts only touch.** Something resting on a part starts exactly at its top; side by side
   parts share a face. The sheet lists any pair that passes through the other. Fuse with
   `m.group()` only for contents inside a see-through box (goods behind glass).
3. **Every side carries detail.** Any face can be turned into view. `m.mark(part, face,
   shapes)`: face `front`, `back`, `left`, `right` or `top`; `a` runs left to right and `b`
   up as you look at that face (the top: `a` along +x, `b` along +y). Aim for 2 to 4 marks
   on each face of anything the eye lands on.
4. **Borders follow the form.** Parts that make one soft or continuous thing (a crown of
   leaves, a cushion, a cloth) go inside `with m.outline():`, so the ink runs only round their
   outer silhouette. Separate hard parts keep their own borders.
5. **Round things.** `m.cylinder` for upright drums, cans, poles; `wheel()` for wheels. A
   polygon with `inside=<a point inside the solid>` is drawn only while it faces the viewer,
   for other prisms that turn with their object.
6. **Anchors** for every spot a person or a cable uses: `m.anchor(name, x, y, z, facing,
   seat=<seat height>)`. A seat anchor is the centre of the sitter's torso at seat height;
   leave 0.48 between it and the seat's front edge so the shins clear it.
7. **Real sizes.** 1 unit is about 0.7 m: a person 2.5, seat 0.6, desk 1.1, counter 1.3,
   door 3.0 x 1.3, one storey 2.8, car 3.8 x 1.7 x 1.6. Openings people pass under (awnings,
   canopies) start above 2.7.
8. **Look at the sheet** in both themes, from all four sides: every face reads, nothing
   floats or sinks, 0 parts passing through each other. Then place it.
