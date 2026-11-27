#!/usr/bin/env python3
"""Render an isometric scene file for the blog, check it, and publish it.

  python3 .claude/skills/isometric-illustration/scripts/render.py _illustrations/<name>.py \\
      --out <scratch dir> [--publish] [--card] [--gif] [--force]

The scene file lives in _illustrations/ (Jekyll does not publish folders that start with _)
and is named <post prefix>-iso-<subject>.py. It defines:
  build(s)  or  build(s, t)   the drawing; t runs over [0, 1) when the scene is animated
  TITLE, DESC                 the SVG's <title> and <desc> (the post's alt text is separate)
  UNIT = 26                   pixels per grid unit (optional, default 26)
  FRAMES = 36                 frames for --gif (optional; only for build(s, t))

Always writes to --out: <name>-dark.svg and <name>-light.svg, a preview PNG of each on its
page background, <name>-pair.png (both themes side by side), <name>-plan.png (a top-down map
of every placed object, person and anchor on the grid, for arranging) and
<name>-gridcheck.png (the lattice over the art), and prints the layering report. Then:
  --publish  copies the two SVGs to assets/img/ and prints the <figure> to paste in the post.
             Refused while parts pass through each other (fix them, or --force).
  --card     writes assets/img/<name with -iso- as -ill->.webp: the light drawing on the page
             background at 1456x1092, for `thumbnail:`, `share_image:` and the OG card.
  --gif      also writes <name>-dark.gif and <name>-light.gif (published with --publish).
Needs cairosvg and Pillow (pip install cairosvg pillow).
"""
import argparse, importlib.util, inspect, io, re, shutil, sys
from pathlib import Path

sys.dont_write_bytecode = True             # no __pycache__ in the skill or _illustrations/

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]                     # scripts -> skill -> skills -> .claude -> repo
sys.path.insert(0, str(HERE))
import iso  # noqa: E402


def load(path):
    spec = importlib.util.spec_from_file_location("scene_" + re.sub(r"\W", "_", path.stem), path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    if not hasattr(mod, "build"):
        sys.exit("%s defines no build(s)" % path)
    return mod


def size_of(svg_path):
    head = svg_path.read_text()[:400]
    m = re.search(r'width="(\d+)" height="(\d+)"', head)
    return (int(m.group(1)), int(m.group(2))) if m else (None, None)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("scene")
    ap.add_argument("--out", required=True)
    ap.add_argument("--publish", action="store_true")
    ap.add_argument("--card", action="store_true")
    ap.add_argument("--gif", action="store_true")
    ap.add_argument("--force", action="store_true")
    a = ap.parse_args()

    scene = Path(a.scene).resolve()
    name = scene.stem
    if "-iso-" not in name:
        print("note: name it <post prefix>-iso-<subject>.py, like the other pictures (fx-iso-market.py)")
    mod = load(scene)
    unit = getattr(mod, "UNIT", 26)
    animated = len(inspect.signature(mod.build).parameters) > 1
    still = (lambda s: mod.build(s, getattr(mod, "STILL_T", 0.0))) if animated else mod.build
    out = Path(a.out); out.mkdir(parents=True, exist_ok=True)

    iso.write_pair(still, name, str(out), title=getattr(mod, "TITLE", name), desc=getattr(mod, "DESC", ""), unit=unit)
    rep = dict(iso.LAST_REPORT)
    from PIL import Image
    ims = [Image.open(out / ("%s-%s-preview.png" % (name, t))).convert("RGB") for t in ("dark", "light")]
    pair = Image.new("RGB", (ims[0].width * 2, ims[0].height))
    pair.paste(ims[0], (0, 0)); pair.paste(ims[1], (ims[0].width, 0))
    pair.save(out / ("%s-pair.png" % name))
    print("look at:", out / ("%s-pair.png" % name), "| plan:", out / ("%s-plan.png" % name),
          "| grid:", out / ("%s-gridcheck.png" % name))

    gifs = []
    if a.gif:
        if not animated:
            sys.exit("--gif needs build(s, t)")
        gifs = iso.write_gif(mod.build, name, str(out), frames=getattr(mod, "FRAMES", 36), fps=getattr(mod, "FPS", 12),
                             title=getattr(mod, "TITLE", name), unit=unit)
        print("gifs:", *gifs)

    img = ROOT / "assets" / "img"
    if a.publish:
        if rep.get("interpenetrating") and not a.force:
            sys.exit("not published: %d pairs of parts pass through each other (listed above). Fix them, or --force."
                     % len(rep["interpenetrating"]))
        for t in ("dark", "light"):
            shutil.copy(out / ("%s-%s.svg" % (name, t)), img / ("%s-%s.svg" % (name, t)))
        for g in gifs:
            shutil.copy(g, img / Path(g).name)
        w, h = size_of(img / ("%s-dark.svg" % name))
        print("\npublished assets/img/%s-dark.svg and -light.svg (%d x %d). Paste in the post, alt text in the post's language:\n" % (name, w, h))
        print('<figure class="iso-art">\n'
              '<img class="iso-dark" src="/assets/img/%s-dark.svg" alt="WHAT THE SCENE SHOWS" width="%d" height="%d" loading="lazy">\n'
              '<img class="iso-light" src="/assets/img/%s-light.svg" alt="WHAT THE SCENE SHOWS" width="%d" height="%d" loading="lazy">\n'
              '<figcaption>Optional caption</figcaption>\n</figure>' % (name, w, h, name, w, h))

    if a.card:
        import cairosvg
        bg = iso.PALETTES["light"]["_bg"]
        svg = (out / ("%s-light.svg" % name)).read_bytes()
        W, H = 1456, 1092
        png = cairosvg.svg2png(bytestring=svg, background_color=bg, output_width=W * 2)
        art = Image.open(io.BytesIO(png)).convert("RGB")
        k = min(W * 0.92 / art.width, H * 0.92 / art.height)
        art = art.resize((max(1, round(art.width * k)), max(1, round(art.height * k))), Image.LANCZOS)
        card = Image.new("RGB", (W, H), bg)
        card.paste(art, ((W - art.width) // 2, (H - art.height) // 2))
        cname = name.replace("-iso-", "-ill-") if "-iso-" in name else name + "-ill"
        card.save(img / (cname + ".webp"), "WEBP", quality=88, method=6)
        kb = (img / (cname + ".webp")).stat().st_size // 1024
        print("\ncard: assets/img/%s.webp (%d KB). For the post card, share poster and OG card, add to the front matter:\n"
              "  thumbnail: /assets/img/%s.webp\n  share_image: /assets/img/%s.webp" % (cname, kb, cname, cname))
        print("\nMandatory next: the card's focus box in _data/focus.yml, the subject every crop keeps whole\n"
              "(.claude/skills/wikihow-illustration/references/focus-box.md):\n"
              "  %-34s{ box: [x0, y0, x1, y1], size: [%d, %d] }   # the subject\n"
              "then: python3 _build/focus.py --preview <scratchpad>/focus, python3 _build/focus.py (OK),\n"
              "and node _build/og.mjs" % (cname + ".webp:", W, H))


if __name__ == "__main__":
    main()
