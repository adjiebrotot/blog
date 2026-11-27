# wikiHow: the instructional step picture

The look of a wikiHow step picture: one ordinary person, mid-shot, doing the one thing the
step is about, in clean line art with soft shading and a pale, almost empty background.
Friendly and plain. It explains an action, so the hands and the object they hold are the
centre of the picture. Adjie's samples were wikiHow step pictures (a man reading a book in a
chair, a woman holding up two shirts, a painter at an easel with a split-panel palette
close-up, a man painting a beach scene from behind). The four pictures in `examples/` were
generated from them and are ours to keep; `generate.sh wikihow` attaches them: a mid-shot
(`wikihow-midshot.webp`), an Indonesian street scene (`wikihow-indonesia.webp`), a split
panel (`wikihow-split.webp`) and a back view (`wikihow-back.webp`).

## The look

- **Friendly and plain.** Ordinary people in ordinary clothes, in a calm good mood. A small
  closed smile or a concentrating look. Never a grin, never a pose for the camera.
- **Realistic proportions, simplified.** Not chibi, not big-eyed, not a caricature. Detail
  is left out, not exaggerated.
- **One action.** Everything in the frame serves the verb of the step. The object in the
  hands is drawn clearly, and a little larger than life if that helps it read.
- **Line:** every shape has a thin, even outline in a **darker shade of its own colour**,
  never black: skin gets a warm brown, an orange shirt a burnt orange. Few inner lines: a
  nose is one stroke, a hand one or two finger lines, a fold one curve.
- **Colour and shading:** clean, fairly saturated fills for the person and the main object
  (orange, teal, green, red, pink, mid blue shirts; warm skin; brown, ginger, black or blond
  hair). Soft shading on the side away from the light, gentle highlights on hair and glossy
  things. Painterly at the edges, never glossy, 3D or photo-real.
- **The background is the palest, least saturated part:** light blue-grey, pale green, pale
  sky, with a soft gradient, a big soft blob, or a hint of a wall, window or horizon.
- **Faces:** small almond eyes with a heavier upper lid line, eyebrows as one soft stroke, a
  one-stroke nose, a small curved mouth. Looking down at the object is often truer to the
  step than looking at the reader.
- **Hands** hold things the way people do: a book by its edges with the thumbs on the pages,
  a phone in the palm with the thumb on the screen, a hanger by its hook.
- **Composition:** mid-shot by default (head in the upper third, hands and object at the
  centre, the body cut by the frame or a table edge); a close-up for a detail step, a split
  panel for a comparison, a back view when what they look at matters more. Props in the
  foreground may overlap the body (a desk edge, a plant, a mug). Few of them.

## The idea

Settle the brief in a few lines:

- **Action:** the one verb the picture shows, and the object in the hands.
- **Who:** an everyday person. Vary age, gender, skin tone and hair across a post; match the
  post's character if it has one (Robert, Geoff). Indonesian posts can show Indonesian
  people and settings (a warung, a motorbike, a batik shirt, a hijab) when it fits.
- **Framing:** mid-shot (head to waist) by default; a close-up on the hands for a detail
  step; a diagonal split panel for "this vs that" or "before and after"; a back view when
  what they look at matters more than their face.
- **Setting:** one or two props that say where we are, nothing more.
- **Keep the pose simple.** Sitting at a table, standing, holding something up. Complicated
  poses (on a vehicle, mid-stride, two people touching) go wrong more often.

Use it where the reader has to imagine a person doing something, not where a chart or a
screenshot shows the real thing.

## The prompt

Opening line:

```text
Draw a new picture in the drawing style of the attached reference pictures:
```

To keep a post's character the same across pictures, attach that post's first picture with
`--ref` (it goes before the examples) and open with:

```text
The first attached picture shows a character. Draw the same [man / woman] (same face, hair
and clothes) in a new scene, in the drawing style of all the attached pictures:
```

(Tested: the same face, hair and shirt came back in a new pose. Still check the face.)

The scene, one to three sentences, in this order: **who** (age, skin, hair, clothes), **the
action with the object**, **where** (one or two props), then **framing** and `4:3`. The
example that made `examples/wikihow-midshot.webp`:

```text
A man in his thirties with light skin and short brown hair, wearing a plain orange t-shirt,
sits at a wooden desk and checks a total on a calculator he holds tilted towards the viewer
so its keys show. A paper receipt and a small pink piggy bank are on the desk. Mid-shot,
head to waist, 4:3.
```

