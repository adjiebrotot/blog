"""
iso.py - isometric sketch engine for the blog's isometric illustrations (v3).
Used through render.py; see ../SKILL.md.

A scene is plain Python calling primitives on a Scene; Scene.svg(theme)
renders it once per theme from the same geometry, so the dark and light
files are always the same drawing.

GRID FIRST. Every scene lives on one isometric lattice:
  +x runs to the lower-right on screen, +y to the lower-left, +z up.
  1 unit = one grid cell (about knee height of a character).
  box / tile / poly coordinates snap to the sub-grid (default 1/20 unit,
  so decimal measures like 0.6 or 1.35 stay exact),
  every edge sits on a lattice line. Scene.svg(..., grid_overlay=True)
  draws the lattice over the art (write_pair saves <name>-gridcheck.png).

LAYERING (v3). Every primitive is its own sortable unit, so a person's arm,
a bench leg and a pylon member each find their own place. For every pair of
units whose drawings overlap on screen the renderer decides who is in front:
  1. if their 3D bounding boxes are separated on x, y or z, the one that ends
     first is behind (exact for any shapes, not only boxes);
  2. otherwise it compares the real geometry: it intersects their projected
     faces and, at the middle of each overlap, compares the depth (x+y+z) of
     the two surfaces. The larger depth is nearer to the viewer.
The pairs become a graph that is topologically sorted. This is exact for
any units that do not interpenetrate, including diagonal lines, wires,
roofs, cylinders and people standing next to each other. Rules for authors:
  * Parts that touch are fine. Parts that pass through each other are a
    modelling error: Scene.check() (run by write_pair) lists them.
  * s.group() still bundles parts into ONE unit painted in written order.
    Use it only for small props whose parts really interpenetrate.
  * Details stick to the face they are drawn on, so they layer with it.

OBJECTS. Build each thing once in its own space (a function model(m, ...),
front facing +x, details on every side, anchors for people and cables) and
place it: s.place(model, x, y, z, rot=0|90|180|270, mirror, scale). The
object is a group for building and arranging only; its parts still sort one
by one. models.py holds the library; sheet.py draws objects alone.
"""
import math, heapq, os, io, copy
from contextlib import nullcontext
from contextlib import contextmanager

C30 = math.cos(math.radians(30))
EPS = 1e-6
AREA_EPS = 2e-4      # unit^2: overlaps smaller than this are touching, not covering
DTOL = 1e-4          # depth tolerance: closer than this is coplanar (author order wins)

# ── Palettes (roles from light.css / dark.css) ───────────────────────────
PALETTES = {
    "light": {
        "_bg": "#F0F4FF", "_ink": "#14203A", "_ink_op": 0.9, "_face": "#14203A",
        "_shadow": "#14203A", "_shadow_op": 0.10, "_grid": "#C8D4E8",
        "_shade": (1.10, 0.97, 0.80),          # top, left, right
        "ground": "#E3EAF7", "floor": "#FFFFFF", "wall": "#FFFFFF", "panel": "#DCE3F0",
        "paper": "#FFFFFF", "concrete": "#D3DBE8", "gravel": "#C9D2E1", "road": "#9AA6BA",
        "brand": "#0052CC", "blue": "#3A71C8", "sky": "#5A91E8", "pale": "#BFD5F7",
        "gold": "#F2B24C", "amber": "#B45309", "teal": "#4A9E87", "green": "#8CC9A4",
        "leaf": "#4F9E6E", "coral": "#E66A6A", "red": "#E63939", "rose": "#C46A7E",
        "purple": "#9B59B6", "metal": "#AEB9CC", "steel": "#6E7C8E", "glass": "#CFE0FA",
        "navy": "#14203A", "white": "#FFFFFF", "wood": "#C98A4B", "shirt": "#F4F7FD",
        "denim": "#4A6FA5", "khaki": "#C9B48A", "maroon": "#8E3B46", "olive": "#7D8B4E",
        "skin1": "#F6C9A0", "skin2": "#D9A274", "skin3": "#A8714A", "skin4": "#7A4E33",
        "hair1": "#3A2A22", "hair2": "#7A4A2A", "hair3": "#2B3550", "hair4": "#E39B4A",
        "hair5": "#B9B9C4", "shoe": "#3C4A63", "pants": "#2E3D5C",
        "light_on": "#FFD28C", "wire": "#14203A", "blush": "#F29C9C", "screen": "#9CC2F5",
    },
    "dark": {
        "_bg": "#0F1728", "_ink": "#060A14", "_ink_op": 0.9, "_face": "#0B1220",
        "_shadow": "#000000", "_shadow_op": 0.35, "_grid": "#2C3A52",
        "_shade": (1.18, 1.0, 0.78),
        "ground": "#162033", "floor": "#1C2942", "wall": "#2A3A5A", "panel": "#2C3A52",
        "paper": "#B8C6DE", "concrete": "#2A3954", "gravel": "#24314A", "road": "#111A2C",
        "brand": "#2D67C7", "blue": "#2F5FA8", "sky": "#4A7BC8", "pale": "#36507E",
        "gold": "#E0A94F", "amber": "#B7712A", "teal": "#3E8A76", "green": "#3F7A5F",
        "leaf": "#2F6B4C", "coral": "#C85F5F", "red": "#C6382F", "rose": "#A85F72",
        "purple": "#7E4C99", "metal": "#4F5F7A", "steel": "#3A4760", "glass": "#4A6A9E",
        "navy": "#2B3A5C", "white": "#3A4B6B", "wood": "#8A5A30", "shirt": "#9FB0CC",
        "denim": "#36507E", "khaki": "#8F7F5E", "maroon": "#6E2E38", "olive": "#5A6638",
        "skin1": "#E8B98F", "skin2": "#C48E62", "skin3": "#93613E", "skin4": "#6B4430",
        "hair1": "#2A1E18", "hair2": "#6A3F24", "hair3": "#1E2740", "hair4": "#C9843C",
        "hair5": "#8E93A3", "shoe": "#0B1220", "pants": "#22304D",
        "light_on": "#FFD28C", "wire": "#8DA2C4", "blush": "#C46A6A", "screen": "#7FA6E0",
    },
}


def _hex(c):
    c = c.lstrip("#"); return tuple(int(c[i:i + 2], 16) for i in (0, 2, 4))


def shade(c, k):
    r, g, b = _hex(c)
    if k >= 1:
        t = k - 1; r, g, b = (v + (255 - v) * t for v in (r, g, b))
    else:
        r, g, b = (v * k for v in (r, g, b))
    return "#%02X%02X%02X" % tuple(max(0, min(255, round(v))) for v in (r, g, b))


