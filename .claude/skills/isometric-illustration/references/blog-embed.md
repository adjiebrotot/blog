# Putting the pair in a post

The blog's theme is a class on `<html>`, not a media query: dark is the default `:root`,
light is `:root.light`, set by the script in `_includes/head.html` before first paint from
the reader's own pick (or their system's). A single SVG with `prefers-color-scheme` would
disagree with a reader who picked a theme by hand, so the art ships as two files and CSS
shows the one that matches.

## Markup

`render.py --publish` prints this with the real width and height:

```html
<figure class="iso-art">
<img class="iso-dark" src="/assets/img/fx-iso-market-dark.svg" alt="Shoppers queue at a money changer while a clerk counts notes" width="1032" height="760" loading="lazy">
<img class="iso-light" src="/assets/img/fx-iso-market-light.svg" alt="Shoppers queue at a money changer while a clerk counts notes" width="1032" height="760" loading="lazy">
<figcaption>Optional caption.</figcaption>
</figure>
```

- **Both images carry the same alt text**, in the post's language. The hidden one is
  `display: none`, which takes it out of the accessibility tree, so a screen reader reads
  exactly one in either theme. (An empty alt on the light copy would leave light-theme
  readers with nothing.)
- Keep `width` and `height` from the SVG so the layout does not jump while it loads.
- `loading="lazy"` also means the hidden copy is never downloaded.
- One pair serves both languages: the art has no words. Each post writes its own alt text
  and caption.

## CSS (already in `assets/css/blog.css`)

```css
.prose .iso-art img { width: 100%; border: 0; border-radius: 0; }
.iso-art .iso-light, .iso-art .iso-still { display: none; }
:root.light .iso-art .iso-dark { display: none; }
:root.light .iso-art .iso-light:not(.iso-still) { display: block; }
@media (prefers-reduced-motion: reduce) {
  .iso-art .iso-anim { display: none !important; }
  :root:not(.light) .iso-art .iso-dark.iso-still, :root.light .iso-art .iso-light.iso-still { display: block; }
}
```

The drawing has no frame or background: its floor is one tonal step off `--bg`, so it sits
in the page.

## The card (post cards, share poster, OG image)

Post cards and `_build/og.mjs` look for an `*-ill-*.webp`, and the share poster for
`share_image:` or the post's first image. An SVG pair cannot feed them (and the dark copy
would land on a light poster). When the isometric scene is the post's lead picture, run
`render.py --card`: it writes `assets/img/<prefix>-ill-<subject>.webp`, the light drawing
on the light page colour at 1456 x 1092 (the size of the other illustrations), and prints
the front matter to add:

```yaml
thumbnail: /assets/img/fx-ill-market.webp
share_image: /assets/img/fx-ill-market.webp
```

Then run `node _build/og.mjs` (it finds the card through `thumbnail:`) and set `image:` to
the OG card as usual. Move the crop with `og_position:` if the subject sits off-centre.

## GIFs

GIF transparency is one bit, so anti-aliased edges would halo: `write_gif` flattens every
frame on the theme's exact `--bg` (`#0F1728` dark, `#F0F4FF` light). Place a GIF only on the
page ground, and give readers who prefer reduced motion the still SVG instead:

```html
<figure class="iso-art">
<img class="iso-dark iso-anim" src="/assets/img/tr-iso-station-dark.gif" alt="..." width="W" height="H" loading="lazy">
<img class="iso-light iso-anim" src="/assets/img/tr-iso-station-light.gif" alt="..." width="W" height="H" loading="lazy">
<img class="iso-dark iso-still" src="/assets/img/tr-iso-station-dark.svg" alt="..." width="W" height="H" loading="lazy">
<img class="iso-light iso-still" src="/assets/img/tr-iso-station-light.svg" alt="..." width="W" height="H" loading="lazy">
</figure>
```

The CSS hides the stills by default and swaps them in, one per theme, under
`prefers-reduced-motion`.

## Budget

- SVG: a busy scene is 100 to 350 KB raw and 20 to 60 KB gzipped (GitHub Pages compresses
  SVG). The example supermarket is about 330 KB raw, 50 KB gzipped. Trim product counts or
  use `Scene(sketch=0)` (no wobble) if a scene is far heavier.
- GIF: under about 1.5 MB. Lower `frames`, the `scale`, or the quantize colours in
  `write_gif` if it is over.
- Card WebP: usually 60 to 150 KB.
