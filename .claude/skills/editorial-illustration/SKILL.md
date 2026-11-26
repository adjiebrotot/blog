---
name: editorial-illustration
description: Make an editorial illustration for a post on this blog with an image model, in one of three styles. Tempo (the Indonesian news-magazine cover painting: a visual metaphor, gouache-painted caricatures on one bold colour), Summer flat (the retro beach-read novel cover: three or four flat colours, a stylish figure with sunglasses and a witty gesture) or Renaissance collage (a torn-paper mood board where modern things, a bullet train, a bomber, a laptop, a person with a phone, are painted, engraved or carved in old-master techniques). Saved as WebP in assets/img/. Use when Adjie asks for one of these styles by name ("Tempo style", "summer novel", "flat", "Renaissance", "collage"), for a satirical, editorial or magazine-cover picture, a caricature of a public figure, a social card with a point of view, or a picture that makes an argument or sets a mood rather than showing a step. For one person doing one step in a soft instructional style, use wikihow-illustration; for a place or system with exact layout, isometric-illustration.
---

# Editorial illustration

Three styles that make a point rather than explain a step. Each has its own style guide in
`references/`, three example pictures in `examples/` that the generator attaches as style
references, and a style block to paste word for word. They share the wikiHow skill's
generator (same keys, same providers) through `scripts/generate.sh`.

| | Tempo | Summer flat | Renaissance collage |
|---|---|---|---|
| Looks like | a *Tempo* cover painting | a summer beach-read novel cover | a scrapbook of torn old-master fragments |
| Made of | soft gouache, no outlines, warm light and violet shadows | 3 or 4 flat colours plus black and white, crisp edges | oil paint, sepia engraving, marble, fresco, gold leaf, torn paper |
| People | gentle caricatures, big heads, pushed expressions | elegant fashion figures, eyes hidden by sunglasses, red lips | old-master portraits of modern people, or no people |
| Background | one bold flat colour, a big empty area | one bright colour, stripes or polka dots | layered paper, painted sky |
| Carries | a visual metaphor: a satirical or political point | a feeling: a light personal or money-habit point | a big theme: history, wealth and power, eras compared |
| Guide | `references/tempo.md` | `references/summer-flat.md` | `references/renaissance-collage.md` |

**Which skill.** `wikihow-illustration` shows a reader *how*: one person, one step, a pale
background. This skill shows a reader *what the writer thinks*: a metaphor, a mood, a jab.
`isometric-illustration` shows *how a place or system fits together*, drawn in code. Keep one
style through a post, so its pictures read as a set.

**The styles are the inspiration, not the brands.** Never ask for or keep a *Tempo* masthead,
cover lines, a price or a barcode, a book title or author name, or a copy of a real painting.
Never commit Adjie's sample covers or the Renaissance sample to this public repo (they are
not ours): the nine pictures in `examples/` were generated from them and are ours to keep.
Never say in a caption or alt text that a picture is from *Tempo* or a book cover.

```
brief → the idea → prompt in _illustrations/<name>.txt → generate.sh <style> → look, retry
      → render.mjs → assets/img/<name>.webp → <img> in the post
```

## Before you start: the API key

The same as `wikihow-illustration`: the generator reads `GEMINI_API_KEY` (Google Gemini API,
direct) or `OPENROUTER_API_KEY` (OpenRouter). Adjie uses both. If neither is set, **ask Adjie
for a key** before anything else, and pass it only as an environment variable for the
command. Never write a key into a file, a commit, a prompt file or a post.

- **429 "rate-limited to prevent exceeding its monthly spending cap"** (Google): the project
  is near the spend cap set in AI Studio, which is separate from its prepaid credit. It
  lifted after a minute or two each time in testing: run one picture at a time and wait a
  minute after a 429 (a refused request costs nothing). If it never lifts, ask Adjie to
  raise the project's spend cap.
- **402 "prepayment credits are depleted"** (Google) or **402** on OpenRouter (less than
  $1.00 left): the account is empty. Stop, tell Adjie it needs topping up, don't retry.

## Which model

**Nano Banana 2.1** (`gemini-nano-banana-2.1` on Google, `google/gemini-nano-banana-2.1` on
OpenRouter, about $0.04 a picture), the default in `generate.sh`. It was tuned on it on
26 November 2026: about twenty tuning pictures, then the blog's fifteen illustration briefs
redrawn in all three styles. Gemini 3 Pro Image (`--model
gemini-3-pro-image`, dearer) made the Tempo test more cartoonish, with an angry childlike face,
so don't switch to it for looks; try it only when hands or text keep failing.

