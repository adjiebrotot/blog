"""Animated GIF: a train passes through a station while people walk.
Grid: x -3..19 (track direction), y -4..5. Track at y -3..-0.6, platform
y 0..4.4 (top z 0.6). Two walking lanes on the platform: y 0.85 heading +x
(faces visible) and y 1.95 heading -x (backs visible), pillars at y 2.85,
benches from y 3.3. Seamless loop: every motion is periodic in t in [0, 1)."""
import sys, os, math; sys.dont_write_bytecode = True; sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from iso import write_gif, write_pair

L = 16
X0, X1 = -1.0, L + 1.0          # the visible track window between the portals
PZ = 0.6                        # platform top
CAR_H = 3.0                     # train body height (a person is about 2.5)


def track(s):
    s.tile(-3, -4.2, 0, L + 6, 9.4, "ground", stroke=False)
    s.tile(X0, -3.2, 0, X1 - X0, 2.8, "gravel")
    for i in range(int(X0), int(X1)):
        s.tile(i + 0.3, -2.9, 0.02, 0.3, 2.2, "wood", stroke=False)
    for r in (-2.5, -1.1):
        s.box(X0, r, 0.0, X1 - X0, 0.1, 0.1, "steel", top="metal")
    for mx in (1.5, 8.5, 15.5):                       # overhead line masts on the far side
        s.box(mx, -4.0, 0, 0.2, 0.2, 4.9, "steel")
        s.box(mx, -3.8, 4.6, 0.2, 2.4, 0.12, "steel")
    # contact wire: s.wire splits it so it layers piece by piece
    s.wire((X0, -1.8, 4.45), (8.6, -1.8, 4.45), sag=0.08, mat="wire", width=1.0)
    s.wire((8.6, -1.8, 4.45), (X1, -1.8, 4.45), sag=0.08, mat="wire", width=1.0)


def portals(s):
    s.box(X0 - 1.4, -4.0, 0, 1.4, 3.8, 4.6, "concrete", top="leaf")
    s.face_mark(X0, -4.0, 0, "r", [("poly", [(0.6, 0), (3.4, 0), (3.4, 3.4), (2.9, 3.9), (1.1, 3.9), (0.6, 3.4)], "navy")])
    s.box(X1, -4.0, 0, 1.4, 3.8, 4.6, "concrete", top="leaf")
    s.face_mark(X1, -0.2, 0, "l", [("rect", 0, 4.2, 1.4, 0.4, ("~", "concrete", 0.85))])


