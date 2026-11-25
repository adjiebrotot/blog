"""A street food stall, built from library objects: the cart, two stools, a
lamp and two trees are placed, then people go on the objects' anchors (the
seller at the cart's end, a customer on a stool, another at the counter).
Grid: ground x -1..10, y -1..7; the cart runs along x at y 1.2..2.4."""
import sys, os; sys.dont_write_bytecode = True; sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from models import food_cart, stool, street_lamp, tree

TITLE = "A street food stall"
DESC = "Isometric street food stall: a seller beside a cart with a striped canopy, customers on a stool and standing, a girl waving."
UNIT = 30


def ground(s):
    s.tile(-1, -1, 0, 11, 8, "ground", stroke=False)
    pave = s.tile(-0.5, -0.5, 0, 10, 6.5, "concrete")
    s.mark(pave, "top", [("line", [(i, 0), (i, 6.5)], ("~", "concrete", 0.9), 0.8) for i in range(1, 10)]
           + [("line", [(0, j), (10, j)], ("~", "concrete", 0.9), 0.8) for j in range(1, 7)])
    s.tile(-1, 6.0, 0, 11, 1.0, "road")


def build(s):
    ground(s)
    # objects first: the cart's front (its decorated side) turned to +y
    cart = s.place(food_cart, 3.0, 1.2, rot=90, mirror=True)      # mirrored: local y runs along +x
    seat = s.place(stool, 3.2, 3.55, rot=270)                     # turned to face the cart
    s.place(street_lamp, 8.2, 0.6)
    s.place(tree, 0.0, 0.0, size=1.1)
    s.place(tree, 8.1, 4.7, kind="pine", size=0.9)
    # then people on the objects' anchors
    s.person_at(cart.anchor("seller"), hair_style="hijab", hair="teal", top="paper", outfit="apron", inner="coral",
                skin="skin2", pose="hold", holding="plate", mouth="grin")
    s.person_at(seat.anchor("seat"), hair_style="short", hair="hair1", top="gold", outfit="tee", skin="skin3")
    s.person_at(cart.anchor("customer", 1), hair_style="sidepart", hair="hair1", top="maroon", outfit="batik",
                skin="skin3")
    s.person(7.6, 2.6, facing="l", hair_style="bob", hair="hair2", top="sky", outfit="shirt", skin="skin1",
             pose="hold", holding="cup", glasses="_face")
    s.person(5.6, 4.3, facing="l", h=0.7, hair_style="pigtails", hair="hair2", top="coral", outfit="dress",
             skin="skin2", pose="wave", mouth="grin", blush=True)


if __name__ == "__main__":
    from iso import write_pair
    out = sys.argv[1] if len(sys.argv) > 1 else "out"
    print(write_pair(build, "food-stall", out, unit=UNIT, title=TITLE, desc=DESC))
