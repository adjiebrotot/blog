---
name: wikihow-illustration
description: Make a wikiHow-style illustration for a post on this blog with an image model on OpenRouter. A friendly, clean, softly shaded drawing of one person doing one action, on a pale background, saved as WebP in assets/img/. Use when Adjie asks for an illustration, a drawing, an image, a "wikiHow-style" picture, a picture for a step or a section, or a cover image that is not a screenshot or a chart.
---

# wikiHow-style illustration

The look of a wikiHow step picture: one ordinary person, mid-shot, doing the one thing the
step is about, in clean line art with soft shading and a pale, almost empty background.
Friendly and plain. It explains an action, so the hands and the object they hold are the
centre of the picture. The four pictures in `examples/` are the target look: a mid-shot, an
Indonesian street scene, a split panel and a back view. They were generated from Adjie's
wikiHow samples and are passed to the model as style references every time.

The style is the inspiration, not the brand. **Never** ask for or keep the wikiHow logo or
watermark, never commit a real wikiHow picture to this public repo, and never say in a
caption or alt text that the picture is from wikiHow.

```
brief  →  prompt in _illustrations/<name>.txt  →  generate.mjs (OpenRouter)  →  look, retry
       →  render.mjs  →  assets/img/<name>.webp  →  <img> in the post
```

## Before you start: the API key

Pictures come from an image model on [OpenRouter](https://openrouter.ai/). The script reads
the key from `OPENROUTER_API_KEY`. If it is not set, **ask Adjie for a key** (or for another
image service he prefers) before doing anything else, and pass it only as an environment
variable for the command. Never write a key into a file, a commit, a prompt file or a post.

OpenRouter refuses image output when the key has less than $1.00 of credit left (error
402). Tell Adjie the balance needs topping up; don't retry.

## Which model

| Model | Cost per picture | Use for |
|-------|------------------|---------|
| `google/gemini-nano-banana-2.1` | about $0.04 | **Default** (Adjie's choice). The wikiHow look at a quarter of the price of Pro; follows the reference pictures well. |
| `google/gemini-3-pro-image` | about $0.14 | When Nano Banana keeps failing a scene: slightly cleaner outlines and hands. |
| `google/gemini-3.1-flash-image` | about $0.07 | A fallback if the two above are unavailable. |
| `openai/gpt-5.4-image-2` | about $0.17 | Not for this style: softer and more painterly, weaker outlines, and the dearest. |

Compared on 25 October 2026 with the same prompt; the prompt was then tuned on Nano Banana. Model ids change: if one is gone, list the
current ones with
`curl -s https://openrouter.ai/api/v1/models | grep -o '"id":"[^"]*image[^"]*"'`
and prefer the newest Gemini image model.

## Step 1: Write the brief

Settle these in a few lines (in the plan, if the post goes through `ai-assisted-blog-post`):

- **Action:** the one verb the picture shows, and the object in the hands.
- **Who:** an everyday person. Vary age, gender, skin tone and hair across a post; match the
  post's character if it has one (Robert, Geoff). Indonesian posts can show Indonesian
  people and settings (a warung, a motorbike, a batik shirt, a hijab) when it fits.
- **Framing:** mid-shot (head to waist) by default; a close-up on the hands for a detail
  step; a diagonal split panel for "this vs that" or "before and after"; a back view when
  what they look at matters more than their face.
- **Setting:** one or two props that say where we are, nothing more.
- **Words in the picture:** none, so one picture serves both languages. Models garble text,
  so put numbers and labels in the post, not the picture.
- **Keep the pose simple.** Sitting at a table, standing, holding something up. Complicated
  poses (on a vehicle, mid-stride, two people touching) go wrong more often.

## Step 2: Write the prompt

Build it from `references/image-prompt.md`: the opening line, the scene from the brief, then
the style block word for word, so every picture on the blog matches. Its "What the tests
taught" list fixes the usual failures (device facing away, extra hands, fake text), so apply
it before the first try. `references/style-guide.md` explains
the look in detail; use it to word the scene and to judge the result.

Save the prompt as `_illustrations/<name>.txt` at the repo root. Jekyll skips folders that
start with `_`, so it stays in git, unpublished, for regenerating later. `<name>` starts
with the post's short prefix, like the screenshots (`rvo-...`): `rvo-ill-compare-rent.txt`.

## Step 3: Generate and look at it

```sh
K=.claude/skills/wikihow-illustration
OPENROUTER_API_KEY=... node $K/scripts/generate.mjs \
  _illustrations/<name>.txt <scratchpad>/<name>.png \
  --ref $K/examples/ref-midshot.webp --ref $K/examples/ref-indonesia.webp \
  --ref $K/examples/ref-split-panel.webp --ref $K/examples/ref-back-view.webp
```

- `--model` picks the model (default `google/gemini-nano-banana-2.1`), `--aspect` the shape
  (default `4:3`; use `16:9` for a social card).
- `--ref` attaches a style reference and can be repeated. Always pass the four examples. For
  the same character across a post, put that post's first picture before them (see
  `references/image-prompt.md`).
- **One request at a time.** Parallel requests get a 429 from OpenRouter; the script waits
  and retries three times, but running several at once still fails.

Then **open the PNG with Read and check it**:

- [ ] The action reads in one second: you can say the step from the picture alone.
- [ ] Hands: five fingers, holding the object the way people do.
- [ ] The object is right (a calculator shows its keys, a phone its screen to the user).
- [ ] Face calm and friendly, eyes level, looking at the object or the reader.
- [ ] Clean outlines, soft shading, pale quiet background: it sits with the style reference.
- [ ] No text, letters, logo, watermark or signature anywhere.

If it fails, change the prompt (say what was wrong: "the calculator faces the viewer, with
its keys visible") and generate again. Two or three tries is normal; draft with the cheaper
model if it takes more. Keep the final wording in the `.txt` file.

## Step 4: Put it in the post

Convert the PNG to WebP at the width the blog needs:

```sh
node .claude/skills/wikihow-illustration/scripts/render.mjs <scratchpad>/<name>.png assets/img/<name>.webp
```

(`--width 1456` is the default, sharp on high-density screens and usually 60 to 150 KB.)
Then use an `<img>` with its real pixel size, like the other images on the blog, inside a
`<figure>` when it has a caption:

```html
<figure>
<img src="/assets/img/rvo-ill-compare-rent.webp" alt="A woman holds up two rental listings, one in each hand, and compares them" width="1456" height="1092" loading="lazy">
</figure>
```

- **Alt text** says what the person is doing and with what, in the post's language. Not
  "illustration of" and not the style.
- A picture can also be the social card (`image:` and `image_alt:` in the front matter).
  Cards work best wide: generate a version with `--aspect 16:9` and render it with
  `--width 1200`.
- The picture carries its own pale background, so it works in the light and the dark theme.

Run the checks in `CLAUDE.md`, and commit the WebP with its prompt file. Tell Adjie which
model made it and what it cost (the script prints both).