## Step 1: The brief and the idea

Settle in a few lines (in the plan's features table, if the post goes through
`ai-assisted-blog-post`):

- **Style:** Tempo, Summer flat or Renaissance collage (the table above), the same for the
  whole post unless Adjie says otherwise.
- **The point:** one sentence: what the section argues or feels.
- **The idea:** how the picture says it, in the style's own grammar. Tempo needs a visual
  metaphor with an everyday object; Summer flat a stylish person with one witty gesture;
  the collage a hero object plus four to six fragments, each in a named old technique. Each
  guide has a table or recipe for this. Pass the briefing a test: someone who has not read
  the post should get the point from the description alone.
- **Who:** age, skin, hair, clothes. Indonesian people and settings where the post is about
  Indonesia. A public figure (a president, a minister) by name and description, for editorial
  comment on their public role: exaggerate the expression and posture, never their ethnicity
  or body, and never caricature a private person. **The reverse matters too:** a generic
  "heavy-set Indonesian politician in a peci" came back as a clear likeness of the sitting
  president in the collage and Tempo tests. When nobody real is meant, say so: "an invented
  face that resembles no real politician". When someone real is meant, name them, and let
  Adjie decide.
- **Words in the picture:** usually none. A short quoted phrase works (a speech bubble, a
  phone screen, a ribbon banner in the collage); with words, make one picture per language.
- **Shape:** `4:3` in a post, `16:9` for a social card.

## Step 2: Write the prompt

From the style's guide, in this order: the **opening line**, the **scene** (the guide says
what goes in it and in which order), the **style block** word for word, then **one text
rule** (`No text, no letters, no numbers.`, `No readable words.` for the collage, or `No text
except the exact words quoted in the scene.`). Read the guide's "What the tests taught" before
the first try: it fixes the usual failures (props too small, a scowl instead of a frown,
US dollars, the examples leaking into the scene).

Save it as `_illustrations/<name>.txt` at the repo root (Jekyll skips `_` folders, so it stays
in git, unpublished). `<name>` starts with the post's short prefix, like the other pictures:
`gpi-ill-throne.txt`.

## Step 3: Generate and look at it

```sh
K=.claude/skills/editorial-illustration
GEMINI_API_KEY=... sh $K/scripts/generate.sh tempo _illustrations/<name>.txt <scratchpad>/<name>.png
```

- The first argument is the style: `tempo`, `flat` or `collage`. The script attaches that
  style's three examples and picks Nano Banana 2.1.
- `--aspect 16:9` for a social card; `--model <id>` to change the model; `--ref <image>` to
  attach a post's earlier picture *before* the examples, to keep a character the same (open
  the prompt with "The first attached picture shows a character. Draw the same ...").
- Run one at a time on Google (two at most); the script waits and retries a 429 or 503
  three times, ten seconds apart.

Then **open the PNG with Read and check it**:

- [ ] The point reads in two seconds without the caption.
- [ ] It is the style: compare with the style's examples and the guide's "What to reject".
- [ ] Faces: the expression asked for; a public figure is recognisable and not demeaned.
- [ ] Hands: five fingers, holding things the way people do.
- [ ] Words: exactly the ones quoted, spelled right; nothing else readable (the collage's
      illegible old handwriting is texture and is fine).
- [ ] Nothing from the examples that the scene did not ask for, no masthead, title, logo,
      watermark or signature, and (collage) no classical figure or famous painting.
- [ ] No stray smudge or square in an empty background.

If it fails, say in the prompt what was wrong and generate again. Two or three tries is
normal. Keep the final wording in the `.txt` file.

## Step 4: Put it in the post

Exactly as in `wikihow-illustration`: render the PNG to WebP with
`node .claude/skills/wikihow-illustration/scripts/render.mjs <png> assets/img/<name>.webp`
(`--width 1456` by default, `--width 1200` for a 16:9 card), then an `<img>` with its real
pixel size, inside a `<figure>`, with alt text that says what the picture shows in the
post's language ("Caricature of ...", "Collage of ..." is fine when it is one; never the
style's source). These pictures carry their own background, so they work in both themes.

Run the checks in `CLAUDE.md`, and commit the WebP with its prompt file. Tell Adjie the style,
the model and the number of tries.
