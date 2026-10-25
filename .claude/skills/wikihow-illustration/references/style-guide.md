# Style guide: the wikiHow look

What makes a picture read as "wikiHow style", taken from the step pictures Adjie shared
(a man reading a book in a chair, a woman holding up two shirts, a painter at an easel with
a split-panel palette close-up, a man painting a beach scene from behind).

## The feel

- **Friendly and plain.** Ordinary people in ordinary clothes, in a calm good mood. A small
  closed smile or a concentrating look. Never a grin, never a pose for the camera.
- **Realistic proportions, simplified.** Adult heads are about one seventh of the body, not
  chibi or big-eyed. Detail is left out, not exaggerated.
- **One action.** Everything in the frame serves the verb of the step. The object in the
  hands is drawn clearly and a little larger than life if that helps it read.

## Line

- Every shape has an outline in a **darker shade of its own fill**, never pure black: skin
  gets a warm brown, an orange shirt a burnt orange, a teal book a deep teal.
- One even weight: **3 px at 728 wide** for outlines, 2 to 2.5 px for inner lines (fingers,
  ear folds, a shirt seam, a nose). Round caps and joins.
- Inner lines are few: a nose is one stroke, a hand gets one or two finger lines, a fold
  gets one curve.

## Colour

- **Fills are clean and fairly saturated** for the person and the main object: orange,
  teal, green, red, pink, mid blue shirts; warm skin; brown, ginger, black or blond hair.
- **Background is pale and cool or soft:** light blue-grey, pale green, pale sky. It may be
  a gentle vertical gradient or carry one or two big soft blobs or a hint of a wall, window
  or horizon. It is always the least saturated part of the picture.
- **Every colour comes in three tones:** base fill, one shadow tone (about 10 to 15 percent
  darker and a little warmer for skin, a little cooler for cloth) and the outline (about
  35 to 45 percent darker). A highlight tone is optional and used sparingly (hair shine,
  glass, a pig's back).
- To tie a picture to the blog, take one prop colour from the blog's palette
  (`assets/css/blog.css`): blue `#3A71C8` / `#5A91E8`, green `#1F7F63` / `#4A9E87`,
  coral `#E66A6A`, gold `#B45309`. Don't tint the whole picture blue.

Ready palettes (fill / shadow / outline):

| Part | Fill | Shadow | Outline |
|------|------|--------|---------|
| Light skin | `#F2C9A5` | `#DFA883` | `#B5774F` |
| Medium skin | `#D9A178` | `#C3875E` | `#8E5634` |
| Brown skin | `#A86F48` | `#8E5A38` | `#5E3520` |
| Dark skin | `#7A4B2E` | `#643B23` | `#3E2312` |
| Brown hair | `#7A4A2A` | `#5E3720` | `#4A2A17` |
| Black hair | `#3A2E2A` | `#2A201C` | `#17110E` |
| Ginger hair | `#E0823C` | `#C46A28` | `#8F4A1A` |
| Orange cloth | `#F08A3C` | `#D46F25` | `#A9531A` |
| Teal cloth | `#4DBFA8` | `#36A28C` | `#23705F` |
| Blue cloth | `#5A91E8` | `#4479CF` | `#2C5799` |
| Green cloth | `#8CC66B` | `#72AD52` | `#4E7E36` |
| Red cloth | `#E26A62` | `#C9524B` | `#93352F` |
| Wood | `#E6B57E` | `#D29E64` | `#A8733E` |
| Paper | `#FFFFFF` | `#E8EDF5` | `#9AA9BF` |
| Grey device | `#4C5B76` | `#3A4760` | `#283247` |

## Shading

- **Cel shading, one step.** Each shape gets one shadow area with a hard edge, on the side
  away from the light. Pick the light direction once per picture (upper right is a good
  default) and keep it everywhere.
- Where shadows go: the far side of the face and under the jaw onto the neck, under the
  hair line, the side of the torso and inside of the arms, under the chin of the shirt
  collar, the lower part of hands, the bottom of objects.
- No gradients on the person, no drop shadows, no glow, no texture. A soft gradient is
  allowed only in the background.

## Faces

- Almond eyes, fairly small: a white almond, a brown or dark iris circle, a dark pupil, one
  tiny white catch-light, and a **heavier upper lid line** in dark brown. No lower lashes.
- Eyebrows are one thick soft stroke in the hair's shadow colour.
- The nose is one stroke down and a small hook for the nostril, in the skin outline colour.
- The mouth is one curve, darker than the lips would be; a short lighter curve under it can
  suggest the lower lip. Teeth only for an open, laughing mouth.
- Ears sit level with the eyes and nose; one inner curve each.
- Looking down at the object (eyes half closed, lid line low) is often truer to the step
  than looking at the reader.

## Hands

- The hardest part, so keep them simple: a palm shape with the fingers drawn as one mass and
  separated by one or two lines, plus a separate thumb.
- A hand is about as long as the face from chin to eyebrow.
- Hands hold things the way people do: a book by its edges with the thumbs on the pages, a
  phone in the palm with the thumb on the screen, a hanger by its hook.
- When a hand does not read after a couple of tries, hide part of it behind the object.

## Composition

- **Canvas 4:3**, 728 × 546 (the size wikiHow uses), rendered at twice that.
- **Mid-shot** by default: the head in the upper third, the hands and object at the centre,
  the body cut by the frame or by a table edge at the bottom.
- **Close-up** for a detail step: hands and object fill the frame, maybe a sleeve.
- **Split panel** for a comparison or a before-and-after: a diagonal band (a thick dark line)
  from one corner to the other, a different background colour on each side.
- **Back view** (over the shoulder, from behind) when the thing being looked at matters more
  than the face, like the painter at the beach.
- Leave breathing room around the person; nothing important within 20 px of the edge.
- Props sit in the foreground and may overlap the body (a desk edge, a plant, a mug).

## What to avoid

- Pure black outlines, thick comic outlines, or no outlines at all.
- Gradients, gloss or glow on people and objects; 3D or photo-real rendering.
- Busy backgrounds, patterned wallpaper, many props.
- Big anime eyes, exaggerated cartoon proportions, emoji faces.
- Words in the picture (see the brief in `SKILL.md`).
- The wikiHow logo, watermark or caption bar, and any scene copied from a real wikiHow
  article.
