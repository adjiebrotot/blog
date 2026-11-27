---
name: editorial-illustration
description: Make an illustration for a post on this blog with an image model, in one of five styles: wikiHow (one person doing one step, soft shading, a pale background), Tempo (a news-magazine cover painting, a visual metaphor in gouache caricature), Summer flat (a retro beach-read novel cover, a stylish figure in sunglasses), Renaissance collage (modern things in old-master techniques on torn paper) or Live-action hybrid (hand-drawn grayscale people sketched into a real photograph). Saved as WebP in assets/img/ with a focus box. Use when Adjie asks for an illustration, a drawing, an image, a picture for a step or a section, a cover image that is not a screenshot or a chart, a style by name (wikiHow, Tempo, summer novel, collage, live-action), a caricature or a social card with a point of view. For an isometric picture, or a place or system with exact layout, use isometric-illustration.
---

# Illustration with an image model

Five styles, each its own unique theme, walled off from the others (**The great wall**,
below). Each style is a sealed folder, `styles/<style>/`: its guide (`guide.md`), its data
(`style.json`: the start of its style block, the words it owns, the description the judge
reads, its examples) and its example pictures (`examples/`). Only the workflow is shared:
the generator, the keys, the checks and the focus box.

| Style | Looks like | Made of | Carries | Folder | Key |
|---|---|---|---|---|---|
| wikiHow | an instructional step picture | thin outlines in a darker shade of each colour, soft shading, pale wash | *how*: one person, one action, the object in the hands | `styles/wikihow/` | `wikihow` |
| Tempo | a *Tempo* cover painting | soft gouache, no outlines, warm light and violet shadows, one bold colour | a visual metaphor: a satirical or political point | `styles/tempo/` | `tempo` |
| Summer flat | a summer beach-read novel cover | 3 or 4 flat colours plus black and white, crisp edges | a feeling: a light personal or money-habit point | `styles/flat/` | `flat` |
| Renaissance collage | a scrapbook of torn old-master fragments | oil, sepia engraving, marble, fresco, gold leaf, torn paper | a big theme: history, wealth and power, eras compared | `styles/collage/` | `collage` |
| Live-action hybrid | a photo with friendly doodled people in it | a real photograph, plus black brush-pen line art with grayscale fills | *who and where*: everyday people in a real place, a relatable moment | `styles/hybrid/` | `hybrid` |

**Which style.** wikiHow shows a reader *how*: one person, one step, a pale background.
Live-action hybrid shows *who and where*: people like the reader in a place that is real
(a Jakarta sidewalk, a warung, an office, a train platform), friendly rather than pointed,
and it can be drawn onto Adjie's own photograph. Tempo, Summer flat and the collage show
*what the writer thinks*: a metaphor, a mood, a theme.
`isometric-illustration` shows *how a place or system fits together*, drawn in code, with
exact counts and a version for each theme. Keep one style through a post, so its pictures
read as a set, unless Adjie asks otherwise.

**By category (Adjie's choice, 27 November 2026):** a `politics` post uses **Tempo**, a
`finance` post uses **Live-action hybrid**, in both languages. Other categories pick by the
rule above.

**The styles are the inspiration, not the brands or the sources.** Never ask for or keep a
wikiHow logo, a *Tempo* masthead, cover lines, a price or a barcode, a book title or author
name, a copy of a real painting, Never commit Adjie's samples to this public repo (they are
not ours): every picture in `examples/` was generated from them and is ours to
keep. Never say in a caption or alt text that a picture is from wikiHow, *Tempo*, a book
cover.

## The great wall

Every style is its own world. A picture is made in exactly one style, from that style's
folder alone, and nothing from another style may cross into it: not a word, not an idea, not
a picture. Adjie's rule, after two leaks in a style since removed: one picture came back with the
collage's white cut-out borders and sepia, another with Tempo's pushed caricature
expression. Neither leaked through a file. They leaked through *words* (the prompt said
"cut out", "ochre", "gouache"), an *idea* (the scene was Tempo's grandmother-and-chilli
example) and *examples* that had already drifted. So the
wall stands on all three, and on the finished picture too:

1. **One picture, one style.** No blends, no "Tempo with a collage background", no borrowed
   trait. A deliberate borrowing happens only when Adjie asks for it, and is passed by name
   with `--allow <word>` (the China post's wikiHow picture is a caricature on purpose, so
   regenerating it takes `--allow caricature`).
