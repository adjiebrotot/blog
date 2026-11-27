#!/usr/bin/env python3
"""Enforces the focus boxes in _data/focus.yml and previews every crop they drive.

    python3 _build/focus.py                       # check; exit 1 on MISSING or ERROR
    python3 _build/focus.py --new <picture>       # print the line to add for a new picture
    python3 _build/focus.py --preview DIR         # check, and draw every crop to look at

The rule: .claude/skills/wikihow-illustration/references/focus-box.md.

1. MISSING: every illustration (*-ill-*.webp in assets/img/) and every picture a post sets as
   `thumbnail:` or `share_image:`, or og.mjs uses for the home card, needs a focus box.
2. ERROR: a wrong `size`, a box outside the picture, a box of 90% or more on both sides (the
   centre crop again), a side under 10% (a sliver), or a line without a `# subject` comment.
   REVIEW: a box wider or taller than the square thumbnail can show; it will be centred.
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
    """{file: (box, size, subject or '')}, and the lines that do not parse."""
    out, bad = {}, []
    pat = re.compile(r'^([\w.-]+):\s*\{\s*box:\s*\[([^\]]+)\],\s*size:\s*\[([^\]]+)\]\s*\}\s*(?:#\s*(.*\S))?\s*$')
    for line in (ROOT / '_data/focus.yml').read_text().splitlines():
        if not line.strip() or line.lstrip().startswith('#'):
            continue
        m = pat.match(line)
        if not m:
            bad.append(line)
            continue
        out[m[1]] = ([float(v) for v in m[2].split(',')], [int(v) for v in m[3].split(',')], m[4] or '')
    return out, bad


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
    for f in sorted(IMG.glob('*-ill-*.webp')):
        found.setdefault(f.name, 'an illustration')
    return found


def new_line(arg):
    name = Path(arg).name
    with Image.open(IMG / name) as im:
        w, h = im.size
    print(f'{name + ":":<34}{{ box: [x0, y0, x1, y1], size: [{w}, {h}] }}   # the subject')
    print(f'Add it to _data/focus.yml, fill in the box (percent) and the subject; the square card'
          f' shows {min(100, round(100 * h / w))}% of the width and {min(100, round(100 * w / h))}% of the height.')


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
    if '--new' in sys.argv:
        new_line(sys.argv[sys.argv.index('--new') + 1])
        return 0
    focus, bad = load_focus()
    problems = 0
    for line in bad:
        problems += 1
        print(f'ERROR    cannot read: {line}\n         write it as  <file>: {{ box: [x0, y0, x1, y1], size: [w, h] }}  # the subject')
    for name, where in cropped_pictures().items():
        if name not in focus and (IMG / name).exists():
            problems += 1
            with Image.open(IMG / name) as im:
                w, h = im.size
            print(f'MISSING  {name} ({where}): add\n  {name}: {{ box: [x0, y0, x1, y1], size: [{w}, {h}] }}   # the subject')
    for name, (box, size, subject) in focus.items():
        if not (IMG / name).exists():
            print(f'WARN     {name}: no such file in assets/img/')
            continue
        with Image.open(IMG / name) as im:
            iw, ih = im.size
        if [iw, ih] != size:
            problems += 1
            print(f'ERROR    {name}: size is {iw}x{ih}, focus.yml says {size[0]}x{size[1]}')
        bw, bh = box[2] - box[0], box[3] - box[1]
        if not (0 <= box[0] < box[2] <= 100 and 0 <= box[1] < box[3] <= 100):
            problems += 1
            print(f'ERROR    {name}: box {box} must be 0 <= x0 < x1 <= 100 and 0 <= y0 < y1 <= 100')
        elif bw >= 90 and bh >= 90:
            problems += 1
            print(f'ERROR    {name}: the box is the whole picture, which crops at the centre again. Box the subject.')
        elif bw < 10 or bh < 10:
            problems += 1
            print(f'ERROR    {name}: a box of {bw:g}% x {bh:g}% is a sliver. Box the whole subject.')
        else:
            sq_w, sq_h = min(100, 100 * ih / iw), min(100, 100 * iw / ih)
            if bw > sq_w + 1 or bh > sq_h + 1:
                print(f'REVIEW   {name}: the square card shows {sq_w:.0f}% x {sq_h:.0f}%, the box is {bw:g}% x {bh:g}%:'
                      f' it will be centred and cut. Fine only if the cut parts do not carry the point.')
        if not subject:
            problems += 1
            print(f'ERROR    {name}: name the subject the box keeps, as a comment: `# the panicked engineer`')
    if '--preview' in sys.argv:
        out = Path(sys.argv[sys.argv.index('--preview') + 1])
        out.mkdir(parents=True, exist_ok=True)
        for name, (box, _, _) in focus.items():
            if (IMG / name).exists():
                preview(name, box, out)
        print(f'Previews in {out}/')
    print('OK' if not problems else f'{problems} to fix (rule: .claude/skills/wikihow-illustration/references/focus-box.md)')
    return 1 if problems else 0


if __name__ == '__main__':
    sys.exit(main())
