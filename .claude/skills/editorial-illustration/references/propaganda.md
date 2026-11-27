# Propaganda poster: the mid-century public poster

The public poster of the 1930s to the 1960s, in four treatments: a **screen print** in flat
inks, a **painted** gouache-and-oil illustration, a **jet-age** graphic of diagonals and speed
streaks, and a constructivist **photomontage**. All four are earnest on the surface, so they
carry irony well: official optimism taken at its word, a national plan in heroic dress, or a
household money habit turned into a call to arms.

Adjie's samples were twelve posters: eight stock screen prints (heroes, rays, silhouettes,
slogan bands), a 1954 painted poster of a man refusing a drink with one word above him, a
1960s jet-age poster, a 1930s painted flypast over a parade and a 1930s photomontage. The
pictures in `examples/`, two per treatment, were generated from the ones that carry no
symbol (the rest were described in words) and are ours to keep. `generate.sh
propaganda-<treatment>` attaches only that treatment's two.

## The rule: the look, never the ideology

The samples are Soviet posters, full of Lenin, Marx, Stalin, the hammer and sickle, red stars
on planes and Red Square. **None of that goes in a picture on this blog**: no hammer and
sickle (crossed, held up or on a flag), no red star, no CCCP or Cyrillic letters, no portrait
or name of Lenin, Marx, Stalin, Mao or any communist leader, no Kremlin, onion domes or Red
Square, no Soviet or party flag, no party logo of any kind, no insignia on aircraft or
vehicles. In Indonesia this imagery can be read as spreading a banned ideology (TAP MPRS
XXV/1966, and Article 188 of the 2023 Criminal Code), and people have been detained over a
T-shirt with the symbol. A farmer holds rice stalks or a hoe, never a sickle held up; a
worker holds a wrench, a welding torch or a steel beam, never a hammer held up. A flag in a
hero's hand is a plain red banner, or the post's own symbol. The Indonesian flag may appear
only whole, upright and respectful, with nothing written or drawn on it (Law 24/2009,
Article 24).

What stays is the visual grammar, which belongs to no party: idealised people, low angles,
monumental scale, machines in formation, diagonals, flat inks, block letters and cut-out
photographs.

## Rays and slogans are tools, not the style

The sunburst and the slogan band along the bottom are what everyone remembers, and the first
version of this style put both in every picture. Adjie's note: most of the samples have
neither. A painted refusal with one word in a corner, a jet streaking across with no text, a
flypast over a square, a photomontage of a crowd looking up. So:

- **Rays only in the screen print, and only when the picture is about glory or a dawn** (the
  piggy bank held up like a torch). Never in the other three treatments.
- **Words only when they carry the point.** One word ("TIDAK!") is often stronger than a
  slogan; many posters need none.
- **Vary where the words sit:** a corner, across the top, on a banner held in the picture, or
  the band along the bottom. Say where in the scene.

## The four treatments

| Treatment | Looks like | Best for | Words | Key | Examples |
|---|---|---|---|---|---|
| Screen print | flat inks (brick red, cream, near black, plus mustard or navy), hard edges, halftone, silhouettes of industry or the city | a call to action, a plan in heroic dress | a slogan in a corner, the top or a band | `propaganda-print` | `print-saver` (rays, band), `print-beam` (no rays, corner) |
| Painted | 1950s gouache and oil, no outlines, solid modelling; a person mid-gesture on one flat colour, or a vast painted panorama | a personal choice (a refusal, a warning, a shock), a spectacle | one big painted word, or none | `propaganda-painted` | `painted-refuse`, `painted-flypast` |
| Jet age | 1960s flat angular shapes, sharp diagonals, speed streaks, machines cutting across, people as bold profiles in a corner, yellow, red, grey, black and white | technology, infrastructure, speed, progress | usually none | `propaganda-jet` | `jet-train`, `jet-airport` |
| Photomontage | 1930s cut-out black-and-white and hand-tinted photographs at bold angles, red painted wedges, a crowd of faces looking up | a megaproject's spectacle, a leader and a crowd, mass enthusiasm | a banner, or none | `propaganda-montage` | `montage-trucks`, `montage-future` |

The examples are `examples/propaganda-<name>.webp`.

## The idea

Decide which way the poster speaks:

