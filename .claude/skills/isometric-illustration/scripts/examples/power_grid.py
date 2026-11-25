"""Example: a power station, a step-up substation, a transmission line and a town.
Grid: x -9..30, y -6..9. Every pylon part and every wire piece is its own
sortable unit, so wires pass in front of near legs and behind far ones."""
import sys, os; sys.dont_write_bytecode = True; sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from iso import write_pair

ARMS = (-1.0, 0.0, 1.0)
TOWER_H = 6.5


def ground(s):
    s.tile(-10, -7, 0, 41, 17, "ground", stroke=False)
    s.tile(-9, -6, 0, 14.5, 12, "concrete")                          # plant yard
    s.tile(-9, 6.4, 0, 39, 1.4, "road")                              # road
    s.face_mark(-9, 6.4, 0, "t", [("rect", 0.5 + i * 2, 0.66, 1.0, 0.08, "!paper") for i in range(19)])


def plant(s):
    # turbine hall with a roof monitor, windows and a roller door
    s.box(-4.5, -1.2, 0, 7, 3.4, 2.8, "white", top="metal")
    s.face_mark(-4.5, 2.2, 0, "l", [("rect", 0, 0, 7, 0.25, "steel"), ("rect", 0, 2.45, 7, 0.12, "brand")]
                + [("rect", 0.4 + i * 1.05, 1.35, 0.7, 0.75, "glass") for i in range(5)]
                + [("line", [(0.75 + i * 1.05, 1.35), (0.75 + i * 1.05, 2.1)], "steel", 1.0) for i in range(5)]
                + [("rect", 5.6, 0.25, 1.1, 1.5, "steel")]
                + [("line", [(5.6, 0.4 + k * 0.2), (6.7, 0.4 + k * 0.2)], ("~", "steel", 0.7), 0.8) for k in range(7)])
    s.face_mark(2.5, -1.2, 0, "r", [("rect", 0.4 + i * 1.0, 1.4, 0.6, 0.7, "glass") for i in range(3)])
    s.box(-3.8, -0.6, 2.8, 5.6, 1.6, 0.6, "white", top="panel")
    s.face_mark(-3.8, 1.0, 2.8, "l", [("rect", 0.2 + i * 0.55, 0.15, 0.4, 0.3, "glass") for i in range(10)])
    # boiler house, vents, pipe bridge to the chimney
    s.box(-4.2, -5.0, 0, 3.0, 3.0, 4.6, "metal", top="panel")
    s.face_mark(-4.2, -2.0, 0, "l", [("rect", 0.3, 0.6 + k * 1.2, 2.4, 0.15, ("~", "metal", 0.85)) for k in range(3)])
    s.face_mark(-1.2, -5.0, 0, "r", [("rect", 0.3 + k * 0.9, 3.4, 0.5, 0.8, "glass") for k in range(3)])
    for vx in (-3.6, -2.4):
        s.box(vx, -4.4, 4.6, 0.6, 0.6, 0.5, "steel")
    s.box(-1.2, -4.0, 3.2, 1.75, 0.5, 0.5, "steel", top="metal")
    s.cylinder(1.0, -3.75, 0, 0.55, 7.6, "white", bands=((6.2, 6.6, "red"), (7.0, 7.4, "red")))
    s.cylinder(1.0, -3.75, 0, 0.75, 0.4, "concrete")
    # cooling towers with steam
    for (tx, ty) in ((-7.0, 1.8), (-6.2, -3.6)):
        s.tower(tx, ty, 0, 2.0, 1.4, 5.4, "white", bands=((0, 0.35, "concrete"), (4.9, 5.1, "panel")))
    s.cloud(-6.2, -3.6, 6.4, 1.3); s.cloud(-6.6, -4.2, 7.9, 0.95)
    s.cloud(-7.0, 1.8, 6.4, 1.3); s.cloud(-7.5, 1.2, 7.8, 0.9)
    s.cloud(1.0, -3.75, 8.3, 0.55)
    # fuel tanks
    for k in range(2):
        s.cylinder(3.4 + k * 1.4, 4.4, 0, 0.6, 1.4, "panel", bands=((1.1, 1.2, "steel"),))