def _jit(a, b, seed, j):
    """Deterministic wobble per screen vertex: shared corners move together,
    and the same corner wobbles the same way in every frame (no boiling)."""
    h = (int(round(a * 2)) * 73856093) ^ (int(round(b * 2)) * 19349663) ^ (seed * 83492791)
    h &= 0xFFFFFFFF
    return ((h % 1000) / 500 - 1) * j, (((h // 1000) % 1000) / 500 - 1) * j


# ── projection and depth geometry (unit-free screen coordinates) ─────────
def _S(x, y, z):
    """World point -> screen point at unit 1 (y grows downwards)."""
    return ((x - y) * C30, (x + y) * 0.5 - z)


def _area2(poly):
    s = 0.0
    n = len(poly)
    for i in range(n):
        x0, y0 = poly[i]; x1, y1 = poly[(i + 1) % n]
        s += x0 * y1 - x1 * y0
    return s


def _hull(pts):
    pts = sorted(set((round(x, 9), round(y, 9)) for x, y in pts))
    if len(pts) < 3:
        return pts

    def cross(o, a, b):
        return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])
    lo, hi = [], []
    for p in pts:
        while len(lo) >= 2 and cross(lo[-2], lo[-1], p) <= 0:
            lo.pop()
        lo.append(p)
    for p in reversed(pts):
        while len(hi) >= 2 and cross(hi[-2], hi[-1], p) <= 0:
            hi.pop()
        hi.append(p)
    return lo[:-1] + hi[:-1]


def _bbox2(poly):
    xs = [p[0] for p in poly]; ys = [p[1] for p in poly]
    return (min(xs), min(ys), max(xs), max(ys))


class _Facet:
    """A convex screen polygon with a depth function. kind 'p': planar (depth
    is affine in screen x, y); kind 's': a line segment of some half width."""
    __slots__ = ("kind", "poly", "bb", "k")

    def depth(self, x, y):
        if self.kind == "p":
            a, b, c = self.k
            return a * x + b * y + c
        ax, ay, dx, dy, l2, d0, d1 = self.k
        t = ((x - ax) * dx + (y - ay) * dy) / l2 if l2 > 0 else 0.0
        t = 0.0 if t < 0 else 1.0 if t > 1 else t
        return d0 + t * (d1 - d0)


def _plane_facet(pts3):
    proj = [_S(*p) for p in pts3]
    dep = [p[0] + p[1] + p[2] for p in pts3]
    if abs(_area2(proj)) < 1e-7:
        return None                                  # edge-on: covers nothing
    best, tri = 0.0, None
    n = len(proj)
    for i in range(1, n - 1):                        # best-conditioned triangle
        (x0, y0), (x1, y1), (x2, y2) = proj[0], proj[i], proj[i + 1]
        a = abs((x1 - x0) * (y2 - y0) - (y1 - y0) * (x2 - x0))
        if a > best:
            best, tri = a, (0, i, i + 1)
    i, j, k = tri
    (x0, y0), (x1, y1), (x2, y2) = proj[i], proj[j], proj[k]
    d0, d1, d2 = dep[i], dep[j], dep[k]
    e1 = (x1 - x0, y1 - y0, d1 - d0); e2 = (x2 - x0, y2 - y0, d2 - d0)
    nx = e1[1] * e2[2] - e1[2] * e2[1]
    ny = e1[2] * e2[0] - e1[0] * e2[2]
    nz = e1[0] * e2[1] - e1[1] * e2[0]
    a, b = -nx / nz, -ny / nz
    f = _Facet(); f.kind = "p"; f.k = (a, b, d0 - a * x0 - b * y0)
    f.poly = _hull(proj); f.bb = _bbox2(f.poly)
    if len(f.poly) < 3:
        return None
    return f


def _seg_facet(p, q, hw):
    (ax, ay), (bx, by) = _S(*p), _S(*q)
    d0, d1 = sum(p), sum(q)
    dx, dy = bx - ax, by - ay
    L = math.hypot(dx, dy)
    f = _Facet(); f.kind = "s"
    if L < 1e-9:
        f.k = (ax, ay, 0.0, 0.0, 0.0, d0, d0)
        f.poly = [(ax - hw, ay - hw), (ax + hw, ay - hw), (ax + hw, ay + hw), (ax - hw, ay + hw)]
    else:
        nx, ny = -dy / L * hw, dx / L * hw
        tx, ty = dx / L * hw * 0.5, dy / L * hw * 0.5
        f.k = (ax, ay, dx, dy, L * L, d0, d1)
        f.poly = _hull([(ax + nx - tx, ay + ny - ty), (bx + nx + tx, by + ny + ty),
                        (bx - nx + tx, by - ny + ty), (ax - nx - tx, ay - ny - ty)])
    f.bb = _bbox2(f.poly)
    return f


def _clip(subject, clipper):
    """Sutherland-Hodgman: subject polygon clipped by a convex CCW clipper."""
    out = subject
    n = len(clipper)
    for i in range(n):
        if not out:
            break
        px, py = clipper[i]; qx, qy = clipper[(i + 1) % n]
        ex, ey = qx - px, qy - py
        inp, out = out, []
        m = len(inp)
        sx, sy = inp[-1]
        s_in = ex * (sy - py) - ey * (sx - px) >= 0
        for j in range(m):
            cx, cy = inp[j]
            c_in = ex * (cy - py) - ey * (cx - px) >= 0
            if c_in != s_in:
                dx, dy = cx - sx, cy - sy
                den = ex * dy - ey * dx
                if den != 0:
                    t = (ey * (sx - px) - ex * (sy - py)) / den
                    out.append((sx + t * dx, sy + t * dy))
            if c_in:
                out.append((cx, cy))
            sx, sy, s_in = cx, cy, c_in
    return out


def _centroid(poly):
    a = cx = cy = 0.0
    n = len(poly)
    for i in range(n):
        x0, y0 = poly[i]; x1, y1 = poly[(i + 1) % n]
        c = x0 * y1 - x1 * y0
        a += c; cx += (x0 + x1) * c; cy += (y0 + y1) * c
    if abs(a) < 1e-12:
        return 0.0, 0.0, 0.0
    return cx / (3 * a), cy / (3 * a), abs(a) / 2


def _compare(A, B, early=False):
    """Area-weighted vote over every pair of overlapping facets.
    Returns None if the two never cover each other, else a number:
    > 0 when A is in front of B, < 0 when behind, 0 when coplanar.
    early=True returns 0 at the first real overlap (overlap test only)."""
    vote, seen = 0.0, False
    for fa in A.facets:
        ab = fa.bb
        for fb in B.facets:
            bb = fb.bb
            if ab[2] <= bb[0] or bb[2] <= ab[0] or ab[3] <= bb[1] or bb[3] <= ab[1]:
                continue
            if fa.kind == "s" and fb.kind == "s":
                # two lines cover each other only where they cross; lines that
                # merely meet at a joint (a lattice node, a wire on a peg) don't
                ax, ay, dx, dy, _, _, _ = fa.k
                bx, by, ex, ey, _, _, _ = fb.k
                den = dx * ey - dy * ex
                if abs(den) > 1e-12:
                    t = ((bx - ax) * ey - (by - ay) * ex) / den
                    u = ((bx - ax) * dy - (by - ay) * dx) / den
                    if not (0.03 < t < 0.97 and 0.03 < u < 0.97):
                        continue
                    cx, cy = ax + t * dx, ay + t * dy
                    if early:
                        return 0.0
                    seen = True
                    d = fa.depth(cx, cy) - fb.depth(cx, cy)
                    w = 1e-3
                    vote += w if d > DTOL else -w if d < -DTOL else 0.0
                    continue
            inter = _clip(fa.poly, fb.poly)
            if len(inter) < 3:
                continue
            cx, cy, ar = _centroid(inter)
            if ar < AREA_EPS:
                continue
            if early:
                return 0.0
            seen = True
            d = fa.depth(cx, cy) - fb.depth(cx, cy)
            if d > DTOL:
                vote += ar
            elif d < -DTOL:
                vote -= ar
    return vote if seen else None


def _behind(a, b):
    """-1 if box a is behind b, 1 if in front, 0 if not separable."""
    for k in (0, 2, 4):
        ab = a[k + 1] <= b[k] + EPS
        ba = b[k + 1] <= a[k] + EPS
        if ab and not ba:
            return -1
        if ba and not ab:
            return 1
    return 0


def _hex_overlap(a, b):
    """Do the screen hexagons of two 3D boxes overlap (Lebron's test)?"""
    for (i0, i1, j0, j1) in ((0, 1, 2, 3), (0, 1, 4, 5), (2, 3, 4, 5)):
        lo_a, hi_a = a[i0] - a[j1], a[i1] - a[j0]
        lo_b, hi_b = b[i0] - b[j1], b[i1] - b[j0]
        if hi_a <= lo_b + EPS or hi_b <= lo_a + EPS:
            return False
    return True


class _Item:
    __slots__ = ("kind", "data", "marks", "atom", "tag", "box", "bb", "local", "T", "ol")

    def __init__(self, kind, data, tag):
        self.kind, self.data, self.marks, self.atom, self.tag, self.box = kind, data, [], None, tag, None
        self.bb, self.local, self.T, self.ol = None, None, None, None


class _Atom:
    __slots__ = ("items", "bb", "facets", "seq", "boxlike", "sbb")

    def __init__(self, seq, boxlike):
        self.items, self.facets, self.seq, self.boxlike = [], [], seq, boxlike
        self.bb = [1e18, -1e18, 1e18, -1e18, 1e18, -1e18]
        self.sbb = None


# ── objects: transforms, the drawing view a model gets, instances ────────
_LEGACY_AXES = {"r": ((0, 1, 0), (0, 0, 1)), "l": ((1, 0, 0), (0, 0, 1)), "t": ((1, 0, 0), (0, 1, 0))}
FACE_NORMALS = {"front": (1, 0, 0), "back": (-1, 0, 0), "left": (0, 1, 0), "right": (0, -1, 0), "top": (0, 0, 1),
                "+x": (1, 0, 0), "-x": (-1, 0, 0), "+y": (0, 1, 0), "-y": (0, -1, 0), "+z": (0, 0, 1)}
_VISIBLE = {(1, 0, 0): "r", (0, 1, 0): "l", (0, 0, 1): "t"}
_DIR_FACING = {(1, 0): "r", (0, 1): "l", (-1, 0): "ul", (0, -1): "ur"}
_ROT = {0: ((1, 0), (0, 1)), 90: ((0, -1), (1, 0)), 180: ((-1, 0), (0, -1)), 270: ((0, 1), (-1, 0))}


def _face_frame(box, n):
    """Lower-left corner and (a, b) axes of a box face, as you look at it:
    a runs left to right (the +x face runs along -y, +y along +x, -x along
    +y, -y along -x), b runs up. The top runs a along +x, b along +y."""
    x, y, z, w, d, h = box
    if n == (1, 0, 0):
        return (x + w, y + d, z), (0, -1, 0), (0, 0, 1)
    if n == (0, 1, 0):
        return (x, y + d, z), (1, 0, 0), (0, 0, 1)
    if n == (-1, 0, 0):
        return (x, y, z), (0, 1, 0), (0, 0, 1)
    if n == (0, -1, 0):
        return (x + w, y, z), (-1, 0, 0), (0, 0, 1)
    return (x, y, z + h), (1, 0, 0), (0, 1, 0)


class _T:
    """Placement transform: mirror across x, turn by 90-degree steps, scale,
    then move. Boxes stay axis-aligned, so the sorter stays exact."""
    __slots__ = ("m", "k", "t")

    def __init__(self, m=((1, 0), (0, 1)), k=1.0, t=(0.0, 0.0, 0.0)):
        self.m, self.k, self.t = m, k, t

    @staticmethod
    def make(x, y, z, rot=0, mirror=False, k=1.0):
        if rot % 90:
            raise ValueError("rot must be a multiple of 90 (got %r)" % (rot,))
        (a, b), (c, d) = _ROT[rot % 360]
        if mirror:
            b, d = -b, -d
        return _T(((a, b), (c, d)), k, (x, y, z))

    def pt(self, x, y, z):
        (a, b), (c, d) = self.m
        tx, ty, tz = self.t
        k = self.k
        return (tx + k * (a * x + b * y), ty + k * (c * x + d * y), tz + k * z)

    def vec(self, x, y, z):
        (a, b), (c, d) = self.m
        k = self.k
        return (k * (a * x + b * y), k * (c * x + d * y), k * z)

    def dir(self, n):
        (a, b), (c, d) = self.m
        return (a * n[0] + b * n[1], c * n[0] + d * n[1], n[2])

    def then(self, child):
        (a, b), (c, d) = self.m
        (e, f), (g, h) = child.m
        return _T(((a * e + b * g, a * f + b * h), (c * e + d * g, c * f + d * h)), self.k * child.k, self.pt(*child.t))

    def box(self, x, y, z, w, d, h):
        p, q = self.pt(x, y, z), self.pt(x + w, y + d, z + h)
        return (min(p[0], q[0]), min(p[1], q[1]), p[2], abs(q[0] - p[0]), abs(q[1] - p[1]), q[2] - p[2])


class Anchor:
    """A spot a placed object offers: a seat, a place to stand, a cable peg.
    (x, y, z) in the scene, facing 'r', 'l', 'ul' or 'ur', meta from the model
    (seat=<seat height> for seats)."""
    __slots__ = ("x", "y", "z", "facing", "meta", "name")

    def __init__(self, x, y, z, facing, meta, name):
        self.x, self.y, self.z, self.facing, self.meta, self.name = x, y, z, facing, meta, name

    @property
    def p(self):
        return (self.x, self.y, self.z)

    def __repr__(self):
        return "Anchor(%s %.2f,%.2f,%.2f %s)" % (self.name, self.x, self.y, self.z, self.facing)


class Instance:
    """One placed object (or person): its name in the report and the plan,
    its anchors by name, and its bounding box in the scene."""
    def __init__(self, name, parent):
        self.name, self.parent, self.anchors, self.kind, self.facing = name, parent, {}, "object", None
        self.start, self.bb = 0, None

    def anchor(self, name, i=0):
        return self.anchors[name][i]

    def __repr__(self):
        return "Instance(%s)" % self.name


def _open(sc, base, parent):
    n = sc._names.get(base, 0) + 1
    sc._names[base] = n
    inst = Instance("%s#%d" % (base, n), parent)
    inst.start = len(sc._items)
    return inst


def _close(sc, inst):
    bbs = [it.bb for it in sc._items[inst.start:] if it.bb is not None and it.kind not in ("shadow",)]
    if bbs:
        inst.bb = [min(b[0] for b in bbs), max(b[1] for b in bbs), min(b[2] for b in bbs),
                   max(b[3] for b in bbs), min(b[4] for b in bbs), max(b[5] for b in bbs)]
    sc.instances.append(inst)


def _build(sc, model, T, parent, name, kw):
    inst = _open(sc, name or getattr(model, "__name__", "object"), parent)
    with sc.tag(inst.name):
        model(View(sc, T, inst), **kw)
    _close(sc, inst)
    if parent is not None:                           # a part's anchors belong to the whole too
        for k, v in inst.anchors.items():
            parent.anchors.setdefault(k, []).extend(v)
    return inst


def _library():
    import importlib, os, sys
    here = os.path.dirname(os.path.abspath(__file__))
    if here not in sys.path:
        sys.path.insert(0, here)
    return importlib.import_module("models")


class View:
    """What a model draws on: the same drawing calls as a Scene, in the
    model's own coordinates. Created by Scene.place(); never made by hand."""

    def __init__(self, sc, T, inst):
        self.sc, self.T, self.inst = sc, T, inst
        self.u, self.snap = sc.u, None             # fine detail: models keep exact measures

    def sn(self, v):
        return self.sc.sn(v)

    @property
    def k(self):
        return self.T.k

    def _faces(self, faces):
        if faces is None or faces == "tlr":
            return "tlr"
        if isinstance(faces, str) and "," not in faces and set(faces) <= set("tlr"):
            toks = [{"t": "+z", "l": "+y", "r": "+x"}[c] for c in faces]
        else:
            toks = [t.strip() for t in (faces.split(",") if isinstance(faces, str) else faces)]
        out = ""
        for t in toks:
            side = _VISIBLE.get(self.T.dir(FACE_NORMALS[t]))
            if side and side not in out:
                out += side
        return out

    def box(self, x, y, z, w, d, h, mat, top=None, faces=None, opacity=1, snap=True):
        """faces: None for all, or names ('front,top', '+x,-y', ...)."""
        if snap and self.snap:
            x1, y1, z1 = self.sn(x + w), self.sn(y + d), self.sn(z + h)
            x, y, z = self.sn(x), self.sn(y), self.sn(z)
            w, d, h = max(x1 - x, self.snap), max(y1 - y, self.snap), max(z1 - z, 0)
        it = self.sc.box(*self.T.box(x, y, z, w, d, h), mat, top=top, faces=self._faces(faces), opacity=opacity, snap=False)
        it.local, it.T = (x, y, z, w, d, h), self.T
        return it

    def tile(self, x, y, z, w, d, mat, stroke=True, opacity=1, snap=True):
        if snap and self.snap:
            x1, y1 = self.sn(x + w), self.sn(y + d)
            x, y, z = self.sn(x), self.sn(y), self.sn(z)
            w, d = x1 - x, y1 - y
        X, Y, Z, W, D, _ = self.T.box(x, y, z, w, d, 0)
        it = self.sc.tile(X, Y, Z, W, D, mat, stroke=stroke, opacity=opacity, snap=False)
        it.local, it.T = (x, y, z, w, d, 0), self.T
        return it

    def shadow(self, x, y, w, d, z=0):
        X, Y, Z, W, D, _ = self.T.box(x, y, z, w, d, 0)
        return self.sc.shadow(X, Y, W, D, Z)

    def poly(self, pts, mat, stroke=True, opacity=1, snap=True, inside=None):
        if snap and self.snap:
            pts = [tuple(self.sn(c) for c in q) for q in pts]
        return self.sc.poly([self.T.pt(*q) for q in pts], mat, stroke=stroke, opacity=opacity, snap=False,
                            inside=self.T.pt(*inside) if inside is not None else None)

    def line(self, pts, mat="_ink", width=None, dash=None, opacity=1):
        return self.sc.line([self.T.pt(*q) for q in pts], mat, width, dash, opacity)

    def wire(self, a, b, sag=0.6, mat="wire", width=1.2, n=20):
        return self.sc.wire(self.T.pt(*a), self.T.pt(*b), sag * self.T.k, mat, width, n)

    def cylinder(self, x, y, z, r, h, mat, bands=(), n=28, cap=True):
        k = self.T.k
        X, Y, Z = self.T.pt(x, y, z)
        bands = tuple((self.T.pt(0, 0, b0)[2], self.T.pt(0, 0, b1)[2], m) for b0, b1, m in bands)
        return self.sc.cylinder(X, Y, Z, r * k, h * k, mat, bands=bands, n=n, cap=cap)

    def tower(self, x, y, z, r0, r1, h, mat, bands=(), n=28):
        k = self.T.k
        X, Y, Z = self.T.pt(x, y, z)
        bands = tuple((self.T.pt(0, 0, b0)[2], self.T.pt(0, 0, b1)[2], m) for b0, b1, m in bands)
        return self.sc.tower(X, Y, Z, r0 * k, r1 * k, h * k, mat, bands=bands, n=n)

    def cloud(self, x, y, z, r, mat="white", opacity=0.95):
        return self.sc.cloud(*self.T.pt(x, y, z), r * self.T.k, mat, opacity)

    def mark(self, on, face, shapes):
        return self.sc.mark(on, face, shapes)

    def face_mark(self, x, y, z, side, shapes, on=None):
        U, V = _LEGACY_AXES[side]
        n = {"r": (1, 0, 0), "l": (0, 1, 0), "t": (0, 0, 1)}[side]
        sw = _VISIBLE.get(self.T.dir(n))
        if sw is None:
            return
        self.sc._put_mark(self.T.pt(x, y, z), self.T.vec(*U), self.T.vec(*V), sw, shapes, on)

    def anchor(self, name, x, y, z=0, facing="+x", **meta):
        """Offer a spot: name, its point, which way someone there faces
        ('+x' front, '-x', '+y', '-y'), and meta (seat=<seat height>)."""
        X, Y, Z = self.T.pt(x, y, z)
        f = self.T.dir(FACE_NORMALS[facing])
        if "seat" in meta:
            meta["seat"] *= self.T.k
        a = Anchor(X, Y, Z, _DIR_FACING[(f[0], f[1])], meta, name)
        self.inst.anchors.setdefault(name, []).append(a)
        return a

    def place(self, model, x=0, y=0, z=0, rot=0, mirror=False, scale=1.0, name=None, **kw):
        return _build(self.sc, model, self.T.then(_T.make(x, y, z, rot, mirror, scale)), self.inst, name, kw)

    def person(self, x, y, z=0, facing="r", h=1.0, **kw):
        (fx, fy), (sx, sy) = FACINGS[facing]
        cx, cy = x + (fx * TW / 2 + sx * TD / 2) * h, y + (fy * TW / 2 + sy * TD / 2) * h
        X, Y, Z = self.T.pt(cx, cy, z)
        f = self.T.dir((fx, fy, 0))
        if kw.get("sit"):
            kw["sit"] *= self.T.k
        return self.sc.person_center(X, Y, Z, facing=_DIR_FACING[(f[0], f[1])], h=h * self.T.k, **kw)

    def group(self):
        return self.sc.group()

    def outline(self, key=None):
        return self.sc.outline(key)

    def new_outline(self, name="part"):
        return self.sc.new_outline(name)

    def tag(self, name):
        return self.sc.tag(self.inst.name + " " + name)


class Scene:
    def __init__(self, unit=28, seed=7, sketch=0.5, stroke=1.6, snap=1 / 20, pad=16,
                 background=False):
        self.u, self.seed, self.sketch, self.stroke = unit, seed, sketch, stroke
        self.snap, self.pad, self.background = snap, pad, background
        self.atoms, self._items, self._stack, self._seq, self._last = [], [], [], 0, None
        self._bb = None
        self._tag = None
        self._ol, self._olseq = None, 0
        self.stats = {}
        self.instances, self._names = [], {}

    # ── grid ─────────────────────────────────────────────────────────────
    def sn(self, v):
        return round(v / self.snap) * self.snap if self.snap else v

    def p(self, x, y, z=0):
        u = self.u
        q = ((x - y) * C30 * u, (x + y) * 0.5 * u - z * u)
        bb = self._bb
        if bb is not None:
            if q[0] < bb[0]: bb[0] = q[0]
            if q[1] < bb[1]: bb[1] = q[1]
            if q[0] > bb[2]: bb[2] = q[0]
            if q[1] > bb[3]: bb[3] = q[1]
        return q

    # ── sortable units ───────────────────────────────────────────────────
    def _emit(self, kind, data, bb, facets, boxlike=False):
        it = _Item(kind, data, self._tag)
        it.ol = self._ol
        if self._stack:
            atom = self._stack[-1]; atom.boxlike = False
        else:
            atom = _Atom(self._seq, boxlike); self._seq += 1
            self.atoms.append(atom)
        atom.items.append(it)
        atom.facets.extend(f for f in facets if f is not None)
        G = atom.bb
        G[0] = min(G[0], bb[0]); G[1] = max(G[1], bb[1]); G[2] = min(G[2], bb[2])
        G[3] = max(G[3], bb[3]); G[4] = min(G[4], bb[4]); G[5] = max(G[5], bb[5])
        it.atom = atom
        it.bb = bb
        self._items.append(it)
        self._last = it
        return it

    @contextmanager
    def group(self):
        """Bundle primitives into ONE sortable unit, painted in the order
        written. Only for small props whose parts interpenetrate; separate
        primitives layer better. Nested groups flatten into the outer one."""
        if self._stack:
            yield self._stack[-1]; return
        g = _Atom(self._seq, False); self._seq += 1
        self.atoms.append(g); self._stack.append(g)
        try:
            yield g
        finally:
            self._stack.pop()

    def new_outline(self, name="part"):
        """A key for an outline group, to reuse across several outline() blocks."""
        self._olseq += 1
        return "%s#%d" % (name, self._olseq)

    @contextmanager
    def outline(self, key=None):
        """Parts made inside share ONE border: the ink line runs only round
        the outside of the whole (its silhouette, and where it meets other
        things), not along the seams where its own boxes meet. Use it for
        anything soft or continuous that is modelled from several boxes: a
        hijab, a head of hair, an arm, a tree's crown, a cushion. Pass the
        same key (new_outline()) to join parts made in different places."""
        key = key or self.new_outline()
        old, self._ol = self._ol, key
        try:
            yield key
        finally:
            self._ol = old

    @contextmanager
    def tag(self, name):
        """Label the primitives made inside, for Scene.check() messages."""
        old, self._tag = self._tag, name
        try:
            yield
        finally:
            self._tag = old

    # ── primitives ───────────────────────────────────────────────────────
    def box(self, x, y, z, w, d, h, mat, top=None, faces="tlr", opacity=1, snap=True):
        """Axis-aligned box. mat/top: palette name or '#hex'. Returns a handle
        that mark() and face_mark(on=...) accept."""
        faces = "tlr" if faces is None else faces
        if snap and self.snap:
            x1, y1, z1 = self.sn(x + w), self.sn(y + d), self.sn(z + h)
            x, y, z = self.sn(x), self.sn(y), self.sn(z)
            w, d, h = max(x1 - x, self.snap), max(y1 - y, self.snap), max(z1 - z, 0)
        fs = []
        if h > 0 and "l" in faces:
            fs.append(_plane_facet([(x, y + d, z), (x + w, y + d, z), (x + w, y + d, z + h), (x, y + d, z + h)]))
        if h > 0 and "r" in faces:
            fs.append(_plane_facet([(x + w, y, z), (x + w, y + d, z), (x + w, y + d, z + h), (x + w, y, z + h)]))
        if "t" in faces:
            fs.append(_plane_facet([(x, y, z + h), (x + w, y, z + h), (x + w, y + d, z + h), (x, y + d, z + h)]))
        it = self._emit("box", (x, y, z, w, d, h, mat, top, faces, opacity),
                        (x, x + w, y, y + d, z, z + h), fs, boxlike=True)
        it.box = (x, y, z, w, d, h, faces)
        it.local, it.T = (x, y, z, w, d, h), _T()
        return it

    def tile(self, x, y, z, w, d, mat, stroke=True, opacity=1, snap=True):
        """Flat horizontal quad (floors, rugs, road paint)."""
        if snap and self.snap:
            x1, y1 = self.sn(x + w), self.sn(y + d)
            x, y, z = self.sn(x), self.sn(y), self.sn(z)
            w, d = x1 - x, y1 - y
        f = _plane_facet([(x, y, z), (x + w, y, z), (x + w, y + d, z), (x, y + d, z)])
        it = self._emit("tile", (x, y, z, w, d, mat, stroke, opacity), (x, x + w, y, y + d, z, z), [f], boxlike=True)
        it.box = (x, y, z, w, d, 0, "t")
        it.local, it.T = (x, y, z, w, d, 0), _T()
        return it

    def shadow(self, x, y, w, d, z=0):
        f = _plane_facet([(x, y, z), (x + w, y, z), (x + w, y + d, z), (x, y + d, z)])
        return self._emit("shadow", (x, y, z, w, d), (x, x + w, y, y + d, z, z), [f], boxlike=True)

    def poly(self, pts, mat, stroke=True, opacity=1, snap=True, inside=None):
        """Any planar 3D polygon (roof slopes, gables, signs). Shaded
        automatically from its normal. With inside=<a point inside the solid
        it bounds>, it is drawn only while it faces the viewer (for prisms
        such as wheels, which turn with their object)."""
        if snap and self.snap:
            pts = [tuple(self.sn(c) for c in q) for q in pts]
        if inside is not None and not _faces_viewer(pts, inside):
            return None
        xs, ys, zs = zip(*pts)
        return self._emit("poly", (pts, mat, stroke, opacity), (min(xs), max(xs), min(ys), max(ys), min(zs), max(zs)),
                          [_plane_facet(pts)])

    def line(self, pts, mat="_ink", width=None, dash=None, opacity=1):
        """3D polyline (rails, masts, handles, lattice members). Long lines
        that weave between objects should be split: see wire()."""
        xs, ys, zs = zip(*pts)
        hw = (width or self.stroke) / 2 / self.u
        fs = [_seg_facet(pts[i], pts[i + 1], hw) for i in range(len(pts) - 1)]
        return self._emit("line", (pts, mat, width, dash, opacity), (min(xs), max(xs), min(ys), max(ys), min(zs), max(zs)), fs)

    def wire(self, a, b, sag=0.6, mat="wire", width=1.2, n=20):
        """Sagging cable from a to b, split into n units so each piece layers
        on its own (in front of one pylon leg, behind the next)."""
        pts = []
        for i in range(n + 1):
            f = i / n
            q = [a[j] + (b[j] - a[j]) * f for j in range(3)]
            q[2] -= sag * 4 * f * (1 - f)
            pts.append(tuple(q))
        for i in range(n):
            self.line([pts[i], pts[i + 1]], mat, width)

    def _round_facets(self, x, y, z, prof, k=8):
        """Facets of the visible half of a round solid. prof: [(r, z), ...]."""
        fs = []
        angs = [-math.pi / 4 + math.pi * i / k for i in range(k + 1)]
        for (ra, za), (rb, zb) in zip(prof, prof[1:]):
            for a0, a1 in zip(angs, angs[1:]):
                fs.append(_plane_facet([(x + ra * math.cos(a0), y + ra * math.sin(a0), za),
                                        (x + ra * math.cos(a1), y + ra * math.sin(a1), za),
                                        (x + rb * math.cos(a1), y + rb * math.sin(a1), zb),
                                        (x + rb * math.cos(a0), y + rb * math.sin(a0), zb)]))
        rt, zt = prof[-1]
        fs.append(_plane_facet([(x + rt * math.cos(i * math.pi / 6), y + rt * math.sin(i * math.pi / 6), zt) for i in range(12)]))
        return fs

    def cylinder(self, x, y, z, r, h, mat, bands=(), n=28, cap=True):
        """Vertical cylinder centred at (x,y). bands=[(z0, z1, mat), ...] paints
        stripes (chimney bands, pipe rings) in world z."""
        return self._emit("cyl", (x, y, z, r, h, mat, n, 0, tuple(bands), cap), (x - r, x + r, y - r, y + r, z, z + h),
                          self._round_facets(x, y, z, [(r, z), (r, z + h)]))

    def tower(self, x, y, z, r0, r1, h, mat, bands=(), n=28):
        """Cooling tower: r0 at the base, waist 0.86*r1 at 2/3 h, lip r1, hollow top."""
        R = max(r0, r1)
        return self._emit("cyl", (x, y, z, r0, h, mat, n, r1, tuple(bands), True), (x - R, x + R, y - R, y + R, z, z + h),
                          self._round_facets(x, y, z, [(r0, z), (r1 * 0.86, z + h * 0.66), (r1, z + h)]))

    def cloud(self, x, y, z, r, mat="white", opacity=0.95):
        """Steam/smoke puff of overlapping circles, outlined as one shape."""
        e1 = (1 / math.sqrt(2), -1 / math.sqrt(2), 0.0)
        e2 = (1 / math.sqrt(6), 1 / math.sqrt(6), -2 / math.sqrt(6))
        R = r * 1.25 / 1.2247
        disk = [(x + R * (math.cos(t) * e1[0] + math.sin(t) * e2[0]), y + R * (math.cos(t) * e1[1] + math.sin(t) * e2[1]),
                 z + R * (math.cos(t) * e1[2] + math.sin(t) * e2[2])) for t in (i * math.pi / 6 for i in range(12))]
        return self._emit("cloud", (x, y, z, r, mat, opacity), (x - r, x + r, y - r, y + r, z - r * 0.5, z + r),
                          [_plane_facet(disk)])

    def _find_face(self, A, side, U, V):
        """The latest box (or tile) whose drawn `side` face holds the anchor A,
        nudged a little into the face along U and V."""
        t = 1e-4
        nu = [(1 if c > 0 else -1 if c < 0 else 0) * 2e-3 for c in U]
        nv = [(1 if c > 0 else -1 if c < 0 else 0) * 2e-3 for c in V]
        x, y, z = (A[i] + nu[i] + nv[i] for i in range(3))
        for it in reversed(self._items):
            b = it.box
            if b is None:
                continue
            bx, by, bz, w, d, h, faces = b
            if side not in faces:
                continue
            if side == "r":
                if abs(A[0] - (bx + w)) < t and by - t <= y <= by + d + t and bz - t <= z <= bz + h + t:
                    return it
            elif side == "l":
                if abs(A[1] - (by + d)) < t and bx - t <= x <= bx + w + t and bz - t <= z <= bz + h + t:
                    return it
            elif abs(A[2] - (bz + h)) < t and bx - t <= x <= bx + w + t and by - t <= y <= by + d + t:
                return it
        return None

    def face_mark(self, x, y, z, side, shapes, on=None):
        """2D detail painted on a box face, by world coordinates (the older
        form; inside objects prefer mark()). It layers with the face it sits
        on: `on` (a handle from box()/tile()), else the box whose `side` face
        contains (x, y, z), else the latest primitive.
        side 'r' = plane x=const (a runs +y), 'l' = plane y=const (a runs +x),
        't' = plane z=const (a runs +x, b runs +y). b runs up for r/l.
        shapes (a,b in world units on the face):
          ('rect', a, b, w, h, mat[, opacity])
          ('poly', [(a,b),...], mat[, opacity])
          ('line', [(a,b),...], mat, width)
          ('ell',  a, b, ra, rb, mat[, opacity])        filled ellipse
          ('ring', a, b, ra, rb, mat, width)
          ('arc',  a, b, w, depth, mat, width)          smile/curve
        mat: palette name, '#hex', '_ink', '_face', or '!name' (emissive:
        not darkened by the face shading, e.g. '!light_on' lit windows)."""
        U, V = _LEGACY_AXES[side]
        self._put_mark((x, y, z), U, V, side, shapes, on)

    def _put_mark(self, A, U, V, side, shapes, on):
        it = on or self._find_face(A, side, U, V) or self._last
        if it is None:
            it = self._emit("none", None, (A[0], A[0], A[1], A[1], A[2], A[2]), [])
        it.marks.append((tuple(A), tuple(U), tuple(V), side, shapes))

    def mark(self, on, face, shapes):
        """Details on one face of a box (or the top of a tile), in the face's
        own frame: `a` runs left to right and `b` up, both from the face's
        lower-left corner as you look at that face. face: 'front' (+x),
        'back' (-x), 'left' (+y), 'right' (-y), 'top' (+z), or '+x'... '+z'.
        On 'top', a runs along +x and b along +y. The marks turn with a placed
        object and are drawn only while their face looks at the viewer.
        Shapes as in face_mark()."""
        n = FACE_NORMALS[face]
        A, U, V = _face_frame(on.local, n)
        T = on.T
        nw = T.dir(n)
        side = _VISIBLE.get(nw)
        if side is None:
            return                                  # that face is turned away
        self._put_mark(T.pt(*A), T.vec(*U), T.vec(*V), side, shapes, on)

    # ── objects: build once in their own space, then place ───────────────
    def place(self, model, x=0, y=0, z=0, rot=0, mirror=False, scale=1.0, name=None, **kw):
        """Build `model(m, **kw)` in its own coordinates and put it here.
        The model draws on `m` exactly as on a scene (box, mark, cylinder,
        anchor, place, ...) with its origin at its footprint's back corner
        and its front facing +x. rot turns it about z in 90-degree steps
        (90: front faces +y, 180: -x, 270: -y); mirror flips it across its
        own x axis first; scale grows it. Every part still sorts on its own,
        so the object sits in the scene (a person on its seat, an arm in
        front of its counter). Returns an Instance with .anchors and .bb."""
        T = _T.make(self.sn(x), self.sn(y), self.sn(z), rot, mirror, scale)    # the spot snaps to the grid
        return _build(self, model, T, None, name, kw)

    def person_at(self, anchor, **kw):
        """Put a person on an anchor from a placed object: centred on the
        spot, facing the anchor's way, sitting if the anchor has a `seat`
        height. Any person() option can follow."""
        if anchor.meta.get("seat") and "sit" not in kw:
            kw["sit"] = anchor.meta["seat"]
        kw.setdefault("facing", anchor.facing)
        return self.person_center(anchor.x, anchor.y, anchor.z, **kw)

    def person_center(self, cx, cy, z=0, facing="r", h=1.0, **kw):
        """person() by the centre of the torso instead of its corner."""
        (fx, fy), (sx, sy) = FACINGS[facing]
        X = cx - (fx * TW / 2 + sx * TD / 2) * h
        Y = cy - (fy * TW / 2 + sy * TD / 2) * h
        return self.person(X, Y, z, facing=facing, h=h, **kw)

    # ── reusable props ───────────────────────────────────────────────────
    def tree(self, x, y, z=0, kind="round", s=1.0, leaf="leaf"):
        """A voxel tree centred on (x, y): models.tree placed for you."""
        m = _library()
        return self.place(m.tree, x - 0.55 * s, y - 0.55 * s, z, kind=kind, size=s, leaf=leaf)

    def bench(self, x, y, z=0, length=1.8, facing="l", seat=0.6, mat="wood", leg="steel"):
        """models.bench placed with its seats facing `facing` ('r' or 'l'),
        backrest on the far side, from the corner (x, y). Seat people with
        s.person_at(bench.anchors["seat"][i])."""
        m = _library()
        if facing == "r":
            return self.place(m.bench, x, y, z, rot=0, length=length, seat=seat, mat=mat, leg=leg)
        return self.place(m.bench, x + length, y, z, rot=90, length=length, seat=seat, mat=mat, leg=leg)

    # ── character ────────────────────────────────────────────────────────
    def person(self, x, y, z=0, *, facing="r", h=1.0, skin="skin1", hair="hair1",
               hair_style="short", top="blue", outfit="tee", inner="shirt", sleeve=None,
               tie=None, bottom="pants", skirt=None, shoe="shoe", eyes="dot", mouth="smile",
               brows=True, blush=False, glasses=None, beard=None, carry=None, carry_color="gold",
               hat=None, walk=0.0, sit=None, pose="down", holding=None, hold_color=None):
        """Blocky character. See references/characters.md for every option.
        (x, y, z) is the back corner of the body's footprint; z is the floor,
        or the seat top when sit=<seat height>. The body is about 0.75 x 0.7
        units on the floor and 2.5 units tall at h=1. Every part is its own
        sortable unit and no two parts pass through each other."""
        inst = _open(self, "person", None)
        inst.kind, inst.facing = "person", facing
        _person(self, x, y, z, dict(facing=facing, h=h, skin=skin, hair=hair, hair_style=hair_style, top=top,
                                    outfit=outfit, inner=inner, sleeve=sleeve, tie=tie, bottom=bottom, skirt=skirt,
                                    shoe=shoe, eyes=eyes, mouth=mouth, brows=brows, blush=blush, glasses=glasses,
                                    beard=beard, carry=carry, carry_color=carry_color, hat=hat, walk=walk, sit=sit,
                                    pose=pose, holding=holding, hold_color=hold_color))
        _close(self, inst)
        return inst

    # ── ordering ─────────────────────────────────────────────────────────
    def _order(self):
        A = [a for a in self.atoms if a.items]
        n = len(A)
        for a in A:
            if a.facets:
                xs0, ys0, xs1, ys1 = zip(*(f.bb for f in a.facets))
                a.sbb = (min(xs0), min(ys0), max(xs1), max(ys1))
            else:
                a.sbb = None
        succ = [[] for _ in range(n)]
        indeg = [0] * n
        idx = sorted((i for i in range(n) if A[i].sbb), key=lambda i: A[i].sbb[0])
        pairs = exact = 0
        for p in range(len(idx)):
            i = idx[p]; ai = A[i]; si = ai.sbb
            for q in range(p + 1, len(idx)):
                j = idx[q]; aj = A[j]; sj = aj.sbb
                if sj[0] >= si[2]:
                    break
                if sj[1] >= si[3] or si[1] >= sj[3]:
                    continue
                r = _behind(ai.bb, aj.bb)
                if ai.boxlike and aj.boxlike:
                    if not _hex_overlap(ai.bb, aj.bb):
                        continue
                    if r == 0:
                        exact += 1; v = _compare(ai, aj)
                        if v is None:
                            continue
                        r = 1 if v > 0 else -1 if v < 0 else 0
                elif r != 0:
                    if _compare(ai, aj, early=True) is None:
                        continue
                else:
                    exact += 1; v = _compare(ai, aj)
                    if v is None:
                        continue
                    r = 1 if v > 0 else -1 if v < 0 else 0
                if r == 0:                              # coplanar: author order wins
                    r = -1 if ai.seq < aj.seq else 1
                pairs += 1
                if r < 0:
                    succ[i].append(j); indeg[j] += 1
                else:
                    succ[j].append(i); indeg[i] += 1
        heap = [(A[i].seq, i) for i in range(n) if indeg[i] == 0]
        heapq.heapify(heap)
        done, out, cycles = [False] * n, [], 0
        self.cycle_units = []
        while len(out) < n:
            if not heap:   # cyclic overlap: release the furthest-back unit
                cycles += 1
                k = min((i for i in range(n) if not done[i]),
                        key=lambda i: (indeg[i], A[i].bb[1] + A[i].bb[3] + A[i].bb[5], A[i].seq))
                indeg[k] = 0
                heap.append((A[k].seq, k))
                self.cycle_units.append(A[k])
            _, i = heapq.heappop(heap)
            if done[i]:
                continue
            done[i] = True; out.append(A[i])
            for j in succ[i]:
                indeg[j] -= 1
                if indeg[j] == 0 and not done[j]:
                    heapq.heappush(heap, (A[j].seq, j))
        self.stats = {"units": n, "pairs": pairs, "exact_tests": exact, "cycles": cycles}
        return out

    def check(self, tol=0.01):
        """Pairs of boxes that pass through each other by more than tol on
        every axis (outside groups). Each one is a layering risk: move or
        trim a part until the list is empty."""
        boxes = [a for a in self.atoms if a.boxlike and a.items and a.items[0].kind == "box"
                 and a.items[0].box[5] > tol]
        boxes.sort(key=lambda a: a.bb[0])
        bad = []
        for p in range(len(boxes)):
            a = boxes[p]
            for q in range(p + 1, len(boxes)):
                b = boxes[q]
                if b.bb[0] >= a.bb[1] - tol:
                    break
                if all(min(a.bb[k + 1], b.bb[k + 1]) - max(a.bb[k], b.bb[k]) > tol for k in (0, 2, 4)):
                    bad.append((_desc(a.items[0]), _desc(b.items[0])))
        return bad

    # ── rendering ────────────────────────────────────────────────────────
    def _c(self, m):
        pal = self._pal
        if m is None:
            return None
        if isinstance(m, tuple):
            base = self._c(m[1]); return shade(base, m[2])
        if m.startswith("#"):
            return m
        if m.startswith("!"):
            return pal[m[1:]]
        return pal[m]

    def _pts(self, pts):
        j, sd = self.sketch, self.seed
        out = []
        for (a, b) in pts:
            if j:
                da, db = _jit(a, b, sd, j); out.append((a + da, b + db))
            else:
                out.append((a, b))
        return out

    def _face_svg(self, pts, fill, op=1, stroke=True):
        q = " ".join("%.1f,%.1f" % t for t in self._pts(pts))
        st = ' class="k"' if stroke else ""          # .k = the ink outline, defined once in <style>
        return '<polygon points="%s" fill="%s"%s%s/>' % (q, fill, st, "" if op == 1 else ' fill-opacity="%.2f"' % op)

    def _face(self, it, k, wpts, fill, op=1, stroke=True):
        """One face from world points. Outside an outline group: filled and
        fully bordered. Inside one: filled, then bordered only along the
        stretches of its edges that are the group's silhouette."""
        if it.ol is None or not stroke:
            return self._face_svg([self.p(*q) for q in wpts], fill, op, stroke)
        scr = self._pts([self.p(*q) for q in wpts])
        opa = "" if op == 1 else ' fill-opacity="%.2f"' % op
        seam = (' stroke="%s" stroke-width="0.7"' % fill) if op == 1 else ""      # close anti-aliasing gaps
        out = ['<polygon points="%s" fill="%s"%s%s/>' % (_pl(scr), fill, seam, opa)]
        n = len(scr)
        for i, t0, t1 in self._silhouette(it, k, wpts):
            (ax, ay), (bx, by) = scr[i], scr[(i + 1) % n]
            out.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" class="k"/>'
                       % (ax + (bx - ax) * t0, ay + (by - ay) * t0, ax + (bx - ax) * t1, ay + (by - ay) * t1))
        return "".join(out)

    def _group_faces(self, ol):
        if self._olfaces is None:
            self._olfaces = {}
            for it2 in self._items:
                if it2.ol is None:
                    continue
                if it2.kind == "box":
                    wfs = [wp[1] for wp in _box_faces(it2.data)]
                elif it2.kind == "tile":
                    x, y, z, w, dd = it2.data[:5]
                    wfs = [[(x, y, z), (x + w, y, z), (x + w, y + dd, z), (x, y + dd, z)]]
                elif it2.kind == "poly":
                    wfs = [it2.data[0]]
                else:
                    continue
                for k2, wp in enumerate(wfs):
                    f = _plane_facet(wp)
                    if f is not None:
                        self._olfaces.setdefault(it2.ol, []).append(((id(it2), k2), f))
        return self._olfaces.get(ol, [])

    def _silhouette(self, it, k, wpts):
        """Stretches (edge index, t0, t1) of a face's edges where the shape
        meets the outside: just across the edge there is no face of the same
        outline group continuing the surface (same depth at the edge)."""
        me = _plane_facet(wpts)
        poly = [_S(*q) for q in wpts]
        n = len(poly)
        if me is None:
            return [(i, 0.0, 1.0) for i in range(n)]
        others = [f for key, f in self._group_faces(it.ol) if key != (id(it), k)]
        eps = 1.4 / self.u
        out = []
        for i in range(n):
            (ax, ay), (bx, by) = poly[i], poly[(i + 1) % n]
            L = math.hypot(bx - ax, by - ay)
            if L < 1e-9:
                continue
            nx, ny = (by - ay) / L, -(bx - ax) / L
            mx, my = (ax + bx) / 2 + nx * eps, (ay + by) / 2 + ny * eps
            if _inside(me.poly, mx, my):
                nx, ny = -nx, -ny
            N = max(3, int(L * self.u / 3))
            run = None
            for j in range(N):
                t = (j + 0.5) / N
                qx, qy = ax + (bx - ax) * t + nx * eps, ay + (by - ay) * t + ny * eps
                d0 = me.depth(qx, qy)
                cont = False
                for f in others:
                    b = f.bb
                    if b[0] <= qx <= b[2] and b[1] <= qy <= b[3] and _inside(f.poly, qx, qy) and abs(f.depth(qx, qy) - d0) < 0.12:
                        cont = True
                        break
                if not cont:
                    run = (j / N if run is None else run[0], (j + 1) / N)
                elif run is not None:
                    out.append((i,) + run); run = None
            if run is not None:
                out.append((i,) + run)
        return out

    def _render(self, theme, grid_overlay=False):
        pal = PALETTES[theme]
        self._pal, self._ink, self._iop = pal, pal["_ink"], pal["_ink_op"]
        st, sl, sr = pal["_shade"]
        self._bb = [1e9, 1e9, -1e9, -1e9]
        self._olfaces = None
        o = []
        P = self.p
        for g in self._order():
            for it in g.items:
                kind, d = it.kind, it.data
                if kind == "box":
                    x, y, z, w, dd, h, mat, top, faces, op = d
                    c = self._c(mat); ct = self._c(top) or c
                    for k_, wp in enumerate(_box_faces(d)):
                        fill = shade(ct, st) if wp[0] == "t" else shade(c, sl if wp[0] == "l" else sr)
                        o.append(self._face(it, k_, wp[1], fill, op))
                elif kind == "tile":
                    x, y, z, w, dd, mat, strk, op = d
                    o.append(self._face(it, 0, [(x, y, z), (x + w, y, z), (x + w, y + dd, z), (x, y + dd, z)], self._c(mat), op, strk))
                elif kind == "shadow":
                    x, y, z, w, dd = d
                    q = " ".join("%.1f,%.1f" % P(*t) for t in [(x, y, z), (x + w, y, z), (x + w, y + dd, z), (x, y + dd, z)])
                    o.append('<polygon points="%s" fill="%s" fill-opacity="%.2f"/>' % (q, pal["_shadow"], pal["_shadow_op"]))
                elif kind == "line":
                    pts, mat, width, dash, op = d
                    col = self._c(mat); aop = self._iop if mat == "_ink" else 1
                    q = " ".join("%.1f,%.1f" % P(*t) for t in pts)
                    o.append('<polyline points="%s" fill="none" stroke="%s" stroke-opacity="%.2f" stroke-width="%.2f"%s/>'
                             % (q, col, aop * op, width or self.stroke, ' stroke-dasharray="%s"' % dash if dash else ""))
                elif kind == "poly":
                    pts, mat, strk, op = d
                    o.append(self._face(it, 0, pts, shade(self._c(mat), _normal_shade(pts, st, sl, sr)), op, strk))
                elif kind == "cyl":
                    o.append(self._cyl(*d))
                elif kind == "cloud":
                    o.append(self._cloud(*d))
                for m in it.marks:
                    o.append(self._marks(*m, shade_k={"r": sr, "l": sl, "t": st}[m[3]]))
        if grid_overlay:
            o.append(self._grid_svg())
        bb, self._bb = self._bb, None
        pd = self.pad + self.stroke
        view = (math.floor(bb[0] - pd), math.floor(bb[1] - pd), math.ceil(bb[2] - bb[0] + 2 * pd), math.ceil(bb[3] - bb[1] + 2 * pd))
        return "".join(o), view

    def svg(self, theme="light", title="Illustration", desc="", view=None, grid_overlay=False):
        body, v = self._render(theme, grid_overlay)
        return _wrap(body, view or v, theme, title, desc, self.background, self._style(theme))

    def _style(self, theme):
        pal = PALETTES[theme]
        return ".k{stroke:%s;stroke-opacity:%.2f;stroke-width:%.2f}" % (pal["_ink"], pal["_ink_op"], self.stroke)

    def _marks(self, A, U, V, side, shapes, shade_k=1.0):
        ax, ay, az = A
        ux, uy, uz = U
        vx, vy, vz = V

        def P(a, b):
            return self.p(ax + a * ux + b * vx, ay + a * uy + b * vy, az + a * uz + b * vz)

        def col(m):
            if m in ("_face", "_ink"):
                return self._pal[m]
            if isinstance(m, str) and (m.startswith("!") or m.startswith("#")):
                return self._c(m)
            return shade(self._c(m), shade_k)

        def ell_pts(a, b, ra, rb, n=18):
            return [P(a + ra * math.cos(t * 2 * math.pi / n), b + rb * math.sin(t * 2 * math.pi / n)) for t in range(n)]

        out = []
        for s in shapes:
            k = s[0]
            if k == "rect":
                _, a, b, w, h, m, *op = s
                q = [P(a, b), P(a + w, b), P(a + w, b + h), P(a, b + h)]
                out.append('<polygon points="%s" fill="%s"%s/>' % (_pl(q), col(m), ' fill-opacity="%.2f"' % op[0] if op else ""))
            elif k == "poly":
                _, pts, m, *op = s
                out.append('<polygon points="%s" fill="%s"%s/>' % (_pl([P(a, b) for a, b in pts]), col(m), ' fill-opacity="%.2f"' % op[0] if op else ""))
            elif k == "line":
                _, pts, m, w = s
                out.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="%.2f"/>' % (_pl([P(a, b) for a, b in pts]), col(m), w))
            elif k == "ell":
                _, a, b, ra, rb, m, *op = s
                out.append('<polygon points="%s" fill="%s"%s/>' % (_pl(ell_pts(a, b, ra, rb)), col(m), ' fill-opacity="%.2f"' % op[0] if op else ""))
            elif k == "ring":
                _, a, b, ra, rb, m, w = s
                out.append('<polygon points="%s" fill="none" stroke="%s" stroke-width="%.2f"/>' % (_pl(ell_pts(a, b, ra, rb, 24)), col(m), w))
            elif k == "arc":
                _, a, b, w, dep, m, wd = s
                p0, pm, p1 = P(a - w / 2, b), P(a, b - dep * 2), P(a + w / 2, b)
                out.append('<path d="M%.1f %.1f Q%.1f %.1f %.1f %.1f" fill="none" stroke="%s" stroke-width="%.2f"/>' % (*p0, *pm, *p1, col(m), wd))
        return "".join(out)

    def _cyl(self, x, y, z, r, h, mat, n, r1, bands, cap):
        st, sl, sr = self._pal["_shade"]
        ink, iop, sw = self._ink, self._iop, self.stroke
        base = self._c(mat)
        tower = bool(r1)
        prof = [(r, z), (r1 * 0.86, z + h * 0.66), (r1, z + h)] if tower else [(r, z), (r, z + h)]
        zs = sorted(set([q[1] for q in prof] + [b for b0, b1, _ in bands for b in (b0, b1) if z < b < z + h]))

        def rad(zz):
            for (ra, za), (rb, zb) in zip(prof, prof[1:]):
                if za <= zz <= zb:
                    return ra + (rb - ra) * (zz - za) / (zb - za)
            return prof[-1][0]

        def mat_at(zz):
            for b0, b1, m in bands:
                if b0 <= zz < b1:
                    return self._c(m)
            return base

        out = []
        n = max(8, min(n, 2 * round(max(r, r1) * self.u * 0.45)))     # detail follows the drawn size
        m = n // 2
        angs = [-math.pi / 4 + math.pi * i / m for i in range(m + 1)]
        for za, zb in zip(zs, zs[1:]):
            c = mat_at((za + zb) / 2)
            ra, rb = rad(za), rad(zb)
            for i in range(m):
                a0, a1 = angs[i], angs[i + 1]
                am = (a0 + a1) / 2
                k = sl + (sr - sl) * ((math.cos(am) - math.sin(am)) / 2 + 0.5)
                col = shade(c, k)
                q = [self.p(x + ra * math.cos(a0), y + ra * math.sin(a0), za), self.p(x + ra * math.cos(a1), y + ra * math.sin(a1), za),
                     self.p(x + rb * math.cos(a1), y + rb * math.sin(a1), zb), self.p(x + rb * math.cos(a0), y + rb * math.sin(a0), zb)]
                out.append('<polygon points="%s" fill="%s" stroke="%s" stroke-width="0.6"/>' % (_pl(q), col, col))
            if za != z and any(abs(za - b) < 1e-9 for b0, b1, _ in bands for b in (b0, b1)):
                out.append('<polyline points="%s" fill="none" stroke="%s" stroke-opacity="%.2f" stroke-width="%.2f"/>'
                           % (_pl([self.p(x + ra * math.cos(a), y + ra * math.sin(a), za) for a in angs]), ink, iop * 0.6, sw * 0.6))
        for a in (angs[0], angs[-1]):
            out.append('<polyline points="%s" fill="none" stroke="%s" stroke-opacity="%.2f" stroke-width="%.2f"/>'
                       % (_pl([self.p(x + rr * math.cos(a), y + rr * math.sin(a), zz) for rr, zz in prof]), ink, iop, sw))
        out.append('<polyline points="%s" fill="none" stroke="%s" stroke-opacity="%.2f" stroke-width="%.2f"/>'
                   % (_pl([self.p(x + r * math.cos(a), y + r * math.sin(a), z) for a in angs]), ink, iop, sw))
        if cap:
            rt = prof[-1][0]; zt = z + h
            ring = [self.p(x + rt * math.cos(i * 2 * math.pi / n), y + rt * math.sin(i * 2 * math.pi / n), zt) for i in range(n)]
            out.append('<polygon points="%s" fill="%s" stroke="%s" stroke-opacity="%.2f" stroke-width="%.2f"/>'
                       % (_pl(ring), shade(mat_at(zt - 1e-6), st), ink, iop, sw))
            if tower:
                ri = rt * 0.82
                inner = [self.p(x + ri * math.cos(i * 2 * math.pi / n), y + ri * math.sin(i * 2 * math.pi / n), zt) for i in range(n)]
                out.append('<polygon points="%s" fill="%s" stroke="%s" stroke-opacity="%.2f" stroke-width="%.2f"/>'
                           % (_pl(inner), shade(base, 0.55), ink, iop * 0.6, sw * 0.7))
        return "".join(out)

    def _cloud(self, x, y, z, r, mat, op):
        cx, cy = self.p(x, y, z)
        R = r * self.u
        circ = [(cx - R * 0.75, cy + R * 0.15, R * 0.62), (cx + R * 0.7, cy + R * 0.2, R * 0.66),
                (cx - R * 0.1, cy - R * 0.3, R * 0.85), (cx + R * 0.15, cy + R * 0.3, R * 0.6)]
        bb = self._bb
        for a, b, rr in circ:
            bb[0] = min(bb[0], a - rr); bb[1] = min(bb[1], b - rr); bb[2] = max(bb[2], a + rr); bb[3] = max(bb[3], b + rr)
        c = self._c(mat); st = self._pal["_shade"][0]
        out = ['<circle cx="%.1f" cy="%.1f" r="%.1f" fill="none" stroke="%s" stroke-opacity="%.2f" stroke-width="%.2f"/>'
               % (a, b, rr, self._ink, self._iop * op, self.stroke * 2) for a, b, rr in circ]
        out += ['<circle cx="%.1f" cy="%.1f" r="%.1f" fill="%s" fill-opacity="%.2f"/>' % (a, b, rr, shade(c, st), op) for a, b, rr in circ]
        out.append('<circle cx="%.1f" cy="%.1f" r="%.1f" fill="%s" fill-opacity="%.2f"/>' % (cx + R * 0.15, cy + R * 0.25, R * 0.45, shade(c, 0.94), op * 0.6))
        return "".join(out)

    def plan_svg(self, u=30):
        """A top-down plan for arranging the scene: every placed object's
        footprint with its name, people with an arrow for where they face,
        anchors as dots, the 1-unit grid with coordinates. Turned like the
        drawing (x to the lower right, y to the lower left), not squashed."""
        k = 0.7071 * u
        P = lambda x, y: ((x - y) * k, (x + y) * k)
        xs, ys = [], []
        for it in self._items:
            if it.bb is not None and it.kind != "none":
                xs += [it.bb[0], it.bb[1]]; ys += [it.bb[2], it.bb[3]]
        if not xs:
            return '<svg xmlns="http://www.w3.org/2000/svg"/>'
        x0, x1, y0, y1 = math.floor(min(xs)), math.ceil(max(xs)), math.floor(min(ys)), math.ceil(max(ys))
        o = []
        for it in self._items:                          # the ground, faintly
            if it.kind == "tile" and it.bb[4] <= 0.05:
                bx0, bx1, by0, by1 = it.bb[:4]
                o.append('<polygon points="%s" fill="#E3EAF7" stroke="none"/>' % _pl([P(bx0, by0), P(bx1, by0), P(bx1, by1), P(bx0, by1)]))
        g = []
        for x in range(x0, x1 + 1):
            g.append("M%.1f %.1fL%.1f %.1f" % (*P(x, y0), *P(x, y1)))
        for y in range(y0, y1 + 1):
            g.append("M%.1f %.1fL%.1f %.1f" % (*P(x0, y), *P(x1, y)))
        o.append('<path d="%s" stroke="#C8D4E8" stroke-width="0.8" fill="none"/>' % "".join(g))
        lab = 'font-family="DejaVu Sans, Arial, sans-serif" font-size="%d" fill="%s" text-anchor="middle"'
        for x in range(x0, x1 + 1, 2 if x1 - x0 > 16 else 1):
            q = P(x, y0 - 0.6)
            o.append('<text x="%.1f" y="%.1f" %s>x%d</text>' % (q[0], q[1], lab % (10, "#4C5B76"), x))
        for y in range(y0, y1 + 1, 2 if y1 - y0 > 16 else 1):
            q = P(x0 - 0.6, y)
            o.append('<text x="%.1f" y="%.1f" %s>y%d</text>' % (q[0], q[1], lab % (10, "#4C5B76"), y))
        dirs = {"r": (1, 0), "l": (0, 1), "ul": (-1, 0), "ur": (0, -1)}
        tops = [i for i in self.instances if i.parent is None and i.bb]
        for inst in sorted(tops, key=lambda i: i.kind == "person"):
            bx0, bx1, by0, by1, bz0, bz1 = inst.bb
            poly = _pl([P(bx0, by0), P(bx1, by0), P(bx1, by1), P(bx0, by1)])
            c = P((bx0 + bx1) / 2, (by0 + by1) / 2)
            if inst.kind == "person":
                o.append('<polygon points="%s" fill="#F29C9C" fill-opacity="0.7" stroke="#C6382F" stroke-width="1"/>' % poly)
                dx, dy = dirs[inst.facing]
                cx, cy = (bx0 + bx1) / 2, (by0 + by1) / 2
                a, b = P(cx, cy), P(cx + dx * 0.6, cy + dy * 0.6)
                o.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="#C6382F" stroke-width="2"/>' % (*a, *b))
                o.append('<circle cx="%.1f" cy="%.1f" r="2.5" fill="#C6382F"/>' % b)
                o.append('<text x="%.1f" y="%.1f" %s>%s</text>' % (c[0], c[1] - 8, lab % (9, "#7A1F1F"), inst.name))
            else:
                o.append('<polygon points="%s" fill="#BFD5F7" fill-opacity="0.55" stroke="#14203A" stroke-width="1.2"/>' % poly)
                o.append('<text x="%.1f" y="%.1f" %s>%s</text>' % (c[0], c[1], lab % (11, "#14203A"), inst.name))
                o.append('<text x="%.1f" y="%.1f" %s>h %.1f</text>' % (c[0], c[1] + 12, lab % (9, "#4C5B76"), bz1))
                for name, lst in inst.anchors.items():
                    for an in lst:
                        q = P(an.x, an.y)
                        dx, dy = dirs[an.facing]
                        r = P(an.x + dx * 0.35, an.y + dy * 0.35)
                        o.append('<circle cx="%.1f" cy="%.1f" r="3" fill="#B45309"/>' % q)
                        o.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="#B45309" stroke-width="1.5"/>' % (*q, *r))
                        o.append('<text x="%.1f" y="%.1f" %s>%s</text>' % (q[0], q[1] - 5, lab % (8, "#B45309"), name))
        pts = [P(x0 - 1.2, y0 - 1.2), P(x1 + 1, y0), P(x1 + 1, y1 + 1), P(x0, y1 + 1)]
        vx0, vx1 = min(p[0] for p in pts), max(p[0] for p in pts)
        vy0, vy1 = min(p[1] for p in pts), max(p[1] for p in pts)
        return ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="%d %d %d %d" width="%d" height="%d">'
                '<rect x="%d" y="%d" width="%d" height="%d" fill="#FFFFFF"/>%s</svg>'
                % (vx0, vy0, vx1 - vx0, vy1 - vy0, vx1 - vx0, vy1 - vy0, vx0, vy0, vx1 - vx0, vy1 - vy0, "".join(o)))

    def _grid_svg(self):
        """The baseline lattice: x-lines, y-lines and verticals through every
        unit point of the z=0 plane. Over the art, so misplaced edges show."""
        bb = list(self._bb)
        keep, self._bb = self._bb, None
        u = self.u
        out = []
        lo, hi = -80, 80
        for i in range(lo, hi):
            a, b = self.p(i, lo), self.p(i, hi); out.append("M%.1f %.1fL%.1f %.1f" % (*a, *b))
            a, b = self.p(lo, i), self.p(hi, i); out.append("M%.1f %.1fL%.1f %.1f" % (*a, *b))
        for k in range(-160, 160):
            sx = k * C30 * u
            out.append("M%.1f %.1fL%.1f %.1f" % (sx, bb[1] - 50, sx, bb[3] + 50))
        self._bb = keep
        return '<path d="%s" stroke="#E63939" stroke-opacity="0.35" stroke-width="0.6" fill="none"/>' % "".join(out)


