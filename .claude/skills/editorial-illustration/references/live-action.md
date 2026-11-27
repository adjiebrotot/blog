# Live-action hybrid: drawn people in a real photograph

A mixed-media picture: a real photograph of a real kind of place (a city waterfront, a
train platform, a café, a field, a street at sunset) with friendly hand-drawn 2D people
sketched into it, in black ink and greys. The photo says *where*, the drawing says *who* and
*what they feel*. Human, relatable, never pointed. Adjie's sample was a one-page design
system (three colleagues on a waterfront ledge, a commuter with headphones on a platform, a
team round a laptop, a planter, two people looking at a skyline); the pictures in
`examples/` were generated from it and are ours to keep; `generate.sh hybrid` attaches them.

## The look

The design system's own four principles:

- **Real-world context.** An authentic, relatable photograph: natural daylight or golden
  hour, true colours, real depth of field (the background softens). A place readers know,
  not a postcard.
- **Human and simple illustration.** People are hand-drawn, sketchy and friendly: rounded,
  approachable shapes, simple faces (small dot or oval eyes, short brows, a line for the nose,
  a small curved mouth), expressive but never detailed. Slightly large heads and hands.
- **Clear contrast.** The drawing stays visibly drawn: colour photo, grayscale drawing. The
  things the people hold or use (a laptop, a coffee cup, a backpack, a phone, a hard hat)
  are drawn too, in the same ink.
- **Narrative and everyday moments.** People doing things together: talking on a ledge,
  leaning over one laptop, walking to the train, planting a seedling, a high five, two
  friends seen from behind looking at the city.

The drawing's rules:

- **Line:** a textured black outline like a brush pen or marker, heavier on the outer
  contour (about 4 to 8 px at 1456 px wide), thinner for details inside (2 to 4 px).
- **Fill:** flat grayscale only, five tones: ink `#111111` (hair, beards, outlines), grey
  `#6B6B6B` (trousers, dark clothes), grey `#BDBDBD` (shadow side, bags), grey `#EBEBEB`
  (shirts, light fills) and paper `#FFFFFF` (skin, highlights). An optional pencil or paper
  texture in the fills. No colour, no gradients, no 3D shading on anything drawn.
- **Doodle marks:** short dashes radiating near a head (surprise, excitement, an idea), a
  round speech bubble with an icon in it (a music note, a lightbulb, a coin) rather than
  words, a few motion lines.
- **Grounded:** the drawn people stand on the photo's real ground, sit on its real ledge or
  bench, and are the right size for the place, with a faint soft contact shadow.
- **Composition:** the people in the foreground or midground, one clear subject, natural
  light and a real setting, and a calm area of the photo (sky, water, a wall) left free for
  a title, top left or top right.

## Two ways to get the photograph

1. **Generated (the default).** The model makes the photo and the drawing together. Name a
   *kind* of real place ("the pedestrian sidewalk of a business district in Jakarta", "an
   elevated MRT platform", "a warung with plastic stools") rather than a landmark, unless the
   post is about it. A generated photo is not a record: never caption it as a real place on a
   real day, never use it as evidence, and keep the passers-by blurred and anonymous.
2. **Adjie's own photograph.** Attach it with `--ref` (it goes before the examples) and use
   the second opening line below. The photo must be Adjie's, or licensed for reuse, and
   should not show a stranger's face clearly. This is the truest version of the style: a
   real place he was, with the people of the story drawn in.

## The idea

Pick the small human moment that carries the section, and the real place it happens in.
The drawing carries the feeling (the doodle marks, the expression, the gesture); the photo
carries the setting. Good pairings:

| The point | The picture |
|-----------|-------------|
| The daily commute is where the money goes | a young man with headphones and a backpack walks along a real elevated MRT platform, a music-note bubble above his head |
| Two offers, one decision | two colleagues at a café table lean over one laptop, one pointing at the screen, the other's eyebrows raised |
| A modest meal, a receipt that adds up | a man at a real warung table with a plate of fried rice, reading a long receipt, little shock dashes round his head |
| Retiring abroad | an older couple seen from behind on a real bench by a river at sunset, her head on his shoulder |
| Field work, the real economy | an engineer in a hard hat with a clipboard explains something to a farmer in a real rice field |

It suits a personal story, travel, daily life, work and a case study's character in a real
city. For a satirical point, use Tempo or the propaganda poster; for a step, wikiHow.

## The prompt

Opening line, with a generated photograph:

```text
Make a new picture in the style of the attached reference pictures:
```

With Adjie's photograph as the first `--ref`:

```text
The first attached picture is a photograph. Keep it exactly as it is (same place, framing,
light and colours) and draw people into it in the style of the other attached pictures:
```

The scene, in this order: **the photograph** (the place, the time of day and the light,
what is sharp and what is blurred; skip it with Adjie's photo), then `Drawn into it:`
**who** (age, hair, glasses, hijab, beard, clothes named in greys), **what they do and with
what**, **where they are in the photo** (sitting on the ledge in the foreground, walking along
the platform on the left), **the expression and the doodle marks**, then **the framing**,
**where the empty space is**, and the aspect. The example that made
`examples/hybrid-street.webp`:

```text
DRAFT: filled in after the tuning tests.
```

The style block, word for word, at the end:

```text
Style: a live-action and 2D illustration hybrid (mixed media), matching the attached
reference pictures. The setting is a real photograph with natural light, true colours and
real depth of field. The people, and everything they hold or use, are hand-drawn 2D
characters in a sketchy, friendly style placed into that photograph: textured black brush-pen
outlines, heavier on the outer contour and thinner inside; flat grayscale fills only (near
black hair, mid grey and light grey clothes, skin left paper white) with an optional light
pencil texture; no colour, no gradients and no 3D shading on anything drawn; rounded,
approachable shapes; simple friendly faces with small dot eyes, short eyebrows and a small
curved mouth, expressive but not detailed. Small doodle marks near the heads (short dashes for
surprise or excitement, a round speech bubble with an icon). The drawn people sit and stand
convincingly in the photo, at the right scale, with a faint soft contact shadow. People in the
foreground or midground, one clear subject, and a calm area of the photo left free for a
title. Only the style comes from the attached pictures: never reuse their people, places or
layout. No logo, no watermark, no signature.
```

Then one text rule: `No text, no letters, no numbers.` or, with words quoted in the scene,
`No text except the exact words quoted in the scene.`

## What the tests taught

DRAFT: filled in after the tuning tests on Nano Banana 2.1.

## What to reject

- Colour on the drawn people or their things, or soft 3D shading: the contrast is the style.
- Drawn people that float, slide off the ledge or are the wrong size for the place.
- A drawn background, or a photo so busy the people get lost in it.
- Photographed people in the foreground, or a clear face of a stranger anywhere.
- A recognisable landmark the post did not ask for, a logo on a laptop, a shop sign that
  reads, a watermark or a signature.
