# The prompt

A prompt is the scene (from the brief in `SKILL.md`), then the style block word for word.
This one made `examples/style-reference.webp`:

```text
A man in his thirties with light skin and short brown hair, wearing a plain orange t-shirt,
holds a calculator in both hands and checks the total, sitting at a wooden desk with a paper
receipt and a small pink piggy bank on it. Mid-shot, head to waist, 4:3.

Style: clean digital illustration in the style of a how-to guide step picture. Realistic,
simplified proportions. Every shape has a thin outline in a darker shade of its own colour,
never black. Flat, fairly saturated fills with soft painterly shading and gentle highlights,
light from the upper right. Simple friendly face: small almond eyes with a heavy upper lid
line, a one-stroke nose, a small closed smile. Pale, quiet, light blue-grey background with
a soft gradient and almost no detail. No text, no letters, no logo, no watermark, no
signature.
```

## The scene

Write it in one or two sentences, in this order: **who** (age, skin, hair, clothes),
**the action with the object**, **where** (one or two props), then **framing**. Be
concrete about the object's position when it matters ("holding the phone so its screen
faces her", "the calculator tilted towards the viewer so its keys show"); models often show
the back of a device.

With `--ref`, open with:

```text
Match the drawing style of the attached reference picture exactly (line, colour, shading,
background), but draw a new scene:
```

## Framing variants

Swap the framing sentence:

- **Mid-shot:** "Mid-shot, head to waist, 4:3."
- **Close-up:** "Close-up on the hands and the [object], a bit of sleeve visible, 4:3."
- **Comparison:** "Split diagonally into two panels by a thick dark line: on the left
  [...], on the right [...], each with its own pale background colour. 4:3."
- **Back view:** "Seen from behind and slightly to the side, so we see what they are
  looking at: [...]. 4:3."
- **Social card:** end with "16:9, the person on the left third, empty pale space on the
  right." and generate with `--aspect 16:9`.

## Background colour

Keep it pale. Change "light blue-grey" to suit the scene: pale green for outdoors or
plants, pale warm beige for a kitchen or a shop, pale sky blue for travel. One colour per
picture, and keep a post's pictures in the same family.

## Don'ts

- Don't name wikiHow in the prompt. Some models refuse a brand, others add its watermark;
  the style block describes the look without it.
- Don't ask for words, labels or numbers in the picture.
- Don't attach real wikiHow pictures as references: they are copyrighted. Use the style
  reference here or a picture already on this blog.
