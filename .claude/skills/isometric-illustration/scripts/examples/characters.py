"""Character sheet: every hair style, all four facings, the arm poses, held
things, sitting, and the whole-body poses (run, jump, squat, kneel, floor,
lie, sleep). Render it after any change to the rig and look at it zoomed in,
in both themes. People stand on a slab, 2 units apart, in rows."""
import sys, os; sys.dont_write_bytecode = True; sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from iso import write_pair

ROW1 = [  # facing r (towards the lower right)
    dict(hair_style="short", hair="hair1", top="blue", outfit="shirt", skin="skin2"),
    dict(hair_style="sidepart", hair="hair2", top="navy", outfit="suit", inner="shirt", tie="red", skin="skin1"),
    dict(hair_style="long", hair="hair3", top="coral", outfit="cardigan", inner="paper", skin="skin1", bottom="denim"),
    dict(hair_style="bob", hair="hair4", top="teal", outfit="stripes", inner="paper", skin="skin2", glasses="_face"),
    dict(hair_style="hijab", hair="rose", top="sky", outfit="tee", skin="skin2", bottom="navy"),
    dict(hair_style="bun", hair="hair2", top="gold", outfit="dress", skin="skin3", eyes="happy", blush=True),
    dict(hair_style="ponytail", hair="hair1", top="purple", outfit="hoodie", skin="skin1"),
    dict(hair_style="spiky", hair="hair4", top="coral", outfit="tee", skin="skin1", mouth="grin", shorts=True, bottom="khaki"),
]
ROW2 = [  # facing l (towards the lower left)
    dict(hair_style="curly", hair="hair1", top="maroon", outfit="batik", skin="skin4"),
    dict(hair_style="quiff", hair="hair2", top="olive", outfit="polo", skin="skin3", beard=True),
    dict(hair_style="cap", hat="red", hair="hair1", top="gold", outfit="tee", skin="skin2", bottom="denim"),
    dict(hair_style="hardhat", hat="gold", hair="hair3", top="coral", outfit="hivis", inner="navy", skin="skin3"),
    dict(hair_style="bald", hair="hair5", top="khaki", outfit="jacket", inner="paper", skin="skin2", glasses="_face"),
    dict(hair_style="hijab", hair="teal", top="paper", outfit="tee", skin="skin1", eyes="happy"),
    dict(hair_style="pigtails", hair="hair2", top="navy", outfit="dress", skin="skin1", h=0.78, mouth="grin", blush=True),
    dict(hair_style="long", hair="hair1", top="purple", outfit="apron", inner="paper", skin="skin3"),
]
ROW3 = [  # arm poses and held things
    dict(hair_style="short", hair="hair2", top="teal", outfit="tee", skin="skin1", pose="wave", mouth="grin"),
    dict(hair_style="bob", hair="hair1", top="brand", outfit="shirt", skin="skin2", pose="point"),
    dict(hair_style="hijab", hair="coral", top="navy", outfit="tee", skin="skin3", pose="phone", facing="l", nod=0.2),
    dict(hair_style="cap", hat="brand", hair="hair3", top="gold", outfit="polo", skin="skin4", pose="hold", holding="box"),
    dict(hair_style="long", hair="hair2", top="rose", outfit="tee", skin="skin1", pose="hold", holding="tablet", facing="l"),
    dict(hair_style="short", hair="hair1", top="navy", outfit="suit", inner="shirt", tie="gold", skin="skin2", carry="briefcase", carry_color="wood"),
    dict(hair_style="bun", hair="hair3", top="green", outfit="cardigan", inner="paper", skin="skin1", pose="hips", facing="l"),
    dict(hair_style="spiky", hair="hair1", top="sky", outfit="shirt", skin="skin3", carry="suitcase", carry_color="sky"),
]
ROW4 = [  # walking away (back views)
    dict(facing="ul", hair_style="ponytail", hair="hair2", top="coral", outfit="tee", skin="skin1", walk=0.8),
    dict(facing="ur", hair_style="long", hair="hair1", top="teal", outfit="cardigan", inner="paper", skin="skin2", walk=-0.8),
    dict(facing="ul", hair_style="hijab", hair="purple", top="paper", outfit="tee", skin="skin2", carry="bag", carry_color="gold"),
    dict(facing="ur", hair_style="hardhat", hat="gold", hair="hair1", top="coral", outfit="hivis", inner="navy", skin="skin3"),
]
ROW5 = [  # whole-body poses
    dict(pose="run", walk=0.9, hair_style="ponytail", hair="hair1", top="coral", outfit="tee", shorts=True, bottom="navy", skin="skin2", mouth="open"),
    dict(pose="jump", hair_style="curly", hair="hair2", top="gold", outfit="tee", skin="skin3", mouth="grin", eyes="happy"),
    dict(pose="squat", hair_style="short", hair="hair1", top="olive", outfit="hoodie", skin="skin2"),
    dict(pose="kneel", hair_style="bun", hair="hair3", top="teal", outfit="shirt", skin="skin1", facing="l"),
    dict(pose="floor", hair_style="hijab", hair="sky", top="rose", outfit="tee", skin="skin2", holding="book"),
    dict(pose="hold", arms="think", hair_style="sidepart", hair="hair2", top="maroon", outfit="jacket", inner="paper", skin="skin4", mouth="flat"),
    dict(pose="cheer", hair_style="pigtails", hair="hair4", top="purple", outfit="dress", skin="skin1", mouth="open", eyes="happy"),
    dict(hair_style="buzz", hair="hair1", top="navy", outfit="tee", skin="skin3", pose="hips"),
]


def build(s):
    s.box(-1.0, -1.2, -0.3, 17.6, 18.4, 0.3, "panel", top="floor")
    for i, kw in enumerate(ROW1):
        s.person(i * 2.0, 0.0, **kw)
    for i, kw in enumerate(ROW2):
        s.person(i * 2.0, 3.0, facing="l", **kw)
    for i, kw in enumerate(ROW3):
        kw = dict(kw); f = kw.pop("facing", "r")
        s.person(i * 2.0, 6.0, facing=f, **kw)
    for i, kw in enumerate(ROW4):
        s.person(i * 2.0, 9.0, **kw)
    b = s.bench(8.6, 8.4, length=2.7)                    # a library bench; people sit on its seat anchors
    s.person_at(b.anchor("seat", 2), hair_style="bob", hair="hair4", top="sky", outfit="shirt", skin="skin1", holding="laptop")
    s.person_at(b.anchor("seat", 0), hair_style="short", hair="hair1", top="maroon", outfit="batik", skin="skin3", mouth="grin")
    for i, kw in enumerate(ROW5):
        kw = dict(kw); f = kw.pop("facing", "r")
        s.person(i * 2.2, 12.2, facing=f, **kw)
    # lying down: on the back on a mat, and curled on the side
    s.box(0.0, 15.2, 0.0, 2.9, 1.1, 0.12, "sky")
    s.person(0.1, 15.35, 0.12, facing="r", pose="lie", hair_style="long", hair="hair2", top="paper", outfit="tee", skin="skin1")
    s.box(4.0, 15.0, 0.0, 2.7, 1.5, 0.12, "green")
    s.person(4.1, 15.2, 0.12, facing="r", pose="sleep", hair_style="short", hair="hair1", top="navy", outfit="tee", skin="skin3")


if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else "out"
    print(write_pair(build, "characters", out, unit=40, title="Character sheet"))
