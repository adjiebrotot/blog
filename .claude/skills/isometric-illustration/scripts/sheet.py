#!/usr/bin/env python3
"""Model sheet: one object from all four sides, in both themes, to check its
craft before it goes into a scene; or the whole library as a catalogue.

  python3 .claude/skills/isometric-illustration/scripts/sheet.py bench --out <dir> [--kw length=2.4] [--unit 48]
  python3 .claude/skills/isometric-illustration/scripts/sheet.py _illustrations/x.py:my_cart --out <dir>
  python3 .claude/skills/isometric-illustration/scripts/sheet.py --catalog --out <dir>

A bare name comes from models.py; path.py:name loads a model from a scene
file. Writes <name>-sheet.png (rot 0, 90, 180, 270 left to right; dark on
top, light below) and prints the parts that pass through each other.
"""
import argparse, ast, importlib.util, io, sys
from pathlib import Path

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import iso  # noqa: E402
import models  # noqa: E402


def load(spec):
    if ":" in spec:
        path, name = spec.rsplit(":", 1)
        sp = importlib.util.spec_from_file_location("scene_mod", path)
        mod = importlib.util.module_from_spec(sp)
        sp.loader.exec_module(mod)
        return getattr(mod, name)
    return getattr(models, spec)


def render(build, unit, scale=1.0):
    import cairosvg
    from PIL import Image
    ims = []
    for theme in ("dark", "light"):
        sc = iso.Scene(unit=unit)
        build(sc)
        png = cairosvg.svg2png(bytestring=sc.svg(theme).encode(), background_color=iso.PALETTES[theme]["_bg"], scale=scale)
        ims.append(Image.open(io.BytesIO(png)).convert("RGB"))
    out = Image.new("RGB", (max(i.width for i in ims), sum(i.height for i in ims)))
    out.paste(ims[0], (0, 0)); out.paste(ims[1], (0, ims[0].height))
    return out, sc


def footprint(model, kw):
    """The model's bounding box when placed at the origin."""
    sc = iso.Scene(unit=10)
    inst = sc.place(model, **kw)
    return inst.bb


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("model", nargs="?")
    ap.add_argument("--out", required=True)
    ap.add_argument("--kw", action="append", default=[], help="option=value, repeatable")
    ap.add_argument("--unit", type=int, default=44)
    ap.add_argument("--catalog", action="store_true")
    a = ap.parse_args()
    out = Path(a.out); out.mkdir(parents=True, exist_ok=True)
    kw = {k: ast.literal_eval(v) for k, v in (x.split("=", 1) for x in a.kw)}

    if a.catalog:
        from PIL import Image, ImageDraw
        tiles, bad_all = [], []
        for f in models.MODELS:
            bb = footprint(f, {})
            w, d, h = bb[1] - bb[0], bb[3] - bb[2], bb[5] - bb[4]
            u = max(10, min(90, 220 / ((w + d) * 0.866 + 0.6), 240 / (h + (w + d) * 0.5 + 0.6)))
            img, sc = render(lambda s, f=f: s.place(f), u, scale=1.0)
            bad_all += sc.check()
            tiles.append((f.__name__, img))
        cols, cw, ch = 6, 260, 300
        sheet = Image.new("RGB", (cols * cw, ((len(tiles) + cols - 1) // cols) * ch * 2), "#FFFFFF")
        d = ImageDraw.Draw(sheet)
        for i, (nm, img) in enumerate(tiles):
            half = img.height // 2
            for t, (y0, y1) in enumerate(((0, half), (half, img.height))):
                part = img.crop((0, y0, img.width, y1))
                k = min((cw - 16) / part.width, (ch - 40) / part.height, 1.0)
                part = part.resize((max(1, int(part.width * k)), max(1, int(part.height * k))))
                cx, cy = (i % cols) * cw, (i // cols) * ch * 2 + t * ch
                bg = iso.PALETTES["dark" if t == 0 else "light"]["_bg"]
                d.rectangle([cx + 4, cy + 4, cx + cw - 4, cy + ch - 4], fill=bg)
                sheet.paste(part, (cx + (cw - part.width) // 2, cy + 8 + (ch - 40 - part.height) // 2))
                d.text((cx + 10, cy + ch - 26), nm, fill="#EAF1FF" if t == 0 else "#14203A")
        path = out / "catalog-sheet.png"
        sheet.save(path)
        print("%s: %d models, %d pairs passing through each other" % (path, len(tiles), len(bad_all)))
        for x, y in bad_all[:20]:
            print("  passes through:", x, "|", y)
        return

    model = load(a.model)

    def build(sc):
        bb = footprint(model, kw)
        span = max(bb[1] - bb[0], bb[3] - bb[2]) + 0.8
        for i, rot in enumerate((0, 90, 180, 270)):
            # line the four turned copies up along x by their bounding boxes
            probe = iso.Scene(unit=10).place(model, 0, 0, 0, rot=rot, **kw).bb
            # (x - y) runs straight across the screen, so step along +x and -y
            sc.place(model, i * span - probe[0], -i * span - probe[2], 0, rot=rot, **kw)
    img, sc = render(build, a.unit)
    name = a.model.split(":")[-1]
    path = out / ("%s-sheet.png" % name)
    img.save(path)
    bad = sc.check()
    sc._order()
    print("%s: %d units, %d cycles broken, %d pairs passing through each other" % (path, sc.stats["units"], sc.stats["cycles"], len(bad)))
    for x, y in bad[:20]:
        print("  passes through:", x, "|", y)


if __name__ == "__main__":
    main()