def train(s, t):
    """3 cars travelling +x; every piece is clipped to [X0, X1] so the train
    slides out of one portal and into the other."""
    def cbox(x, y, z, w, d, h, mat, **kw):
        a, b = max(x, X0), min(x + w, X1)
        if b - a > 0.01:
            return s.box(a, y, z, b - a, d, h, mat, snap=False, **kw)
        return None

    def cmarks(on, x0, shapes, y, z):
        out = []
        for sh in shapes:
            a0, a1 = max(x0 + sh[1], X0), min(x0 + sh[1] + sh[3], X1)
            if a1 - a0 > 0.01:
                out.append((sh[0], a0 - X0, sh[2], a1 - a0, sh[4], sh[5]))
        if out:
            s.face_mark(X0, y, z, "l", out, on=on)

    tx = -22 + t * 44
    for c in range(3):
        x0 = tx + c * 6.5
        y0, d = -2.75, 1.9
        for bx in (0.6, 4.4):                                        # bogies
            b = cbox(x0 + bx, y0 + 0.2, 0.1, 1.0, d - 0.4, 0.3, "navy")  # sits on the rails (top 0.1)
            if b:
                cmarks(b, x0, [("rect", bx + 0.1, 0.03, 0.25, 0.24, "steel"), ("rect", bx + 0.65, 0.03, 0.25, 0.24, "steel")], y0 + d - 0.2, 0.1)
        body = cbox(x0, y0, 0.4, 6.2, d, CAR_H, "white", top="metal")
        if body:
            sh = [("rect", 0, 0, 6.2, 0.25, "steel"), ("rect", 0, 1.05, 6.2, 0.18, "brand"), ("rect", 0, CAR_H - 0.3, 6.2, 0.07, "gold")]
            for dx in (0.6, 4.6):                                    # doors
                sh += [("rect", dx, 0.05, 1.0, 2.5, "panel"), ("rect", dx + 0.1, 1.45, 0.32, 0.8, "glass"),
                       ("rect", dx + 0.58, 1.45, 0.32, 0.8, "glass"), ("rect", dx + 0.49, 0.05, 0.02, 2.5, "steel")]
            for wx in (1.9, 2.85, 3.6):
                sh += [("rect", wx, 1.45, 0.65, 0.8, "glass")]
            cmarks(body, x0, sh, y0 + d, 0.4)
            for rx in (1.6, 3.8):                                    # roof units
                cbox(x0 + rx, y0 + 0.5, 0.4 + CAR_H, 0.9, 0.9, 0.22, "steel", top="metal")
        if c == 2 and X0 < x0 + 6.2 < X1 - 0.6:                      # lead car nose
            n = s.box(x0 + 6.2, y0 + 0.1, 0.4, 0.5, d - 0.2, CAR_H - 0.1, "brand", snap=False)
            s.face_mark(x0 + 6.7, y0 + 0.1, 0.4, "r", [("rect", 0.2, 1.6, d - 0.6, 0.9, "glass"),
                        ("ell", 0.3, 0.6, 0.12, 0.12, "!light_on"), ("ell", d - 0.5, 0.6, 0.12, 0.12, "!light_on"),
                        ("rect", 0, 1.05, d - 0.2, 0.12, "gold")], on=n)
            s.line([(x0 + 4.0, y0 + 0.95, 3.62), (x0 + 4.6, y0 + 0.95, 4.45), (x0 + 5.2, y0 + 0.95, 3.62)], "steel", 1.6)


def platform(s):
    p = s.box(X0, 0, 0, X1 - X0, 4.4, PZ, "concrete", top="floor")
    s.face_mark(X0, 0, PZ, "t", [("rect", 0, 0.05, X1 - X0, 0.12, "paper"), ("rect", 0, 0.3, X1 - X0, 0.3, "gold")]
                + [("ell", 0.25 + i * 0.5, 0.45, 0.05, 0.05, ("~", "gold", 0.8)) for i in range(int((X1 - X0) * 2))], on=p)
    s.face_mark(X1, 0, 0, "r", [("rect", 0, 0.1, 4.4, 0.08, ("~", "concrete", 0.8))], on=p)
    s.face_mark(X0, 4.4, 0, "l", [("rect", 0, 0.45, X1 - X0, 0.08, "brand")], on=p)


def canopy(s):
    top = 4.9
    for px in (1.0, 6.0, 11.0):
        s.box(px, 2.85, PZ + 0.1, 0.24, 0.24, top - PZ - 0.3, "steel")
        s.box(px - 0.1, 2.75, PZ, 0.44, 0.44, 0.1, "metal")
        s.box(px - 0.03, -0.4, top - 0.2, 0.3, 3.55, 0.2, "steel")   # cantilever beam
    # glass roof: translucent so the train behind it stays readable
    s.box(-0.5, -0.6, top, 13.5, 4.2, 0.12, "sky", top="glass", opacity=0.35)
    s.face_mark(-0.5, -0.6, top + 0.12, "t", [("line", [(i * 1.5, 0), (i * 1.5, 4.2)], "steel", 1.2) for i in range(10)]
                + [("line", [(0, 2.1), (13.5, 2.1)], "steel", 1.2)])
    # departure board + clock hanging from the beams, above head height
    s.line([(5.7, 1.0, top), (5.7, 1.0, 4.15)], "steel", 1.4)
    s.line([(7.3, 1.0, top), (7.3, 1.0, 4.15)], "steel", 1.4)
    b = s.box(5.4, 0.9, 3.6, 2.2, 0.2, 0.55, "navy")
    s.face_mark(5.4, 1.1, 3.6, "l", [("rect", 0.12, 0.33, 0.25, 0.12, "!light_on"), ("rect", 0.45, 0.33, 1.5, 0.12, "!pale"),
                                     ("rect", 0.12, 0.12, 0.25, 0.12, "!light_on"), ("rect", 0.45, 0.12, 1.2, 0.12, "!pale")], on=b)
    s.line([(3.2, 1.0, top), (3.2, 1.0, 4.15)], "steel", 1.4)
    s.cylinder(3.2, 1.0, 3.65, 0.3, 0.5, "paper", n=20)


