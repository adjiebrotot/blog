"""Example: shoppers in a supermarket (a room diorama).
Grid: 14 x 11 cells. Back walls on x=0 and y=0. Shelves run along +x and
face +y (their 'l' face is the visible front)."""
import sys, os; sys.dont_write_bytecode = True; sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from iso import write_pair

GOODS = ["coral", "gold", "teal", "sky", "rose", "green", "amber", "purple", "red"]


def floor(s, W, D):
    for i in range(W):
        for j in range(D):
            s.tile(i, j, 0, 1, 1, "floor" if (i + j) % 2 else "ground", stroke=False)
    with s.group():                                  # grout lines on the lattice
        for i in range(W + 1):
            s.line([(i, 0, 0), (i, D, 0)], "panel", 0.8)
        for j in range(D + 1):
            s.line([(0, j, 0), (W, j, 0)], "panel", 0.8)


def walls(s, W, D, H=3.6):
    s.box(-0.3, -0.3, 0, W + 0.3, 0.3, H, "wall")                  # back-right wall
    s.face_mark(0, 0, 0, "l", [("rect", 0, 0, W, 0.3, "steel"), ("rect", 0, H - 0.9, W, 0.35, "brand")]
                + [("ell", 1.2 + i * 2.4, H - 0.72, 0.1, 0.1, "!paper") for i in range(6)])
    s.box(-0.3, 0, 0, 0.3, D, H, "wall")                           # back-left wall
    s.face_mark(0, 0, 0, "r", [("rect", 0, 0, D, 0.3, "steel"), ("rect", 0, H - 0.9, D, 0.35, "brand")]
                + [("rect", 1.0 + i * 3.2, 1.0, 2.2, 1.4, "glass") for i in range(3)]
                + [("line", [(2.1 + i * 3.2, 1.0), (2.1 + i * 3.2, 2.4)], "steel", 1.2) for i in range(3)])
    # sale poster + clock on the right wall
    s.box(9.0, 0, 1.2, 1.6, 0.06, 1.1, "gold")
    s.face_mark(9.0, 0.06, 1.2, "l", [("ell", 0.5, 0.55, 0.3, 0.3, "coral"), ("rect", 0.95, 0.65, 0.5, 0.1, "navy"),
                                      ("rect", 0.95, 0.42, 0.4, 0.08, "navy"), ("rect", 0.95, 0.22, 0.45, 0.08, "navy")])
    s.box(5.6, 0, 2.3, 0.7, 0.06, 0.7, "paper")
    s.face_mark(5.6, 0.06, 2.3, "l", [("ring", 0.35, 0.35, 0.28, 0.28, "navy", 1.4),
                                      ("line", [(0.35, 0.35), (0.35, 0.56)], "navy", 1.4), ("line", [(0.35, 0.35), (0.5, 0.3)], "navy", 1.4)])


def shelf(s, x, y, length, seed):
    """Gondola shelf: products are separate boxes so they layer by themselves."""
    s.box(x, y, 0, length, 1.0, 0.25, "steel")
    s.box(x, y, 0.25, length, 0.12, 2.5, "panel")
    for t in range(3):
        z = 0.25 + t * 0.78
        s.box(x, y + 0.12, z + 0.7, length, 0.88, 0.06, "metal")
        s.face_mark(x, y + 1.0, z + 0.7, "l", [("rect", i * 0.9 + 0.3, -0.02, 0.28, 0.1, "paper") for i in range(int(length / 0.9))])
        cx, i = x + 0.08, 0
        while cx < x + length - 0.45:
            kind = (seed + i * 3 + t * 5) % 4
            c = GOODS[(seed + i + t * 2) % len(GOODS)]
            if kind == 0:                                           # cereal box
                w, h = 0.42, 0.58
                s.box(cx, y + 0.3, z, w, 0.5, h, c)
                s.face_mark(cx, y + 0.8, z, "l", [("rect", 0.05, 0.3, w - 0.1, 0.12, "paper"), ("ell", w / 2, 0.14, 0.08, 0.06, ("~", c, 0.7))])
            elif kind == 1:                                         # cans
                w = 0.5
                for k in range(2):
                    s.cylinder(cx + 0.12 + k * 0.26, y + 0.62, z, 0.11, 0.34, c, bands=((z + 0.12, z + 0.22, "paper"),), n=16)
            elif kind == 2:                                         # bottles
                w = 0.5
                for k in range(2):
                    bx = cx + 0.12 + k * 0.26
                    s.cylinder(bx, y + 0.62, z, 0.1, 0.42, c, bands=((z + 0.15, z + 0.27, "paper"),), n=16)
                    s.cylinder(bx, y + 0.62, z + 0.42, 0.04, 0.12, "navy", n=10)
            else:                                                   # flat packs
                w, h = 0.46, 0.38
                s.box(cx, y + 0.35, z, w, 0.45, h, c, top=("~", c, 1.1))
                s.face_mark(cx, y + 0.8, z, "l", [("rect", 0, h - 0.1, w, 0.05, "paper")])
            cx += w + 0.06; i += 1
    s.box(x + length / 2 - 0.05, y + 0.4, 2.75, 0.1, 0.1, 0.6, "steel")          # aisle sign
    s.box(x + length / 2 - 0.6, y + 0.45, 3.35, 1.2, 0.08, 0.45, "brand")
    s.face_mark(x + length / 2 - 0.6, y + 0.53, 3.35, "l", [("ell", 0.25, 0.22, 0.13, 0.13, "!paper"),
                                                            ("rect", 0.5, 0.26, 0.55, 0.07, "!paper"), ("rect", 0.5, 0.12, 0.4, 0.07, "!paper")])


