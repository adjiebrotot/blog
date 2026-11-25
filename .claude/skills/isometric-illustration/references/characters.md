# Characters: `Scene.person()`

```python
s.person(x, y, z=0, facing="r", h=1.0, skin="skin2", hair="hair1", hair_style="short",
         top="blue", outfit="shirt", bottom="pants", pose="down", holding=None, carry=None, ...)
```

`(x, y, z)` is the back corner of the body's footprint, the corner nearest the top of the
screen. `z` is the floor, or the seat top when the person sits. The footprint is about
0.75 x 0.7 units (more with a bag or suitcase), and the person is about 2.5 units tall at
`h=1`. People are not snapped to the grid, so they can stand on off-grid floors and seats.

`scripts/examples/characters.py` draws every option below. Run it after any change to the
rig and look at it zoomed in, in both themes.

## Proportions (h = 1)

A blocky adult about 3.7 heads tall, built from boxes that only touch each other:

| part | size (forward x across x up) | notes |
|---|---|---|
| shoes | 0.38 x 0.26 x 0.12 | toes 0.07 past the torso front |
| legs | 0.26 x 0.26 x 0.84, 0.04 apart | hips at 0.96 |
| torso | 0.32 x 0.60 x 0.78 | shoulders at 1.74 |
| neck | 0.16 x 0.20 x 0.05 | a shade darker than the skin |
| head | 0.66 cube | the face is painted on the front |
| arms | 0.18 x 0.15, 0.86 long with the hand | hands reach the upper thigh |
| hair | a 0.07 layer on top, painted on the face and sides | volumes for long hair, buns, ponytails |

Because every part is its own box, the sorter places each one against the scene: an arm in
front of a counter, legs behind a bench seat, a walker's head behind a seated person's.

## Options

| option | values | notes |
|---|---|---|
| `facing` | `r`, `l`, `ul`, `ur` | `r` heads lower right (+x), `l` lower left (+y): face visible. `ul` heads upper left (-x), `ur` upper right (-y): the back is visible, for people walking away |
| `h` | 0.6 to 1.3 | body scale. Below 1 the head shrinks more slowly (it scales by the square root of `h`), so `h=0.6` to `0.8` reads as a child. Use 1.1 to 1.2 in wide scenes at unit 20 |
| `skin` | `skin1` to `skin4` | vary across a crowd |
| `hair` | `hair1` to `hair5` or any palette name | for `hijab` this is the scarf colour |
| `hair_style` | `short`, `sidepart`, `quiff`, `spiky` (swept-back), `curly` (two-tier volume), `bun`, `ponytail`, `pigtails`, `long`, `bob`, `bald`, `cap`, `hardhat`, `hijab` | `hijab` wraps the head, frames the face and drapes over the shoulders |
| `hat` | palette name | colour of `cap` and `hardhat` |
| `outfit` | `tee`, `shirt` (collar, buttons, pocket, belt), `polo`, `batik` (long sleeves, gold motif), `batik_short`, `suit` (lapels, buttons, pocket square; add `tie=`), `jacket` (open over `inner`), `cardigan` (open over `inner`), `stripes` (stripes in `inner`), `hoodie`, `hivis` (reflective bands, sleeves in `inner`), `apron` (`inner` = apron colour), `dress` | `top` is the main colour. Each outfit also has a back |
| `inner`, `sleeve`, `tie` | palette names | shirt under a jacket, a sleeve override, the tie |
| `bottom`, `skirt`, `shoe` | palette names | `skirt` (or `outfit="dress"`) adds a knee-length skirt; the legs below show `bottom` |
| `eyes` | `dot` (with a highlight), `happy`, `wink`, `closed` | |
| `mouth` | `smile`, `grin`, `open`, `o`, `flat` | |
| `brows`, `blush` | bool | brows default on; blush for children or cheerful faces |
| `glasses` | colour (`_face` for dark frames) | |
| `beard` | `True` (hair colour) or a palette name | the mouth is then drawn light |
| `pose` | `down`, `hold` (both forearms forward), `phone` (near hand up with a phone), `point` (near arm forward), `wave` (near arm raised above the head) | sitting people default to `lap` (forearms on the thighs) |
| `holding` | `box`, `tablet`, `laptop`, `book`, `clipboard`, `plate`, `cup` | with `pose="hold"`, or on the lap when sitting. `hold_color` overrides the colour |
| `carry` | `bag`, `basket`, `briefcase`, `suitcase` (rolled behind) | with `pose="down"`, in the near hand. `carry_color` sets the colour |
| `walk` | -1 to 1 | stride phase. Animate with `sin(2*pi*(n*t + phase))`, n a whole number |
| `sit` | seat height (0.6 for an adult seat) | then `z` is the seat top. Thighs run forward from the torso and the shins come down 0.5 in front of it |

## Seating

`s.bench(x, y, z, length, facing="l", seat=0.6)` builds a bench with its backrest on the far
side. Seat a person facing the same way, with the torso 0.12 in front of the backrest:

```python
s.bench(2.0, 3.3, 0.6, length=1.8)                       # on a platform at z 0.6
s.person(2.3, 3.42, 0.6 + 0.6, facing="l", sit=0.6, holding="book")
```

For a chair or a stool, keep the seat's front edge at most 0.48 in front of the person's
`y` (facing `l`) or `x` (facing `r`), so the shins clear it.

## Crowds

- Mix skin tones, hair styles and outfits; repeat a combination only on purpose (a uniform).
- Give each person room: about 1 unit between people standing side by side.
- In an animation each walker has a lane; walkers heading the other way use `ul` or `ur`.
- Turn faces towards the action or the reader. A back view is for someone leaving, queuing,
  or looking at the same thing the reader looks at.
