# SVG kit: how to build the picture

How `examples/budget-calculator.svg` is put together. Follow the same structure for a new
picture; it is what keeps outlines clean and shadows inside their shapes.

## The file

```svg
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 728 546">
  <title>What the picture shows, in one sentence</title>
  <defs> shapes, clip paths, the background gradient </defs>
  1. background
  2. body, back to front (torso, neck, ears, face, features, hair)
  3. arms, the object, the hands
  4. foreground props
</svg>
```

- Only a `viewBox`, no `width` or `height`: the render script sizes it.
- No `<image>`, no external fonts, no filters. `<text>` only for numbers or symbols, in
  `Arial, sans-serif`, bold.
- Comment each layer group in one line, so the next edit can find the hands.

## Define, fill, shade, outline

Every shape with a shadow is drawn in four steps. Define its path once in `<defs>` with an
`id`, plus a clip path that uses it:

```svg
<defs>
  <path id="face" d="M312 160 C312 110 336 92 364 92 C392 92 416 110 416 160 C416 204 396 240 364 240 C332 240 312 204 312 160 Z"/>
  <clipPath id="c-face"><use href="#face"/></clipPath>
</defs>

<use href="#face" fill="#F2C9A5"/>                                         <!-- 1. fill -->
<g clip-path="url(#c-face)">                                               <!-- 2. shade -->
  <path d="M300 120 C318 130 326 160 324 190 C326 214 344 236 372 244 L300 250 Z" fill="#DFA883"/>
</g>
<use href="#face" fill="none" stroke="#B5774F" stroke-width="3"/>          <!-- 3. outline -->
<!-- 4. inner lines and features on top -->
```

Why: the shadow shape can be drawn loosely (it may spill past the edge, the clip trims it),
and the outline goes on last, so it always sits cleanly over the edge of the shadow. Shapes
without a shadow (an ear, a button) are a single element with `fill` and `stroke`.

## Drawing shapes

- Use cubic curves (`C`) for anything organic: faces, hair, cloth, hands. Straight lines
  (`L`) only for made things: a desk, a phone, a book cover, a window.
- Sketch the big shapes first, in this order, and render before adding any detail: the
  background, the torso, the head, the object, the arms, the hands. If the big shapes read,
  the picture will.
- Overlap, don't butt: a neck goes under the face and into the collar, an arm starts inside
  the torso at the shoulder. A shared edge between two shapes leaves a hairline gap.
- Keep paths in drawing order. Whatever is in front is drawn later: arms after the torso,
  the object after the arms, the fingers that wrap around it after the object.
- `stroke-linejoin="round"` and `stroke-linecap="round"` on outlines and inner lines.

## Proportions at 728 × 546 (mid-shot)

| Part | Size | Where |
|------|------|-------|
| Head (face oval) | about 104 × 148 | centre near x 364, y 165 |
| Eyes | almond about 22 × 12, 38 apart | a little below the middle of the face |
| Neck | about 44 wide | from under the jaw into the collar |
| Shoulders | about 230 wide | y 290 to 300 |
| Hand | about 50 × 55 | at the object, near chest height |
| Table edge | full width | y 440 to 460 |

Move the person off-centre (x 250 or 480) when a prop or a second panel needs the space.

## Split panel

A diagonal band divides two scenes:

```svg
<clipPath id="left"><path d="M0 0 L330 0 L0 546 Z"/></clipPath>
<rect width="728" height="546" fill="#E8F0D8"/>                          <!-- right scene bg -->
<g clip-path="url(#left)"> <rect width="728" height="546" fill="#E9D3B4"/> ...left scene... </g>
<path d="M330 0 L0 546" stroke="#3B2E26" stroke-width="8"/>
```

## Rendering problems

- **Hairline gaps between shapes:** overlap them by a few pixels.
- **A shadow outside its shape:** the shadow path is not inside the `<g clip-path>`, or the
  clip path id is wrong.
- **An outline under something it should be over:** move the outline `<use>` later.
- **Wrong size or squashed output:** check the `viewBox`.