def substation(s):
    s.tile(6.0, -2.5, 0.02, 6.4, 7.4, "gravel")
    for i, ty in enumerate((-1.4, 1.6)):
        s.box(6.8, ty, 0, 1.8, 1.8, 0.2, "concrete")
        s.box(6.9, ty + 0.1, 0.2, 1.6, 1.6, 1.5, "teal", top=("~", "teal", 1.15))
        s.face_mark(6.9, ty + 1.7, 0.2, "l", [("line", [(0.15 + k * 0.18, 0.15), (0.15 + k * 0.18, 1.3)], ("~", "teal", 0.7), 1.0) for k in range(8)])
        s.face_mark(8.5, ty + 0.1, 0.2, "r", [("rect", 0.3, 0.9, 1.0, 0.35, "paper"), ("rect", 0.4, 1.0, 0.3, 0.15, "gold")])
        s.cylinder(7.1, ty + 0.8, 1.7, 0.18, 0.7, "metal")              # conservator (approx.)
        for k in range(3):                                              # bushings with ribs
            s.cylinder(7.9, ty + 0.4 + k * 0.4, 1.7, 0.07, 0.75, "paper", bands=((2.0, 2.06, "steel"), (2.2, 2.26, "steel")), n=12)
    for gy in (-0.8, 2.8):                                              # line gantry
        s.box(10.4, gy, 0, 0.25, 0.25, 4.0, "steel")
    s.box(10.4, -0.8, 4.0, 0.25, 3.85, 0.25, "steel")
    for k, dy in enumerate(ARMS):
        s.line([(10.52, 1.0 + dy * 1.1, 4.0), (10.52, 1.0 + dy * 1.1, 3.45)], "teal", 3)
        s.wire((7.95, -1.0 + 0.4 * k, 2.45), (10.52, 1.0 + dy * 1.1, 3.45), sag=0.15, n=8)
    # fence: posts + mesh
    for fx in [6.0 + i * 0.8 for i in range(9)]:
        s.box(fx, 4.9, 0, 0.08, 0.08, 1.0, "steel")
    s.box(6.0, 4.88, 0.05, 6.4, 0.02, 0.9, "metal", opacity=0.25, faces="l", snap=False)    # mesh just behind the posts
    s.face_mark(6.0, 4.9, 0.05, "l", [("line", [(i * 0.2, 0), (i * 0.2 + 0.4, 0.9)], "steel", 0.6) for i in range(30)])
    # control kiosk: in the open front corner, not behind a lattice tower
    # (a solid box seen through a pylon reads as sitting inside it)
    k = s.box(10.9, 3.3, 0, 1.4, 1.3, 1.5, "white", top="coral")
    s.face_mark(10.9, 4.6, 0, "l", [("rect", 0.15, 0, 0.5, 1.05, "navy"), ("rect", 0.8, 0.6, 0.45, 0.4, "!light_on")], on=k)
    s.face_mark(12.3, 3.3, 0, "r", [("rect", 0.4, 0.6, 0.5, 0.4, "!light_on")], on=k)


def pylon(s, x, y, h=TOWER_H):
    """Lattice pylon. Legs, bracing, arms and insulators are separate units."""
    b, tp = 0.6, 0.2
    def L(sx, sy, f):
        r = b + (tp - b) * f
        return (x + sx * r, y + sy * r, h * f)
    legs = [(-1, -1), (1, -1), (1, 1), (-1, 1)]
    f0 = 0.25 / h                                          # legs stand on their footings
    for sx, sy in legs:
        s.box(x + sx * b - 0.15, y + sy * b - 0.15, 0, 0.3, 0.3, 0.25, "concrete", snap=False)
        s.line([L(sx, sy, f0), L(sx, sy, 1)], "steel", 2.4)
    base = f0
    for i in range(6):
        f0, f1 = base + (1 - base) * i / 6, base + (1 - base) * (i + 1) / 6
        for a, c in ((legs[3], legs[2]), (legs[1], legs[2]), (legs[0], legs[1]), (legs[0], legs[3])):
            s.line([L(*a, f0), L(*c, f1)], "steel", 1.0)
            s.line([L(*c, f0), L(*a, f1)], "steel", 1.0)
            s.line([L(*a, f1), L(*c, f1)], "steel", 1.0)
    s.box(x - 0.12, y - 1.3, h - 0.7, 0.24, 2.6, 0.2, "steel", snap=False)
    s.box(x - 0.1, y - 0.1, h, 0.2, 0.2, 0.6, "steel", snap=False)
    for dy in ARMS:
        s.line([(x, y + dy, h - 0.7), (x, y + dy, h - 1.3)], "teal", 3.2)
    s.shadow(x - b, y - b, 2 * b, 2 * b)