def _box_faces(d):
    """The drawn faces of a box item as (side, world points)."""
    x, y, z, w, dd, h, mat, top, faces, op = d
    out = []
    if h > 0 and "l" in faces:
        out.append(("l", [(x, y + dd, z), (x + w, y + dd, z), (x + w, y + dd, z + h), (x, y + dd, z + h)]))
    if h > 0 and "r" in faces:
        out.append(("r", [(x + w, y, z), (x + w, y + dd, z), (x + w, y + dd, z + h), (x + w, y, z + h)]))
    if "t" in faces:
        out.append(("t", [(x, y, z + h), (x + w, y, z + h), (x + w, y + dd, z + h), (x, y + dd, z + h)]))
    return out


def _inside(poly, x, y):
    """Point in a convex polygon of either winding (edges count as inside)."""
    sign = 0
    n = len(poly)
    for i in range(n):
        (ax, ay), (bx, by) = poly[i], poly[(i + 1) % n]
        c = (bx - ax) * (y - ay) - (by - ay) * (x - ax)
        if abs(c) < 1e-12:
            continue
        if sign == 0:
            sign = 1 if c > 0 else -1
        elif (c > 0) != (sign > 0):
            return False
    return True


def _faces_viewer(pts, inside):
    """Does the planar polygon's outward side (away from `inside`) look at the
    viewer, who looks along -(1, 1, 1)?"""
    (x0, y0, z0), (x1, y1, z1), (x2, y2, z2) = pts[0], pts[1], pts[2]
    ux, uy, uz = x1 - x0, y1 - y0, z1 - z0
    vx, vy, vz = x2 - x0, y2 - y0, z2 - z0
    n = (uy * vz - uz * vy, uz * vx - ux * vz, ux * vy - uy * vx)
    c = [sum(p[i] for p in pts) / len(pts) for i in range(3)]
    out = sum(n[i] * (c[i] - inside[i]) for i in range(3))
    if out < 0:
        n = (-n[0], -n[1], -n[2])
    return n[0] + n[1] + n[2] > 1e-9


