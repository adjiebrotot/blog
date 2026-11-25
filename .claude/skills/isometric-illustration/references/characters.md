# Characters: `Scene.person()`

```python
s.person(x, y, z=0, facing="r", h=1.0, skin="skin2", hair="hair1", hair_style="short",
         top="blue", outfit="shirt", bottom="pants", pose="down", holding=None, carry=None, ...)
```

`(x, y, z)` is the back corner of the standing footprint, the corner nearest the top of the
screen. `z` is the floor, or the seat top when the person sits. The footprint is about
0.85 x 0.7 units (more with a bag or suitcase, a stride or a whole-body pose), and the person
is about 2.55 units tall at `h=1`. People are not snapped to the grid, so they can stand on
off-grid floors and seats.

The rig lives in `scripts/people.py`. `scripts/examples/characters.py` draws every option
below. Run it after any change to the rig and look at it zoomed in, in both themes, at the
size of the sheet (unit 40) and at a scene's size (unit 20 to 26).

## How a person is built

- **Skeleton and poses.** Joints are placed in body space (f forward, s towards the viewer's
  side, z up) and solved with two-bone IK, so an arm or a leg can point anywhere: a stride, a
  knee raised to run, a forearm on a knee. The pelvis can drop and the upper body can lean;
  lying poses turn the whole body onto its back or side.
- **Limbs are tubes** (`Scene.tube`): rounded, tapered segments with three-tone shading.
  Garments are segments of the same tube: a sleeve is wider than the arm and ends in a hem
  (with the dark inside showing when the opening faces the viewer), trousers break over the
  shoe, stripes run round the sleeve.
- **Torso, head, hair, shoes and held things are faceted solids** (lofts of rounded rings),
  so the shading reads as a curved surface. The shirt is its own shell over the trousers: an
  untucked hem overhangs them and casts a shadow, a tucked shirt goes under a belt, a jacket
  hangs lower and wider.
- **Details are painted on the facets** and clipped to each one, so a pattern runs on round a
  curved torso and a hairline round a curved head: the face, the hairline and its shadow on
  the forehead, collars, buttons, pockets, batik, stripes, hi-vis bands.
- **One body, one outline.** The whole person is one soft outline group: ink only on the
  outer silhouette; a thin line in a darker shade of a part's own colour where it passes in
  front of another part (an arm over the torso, the near leg over the far one); no line at
  all where parts meet at the same depth (hair into the forehead, sleeve into the shirt,
  thigh into the hips). Hair, garments and limbs read as single pieces. The line gets finer
  on small people (`unit * h` below 40).
- **Detail follows size.** Below about 17 px of head the face is simple (dot eyes, a line
  mouth, no modelled nose). From there up it has eye whites, irises with a highlight, upper
  lids, shaped brows, a modelled nose and lips. From about 34 px of head it also gets lashes,
  lower lids, nostrils, mouth corners, a chin line and laces. A sheet at unit 40 shows the
  middle level; a portrait needs unit 50+ at `h=1`.

## Proportions (h = 1)

| part | measure | notes |
|---|---|---|
| head | 0.72 tall, 0.64 wide | eyes at mid-height, ears at eye level, a modelled nose |
| neck | 0.07 radius | a shade darker than the skin |
| torso | shoulders 1.66, waist 1.18, hips 0.98 | wider at the chest, narrower at the waist |
| arms | upper 0.35, forearm 0.29, hand 0.15 | hands reach the upper thigh |
| legs | thigh 0.45, shin 0.44 | hips at 0.98 |
| shoes | 0.39 long, 0.13 high | a sole in a darker (or white) band |

A child is `h=0.6` to `0.8`; the head shrinks more slowly than the body (by the square root
of `h`).

## Options