2. **One folder per style.** A picture is made from its own folder only: its guide, its
   style block, its examples. `generate.sh <style>` attaches that folder's examples and
   nothing else. Never attach another style's example, and never use a post picture of
   another style as a `--ref`: the script refuses both.
3. **Own words only.** Each style owns the technique words of its look (`style.json`,
   `"words"`: `gouache` and `caricature` are Tempo's, `torn`, `sepia`, `ochre`, `engraving`
   are the collage's, `doodle` and `brush-pen` the hybrid's, and so on). A prompt may not use
   another style's words anywhere outside its own style block, and a style block may not use
   them at all, not even to forbid them: naming a feature plants it. Describe what the style
   *is*, in its own words. `generate.sh` refuses a prompt that breaks this, before any cost.
4. **Own ideas only.** Write a scene from the style's own guide. Never reuse a scene, a
   character, a metaphor or a palette from another style's guide or examples.
5. **Every picture is judged.** After generating, `generate.sh` asks a vision model whether
   the picture stays in its style (`scripts/judge.mjs`, which reads every style's
   description). A leak exits with code 3 and the picture is failed: never use it, rewrite
   the scene in the style's own words and generate again. Run the judge by hand on any
   picture made another way.
6. **Changing or adding a style touches only its folder.** Its words must not overlap any
   other style's, its block must pass, and afterwards `node scripts/walls.mjs` must end with
   "the great wall holds": no word owned twice, no block using a neighbour's words, every
   example of every style passing the judge as its own style. Never edit another style's
   folder to make room for a new one.

Where the walls run closest, and what keeps each pair apart:

| Neighbours | Stays on its own side by |
|---|---|
| wikiHow / Live-action hybrid | colour drawing on a pale painted wash / grey drawing on a real colour photograph |
| Tempo / Summer flat | gouache caricature, violet shadows, painted texture / fashion figures in sunglasses, 3 or 4 flat colours, crisp edges, no texture |
| Tempo / Renaissance collage | one painted scene on one bold colour / torn fragments of many old-master techniques, warm sepia |

```
brief → the idea → prompt in _illustrations/<name>.txt → generate.sh <style> → look, retry
      → render.mjs → assets/img/<name>.webp → focus box → <img> in the post
```

## Before you start: the API key

The generator reads `GEMINI_API_KEY` (Google Gemini API, direct) or `OPENROUTER_API_KEY`
(OpenRouter). Adjie uses both interchangeably. With only `GEMINI_API_KEY` set it calls
Google; with `OPENROUTER_API_KEY` set it calls OpenRouter (`--provider google|openrouter`
overrides). If neither is set, **ask Adjie for a key** before anything else, and pass it only
as an environment variable for the command. Never write a key into a file, a commit, a
prompt file or a post.

- **429 "rate-limited to prevent exceeding its monthly spending cap"** (Google): the project
  is near the spend cap set in AI Studio, which is separate from its prepaid credit. It
  lifted after a minute or two each time in testing: run one picture at a time and wait a
  minute after a 429 (a refused request costs nothing).
- **429 "has exceeded its monthly spending cap"** (Google): the cap is reached and it does
  not lift; every call fails, even a text one. Stop and ask Adjie to raise the cap at
  ai.studio/spend (or for an OpenRouter key).
- **402 "prepayment credits are depleted"** (Google) or **402** on OpenRouter (less than
  $1.00 left): the account is empty. Stop, tell Adjie it needs topping up, don't retry.

Google returns no cost in the reply, so the script prints none; billing shows in Google
Cloud. OpenRouter's cost is printed after each picture.

## Which model

**Nano Banana 2.1** (`gemini-nano-banana-2.1` on Google, `google/gemini-nano-banana-2.1` on
OpenRouter, about $0.04 a picture) for every style: Adjie's choice, and the model every
style guide was tuned on. The alternatives, compared on the wikiHow prompt on 25 October
2026 and on the Tempo prompt on 26 November 2026:

| Model | Cost per picture | Use for |
|-------|------------------|---------|
| `gemini-nano-banana-2.1` | about $0.04 | **Default.** Follows the example pictures well in every style. |
| `gemini-3-pro-image` | about $0.14 | Only when hands or words keep failing: slightly cleaner outlines and hands, but it made the Tempo test more cartoonish (a childlike, angry face). |
| `gemini-3.1-flash-image` | about $0.07 | A fallback if the two above are unavailable. |
| `openai/gpt-5.4-image-2` (OpenRouter) | about $0.17 | Not for these styles: softer and more painterly, weaker outlines, the dearest. |

Model ids change. List the current ones with
`curl -s -H "x-goog-api-key: $GEMINI_API_KEY" "https://generativelanguage.googleapis.com/v1beta/models?pageSize=200" | grep -o '"models/[^"]*image[^"]*"'`
(Google; `gemini-nano-banana-2.1` lists without "image" in its id) or
`curl -s https://openrouter.ai/api/v1/models | grep -o '"id":"[^"]*image[^"]*"'`
(OpenRouter), and prefer the newest Gemini image model.

## Step 1: The brief and the idea

Settle in a few lines (in the plan's features table, if the post goes through
`ai-assisted-blog-post`):

- **Style:** one of the five (the table above), the same for the whole post unless Adjie says
  otherwise.
- **The point:** one sentence: the step the picture shows, or what the section argues or
  feels.
- **The idea:** how the picture says it, in the style's own grammar. wikiHow needs one verb
  and the object in the hands; Tempo a visual metaphor with an everyday object; Summer flat
  a stylish person with one witty gesture; the collage a hero object plus four to six
  fragments, each in a named old technique; the hybrid a real place and a small human moment
  in it. Each guide has a table or recipe for this; take the idea from
  this style's guide, never from another's (the great wall, rule 4). Pass the brief a test:
  someone who has not read the post should get the point from the description alone.
- **Who:** age, skin, hair, clothes. Indonesian people and settings where the post is about
  Indonesia; vary age, gender, skin tone and hair across a post, or keep the post's own
  character (Robert, Geoff). A public figure (a president, a minister) by name and
  description, for editorial comment on their public role: exaggerate the expression and
  posture, never their ethnicity or body, and never caricature a private person. **The
  reverse matters too:** a generic "heavy-set Indonesian politician in a peci" came back as a
  clear likeness of the sitting president in the collage and Tempo tests. When nobody
  real is meant, say so ("an invented face that resembles no real politician") and change
  the dress and the pose that point to someone; look at the face before using it. When
  someone real is meant, name them, and let Adjie decide.
- **Words in the picture:** usually none. A short quoted phrase works (a speech bubble, a
  phone screen, a ribbon banner); detailed writing (a receipt, a list, a screen of text)
  always becomes slop, so ask for "only wavy scribble lines, no readable words". With words,
  make one picture per
  language: for the second, attach the first picture with `--ref` and ask to "make it again
  exactly ... changing only the words: the quoted words now read exactly ..." (prompt in
  `_illustrations/restyle/gsl-ill-podium-id--tempo.txt`). Tested in the Tempo, flat
  and collage styles: the same picture came back, only the words changed, spelled
  right. Words on something small (a phone in a hand) can come out garbled: make the object
  big and the words "big bold letters on two lines", and zoom in to check every letter.
- **Shape:** `4:3` in a post, `16:9` for a social card.

## Step 2: Write the prompt

From the style's own guide only, in this order: the **opening line**, the **scene** (the
guide says what goes in it and in which order), the **style block** word for word, then **one text rule** (`No text, no letters, no numbers.`, `No readable words.` for the collage, or `No text
except the exact words quoted in the scene.`). Read the guide's "What the tests taught" before
the first try: it fixes the usual failures (a device facing away, props too small, a scowl
instead of a frown, US dollars, the examples leaking into the scene).

Save it as `_illustrations/<name>.txt` at the repo root (Jekyll skips `_` folders, so it stays
in git, unpublished, for regenerating later). `<name>` starts with the post's short prefix,
like the other pictures: `gpi-ill-throne.txt`.

## Step 3: Generate and look at it

```sh
K=.claude/skills/editorial-illustration
GEMINI_API_KEY=... sh $K/scripts/generate.sh tempo _illustrations/<name>.txt <scratchpad>/<name>.png
```

- The first argument is the style key from the table: `wikihow`, `tempo`, `flat`, `collage`,
  or `hybrid`.