def fridge(s, x, y, d):
    s.box(x, y, 0, 1.3, d, 3.0, "white", top="panel")
    s.face_mark(x + 1.3, y, 0, "r", [("rect", 0, 0, d, 0.3, "steel"), ("rect", 0, 2.6, d, 0.4, "brand")])
    doors = []
    for k in range(int(d // 1.2)):
        a = 0.12 + k * 1.2
        doors += [("rect", a, 0.4, 1.05, 2.1, "navy")]
        for r in range(3):                                          # goods behind the glass
            for c in range(3):
                doors.append(("rect", a + 0.1 + c * 0.32, 0.5 + r * 0.7, 0.24, 0.42, GOODS[(k + r * 2 + c) % len(GOODS)]))
        doors += [("rect", a, 0.4, 1.05, 2.1, "glass", 0.45), ("rect", a + 0.9, 1.0, 0.06, 0.8, "!paper")]
    s.face_mark(x + 1.3, y, 0, "r", doors)


def produce(s, x, y):
    for k, (c, fruit) in enumerate((("wood", "coral"), ("wood", "gold"), ("wood", "green"))):
        bx = x + k * 1.0
        s.box(bx, y, 0, 0.9, 1.2, 0.7, c)
        s.face_mark(bx, y + 1.2, 0, "l", [("line", [(0.05, 0.25), (0.85, 0.25)], ("~", "wood", 0.7), 1.0),
                                          ("line", [(0.05, 0.48), (0.85, 0.48)], ("~", "wood", 0.7), 1.0)])
        s.face_mark(bx, y, 0.7, "t", [("ell", 0.2 + (i % 3) * 0.25, 0.2 + (i // 3) * 0.27, 0.11, 0.11, fruit) for i in range(12)])
        s.box(bx + 0.2, y + 1.2, 0.35, 0.5, 0.04, 0.25, "paper")                 # price card


def cart(s, x, y, items=("coral", "gold")):
    with s.group():
        for wx, wy in ((0, 0), (1.1, 0), (0, 0.7), (1.1, 0.7)):
            s.box(x + wx, y + wy, 0, 0.12, 0.12, 0.14, "navy", snap=False)
        s.box(x, y, 0.14, 1.25, 0.82, 0.08, "steel", snap=False)
        s.box(x + 0.25, y + 0.2, 0.75, 0.4, 0.35, 0.3, items[0], snap=False)
        s.box(x + 0.7, y + 0.15, 0.75, 0.35, 0.45, 0.4, items[1], snap=False)
        s.box(x, y, 0.55, 1.25, 0.82, 0.62, "metal", faces="lr", opacity=0.35, snap=False)
        s.face_mark(x, y + 0.82, 0.55, "l", [("line", [(i * 0.25, 0), (i * 0.25, 0.62)], "steel", 1.0) for i in range(6)]
                    + [("line", [(0, 0.3), (1.25, 0.3)], "steel", 1.0)])
        s.face_mark(x + 1.25, y, 0.55, "r", [("line", [(i * 0.2, 0), (i * 0.2, 0.62)], "steel", 1.0) for i in range(5)])
        s.line([(x, y, 1.17), (x + 1.25, y, 1.17), (x + 1.25, y + 0.82, 1.17), (x, y + 0.82, 1.17), (x, y, 1.17)], "steel", 1.6)
        s.line([(x + 0.1, y + 0.8, 0.22), (x + 0.1, y + 0.8, 0.55)], "steel", 1.6)
        s.line([(x - 0.3, y, 1.35), (x - 0.3, y + 0.82, 1.35)], "red", 3.5)


def checkout(s, x, y):
    s.box(x, y, 0, 3.2, 1.0, 1.0, "blue", top="paper")
    s.face_mark(x, y + 1.0, 0, "l", [("rect", 0, 0, 3.2, 0.12, "navy"), ("rect", 0.2, 0.55, 2.8, 0.06, ("~", "blue", 1.2))])
    s.box(x + 1.2, y + 0.15, 1.0, 1.9, 0.7, 0.05, "navy")                          # belt
    s.face_mark(x + 1.2, y + 0.15, 1.05, "t", [("line", [(i * 0.3, 0.05), (i * 0.3, 0.65)], "steel", 0.8) for i in range(1, 7)])
    s.box(x + 0.15, y + 0.2, 1.0, 0.7, 0.6, 0.35, "steel", top="metal")            # till
    s.box(x + 0.25, y + 0.25, 1.35, 0.08, 0.5, 0.4, "navy")                        # screen
    s.face_mark(x + 0.33, y + 0.25, 1.35, "r", [("rect", 0.05, 0.05, 0.4, 0.3, "!sky")])
    s.box(x + 1.4, y + 0.3, 1.05, 0.25, 0.4, 0.12, "gold")                         # items on belt
    s.box(x + 1.9, y + 0.25, 1.05, 0.35, 0.3, 0.25, "teal")


def plant(s, x, y):
    s.box(x, y, 0, 0.6, 0.6, 0.5, "amber")
    s.box(x + 0.05, y + 0.05, 0.5, 0.5, 0.5, 0.55, "leaf")
    s.box(x + 0.15, y + 0.15, 1.05, 0.3, 0.3, 0.3, "leaf")


def build(s):
    W, D = 14, 11
    floor(s, W, D)
    walls(s, W, D)
    shelf(s, 0.6, 0.4, 7.2, 1)
    shelf(s, 0.6, 3.8, 7.2, 4)
    fridge(s, 0.0, 6.2, 4.6)
    produce(s, 9.2, 1.0)
    checkout(s, 9.0, 7.2)
    plant(s, 12.9, 0.4)
    cart(s, 3.4, 8.2)
    # people
    s.person(10.4, 6.6, hair_style="cap", hat="brand", hair="hair1", top="teal", outfit="apron", inner="paper",
             skin="skin4", facing="l", mouth="grin")                               # cashier behind the counter
    s.person(2.4, 8.3, hair_style="long", hair="hair3", top="coral", outfit="cardigan", inner="paper",
             bottom="denim", skin="skin1", pose="hold")                            # pushing the cart
    s.person(7.6, 5.4, hair_style="bob", hair="hair5", top="purple", outfit="stripes", inner="shirt",
             skin="skin2", glasses="_face", carry="basket", carry_color="red", facing="l")
    s.person(10.2, 2.6, hair_style="hijab", hair="rose", top="sky", outfit="tee", bottom="navy",
             skin="skin2", blush=True, carry="bag", carry_color="gold", facing="l")
    s.person(6.2, 9.1, hair_style="pigtails", hair="hair2", top="navy", outfit="dress", skirt="navy",
             bottom="coral", skin="skin1", h=0.78, eyes="happy", mouth="grin", blush=True)
    s.person(12.6, 9.2, hair_style="short", hair="hair2", top="navy", outfit="suit", inner="shirt", tie="red",
             skin="skin3", mouth="open", facing="l", carry="briefcase", carry_color="wood")


if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else "out"
    print(write_pair(build, "supermarket", out, unit=30, title="Shoppers in a supermarket",
                     desc="Isometric supermarket with shelves, a fridge, fruit crates, a checkout and six shoppers."))
