"""
models.py - the object library: each object is built once, in its own space,
with its details on every side, and then placed in scenes with s.place().

Conventions for every model here (and for new ones):
  * Signature model(m, **options). Draw on `m` exactly as on a scene.
  * Origin at the footprint's back corner, (0, 0, 0) on the floor. The front
    faces +x: with rot=0 the viewer sees the front and the left side (+y);
    rot=90 turns the front to +y, 180 to -x (back in view), 270 to -y.
  * Parts only touch, never pass through each other (fuse with m.group()
    only for contents inside see-through boxes).
  * Borders follow the form, not the construction: parts that make one soft
    or continuous thing (a crown of leaves, a cushion, a draped cloth) go
    inside `with m.outline():` so only their outer silhouette is inked.
  * Details go on every face that can be turned into view: m.mark(part,
    face, shapes) with face 'front', 'back', 'left', 'right' or 'top'.
  * Spots for people and cables are anchors: m.anchor(name, x, y, z,
    facing, seat=...). Scenes use s.person_at(inst.anchor("seat")).
The docstring of each model gives its footprint (x by y by height) and anchors.
"""
import math

GOODS = ["coral", "gold", "teal", "sky", "rose", "green", "amber", "purple", "red"]


def around(m, it, fn, faces=("front", "left", "back", "right")):
    """Mark several vertical faces of a part: fn(width, height, face) -> shapes."""
    x, y, z, w, d, h = it.local
    for f in faces:
        m.mark(it, f, fn(d if f in ("front", "back") else w, h, f))


def wheel(m, cx, cz, r, y0, y1, tire="navy", hub="metal", spokes=False):
    """A round wheel: an octagonal prism on an axle along y from y0 to y1,
    centred at (cx, cz). Only the faces turned to the viewer are drawn, so
    it stays right however the object is rotated."""
    ang = [math.pi / 8 + i * math.pi / 4 for i in range(8)]
    ring = [(cx + r * math.cos(a), cz + r * math.sin(a)) for a in ang]
    mid = (cx, (y0 + y1) / 2, cz)
    for y in (y0, y1):
        m.poly([(x, y, z) for x, z in ring], tire, inside=mid, snap=False)
    for (xa, za), (xb, zb) in zip(ring, ring[1:] + ring[:1]):
        m.poly([(xa, y0, za), (xb, y0, zb), (xb, y1, zb), (xa, y1, za)], ("~", tire, 0.9), inside=mid, snap=False)
    rh = r * (0.5 if not spokes else 0.82)
    hubring = [(cx + rh * math.cos(a), cz + rh * math.sin(a)) for a in ang]
    for y, dy in ((y0, -0.004), (y1, 0.004)):
        m.poly([(x, y + dy, z) for x, z in hubring], hub, inside=mid, snap=False)
        if spokes:
            for a in ang[::2]:
                m.line([(cx - rh * math.cos(a), y + dy * 2, cz - rh * math.sin(a)), (cx + rh * math.cos(a), y + dy * 2, cz + rh * math.sin(a))], "steel", 1.0)


def wheel_part(m, r=0.36, width=0.12, tire="navy", hub="metal", spokes=False):
    """wheel() as a placeable part: axle along y from 0 to width, touching the
    floor, centred on x=0. Place it with rot=270 for an axle along x."""
    wheel(m, 0, r, r, 0, width, tire, hub, spokes)


def _rng(seed):
    state = [seed * 9301 + 49297]

    def r(n):
        state[0] = (state[0] * 9301 + 49297) % 233280
        return state[0] * n // 233280
    return r


# ── furniture ────────────────────────────────────────────────────────────
def bench(m, length=1.8, seat=0.6, mat="wood", leg="steel"):
    """Slatted park bench. 0.6 x length x seat+0.6. Faces +x.
    Anchors: 'seat' (one per 0.9 of length, facing +x, seat=<height>)."""
    S, L = seat, length
    for e in (0.12, L - 0.22):
        m.box(0.0, e, 0, 0.1, 0.1, S + 0.6, leg)                  # back post, up into the backrest
        m.box(0.5, e, 0, 0.1, 0.1, S - 0.08, leg)                 # front post
        m.box(0.1, e + 0.02, 0.12, 0.4, 0.06, 0.06, leg)          # stretcher
    for x0, x1 in ((0.1, 0.26), (0.27, 0.43), (0.44, 0.6)):       # seat slats with gaps
        sl = m.box(x0, 0, S - 0.08, x1 - x0, L, 0.08, mat)
        m.mark(sl, "front", [("ell", 0.08, 0.04, 0.015, 0.015, ("~", mat, 0.7)), ("ell", L - 0.08, 0.04, 0.015, 0.015, ("~", mat, 0.7))])
    for z0 in (S + 0.1, S + 0.34):                                # backrest slats
        b = m.box(0.1, 0, z0, 0.06, L, 0.16, mat)
        m.mark(b, "front", [("line", [(0.05, 0.08), (L - 0.05, 0.08)], ("~", mat, 0.8), 0.8)])
        m.mark(b, "back", [("line", [(0.05, 0.08), (L - 0.05, 0.08)], ("~", mat, 0.8), 0.8)])
    n = max(1, round((L - 0.1) / 0.9))
    for i in range(n):
        m.anchor("seat", 0.34, L * (i + 0.5) / n, S, "+x", seat=S)


def chair(m, seat=0.6, mat="wood", cushion=None):
    """Chair. 0.6 x 0.6 x seat+0.62. Faces +x. Anchor: 'seat'."""
    S = seat
    for y0 in (0.0, 0.52):
        m.box(0, y0, 0, 0.08, 0.08, S + 0.62, mat)                # back legs, up into the back
        m.box(0.52, y0, 0, 0.08, 0.08, S - 0.08, mat)             # front legs
    st = m.box(0.08, 0, S - 0.08, 0.52, 0.6, 0.08, mat)
    m.mark(st, "front", [("line", [(0.03, 0.04), (0.57, 0.04)], ("~", mat, 0.8), 0.8)])
    if cushion:
        st = m.box(0.1, 0.04, S, 0.46, 0.52, 0.06, cushion)
    back = m.box(0.0, 0.08, S + 0.18, 0.06, 0.44, 0.36, mat)
    around(m, back, lambda w, h, f: [("rect", 0.06, 0.08, w - 0.12, h - 0.16, ("~", mat, 0.88))] if f in ("front", "back") else [])
    m.anchor("seat", 0.26 if not cushion else 0.27, 0.3, S + (0.06 if cushion else 0), "+x", seat=S + (0.06 if cushion else 0))


def stool(m, seat=0.55, mat="wood"):
    """Square stool. 0.45 x 0.45 x seat. Anchor: 'seat' (facing +x)."""
    for x0, y0 in ((0.02, 0.02), (0.35, 0.02), (0.02, 0.35), (0.35, 0.35)):
        m.box(x0, y0, 0, 0.08, 0.08, seat - 0.06, mat)
    m.box(0.1, 0.1, 0.15, 0.25, 0.25, 0.04, ("~", mat, 0.9))       # foot rail board, between the legs
    t = m.box(0, 0, seat - 0.06, 0.45, 0.45, 0.06, mat, top=("~", mat, 1.1))
    m.mark(t, "top", [("ring", 0.225, 0.225, 0.12, 0.12, ("~", mat, 0.85), 0.8)])
    m.anchor("seat", 0.14, 0.225, seat, "+x", seat=seat)