def _desc(it):
    x, y, z, w, d, h = it.box[:6]
    return "%s box x%.2f..%.2f y%.2f..%.2f z%.2f..%.2f" % (it.tag or "", x, x + w, y, y + d, z, z + h)


def _pl(q):
    return " ".join("%.1f,%.1f" % t for t in q)


def _normal_shade(pts, st, sl, sr):
    (x0, y0, z0), (x1, y1, z1), (x2, y2, z2) = pts[0], pts[1], pts[2]
    ux, uy, uz = x1 - x0, y1 - y0, z1 - z0
    vx, vy, vz = x2 - x0, y2 - y0, z2 - z0
    nx, ny, nz = abs(uy * vz - uz * vy), abs(uz * vx - ux * vz), abs(ux * vy - uy * vx)
    t = nx + ny + nz or 1
    return (sr * nx + sl * ny + st * nz) / t


def _wrap(body, view, theme, title, desc, background, style=""):
    vx, vy, vw, vh = view
    bg = ('<rect x="%d" y="%d" width="%d" height="%d" fill="%s"/>' % (vx, vy, vw, vh, PALETTES[theme]["_bg"])) if background else ""
    return ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="%d %d %d %d" width="%d" height="%d" role="img" '
            'aria-labelledby="t d" data-theme="%s"><title id="t">%s</title><desc id="d">%s</desc><style>%s</style>'
            '<g stroke-linejoin="round" stroke-linecap="round">%s%s</g></svg>'
            % (vx, vy, vw, vh, vw, vh, theme, _esc(title), _esc(desc or title), style, bg, body))


