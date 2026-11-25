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

TUBES AND PEOPLE. Scene.tube() draws rounded, tapered segments (limbs, hoses)
that sort as one unit by their axes. People (people.py) are tubes, faceted
lofts and paint clipped to each facet, in one soft outline group: ink on the
outer silhouette, a thin shade line where a part passes in front of another,
nothing where parts meet at the same depth.

OBJECTS. Build each thing once in its own space (a function model(m, ...),
front facing +x, details on every side, anchors for people and cables) and
place it: s.place(model, x, y, z, rot=0|90|180|270, mirror, scale). The
object is a group for building and arranging only; its parts still sort one
by one. models.py holds the library; sheet.py draws objects alone.
"""
import math, heapq, os, io
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
        "eyewhite": "#FFFFFF", "iris": "#5B3A24", "lip": "#C9776C", "mouth": "#6B2A2E",
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
        "eyewhite": "#DCE3EE", "iris": "#4A2E1C", "lip": "#A65E56", "mouth": "#4A1C20",
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


def _unit3(v):
    n = math.sqrt(v[0] * v[0] + v[1] * v[1] + v[2] * v[2])
    return (v[0] / n, v[1] / n, v[2] / n) if n > 1e-12 else (0.0, 0.0, 1.0)


def _perp_basis(d):
    a = (1.0, 0.0, 0.0) if abs(d[0]) < 0.9 else (0.0, 1.0, 0.0)
    e1 = _unit3((d[1] * a[2] - d[2] * a[1], d[2] * a[0] - d[0] * a[2], d[0] * a[1] - d[1] * a[0]))
    e2 = (d[1] * e1[2] - d[2] * e1[1], d[2] * e1[0] - d[0] * e1[2], d[0] * e1[1] - d[1] * e1[0])
    return e1, e2


def _tube_end(P, r, Q, e, n=16):
    """Screen points (unit 1) of one end of a tube segment: the sphere's
    outline, or the rim of a flat end facing away from Q."""
    if e == "r" or (abs(P[0] - Q[0]) + abs(P[1] - Q[1]) + abs(P[2] - Q[2])) < 1e-9:
        cx, cy = _S(*P)
        R = r * 1.2247449
        return [(cx + R * math.cos(2 * math.pi * i / n), cy + R * math.sin(2 * math.pi * i / n)) for i in range(n)]
    d = _unit3((P[0] - Q[0], P[1] - Q[1], P[2] - Q[2]))
    e1, e2 = _perp_basis(d)
    out = []
    for i in range(n):
        t = 2 * math.pi * i / n
        c, s = math.cos(t) * r, math.sin(t) * r
        out.append(_S(P[0] + c * e1[0] + s * e2[0], P[1] + c * e1[1] + s * e2[1], P[2] + c * e1[2] + s * e2[2]))
    return out


def _tube_facet(sg):
    A, ra, B, rb, mat, ea, eb = sg[:7]
    f = _Facet(); f.kind = "t"
    f.poly = _hull(_tube_end(A, ra, B, ea) + _tube_end(B, rb, A, eb))
    f.bb = _bbox2(f.poly)
    (ax, ay), (bx, by) = _S(*A), _S(*B)
    dx, dy = bx - ax, by - ay
    bias = 0.8 * max(ra, rb)
    f.k = (ax, ay, dx, dy, dx * dx + dy * dy, sum(A) + bias, sum(B) + bias)
    return f


def _halfplane(poly, o, m, off):
    """The part of a convex polygon where (p - o) . m >= off."""
    out = []
    n = len(poly)
    for i in range(n):
        p, q = poly[i], poly[(i + 1) % n]
        dp = (p[0] - o[0]) * m[0] + (p[1] - o[1]) * m[1] - off
        dq = (q[0] - o[0]) * m[0] + (q[1] - o[1]) * m[1] - off
        if dp >= 0:
            out.append(p)
        if (dp >= 0) != (dq >= 0):
            t = dp / (dp - dq)
            out.append((p[0] + (q[0] - p[0]) * t, p[1] + (q[1] - p[1]) * t))
    return out


def _runs_svg(runs, scr, hard, soft):
    """Contour runs (edge, t0, t1, cls) along a closed polygon, joined into
    as few polylines as possible."""
    n = len(scr)
    paths, cur = [], None
    for i, t0, t1, cls in runs:
        (ax, ay), (bx, by) = scr[i], scr[(i + 1) % n]
        p0 = (ax + (bx - ax) * t0, ay + (by - ay) * t0)
        p1 = (ax + (bx - ax) * t1, ay + (by - ay) * t1)
        full = t0 < 1e-9 and t1 > 1 - 1e-9
        if cur and cur[0] == cls and cur[2] == (i - 1, 1.0) and t0 < 1e-9:
            cur[1].append(p1)
            cur[3] = cur[3] or full
        else:
            cur = [cls, [p0, p1], None, full]
            paths.append(cur)
        cur[2] = (i, 1.0) if t1 > 1 - 1e-9 else (i, t1)
    if len(paths) > 1:
        f, l = paths[0], paths[-1]
        if f[0] == l[0] and l[2] == (n - 1, 1.0) and abs(f[1][0][0] - l[1][-1][0]) < 1e-6 and abs(f[1][0][1] - l[1][-1][1]) < 1e-6:
            l[1].extend(f[1][1:]); paths.pop(0)
    out = []
    for cls, pts, _, full in paths:
        if not full and sum(math.hypot(b[0] - a[0], b[1] - a[1]) for a, b in zip(pts, pts[1:])) < 3.0:
            continue                                  # a stub at a corner, not a contour
        out.append('<polyline points="%s" fill="none"%s/>' % (_pl(pts), hard if cls == 2 else soft))
    return "".join(out)


def _shade_n(n, st, sl, sr):
    t = abs(n[0]) + abs(n[1]) + abs(n[2]) or 1
    return (sr * abs(n[0]) + sl * abs(n[1]) + st * abs(n[2])) / t


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
    __slots__ = ("kind", "data", "marks", "atom", "tag", "box", "bb", "local", "T", "ol", "tf")

    def __init__(self, kind, data, tag):
        self.kind, self.data, self.marks, self.atom, self.tag, self.box = kind, data, [], None, tag, None
        self.bb, self.local, self.T, self.ol, self.tf = None, None, None, None, None


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
        self._softol = set()
        self._olw = {}
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
    def outline(self, key=None, soft=False, width=None):
        """Parts made inside share ONE border: the ink line runs only round
        the outside of the whole (its silhouette, and where it meets other
        things), not along the seams where its own boxes meet. Use it for
        anything soft or continuous that is modelled from several boxes: a
        hijab, a head of hair, an arm, a tree's crown, a cushion. Pass the
        same key (new_outline()) to join parts made in different places."""
        key = key or self.new_outline()
        if soft:
            self._softol.add(key)
        if width is not None:
            self._olw[key] = width
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

    def tube(self, segs, mat=None):
        """A rounded limb: a chain of tapered segments, each one the hull of two
        spheres (or a sphere and a flat disc). segs: [(A, ra, B, rb, mat, endA,
        endB), ...] with A, B world points and ra, rb radii in units. Ends:
        'r' round, 'f' flat (a seam inside a limb, no line), 'h' flat with a
        hem line, 'o' an opening (a sleeve or trouser end: hem line, and the
        dark inside when it faces the viewer). A zero-length segment is a
        sphere. The chain is ONE sortable unit, filled with three-tone shading
        and inked only round its outer silhouette (softly where it passes in
        front of another part of the same outline group)."""
        fs, tf = [], []
        xs, ys, zs = [], [], []
        for sg in segs:
            A, ra, B, rb = sg[0], sg[1], sg[2], sg[3]
            for P, r in ((A, ra), (B, rb)):
                xs += [P[0] - r, P[0] + r]; ys += [P[1] - r, P[1] + r]; zs += [P[2] - r, P[2] + r]
            f = _tube_facet(sg)
            fs.append(f); tf.append(f)
        it = self._emit("tube", [tuple(s) for s in segs], (min(xs), max(xs), min(ys), max(ys), min(zs), max(zs)), fs)
        it.tf = tf
        return it

    def shadow_poly(self, pts):
        """A soft floor shadow of any outline (world points on one plane)."""
        xs, ys, zs = zip(*pts)
        return self._emit("shadowp", tuple(pts), (min(xs), max(xs), min(ys), max(ys), min(zs), max(zs)),
                          [_plane_facet(pts)], boxlike=True)

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

    def _put_mark(self, A, U, V, side, shapes, on, clip=False):
        """side: 'r', 'l', 't', or the face's world normal (shaded like the face).
        clip: keep the marks inside the face they sit on (polys only)."""
        it = on or self._find_face(A, side, U, V) or self._last
        if it is None:
            it = self._emit("none", None, (A[0], A[0], A[1], A[1], A[2], A[2]), [])
        it.marks.append((tuple(A), tuple(U), tuple(V), side, shapes, clip))

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
               tie=None, bottom="pants", skirt=None, shorts=False, shoe="shoe", eyes="dot", mouth="smile",
               brows=True, blush=False, glasses=None, beard=None, eye_color="iris", carry=None,
               carry_color="gold", hat=None, walk=0.0, sit=None, pose="down", arms=None, lean=None,
               nod=None, air=None, holding=None, hold_color=None):
        """A person. See references/characters.md for every option.
        (x, y, z) is the back corner of the standing footprint; z is the floor,
        or the seat top when sit=<seat height>. About 0.85 x 0.7 units on the
        floor and 2.5 units tall at h=1. pose: an arm pose (down, hold, phone,
        point, wave, cheer, hips, think) or a whole-body pose (run, jump,
        squat, kneel, floor, lie, sleep); arms= overrides the arms of any pose."""
        inst = _open(self, "person", None)
        inst.kind, inst.facing = "person", facing
        _draw_person(self, x, y, z, dict(facing=facing, h=h, skin=skin, hair=hair, hair_style=hair_style, top=top,
                                         outfit=outfit, inner=inner, sleeve=sleeve, tie=tie, bottom=bottom, skirt=skirt,
                                         shorts=shorts, shoe=shoe, eyes=eyes, mouth=mouth, brows=brows, blush=blush,
                                         glasses=glasses, beard=beard, eye_color=eye_color, carry=carry,
                                         carry_color=carry_color, hat=hat, walk=walk, sit=sit, pose=pose, arms=arms,
                                         lean=lean, nod=nod, air=air, holding=holding, hold_color=hold_color))
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
            if it.ol in self._softol:
                q = " ".join("%.1f,%.1f" % self.p(*t) for t in wpts)
                return '<polygon points="%s" fill="%s" stroke="%s" stroke-width="0.6"/>' % (q, fill, fill)
            return self._face_svg([self.p(*q) for q in wpts], fill, op, stroke)
        soft_grp = it.ol in self._softol
        scr = [self.p(*q) for q in wpts] if soft_grp else self._pts([self.p(*q) for q in wpts])
        opa = "" if op == 1 else ' fill-opacity="%.2f"' % op
        seam = (' stroke="%s" stroke-width="0.7"' % fill) if op == 1 else ""      # close anti-aliasing gaps
        out = ['<polygon points="%s" fill="%s"%s%s/>' % (_pl(scr), fill, seam, opa)]
        n = len(scr)
        if it.ol in self._softol:
            runs = self._contours(it, _plane_facet(wpts), [_S(*q) for q in wpts], skip={(id(it), k)})
            self._late.append(_runs_svg(runs, scr, self._hard_style(it.ol), self._soft_style(fill, it.ol)))
            return "".join(out)
        for i, t0, t1 in self._silhouette(it, k, wpts):
            (ax, ay), (bx, by) = scr[i], scr[(i + 1) % n]
            out.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" class="k"/>'
                       % (ax + (bx - ax) * t0, ay + (by - ay) * t0, ax + (bx - ax) * t1, ay + (by - ay) * t1))
        return "".join(out)

    def _soft_style(self, fill, ol=None):
        return ' stroke="%s" stroke-width="%.2f"' % (shade(fill, 0.66), self.stroke * 0.62 * self._olw.get(ol, 1.0))

    def _hard_style(self, ol):
        w = self._olw.get(ol)
        return ' class="k"' if w is None else ' class="k" stroke-width="%.2f"' % (self.stroke * w)

    def _contours(self, it, me, poly, skip=(), own=()):
        """For a soft outline group (a person): stretches (edge, t0, t1, cls) of
        a shape's edges that need a line. cls 2: the outer silhouette (ink);
        cls 1: the shape passes in front of another part of the same group
        (a thin line in a darker shade of its own colour). Where the group
        continues at the same depth (hair into forehead, shirt into sleeve)
        there is no line at all. `own`: convex pieces of the same shape (a
        tube's other segments): no line inside them."""
        n = len(poly)
        if me is None:
            return [(i, 0.0, 1.0, 2) for i in range(n)]
        others = [f for key, f in self._group_faces(it.ol) if key not in skip]
        eps = 1.4 / self.u
        tol = 0.1
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
            N = max(2, int(L * self.u / 3))
            cl = []
            for j in range(N):
                t = (j + 0.5) / N
                qx, qy = ax + (bx - ax) * t + nx * eps, ay + (by - ay) * t + ny * eps
                cls = 2
                if any(_inside(p, qx, qy) for p in own):
                    cls = 0
                else:
                    ex, ey = qx - nx * eps, qy - ny * eps          # on the edge itself
                    d0 = me.depth(ex, ey)
                    for f in others:
                        b = f.bb
                        if b[0] <= qx <= b[2] and b[1] <= qy <= b[3] and _inside(f.poly, qx, qy):
                            if abs(f.depth(ex, ey) - d0) < tol:
                                cls = 0
                                break
                            cls = 1
                cl.append(cls)
            # a lone sample that flips class is noise at a corner, not a change of contour
            if N >= 3:
                for j in range(N):
                    prv = cl[j - 1] if j > 0 else cl[j + 1]
                    nxt = cl[j + 1] if j < N - 1 else cl[j - 1]
                    if cl[j] != prv and prv == nxt:
                        cl[j] = prv
            run, rc = None, 0
            for j in range(N + 1):
                cls = cl[j] if j < N else -1
                if run is not None and cls != rc:
                    if rc > 0:
                        out.append((i, run, j / N, rc))
                    run = None
                if run is None and cls > 0:
                    run, rc = j / N, cls
        return out

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
                elif it2.kind == "tube":
                    for k2, f in enumerate(it2.tf):
                        self._olfaces.setdefault(it2.ol, []).append(((id(it2), 1000 + k2), f))
                    continue
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
        self._clipn = 0
        o = []
        P = self.p
        self._late = []                 # a person's contour lines go on top of the paint on its face
        for g in self._order():
            for it in g.items:
                kind, d = it.kind, it.data
                self._late = []
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
                    kk = _normal_shade(pts, st, sl, sr)
                    if it.ol in self._softol:
                        kk = 1 + (kk - 1) * 0.7
                    o.append(self._face(it, 0, pts, shade(self._c(mat), kk), op, strk))
                elif kind == "cyl":
                    o.append(self._cyl(*d))
                elif kind == "cloud":
                    o.append(self._cloud(*d))
                elif kind == "tube":
                    o.append(self._tube_svg(it, d))
                elif kind == "shadowp":
                    q = " ".join("%.1f,%.1f" % P(*t) for t in d)
                    o.append('<polygon points="%s" fill="%s" fill-opacity="%.2f"/>' % (q, pal["_shadow"], pal["_shadow_op"]))
                for m in it.marks:
                    side = m[3]
                    sk = _shade_n(side, st, sl, sr) if isinstance(side, tuple) else {"r": sr, "l": sl, "t": st}[side]
                    if isinstance(side, tuple) and it.ol in self._softol:
                        sk = 1 + (sk - 1) * 0.7
                    svg = self._marks(*m[:5], shade_k=sk)
                    if len(m) > 5 and m[5] and kind == "poly":
                        self._clipn += 1
                        cid = "c%d" % self._clipn
                        q = _pl([self.p(*t) for t in d[0]] if it.ol in self._softol else self._pts([self.p(*t) for t in d[0]]))
                        svg = '<clipPath id="%s"><polygon points="%s"/></clipPath><g clip-path="url(#%s)">%s</g>' % (cid, q, cid, svg)
                    o.append(svg)
                o.extend(self._late)
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
            elif k == "spoly":
                _, pts, m = s[:3]
                c_ = col(m)
                out.append('<polygon points="%s" fill="%s" stroke="%s" stroke-width="0.7"/>' % (_pl([P(a, b) for a, b in pts]), c_, c_))
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

    def _tube_svg(self, it, segs):
        st, sl, sr = self._pal["_shade"]
        u = self.u
        bb = self._bb
        parts = []
        for k, sg in enumerate(segs):
            A, ra, B, rb, mat, ea, eb = sg[:7]
            hull = it.tf[k].poly
            for x, y in hull:
                X, Y = x * u, y * u
                if X < bb[0]: bb[0] = X
                if Y < bb[1]: bb[1] = Y
                if X > bb[2]: bb[2] = X
                if Y > bb[3]: bb[3] = Y
            parts.append(((sum(A) + sum(B)) / 2, k, sg, hull))
        parts.sort(key=lambda q: (q[0], q[1]))
        out = []
        for _, k, sg, hull in parts:
            A, ra, B, rb, mat, ea, eb = sg[:7]
            c = self._c(mat)
            base, dark, light = shade(c, sl), shade(c, sr), shade(c, st)
            px = [(x * u, y * u) for x, y in hull]
            out.append('<polygon points="%s" fill="%s" stroke="%s" stroke-width="0.6"/>' % (_pl(px), base, base))
            a2, b2 = _S(*A), _S(*B)
            dx, dy = b2[0] - a2[0], b2[1] - a2[1]
            L = math.hypot(dx, dy)
            if L > 1e-6:
                m = (-dy / L, dx / L)
                if m[0] + 0.35 * m[1] < 0:
                    m = (-m[0], -m[1])
            else:
                m = (0.944, 0.33)
            R = min(ra, rb) * 1.2247
            o2 = (a2[0], a2[1])
            dk = _halfplane(hull, o2, m, 0.12 * R)
            if len(dk) >= 3:
                out.append('<polygon points="%s" fill="%s"/>' % (_pl([(x * u, y * u) for x, y in dk]), dark))
            lt = _halfplane(hull, o2, (-m[0], -m[1]), 0.5 * R)
            if len(lt) >= 3:
                out.append('<polygon points="%s" fill="%s"/>' % (_pl([(x * u, y * u) for x, y in lt]), light))
            for P, Q, r, e in ((B, A, rb, eb), (A, B, ra, ea)):
                if e not in ("h", "o") or r <= 0:
                    continue
                d = _unit3((P[0] - Q[0], P[1] - Q[1], P[2] - Q[2]))
                e1, e2 = _perp_basis(d)
                faces = d[0] + d[1] + d[2] > 0
                ring = []
                for i in range(25):
                    t = 2 * math.pi * i / 24
                    v = (math.cos(t) * e1[0] + math.sin(t) * e2[0], math.cos(t) * e1[1] + math.sin(t) * e2[1],
                         math.cos(t) * e1[2] + math.sin(t) * e2[2])
                    ring.append(((P[0] + r * v[0], P[1] + r * v[1], P[2] + r * v[2]), v[0] + v[1] + v[2]))
                if faces and e == "o":
                    out.append('<polygon points="%s" fill="%s"/>' % (_pl([self.p(*q) for q, _ in ring[:-1]]), shade(c, 0.5)))
                    out.append('<polyline points="%s" fill="none"%s/>' % (_pl([self.p(*q) for q, _ in ring]), self._soft_style(base, it.ol)))
                elif not faces:
                    run = []
                    for q, vis in ring:
                        if vis > 0:
                            run.append(self.p(*q))
                        elif len(run) > 1:
                            out.append('<polyline points="%s" fill="none"%s/>' % (_pl(run), self._soft_style(base, it.ol))); run = []
                        else:
                            run = []
                    if len(run) > 1:
                        out.append('<polyline points="%s" fill="none"%s/>' % (_pl(run), self._soft_style(base, it.ol)))
        # the outline: ink round the silhouette, soft where it passes over its own figure
        soft_grp = it.ol in self._softol
        for k, sg in enumerate(segs):
            hull = it.tf[k].poly
            own = [it.tf[j].poly for j in range(len(segs)) if j != k]
            if soft_grp:
                runs = self._contours(it, it.tf[k], hull, skip={(id(it), 1000 + j) for j in range(len(segs))}, own=own)
            else:
                runs = []
                for i, t0, t1, cls in self._contours_plain(hull, own):
                    runs.append((i, t0, t1, cls))
            base = shade(self._c(sg[4]), sl)
            out.append(_runs_svg(runs, [(x * u, y * u) for x, y in hull], self._hard_style(it.ol) + ' stroke-linecap="butt"',
                                 self._soft_style(base, it.ol) + ' stroke-linecap="butt"'))
        return "".join(out)

    def _contours_plain(self, poly, own):
        """Edges of one tube segment that are not inside its other segments."""
        out = []
        n = len(poly)
        eps = 1.4 / self.u
        cx = sum(p[0] for p in poly) / n; cy = sum(p[1] for p in poly) / n
        for i in range(n):
            (ax, ay), (bx, by) = poly[i], poly[(i + 1) % n]
            L = math.hypot(bx - ax, by - ay)
            if L < 1e-9:
                continue
            nx, ny = (by - ay) / L, -(bx - ax) / L
            if (ax - cx) * nx + (ay - cy) * ny < 0:
                nx, ny = -nx, -ny
            N = max(2, int(L * self.u / 3))
            run = None
            for j in range(N + 1):
                ok = False
                if j < N:
                    t = (j + 0.5) / N
                    qx, qy = ax + (bx - ax) * t + nx * eps, ay + (by - ay) * t + ny * eps
                    ok = not any(_inside(p, qx, qy) for p in own)
                if ok and run is None:
                    run = j / N
                elif not ok and run is not None:
                    out.append((i, run, j / N, 2)); run = None
        return out

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


# ══ the character rig: people.py ════════════════════════════════════════
from people import FACINGS, TW, TD, draw as _draw_person  # noqa: E402


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
