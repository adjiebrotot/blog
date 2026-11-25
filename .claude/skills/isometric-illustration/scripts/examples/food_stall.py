"""A street food stall: a cart with a striped canopy, a seller holding a plate,
a customer on a stool with his back to us, a man drinking from a cup, a girl,
a lamp post and two trees. Grid: ground x -1..10, y -1..7. The cart stands at
x 3..5.6, y 1.2..2.4; the seller stands at its open end (x 5.85), customers in front.
Run it through render.py like a scene in _illustrations/."""
import sys, os; sys.dont_write_bytecode = True; sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

TITLE = "A street food stall"
DESC = "Isometric street food stall: a seller behind a cart with a striped canopy, customers on stools and standing."
UNIT = 30


def ground(s):
    s.tile(-1, -1, 0, 11, 8, "ground", stroke=False)
    pave = s.tile(-0.5, -0.5, 0, 10, 6.5, "concrete")
    s.face_mark(-0.5, -0.5, 0, "t", [("line", [(i, 0), (i, 6.5)], ("~", "concrete", 0.9), 0.8) for i in range(1, 10)]
                + [("line", [(0, j), (10, j)], ("~", "concrete", 0.9), 0.8) for j in range(1, 7)], on=pave)
    s.tile(-1, 6.0, 0, 11, 1.0, "road")


def cart(s, x=3.0, y=1.2, w=2.6, d=1.2):
    for lx, ly in ((0.1, 0.1), (w - 0.25, 0.1), (0.1, d - 0.25), (w - 0.25, d - 0.25)):
        s.box(x + lx, y + ly, 0, 0.15, 0.15, 0.5, "steel")
    body = s.box(x, y, 0.5, w, d, 1.1, "white", top="paper")
    s.face_mark(x, y + d, 0.5, "l", [("rect", 0, 0, w, 0.15, "coral"), ("rect", 0, 0.95, w, 0.15, "coral"),
                                     ("rect", 0.3, 0.35, 0.9, 0.12, "brand"), ("rect", 0.3, 0.55, 0.6, 0.08, "brand"),
                                     ("ell", 1.95, 0.5, 0.28, 0.28, "gold"), ("ell", 1.95, 0.5, 0.15, 0.15, "coral")], on=body)
    s.face_mark(x + w, y, 0.5, "r", [("rect", 0, 0, d, 0.15, "coral"), ("rect", 0, 0.95, d, 0.15, "coral")], on=body)
    wheel = s.box(x + 0.35, y + d, 0.0, 0.7, 0.06, 0.7, "navy")             # big wheel on the near side
    s.face_mark(x + 0.35, y + d + 0.06, 0, "l", [("ring", 0.35, 0.35, 0.27, 0.27, "steel", 1.6),
                                                 ("line", [(0.35, 0.08), (0.35, 0.62)], "steel", 1.0),
                                                 ("line", [(0.08, 0.35), (0.62, 0.35)], "steel", 1.0)], on=wheel)
    # glass case on the counter with food inside (translucent, like a shop window)
    # (food inside see-through glass: one group, painted in the order written)
    s.box(x + 1.3, y + 0.15, 1.6, 1.15, 0.85, 0.08, "steel")
    with s.group():
        for i, c in enumerate(("gold", "coral", "green")):
            s.box(x + 1.4 + i * 0.35, y + 0.3, 1.68, 0.28, 0.5, 0.12, c, top=("~", c, 1.1))
        s.box(x + 1.3, y + 0.15, 1.68, 1.15, 0.85, 0.55, "glass", top="glass", opacity=0.35)
    # a pot on the counter
    s.cylinder(x + 0.55, y + 0.55, 1.6, 0.3, 0.35, "steel", bands=((1.85, 1.9, "metal"),))
    s.cloud(x + 0.55, y + 0.55, 2.45, 0.3, mat="white", opacity=0.85)
    # canopy on four posts
    for px, py in ((0, 0), (w - 0.1, 0), (0, d - 0.1), (w - 0.1, d - 0.1)):
        s.box(x + px, y + py, 1.6, 0.1, 0.1, 1.6, "wood")
    roof = s.box(x - 0.2, y - 0.2, 3.2, w + 0.4, d + 0.4, 0.12, "coral", top="paper")
    s.face_mark(x - 0.2, y - 0.2, 3.32, "t", [("rect", i * 0.6, 0, 0.3, d + 0.4, "coral") for i in range(5)], on=roof)
    s.face_mark(x - 0.2, y + d + 0.2, 3.2, "l", [("rect", i * 0.6, 0, 0.3, 0.12, "paper") for i in range(5)], on=roof)


def stools(s):
    for sx in (2.8, 4.4):
        s.box(sx, 3.0, 0, 0.5, 0.5, 0.55, "wood", top=("~", "wood", 1.1))


def lamp_and_tree(s):
    s.box(8.2, 0.6, 0, 0.3, 0.3, 0.1, "steel")
    s.box(8.3, 0.7, 0.1, 0.1, 0.1, 3.6, "steel")
    lamp = s.box(8.15, 0.55, 3.7, 0.4, 0.4, 0.3, "navy")
    s.face_mark(8.55, 0.55, 3.7, "r", [("rect", 0.06, 0.04, 0.28, 0.2, "!light_on")], on=lamp)
    s.tree(0.6, 0.6, s=1.1)
    s.tree(8.6, 5.2, kind="pine", s=0.9)


def people(s):
    # the seller stands at the open end of the cart, where the viewer can see her
    # (anyone behind the cart, at lower y, would be hidden by it)
    s.person(5.85, 1.3, facing="l", hair_style="hijab", hair="teal", top="paper", outfit="apron", inner="coral",
             skin="skin2", pose="hold", holding="plate", mouth="grin")
    s.person(3.03, 3.47, 0.55, facing="ur", sit=0.55, hair_style="short", hair="hair1", top="gold", outfit="tee",
             skin="skin3")                                                                       # eating, back to us
    s.person(8.0, 2.6, facing="l", hair_style="sidepart", hair="hair1", top="maroon", outfit="batik", skin="skin3",
             pose="hold", holding="cup", glasses="_face")                                        # drinking
    s.person(5.4, 4.3, facing="l", h=0.7, hair_style="pigtails", hair="hair2", top="sky", outfit="dress",
             skin="skin2", pose="wave", mouth="grin", blush=True)                                # a girl waving


def build(s):
    ground(s); cart(s); stools(s); lamp_and_tree(s); people(s)


if __name__ == "__main__":
    from iso import write_pair
    out = sys.argv[1] if len(sys.argv) > 1 else "out"
    print(write_pair(build, "food-stall", out, unit=UNIT, title=TITLE, desc=DESC))
