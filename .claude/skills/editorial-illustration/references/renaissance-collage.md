# Renaissance collage: modern things in old-master techniques

A mixed-media scrapbook collage, like a Renaissance mood board: torn paper, gilded frames,
painted skies, wax seals, pressed flowers, layered with soft shadows. The twist that makes
it ours: **the subjects are modern** (a bullet train, a B-2 bomber, a skyscraper, a laptop,
a woman in a hijab with a smartphone) and only the *techniques* are old: oil painting with
sfumato and craquelure, sepia copperplate engraving, fresco plaster, white marble, gold leaf.
The three pictures in `examples/` were generated from Adjie's sample and are ours to keep;
`generate.sh collage` attaches them.

## The rule Adjie set

Never put Renaissance subject matter in the picture. No Venus, no David, no saints, angels,
gods, cherubs or classical statues, and no copy of a famous painting or building (no Birth of
Venus face, no Duomo). The *subject* is always from the post's world; the old masters lend
only their *technique*. A marble statue is fine when it is a statue of a modern thing (a
smartphone, a suburban house, a calculator); an oil portrait is fine when it is a portrait of
a modern person in modern clothes.

## The look

- **Layers of cut and torn paper** with deckled edges, white cut-out borders and soft drop
  shadows, overlapping like a scrapbook page. Visible paper grain.
- **One hero cut-out** near the centre (the main subject, painted in oil), with four to six
  supporting fragments around it. More than that turns into clutter.
- **Each fragment in a different old technique:** an oil-painted subject in warm golden light;
  a sepia engraving with cross-hatching for a city, a map or a machine; a gilded oval frame
  holding a small painted object; a white marble sculpture of a modern object; a patch of
  painted cloudy sky or cracked fresco.
- **The paper scraps:** an old ledger page with faded columns, a blueprint, an engraved map,
  sheet music, a torn boarding pass, a pressed flower that suits the place (jasmine,
  frangipani, chilli, poppy), a wax seal, a strip of gold leaf.
- **Warm muted palette:** ochre, cream, faded rose, sage, sky blue and gold.

## The idea

List the post's subject as objects: the hero (what the section is about), the place (as an
engraving), two or three symbols (in frames, as marble, as a scrap). Name each one with its
technique. The collage suits a big theme, a history, a comparison of eras, wealth and power,
or an essay with several threads, and a social card that should feel rich.

## The prompt

Opening line:

```text
Make a new picture in the style of the attached reference pictures:
```

The scene: `A mixed-media paper collage about <topic>.`, then **the hero cut-out and its
technique**, **what is behind it**, then `Around them:` the fragments, each with its
technique, then the aspect. Say `No people.` when there are none. The example that made
`examples/collage-bomber.webp`:

```text
A mixed-media paper collage about a modern military budget. At the centre, cut out with a
thin white paper border, a black B-2 stealth bomber flying across a golden evening sky,
painted like an old-master oil painting with warm glazes, soft sfumato clouds and fine
craquelure. Behind it, a torn fragment of a modern glass skyscraper drawn as a sepia
copperplate engraving with fine cross-hatching. Around them: a torn strip of an old ledger
page with faded columns of numbers, a gilded oval frame holding a small painted radar dish, a
sprig of pressed red poppies, a wax seal, a scrap of old sheet music, and a patch of painted
fresco sky. 4:3.
```

The style block, word for word, at the end:

```text
Style: a layered scrapbook collage of cut and torn paper fragments with soft drop shadows,
deckled torn edges, white cut-out borders and visible paper texture. Every subject is modern,
but rendered in old-master techniques: oil painting with sfumato, warm glazes and fine
craquelure, sepia copperplate engraving with cross-hatching, cracked fresco plaster, white
marble sculpture, gilded ornament and gold leaf. Warm muted palette of ochre, cream, faded
rose, sage, sky blue and gold. Only the technique comes from the attached pictures: never
reuse their people, objects, paper scraps or layout, and show only what this scene describes.
No classical figures, gods, angels, ancient statues or famous old paintings. No logo, no
watermark, no signature.
```

Then one text rule: `No readable words.` or, with words quoted in the scene,
`No text except the exact words quoted in the scene.`

## What the tests taught

Tested on 26 November 2026 on the Gemini API with Nano Banana 2.1.

- **The examples leak.** A collage with no person in its scene came back with the hijab
  woman of `collage-portrait.webp` in it, and its coin stack. The "never reuse their people,
  objects, paper scraps or layout" sentence and an explicit `No people.` stopped it.
- **Old handwriting appears on the scraps** as illegible cursive and faded numbers. That is
  part of the look and reads as texture; it is not text to check. Real words must be quoted.
- **Quoted words go on a parchment ribbon banner** ("a long curling parchment ribbon banner
  unfurls with exactly the words ..."), the old-master version of a speech bubble.
- **Modern machines come out well** in oil (a bullet train, a B-2 bomber, a laptop by
  candlelight) and cities in engraving (skyscrapers with cranes, a jammed street).
- **Oil portraits are realistic, so faces drift towards real people.** A generic Indonesian
  politician came back looking like the sitting president. Say "an invented face that
  resembles no real person" when nobody real is meant (see `SKILL.md`, step 1).
- **Banknotes come out as US dollars** unless you say "engraved banknotes with blank panels".
- **A 16:9 card with "the right half is calmer"** kept the right half to parchment and sky,
  as asked, leaving room for a title in the social preview.
- The model's sense of "Renaissance" drifts to 18th and 19th century (romantic skies,
  Victorian ledgers). That is fine for the mood; what matters is no classical subject.

## What to reject

- Any classical figure, god, angel, cherub or statue of a person; any recognisable famous
  painting, fresco or building from the Renaissance.
- A flat digital look: no torn edges, no shadows, no paper.
- More than about seven fragments, or a hero so small it no longer reads.
- Readable words other than the ones quoted.