def table(m, length=1.4, depth=0.9, height=1.1, mat="wood"):
    """Table. depth x length x height (length along y). Anchor: 'top'
    (centre of the tabletop) for things on it."""
    H, L, D = height, length, depth
    for x0, y0 in ((0.04, 0.04), (D - 0.14, 0.04), (0.04, L - 0.14), (D - 0.14, L - 0.14)):
        m.box(x0, y0, 0, 0.1, 0.1, H - 0.08, mat)
    for x0, y0, w, d in ((0.06, 0.14, 0.04, L - 0.28), (D - 0.1, 0.14, 0.04, L - 0.28),
                         (0.14, 0.06, D - 0.28, 0.04), (0.14, L - 0.1, D - 0.28, 0.04)):
        m.box(x0, y0, H - 0.24, w, d, 0.16, ("~", mat, 0.92))     # apron boards
    t = m.box(0, 0, H - 0.08, D, L, 0.08, mat, top=("~", mat, 1.08))
    m.mark(t, "top", [("line", [(0.05, 0.1 + i * 0.27), (D - 0.05, 0.1 + i * 0.27)], ("~", mat, 0.9), 0.7)
                      for i in range(int((L - 0.1) / 0.27))])
    m.anchor("top", D / 2, L / 2, H, "+x")


def laptop(m, color="steel"):
    """Open laptop. 0.34 x 0.48 x 0.3. The user sits at -x facing +x; the lid
    shows its back (with a logo) to the front."""
    base = m.box(0, 0, 0, 0.32, 0.48, 0.03, color, top=("~", color, 1.05))
    m.mark(base, "top", [("rect", 0.05, 0.05, 0.16, 0.38, ("~", color, 0.8)), ("rect", 0.23, 0.17, 0.06, 0.14, ("~", color, 0.85))])
    lid = m.box(0.32, 0, 0, 0.03, 0.48, 0.3, color)
    m.mark(lid, "front", [("ell", 0.24, 0.17, 0.03, 0.03, "!paper")])
    m.mark(lid, "back", [("rect", 0.03, 0.04, 0.42, 0.23, "!screen"), ("rect", 0.06, 0.18, 0.2, 0.03, "!paper"),
                         ("rect", 0.06, 0.12, 0.28, 0.03, "!paper")])


def desk(m, length=1.6, depth=0.8, height=1.1, mat="wood", panel="white"):
    """Office desk, the user at -x facing +x (the viewer). depth x length x
    height. Drawer pedestal at the +y end (drawers on the user's side),
    modesty panel to the front. Anchor: 'top', 'knee' (where a chair goes:
    its back corner)."""
    H, L, D = height, length, depth
    m.box(0.02, 0.02, 0, D - 0.04, 0.06, H - 0.06, panel)           # side panel
    ped = m.box(0.02, L - 0.5, 0, D - 0.04, 0.48, H - 0.06, panel)  # drawer pedestal
    m.mark(ped, "back", [("rect", 0.04, 0.06 + i * 0.32, 0.4, 0.28, ("~", panel, 0.93)) for i in range(3)]
           + [("rect", 0.16, 0.24 + i * 0.32, 0.16, 0.03, "steel") for i in range(3)])
    m.mark(ped, "front", [("line", [(0.04, 0.12), (0.44, 0.12)], ("~", panel, 0.85), 0.8)])
    mp = m.box(D - 0.06, 0.08, 0.35, 0.04, L - 0.58, H - 0.41, panel)  # modesty panel
    m.mark(mp, "front", [("rect", 0.06, 0.06, L - 0.7, H - 0.53, ("~", panel, 0.95))])
    t = m.box(0, 0, H - 0.06, D, L, 0.06, mat, top=("~", mat, 1.06))
    m.mark(t, "top", [("line", [(0.04, 0.12 + i * 0.3), (D - 0.04, 0.12 + i * 0.3)], ("~", mat, 0.92), 0.7)
                      for i in range(int(L / 0.3))])
    m.anchor("top", D / 2, L / 2, H, "+x")
    m.anchor("knee", -0.66, (L - 0.5) / 2 - 0.3, 0, "+x")


def desk_set(m, length=1.6, mat="wood", chair_mat="navy"):
    """A desk with a chair, an open laptop, a lamp, a mug and papers. The
    user sits at -x facing +x. About 1.5 x length. Anchor: 'seat'."""
    desk(m, length=length, mat=mat)
    k = m.inst.anchors["knee"][0]
    m.place(chair, -0.66, (length - 0.5) / 2 - 0.3, 0, mat=chair_mat, cushion="sky")
    m.place(laptop, 0.2, (length - 0.5) / 2 - 0.24, 1.1)
    lamp = m.box(0.5, length - 0.32, 1.1, 0.18, 0.18, 0.04, "steel")
    m.box(0.57, length - 0.25, 1.14, 0.04, 0.04, 0.42, "steel")
    head = m.box(0.42, length - 0.3, 1.56, 0.3, 0.14, 0.1, "gold")
    m.mark(head, "front", [("rect", 0.02, 0.0, 0.1, 0.03, "!light_on")])
    del k, lamp
    m.cylinder(0.62, length - 0.7, 1.1, 0.06, 0.13, "coral", bands=((1.16, 1.19, "paper"),), n=12)
    p = m.box(0.15, length - 0.74, 1.1, 0.3, 0.22, 0.02, "paper")
    m.mark(p, "top", [("line", [(0.05, 0.04 + i * 0.04), (0.25, 0.04 + i * 0.04)], "steel", 0.6) for i in range(4)])


