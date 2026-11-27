#!/usr/bin/env python3
"""Checks the focus boxes in _data/focus.yml and previews every crop they drive.

    python3 _build/focus.py [--preview DIR]

1. Lists each picture the site crops (a post's `thumbnail:`, `share_image:` and first
   *-ill-*.webp, plus the home card's picture in og.mjs) that has no focus box: give it one.
2. Warns when an entry's `size` is not the file's real size.
3. With --preview DIR, writes one PNG per picture: the picture with its box in red, then the
   crop of every frame shape the site uses (square thumbnail, 16:10 card, 4:3 featured
   card, the social card, the Post and Story posters), computed with the same rule as
   blog.css, blog.js and og.mjs. Look at them: each crop must show the subject whole.
"""
import re
import sys
from pathlib import Path

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parent.parent
IMG = ROOT / 'assets/img'
# Frame shapes, width/height: blog.css (.post-card-thumb), og.mjs (.ill), blog.js (drawSticker).
FRAMES = {'square card': 1, '16:10 card': 1.6, '4:3 featured': 4 / 3, 'social card': 500 / 510,
          'Post poster': 924 / 554, 'Story poster': 888 / 480}


def load_focus():
    out = {}
    pat = re.compile(r'^([\w.-]+):\s*\{\s*box:\s*\[([^\]]+)\],\s*size:\s*\[([^\]]+)\]', re.M)
    for m in pat.finditer((ROOT / '_data/focus.yml').read_text()):
        out[m[1]] = ([float(v) for v in m[2].split(',')], [int(v) for v in m[3].split(',')])
    return out


def cropped_pictures():
    found = {}
    for post in sorted((ROOT).glob('*/_posts/*.md')):
        src = post.read_text()
        fm = src.split('---')[1]
        for key in ('thumbnail', 'share_image'):
            m = re.search(rf'^{key}:\s*"?/assets/img/([^"\s]+)', fm, re.M)
            if m:
                found.setdefault(m[1], post.name)
        m = re.search(r'/assets/img/([\w-]+-ill-[\w-]+\.webp)', src)
        if m:
            found.setdefault(m[1], post.name)
    m = re.search(r"ill: '([\w.-]+)'", (ROOT / '_build/og.mjs').read_text())
    if m:
        found.setdefault(m[1], 'og.mjs (home card)')
    return found


def crop(box, iw, ih, cr):
    """The visible rectangle (x0, y0, x1, y1 in pixels) of a cover crop to ratio cr."""
    ir = iw / ih
    vx, vy = min(1, cr / ir), min(1, ir / cr)

    def at(a, b, v, top=False):
        s = (a + b) / 200 - v / 2
        if top:
            s = min(s, a / 100)  # a box taller than the frame keeps its top (a head)
        return 0.5 if v >= 1 else max(0, min(1, s / (1 - v)))
    sx = at(box[0], box[2], vx) * (1 - vx)
    sy = at(box[1], box[3], vy, True) * (1 - vy)
    return sx * iw, sy * ih, (sx + vx) * iw, (sy + vy) * ih


def preview(name, box, out):
    im = Image.open(IMG / name).convert('RGB')
    iw, ih = im.size
    H = 300
    tiles = []
    full = im.copy()
    d = ImageDraw.Draw(full)
    d.rectangle([box[0] * iw / 100, box[1] * ih / 100, box[2] * iw / 100 - 1, box[3] * ih / 100 - 1],
                outline=(230, 0, 0), width=max(3, iw // 250))
    tiles.append(('picture + box', full.resize((round(H * iw / ih), H))))
    for label, cr in FRAMES.items():
        c = im.crop(tuple(round(v) for v in crop(box, iw, ih, cr)))
        tiles.append((label, c.resize((round(H * cr), H))))
    sheet = Image.new('RGB', (sum(t.width for _, t in tiles) + 16 * (len(tiles) + 1), H + 48), 'white')
    d = ImageDraw.Draw(sheet)
    x = 16
    for label, t in tiles:
        sheet.paste(t, (x, 32))
        d.text((x, 10), label, fill=(0, 0, 0))
        x += t.width + 16
    sheet.save(out / (Path(name).stem + '.png'))


def main():
    focus = load_focus()
    problems = 0
    for name, where in cropped_pictures().items():
        if name not in focus:
            problems += 1
            with Image.open(IMG / name) as im:
                w, h = im.size
            print(f'MISSING  {name} ({where}): add\n  {name}: {{ box: [x0, y0, x1, y1], size: [{w}, {h}] }}')
    for name, (box, size) in focus.items():
        if not (IMG / name).exists():
            print(f'WARN     {name}: no such file in assets/img/')
            continue
        with Image.open(IMG / name) as im:
            if list(im.size) != size:
                problems += 1
                print(f'ERROR    {name}: size is {im.size[0]}x{im.size[1]}, focus.yml says {size[0]}x{size[1]}')
        if not (0 <= box[0] < box[2] <= 100 and 0 <= box[1] < box[3] <= 100):
            problems += 1
            print(f'ERROR    {name}: box {box} must be 0 <= x0 < x1 <= 100 and 0 <= y0 < y1 <= 100')
    if '--preview' in sys.argv:
        out = Path(sys.argv[sys.argv.index('--preview') + 1])
        out.mkdir(parents=True, exist_ok=True)
        for name, (box, _) in focus.items():
            if (IMG / name).exists():
                preview(name, box, out)
        print(f'Previews in {out}/')
    print('OK' if not problems else f'{problems} to fix')
    return 1 if problems else 0


if __name__ == '__main__':
    sys.exit(main())
