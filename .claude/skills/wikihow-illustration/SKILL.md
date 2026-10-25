---
name: wikihow-illustration
description: Make a wikiHow-style illustration for a post on this blog. A friendly, flat, softly shaded drawing of one person doing one action, on a pale background, drawn as SVG and rendered to WebP in assets/img/ (or a prompt for an image model, when Adjie wants to generate it himself). Use when Adjie asks for an illustration, a drawing, a "wikiHow-style" image, a picture for a step or a section, or a cover image that is not a screenshot or a chart.
---

# wikiHow-style illustration

The look of a wikiHow step picture: one ordinary person, mid-shot, doing the one thing the
step is about, drawn in clean flat colour with a single soft shadow tone and a pale, almost
empty background. Friendly and plain, never cartoonish or glossy. It explains an action, so
the hands and the object they hold are the centre of the picture.

The style is the inspiration, not the brand. **Never** draw the wikiHow logo or watermark,
copy a real wikiHow picture, or say in a caption or alt text that the picture is from
wikiHow.

```
brief (what the picture must show)  →  SVG in _illustrations/  →  render  →  look at it, fix
                                                                   →  WebP in assets/img/  →  <img> in the post
```

## When a picture earns its place

Use one where a reader has to *imagine a person doing something*: a habit, a step, a
choice, a feeling about money or work ("put the receipt in an envelope", "ask your landlord
first", "two shirts, one budget"). Don't use one where a chart, a screenshot or a tool embed
shows the real thing better (see the Features table in `ai-assisted-blog-post`). One or two
per post is usually right; one per step suits a how-to post.

## Step 1: Write the brief

Before drawing, settle these in a few lines (in the plan, if the post goes through
`ai-assisted-blog-post`):

- **Action:** the one verb the picture shows, and the object in the hands.
- **Who:** an everyday person. Vary age, gender, skin tone and hair across a post; match the
  post's character if it has one (Robert, Geoff). Indonesian posts can show Indonesian
  people and settings (a warung, a motorbike, a batik shirt, a hijab) when it fits.
- **Framing:** mid-shot (head to waist) by default; a close-up on the hands for a detail
  step; a diagonal split panel for a "this vs that" or "before and after".
- **Setting:** one or two props that say where we are, nothing more.
- **Words in the picture:** avoid them, so one picture serves both languages. Numbers and
  symbols (1,250, %, $, Rp) are fine. If words are unavoidable, make one file per language
  (`-en.webp`, `-id.webp`), like the screenshots.

## Step 2: Draw the SVG

Read `references/style-guide.md` (the look) and `references/svg-kit.md` (how to build it),
and open `examples/budget-calculator.svg`, a finished picture that follows both. Start from
a copy of it when the scene is close; its structure (define, fill, shade, outline) is the
part to keep.

Save the source as `_illustrations/<name>.svg` at the repo root. Jekyll skips folders that
start with `_`, so the source stays in git for later edits but is not published. `<name>`
starts with the post's short prefix, like the screenshots (`rvo-...`): `rvo-ill-compare-rent.svg`.

## Step 3: Render and look at it

```sh
node .claude/skills/wikihow-illustration/scripts/render.mjs \
  _illustrations/<name>.svg assets/img/<name>.webp --preview <scratchpad>/<name>.png
```

The default `--width 1456` is twice the 728 × 546 drawing, sharp on high-density screens and
usually 30 to 80 KB. Then **open the preview PNG with Read and look at it** as a reader
would, against the checklist below. Fix and re-render; two or three rounds is normal. Stop
when it passes, not when it is perfect.

- [ ] The action reads in one second: you can say the step from the picture alone.
- [ ] Hands are on the object, at a believable size (a hand is about as long as the face).
- [ ] Face: eyes level, the same size and looking at the object or the reader; a calm,
      friendly expression.
- [ ] Every shape has its darker outline, and the shadow sits on the same side everywhere
      (light from the upper right in the example).
- [ ] No stray gaps between shapes, no outline cutting through a hand or a face.
- [ ] Background is pale and quiet; the person is the most saturated thing in the picture.
- [ ] Nothing from wikiHow: no logo, no watermark, no copied scene.
- [ ] No words, or one file per language.

If after three rounds a part still looks wrong (hands are the usual one), simplify it:
crop it out of frame, turn it away, or put the object in front of it. A simple picture that
reads is better than a detailed one that looks off.

## Step 4: Put it in the post

Use an `<img>` with its real pixel size, like the other images on the blog, inside a
`<figure>` when it has a caption:

```html
<figure>
<img src="/assets/img/rvo-ill-compare-rent.webp" alt="A woman holds up two rental listings, one in each hand, and compares them" width="1456" height="1092" loading="lazy">
</figure>
```

- **Alt text** says what the person is doing and with what, in the post's language. Not
  "illustration of" and not the style.
- The first picture in a post can also be the social card (`image:` and `image_alt:` in the
  front matter). Cards work best at 1200 × 630, so for a card draw a second SVG with
  `viewBox="0 0 1200 630"` (the same scene, wider, the person off-centre) and render it with
  `--width 1200`.
- The picture carries its own pale background, so it works in both the light and the dark
  theme. Don't make it transparent.

Then run the checks in `CLAUDE.md` and commit the SVG source with the WebP.

## When Adjie wants to generate it himself

If he would rather use an image model (ChatGPT, Gemini, Midjourney...) or asks for "a
prompt", write one from `references/image-prompt.md` instead of drawing. When he sends the
result back, convert it with the same script (it reads PNG, JPG and WebP too), check it
against the checklist above, and place it as in Step 4. There is no SVG source then; say so
in the commit.