- **Irony:** a state programme or a national target in heroic dress, so the reader sees the
  gap between the poster and the facts (downstreaming, a new capital, a free-meals programme,
  a growth target, officials' perks).
- **Mobilisation:** a personal-finance habit as a call to arms (pay yourself first, refuse
  the instant loan, clear the credit card), cheerful and tongue in cheek.

Then pick the treatment that fits, one figure or machine, one gesture or motion, and words
only if they earn their place. Every row below was tested and came out as described:

| The point | Treatment | The picture | Words |
|---|---|---|---|
| Pay yourself first | print | a young woman holds a piggy bank high like a torch, rays behind; towers, cranes and an elevated train below | `PAY YOURSELF FIRST!` in a bottom band |
| Building together | print | three workers in profile carry one steel beam; a half-built bridge and cranes in silhouette; plain cream sky | `BUILD IT TOGETHER` top left |
| Breaking a debt cycle | print | a woman in profile cuts a paper chain of bills with big scissors; shophouses in silhouette | `CUT THE CHAIN!` top right |
| Downstreaming hype | print | a smelter worker holds up a glowing nickel ingot, the national flag on a pole; smelter chimneys and an ore barge | `MAJU TERUS HILIRISASI!` across the top, 3:4 |
| Officials' perks | print | a beaming official holds a golden fried chicken leg up like a torch over a queue of small citizens | `WE WORK FOR YOU!` in a band |
| Refusing an instant loan | painted | a woman at a café table raises her palm to a phone pushed at her from the frame's edge; plain mustard background | `TIDAK!` top right |
| Prices out of reach | painted | a grandmother squints at one chilli at a market stall, hand on her cheek; plain brick red background | `MAHAL!` top left |
| State spectacle | painted | a squadron of red propeller planes flies at the viewer over a national-day crowd at the National Monument | none |
| A high-speed railway | jet | a white train streaks diagonally along a viaduct; an engineer and an official in profile below | none |
| A new airport | jet | an airliner climbs steeply over a terminal, tower and radar; a pilot and an engineer in profile | none |
| The grid | jet | transmission towers stride diagonally, power lines as speed streaks; a lineman in profile | none |
| A mining boom | montage | an invented official waves from a tribune at giant dump trucks flying in formation; a crowd of faces looks up | none |
| Saving for the future | montage | a huge cut-out profile of a young woman looking up; tilted photos of towers, cranes and a school; a clay piggy bank | `SAVE FOR TOMORROW` on a top banner |
| A new capital in the forest | montage | giant tilted photos of towers and cranes rise out of rainforest, excavators fly above, a crowd looks up or at phones | `THE NEW CAPITAL RISES` on a bottom banner |

Words are part of the picture, so make one picture per language (Step 1 of `SKILL.md` has the
remake method).

## The prompt

Run it with the treatment's key: `sh generate.sh propaganda-painted <prompt> <out.png>`.
Plain `propaganda` stops and asks for one, on purpose.

Opening line:

```text
Make a new poster in the style of the attached reference pictures:
```

The scene, in this order: **the figure or the machine** (age, skin, hair, clothes, as an
idealised poster figure; or what the machine is and how it moves), **the gesture or the
motion** with the object that carries the point, **the angle** (from below, from high above,
in profile), **what is behind** (a plain colour, a painted sky, silhouettes, photographs),
**the words** in quotes with where they sit and in what colour (or nothing), then **the
palette** if it differs from the treatment's, and the aspect.

The example that made `examples/propaganda-painted-refuse.webp`:

```text
A young Indonesian woman in her twenties with shoulder-length black hair, in a neat
1950s-style white blouse, sits on the left at a café table and calmly holds up her open palm
to refuse a smartphone that a hand in a checked sleeve pushes towards her from the right edge
of the frame; the phone's screen glows with one big green button and nothing written on it.
A cup of coffee and a small plate of cakes on the table. She looks straight at the viewer,
calm and firm, with a small confident smile. Plain flat mustard yellow background. The single
word "TIDAK!" in huge red painted capitals in the upper right corner. 4:3.
```

And the one that made `examples/propaganda-jet-train.webp`:

```text
A sleek white high-speed train with a red stripe streaks diagonally from the lower left to
the upper right across the poster, long speed streaks behind it, an overhead power line mast
and a viaduct in angular flat shapes. In the lower right corner, the bold profiles of a young
Indonesian woman engineer in a white hard hat and an older Indonesian man in a suit, side by
side, facing left and looking up along the line. Palette: yellow, red, grey, black and white.
4:3.
```

Then the shared style block, word for word:

```text
Style: a mid-20th-century public poster in the treatment named below. One clear idea; an
earnest, idealised figure or a monumental machine; a bold, simple composition with strong
diagonals; a limited palette; a printed paper look. Only the style comes from any attached
pictures: never reuse their people, machines, buildings, symbols or words. No hammer and
sickle, no stars on anything, no Cyrillic letters, no communist leaders, no Kremlin, onion
domes or Red Square, no party emblems, no insignia on aircraft or vehicles. No logo, no
watermark, no signature.
```

Then the treatment's line, word for word:

```text
Treatment: a screen print in flat inks (brick red, cream and near black, plus mustard or navy
where named): hard edges, two or three flat tones per colour, faint paper grain, halftone and
slight misregistration, no gradients. Only the rays and lettering the scene asks for.
```

```text
Treatment: a 1950s painted illustration poster in gouache and oil, realistic and idealised:
no ink outlines, every form built from paint, solidly modelled faces and hands with soft
brushwork, warm skin, rich darks and light catching the fabric; the background either one
plain flat colour or a painted sky. No sunburst rays. Only the lettering the scene asks for,
big, flat and painted.
```

```text
Treatment: a 1960s jet-age graphic poster: flat angular shapes, sharp diagonals and speed
streaks, machines cutting across the frame, people as bold profiles in a corner, a flat
palette of yellow, red, grey, black and white, a little print texture, no gradients and no
sunburst rays. No lettering unless the scene asks for it.
```

```text
Treatment: a 1930s constructivist photomontage: black-and-white and hand-tinted photographs
cut out and pasted together at bold scales and angles, with flat painted shapes in red; a
huge machine or object against a photographed sky, a crowd of cut-out faces looking up in
wonder, a grainy printed look. Every face is an invented person who resembles no real one.
No sunburst rays. No lettering unless the scene asks for it.
```

Then one text rule: `No text except the exact words quoted in the scene.` or, with no words,
`No text, no letters, no numbers.`

## What the tests taught

Tested on 27 November 2026 on the Gemini API with Nano Banana 2.1: eleven pictures of the
first, print-only version, then twelve more for the four treatments, the last four through
`generate.sh propaganda-<treatment>` with the examples alone.

- **The examples set the habit.** When all three examples had rays and a bottom band, so
  did every new poster. With two examples per treatment, and one of the print pair without
  rays, the four validation posters added no ray and no band they were not asked for.
- **Every treatment works from words alone,** first try: the painted panorama, the jet-age
  train and the photomontage were made with no reference at all. The painted close-up needed
  "no ink outlines, every form built from paint" to look like gouache rather than a modern
  retro illustration.
- **Words come out letter-perfect** in English and Indonesian, one to four words in
  capitals (`"TIDAK!"`, `"MAHAL!"`, `"PAY YOURSELF FIRST!"`, `"MAJU TERUS HILIRISASI!"`,
  `"THE NEW CAPITAL RISES"`), in a corner, across the top or on a banner. Say where they sit
  and their colour.
- **The second language is a remake.** Attaching the English poster with `--ref` and asking
  to "make the attached poster again exactly as it is ..., changing only the words: the slogan
  in the band now reads exactly ..." gave the same poster with `"SISIHKAN DULU!"`.
- **Without the examples the colour drifts:** an unreferenced print added mustard rays
  nobody asked for. Name the palette in the scene whenever it is more than the treatment's.
- **A heroic Indonesian man in a peci pointing ahead comes back as Sukarno**, even with "an
  invented face that resembles no real politician": that dress and gesture are the model's
  idea of an Indonesian poster. When nobody real is meant, change both (a hard hat, glasses,
  a batik shirt, a woman, a held object instead of a pointing arm), and look at the face
  before using it. A bald official with a moustache in a suit, and the montage's waving
  official, read as nobody.
- **Photomontage faces are photographs**, so they can drift towards real people more than
  painted ones. Keep "every face is an invented person" and look at each face in the crowd.
- **Never name a building.** "A school" came back with SCHOOL written on it. Describe it ("a
  low building with a clock and a flagpole") and add "with no words on any building".
- **No banned symbol appeared** in any test with the style block's ban, the flypast's planes
  included ("with nothing painted on them"). A farmer told "she holds nothing else: no tools
  in her hands" carried only her rice. The Indonesian flag came back right: red over white,
  whole, nothing on it.
- **Hands hold up:** a card snapped between two fists came out right with "exactly two hands,
  five fingers each". A chilli held between finger and thumb is small; that is fine when the
  face carries the point.
- **Say who holds each banner pole.** In a family march one pole floated free.
- **3:4 portrait works** for a poster that stands alone; 4:3 is the default in a post.

## What to reject

- Any hammer, sickle, star, Cyrillic, leader portrait or name, Kremlin, party flag or
  insignia, even a hint.
- Rays or a slogan band the scene did not ask for, or rays in any treatment but the print.
- The wrong treatment's look: outlines on a painted poster, gradients on a print or jet-age
  poster, a drawn face in a photomontage.
- Colours outside the palette the scene or treatment named.
- A misspelt word, extra words, or words in the wrong language.
- A hero who looks mean, sinister or mocked rather than earnest: the irony is in the words
  and the context, not in the face.