| option | values | notes |
|---|---|---|
| `facing` | `r`, `l`, `ul`, `ur` | `r` heads lower right (+x), `l` lower left (+y): face visible. `ul` heads upper left (-x), `ur` upper right (-y): the back is visible. Lying poses: the way the head points |
| `h` | 0.6 to 1.3 | body scale. Use 1.1 to 1.2 in wide scenes at unit 20 |
| `skin` | `skin1` to `skin4` | vary across a crowd |
| `hair` | `hair1` to `hair5` or any palette name | for `hijab` this is the scarf colour |
| `hair_style` | `short`, `sidepart`, `quiff`, `spiky`, `curly`, `bun`, `ponytail`, `pigtails`, `long` (with a lock over the near shoulder), `bob`, `bald`, `cap`, `hardhat`, `hijab` | `hijab` frames the face, covers the head and drapes over the shoulders |
| `hat` | palette name | colour of `cap` and `hardhat` |
| `outfit` | `tee`, `shirt` (collar, placket, buttons, pocket, tucked under a belt), `polo` (tucked), `batik` (long sleeves, gold motif all round), `batik_short`, `suit` (lapels, a shirt collar, buttons, pocket square; add `tie=`; shirt cuffs show), `jacket` (open over `inner`), `cardigan` (open over `inner`, buttons), `stripes` (stripes in `inner`, round the sleeves too), `hoodie` (hood behind the neck, pocket, drawstrings), `hivis` (reflective bands, sleeves in `inner`), `apron` (an apron panel in `inner` over the front), `dress` | `top` is the main colour. Every outfit has a front, sides and a back |
| `inner`, `sleeve`, `tie` | palette names | shirt under a jacket, a sleeve override, the tie |
| `bottom`, `skirt`, `shorts`, `shoe` | palette names; `shorts=True` | `skirt` (or `outfit="dress"`) adds a knee-length skirt, the legs below show `bottom` (pass a skin name for bare legs); `shorts` ends the trousers above the knee |
| `eyes` | `dot`, `happy`, `wink`, `closed` | lying poses default to `closed` |
| `eye_color` | palette name | the iris, `iris` (dark brown) by default |
| `mouth` | `smile`, `grin` (teeth), `open`, `o`, `flat`, `frown` | |
| `brows`, `blush` | bool | brows default on; blush for children or cheerful faces |
| `glasses` | colour (`_face` for dark frames) | tinted lenses, the arm runs back to the ear |
| `beard` | `True` (hair colour) or a palette name | a full beard joined to the sideburns, and a moustache |
| `pose` | arms: `down`, `hold` (both forearms forward), `phone` (near hand up with a phone), `point`, `wave`, `cheer` (both arms up), `hips` (hands on hips), `think` (hand at the chin). Whole body: `run`, `jump`, `squat`, `kneel`, `floor` (cross-legged on the floor), `lie` (on the back), `sleep` (curled on the side) | sitting people (`sit=`) rest their forearms on their thighs; `squat`, `kneel` and `floor` rest them on the knees |
| `arms` | any arm pose | overrides the arms of any pose: `pose="squat", arms="hold", holding="box"` |
| `lean`, `nod` | radians | lean the upper body forward (+) or back; tip the head down (+) or up. Poses set their own |
| `air` | units | height of a `jump` (0.6) or a `run` (0.1) above the floor; the shadow stays on the floor |
| `holding` | `box`, `tablet`, `laptop`, `book`, `clipboard`, `plate`, `cup` | with `pose="hold"`, on the lap when sitting, or with `arms="hold"`/`"knees"`. `hold_color` overrides the colour |
| `carry` | `bag`, `basket`, `briefcase`, `suitcase` (rolled behind) | in the near hand while standing. `carry_color` sets the colour |
| `walk` | -1 to 1 | stride phase (and the phase of `run`). Animate with `sin(2*pi*(n*t + phase))`, n a whole number |
| `sit` | seat height (0.6 for an adult seat) | then `z` is the seat top. The thighs rest on the seat, the shins come down to the floor in front of it |

## Poses and space

- `run`, `jump`: the body leaves the floor (`air`); keep about 1.5 units clear around them.
- `squat`, `kneel`, `floor`: about 1 x 1 unit; the knees come forward about 0.5.
- `lie`: about 2.6 units along `facing` and 0.85 across, face up. Put it on a bed or a mat
  (`z` = its top). `sleep` lies on the far side with the knees drawn up and the face towards
  the viewer: about 2.6 x 1.2 units.
- Lying people have no pillow or blanket of their own: place a mat, bed or cushion object.

## Seating and standing at objects

Objects offer anchors: a bench or chair a `seat` per place, a counter `staff` and
`customer`, an ATM a `user`, a food cart a `seller`. `s.person_at(anchor, **look)` puts
someone there, centred on the spot, facing the anchor's way, sitting at the right height:

```python
b = s.place(bench, 3.8, 3.3, 0.6, rot=90)                 # on a platform at z 0.6, seats face +y
s.person_at(b.anchor("seat", 0), holding="book", hair_style="bun", top="teal")
till = s.place(counter, 12.2, 7.4, rot=90, length=3.2)
s.person_at(till.anchor("staff"), outfit="apron", hair_style="cap")
```

`s.person_center(cx, cy, z, facing=...)` places by the torso's centre for your own spots. A
sitting person needs about 0.5 between the seat anchor and the seat's front edge for the
shins.

## Crowds

- Mix skin tones, hair styles and outfits; repeat a combination only on purpose (a uniform).
- Give each person room: about 1 unit between people standing side by side.
- In an animation each walker has a lane; walkers heading the other way use `ul` or `ur`.
- Turn faces towards the action or the reader. A back view is for someone leaving, queuing,
  or looking at the same thing the reader looks at.
- A person costs about 60 to 150 drawn parts (more at portrait size), so a scene of 10 to 15
  people renders in a few seconds; a sheet of 50 takes about 15.
