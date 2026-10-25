# The prompt

Tuned on Nano Banana 2.1 with eighteen test pictures (25 October 2026). A prompt has three
parts, in this order: the opening line, the scene, the style block. Pass the four pictures in
`examples/` as `--ref`; they carry the look better than words alone.

## 1. Opening line

```text
Draw a new picture in the drawing style of the attached reference pictures:
```

To keep a post's character the same across pictures, attach that post's first picture as
the **first** `--ref` (before the four examples) and open with:

```text
The first attached picture shows a character. Draw the same [man / woman] (same face, hair
and clothes) in a new scene, in the drawing style of all the attached pictures:
```

(Tested: the same face, hair and shirt came back in a new pose. Still check the face.)

## 2. The scene

One to three sentences, in this order: **who** (age, skin, hair, clothes), **the action with
the object**, **where** (one or two props), then **framing** and `4:3`. The example that made
`examples/ref-midshot.webp`:

```text
A man in his thirties with light skin and short brown hair, wearing a plain orange t-shirt,
sits at a wooden desk and checks a total on a calculator he holds tilted towards the viewer
so its keys show. A paper receipt and a small pink piggy bank are on the desk. Mid-shot,
head to waist, 4:3.
```

What the tests taught:

- **Say which way a device faces.** Left alone, models show the back of a calculator or a
  phone. "Tilted towards the viewer so its keys show", "looking at the phone screen".
- **Spell out the action as a movement.** "Pays with her phone" gave a phone held in the
  air; "holds her phone flat just above the QR code stand, looking at the phone screen"
  gave the real thing.
- **Hands in a close-up:** say "exactly two hands" and what each one does, plus
  "anatomically correct hands, five fingers each". Without it, a close-up got three hands.
- **Anything with writing on it** (a notebook, a receipt, a screen, a sign): say "only
  wavy scribble lines, no readable words". Asking for "a list" got garbled fake English;
  with the scribble line, the page came out clean. Charts are safe: "a simple line chart
  going up" drew one with no labels.
- **Never use the words "label", "labelled" or "sign"**, not even to forbid them. "Labelled-free
  envelopes" got three envelopes with Indonesian words written on them. Say what it looks like
  instead: "plain white envelopes with nothing written on them".
- **Always name the clothes.** Whatever you leave out comes from the references: a man with
  no shirt described got the orange t-shirt of `ref-midshot.webp`. In a split panel, say
  "the same man in the same [shirt]" on the second side.
- **Spell out the pose with vehicles and furniture.** "Sits on a parked scooter" got a man
  standing beside it. Say "sitting astride the scooter, both feet on the ground".
- **People of any background work:** a hijab, dark skin with short natural hair, an older man
  with grey hair all came out well and respectfully. Name skin tone and hair directly.
- Name the background colour in the scene when it matters ("pale warm beige background",
  "pale green background"). Keep a post's pictures in one colour family.

## 3. The style block

Word for word, at the end:

```text
Style: match the attached reference pictures exactly: an instructional step illustration with
realistic simplified proportions, crisp even outlines in a darker shade of each colour (never
black), saturated flat fills with soft painterly shading and gentle highlights, simple
friendly faces with small almond eyes and a heavy upper lid line. The background is a soft,
out-of-focus painted wash with large blurred shapes and no detail, paler than the person.
Only the drawing style comes from the references, not their people or scenes. No text, no
letters, no logo, no watermark, no signature.
```

"Only the drawing style comes from the references" stops the model reusing the people in the
example pictures. Without any `--ref` the same block still works, a little flatter and less
like wikiHow; drop the words "match the attached reference pictures exactly:" then.

## Framing variants

Swap the framing sentence:

- **Mid-shot:** "Mid-shot, head to waist, 4:3."
- **Close-up:** "Close-up from the person's own point of view: exactly two hands, ... 4:3."
- **Comparison:** "Split diagonally into two panels by a thick dark line from the top right to
  the bottom left. On the left, [...]. On the right, the same [person] [...]. Each panel has
  its own pale background colour. 4:3." (made `examples/ref-split-panel.webp`)
- **Back view:** "Seen from behind and slightly to the side, [who] [does what] and looks at
  [...]. 4:3." (made `examples/ref-back-view.webp`)
- **Social card:** "Wide picture for a social card: the [person] on the left third, plenty of
  empty pale background on the right. 16:9." with `--aspect 16:9`. (Tested: it comes back
  at 1376 × 768 with the person on the left and room on the right; render it with
  `--width 1200`.)

## Don'ts

- Don't name wikiHow in the prompt. The style block and the references give the look, and a
  brand name invites its watermark.
- Don't ask for words, labels or numbers in the picture.
- Don't put real wikiHow pictures in the repo (it is public and they are wikiHow's). The four
  in `examples/` were generated from Adjie's wikiHow samples and are ours to keep.
