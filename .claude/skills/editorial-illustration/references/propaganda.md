# Propaganda poster: the heroic mid-century public poster

The look of mid-20th-century state posters: one heroic figure seen from below, sunburst rays
behind, factories, cranes and ships in silhouette, a bold slogan in block capitals, all in a
few flat inks of brick red, cream and black. Earnest on the surface, so it carries irony
well: official optimism taken at its word, a national plan in heroic dress, or a household
money habit turned into a call to arms. Adjie's samples were eight stock posters; the
pictures in `examples/` were generated from crops of the three that carry no symbol (a worker
with a wrench, a raised fist with a plain red banner, a steelworks), with none of their
words, and are ours to keep; `generate.sh propaganda` attaches them.

## The rule: the look, never the ideology

The samples are Soviet posters, full of Lenin, Marx, the hammer and sickle and the red star.
**None of that goes in a picture on this blog**: no hammer and sickle (crossed, held up or
on a flag), no red star with them, no CCCP or Cyrillic letters, no portrait of Lenin, Marx,
Stalin, Mao or any communist leader, no Soviet or party flag, no party logo of any kind. In
Indonesia this imagery can be read as spreading a banned ideology (TAP MPRS XXV/1966, and
Article 188 of the 2023 Criminal Code), and people have been detained over a T-shirt with
the symbol. A farmer holds rice stalks or a hoe, never a sickle held up; a worker holds a
wrench, a welding torch or a hard hat, never a hammer held up. The flag in the hero's hand
is a plain red banner, or the post's own symbol. The Indonesian flag may appear only whole,
upright and respectful, with nothing written or drawn on it (Law 24/2009, Article 24).

What stays is the visual grammar, which belongs to no party: rays, low angles, monumental
figures, industry silhouettes, flat inks and block letters.

## The look

- **Three to five flat inks:** brick red `#B23A2E`, cream `#EFE3C8`, near black `#1E1E1E`,
  plus mustard `#E0A93B` or deep navy `#1F2A44` when the scene needs them. Hard edges, two or
  three flat tones per colour to model a face or a fold, like a screen print or lithograph,
  with a faint paper grain, halftone and slight misregistration. No gradients, no photo
  texture.
- **Sunburst rays** radiate from behind the hero or from a sun disk: the signature.
- **One heroic figure** from a low angle, chin up, looking at the horizon or straight out:
  a raised fist, a tool held up, an arm pointing to the future, a banner, a drum.
- **Monumental scale.** The figure or a giant head towers over the city; planes fly in
  formation; diagonals everywhere.
- **Silhouettes** along the bottom in near black or navy: factories, smokestacks, cranes,
  ships, power pylons, a rocket, a skyline, a crowd with banners.
- **The slogan** in a band along the bottom (or across the top): condensed block capitals or
  stencil letters, sometimes outlined, in cream on red or red on cream. A cream border frames
  the whole poster.

## The idea

Decide which way the poster speaks:

- **Irony:** a state programme or a national target in heroic dress, so the reader sees the
  gap between the slogan and the facts (downstreaming, a new capital, a free-meals programme,
  a growth target).
- **Mobilisation:** a personal-finance habit as a call to arms (pay yourself first, clear the
  credit card, invest every month), cheerful and tongue in cheek.

Then: one figure, one gesture, one object that carries the point, one row of silhouettes
that says where, and a slogan of two to five words.

| The point | The picture | Slogan |
|-----------|-------------|--------|
| Downstreaming hype | a smelter worker in a hard hat holds up a glowing nickel ingot, the national flag on a pole; smelter chimneys and an ore barge in silhouette | `MAJU TERUS HILIRISASI!` |
| Pay yourself first | a young woman in an office shirt holds a piggy bank high like a torch; office towers, cranes and an elevated train below | `PAY YOURSELF FIRST!` |
| A new capital in the forest | a giant city planner in a hard hat with a rolled blueprint over rainforest turning into towers | `BUILD THE NEW CAPITAL!` |
| Officials' perks | a beaming official holds a golden fried chicken leg up like a torch over a queue of small citizens | `WE WORK FOR YOU!` |
| Clearing the credit card | a man snaps a credit card in two with both fists, a mall and billboards below | `DEBT FREE BY DECEMBER!` |
| Investing every month | a family of three marches forward behind a banner with a rising line chart | `INVEST EVERY MONTH!` |
| Food self-sufficiency | a rice farmer hugs a golden sheaf of rice; terraces, a tractor and pylons below | `SWASEMBADA PANGAN!` |

All seven were tested; the table's pictures came out as described.