def _esc(t):
    return t.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


# ══ the character rig ═══════════════════════════════════════════════════
# A blocky ADULT figure, about 3.7 heads tall: shoulders (torso + arms) are
# wider than the head, arms reach the upper thigh, legs are a third of the
# height. Local frame: f = forward (the way the person faces), s = sideways
# towards the viewer's side of the body, z = up. Measures at h = 1:
#
#   shoes 0.12   legs 0.84 (each 0.26 wide, 0.04 apart)   torso 0.78 tall,
#   0.60 wide, 0.32 deep   neck 0.05   head 0.66 cube   arms 0.15 x 0.18,
#   0.86 long with the hand   total about 2.5 with hair
#
# Every part is its own box that only touches its neighbours, so the sorter
# places each one against the scene (an arm in front of a counter, legs
# behind a bench seat), and the face never ends up under its own hair.
TW, TD, TH = 0.32, 0.60, 0.78           # torso depth (f), width (s), height
HS = 0.66                               # head size
SHOE = 0.12
LEG_Z = 0.96                            # hip height when standing
NECK = 0.05
AW, AD = 0.15, 0.18                     # arm width (s), depth (f)
ARM = 0.86                              # shoulder to fingertips
SHORT_SLEEVES = ("tee", "polo", "hivis", "dress", "apron", "batik_short")
DRAPE = 0.16                            # hijab drape over the shoulders


FACINGS = {   # facing: (forward axis, side axis) as unit vectors in (x, y)
    "r": ((1, 0), (0, 1)), "dr": ((1, 0), (0, 1)),      # towards the lower right: face visible
    "l": ((0, 1), (1, 0)), "dl": ((0, 1), (1, 0)),      # towards the lower left: face visible
    "ul": ((-1, 0), (0, 1)),                            # walking away to the upper left: back visible
    "ur": ((0, -1), (1, 0)),                            # walking away to the upper right: back visible
}


