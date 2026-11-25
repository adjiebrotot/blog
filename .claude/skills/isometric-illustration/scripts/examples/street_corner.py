"""A street corner built only from library objects, the object-first way:
two shop houses, an ATM and a house along the back of a pavement, a food cart, a bench,
a lamp and trees on it, a car and a scooter on the road, and people placed on
the objects' anchors (at the ATM, at the shop door, at the cart, on the bench).

Grid: buildings at y 2.4..5 with their fronts turned to +y (rot=90), the
pavement y 5..7, the road y 7..10, x 0..16."""
import sys, os; sys.dont_write_bytecode = True; sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from models import shopfront, atm, food_cart, bench, street_lamp, tree, car, motorbike, plant, house

TITLE = "A street corner"
DESC = "Isometric street corner: shop houses, an ATM, a food cart and a bench on the pavement, a car and a scooter on the road, people going about their day."
UNIT = 22


def ground(s):
    s.tile(-1, 0, 0, 18, 5.0, "ground", stroke=False)
    pave = s.tile(-1, 5.0, 0, 18, 2.0, "concrete")
    s.mark(pave, "top", [("line", [(i, 0), (i, 2.0)], ("~", "concrete", 0.9), 0.8) for i in range(1, 18)])
    s.box(-1, 6.9, 0, 18, 0.1, 0.12, "concrete", top="paper")                    # kerb
    road = s.tile(-1, 7.0, 0, 18, 3.0, "road")
    s.mark(road, "top", [("rect", 0.5 + i * 2, 1.45, 1.0, 0.1, "!paper") for i in range(9)])


def build(s):
    ground(s)
    # objects: buildings turned to face the street (+y)
    shop1 = s.place(shopfront, 3.2, 2.4, rot=90, awning="coral", sign="brand")
    shop2 = s.place(shopfront, 6.6, 2.4, rot=90, awning="teal", sign="gold", wall="pale")
    cash = s.place(atm, 7.7, 4.3, rot=90)
    cart = s.place(food_cart, 10.2, 4.6, rot=90, mirror=True)
    seat = s.place(bench, 2.8, 5.3, rot=90)
    s.place(plant, 3.25, 5.05)
    s.place(house, 16.0, 2.2, rot=90, roof="sky", lit=False)
    s.place(street_lamp, 9.5, 6.3, rot=90)
    s.place(tree, 14.3, 4.6, size=1.0)
    s.place(tree, -0.6, 5.1, kind="pine", size=0.9)
    s.place(car, 2.0, 7.6, color="sky")
    s.place(motorbike, 9.0, 8.6, color="red")
    # people on the anchors the objects offer
    s.person_at(cash.anchor("user"), hair_style="hijab", hair="purple", top="paper", outfit="tee", skin="skin2", carry="bag", carry_color="gold")
    s.person_at(shop2.anchor("door"), hair_style="cap", hat="brand", hair="hair1", top="gold", outfit="tee", skin="skin3")
    s.person_at(cart.anchor("seller"), hair_style="short", hair="hair1", top="paper", outfit="apron", inner="coral", skin="skin4",
                pose="hold", holding="plate", mouth="grin")
    s.person_at(cart.anchor("customer", 1), hair_style="ponytail", hair="hair2", top="teal", outfit="tee", skin="skin1")
    s.person_at(seat.anchor("seat", 0), hair_style="bun", hair="hair5", top="rose", outfit="cardigan", inner="paper", skin="skin2",
                holding="book", glasses="_face")
    s.person_at(seat.anchor("seat", 1), hair_style="sidepart", hair="hair1", top="maroon", outfit="batik", skin="skin3", mouth="grin")
    s.person(5.0, 5.4, facing="r", hair_style="long", hair="hair1", top="coral", outfit="shirt", skin="skin2", pose="phone")
    s.person(14.8, 6.0, facing="r", hair_style="short", hair="hair2", top="navy", outfit="suit", inner="shirt", tie="red",
             skin="skin1", carry="briefcase", carry_color="wood", walk=0.7)
    del shop1


if __name__ == "__main__":
    from iso import write_pair
    out = sys.argv[1] if len(sys.argv) > 1 else "out"
    print(write_pair(build, "street-corner", out, unit=UNIT, title=TITLE, desc=DESC))