def house(s, x, y, c, lit=True):
    s.box(x, y, 0, 1.8, 1.6, 1.3, "white", top="panel")
    s.poly([(x - 0.1, y - 0.1, 1.3), (x + 1.9, y - 0.1, 1.3), (x + 1.9, y + 0.8, 2.1), (x - 0.1, y + 0.8, 2.1)], c)
    s.poly([(x - 0.1, y + 0.8, 2.1), (x + 1.9, y + 0.8, 2.1), (x + 1.9, y + 1.7, 1.3), (x - 0.1, y + 1.7, 1.3)], c)
    s.poly([(x + 1.8, y, 1.3), (x + 1.8, y + 1.6, 1.3), (x + 1.8, y + 0.8, 2.0)], "white")
    s.face_mark(x, y + 1.6, 0, "l", [("rect", 0.25, 0.55, 0.45, 0.45, "!light_on" if lit else "glass"),
                                      ("line", [(0.475, 0.55), (0.475, 1.0)], "steel", 0.8),
                                      ("rect", 1.05, 0, 0.45, 0.9, "navy"), ("ell", 1.4, 0.45, 0.03, 0.03, "gold")])
    s.face_mark(x + 1.8, y, 0, "r", [("rect", 0.55, 0.55, 0.5, 0.4, "!light_on" if lit else "glass")])


def build(s):
    ground(s); plant(s); substation(s)
    towers = [(15.0, 1.0), (20.5, 1.0), (26.0, 1.0)]
    for tx, ty in towers:
        pylon(s, tx, ty)
    for k, dy in enumerate(ARMS):
        prev = (10.52, 1.0 + dy * 1.1, 3.45)
        for tx, ty in towers:
            pt = (tx, ty + dy, TOWER_H - 1.3)
            s.wire(prev, pt, sag=0.5 if prev[0] < 11 else 0.95)
            prev = pt
    for (tx, ty) in zip(towers, towers[1:]):                           # shield wire on the peaks
        s.wire((tx[0], tx[1], TOWER_H + 0.6), (ty[0], ty[1], TOWER_H + 0.6), sag=0.6, width=0.8)
    # town
    house(s, 26.5, -4.0, "coral"); house(s, 28.6, 3.0, "gold"); house(s, 23.0, 3.6, "sky", lit=False)
    for (tx, ty, k) in ((24.8, -2.0, "round"), (21.6, -2.6, "pine"), (16.6, 4.6, "round"), (13.4, 5.2, "pine"),
                        (-8.4, 5.0, "round"), (30.2, -1.0, "pine")):
        s.tree(tx, ty, kind=k, s=0.9)
    # people: field engineers
    s.person(3.0, 5.2, h=1.15, hair_style="hardhat", hat="gold", hair="hair1", top="coral", outfit="hivis", inner="navy",
             skin="skin2", pose="hold", holding="clipboard")
    s.person(9.0, 5.5, h=1.15, hair_style="hardhat", hat="paper", hair="hair3", top="gold", outfit="hivis", inner="blue",
             skin="skin3", glasses="_face", facing="r", pose="point", mouth="open")
    s.person(18.4, 4.6, h=1.15, hair_style="hijab", hair="brand", top="coral", outfit="hivis", inner="navy",
             skin="skin1", facing="l", carry="briefcase", carry_color="steel")


if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else "out"
    print(write_pair(build, "power-grid", out, unit=20, title="Power station and transmission line",
                     desc="A power station with cooling towers feeds a substation and a transmission line to a small town."))
