"""Character sheet: every hair style, all four facings, the poses, held
things and sitting. Render it after any change to the rig and look at it zoomed in.
Grid: people stand on a slab, 2 units apart, in four rows."""
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
    dict(hair_style="spiky", hair="hair4", top="coral", outfit="tee", skin="skin1", mouth="grin"),
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
ROW4 = [  # walking away (back views) and sitting
    dict(facing="ul", hair_style="ponytail", hair="hair2", top="coral", outfit="tee", skin="skin1", walk=0.8),
    dict(facing="ur", hair_style="long", hair="hair1", top="teal", outfit="cardigan", inner="paper", skin="skin2", walk=-0.8),
    dict(facing="ul", hair_style="hijab", hair="purple", top="paper", outfit="tee", skin="skin2", carry="bag", carry_color="gold"),
    dict(facing="ur", hair_style="hardhat", hat="gold", hair="hair1", top="coral", outfit="hivis", inner="navy", skin="skin3"),
]
ROW3 = [  # poses and held things
    dict(hair_style="short", hair="hair2", top="teal", outfit="tee", skin="skin1", pose="wave", mouth="grin"),
    dict(hair_style="bob", hair="hair1", top="brand", outfit="shirt", skin="skin2", pose="point"),
    dict(hair_style="hijab", hair="coral", top="navy", outfit="tee", skin="skin3", pose="phone", facing="l"),
    dict(hair_style="cap", hat="brand", hair="hair3", top="gold", outfit="polo", skin="skin4", pose="hold", holding="box"),
    dict(hair_style="long", hair="hair2", top="rose", outfit="tee", skin="skin1", pose="hold", holding="tablet", facing="l"),
    dict(hair_style="short", hair="hair1", top="navy", outfit="suit", inner="shirt", tie="gold", skin="skin2", carry="briefcase", carry_color="wood"),
    dict(hair_style="bun", hair="hair3", top="green", outfit="cardigan", inner="paper", skin="skin1", carry="bag", carry_color="coral", facing="l"),
    dict(hair_style="spiky", hair="hair1", top="sky", outfit="shirt", skin="skin3", carry="suitcase", carry_color="sky"),
]


def build(s):
    s.box(-1.0, -1.2, -0.3, 17.6, 12.4, 0.3, "panel", top="floor")
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


if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else "out"
    print(write_pair(build, "characters", out, unit=40, title="Character sheet"))
