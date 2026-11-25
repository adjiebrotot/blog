"""A power station, a step-up substation, a transmission line and a town,
built object-first. The plant building is a model made in this file (the way
a post adds its own objects); cooling towers, the chimney, transformers, the
gantry, pylons, houses, trees and the fence come from the library. Wires run
between the anchors the objects offer (bushings, gantry pegs, pylon arms), so
they always meet the hardware.
Grid: x -9..30, y -6..9."""
import sys, os; sys.dont_write_bytecode = True; sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from models import cooling_tower, chimney, transformer, gantry, pylon, house, fence

TITLE = "Power station and transmission line"
DESC = "A power station with cooling towers feeds a substation and a transmission line to a small town."
UNIT = 20


def plant_building(m):
    """Turbine hall with a roof monitor, and a boiler house with vents and a
    pipe bridge towards the chimney. 7 x 7.2 x 5.1; the hall faces +y."""
    hall = m.box(0, 3.8, 0, 7, 3.4, 2.8, "white", top="metal")
    m.mark(hall, "left", [("rect", 0, 0, 7, 0.25, "steel"), ("rect", 0, 2.45, 7, 0.12, "brand")]
           + [("rect", 0.4 + i * 1.05, 1.35, 0.7, 0.75, "glass") for i in range(5)]
           + [("line", [(0.75 + i * 1.05, 1.35), (0.75 + i * 1.05, 2.1)], "steel", 1.0) for i in range(5)]
           + [("rect", 5.6, 0.25, 1.1, 1.5, "steel")]
           + [("line", [(5.6, 0.4 + k * 0.2), (6.7, 0.4 + k * 0.2)], ("~", "steel", 0.7), 0.8) for k in range(7)])
    m.mark(hall, "front", [("rect", 0.4 + i * 1.0, 1.4, 0.6, 0.7, "glass") for i in range(3)] + [("rect", 0, 0, 3.4, 0.25, "steel")])
    m.mark(hall, "back", [("rect", 0.4 + i * 1.0, 1.4, 0.6, 0.7, "glass") for i in range(3)])
    mon = m.box(0.7, 4.4, 2.8, 5.6, 1.6, 0.6, "white", top="panel")
    m.mark(mon, "left", [("rect", 0.2 + i * 0.55, 0.15, 0.4, 0.3, "glass") for i in range(10)])
    m.mark(mon, "right", [("rect", 0.2 + i * 0.55, 0.15, 0.4, 0.3, "glass") for i in range(10)])
    boiler = m.box(0.3, 0, 0, 3.0, 3.0, 4.6, "metal", top="panel")
    m.mark(boiler, "left", [("rect", 0.3, 0.6 + k * 1.2, 2.4, 0.15, ("~", "metal", 0.85)) for k in range(3)])
    m.mark(boiler, "front", [("rect", 0.3 + k * 0.9, 3.4, 0.5, 0.8, "glass") for k in range(3)])
    for vx in (0.9, 2.1):
        m.box(vx, 0.6, 4.6, 0.6, 0.6, 0.5, "steel")
    m.box(3.3, 1.0, 3.2, 1.75, 0.5, 0.5, "steel", top="metal")     # pipe bridge to the stack


def ground(s):
    s.tile(-10, -7, 0, 41, 17, "ground", stroke=False)
    s.tile(-9, -6, 0, 14.5, 12, "concrete")                          # plant yard
    road = s.tile(-9, 6.4, 0, 39, 1.4, "road")
    s.mark(road, "top", [("rect", 0.5 + i * 2, 0.66, 1.0, 0.08, "!paper") for i in range(19)])
    s.tile(6.0, -2.5, 0.02, 6.4, 7.4, "gravel")                      # substation yard


def build(s):
    ground(s)
    # the plant
    s.place(plant_building, -4.5, -5.0)
    s.place(chimney, 0.25, -4.5)
    s.place(cooling_tower, -9.0, -0.2)
    s.place(cooling_tower, -8.2, -5.6)
    for k in range(2):                                               # fuel tanks
        s.cylinder(3.4 + k * 1.4, 4.4, 0, 0.6, 1.4, "panel", bands=((1.1, 1.2, "steel"),))
    # the substation: transformers, a gantry, a fence, a control kiosk
    t1 = s.place(transformer, 6.8, -1.4)
    s.place(transformer, 6.8, 1.6)
    g = s.place(gantry, 10.4, -0.8, span=3.85)
    s.place(fence, 12.4, 4.85, rot=90, length=6.4)                   # along x, mesh facing the road
    k = s.box(10.9, 3.3, 0, 1.4, 1.3, 1.5, "white", top="coral")     # control kiosk, clear of the pylons
    s.mark(k, "left", [("rect", 0.15, 0, 0.5, 1.05, "navy"), ("rect", 0.8, 0.6, 0.45, 0.4, "!light_on")])
    s.mark(k, "front", [("rect", 0.4, 0.6, 0.5, 0.4, "!light_on")])
    # the line: pylons, and wires between the anchors
    towers = [s.place(pylon, x - 0.6, 0.4) for x in (15.0, 20.5, 26.0)]
    for i in range(3):
        s.wire(t1.anchor("bushing", i).p, g.anchor("peg", i).p, sag=0.15, n=8)
        prev = g.anchor("peg", i).p
        for tw in towers:
            p = tw.anchor("phase", i).p
            s.wire(prev, p, sag=0.5 if prev[0] < 11 else 0.95)
            prev = p
    for a, b in zip(towers, towers[1:]):                             # shield wire over the peaks
        s.wire(a.anchor("peak").p, b.anchor("peak").p, sag=0.6, width=0.8)
    # the town
    s.place(house, 28.9, -4.0, rot=90, roof="coral")
    s.place(house, 31.0, 3.0, rot=90, roof="gold")
    s.place(house, 25.4, 3.6, rot=90, roof="sky", lit=False)
    for (tx, ty, kind) in ((24.8, -2.0, "round"), (21.6, -2.6, "pine"), (16.6, 4.6, "round"), (13.4, 5.6, "pine"),
                           (-8.4, 5.0, "round"), (30.2, -1.0, "pine")):
        s.tree(tx, ty, kind=kind, s=0.9)
    # field engineers
    s.person(3.0, 5.2, h=1.15, hair_style="hardhat", hat="gold", hair="hair1", top="coral", outfit="hivis", inner="navy",
             skin="skin2", pose="hold", holding="clipboard")
    s.person(9.0, 5.5, h=1.15, hair_style="hardhat", hat="paper", hair="hair3", top="gold", outfit="hivis", inner="blue",
             skin="skin3", glasses="_face", facing="r", pose="point", mouth="open")
    s.person(18.4, 4.6, h=1.15, hair_style="hijab", hair="brand", top="coral", outfit="hivis", inner="navy",
             skin="skin1", facing="l", carry="briefcase", carry_color="steel")


if __name__ == "__main__":
    from iso import write_pair
    out = sys.argv[1] if len(sys.argv) > 1 else "out"
    print(write_pair(build, "power-grid", out, unit=UNIT, title=TITLE, desc=DESC))