The style block, word for word, at the end:

```text
Style: match the attached reference pictures exactly: an instructional step illustration with
realistic simplified proportions, crisp even outlines in a darker shade of each colour (never
black), saturated flat fills with soft painterly shading and gentle highlights, simple
friendly faces with small almond eyes and a heavy upper lid line. The background is a soft,
out-of-focus painted wash with large blurred shapes and no detail, paler than the person.
Only the drawing style comes from the references, not their people or scenes. No logo, no
watermark, no signature. No text, except the exact words quoted in the scene, if any.
```

With no quoted words in the scene this keeps the picture text-free. "Only the drawing style
comes from the references" stops the model reusing the people in the example pictures.

### Framing variants

Swap the framing sentence:

- **Mid-shot:** "Mid-shot, head to waist, 4:3."
- **Close-up:** "Close-up from the person's own point of view: exactly two hands, ... 4:3."
- **Comparison:** "Split diagonally into two panels by a thick dark line from the top right to
  the bottom left. On the left, [...]. On the right, the same [person] [...]. Each panel has
  its own pale background colour. 4:3." (made `examples/wikihow-split.webp`)
- **Back view:** "Seen from behind and slightly to the side, [who] [does what] and looks at
  [...]. 4:3." (made `examples/wikihow-back.webp`)
- **Social card:** "Wide picture for a social card: the [person] on the left third, plenty of
  empty pale background on the right. 16:9." with `--aspect 16:9`. (Tested: it comes back
  at 1376 × 768 with the person on the left and room on the right.)

## What the tests taught

Tuned on Nano Banana 2.1 with eighteen test pictures (25 October 2026), after comparing four
models on the same prompt: Gemini 3 Pro Image had slightly cleaner outlines and hands at
three times the price; GPT-5.4 Image 2 was softer and more painterly, with weak outlines.

- **Say which way a device faces.** Left alone, models show the back of a calculator or a
  phone. "Tilted towards the viewer so its keys show", "looking at the phone screen".
- **Spell out the action as a movement.** "Pays with her phone" gave a phone held in the
  air; "holds her phone flat just above the QR code stand, looking at the phone screen"
  gave the real thing.
- **Hands in a close-up:** say "exactly two hands" and what each one does, plus
  "anatomically correct hands, five fingers each". Without it, a close-up got three hands.
- **Short text is allowed.** Quote the exact words in the scene ("a mug with the word
  RENT printed on it"), keep it to a word or two or a number, and check the spelling in the
  result. If it comes back wrong after two tries, switch to scribble.
- **Detailed writing** (a notebook, a receipt, a list, a screen of text): say "only
  wavy scribble lines, no readable words". Asking for "a list" got garbled fake English;
  with the scribble line, the page came out clean. Charts are safe: "a simple line chart
  going up" drew one with no labels.
- **Never use the words "label", "labelled" or "sign"**, not even to forbid them.
  "Labelled-free envelopes" got three envelopes with Indonesian words written on them. Say
  what it looks like instead: "plain white envelopes with nothing written on them".
- **Always name the clothes.** Whatever you leave out comes from the examples: a man with
  no shirt described got the orange t-shirt of `wikihow-midshot.webp`. In a split panel, say
  "the same man in the same [shirt]" on the second side.
- **Spell out the pose with vehicles and furniture.** "Sits on a parked scooter" got a man
  standing beside it. Say "sitting astride the scooter, both feet on the ground".
- **People of any background work:** a hijab, dark skin with short natural hair, an older man
  with grey hair all came out well and respectfully. Name skin tone and hair directly.
- **Name the background colour** in the scene when it matters ("pale warm beige background",
  "pale green background"). Keep a post's pictures in one colour family.
- **Don't name wikiHow in the prompt.** The style block and the examples give the look, and a
  brand name invites its watermark.

## What to reject

- Black or thick comic outlines, or no outlines at all.
- Gloss, glow, 3D rendering, photo-realism, heavy texture.
- Busy backgrounds, patterned walls, many props.
- Anime eyes, exaggerated cartoon proportions.
- Detailed or garbled text (notes, receipts, lists), a logo, a watermark or a signature.
  Short, correct, readable text is allowed.