class _Rig:
    def __init__(self, sc, X, Y, Z, facing, k, tag):
        if facing not in FACINGS:
            raise ValueError("facing must be one of r, l, ul, ur (got %r)" % (facing,))
        self.sc, self.X, self.Y, self.Z, self.k, self.tag = sc, X, Y, Z, k, tag
        self.FX, self.SX = FACINGS[facing]
        self.away = self.FX[0] < 0 or self.FX[1] < 0     # we see the back
        self.wk = max(0.55, min(1.15, sc.u * k / 34))     # face line widths follow the drawn size

    def sub(self, kh, anchor):
        """A rig with the same axes but scale kh, matching this one at anchor
        (used to give children a larger head)."""
        af, as_, az = anchor
        xa, ya, za = self.w(af, as_, az)
        (fx, fy), (sx, sy) = self.FX, self.SX
        r = copy.copy(self)
        r.k = kh
        r.X, r.Y, r.Z = xa - (af * fx + as_ * sx) * kh, ya - (af * fy + as_ * sy) * kh, za - az * kh
        r.wk = max(0.55, min(1.15, self.sc.u * kh / 34))
        return r

    def w(self, f, s, z):
        k, (fx, fy), (sx, sy) = self.k, self.FX, self.SX
        return (self.X + (f * fx + s * sx) * k, self.Y + (f * fy + s * sy) * k, self.Z + z * k)

    def B(self, f0, f1, s0, s1, z0, z1, mat, top=None, faces="tlr", part="", ol=None):
        a, b = self.w(f0, s0, z0), self.w(f1, s1, z1)
        x0, x1, y0, y1 = min(a[0], b[0]), max(a[0], b[0]), min(a[1], b[1]), max(a[1], b[1])
        with self.sc.tag("%s %s" % (self.tag, part)), (self.sc.outline(ol) if ol else nullcontext()):
            return self.sc.box(x0, y0, a[2], x1 - x0, y1 - y0, b[2] - a[2], mat, top=top, faces=faces, snap=False)

    def _sc(self, shapes, flip=False):
        """Scale shapes to the body size; flip mirrors a (a -> -a)."""
        k, wk = self.k, self.wk
        sg = -1 if flip else 1
        out = []
        for s in shapes:
            t = s[0]
            if t == "rect":
                a, w = s[1] * k, s[3] * k
                out.append((t, a if not flip else -(a + w), s[2] * k, w, s[4] * k) + tuple(s[5:]))
            elif t == "poly":
                out.append((t, [(sg * a * k, b * k) for a, b in s[1]]) + tuple(s[2:]))
            elif t == "line":
                out.append((t, [(sg * a * k, b * k) for a, b in s[1]], s[2], s[3] * wk))
            elif t == "ell":
                out.append((t, sg * s[1] * k, s[2] * k, s[3] * k, s[4] * k) + tuple(s[5:]))
            elif t in ("ring", "arc"):
                out.append((t, sg * s[1] * k, s[2] * k, s[3] * k, s[4] * k, s[5], s[6] * wk))
        return out

    def _vert(self, on, axis_plane, anchor, along, shapes):
        """Marks on a vertical face whose normal is world +x or +y. along: the
        local axis vector the shapes' a runs along."""
        x, y, z = anchor
        if axis_plane == (1, 0):          # plane x = const, a runs +y
            side, flip = "r", along[1] < 0
        else:                             # plane y = const, a runs +x
            side, flip = "l", along[0] < 0
        self.sc.face_mark(x, y, z, side, self._sc(shapes, flip), on=on)

    def front(self, on, f, s0, z0, shapes):
        """Marks on a face pointing forward (plane f): a along s, b up.
        Not drawn when the person faces away (that face is hidden)."""
        if not self.away:
            self._vert(on, self.FX, self.w(f, s0, z0), self.SX, shapes)

    def back(self, on, f, s0, z0, shapes):
        """Marks on a face pointing backward (plane f): a along s, b up.
        Only drawn when the person faces away."""
        if self.away:
            self._vert(on, (-self.FX[0], -self.FX[1]), self.w(f, s0, z0), self.SX, shapes)

    def side(self, on, s, f0, z0, shapes):
        """Marks on the near side face (plane s): a along f (back to front), b up."""
        self._vert(on, self.SX, self.w(f0, s, z0), self.FX, shapes)

    def top(self, on, f0, s0, z, shapes):
        """Marks on a top face: a along f, b along s (converted to polygons)."""
        def P(a, b):
            x, y, _ = self.w(f0 + a, s0 + b, z)
            return (x - ox, y - oy)
        ox, oy, oz = self.w(f0, s0, z)
        k = self.k
        out = []
        for s in shapes:
            t = s[0]
            if t == "rect":
                a, b, w, h = s[1], s[2], s[3], s[4]
                out.append(("poly", [P(a, b), P(a + w, b), P(a + w, b + h), P(a, b + h)]) + tuple(s[5:]))
            elif t in ("poly", "line"):
                pts = [P(a, b) for a, b in s[1]]
                out.append((t, pts) + ((s[2], s[3] * self.wk) if t == "line" else tuple(s[2:])))
            elif t == "ell":
                c = P(s[1], s[2]); swap = self.FX[0] == 0
                out.append(("ell", c[0], c[1], (s[4] if swap else s[3]) * k, (s[3] if swap else s[4]) * k) + tuple(s[5:]))
        self.sc.face_mark(ox, oy, oz, "t", out, on=on)

    def line(self, pts, mat, width):
        with self.sc.tag(self.tag + " line"):
            return self.sc.line([self.w(*p) for p in pts], mat, width)

    def pyramid(self, f0, f1, s0, s1, z, apex, mat):
        """A pyramid on a square base; only the two faces the viewer sees."""
        a, b = self.w(f0, s0, z), self.w(f1, s1, z)
        x0, x1, y0, y1 = min(a[0], b[0]), max(a[0], b[0]), min(a[1], b[1]), max(a[1], b[1])
        ap = self.w(*apex)
        with self.sc.tag(self.tag + " spike"):
            self.sc.poly([(x1, y0, z * 0 + a[2]), (x1, y1, a[2]), ap], mat, snap=False)
            self.sc.poly([(x0, y1, a[2]), (x1, y1, a[2]), ap], mat, snap=False)

    def wedge(self, f0, f1, s0, s1, z, h, mat, ol=None):
        """A ramp on (f0..f1, s0..s1) rising from the front (f1) to height h at
        the back (f0): swept-back hair. Draws only the faces the viewer sees."""
        P = lambda f, s_, zz: self.w(f, s_, zz)
        with self.sc.tag(self.tag + " wedge"), (self.sc.outline(ol) if ol else nullcontext()):
            if not self.away:
                self.sc.poly([P(f1, s0, z), P(f1, s1, z), P(f0, s1, z + h), P(f0, s0, z + h)], mat, snap=False)
            else:
                self.sc.poly([P(f0, s0, z), P(f0, s1, z), P(f0, s1, z + h), P(f0, s0, z + h)], mat, snap=False)
            self.sc.poly([P(f0, s1, z), P(f1, s1, z), P(f0, s1, z + h)], mat, snap=False)

    def cyl(self, f, s, z, r, h, mat, **kw):
        x, y, zz = self.w(f, s, z)
        with self.sc.tag(self.tag + " cyl"):
            return self.sc.cylinder(x, y, zz, r * self.k, h * self.k, mat, **kw)


def _person(sc, x, y, z, o):
    k = o["h"]
    X, Y, Z = x, y, z                                # not snapped: seats and floors may be off-grid
    rig = _Rig(sc, X, Y, Z, o["facing"], k, "person@(%.1f,%.1f)" % (x, y))
    B, F, SD = rig.B, rig.front, rig.side
    skin, hair, top, outfit = o["skin"], o["hair"], o["top"], o["outfit"]
    sit, walk = o["sit"], o["walk"]
    style = o["hair_style"]
    hij = style == "hijab"
    scarf = hair if hij else None
    o["_scarf_ol"] = sc.new_outline("scarf") if hij else None      # one border round the whole scarf
    o["_hair_ol"] = sc.new_outline("hair")                          # one border round the whole head of hair
    sleeve = o["sleeve"] or (o["inner"] if outfit == "hivis" else top)
    skirt = o["skirt"] or (top if outfit == "dress" else None)
    stride = walk * 0.12
    if sit:
        sit = sit / k                                  # seat height in body units

    tz = 0.0 if sit else LEG_Z                       # torso bottom
    sz = tz + TH                                     # shoulder height
    hz = sz + NECK                                   # head bottom
    ht = hz + HS                                     # head top
    hf0, hs0 = TW / 2 - HS / 2, TD / 2 - HS / 2      # head back / far side
    hf1, hs1 = hf0 + HS, hs0 + HS

    # soft shadow on the floor
    fz = -(sit or 0)
    f0s, f1s = (-0.1, TW + 0.62) if sit else (-0.1 - abs(stride), TW + 0.16 + abs(stride))
    with sc.tag(rig.tag + " shadow"):
        a, b = rig.w(f0s, -0.12, fz), rig.w(f1s, TD + 0.12, fz)
        sc.shadow(min(a[0], b[0]), min(a[1], b[1]), abs(b[0] - a[0]), abs(b[1] - a[1]), a[2])

    # legs and shoes
    shoe, bottom = o["shoe"], o["bottom"]
    knee = LEG_Z - (0.36 if skirt else 0.0)
    for i, s0 in enumerate((0.02, 0.32)):
        s1 = s0 + 0.26
        if sit:
            B(TW, TW + 0.42, s0, s1, 0.0, 0.24, skirt or bottom, part="thigh")
            B(TW + 0.18, TW + 0.42, s0, s1, -sit + SHOE, 0.0, bottom, part="shin")
            B(TW + 0.16, TW + 0.54, s0, s1, -sit, -sit + SHOE, shoe, top=("~", shoe, 1.25), part="shoe")
        else:
            off = stride if i == 1 else -stride
            B(0.01 + off, 0.39 + off, s0, s1, 0, SHOE, shoe, top=("~", shoe, 1.25), part="shoe")
            B(0.03 + off, 0.29 + off, s0, s1, SHOE, knee, bottom, part="leg")
    if skirt and not sit:
        sk = B(-0.04, TW + 0.04, 0.0, TD, knee, LEG_Z, skirt, part="skirt")
        F(sk, TW + 0.04, 0.0, knee, [("line", [(0.2, 0.0), (0.22, 0.36)], ("~", skirt, 0.8), 1.0),
                                        ("line", [(0.46, 0.0), (0.44, 0.36)], ("~", skirt, 0.8), 1.0)])

    # torso with the outfit; a hijab drapes over the shoulders
    if hij:
        torso = B(0, TW, 0, TD, tz, sz - DRAPE, top, part="torso")
        rig.back(torso, 0, 0, tz, _outfit_back(outfit, top, o["inner"], TH - DRAPE))
        F(torso, TW, 0, tz, _outfit_front(outfit, top, o["inner"], o["tie"], TH - DRAPE)
          + [("poly", [(TD / 2 - 0.2, TH - DRAPE), (TD / 2 + 0.2, TH - DRAPE), (TD / 2, TH - DRAPE - 0.16)], scarf)])
        SD(torso, TD, 0, tz, _outfit_side(outfit, top, o["inner"], TH - DRAPE)
           + [("poly", [(0, TH - DRAPE), (TW, TH - DRAPE), (TW * 0.5, TH - DRAPE - 0.07)], scarf)])
        B(0, TW, 0, TD, sz - DRAPE, sz, scarf, part="hijab drape", ol=o["_scarf_ol"])
        B(hf0, hf1, hs0, hs1, sz, hz, scarf, part="hijab neck", ol=o["_scarf_ol"])
    else:
        torso = B(0, TW, 0, TD, tz, sz, top, part="torso")
        rig.back(torso, 0, 0, tz, _outfit_back(outfit, top, o["inner"], TH))
        F(torso, TW, 0, tz, _outfit_front(outfit, top, o["inner"], o["tie"], TH))
        SD(torso, TD, 0, tz, _outfit_side(outfit, top, o["inner"], TH))
        B(0.08, 0.24, 0.2, 0.4, sz, hz, ("~", skin, 0.88), part="neck")

    # children get a larger head for their size (kh = sqrt(h) instead of h)
    kh = k ** 0.5 if k < 1 else k
    hrig = rig if kh == k else rig.sub(kh, (TW / 2, TD / 2, hz))

    # arms (the raised arm of a wave clears the head, ear and hair)
    reach = {"long": 0.07, "bob": 0.07, "hijab": 0.07, "pigtails": 0.22}.get(style, 0.04)   # hair or ear past the head
    side_out = TD / 2 + (HS / 2 + reach) * kh / k + 0.02
    hands = _arms(rig, o, sleeve, outfit, skin, sz, stride, side_out, scarf)

    # head, hair and face
    head = hrig.B(hf0, hf1, hs0, hs1, hz, ht, skin, top=(None if style == "bald" else hair), part="head")
    _hair(hrig, o, head, hf0, hs0, hz, ht, sz)
    hrig.front(head, hf1, hs0, hz, _face(o, skin))
    hrig.back(head, hf0, hs0, hz, _back_of_head(style, hair))

    _carry(rig, o, hands, sz)


def _arms(rig, o, sleeve, outfit, skin, sz, stride, side_out, scarf):
    """Draw both arms; return where the hands are, for held things."""
    B = rig.B
    short = outfit in SHORT_SLEEVES
    cuff = o["inner"] if outfit in ("suit", "jacket") else sleeve
    f0 = TW / 2 - AD / 2
    hands = {}
    pose = o["pose"]
    if o["sit"] and pose == "down":
        pose = "lap"

    def upper(a0, a1, s0, s1, z0, z1, mat, part):
        """The top of the arm; under a hijab its top is the scarf."""
        sk = o["_scarf_ol"]
        if scarf and z1 > sz - DRAPE + 0.01 and z0 < sz - DRAPE:
            B(a0, a1, s0, s1, z0, sz - DRAPE, mat, part=part, ol=ak)
            B(a0, a1, s0, s1, sz - DRAPE, z1, scarf, part="hijab drape", ol=sk)
        elif scarf and z0 >= sz - DRAPE - 0.01:
            B(a0, a1, s0, s1, z0, z1, scarf, part=part, ol=sk)
        else:
            B(a0, a1, s0, s1, z0, z1, mat, part=part, ol=ak)

    for near in (False, True):
        ak = rig.sc.new_outline("arm")                     # one border round each arm
        s0 = TD if near else -AW
        s1 = s0 + AW
        swing = (stride if near else -stride) * 0.9
        p = pose if pose in ("down", "hold", "lap") else (pose if near else ("lap" if o["sit"] else "down"))
        if p == "down":
            a0, a1 = f0 + swing, f0 + AD + swing
            if short:
                upper(a0, a1, s0, s1, sz - 0.3, sz, sleeve, "sleeve")
                B(a0, a1, s0, s1, sz - ARM + 0.12, sz - 0.3, skin, part="forearm", ol=ak)
            else:
                upper(a0, a1, s0, s1, sz - ARM + 0.2, sz, sleeve, "sleeve")
                B(a0, a1, s0, s1, sz - ARM + 0.12, sz - ARM + 0.2, cuff, part="cuff", ol=ak)
            B(a0 + 0.01, a1 - 0.01, s0 + 0.01, s1 - 0.01, sz - ARM, sz - ARM + 0.12, skin, part="hand", ol=ak)
            hands[near] = ("down", a0, a1, s0, s1, sz - ARM)
        elif p in ("hold", "phone", "lap"):
            ez = sz - {"hold": 0.38, "phone": 0.3, "lap": 0.4}[p]
            upper(f0, f0 + AD, s0, s1, ez, sz, sleeve, "upper arm")
            reach = 0.26 if p != "lap" else 0.3
            B(f0, TW + reach, s0, s1, ez - 0.14, ez, skin if short else sleeve, part="forearm", ol=ak)
            B(TW + reach, TW + reach + 0.12, s0 + 0.01, s1 - 0.01, ez - 0.13, ez - 0.01, skin, part="hand", ol=ak)
            hands[near] = (p, TW + reach, TW + reach + 0.12, s0, s1, ez)
        elif p == "point":
            upper(f0, f0 + AD, s0, s1, sz - 0.16, sz, sleeve, "shoulder")
            B(f0 + AD, TW + 0.4, s0, s1, sz - 0.16, sz - 0.02, sleeve if not short else skin, part="arm", ol=ak)
            B(TW + 0.4, TW + 0.52, s0 + 0.01, s1 - 0.01, sz - 0.15, sz - 0.03, skin, part="hand", ol=ak)
            B(TW + 0.52, TW + 0.62, s0 + 0.045, s1 - 0.045, sz - 0.08, sz - 0.04, skin, part="finger", ol=ak)
            hands[near] = ("point",)
        elif p == "wave":
            so = max(side_out, s0)
            upper(f0, f0 + AD, s0, so + AW, sz - 0.15, sz, sleeve, "shoulder")
            B(f0, f0 + AD, so, so + AW, sz, sz + 0.62, sleeve if not short else skin, part="raised arm", ol=ak)
            B(f0 + 0.01, f0 + AD - 0.01, so + 0.01, so + AW - 0.01, sz + 0.62, sz + 0.76, skin, part="hand", ol=ak)
            hands[near] = ("wave",)
    return hands


