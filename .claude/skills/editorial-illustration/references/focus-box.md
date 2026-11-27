# The focus box: marking what a crop must keep

Every illustration on this blog is shown cropped somewhere: a square thumbnail on the home,
category and landing pages, a 4:3 or 16:10 featured card, the 500x510 social card
(`_build/og.mjs`) and the wide Instagram posters (`blog.js`). None of these frames has the
picture's own shape. Each one moves its crop to keep the picture's **focus box** whole, so
the box decides what a reader sees in every one of them. A picture without a box is cut in
the centre, which on a split or multi-panel picture shows the seam and nothing else.

**Mandatory for every illustration made by `editorial-illustration` (all six styles) and
`isometric-illustration`** (each `*-ill-*.webp`, the isometric `--card` included), and
for any other picture set as a post's `thumbnail:` or `share_image:`. Mark it when the
picture is saved, not later: any illustration can become a post's lead picture.
`python3 _build/focus.py` fails until every one has a valid box.

## How to mark it

1. **Get the line.** `python3 _build/focus.py --new assets/img/<name>.webp` prints it with
   the real size. Add it to `_data/focus.yml` (alphabetical order).
2. **Name the subject first**, in the line's comment: what a reader must see for the picture
   to make its point. A whole person with their face and gesture, the thing they hold or point
   at when it carries the point (the receipt, the rate board), a speech bubble whose words are
   the joke. Write it as a noun phrase: `# the panicked engineer`.
3. **Draw the box around that subject, and only that.** Look at the picture with a percent
   grid (the `--preview` sheet's first tile shows the box in red). Top: the highest part of
   the subject, hat, raised hand or bubble included. Bottom: the lowest part that matters
   (a seated person's lap, not the chair legs; the picture's bottom edge when the body runs
   off it). Sides: the subject's outermost edge, including a held object or a pointing hand.
4. **Make it fit the square.** The square thumbnail is the tightest frame: it shows only
   H/W of the width (75% of a 4:3 picture, 56% of a 16:9 one). Keep the box that narrow
   when you can. When the subject cannot fit, choose the part that carries the point (the
   face and the gesture, the bubble and the speaker's face) rather than a box the square
   must cut anyway. The checker reports such a box as REVIEW.
5. **Preview and look.** `python3 _build/focus.py --preview <scratch dir>` draws the picture
   with its box and every crop shape. Each crop must show the subject whole and still make
   sense on its own. If one does not, move the box, not the frame.

## What never to box (the checker rejects some of these)

- **The whole picture**, or nearly (both sides 90% or more): that is the centre crop again.
  ERROR.
- **The seam of a split or multi-panel picture.** Pick one side: the person or panel the post
  is about. Two neighbouring panels are fine when together they fit the square (the borrower
  and the saver, 66% of a 4:3 picture).
- **A half person**: a box that cuts a face, a head or a hand that tells the story. Box the
  whole figure, or the face and gesture together.
- **Empty background, decoration or a blurred crowd** as the subject.
- **A sliver**: a box under 10% on either side is a typo or a detail no thumbnail can show.
  ERROR.
- **A box without a named subject.** The comment is how the next reader checks the box. ERROR.

`og_position:` in a post's front matter still overrides the social card's crop alone. Use it
only when the social card needs something the box cannot give; the box is the default.