def props(s):
    s.bench(2.0, 3.3, PZ, length=1.8)
    s.bench(12.0, 3.3, PZ, length=1.8)
    s.cylinder(9.3, 3.75, PZ, 0.28, 0.75, "teal", bands=((PZ + 0.6, PZ + 0.75, "navy"),), n=20)   # bin
    m = s.box(14.8, 3.4, PZ, 0.8, 0.7, 1.9, "brand", top="navy")      # ticket machine
    s.face_mark(15.6, 3.4, PZ, "r", [("rect", 0.12, 1.1, 0.45, 0.45, "!sky"), ("rect", 0.15, 0.65, 0.4, 0.08, "navy"),
                                     ("rect", 0.2, 0.35, 0.3, 0.12, "gold")], on=m)
    s.tree(16.4, 3.4, PZ, s=0.8)


def people(s, t):
    # a woman reading on the bench, a man waiting by the ticket machine
    s.person(2.3, 3.42, PZ + 0.6, facing="l", sit=0.6, hair_style="bun", hair="hair2", top="teal", outfit="cardigan",
             inner="paper", skin="skin2", eyes="happy", blush=True, holding="book")
    s.person(13.95, 3.5, PZ, facing="r", hair_style="sidepart", hair="hair1", top="navy", outfit="suit", inner="shirt",
             tie="gold", skin="skin3", pose="phone")
    walkers = [   # (lane y, facing, phase, look)
        (0.85, "r", 0.0, dict(hair_style="spiky", hair="hair4", top="coral", outfit="shirt", skin="skin1", carry="suitcase", carry_color="sky")),
        (0.85, "r", 0.5, dict(hair_style="cap", hat="red", hair="hair1", top="gold", outfit="tee", bottom="denim", skin="skin2")),
        (1.95, "ul", 0.2, dict(hair_style="long", hair="hair3", top="pale", outfit="suit", inner="shirt", skin="skin3", carry="briefcase", carry_color="navy")),
        (1.95, "ul", 0.7, dict(hair_style="hijab", hair="purple", top="green", outfit="tee", skin="skin1", carry="bag", carry_color="coral")),
    ]
    for k, (y, f, ph0, kw) in enumerate(walkers):
        ph = (t + ph0) % 1
        x = -0.6 + ph * 17 if f == "r" else 16.6 - ph * 17
        s.person(x, y, PZ, facing=f, walk=math.sin(2 * math.pi * (8 * t + k * 0.25)), **kw)


def build(s, t=0.45):
    track(s); portals(s); train(s, t); platform(s); canopy(s); props(s); people(s, t)


if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else "out"
    print(write_pair(lambda s: build(s, 0.45), "train-station-still", out, unit=24, title="Train at a station",
                     desc="Isometric station: a train at the platform, people walking both ways, a woman reading on a bench, a canopy and a departure board."))
    if "--gif" in sys.argv:
        print(write_gif(build, "train-station", out, frames=36, fps=12, unit=24, title="Train passing a station"))
