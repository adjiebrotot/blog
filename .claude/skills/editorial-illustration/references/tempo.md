# Tempo: the news-magazine cover painting

The look of the cover paintings on *Tempo*, the Indonesian weekly: one sharp visual idea,
painted like gouache, with caricatured people on a single bold colour. Adjie's samples were
three covers (a politician on the floor reading the assembly sheet of a flat-pack chair, a
family racing on scooters, two politicians swiping a dating app). The three pictures in
`examples/` were generated from them and are ours to keep; `generate.sh tempo` attaches them.

## The look

- **Painted, not drawn.** Soft, chalky, smoothly blended gouache with a fine grain. No
  outlines: every edge is a change of colour or light. Hair and cloth get a few loose
  strokes, never line hatching.
- **One bold background colour** fills most of the frame and is the floor, the wall and the
  sky at once: cobalt blue, crimson, mustard, teal, orange, violet. No room, no horizon.
- **Warm light, cool shadow.** Skin and clothes in warm pinks and peaches under a warm key
  light; the shadow side and the reflected light turn violet-blue. This is what makes it
  read as *Tempo* rather than a generic caricature.
- **Gentle caricature.** Heads and hands a little too big, noses, cheeks, chins and
  expressions pushed, but human and never ugly. A public figure stays recognisable.
- **An unusual angle and a bold crop.** Straight down from above with the person cut by the
  frame in a corner (the most reliable), over the shoulder, or from low down. The body is
  often cut at the chest or the waist.
- **A big calm empty area** of plain background, where a magazine would put its headline.

## The idea comes first

A *Tempo* picture is a visual metaphor, not a scene. Before writing the prompt, say the
point of the section in one sentence and find an everyday object that carries it:

| The point | The picture |
|-----------|-------------|
| A wealth claim propped up by spin | the chart line held up by sticky tape and a pencil |
| Buying a house or investing | a woman with one hand on a toy house and one on a stack of coins of the same height |
| One worker carries the other | two civil servants on a tandem bicycle, one pedalling, one asleep |
| Prices out of reach | a grandmother squinting through a magnifying glass at the price tag on one chilli |
| A weak currency abroad and at home | the traveller on the high pan of a balance scale, the shop selling to tourists on the low one |

Good objects are ones every Indonesian reader owns or knows: a wallet, a coin, a receipt,
a peci, a podium, a plate of fried rice, a phone, a toy house, a scooter, a flag on a stick.

## The prompt

Opening line:

```text
Paint a new picture in the painting style of the attached reference pictures:
```

The scene, in this order: **the angle and crop**, **who** (age, skin, hair, clothes, as
caricature), **the action with the metaphor object**, **the expression** in gentle words,
then **the background colour and where the empty space is**, then the aspect (`4:3`).
The example that made `examples/tempo-closeup.webp`:

```text
A close-up caricature of an Indonesian woman in her sixties with brown skin, round glasses
and a grey bun, wearing a maroon batik blouse, seen from the shoulders up on the left half of
the picture. She squints through a large magnifying glass held in her right hand at a single
small red chilli pepper she holds up in her left hand between finger and thumb; a tiny blank
white price tag hangs from the chilli on a string. Her eyebrows are raised high in disbelief
and her mouth is a small tight O. Flat mustard yellow background with a large empty area on
the right. 4:3.
```

The style block, word for word, at the end:

```text
Style: an editorial cover painting for a weekly news magazine, painted digitally like gouache:
soft, chalky, smoothly blended brushwork with a fine grain, no outlines, every form built from
light and shadow. People are gentle caricatures: slightly oversized heads and hands,
exaggerated noses, cheeks and expressions, but recognisably human and never ugly. A bold,
limited palette: one flat, saturated background colour fills most of the frame, skin and
clothes in warm pinks and peaches lit by a warm key light, with cool violet-blue shadows and
reflected light. The idea is told with everyday objects, from an unusual angle (from above,
from below, over the shoulder) with the figure boldly cropped by the frame, and a large calm
area of plain background colour. Only the painting style comes from the attached pictures:
never reuse their people, objects or layout. No masthead, no headline, no logo, no watermark,
no signature.
```

Then one text rule: `No text, no letters, no numbers.` or, with words quoted in the scene,
`No text except the exact words quoted in the scene.`

## What the tests taught

Tested on 26 November 2026 on the Gemini API: about ten tuning pictures, then fifteen of the
blog's briefs.

- **Nano Banana 2.1 is the model.** Gemini 3 Pro Image made the same prompt more cartoonish:
  a childlike face, an angry frown, glossier paint.
- **Name the expression gently.** "Frowns in concentration" came back as a scowl on both
  models. "A calm, puzzled half-smile", "wide hopeful eyes", "eyebrows raised in disbelief"
  come back as written.
- **"Seen from directly above" works** when the person sits in a corner cropped by the frame
  and the floor is the background colour. A "low angle" is often ignored; ask for it, but
  don't build the idea on it.
- **Give the props a size.** From above, a toy house and a coin stack came out the size of a
  matchbox. "Each as tall as her shoulders" fixed it.
- **One or two big figures, not a crowd.** Three full figures in a row, or a person inside a
  traffic jam, shrank the people and drifted into a cute children's-book look with a busy
  background. Crop in close on one or two people and let the object carry the rest.
- **Short quoted text works.** A speech bubble with "Our economy is skyrocketing!" came back
  letter-perfect, in bold sans serif. Writing on a phone screen ("DEBT $10K") too.
- **Public figures work.** Xi Jinping whispering to Joko Widodo came back recognisable in all
  three styles when the prompt named and described them. Exaggerate the expression and the
  posture, not their ethnicity or body.
- **From above, keep the person in a side corner** (as in `tempo-above.webp`). Seated at the
  bottom edge facing up the picture, a diner came out with the top of his head towards the
  viewer and an upside-down face.
- **A balance scale, a throne, a tandem, a beanstalk** all worked as metaphors on the first
  try: one big object that does the arguing, people around it.
- The model sometimes leaves a small stray square or smudge in the empty background. Look
  for it; retry if it shows.

## What to reject

- Black outlines, comic-book inking, cel shading, or a glossy 3D look.
- A busy room or a landscape behind the people instead of one colour.
- Faces that are ugly, mean or babyish rather than caricatured.
- Any masthead, headline, cover lines, price, barcode or date: this is the cover art
  without the cover.