The slogan is in the post's language and is part of the picture, so make one picture per
language (Step 1 of `SKILL.md` has the remake method).

## The prompt

Opening line:

```text
Make a new poster in the style of the attached reference pictures:
```

The scene, in this order: **the figure** (age, skin, hair, clothes, as a heroic poster
figure), **the gesture with the object**, **the angle** (from below), **what is behind**
(rays, the sun disk), **the silhouettes** along the bottom, **the slogan** in quotes and where
it sits, then **the palette** if it differs from red, cream and black, and the aspect.
The example that made `examples/propaganda-saver.webp`:

```text
A young Indonesian woman in her twenties with short black hair, wearing a plain office shirt
with rolled-up sleeves, seen from a low angle from the waist up, holds a big piggy bank high
above her head in one hand like a torch, chin up, looking proudly to the horizon. Sunburst
rays radiate from behind the piggy bank. Along the bottom, near-black silhouettes of office
towers, construction cranes and an elevated train line. A brick red band along the bottom of
the poster carries the slogan "PAY YOURSELF FIRST!" in big cream condensed block capitals.
4:3.
```

`examples/propaganda-farmer.webp` is the food self-sufficiency row of the table (red, cream,
black and mustard) and `examples/propaganda-card.webp` the credit-card row (with navy).

The style block, word for word, at the end:

```text
Style: a mid-20th-century heroic propaganda poster, matching the attached reference pictures:
flat screen-printed inks in brick red, cream and near black (with mustard or navy only where
the scene names them), hard edges, figures modelled with two or three flat tones per colour,
faint paper grain, halftone and slight misregistration, no gradients and no photographic
detail. A heroic figure seen from a low angle, monumental and idealised; sunburst rays
radiating from behind; industry and city silhouettes along the bottom; strong diagonals; a
bold slogan in condensed block capitals in a band, and a cream border round the poster. Only
the style comes from the attached pictures: never reuse their people, symbols, flags or
words. No hammer and sickle, no red star, no Cyrillic letters, no communist leaders, no party
emblems. No logo, no watermark, no signature.
```

Then one text rule: `No text except the exact words quoted in the scene.` A poster with no
slogan (rare) uses `No text, no letters, no numbers.`

## What the tests taught

Tested on 27 November 2026 on the Gemini API with Nano Banana 2.1: eight tuning pictures with
the three symbol-free sample crops attached, then two briefs through `generate.sh propaganda`
with the examples alone.

- **It works from words alone, but drifts in colour:** without the examples it added mustard
  rays nobody asked for. With them it keeps to the palette the scene names. Name the palette
  in the scene whenever it is more than red, cream and black.
- **Slogans come out letter-perfect** in English and Indonesian, two to four words in
  capitals (`"PAY YOURSELF FIRST!"`, `"MAJU TERUS HILIRISASI!"`, `"SWASEMBADA PANGAN!"`).
  Say where the band sits, its colour and the letters' colour.
- **The second language is a remake.** Attaching the English poster with `--ref` and asking
  to "make the attached poster again exactly as it is ..., changing only the words: the slogan
  in the band now reads exactly ..." gave the same poster with `"SISIHKAN DULU!"`.
- **A heroic Indonesian man in a peci pointing ahead comes back as Sukarno**, even with "an
  invented face that resembles no real politician": that dress and gesture are the model's
  idea of an Indonesian poster. When nobody real is meant, change both (a hard hat, glasses,
  a batik shirt, a woman, a held object instead of a pointing arm), and look at the face
  before using it. A bald official with a moustache in a suit read as nobody.
- **Never name a building in the silhouettes.** "A school" came back with SCHOOL written on
  it. Describe it ("a low building with a clock and a flagpole") and add "with no words on any
  building".
- **No banned symbol appeared** in any test with the style block's ban. A farmer told "she
  holds nothing else: no tools in her hands" carried only her rice. The Indonesian flag came
  back right: red over white, whole, nothing on it.
- **Hands hold up:** a card snapped between two fists came out right with "exactly two hands,
  five fingers each".
- **Say who holds each banner pole.** In the family march one pole floated free.
- **3:4 portrait works** (the slogan band moves to the top) for a poster that stands alone;
  4:3 is the default in a post.

## What to reject

- Any hammer, sickle, star emblem, Cyrillic, leader portrait or party flag, even a hint.
- Gradients, soft airbrushing, glossy 3D or a photo look.
- More than five inks, or colours outside the palette the scene named.
- A misspelt slogan, extra words, or a slogan in the wrong language.
- A crowd of equal small figures instead of one hero; a hero who looks mean, sinister or
  mocked rather than earnest (the irony is in the slogan and the context, not in the face).