def _outfit_front(outfit, top, inner, tie, H):
    """Marks on the torso front: a across the chest (0..0.60), b up (0..H)."""
    c, D = TD / 2, TD
    dk = ("~", top, 0.78)
    lt = ("~", top, 1.15)
    belt = ("rect", 0, 0, D, 0.05, ("~", "navy", 1.0))
    out = []
    if outfit in ("tee", "dress"):
        out += [("arc", c, H - 0.01, 0.22, 0.04, dk, 1.2)]
        if outfit == "dress":
            out += [("rect", 0, 0.0, D, 0.05, dk)]
    elif outfit in ("shirt", "polo", "batik", "batik_short"):
        if outfit.startswith("batik"):
            for r in range(4):
                for q in range(4):
                    a = 0.07 + q * 0.15 + (0.075 if r % 2 else 0)
                    if a > D - 0.04:
                        continue
                    b = 0.1 + r * 0.16
                    out.append(("poly", [(a, b - 0.045), (a + 0.045, b), (a, b + 0.045), (a - 0.045, b)], "gold"))
                    out.append(("ell", a, b, 0.014, 0.014, dk))
        out += [("poly", [(c - 0.14, H), (c, H - 0.09), (c - 0.03, H - 0.14)], lt),
                ("poly", [(c + 0.14, H), (c, H - 0.09), (c + 0.03, H - 0.14)], lt),
                ("line", [(c, H - 0.09), (c, 0.04 if outfit != "polo" else H - 0.3)], dk, 1.0)]
        for i in range(3 if outfit != "polo" else 2):
            out.append(("ell", c + 0.028, H - 0.19 - i * 0.16, 0.018, 0.018, "paper"))
        if outfit == "shirt":
            out += [("rect", D * 0.64, H * 0.56, 0.11, 0.11, dk), belt]
        if outfit == "polo":
            out += [belt]
    elif outfit in ("suit", "jacket"):
        out += [("poly", [(c - 0.13, H), (c + 0.13, H), (c, H - 0.38)], inner)]
        if tie and outfit == "suit":
            out += [("poly", [(c - 0.032, H - 0.01), (c + 0.032, H - 0.01), (c + 0.024, H - 0.07), (c - 0.024, H - 0.07)], ("~", tie, 0.85)),
                    ("poly", [(c - 0.024, H - 0.07), (c + 0.024, H - 0.07), (c + 0.042, H - 0.32), (c, H - 0.38), (c - 0.042, H - 0.32)], tie)]
        out += [("line", [(c - 0.13, H), (c - 0.075, H - 0.19), (c, H - 0.38)], dk, 1.1),
                ("line", [(c + 0.13, H), (c + 0.075, H - 0.19), (c, H - 0.38)], dk, 1.1),
                ("line", [(c, H - 0.38), (c, 0)], dk, 1.0)]
        if outfit == "suit":
            out += [("ell", c - 0.05, H - 0.48, 0.02, 0.02, dk), ("rect", D * 0.66, H * 0.64, 0.11, 0.03, "paper")]
    elif outfit == "cardigan":
        out += [("rect", c - 0.085, 0, 0.17, H, inner),
                ("line", [(c - 0.085, 0), (c - 0.085, H)], dk, 1.0), ("line", [(c + 0.085, 0), (c + 0.085, H)], dk, 1.0)]
        for i in range(3):
            out.append(("ell", c + 0.12, H - 0.18 - i * 0.18, 0.018, 0.018, dk))
    elif outfit == "stripes":
        for i in range(int((H - 0.1) / 0.14) + 1):
            out.append(("rect", 0, 0.06 + i * 0.14, D, 0.05, inner))
        out += [("arc", c, H - 0.01, 0.22, 0.04, dk, 1.2)]
    elif outfit == "hivis":
        out += [("poly", [(c - 0.1, H), (c + 0.1, H), (c, H - 0.2)], inner),
                ("rect", 0.09, 0, 0.07, H, "!paper"), ("rect", D - 0.16, 0, 0.07, H, "!paper"),
                ("rect", 0, 0.18, D, 0.07, "!paper"), ("line", [(c, H - 0.2), (c, 0)], dk, 1.0)]
    elif outfit == "apron":
        out += [("arc", c, H - 0.01, 0.22, 0.04, dk, 1.2),
                ("rect", D * 0.16, 0, D * 0.68, H * 0.7, inner),
                ("line", [(D * 0.16, H * 0.7), (D * 0.26, H)], inner, 1.6),
                ("line", [(D * 0.84, H * 0.7), (D * 0.74, H)], inner, 1.6),
                ("rect", D * 0.32, H * 0.22, D * 0.36, 0.1, ("~", inner, 0.85))]
    elif outfit == "hoodie":
        out += [("poly", [(c - 0.19, H), (c + 0.19, H), (c + 0.07, H - 0.11), (c - 0.07, H - 0.11)], dk),
                ("line", [(c - 0.055, H - 0.11), (c - 0.065, H - 0.3)], "paper", 1.0),
                ("line", [(c + 0.055, H - 0.11), (c + 0.065, H - 0.3)], "paper", 1.0),
                ("poly", [(c - 0.19, 0.07), (c + 0.19, 0.07), (c + 0.14, 0.25), (c - 0.14, 0.25)], dk),
                ("rect", 0, 0, D, 0.05, dk)]
    return out


def _back_of_head(style, hair):
    """Hair on the back of the head (a across, b up), seen when facing away."""
    H = HS
    if style in ("hijab", "long", "bob"):
        return []                                    # the back slab covers it
    if style == "bald":
        return [("poly", [(0, 0.16 * H), (H, 0.16 * H), (H, 0.58 * H), (0, 0.6 * H)], hair)]
    if style in ("cap", "hardhat"):
        return [("poly", [(0, 0.14 * H), (H, 0.14 * H), (H, H), (0, H)], hair)]
    return [("poly", [(0, 0.12 * H), (0.25 * H, 0.08 * H), (0.5 * H, 0.13 * H), (0.75 * H, 0.08 * H), (H, 0.12 * H),
                      (H, H), (0, H)], hair)]


def _outfit_back(outfit, top, inner, H):
    """Marks on the torso back (a across 0..0.60, b up), seen when facing away."""
    c, D = TD / 2, TD
    dk = ("~", top, 0.78)
    out = []
    if outfit in ("tee", "dress", "stripes", "apron"):
        out += [("arc", c, H - 0.01, 0.2, 0.02, dk, 1.2)]
    if outfit == "stripes":
        for i in range(int((H - 0.1) / 0.14) + 1):
            out.append(("rect", 0, 0.06 + i * 0.14, D, 0.05, inner))
    elif outfit == "apron":
        out += [("line", [(c - 0.12, 0.18), (c + 0.12, 0.26)], inner, 1.6), ("line", [(c - 0.12, 0.26), (c + 0.12, 0.18)], inner, 1.6),
                ("line", [(0, 0.22), (D, 0.22)], inner, 1.6)]
    elif outfit == "hivis":
        out += [("rect", 0.09, 0, 0.07, H, "!paper"), ("rect", D - 0.16, 0, 0.07, H, "!paper"), ("rect", 0, 0.18, D, 0.07, "!paper")]
    elif outfit in ("shirt", "polo", "batik", "batik_short"):
        out += [("rect", c - 0.15, H - 0.06, 0.3, 0.06, ("~", top, 1.15))]
        if not outfit.startswith("batik"):
            out += [("rect", 0, 0, D, 0.05, ("~", "navy", 1.0))]
    elif outfit in ("suit", "jacket"):
        out += [("line", [(c, 0), (c, 0.2)], dk, 1.0), ("rect", c - 0.15, H - 0.06, 0.3, 0.06, ("~", top, 0.9))]
    elif outfit == "hoodie":
        out += [("poly", [(c - 0.2, H), (c + 0.2, H), (c + 0.16, H - 0.22), (c, H - 0.28), (c - 0.16, H - 0.22)], dk)]
    return out


def _outfit_side(outfit, top, inner, H):
    """Marks on the torso near side: a back to front (0..0.32), b up."""
    W = TW
    dk = ("~", top, 0.78)
    out = []
    if outfit == "stripes":
        for i in range(int((H - 0.1) / 0.14) + 1):
            out.append(("rect", 0, 0.06 + i * 0.14, W, 0.05, inner))
    elif outfit.startswith("batik"):
        for r in range(4):
            a, b = 0.1 + (0.12 if r % 2 else 0), 0.1 + r * 0.16
            out.append(("poly", [(a, b - 0.045), (a + 0.045, b), (a, b + 0.045), (a - 0.045, b)], "gold"))
    elif outfit == "hivis":
        out += [("rect", 0, 0.18, W, 0.07, "!paper")]
    elif outfit in ("suit", "jacket", "cardigan"):
        out += [("line", [(W * 0.5, 0.05), (W * 0.5, H - 0.06)], dk, 1.0)]
    elif outfit in ("shirt", "polo"):
        out += [("rect", 0, 0, W, 0.05, ("~", "navy", 1.0))]
    elif outfit == "hoodie":
        out += [("rect", 0, 0, W, 0.05, dk), ("poly", [(0, H), (W * 0.45, H), (W * 0.2, H - 0.12), (0, H - 0.14)], dk)]
    return out


def _hair(rig, o, head, hf0, hs0, hz, ht, sz):
    B, F, SD = rig.B, rig.front, rig.side
    style, hair = o["hair_style"], o["hair"]
    hd = ("~", hair, 0.8)
    hf1, hs1 = hf0 + HS, hs0 + HS
    H = HS

    def ear():
        e = B(hf0 + 0.26, hf0 + 0.38, hs1, hs1 + 0.035, hz + 0.2, hz + 0.37, o["skin"], part="ear")
        SD(e, hs1 + 0.035, hf0 + 0.26, hz + 0.2, [("rect", 0.035, 0.045, 0.05, 0.08, ("~", o["skin"], 0.85))])

    # hair painted on the head's near side (a: back 0 -> front H, b up)
    side_short = [(0, H), (H, H), (H, 0.86 * H), (0.6 * H, 0.84 * H), (0.6 * H, 0.5 * H), (0.56 * H, 0.5 * H),
                  (0.56 * H, 0.6 * H), (0.38 * H, 0.6 * H), (0.38 * H, 0.18 * H), (0, 0.14 * H)]
    fringes = {   # hair painted on the face (a across, b up)
        "short": [(0, H), (H, H), (H, 0.8 * H), (0.78 * H, 0.86 * H), (0.55 * H, 0.79 * H), (0.3 * H, 0.86 * H), (0, 0.78 * H)],
        "sidepart": [(0, H), (H, H), (H, 0.68 * H), (0.74 * H, 0.79 * H), (0.36 * H, 0.86 * H), (0, 0.88 * H)],
        "spiky": [(0, H), (H, H), (H, 0.78 * H), (0.84 * H, 0.86 * H), (0.67 * H, 0.76 * H), (0.5 * H, 0.86 * H),
                  (0.33 * H, 0.76 * H), (0.16 * H, 0.86 * H), (0, 0.78 * H)],
        "quiff": [(0, H), (H, H), (H, 0.84 * H), (0.5 * H, 0.9 * H), (0, 0.84 * H)],
        "curly": [(0, H), (H, H), (H, 0.74 * H), (0.84 * H, 0.82 * H), (0.67 * H, 0.75 * H), (0.5 * H, 0.83 * H),
                  (0.33 * H, 0.75 * H), (0.16 * H, 0.82 * H), (0, 0.74 * H)],
        "bun": [(0, H), (H, H), (H, 0.84 * H), (0.5 * H, 0.9 * H), (0, 0.84 * H)],
        "ponytail": [(0, H), (H, H), (H, 0.82 * H), (0.62 * H, 0.86 * H), (0.36 * H, 0.9 * H), (0, 0.84 * H)],
        "pigtails": [(0, H), (H, H), (H, 0.76 * H), (0.75 * H, 0.82 * H), (0.5 * H, 0.75 * H), (0.25 * H, 0.82 * H), (0, 0.76 * H)],
        "long": [(0, H), (H, H), (H, 0.02 * H), (0.9 * H, 0.02 * H), (0.88 * H, 0.72 * H), (0.62 * H, 0.82 * H),
                 (0.4 * H, 0.78 * H), (0.12 * H, 0.72 * H), (0.1 * H, 0.02 * H), (0, 0.02 * H)],
        "bob": [(0, H), (H, H), (H, 0.18 * H), (0.9 * H, 0.18 * H), (0.88 * H, 0.72 * H), (0.12 * H, 0.72 * H),
                (0.1 * H, 0.18 * H), (0, 0.18 * H)],
        "cap": [(0, H), (H, H), (H, 0.88 * H), (0, 0.88 * H)],
        "hardhat": [(0, H), (H, H), (H, 0.9 * H), (0, 0.9 * H)],
    }
    if style == "bald":
        SD(head, hs1, hf0, hz, [("poly", [(0, 0.6 * H), (0.36 * H, 0.58 * H), (0.38 * H, 0.2 * H), (0, 0.16 * H)], hair)])
        ear()
        return
    if style == "hijab":
        # the scarf: crown, both sides and the back of the head, framing the face
        B(hf0 - 0.05, hf1 + 0.02, hs0 - 0.05, hs1 + 0.05, ht, ht + 0.07, hair, part="hijab crown", ol=o["_scarf_ol"])
        B(hf0 - 0.05, hf0, hs0, hs1, sz - 0.3, ht, hair, part="hijab back", ol=o["_scarf_ol"])
        for s0 in (hs0 - 0.05, hs1):
            sl = B(hf0 - 0.05, hf1 + 0.02, s0, s0 + 0.05, sz, ht, hair, part="hijab side", ol=o["_scarf_ol"])
            if s0 == hs1:
                SD(sl, hs1 + 0.05, hf0 - 0.05, sz,
                   [("line", [(0.2, 0.05), (0.34, ht - sz - 0.1)], hd, 1.0), ("line", [(0.44, 0.05), (0.54, ht - sz - 0.24)], hd, 1.0)])
        return
    if style in ("cap", "hardhat"):
        _hat(rig, o, hf0, hs0, ht)
        F(head, hf1, hs0, hz, [("poly", fringes[style], hair)])
        SD(head, hs1, hf0, hz, [("poly", side_short, hair)])
        ear()
        return

    # a thin layer of hair on top: flush with the face, a little over the back and sides
    thick = 0.12 if style == "curly" else 0.07
    ov = 0.05 if style == "curly" else 0.025
    back = 0.08 if style in ("long", "bob") else ov
    sides = 0.06 if style in ("long", "bob") else ov
    cap = B(hf0 - back, hf1, hs0 - sides, hs1 + sides, ht, ht + thick, hair, part="hair", ol=o["_hair_ol"])
    F(head, hf1, hs0, hz, [("poly", fringes.get(style, fringes["short"]), hair)])
    if style == "curly":
        dots = lambda n, z0: [("ell", 0.08 + i * 0.15, z0, 0.045, 0.035, hd) for i in range(n)]
        SD(cap, hs1 + sides, hf0 - back, ht, dots(5, 0.06))
        F(cap, hf1, hs0 - sides, ht, dots(5, 0.06))
        t2 = B(hf0 + 0.06, hf1 - 0.06, hs0 + 0.06, hs1 - 0.06, ht + thick, ht + thick + 0.1, hair, part="curls", ol=o["_hair_ol"])
        SD(t2, hs1 - 0.06, hf0 + 0.06, ht + thick, dots(4, 0.05))
        F(t2, hf1 - 0.06, hs0 + 0.06, ht + thick, dots(4, 0.05))

    if style in ("long", "bob"):
        z0 = hz - 0.3 if style == "long" else hz + 0.1
        B(hf0 - 0.08, hf0, hs0, hs1, z0, ht, hair, part="hair back", ol=o["_hair_ol"])
        cz = hz - 0.01 if style == "long" else hz + 0.12
        for s0 in (hs0 - 0.06, hs1):
            c = B(hf0 - 0.08, hf0 + 0.42, s0, s0 + 0.06, cz, ht, hair, part="hair side", ol=o["_hair_ol"])
            if s0 == hs1:
                SD(c, hs1 + 0.06, hf0 - 0.08, cz, [("line", [(0.18, 0.04), (0.18, ht - cz - 0.1)], hd, 1.0),
                                                   ("line", [(0.34, 0.04), (0.34, ht - cz - 0.16)], hd, 1.0)])
        SD(head, hs1, hf0, hz, [("poly", [(0.42, H), (H, H), (H, 0.84 * H), (0.42, 0.8 * H)], hair)])
        return

    SD(head, hs1, hf0, hz, [("poly", side_short, hair)])
    ear()
    zt = ht + thick
    if style == "bun":
        b = B(hf0 + 0.1, hf0 + 0.36, hs0 + 0.2, hs0 + 0.46, zt, zt + 0.22, hair, part="bun", ol=o["_hair_ol"])
        SD(b, hs0 + 0.46, hf0 + 0.1, zt, [("rect", 0, 0.03, 0.26, 0.045, hd)])
    elif style == "ponytail":
        B(hf0 - 0.06, hf0, hs0 + 0.25, hs0 + 0.41, hz + 0.42, hz + 0.54, "coral", part="hair tie")
        B(hf0 - 0.17, hf0 - 0.06, hs0 + 0.25, hs0 + 0.41, hz - 0.02, hz + 0.56, hair, part="ponytail", ol=o["_hair_ol"])
    elif style == "pigtails":
        for s0 in (hs0 - ov - 0.18, hs1 + 0.035):
            p = B(hf0 + 0.16, hf0 + 0.38, s0, s0 + 0.18, hz + 0.3, hz + 0.52, hair, part="pigtail", ol=o["_hair_ol"])
            if s0 > 0:
                SD(p, s0 + 0.18, hf0 + 0.16, hz + 0.3, [("rect", 0, 0.17, 0.22, 0.045, "coral")])
    elif style == "spiky":
        # swept-back spikes: ramps rising towards the back of the head
        for (b0, w, hh) in ((-0.02, 0.24, 0.2), (0.21, 0.24, 0.28), (0.44, 0.24, 0.22)):
            rig.wedge(hf0 - 0.02, hf1 - 0.08, hs0 + b0, hs0 + b0 + w, zt, hh, hair, ol=o["_hair_ol"])
    elif style == "quiff":
        q = B(hf0 + 0.34, hf1 + 0.04, hs0 + 0.08, hs1 - 0.08, zt, zt + 0.12, hair, part="quiff", ol=o["_hair_ol"])
        F(q, hf1 + 0.04, hs0 + 0.08, zt, [("line", [(0.06, 0.06), (HS - 0.22, 0.06)], hd, 1.0)])