# ── shops ────────────────────────────────────────────────────────────────
def counter(m, length=2.4, height=1.3, color="blue", top="paper", register=True):
    """Shop counter along y. 0.8 x length x height. Customers at +x, staff
    at -x. Anchors: 'staff' (facing +x), 'customer' (facing -x)."""
    H, L = height, length
    body = m.box(0, 0, 0, 0.8, L, H - 0.06, color)
    m.mark(body, "front", [("rect", 0, 0, L, 0.12, "navy"), ("rect", 0.15, H - 0.5, L - 0.3, 0.06, ("~", color, 1.25)),
                           ("ell", L - 0.4, H * 0.45, 0.16, 0.16, "gold"), ("ell", L - 0.4, H * 0.45, 0.08, 0.08, color)])
    m.mark(body, "back", [("rect", 0.1 + i * (L - 0.2) / 3, 0.2, (L - 0.2) / 3 - 0.06, 0.4, ("~", color, 0.75)) for i in range(3)]
           + [("rect", 0.1, 0.72, L - 0.2, 0.04, ("~", color, 0.75))])
    for f in ("left", "right"):
        m.mark(body, f, [("rect", 0, 0, 0.8, 0.12, "navy"), ("rect", 0.1, H - 0.5, 0.6, 0.06, ("~", color, 1.25))])
    t = m.box(-0.04, -0.04, H - 0.06, 0.88, L + 0.08, 0.06, top)
    if register:
        r = m.box(0.1, 0.25, H, 0.45, 0.5, 0.2, "steel", top="metal")
        m.mark(r, "top", [("rect", 0.08 + i % 3 * 0.1, 0.08 + i // 3 * 0.1, 0.06, 0.06, "panel") for i in range(9)])
        m.mark(r, "front", [("rect", 0.06, 0.05, 0.38, 0.06, "navy")])
        sc = m.box(0.12, 0.35, H + 0.2, 0.05, 0.3, 0.26, "navy")
        m.mark(sc, "back", [("rect", 0.03, 0.03, 0.24, 0.2, "!screen")])
        term = m.box(0.45, 0.9, H, 0.14, 0.1, 0.18, "navy")
        m.mark(term, "front", [("rect", 0.02, 0.1, 0.06, 0.05, "!sky")])
    del t
    m.anchor("staff", -0.26, L * 0.3, 0, "+x")
    for i in (0.3, 0.75):
        m.anchor("customer", 1.1, L * i, 0, "-x")


def shelf(m, length=3.6, tiers=3, height=2.6, seed=1, sides=1):
    """Gondola shelf of goods along y, goods facing +x. 1.0 deep per side
    (2.0 with sides=2: goods both ways, back to back) x length x height."""
    if sides == 2:
        m.place(_shelf_side, 1.0, 0, length=length, tiers=tiers, height=height, seed=seed)
        m.place(_shelf_side, 1.0, length, rot=180, length=length, tiers=tiers, height=height, seed=seed + 7)
    else:
        _shelf_side(m, length, tiers, height, seed)


def _shelf_side(m, length=3.6, tiers=3, height=2.6, seed=1):
    L, r = length, _rng(seed)
    base = m.box(0, 0, 0, 1.0, L, 0.25, "steel")
    m.mark(base, "front", [("rect", 0.1, 0.06, L - 0.2, 0.04, ("~", "steel", 1.3))])
    back = m.box(0, 0, 0.25, 0.06, L, height - 0.25, "panel")
    m.mark(back, "back", [("line", [(i * 0.6, 0.05), (i * 0.6, height - 0.35)], ("~", "panel", 0.85), 0.8) for i in range(1, int(L / 0.6) + 1)])
    step = (height - 0.35) / tiers
    for t in range(tiers):
        z = 0.25 + t * step
        if t > 0:
            b = m.box(0.06, 0, z - 0.06, 0.94, L, 0.06, "metal")
            m.mark(b, "front", [("rect", 0.3 + i * 0.9, -0.01, 0.26, 0.07, "paper") for i in range(int(L / 0.9))])
        y, i = 0.08, 0
        while y < L - 0.45:
            kind = (seed + i * 3 + t * 5 + r(3)) % 4
            c = GOODS[(seed + i + t * 2 + r(4)) % len(GOODS)]
            if kind == 0:                                          # cereal box
                w, h = 0.42, min(0.6, step - 0.14)
                bx = m.box(0.3, y, z, 0.5, w, h, c)
                m.mark(bx, "front", [("rect", 0.05, h * 0.55, w - 0.1, 0.12, "paper"), ("ell", w / 2, h * 0.25, 0.08, 0.06, ("~", c, 0.7))])
            elif kind == 1:                                        # cans
                w = 0.5
                for k in range(2):
                    m.cylinder(0.62, y + 0.12 + k * 0.26, z, 0.11, 0.34, c, bands=((z + 0.12, z + 0.22, "paper"),), n=16)
            elif kind == 2:                                        # bottles
                w = 0.5
                for k in range(2):
                    m.cylinder(0.62, y + 0.12 + k * 0.26, z, 0.1, 0.42, c, bands=((z + 0.15, z + 0.27, "paper"),), n=16)
                    m.cylinder(0.62, y + 0.12 + k * 0.26, z + 0.42, 0.04, 0.12, "navy", n=10)
            else:                                                  # flat packs
                w, h = 0.46, 0.38
                bx = m.box(0.35, y, z, 0.45, w, h, c, top=("~", c, 1.1))
                m.mark(bx, "front", [("rect", 0, h - 0.1, w, 0.05, "paper")])
            y += w + 0.06; i += 1


def fridge(m, width=2.4, height=3.0, depth=1.2):
    """Drinks fridge with glass doors on the front (+x). depth x width x height."""
    W, H, D = width, height, depth
    body = m.box(0, 0, 0, D, W, H, "white", top="panel")
    doors = [("rect", 0, 0, W, 0.3, "steel"), ("rect", 0, H - 0.4, W, 0.4, "brand"),
             ("ell", 0.3, H - 0.2, 0.08, 0.08, "!paper"), ("rect", 0.5, H - 0.24, 0.8, 0.08, "!paper")]
    n = max(1, int(W // 1.15))
    dw = (W - 0.12) / n
    for k in range(n):
        a = 0.06 + k * dw
        doors.append(("rect", a + 0.04, 0.4, dw - 0.08, H - 0.9, "navy"))
        for row in range(3):
            for col in range(3):
                doors.append(("rect", a + 0.12 + col * (dw - 0.2) / 3, 0.5 + row * (H - 1.1) / 3,
                              (dw - 0.2) / 3 - 0.06, (H - 1.1) / 3 - 0.2, GOODS[(k + row * 2 + col) % len(GOODS)]))
            doors.append(("rect", a + 0.1, 0.48 + row * (H - 1.1) / 3, dw - 0.2, 0.03, "metal"))
        doors += [("rect", a + 0.04, 0.4, dw - 0.08, H - 0.9, "glass", 0.45),
                  ("poly", [(a + 0.2, 0.5), (a + 0.35, 0.5), (a + 0.7, H - 0.6), (a + 0.55, H - 0.6)], "!paper", 0.25),
                  ("rect", a + dw - 0.16, 1.0, 0.05, 0.7, "!paper")]
    m.mark(body, "front", doors)
    grille = lambda w, h, f: [("rect", 0, 0, w, 0.3, "steel"), ("rect", 0, h - 0.4, w, 0.4, "brand")] + \
        [("line", [(0.15, 0.08 + i * 0.05), (w - 0.15, 0.08 + i * 0.05)], ("~", "steel", 0.7), 0.8) for i in range(4)]
    around(m, body, grille, faces=("left", "right", "back"))


def crate(m, fruit="coral", length=1.2, depth=0.9, height=0.7, price=True):
    """Wooden crate of fruit. depth x length x height."""
    c = m.box(0, 0, 0, depth, length, height, "wood")
    around(m, c, lambda w, h, f: [("line", [(0.04, h * 0.36), (w - 0.04, h * 0.36)], ("~", "wood", 0.7), 1.0),
                                  ("line", [(0.04, h * 0.7), (w - 0.04, h * 0.7)], ("~", "wood", 0.7), 1.0),
                                  ("rect", 0.04, 0.05, 0.05, h - 0.1, ("~", "wood", 0.85)), ("rect", w - 0.09, 0.05, 0.05, h - 0.1, ("~", "wood", 0.85))])
    nx, ny = int((depth - 0.1) / 0.24), int((length - 0.1) / 0.24)
    m.mark(c, "top", [("ell", 0.13 + i * 0.24, 0.13 + j * 0.24, 0.1, 0.1, fruit) for i in range(nx) for j in range(ny)]
           + [("ell", 0.1 + i * 0.24, 0.16 + j * 0.24, 0.03, 0.03, ("~", fruit, 1.3)) for i in range(nx) for j in range(ny)])
    if price:
        card = m.box(depth, length / 2 - 0.25, height * 0.45, 0.04, 0.5, 0.25, "paper")
        m.mark(card, "front", [("rect", 0.06, 0.12, 0.3, 0.06, "navy"), ("rect", 0.06, 0.04, 0.2, 0.05, "coral")])


def trolley(m, items=("coral", "gold", "teal")):
    """Shopping trolley, the handle at -x. 1.3 x 0.82 x 1.2. Anchor: 'push'
    (someone behind it facing +x, pose='hold')."""
    for wx, wy in ((0.05, 0.04), (1.1, 0.04), (0.05, 0.66), (1.1, 0.66)):
        m.box(wx, wy, 0, 0.12, 0.12, 0.14, "navy")
    m.box(0, 0, 0.14, 1.25, 0.82, 0.06, "steel")
    m.line([(0.1, 0.06, 0.2), (0.1, 0.06, 0.55)], "steel", 1.6)
    m.line([(0.1, 0.76, 0.2), (0.1, 0.76, 0.55)], "steel", 1.6)
    with m.group():                                                # goods inside a see-through basket
        for k, c in enumerate(items):
            m.box(0.15 + k * 0.33, 0.15 + (k % 2) * 0.2, 0.61, 0.3, 0.36, 0.3 + (k % 2) * 0.12, c)
        b = m.box(0, 0, 0.55, 1.25, 0.82, 0.62, "metal", opacity=0.3, faces="front,left,back,right")
        around(m, b, lambda w, h, f: [("line", [(i * 0.2, 0), (i * 0.2, h)], "steel", 1.0) for i in range(int(w / 0.2) + 1)]
               + [("line", [(0, h * 0.5), (w, h * 0.5)], "steel", 1.0), ("line", [(0, h), (w, h)], "steel", 1.6)])
    m.line([(-0.3, 0.0, 1.35), (-0.3, 0.82, 1.35)], "red", 3.5)
    m.line([(0.0, 0.0, 1.17), (-0.3, 0.0, 1.35)], "steel", 1.6)
    m.line([(0.0, 0.82, 1.17), (-0.3, 0.82, 1.35)], "steel", 1.6)
    m.anchor("push", -0.86, 0.41, 0, "+x")


def food_cart(m, length=2.6, color="coral", canopy=True):
    """Street food cart along y: a decorated customer side at +x, a big wheel
    on each long side, a glass case of food, a pot with steam and a striped
    canopy. 1.2 x length x 3.5. Anchors: 'seller' (at the +y end, facing +x,
    in view), 'seller_back' (behind it, at -x), 'customer' (facing -x)."""
    L, D = length, 1.2
    for lx, ly in ((0.1, 0.1), (D - 0.25, 0.1), (0.1, L - 0.25), (D - 0.25, L - 0.25)):
        m.box(lx, ly, 0, 0.15, 0.15, 0.5, "steel")
    body = m.box(0, 0, 0.5, D, L, 1.1, "white", top="paper")
    m.mark(body, "front", [("rect", 0, 0, L, 0.15, color), ("rect", 0, 0.95, L, 0.15, color),
                           ("rect", 0.3, 0.55, 0.9, 0.12, "brand"), ("rect", 0.3, 0.38, 0.6, 0.08, "brand"),
                           ("ell", L - 0.65, 0.5, 0.28, 0.28, "gold"), ("ell", L - 0.65, 0.5, 0.15, 0.15, color)])
    around(m, body, lambda w, h, f: [("rect", 0, 0, w, 0.15, color), ("rect", 0, 0.95, w, 0.15, color)], faces=("left", "right", "back"))
    for x0 in (D, -0.07):                                          # spoked wheels, axles along x
        m.place(wheel_part, x0, 0.7, 0, rot=270, r=0.36, width=0.07, hub="wood", spokes=True)
    m.box(0.15, L - 1.25, 1.6, 0.85, 1.15, 0.08, "steel")                # glass case base
    with m.group():                                                   # food inside see-through glass
        for i, c in enumerate(("gold", "coral", "green")):
            m.box(0.3, L - 1.15 + i * 0.35, 1.68, 0.5, 0.28, 0.12, c, top=("~", c, 1.1))
        m.box(0.15, L - 1.25, 1.68, 0.85, 1.15, 0.55, "glass", top="glass", opacity=0.35)
    m.cylinder(0.55, 0.55, 1.6, 0.3, 0.35, "steel", bands=((1.85, 1.9, "metal"),))
    m.cloud(0.55, 0.55, 2.45, 0.3, mat="white", opacity=0.85)
    if canopy:
        for px, py in ((0, 0), (D - 0.1, 0), (0, L - 0.1), (D - 0.1, L - 0.1)):
            m.box(px, py, 1.6, 0.1, 0.1, 1.8, "wood")
        roof = m.box(-0.2, -0.2, 3.4, D + 0.4, L + 0.4, 0.12, color, top="paper")
        m.mark(roof, "top", [("rect", 0, i * 0.6, D + 0.4, 0.3, color) for i in range(int((L + 0.4) / 0.6) + 1) if i * 0.6 + 0.3 <= L + 0.4])
        stripes = lambda w, h, f: [("rect", i * 0.6, 0, 0.3, h, "paper") for i in range(int(w / 0.6) + 1) if i * 0.6 + 0.3 <= w]
        around(m, roof, stripes)
    m.anchor("seller", 0.56, L + 0.45, 0, "+x")
    m.anchor("seller_back", -0.45, L * 0.38, 0, "+x")
    for i in (0.3, 0.72):
        m.anchor("customer", D + 0.55, L * i, 0, "-x")


def atm(m, color="brand"):
    """ATM kiosk, screen to the front (+x). 0.7 x 0.9 x 2.3. Anchor: 'user'
    (facing -x, in front of it)."""
    b = m.box(0, 0, 0, 0.7, 0.9, 2.1, "white", top="panel")
    m.mark(b, "front", [("rect", 0, 1.75, 0.9, 0.35, color), ("ell", 0.2, 1.92, 0.08, 0.08, "!paper"), ("rect", 0.34, 1.9, 0.4, 0.06, "!paper"),
                        ("rect", 0.08, 0.95, 0.74, 0.7, "navy"), ("rect", 0.14, 1.12, 0.62, 0.45, "!screen"),
                        ("rect", 0.2, 1.42, 0.3, 0.05, "!paper"), ("rect", 0.2, 1.3, 0.45, 0.05, "!paper")]
           + [("rect", 0.14 + (i % 3) * 0.1, 0.62 + (i // 3) * 0.08, 0.07, 0.05, "steel") for i in range(9)]
           + [("rect", 0.52, 0.8, 0.22, 0.04, "navy"), ("rect", 0.14, 0.35, 0.62, 0.08, "navy"), ("rect", 0, 0, 0.9, 0.12, "steel")])
    for f in ("left", "right"):
        m.mark(b, f, [("rect", 0, 1.75, 0.7, 0.35, color), ("rect", 0, 0, 0.7, 0.12, "steel"),
                      ("rect", 0.1, 0.3, 0.5, 1.2, ("~", "white", 0.93))])
    m.mark(b, "back", [("rect", 0.1, 0.2, 0.7, 1.4, ("~", "white", 0.9)), ("ell", 0.7, 0.9, 0.04, 0.04, "steel")])
    hood = m.box(0.7, 0.05, 1.75, 0.12, 0.8, 0.06, color)
    del hood
    m.anchor("user", 1.22, 0.45, 0, "-x")


def bin(m, color="teal"):
    """Litter bin. 0.56 x 0.56 x 0.8."""
    m.cylinder(0.28, 0.28, 0, 0.28, 0.75, color, bands=((0.6, 0.75, "navy"), (0.0, 0.08, "navy")), n=20)


def plant(m, size=1.0, pot="amber"):
    """Potted plant. 0.6 x 0.6 x 1.35 at size 1."""
    s = size
    p = m.box(0, 0, 0, 0.6 * s, 0.6 * s, 0.45 * s, pot)
    around(m, p, lambda w, h, f: [("rect", 0, h - 0.08 * s, w, 0.08 * s, ("~", pot, 1.15))])
    with m.outline():                                              # the leaves read as one bush
        m.box(0.05 * s, 0.05 * s, 0.45 * s, 0.5 * s, 0.5 * s, 0.55 * s, "leaf")
        m.box(0.15 * s, 0.15 * s, 1.0 * s, 0.3 * s, 0.3 * s, 0.3 * s, "leaf")


# ── street ───────────────────────────────────────────────────────────────
def tree(m, kind="round", size=1.0, leaf="leaf"):
    """Voxel tree, trunk at (0.55, 0.55) x size. kind 'round' (2.1 tall) or
    'pine' (2.4 tall). Every block is its own part, so people stand in front
    of the trunk and behind the crown."""
    s = size
    c = 0.55 * s
    m.shadow(c - 0.5 * s, c - 0.5 * s, 1.0 * s, 1.0 * s)
    dots = lambda w, h, f: [("rect", w * 0.18, h * 0.22, w * 0.22, h * 0.26, ("~", leaf, 0.85)),
                            ("rect", w * 0.6, h * 0.55, w * 0.18, h * 0.2, ("~", leaf, 0.85))]
    if kind == "pine":
        m.box(c - 0.12 * s, c - 0.12 * s, 0, 0.24 * s, 0.24 * s, 0.7 * s, "wood", snap=False)
        for i, w in enumerate((1.1, 0.8, 0.5)):
            b = m.box(c - w * s / 2, c - w * s / 2, (0.7 + i * 0.55) * s, w * s, w * s, 0.55 * s, leaf, snap=False)
            around(m, b, lambda W, h, f: [("rect", 0, 0, W, h * 0.25, ("~", leaf, 0.85))])
    else:
        m.box(c - 0.12 * s, c - 0.12 * s, 0, 0.24 * s, 0.24 * s, 0.8 * s, "wood", snap=False)
        with m.outline():                                          # one crown, one border
            b = m.box(c - 0.55 * s, c - 0.55 * s, 0.8 * s, 1.1 * s, 1.1 * s, 0.9 * s, leaf, snap=False)
            around(m, b, dots)
            m.box(c - 0.35 * s, c - 0.35 * s, 1.7 * s, 0.7 * s, 0.7 * s, 0.4 * s, leaf, snap=False)


def street_lamp(m, height=3.6):
    """Street lamp, the arm reaching +x. 0.9 x 0.3 x height+0.3."""
    m.box(0, 0, 0, 0.3, 0.3, 0.12, "steel")
    m.box(0.1, 0.1, 0.12, 0.1, 0.1, height - 0.12, "steel")
    m.box(0.2, 0.11, height - 0.22, 0.35, 0.08, 0.06, "steel")
    head = m.box(0.55, 0.0, height - 0.32, 0.4, 0.3, 0.3, "navy")
    for f in ("front", "left", "back", "right"):
        m.mark(head, f, [("rect", 0.05, 0.03, (0.3 if f in ("front", "back") else 0.4) - 0.1, 0.12, "!light_on")])


def house(m, width=2.4, depth=2.0, height=1.5, roof="coral", wall="white", lit=True):
    """House with a gable roof, the door on the front (+x). depth x width x
    about height+1.1. Windows on every side, a chimney on the -y slope.
    Anchor: 'door' (someone standing at the door, facing +x)."""
    W, D, H = width, depth, height
    win = "!light_on" if lit else "glass"
    m.box(-0.05, -0.05, 0, D + 0.1, W + 0.1, 0.1, "concrete")
    w = m.box(0, 0, 0.1, D, W, H, wall, top="panel")

    def window(a, b, ww=0.45, hh=0.45):
        return [("rect", a - 0.03, b - 0.06, ww + 0.06, 0.05, ("~", wall, 0.8)), ("rect", a, b, ww, hh, win),
                ("line", [(a + ww / 2, b), (a + ww / 2, b + hh)], "steel", 0.9), ("line", [(a, b + hh / 2), (a + ww, b + hh / 2)], "steel", 0.9)]
    m.mark(w, "front", [("rect", W / 2 - 0.25, 0, 0.5, 0.95, "navy"), ("ell", W / 2 + 0.15, 0.48, 0.03, 0.03, "gold"),
                        ("rect", W / 2 - 0.3, 0.95, 0.6, 0.05, ("~", wall, 0.8))] + window(0.25, 0.5) + window(W - 0.7, 0.5))
    m.mark(w, "back", window(0.3, 0.5) + window(W - 0.75, 0.5) + [("rect", W / 2 - 0.2, 0, 0.4, 0.8, ("~", wall, 0.85))])
    m.mark(w, "left", window(D / 2 - 0.25, 0.55, 0.5))
    m.mark(w, "right", window(D / 2 - 0.25, 0.55, 0.5))
    m.box(D + 0.05, W / 2 - 0.35, 0, 0.25, 0.7, 0.1, "concrete")      # door step
    top, ridge, ov = 0.1 + H, 0.1 + H + 1.0, 0.12
    m.poly([(-ov, -ov, top), (D + ov, -ov, top), (D + ov, W / 2, ridge), (-ov, W / 2, ridge)], roof)
    m.poly([(-ov, W / 2, ridge), (D + ov, W / 2, ridge), (D + ov, W + ov, top), (-ov, W + ov, top)], roof)
    for x in (0, D):
        m.poly([(x, 0, top), (x, W, top), (x, W / 2, ridge - 0.04)], wall)
    m.box(0.5, 0.3, top + 0.25, 0.3, 0.3, 0.9, "concrete", top="steel")
    m.anchor("door", D + 0.45, W / 2, 0, "+x")


def shopfront(m, width=3.0, depth=2.6, floors=2, awning="coral", sign="brand", wall="white"):
    """Shop house: a glass shop front with goods and an awning on the front
    (+x), a sign band (bars, no text), windows and an air conditioner
    upstairs, a parapet. depth x width x about 2.8 per floor.
    Anchors: 'door' (in front of the entrance, facing -x), 'window'."""
    W, D, FH = width, depth, 2.8
    H = FH * floors
    b = m.box(0, 0, 0, D, W, H, wall, top="concrete")
    front = [("rect", 0.15, 0.1, W - 1.2, 1.9, "navy"), ("rect", 0.2, 0.15, W - 1.3, 1.8, "glass")]
    for r in range(3):
        for c in range(int((W - 1.4) / 0.32)):
            front.append(("rect", 0.3 + c * 0.32, 0.25 + r * 0.55, 0.22, 0.3, GOODS[(r * 3 + c) % len(GOODS)]))
        front.append(("rect", 0.22, 0.2 + r * 0.55, W - 1.34, 0.04, "metal"))
    front += [("poly", [(0.4, 0.2), (0.6, 0.2), (1.1, 1.9), (0.9, 1.9)], "!paper", 0.25),
              ("rect", W - 0.95, 0, 0.75, 2.0, "navy"), ("rect", W - 0.9, 0.05, 0.65, 1.9, "glass"),
              ("rect", W - 0.35, 0.9, 0.05, 0.3, "!paper"), ("rect", 0, 2.05, W, 0.35, "steel")]
    front += [("line", [(0.05, 2.1 + i * 0.07), (W - 0.05, 2.1 + i * 0.07)], ("~", "steel", 0.75), 0.8) for i in range(4)]
    for f in range(1, floors):
        z0 = f * FH + 0.75
        for k in range(2):
            a = 0.35 + k * (W - 1.3)
            front += [("rect", a - 0.05, z0 - 0.08, 0.7, 0.06, ("~", wall, 0.8)), ("rect", a, z0, 0.6, 1.0, "glass" if (f + k) % 2 else "!light_on"),
                      ("line", [(a + 0.3, z0), (a + 0.3, z0 + 1.0)], "steel", 1.0)]
    m.mark(b, "front", front)
    side = []
    for f in range(floors):
        side += [("rect", D / 2 - 0.3, f * FH + 0.9, 0.6, 0.8, "glass"), ("rect", D / 2 - 0.35, f * FH + 0.84, 0.7, 0.05, ("~", wall, 0.8))]
    side += [("rect", 0.12, 0, 0.08, H, "steel")]
    for f in ("left", "right"):
        m.mark(b, f, side)
    m.mark(b, "back", [("rect", W / 2 - 0.3, f * FH + 0.9, 0.6, 0.8, "glass") for f in range(floors)] + [("rect", 0.3, 0, 0.6, 1.9, ("~", wall, 0.85))])
    aw = m.box(D, 0.05, 2.72, 0.7, W - 0.1, 0.1, awning, top="paper")    # above head height (2.6)
    m.mark(aw, "top", [("rect", 0, i * 0.5, 0.7, 0.25, awning) for i in range(int((W - 0.1) / 0.5) + 1) if i * 0.5 + 0.25 <= W - 0.1])
    m.mark(aw, "front", [("rect", i * 0.5, 0, 0.25, 0.1, "paper") for i in range(int((W - 0.1) / 0.5) + 1) if i * 0.5 + 0.25 <= W - 0.1])
    sg = m.box(D, 0.2, FH + 0.05, 0.08, W - 0.4, 0.45, sign)
    m.mark(sg, "front", [("ell", 0.3, 0.22, 0.13, 0.13, "!paper"), ("rect", 0.55, 0.26, W - 1.6, 0.08, "!paper"), ("rect", 0.55, 0.12, (W - 1.6) * 0.6, 0.06, "!paper")])
    if floors > 1:
        ac = m.box(0.4, W, FH + 0.4, 0.6, 0.3, 0.45, "paper")
        m.mark(ac, "left", [("ring", 0.3, 0.22, 0.15, 0.15, "steel", 1.0), ("line", [(0.08, 0.05), (0.08, 0.4)], "steel", 0.8)])
    rim = ("~", wall, 0.95)                                        # parapet rim round a flat roof
    for x0, y0, w, d in ((-0.04, -0.04, D + 0.08, 0.08), (-0.04, W - 0.04, D + 0.08, 0.08),
                         (-0.04, 0.04, 0.08, W - 0.08), (D - 0.04, 0.04, 0.08, W - 0.08)):
        m.box(x0, y0, H, w, d, 0.22, rim, top=("~", wall, 1.05))
    m.cylinder(0.7, 0.8, H, 0.32, 0.6, "sky", bands=((H + 0.45, H + 0.5, "navy"),), n=16)    # water tank
    unit_ = m.box(D - 1.0, W - 0.9, H, 0.6, 0.5, 0.35, "paper")                                # roof unit
    m.mark(unit_, "front", [("ring", 0.25, 0.17, 0.12, 0.12, "steel", 1.0)])
    m.anchor("door", D + 0.95, W - 0.58, 0, "-x")
    m.anchor("window", D + 0.95, W * 0.35, 0, "-x")


def car(m, color="sky", length=3.8, width=1.7):
    """Car, its nose at +x. length x width x 1.6. Headlights at the front,
    tail lights at the back, windows and door lines all round."""
    L, Wd = length, width
    for cx in (0.9, L - 0.9):
        wheel(m, cx, 0.36, 0.36, -0.14, 0.0)
        wheel(m, cx, 0.36, 0.36, Wd, Wd + 0.14)
    body = m.box(0, 0, 0.25, L, Wd, 0.75, color)
    m.mark(body, "front", [("rect", 0.1, 0.0, Wd - 0.2, 0.14, "steel"), ("rect", 0.15, 0.38, 0.32, 0.16, "!light_on"),
                           ("rect", Wd - 0.47, 0.38, 0.32, 0.16, "!light_on"), ("rect", 0.55, 0.3, Wd - 1.1, 0.24, "navy"),
                           ("rect", Wd / 2 - 0.25, 0.04, 0.5, 0.12, "paper")])
    m.mark(body, "back", [("rect", 0.1, 0.0, Wd - 0.2, 0.14, "steel"), ("rect", 0.12, 0.4, 0.3, 0.14, "red"),
                          ("rect", Wd - 0.42, 0.4, 0.3, 0.14, "red"), ("rect", Wd / 2 - 0.25, 0.18, 0.5, 0.12, "paper")])
    sidem = lambda w, h, f: [("line", [(w * 0.38, 0.05), (w * 0.38, h - 0.02)], ("~", color, 0.75), 1.0),
                             ("line", [(w * 0.62, 0.05), (w * 0.62, h - 0.02)], ("~", color, 0.75), 1.0),
                             ("rect", w * 0.42, h - 0.22, 0.14, 0.04, ("~", color, 0.7)), ("rect", w * 0.66, h - 0.22, 0.14, 0.04, ("~", color, 0.7)),
                             ("rect", 0, 0.05, w, 0.08, ("~", color, 0.8))]
    m.mark(body, "left", sidem(L, 0.75, "left"))
    m.mark(body, "right", sidem(L, 0.75, "right"))
    cab = m.box(L * 0.27, 0.1, 1.0, L * 0.47, Wd - 0.2, 0.6, color, top=("~", color, 1.08))
    cw, cd = L * 0.47, Wd - 0.2
    m.mark(cab, "front", [("rect", 0.06, 0.06, cd - 0.12, 0.46, "glass"), ("poly", [(0.25, 0.08), (0.4, 0.08), (0.6, 0.5), (0.45, 0.5)], "!paper", 0.3)])
    m.mark(cab, "back", [("rect", 0.08, 0.08, cd - 0.16, 0.42, "glass")])
    for f in ("left", "right"):
        m.mark(cab, f, [("rect", 0.08, 0.08, cw / 2 - 0.12, 0.44, "glass"), ("rect", cw / 2 + 0.04, 0.08, cw / 2 - 0.12, 0.44, "glass")])


def motorbike(m, color="red"):
    """Step-through scooter, the front wheel at +x. 1.8 x 0.5 x 1.2.
    Anchor: 'rider' (standing beside it, at -y, facing +x)."""
    wheel(m, 0.24, 0.24, 0.24, 0.18, 0.32)                          # rear wheel
    wheel(m, 1.56, 0.24, 0.24, 0.18, 0.32)                          # front wheel
    body = m.box(0.48, 0.1, 0.3, 0.5, 0.34, 0.45, color)            # rear body over the engine
    for f in ("left", "right"):
        m.mark(body, f, [("rect", 0.06, 0.08, 0.36, 0.06, ("~", color, 1.25)), ("arc", 0.25, 0.3, 0.34, 0.03, ("~", color, 0.75), 1.0)])
    m.mark(body, "back", [("rect", 0.1, 0.32, 0.14, 0.08, "red")])
    m.box(0.0, 0.16, 0.5, 0.48, 0.22, 0.05, color)                  # rear fender
    m.box(0.36, 0.12, 0.75, 0.62, 0.3, 0.1, "navy")                 # seat
    deck = m.box(0.98, 0.1, 0.3, 0.32, 0.34, 0.06, "navy")          # floorboard
    m.mark(deck, "top", [("line", [(0.04, 0.06 + i * 0.07), (0.28, 0.06 + i * 0.07)], "steel", 0.6) for i in range(4)])
    shield = m.box(1.3, 0.1, 0.3, 0.1, 0.34, 0.68, color)           # leg shield
    m.mark(shield, "front", [("rect", 0.1, 0.4, 0.14, 0.12, "!light_on"), ("rect", 0.03, 0.08, 0.28, 0.05, ("~", color, 0.75))])
    m.box(1.4, 0.16, 0.5, 0.4, 0.22, 0.05, color)                   # front fender
    m.line([(1.56, 0.25, 0.24), (1.42, 0.25, 1.0)], "steel", 2.2)   # fork
    m.line([(1.42, -0.04, 1.06), (1.42, 0.54, 1.06)], "navy", 2.6)  # handlebar
    hl = m.box(1.4, 0.15, 0.98, 0.12, 0.24, 0.12, color)            # headlight housing
    m.mark(hl, "front", [("rect", 0.04, 0.03, 0.16, 0.07, "!light_on")])
    m.line([(1.42, -0.04, 1.06), (1.36, -0.12, 1.2)], "steel", 1.0)   # mirrors
    m.line([(1.42, 0.54, 1.06), (1.36, 0.62, 1.2)], "steel", 1.0)
    m.anchor("rider", 0.6, -0.55, 0, "+x")


# ── power ────────────────────────────────────────────────────────────────
def pylon(m, height=6.5, arms=(-1.0, 0.0, 1.0)):
    """Lattice transmission tower, centred on (0.6, 0.6), arms along y.
    Anchors: 'phase' (one per arm, at the insulator foot, for wires),
    'peak' (top, for the shield wire)."""
    b, tp, h, c = 0.6, 0.2, height, 0.6
    def L(sx, sy, f):
        r = b + (tp - b) * f
        return (c + sx * r, c + sy * r, h * f)
    legs = [(-1, -1), (1, -1), (1, 1), (-1, 1)]
    base = 0.25 / h
    for sx, sy in legs:
        m.box(c + sx * b - 0.15, c + sy * b - 0.15, 0, 0.3, 0.3, 0.25, "concrete", snap=False)
        m.line([L(sx, sy, base), L(sx, sy, 1)], "steel", 2.4)
    for i in range(6):
        f0, f1 = base + (1 - base) * i / 6, base + (1 - base) * (i + 1) / 6
        for a, cc in ((legs[3], legs[2]), (legs[1], legs[2]), (legs[0], legs[1]), (legs[0], legs[3])):
            m.line([L(*a, f0), L(*cc, f1)], "steel", 1.0)
            m.line([L(*cc, f0), L(*a, f1)], "steel", 1.0)
            m.line([L(*a, f1), L(*cc, f1)], "steel", 1.0)
    m.box(c - 0.12, c - 1.3, h - 0.7, 0.24, 2.6, 0.2, "steel", snap=False)
    m.box(c - 0.1, c - 0.1, h, 0.2, 0.2, 0.6, "steel", snap=False)
    for dy in arms:
        m.line([(c, c + dy, h - 0.7), (c, c + dy, h - 1.3)], "teal", 3.2)
        m.anchor("phase", c, c + dy, h - 1.3)
    m.anchor("peak", c, c, h + 0.6)
    m.shadow(c - b, c - b, 2 * b, 2 * b)


def transformer(m, color="teal"):
    """Oil transformer on a plinth: fins all round, a conservator tank and
    three bushings. 1.8 x 1.8 x 2.5. Anchors: 'bushing' (three, at the tops)."""
    m.box(0, 0, 0, 1.8, 1.8, 0.2, "concrete")
    t = m.box(0.1, 0.1, 0.2, 1.6, 1.6, 1.5, color, top=("~", color, 1.15))
    fins = lambda w, h, f: [("line", [(0.15 + k * 0.18, 0.15), (0.15 + k * 0.18, h - 0.2)], ("~", color, 0.7), 1.0) for k in range(int((w - 0.2) / 0.18))]
    around(m, t, fins, faces=("left", "back", "right"))
    m.mark(t, "front", fins(1.6, 1.5, "front")[:3] + [("rect", 0.5, 0.9, 1.0, 0.35, "paper"), ("rect", 0.6, 1.0, 0.3, 0.15, "gold"),
                                                       ("rect", 0.95, 1.02, 0.45, 0.04, "navy"), ("rect", 0.95, 1.12, 0.35, 0.04, "navy")])
    m.cylinder(0.3, 0.9, 1.7, 0.18, 0.7, "metal")
    for k in range(3):
        y = 0.5 + k * 0.4
        m.cylinder(1.1, y, 1.7, 0.07, 0.75, "paper", bands=((2.0, 2.06, "steel"), (2.2, 2.26, "steel")), n=12)
        m.anchor("bushing", 1.1, y, 2.45)


def gantry(m, span=3.85, height=4.0, pegs=(-1.1, 0.0, 1.1)):
    """Substation line gantry, the beam along y. 0.25 x span x height.
    Anchors: 'peg' (insulator feet, one per entry in pegs)."""
    m.box(0, 0, 0, 0.25, 0.25, height, "steel")
    m.box(0, span - 0.25, 0, 0.25, 0.25, height, "steel")
    m.box(0, 0, height, 0.25, span, 0.25, "steel")
    mid = span / 2
    for dy in pegs:
        m.line([(0.12, mid + dy, height), (0.12, mid + dy, height - 0.55)], "teal", 3)
        m.anchor("peg", 0.12, mid + dy, height - 0.55)


def cooling_tower(m, r0=2.0, r1=1.4, height=5.4, steam=True, color="white"):
    """Hyperbolic cooling tower centred on (r0, r0), with steam."""
    m.tower(r0, r0, 0, r0, r1, height, color, bands=((0, 0.35, "concrete"), (height - 0.5, height - 0.3, "panel")))
    if steam:
        m.cloud(r0, r0, height + 1.0, r1 * 0.93)
        m.cloud(r0 - 0.4, r0 - 0.6, height + 2.4, r1 * 0.68)


def chimney(m, r=0.55, height=7.6, smoke=True):
    """Striped stack centred on (0.75, 0.75) on a round footing."""
    m.cylinder(0.75, 0.75, 0, 0.75, 0.4, "concrete")
    m.cylinder(0.75, 0.75, 0.4, r, height - 0.4, "white", bands=((height - 1.4, height - 1.0, "red"), (height - 0.6, height - 0.2, "red")))
    if smoke:
        m.cloud(0.75, 0.75, height + 0.7, r)


def solar_panel(m, length=2.0, tilt=0.6):
    """Solar panel on a frame, tilted up towards -x (the sun side) so its cells
    face the viewer when turned rot=180. length along y, 1.1 deep."""
    z0, z1 = 0.5, 0.5 + tilt
    for y0 in (0.1, length - 0.2):                                 # legs reach up to the tilted panel
        m.box(0.1, y0, 0, 0.1, 0.1, z0 + 0.05 + tilt * 0.1 / 1.1, "steel", snap=False)
        m.box(0.9, y0, 0, 0.1, 0.1, z0 + 0.05 + tilt * 0.9 / 1.1, "steel", snap=False)
    m.poly([(0.0, 0.0, z0 + 0.06), (0.0, length, z0 + 0.06), (1.1, length, z1 + 0.06), (1.1, 0.0, z1 + 0.06)], "brand")
    for i in range(1, 5):
        y = length * i / 5
        m.line([(0.0, y, z0 + 0.07), (1.1, y, z1 + 0.07)], "sky", 0.9)
    for j in range(1, 3):
        f = j / 3
        m.line([(1.1 * f, 0.0, z0 + 0.07 + tilt * f), (1.1 * f, length, z0 + 0.07 + tilt * f)], "sky", 0.9)


def fence(m, length=4.0, height=1.0, spacing=0.8):
    """Mesh fence along y with posts. 0.1 x length x height."""
    n = int(length / spacing)
    for i in range(n + 1):
        m.box(0.02, min(i * spacing, length - 0.08), 0, 0.08, 0.08, height, "steel", snap=False)
    mesh = m.box(0.0, 0, 0.05, 0.02, length, height - 0.1, "metal", opacity=0.25, faces="front,back", snap=False)
    diag = lambda w, h, f: [("line", [(i * 0.2, 0), (i * 0.2 + h * 0.45, h)], "steel", 0.6) for i in range(int(w / 0.2))]
    m.mark(mesh, "front", diag(length, height - 0.1, "front"))
    m.mark(mesh, "back", diag(length, height - 0.1, "back"))


# ── money ────────────────────────────────────────────────────────────────
def coin_stack(m, coins=6, color="gold"):
    """A stack of coins centred on (0.25, 0.25). 0.5 wide, 0.07 per coin."""
    h = 0.07 * coins
    bands = tuple((0.07 * i, 0.07 * i + 0.015, ("~", color, 0.8)) for i in range(1, coins))
    m.cylinder(0.25, 0.25, 0, 0.24, h, color, bands=bands, n=24)


def cash_stack(m, bundles=4, color="green"):
    """Bundles of banknotes with paper bands, slightly askew. 0.8 x 0.45."""
    for i in range(bundles):
        dx = (0.04 if i % 2 else 0.0)
        b = m.box(dx, 0.02 * (i % 3), i * 0.1, 0.7, 0.36, 0.1, color, top=("~", color, 1.1))
        m.mark(b, "top", [("ell", 0.35, 0.18, 0.09, 0.09, ("~", color, 0.8)), ("rect", 0.3, 0, 0.1, 0.36, "paper"),
                          ("rect", 0.05, 0.04, 0.08, 0.04, ("~", color, 0.75)), ("rect", 0.57, 0.28, 0.08, 0.04, ("~", color, 0.75))])
        around(m, b, lambda w, h, f: [("rect", (w - 0.1) / 2, 0, 0.1, h, "paper")] if f in ("left", "right") else
               [("line", [(0.02, h * 0.5), (w - 0.02, h * 0.5)], ("~", color, 0.75), 0.6)])


def piggy_bank(m, color="rose"):
    """Piggy bank, snout to the front (+x), a coin slot on top. 1.1 x 0.6 x 0.9."""
    for x0 in (0.12, 0.62):
        for y0 in (0.06, 0.42):
            m.box(x0, y0, 0, 0.14, 0.12, 0.16, ("~", color, 0.85))
    body = m.box(0, 0, 0.16, 0.9, 0.6, 0.6, color, top=("~", color, 1.08))
    m.mark(body, "front", [("ell", 0.17, 0.42, 0.04, 0.055, "_face"), ("ell", 0.43, 0.42, 0.04, 0.055, "_face"),
                           ("ell", 0.18, 0.44, 0.013, 0.016, "#FFFFFF"), ("ell", 0.44, 0.44, 0.013, 0.016, "#FFFFFF"),
                           ("ell", 0.1, 0.22, 0.05, 0.03, "blush", 0.8), ("ell", 0.5, 0.22, 0.05, 0.03, "blush", 0.8)])
    m.mark(body, "top", [("rect", 0.35, 0.22, 0.22, 0.05, "_face")])
    for f in ("left", "right"):
        m.mark(body, f, [("arc", 0.45, 0.25, 0.3, 0.04, ("~", color, 0.75), 1.0)])
    snout = m.box(0.9, 0.2, 0.3, 0.1, 0.2, 0.17, ("~", color, 1.12))
    m.mark(snout, "front", [("ell", 0.06, 0.085, 0.025, 0.035, ("~", color, 0.6)), ("ell", 0.14, 0.085, 0.025, 0.035, ("~", color, 0.6))])
    for y0 in (0.04, 0.44):
        m.box(0.62, y0, 0.76, 0.14, 0.12, 0.12, ("~", color, 0.9))
    m.box(-0.06, 0.26, 0.5, 0.06, 0.08, 0.1, ("~", color, 0.9))


MODELS = [bench, chair, stool, table, desk_set, counter, shelf, fridge, crate, trolley, food_cart, atm, bin, plant,
          tree, street_lamp, house, shopfront, car, motorbike, pylon, transformer, gantry, cooling_tower, chimney,
          solar_panel, fence, coin_stack, cash_stack, piggy_bank, laptop]