- The script runs the great wall in three steps. First it checks the prompt, free: its own
  style block is there, no other style's block is, and no other style's word is used (exit
  2, nothing generated, with the reason). Then it generates with Nano Banana 2.1 and this
  style's own examples only. Then the judge looks at the picture: `style check: ... stays in
  <style>` (exit 0) or `LEAK` with the foreign features (exit 3: the picture failed).
  `--lint-only` runs the first step alone, to check a prompt before spending anything.
- `--aspect 16:9` for a social card; `--model <id>` to change the model; `--ref <image>` to
  attach a picture *before* the examples: a post's earlier picture, to keep a character the
  same (open the prompt with "The first attached picture shows a character. Draw the same
  ..."), or Adjie's photograph for the hybrid style (its guide has the opening line). A
  reference from another style is refused.
- Run one at a time (two at most on Google). Parallel requests get a 429; the script waits
  and retries a 429, 502 or 503 three times, ten seconds apart.

Then **open the PNG with Read and check it**:

- [ ] The script said `stays in <style>`. A leak is a failed picture, whatever it looks like.
- [ ] The point reads in two seconds without the caption: the step, the joke, the moment.
- [ ] It is the style and only the style: compare with its examples, its guide's "What to
      reject", and the neighbour table in "The great wall".
- [ ] Faces: the expression asked for; a public figure is recognisable and not demeaned.
- [ ] Hands: five fingers, holding things the way people do. A device faces the way asked.
- [ ] Words: exactly the ones quoted, spelled right; nothing else readable (the collage's
      illegible old handwriting is texture and is fine).
- [ ] Nothing from the examples that the scene did not ask for; no logo, masthead, title,
      watermark or signature; no symbol the guide forbids.
- [ ] No stray smudge or square in an empty background.

If it fails, say in the prompt what was wrong ("the calculator faces the viewer, with its
keys visible") and generate again. Two or three tries is normal. Keep the final wording in
the `.txt` file.

## Step 4: Put it in the post

Convert the PNG to WebP at the width the blog needs:

```sh
node .claude/skills/editorial-illustration/scripts/render.mjs <scratchpad>/<name>.png assets/img/<name>.webp
```

(`--width 1456` is the default, sharp on high-density screens and usually 60 to 150 KB;
`--width 1200` for a 16:9 card.) Then an `<img>` with its real pixel size, like the other
images on the blog, inside a `<figure>` when it has a caption:

```html
<figure>
<img src="/assets/img/rvo-ill-compare-rent.webp" alt="A woman holds up two rental listings, one in each hand, and compares them" width="1456" height="1092" loading="lazy">
</figure>
```

- **Alt text** says what the picture shows, in the post's language: what the person does and
  with what, or "Caricature of ...", "Collage of ..." when it is one. Never
  the style's source.
- A picture can also be the social card (`image:` and `image_alt:` in the front matter).
  Cards work best wide: generate a version with `--aspect 16:9` and render it with
  `--width 1200`.
- These pictures carry their own background, so they work in both themes.

## Step 5: Mark its focus box (mandatory)

Every illustration gets a focus box in `_data/focus.yml` as soon as it is saved, lead picture
or not: the post cards, the social card and the share poster crop it to other shapes, and the
box is what each crop keeps whole. Without one the crop is cut at the centre, which on a
split picture shows only the seam. Follow `references/focus-box.md` exactly:

1. `python3 _build/focus.py --new assets/img/<name>.webp` prints the line; add it.
2. Name the subject in its comment, then box that subject alone, narrow enough for the square
   card.
3. `python3 _build/focus.py --preview <scratchpad>/focus` and look at every crop: each must
   show the subject whole and make sense alone. Fix the box until it does.
4. `python3 _build/focus.py` must say OK. Only then run `node _build/og.mjs` for a social card.

What to box, by style: the person with the object in their hands (wikiHow); the caricature
with the gesture or object that makes the joke, and the speech bubble when its words are the
point (Tempo, Summer flat); the one modern thing the collage is about, not the paper around
it; the drawn characters and what they do, not the photograph around them (hybrid). On a two-sided
picture pick the side the post argues about, never the dividing line. Never the whole
picture.

Run the checks in `CLAUDE.md`, and commit the WebP with its prompt file and its
`_data/focus.yml` line. Tell Adjie the style, the model and the number of tries.