def _hat(rig, o, hf0, hs0, ht):
    B, F, SD = rig.B, rig.front, rig.side
    hf1, hs1 = hf0 + HS, hs0 + HS
    style = o["hair_style"]
    col = o["hat"] or ("brand" if style == "cap" else "gold")
    if style == "cap":
        crown = B(hf0 - 0.03, hf1, hs0 - 0.03, hs1 + 0.03, ht, ht + 0.2, col, part="cap")
        F(crown, hf1, hs0 - 0.03, ht, [("ell", HS / 2 + 0.03, 0.11, 0.055, 0.055, "paper")])
        SD(crown, hs1 + 0.03, hf0 - 0.03, ht, [("line", [(0.36, 0.02), (0.31, 0.2)], ("~", col, 0.8), 1.0)])
        B(hf1, hf1 + 0.22, hs0 + 0.06, hs1 - 0.06, ht, ht + 0.045, ("~", col, 0.85), part="cap brim")
    else:
        B(hf0 - 0.07, hf1 + 0.09, hs0 - 0.07, hs1 + 0.07, ht, ht + 0.045, col, part="hat brim")
        d = B(hf0 + 0.03, hf1 - 0.02, hs0 + 0.03, hs1 - 0.03, ht + 0.045, ht + 0.25, col, part="hat dome")
        F(d, hf1 - 0.02, hs0 + 0.03, ht + 0.045, [("rect", HS / 2 - 0.1, 0, 0.14, 0.205, ("~", col, 1.15))])


def _face(o, skin):
    """Marks on the front of the head: a across, b up, both 0..HS."""
    H, out, Fc = HS, [], "_face"
    ex, ey = (0.33 * H, 0.67 * H), 0.47 * H
    eyes, mouth = o["eyes"], o["mouth"]
    if o["beard"]:
        bc = o["beard"] if o["beard"] is not True else o["hair"]
        out.append(("poly", [(0, 0.42 * H), (0.12 * H, 0.38 * H), (0.2 * H, 0.14 * H), (0.8 * H, 0.14 * H),
                             (0.88 * H, 0.38 * H), (H, 0.42 * H), (H, 0), (0, 0)], bc))
        out.append(("poly", [(0.32 * H, 0.26 * H), (0.68 * H, 0.26 * H), (0.62 * H, 0.32 * H), (0.38 * H, 0.32 * H)], bc))
    for a in ex:
        if eyes == "happy":
            out.append(("arc", a, ey - 0.01, 0.1, -0.035, Fc, 1.6))
        elif eyes == "closed" or (eyes == "wink" and a == ex[0]):
            out.append(("arc", a, ey + 0.01, 0.1, 0.02, Fc, 1.5))
        else:
            out.append(("ell", a, ey, 0.042, 0.062, Fc))
            out.append(("ell", a + 0.014, ey + 0.026, 0.014, 0.017, "#FFFFFF"))
        if o["brows"]:
            out.append(("line", [(a - 0.055, ey + 0.11), (a + 0.055, ey + 0.125)], Fc, 1.4))
    out.append(("rect", 0.47 * H, 0.33 * H, 0.06 * H, 0.06 * H, ("~", skin, 0.86)))       # nose shadow
    mx, my = 0.5 * H, 0.22 * H
    mc = "paper" if o["beard"] else Fc
    if mouth == "smile":
        out.append(("arc", mx, my, 0.15, 0.038, mc, 1.5))
    elif mouth == "grin":
        q = [(mx - 0.085, my), (mx + 0.085, my), (mx + 0.055, my - 0.065), (mx - 0.055, my - 0.065)]
        out.append(("poly", q, "#FFFFFF"))
        out.append(("line", q + [q[0]], Fc, 1.2))
    elif mouth == "open":
        out.append(("ell", mx, my - 0.015, 0.04, 0.05, Fc))
    elif mouth == "o":
        out.append(("ring", mx, my - 0.01, 0.03, 0.035, Fc, 1.3))
    else:
        out.append(("line", [(mx - 0.06, my), (mx + 0.06, my)], mc, 1.4))
    if o["blush"]:
        out += [("ell", 0.15 * H, 0.32 * H, 0.05, 0.03, "blush", 0.85), ("ell", 0.85 * H, 0.32 * H, 0.05, 0.03, "blush", 0.85)]
    if o["glasses"]:
        g, gw = o["glasses"], 0.085
        for a in ex:
            out.append(("line", [(a - gw, ey - 0.065), (a + gw, ey - 0.065), (a + gw, ey + 0.065), (a - gw, ey + 0.065),
                                 (a - gw, ey - 0.065)], g, 1.4))
        out.append(("line", [(ex[0] + gw, ey + 0.025), (ex[1] - gw, ey + 0.025)], g, 1.4))
    return out


def _carry(rig, o, hands, sz):
    B, F = rig.B, rig.front
    carry, col = o["carry"], o["carry_color"]
    held, hc = o["holding"], o["hold_color"]
    near = hands.get(True)
    if carry and near and near[0] == "down":
        _, a0, a1, s0, s1, hb = near
        fm = (a0 + a1) / 2
        if carry in ("bag", "basket", "briefcase"):
            dep = 0.12 if carry != "basket" else 0.16
            hgt = {"bag": 0.34, "basket": 0.24, "briefcase": 0.3}[carry]
            w = {"bag": 0.3, "basket": 0.38, "briefcase": 0.42}[carry]
            top = hb - 0.06
            b = B(fm - w / 2, fm + w / 2, TD + 0.01, TD + 0.01 + dep, top - hgt, top, col, part=carry)
            sm = TD + 0.01 + dep / 2
            rig.line([(fm - w / 2 + 0.07, sm, top), (fm, sm, hb + 0.06), (fm + w / 2 - 0.07, sm, top)], ("~", col, 0.7), 1.6)
            if carry == "basket":
                rig.side(b, TD + 0.01 + dep, fm - w / 2, top - hgt, [("line", [(0.04, hgt * 0.5), (w - 0.04, hgt * 0.5)], ("~", col, 0.75), 1.0)])
            if carry == "briefcase":
                rig.side(b, TD + 0.01 + dep, fm - w / 2, top - hgt, [("rect", w / 2 - 0.04, hgt - 0.09, 0.08, 0.045, "gold")])
        elif carry == "suitcase":
            b = B(-0.62, -0.2, TD + 0.08, TD + 0.32, 0.06, 0.7, col, part="suitcase")
            rig.side(b, TD + 0.32, -0.62, 0.06, [("line", [(0.12, 0.05), (0.12, 0.58)], ("~", col, 0.75), 1.0),
                                                 ("line", [(0.3, 0.05), (0.3, 0.58)], ("~", col, 0.75), 1.0)])
            for wf in (-0.58, -0.32):
                B(wf, wf + 0.08, TD + 0.14, TD + 0.26, 0.0, 0.06, "navy", part="wheel")
            rig.line([(-0.24, TD + 0.2, 0.7), (fm, TD + 0.2, hb + 0.06)], "steel", 2)
    if held:
        c = hc or {"box": "wood", "tablet": "navy", "book": "coral", "clipboard": "wood", "cup": "paper",
                   "phone": "navy", "plate": "paper", "laptop": "steel"}.get(held, "gold")
        h = hands.get(True) or hands.get(False)
        if h and h[0] in ("hold", "lap"):
            _, a0, a1, s0, s1, ez = h
            if h[0] == "lap":
                ez = 0.24
            if held == "box":
                b = B(TW + 0.02, TW + 0.36, 0.02, TD - 0.02, ez - 0.14, ez + 0.16, c, part="box")
                F(b, TW + 0.36, 0.02, ez - 0.14, [("line", [(0, 0.22), (TD - 0.04, 0.22)], ("~", c, 0.75), 1.0)])
                rig.top(b, TW + 0.02, 0.02, ez + 0.16, [("line", [(0.17, 0), (0.17, TD - 0.04)], ("~", c, 0.75), 1.0)])
            elif held in ("tablet", "book", "clipboard", "plate", "laptop"):
                th = {"tablet": 0.035, "book": 0.08, "clipboard": 0.03, "plate": 0.03, "laptop": 0.035}[held]
                b = B(TW + 0.02, TW + 0.34, 0.03, TD - 0.03, ez, ez + th, c, part=held)
                if held == "laptop":
                    rig.top(b, TW + 0.02, 0.03, ez + th, [("rect", 0.12, 0.06, 0.16, TD - 0.18, ("~", c, 0.85))])
                    lid = B(TW + 0.02, TW + 0.05, 0.03, TD - 0.03, ez + th, ez + th + 0.24, c, part="laptop lid")
                    F(lid, TW + 0.05, 0.03, ez + th, [("ell", TD / 2 - 0.03, 0.12, 0.025, 0.025, "!paper")])
                elif held == "tablet":
                    rig.top(b, TW + 0.02, 0.03, ez + th, [("rect", 0.035, 0.035, 0.25, TD - 0.13, "!screen")])
                elif held == "clipboard":
                    rig.top(b, TW + 0.02, 0.03, ez + th, [("rect", 0.035, 0.04, 0.25, TD - 0.14, "paper"),
                                                          ("rect", 0.25, 0.2, 0.05, 0.14, "steel")])
                elif held == "book":
                    F(b, TW + 0.34, 0.03, ez, [("rect", 0.02, 0.02, TD - 0.1, 0.04, "paper")])
            elif held == "cup":
                x, y, zz = rig.w((a0 + a1) / 2, (s0 + s1) / 2, ez)
                rig.cyl((a0 + a1) / 2, (s0 + s1) / 2, ez, 0.065, 0.15, c,
                        bands=((zz + 0.05 * rig.k, zz + 0.1 * rig.k, "amber"),), n=16)
        elif h and h[0] == "phone":
            _, a0, a1, s0, s1, ez = h
            ph = B(a0 + 0.02, a0 + 0.06, s0 - 0.08, s0 + 0.06, ez, ez + 0.22, c, part="phone")
            F(ph, a0 + 0.06, s0 - 0.08, ez, [("ell", 0.03, 0.17, 0.014, 0.014, "steel")])


# ── output helpers ───────────────────────────────────────────────────────
LAST_REPORT = {}      # filled by write_pair: layering stats and interpenetrating parts


def write_pair(build, name, outdir, title="", desc="", preview=True, check=True, **scene_kw):
    """build(scene). Writes <name>-dark.svg and <name>-light.svg (transparent),
    plus <name>-<theme>-preview.png on each theme's --bg and
    <name>-gridcheck.png (light art with the lattice over it). Prints the
    layering stats and any interpenetrating parts (fix those)."""
    os.makedirs(outdir, exist_ok=True)
    paths = []
    for theme in ("dark", "light"):
        sc = Scene(**scene_kw); build(sc)
        svg = sc.svg(theme, title=title or name, desc=desc)
        fp = os.path.join(outdir, "%s-%s.svg" % (name, theme))
        open(fp, "w").write(svg); paths.append(fp)
        if preview:
            _png(svg, fp[:-4] + "-preview.png", PALETTES[theme]["_bg"], 2)
    if check:
        bad = sc.check()
        LAST_REPORT.clear()
        LAST_REPORT.update(sc.stats, interpenetrating=bad)
        print("%s: %d units, %d overlapping pairs (%d by geometry), %d cycles broken, %d interpenetrating"
              % (name, sc.stats["units"], sc.stats["pairs"], sc.stats["exact_tests"], sc.stats["cycles"], len(bad)))
        for a, b in bad[:20]:
            print("  passes through:", a, "|", b)
        for a in sc.cycle_units[:10]:
            print("  in a cycle:", a.items[0].tag or a.items[0].kind, [round(v, 2) for v in a.bb])
    if preview:
        sc = Scene(**scene_kw); build(sc)
        _png(sc.svg("light", grid_overlay=True), os.path.join(outdir, "%s-gridcheck.png" % name), PALETTES["light"]["_bg"], 2)
        _png(sc.plan_svg(), os.path.join(outdir, "%s-plan.png" % name), "#FFFFFF", 1.5)
    return paths


def _png(svg, path, bg, scale):
    try:
        import cairosvg
        cairosvg.svg2png(bytestring=svg.encode(), write_to=path, background_color=bg, scale=scale)
    except Exception as e:
        print("preview skipped:", e)


def write_gif(build_t, name, outdir, frames=36, fps=12, title="", scale=1.25, colors=160, **scene_kw):
    """build_t(scene, t), t in [0,1). Writes <name>-dark.gif and <name>-light.gif
    on one fixed canvas (union of all frames), flattened on the theme --bg."""
    import cairosvg
    from PIL import Image
    os.makedirs(outdir, exist_ok=True)
    paths = []
    for theme in ("dark", "light"):
        bodies, U = [], [1e9, 1e9, -1e9, -1e9]
        for i in range(frames):
            sc = Scene(**scene_kw); build_t(sc, i / frames)
            body, v = sc._render(theme)
            bodies.append(body)
            U = [min(U[0], v[0]), min(U[1], v[1]), max(U[2], v[0] + v[2]), max(U[3], v[1] + v[3])]
        view = (U[0], U[1], U[2] - U[0], U[3] - U[1])
        imgs = []
        for body in bodies:
            png = cairosvg.svg2png(bytestring=_wrap(body, view, theme, title or name, "", False, sc._style(theme)).encode(),
                                   background_color=PALETTES[theme]["_bg"], scale=scale)
            imgs.append(Image.open(io.BytesIO(png)).convert("RGB"))
        strip = Image.new("RGB", (imgs[0].width, imgs[0].height * 3))
        for k, im in enumerate(imgs[::max(1, frames // 3)][:3]):
            strip.paste(im, (0, im.height * k))
        pal_img = strip.quantize(colors=colors, method=Image.Quantize.MEDIANCUT)
        q = [im.quantize(palette=pal_img, dither=Image.Dither.NONE) for im in imgs]
        fp = os.path.join(outdir, "%s-%s.gif" % (name, theme))
        q[0].save(fp, save_all=True, append_images=q[1:], duration=int(1000 / fps), loop=0, disposal=1)
        paths.append(fp)
    return paths
