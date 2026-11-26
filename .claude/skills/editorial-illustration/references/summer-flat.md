# Summer flat: the beach-read novel cover

The look of the flat covers on summer novels (Sophie Kinsella, Meg Cabot, Marian Keyes and
friends): a stylish figure in a few flat colours, eyes hidden behind sunglasses, a witty
gesture, a plain bright background. Light, glamorous, retro 1960s. The three pictures in
`examples/` were generated from Adjie's sample of these covers and are ours to keep;
`generate.sh flat` attaches them.

## The look

- **Three or four flat colours plus black and white.** Turquoise, lemon yellow, coral red,
  hot pink, orange. No gradients, no shading, no texture, no outlines: shapes meet with
  crisp vector edges.
- **Elegant fashion figures.** Long necks, slim limbs, a little elongated, posed like a
  1960s fashion drawing. Skin is one flat tone (any skin tone works).
- **The face is a few shapes.** Big black sunglasses, a hat brim, hair, a book or a hand hide
  the eyes; or the eyes are closed as one curved line. Red lips. A tiny nose or none.
- **A witty gesture tells the story:** a hand over the mouth in shock, sipping through a
  straw, a ticket held up between two fingers, hands on hips.
- **Bold crops.** A face in profile filling the frame, a hat cut off by the top edge, a
  suitcase poking in at a corner.
- **One plain background colour**, or a simple pattern of stripes or polka dots. A white
  silhouette of a skyline along the bottom is the only "place" it needs.

## The idea

Pick the one moment that shows the feeling of the section, with the person as the star:
the saver hugging her piggy bank, the traveller shocked by a price tag, the investor on a
beach towel with a laptop. It suits a light, personal, lifestyle or money-habit point. For
satire or a political point, Tempo is stronger; for a big historical or cultural idea, the
Renaissance collage.

## The prompt

Opening line:

```text
Draw a new picture in the style of the attached reference pictures:
```

The scene, in this order: **who** (skin, hair, sunglasses, lips, clothes in the palette
colours), **the gesture with the object**, **the crop**, **the background colour or
pattern**, then the aspect. The example that made `examples/flat-hat.webp`:

```text
A close-up of a young Indonesian woman with warm brown skin and a sleek black bob, in profile
facing right, wearing huge black cat-eye sunglasses, red lipstick and an enormous red sun hat
whose brim is cut off by the top of the frame. She smiles and holds up a plane ticket between
two fingers next to her face. In the lower right corner, the top of a turquoise suitcase.
Plain lemon yellow background. 4:3.
```

The style block, word for word, at the end:

```text
Style: a retro 1960s-inspired flat illustration like the cover of a summer beach-read novel:
three or four flat colours plus black and white (turquoise, lemon yellow, coral red, hot pink,
orange), no outlines, no gradients, no shading, no texture, crisp vector edges. Elegant
fashion-illustration figures with long necks and slim limbs; the face is reduced to a few
shapes: eyes hidden behind big sunglasses, hair, a hat brim, a book or a hand, or closed as
one curved line, red lips, skin as one flat tone. A witty gesture tells the story. Bold
cropping (a face or a hat cut by the frame), one plain background colour or a simple pattern
of stripes or polka dots, lots of empty space. Not corporate clip art: no round blob heads,
no oversized hands, no tiny generic people. Only the drawing style comes from the attached
pictures: never reuse their people, objects or layout. No title, no author name, no logo,
no watermark, no signature.
```

Then one text rule: `No text, no letters, no numbers.` or, with words quoted in the scene,
`No text except the exact words quoted in the scene.`

## What the tests taught

Tested on 26 November 2026 on the Gemini API with Nano Banana 2.1.

- **Without "retro 1960s" and the face rules it turns into corporate flat art**: generic
  people with full faces, round heads, a bit of Memphis. The words that fixed it: "three or
  four flat colours", "eyes hidden behind big sunglasses", "Not corporate clip art".
- **The close-up profile with a cropped hat is the signature shot** and came out right first
  time. Full figures work too, but give them sunglasses and a gesture.
- **Money comes back as US dollars.** "Plain banknotes" drew green bills with $ signs; add
  `no currency symbols` to the text rule, or quote the exact figure you want.
- **A hijab works well** as a big flat white or coloured shape framing the face.
- **Quoted words come out in bold sans serif, letter-perfect** (a speech bubble, a phone
  screen). With quoted words, use the `No text except ...` rule.
- **Public figures keep full faces** (eyes, brows) even in this style, which is what makes
  them recognisable; give them sunglasses only if the post wants the joke.
- **A crowd or a traffic jam becomes a pattern** of small flat shapes behind the figure. It
  reads well; keep the main figure big.
- A split panel works with "split into two panels by a thick white line", each panel with
  its own background colour named.

## What to reject

- Gradients, soft shadows, outlines, paper texture or a 3D look.
- Full detailed faces with eyes and eyebrows on every figure.
- Busy backgrounds, rooms, more than four colours plus black and white.
- Any book title, author name or cover typography.
