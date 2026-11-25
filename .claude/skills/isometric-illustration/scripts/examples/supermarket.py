"""Shoppers in a supermarket, built object-first: the room (floor and two back
walls) is drawn in the scene; shelves, the fridge, crates, the checkout
counter, a trolley and a plant come from the library and are placed and
turned; the cashier, a customer and the trolley pusher stand on the
objects' anchors. Grid: 14 x 11 cells, back walls on x=0 and y=0."""
import sys, os; sys.dont_write_bytecode = True; sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from models import shelf, fridge, crate, counter, trolley, plant

TITLE = "Shoppers in a supermarket"
DESC = "Isometric supermarket with shelves, a fridge, fruit crates, a checkout and six shoppers."
UNIT = 30


def room(s, W, D, H=3.6):
    for i in range(W):
        for j in range(D):
            s.tile(i, j, 0, 1, 1, "floor" if (i + j) % 2 else "ground", stroke=False)
    with s.group():                                                # grout lines on the lattice
        for i in range(W + 1):
            s.line([(i, 0, 0), (i, D, 0)], "panel", 0.8)
        for j in range(D + 1):
            s.line([(0, j, 0), (W, j, 0)], "panel", 0.8)
    back = s.box(-0.3, -0.3, 0, W + 0.3, 0.3, H, "wall")           # back-right wall
    s.mark(back, "left", [("rect", 0.3, 0, W, 0.3, "steel"), ("rect", 0.3, H - 0.9, W, 0.35, "brand")]
           + [("ell", 1.5 + i * 2.4, H - 0.72, 0.1, 0.1, "!paper") for i in range(6)])
    side = s.box(-0.3, 0, 0, 0.3, D, H, "wall")                    # back-left wall
    s.mark(side, "front", [("rect", 0, 0, D, 0.3, "steel"), ("rect", 0, H - 0.9, D, 0.35, "brand")]
           + [("rect", 0.6 + i * 3.2, 1.0, 2.2, 1.4, "glass") for i in range(3)]
           + [("line", [(1.7 + i * 3.2, 1.0), (1.7 + i * 3.2, 2.4)], "steel", 1.2) for i in range(3)])
    poster = s.box(9.0, 0, 1.2, 1.6, 0.06, 1.1, "gold")            # sale poster and a clock on the wall
    s.mark(poster, "left", [("ell", 0.5, 0.55, 0.3, 0.3, "coral"), ("rect", 0.95, 0.65, 0.5, 0.1, "navy"),
                            ("rect", 0.95, 0.42, 0.4, 0.08, "navy"), ("rect", 0.95, 0.22, 0.45, 0.08, "navy")])
    clock = s.box(5.6, 0, 2.3, 0.7, 0.06, 0.7, "paper")
    s.mark(clock, "left", [("ring", 0.35, 0.35, 0.28, 0.28, "navy", 1.4),
                           ("line", [(0.35, 0.35), (0.35, 0.56)], "navy", 1.4), ("line", [(0.35, 0.35), (0.5, 0.3)], "navy", 1.4)])


def build(s):
    room(s, 14, 11)
    # objects, turned so their fronts face the shoppers
    s.place(shelf, 7.8, 0.3, rot=90, length=7.2, seed=1)                   # against the back wall, goods to +y
    s.place(shelf, 7.8, 3.3, rot=90, length=7.2, seed=4, sides=2)          # island, goods both ways
    s.place(fridge, 0.0, 6.2, width=4.6)                                   # doors to +x
    for k, fruit in enumerate(("coral", "gold", "green")):
        s.place(crate, 10.4 + k * 1.3, 1.0, rot=90, fruit=fruit)
    till = s.place(counter, 12.2, 7.4, rot=90, length=3.2)                 # customers on the +y side
    cart = s.place(trolley, 3.4, 8.2)
    s.place(plant, 13.1, 0.4)
    # people on the anchors
    s.person_at(till.anchor("staff"), hair_style="cap", hat="brand", hair="hair1", top="teal", outfit="apron",
                inner="paper", skin="skin4", mouth="grin")
    s.person_at(till.anchor("customer", 0), hair_style="short", hair="hair2", top="navy", outfit="suit", inner="shirt",
                tie="red", skin="skin3", carry="briefcase", carry_color="wood")
    s.person_at(cart.anchor("push"), hair_style="long", hair="hair3", top="coral", outfit="cardigan", inner="paper",
                bottom="denim", skin="skin1", pose="hold")
    s.person(6.0, 5.8, facing="r", hair_style="bob", hair="hair5", top="purple", outfit="stripes", inner="shirt",
             skin="skin2", glasses="_face", carry="basket", carry_color="red")
    s.person(9.6, 2.4, facing="l", hair_style="hijab", hair="rose", top="sky", outfit="tee", bottom="navy",
             skin="skin2", blush=True, carry="bag", carry_color="gold")
    s.person(6.6, 9.0, facing="r", h=0.72, hair_style="pigtails", hair="hair2", top="navy", outfit="dress",
             skin="skin1", eyes="happy", mouth="grin", blush=True)


if __name__ == "__main__":
    from iso import write_pair
    out = sys.argv[1] if len(sys.argv) > 1 else "out"
    print(write_pair(build, "supermarket", out, unit=UNIT, title=TITLE, desc=DESC))
