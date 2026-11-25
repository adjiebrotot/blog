"""
people.py - the character rig (v4) for iso.py. See ../references/characters.md.

A person is built in BODY space and mapped to the world through a stack of
transforms, so the same parts serve standing, walking, sitting, squatting,
kneeling, jumping and lying down:

  body space   f forward (the way the person faces), s sideways towards the
               viewer's side, z up; origin at the back corner of the standing
               footprint, floor at z = 0, measures at h = 1.
  pose         the pelvis moves and the upper body leans about the hips;
               lying poses turn the whole body onto its back or side.
  world        Scene coordinates (facing, scale h, position).

Parts:
  * limbs, neck, hands and hair locks are TUBES (Scene.tube): rounded, tapered,
    with three-tone shading; joints are solved with two-bone IK, so a limb can
    point anywhere;
  * torso, garments, head, hair volume, shoes and held things are SOLIDS:
    lofts of rounded rings, faceted so the shading reads as a curved surface;
  * details (face, hairline, collars, buttons, patterns) are PAINTED on the
    facets from body-space charts and clipped to each facet, so a pattern runs
    on across a curved torso and a hairline round a curved head.

The whole person is ONE soft outline group: ink only on the outer silhouette,
a thin line in a darker shade of a part's own colour where it passes in front
of another part, and no line where parts meet at the same depth (hair into the
forehead, sleeve into the shirt, thigh into the hips).
"""
import math
from contextlib import contextmanager

# ── measures (h = 1) ────────────────────────────────────────────────────────
TW, TD = 0.32, 0.60          # standing footprint of the torso (anchors, person_center)
CF, CS = 0.16, 0.30          # body centre line
HIP_Z, HIP_S = 0.98, 0.14    # hip joints at CS +- HIP_S
THIGH, SHIN = 0.45, 0.44
ANKLE_Z = 0.10
SH_Z, SH_S = 1.63, 0.33      # shoulder joints at CS +- SH_S
UPPER, FORE = 0.35, 0.29
HEAD_Z = 1.80                # chin
HEAD_F = CF + 0.01           # head centre (f)
FACE_F = 0.33                # the face plane, from the head centre

FACINGS = {   # facing: (forward axis, side axis) as unit vectors in (x, y)
    "r": ((1, 0), (0, 1)), "dr": ((1, 0), (0, 1)),
    "l": ((0, 1), (1, 0)), "dl": ((0, 1), (1, 0)),
    "ul": ((-1, 0), (0, 1)),
    "ur": ((0, -1), (1, 0)),
}

SHORT_SLEEVES = ("tee", "polo", "hivis", "dress", "apron", "batik_short")
TUCKED = ("shirt", "polo", "suit")
OPEN_FRONT = ("suit", "jacket", "cardigan")
LONG_HEM = ("suit", "jacket", "cardigan")

# head: rings from the chin up (z, front, back, half width, front corner r, back corner r)
HEAD = [(0.00, 0.20, 0.05, 0.11, 0.07, 0.04),
        (0.10, 0.30, 0.22, 0.245, 0.11, 0.14),
        (0.28, 0.33, 0.31, 0.31, 0.13, 0.18),
        (0.50, 0.33, 0.33, 0.32, 0.14, 0.20),
        (0.64, 0.29, 0.30, 0.29, 0.14, 0.19),
        (0.72, 0.18, 0.20, 0.18, 0.10, 0.11)]
HEAD_H = 0.72


# ── small vector helpers ───────────────────────────────────────────────────
def add(a, b): return (a[0] + b[0], a[1] + b[1], a[2] + b[2])
def sub(a, b): return (a[0] - b[0], a[1] - b[1], a[2] - b[2])
def mul(a, k): return (a[0] * k, a[1] * k, a[2] * k)
def dot(a, b): return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]
def cross(a, b): return (a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0])
def norm(a): return math.sqrt(dot(a, a))
def lerp(a, b, t): return (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t, a[2] + (b[2] - a[2]) * t)
def mirror(p): return (p[0], 2 * CS - p[1], p[2])        # across the body's centre plane


def unit(a):
    n = norm(a)
    return mul(a, 1 / n) if n > 1e-12 else (0.0, 0.0, 0.0)


def clamp(v, a=0.0, b=1.0):
    return a if v < a else b if v > b else v


class Xf:
    """Affine map p -> M p + t on (f, s, z)."""
    __slots__ = ("M", "t")

    def __init__(self, M=((1, 0, 0), (0, 1, 0), (0, 0, 1)), t=(0.0, 0.0, 0.0)):
        self.M, self.t = M, t

    def __call__(self, p):
        M = self.M
        return (M[0][0] * p[0] + M[0][1] * p[1] + M[0][2] * p[2] + self.t[0],
                M[1][0] * p[0] + M[1][1] * p[1] + M[1][2] * p[2] + self.t[1],
                M[2][0] * p[0] + M[2][1] * p[1] + M[2][2] * p[2] + self.t[2])

    def vec(self, v):
        M = self.M
        return tuple(M[i][0] * v[0] + M[i][1] * v[1] + M[i][2] * v[2] for i in range(3))

    def after(self, inner):
        """self o inner: apply inner first."""
        A, B = self.M, inner.M
        M = tuple(tuple(sum(A[i][k] * B[k][j] for k in range(3)) for j in range(3)) for i in range(3))
        return Xf(M, add(self.vec(inner.t), self.t))


def move(d):
    return Xf(t=tuple(d))


def pitch(a, pivot):
    """Turn about the s axis through pivot; a > 0 tips the top forward (+f)."""
    c, s = math.cos(a), math.sin(a)
    M = ((c, 0, s), (0, 1, 0), (-s, 0, c))
    r = Xf(M)
    return move(pivot).after(r).after(move(mul(pivot, -1)))


def scale(k, pivot):
    return move(pivot).after(Xf(((k, 0, 0), (0, k, 0), (0, 0, k)))).after(move(mul(pivot, -1)))


def ik(S, T, a, b, pole):
    """Two-bone IK: the joint between bones a and b, bending towards pole."""
    d = sub(T, S)
    L = clamp(norm(d), abs(a - b) + 1e-4, a + b - 1e-4)
    u = unit(d)
    if u == (0.0, 0.0, 0.0):
        u = (0.0, 0.0, -1.0)
    ca = (a * a + L * L - b * b) / (2 * a * L)
    sa = math.sqrt(max(0.0, 1 - ca * ca))
    w = sub(pole, mul(u, dot(pole, u)))
    if norm(w) < 1e-6:
        w = cross(u, (0, 1, 0)) if abs(u[1]) < 0.9 else cross(u, (1, 0, 0))
    w = unit(w)
    E = add(S, add(mul(u, a * ca), mul(w, a * sa)))
    return E, add(S, mul(u, L))


def rring(c, ea, eb, a0, a1, b0, b1, rad, m):
    """A rounded rectangle in the plane through c spanned by ea, eb: a from -a0
    to a1, b from -b0 to b1; rad = corner radii at (+a,+b), (-a,+b), (-a,-b),
    (+a,-b); m arc steps per corner (1 = a chamfer)."""
    corners = ((a1, b1, 1, 1), (-a0, b1, -1, 1), (-a0, -b0, -1, -1), (a1, -b0, 1, -1))
    pts = []
    for ci, (ca, cb, sa, sb) in enumerate(corners):
        r = min(rad[ci], (a0 + a1) / 2 - 1e-4, (b0 + b1) / 2 - 1e-4)
        ccx, ccy = ca - sa * r, cb - sb * r
        for i in range(m + 1):
            ang = math.radians(90 * ci + 90 * i / m)
            x, y = ccx + r * math.cos(ang), ccy + r * math.sin(ang)
            pts.append(add(c, add(mul(ea, x), mul(eb, y))))
    return pts


def hring(cf, cs, z, front, back, hw, rf, rb, m):
    """A horizontal rounded ring around (cf, cs) at height z."""
    return rring((cf, cs, z), (1, 0, 0), (0, 1, 0), back, front, hw, hw, (rf, rb, rb, rf), m)


def head_dims(z):
    """HEAD interpolated at height z (from the chin)."""
    rows = HEAD
    if z <= rows[0][0]:
        return rows[0][1:]
    for r0, r1 in zip(rows, rows[1:]):
        if r0[0] <= z <= r1[0]:
            t = (z - r0[0]) / (r1[0] - r0[0])
            return tuple(a + (b - a) * t for a, b in zip(r0[1:], r1[1:]))
    return rows[-1][1:]


def keys(*kf):
    """Piecewise-linear function of the angle round the head (degrees; 0 is the
    face, 180 the back). kf: (angle, value) pairs over 0..180, symmetric."""
    def f(th):
        a = abs(th)
        for (a0, v0), (a1, v1) in zip(kf, kf[1:]):
            if a0 <= a <= a1:
                return v0 + (v1 - v0) * (a - a0) / ((a1 - a0) or 1)
        return kf[-1][1] if a > kf[-1][0] else kf[0][1]
    return f


# ── the rig: drawing in body space ─────────────────────────────────────────
class Face:
    __slots__ = ("it", "b", "n", "w", "bot", "top")


class Rig:
    def __init__(self, sc, X, Y, Z, facing, k, tag, ol):
        if facing not in FACINGS:
            raise ValueError("facing must be one of r, l, ul, ur (got %r)" % (facing,))
        self.sc, self.X, self.Y, self.Z, self.k, self.tag, self.ol = sc, X, Y, Z, k, tag, ol
        self.FX, self.SX = FACINGS[facing]
        self.away = self.FX[0] < 0 or self.FX[1] < 0
        self.T = Xf()
        self.wk = max(0.5, min(1.3, sc.u * k / 34))

    def L(self, p):
        """Local frame (after pose transforms) -> world."""
        F, S, Zl = p
        k, (fx, fy), (sx, sy) = self.k, self.FX, self.SX
        return (self.X + (F * fx + S * sx) * k, self.Y + (F * fy + S * sy) * k, self.Z + Zl * k)

    def W(self, p):
        return self.L(self.T(p))

    @contextmanager
    def xf(self, X):
        old = self.T
        self.T = old.after(X)
        try:
            yield
        finally:
            self.T = old

    # primitives ────────────────────────────────────────────────────────────
    def tube(self, segs, part="limb"):
        """segs: (A, ra, B, rb, mat, endA, endB) in body space."""
        w = [(self.W(a), ra * self.k, self.W(b), rb * self.k, m, ea, eb) for a, ra, b, rb, m, ea, eb in segs]
        with self.sc.tag("%s %s" % (self.tag, part)), self.sc.outline(self.ol, soft=True):
            return self.sc.tube(w)

    def chain(self, nodes, mat, ends=("r", "r"), part="limb"):
        """A one-colour tube through [(p, r), ...]."""
        segs = []
        for i, ((a, ra), (b, rb)) in enumerate(zip(nodes, nodes[1:])):
            segs.append((a, ra, b, rb, mat, ends[0] if i == 0 else "f", ends[1] if i == len(nodes) - 2 else "f"))
        return self.tube(segs, part)

    def ball(self, p, r, mat, part="ball"):
        return self.tube([(p, r, p, r, mat, "r", "r")], part)

    def solid(self, rings, mat, top=None, bottom=None, part="solid", stroke=True):
        """A loft through rings (lists of body points, same count). mat: one
        material or one per band; top/bottom: cap materials (None: open)."""
        allp = [p for r in rings for p in r]
        cen = mul(tuple(map(sum, zip(*allp))), 1 / len(allp))
        cw = self.W(cen)
        faces = []
        sc = self.sc
        with sc.tag("%s %s" % (self.tag, part)), sc.outline(self.ol, soft=True):
            for i in range(len(rings) - 1):
                m_ = mat[i] if isinstance(mat, list) else mat
                A, B = rings[i], rings[i + 1]
                n = len(A)
                for j in range(n):
                    q = [A[j], A[(j + 1) % n], B[(j + 1) % n], B[j]]
                    if norm(sub(q[0], q[1])) < 1e-7 and norm(sub(q[2], q[3])) < 1e-7:
                        continue
                    pts = [q[0]] + [p for a, p in zip(q, q[1:]) if norm(sub(a, p)) > 1e-7]
                    if len(pts) < 3:
                        continue
                    faces.append(self._face(pts, m_, cw, cen, stroke, (q[0], q[1]), (q[3], q[2])))
            for cap, ring, rev in ((top, rings[-1], False), (bottom, rings[0], True)):
                if cap is not None:
                    pts = list(reversed(ring)) if rev else list(ring)
                    faces.append(self._face(pts, cap, cw, cen, stroke, None, None))
        return faces

    def _face(self, pts, mat, cw, cen, stroke, bot, top):
        fc = Face()
        fc.w = [self.W(p) for p in pts]
        fc.it = self.sc.poly(fc.w, mat, snap=False, inside=cw, stroke=stroke)
        fc.b = pts
        n = (0.0, 0.0, 0.0)
        for i in range(1, len(pts) - 1):
            n = add(n, cross(sub(pts[i], pts[0]), sub(pts[i + 1], pts[0])))
        n = unit(n)
        c = mul(tuple(map(sum, zip(*pts))), 1 / len(pts))
        if dot(n, sub(c, cen)) < 0:
            n = mul(n, -1)
        fc.n = n
        fc.bot, fc.top = bot, top
        return fc

    def box(self, c, ea, eb, ec, ha, hb, hc, mat, r=0.015, part="box", top=None):
        """A cuboid centred on c with half sizes along unit axes ea, eb, ec."""
        ec = unit(ec)
        rings = [rring(add(c, mul(ec, z)), ea, eb, ha, ha, hb, hb, (r, r, r, r), 1) for z in (-hc, hc)]
        return self.solid(rings, mat, top=top or mat, bottom=mat, part=part)

    # painting ─────────────────────────────────────────────────────────────
    def _basis(self, fc):
        A = fc.w[0]
        U = unit(sub(fc.w[1], fc.w[0]))
        nw = (0.0, 0.0, 0.0)
        for i in range(1, len(fc.w) - 1):
            nw = add(nw, cross(sub(fc.w[i], fc.w[0]), sub(fc.w[i + 1], fc.w[0])))
        nw = unit(nw)
        if nw[0] + nw[1] + nw[2] < 0:
            nw = mul(nw, -1)
        V = unit(cross(nw, U))
        return A, U, V, nw

    def _put(self, fc, polys3, cull=True):
        """Paint 3D (body) shapes lying on a facet. Shapes that miss the facet
        are dropped; the marks are clipped to it only when one overflows."""
        A, U, V, nw = self._basis(fc)
        fpoly = [(dot(sub(w, A), U), dot(sub(w, A), V)) for w in fc.w]
        fx0, fx1 = min(p[0] for p in fpoly), max(p[0] for p in fpoly)
        fy0, fy1 = min(p[1] for p in fpoly), max(p[1] for p in fpoly)
        out, clip = [], False
        e = 1e-4
        for s in polys3:
            q = [(dot(sub(w, A), U), dot(sub(w, A), V)) for w in (self.W(p) for p in s[1])]
            xs, ys = [a for a, b in q], [b for a, b in q]
            pad = (s[3] / (self.sc.u * 1.0) if s[0] == "line" else 0.0)
            if cull and (max(xs) + pad < fx0 or min(xs) - pad > fx1 or max(ys) + pad < fy0 or min(ys) - pad > fy1):
                continue
            if cull and not clip:
                if pad or not all(_in_convex(fpoly, a, b, e) for a, b in q):
                    clip = True
            out.append((s[0], q) + tuple(s[2:]))
        if out:
            self.sc._put_mark(A, U, V, nw, out, fc.it, clip=clip)

    def paint(self, faces, chart, shapes, lw=1.0):
        """Paint 2D shapes from a body chart onto every facet that looks that
        way: 'front' (s, z) seen from +f, 'back' (s, z) from -f, 'side' (f, z)
        from +s, 'top' (f, s) from above. Shapes as in Scene.face_mark."""
        ax = {"front": 0, "back": 0, "side": 1, "top": 2}[chart]
        sg = -1 if chart == "back" else 1
        i1, i2 = {0: (1, 2), 1: (0, 2), 2: (0, 1)}[ax]
        prims = _prims(shapes, self.wk * lw)
        for fc in faces:
            if fc.it is None:
                continue
            n = fc.n
            an = [abs(v) for v in n]
            dom = 0 if an[0] >= an[1] - 1e-6 and an[0] >= an[2] - 1e-6 else (1 if an[1] >= an[2] - 1e-6 else 2)
            if dom != ax or n[ax] * sg <= 0.05:
                continue
            d = dot(n, fc.b[0])

            def P3(c1, c2):
                p = [0.0, 0.0, 0.0]
                p[i1], p[i2] = c1, c2
                p[ax] = (d - n[i1] * c1 - n[i2] * c2) / n[ax]
                return tuple(p)
            self._put(fc, [(s[0], [P3(*c) for c in s[1]]) + tuple(s[2:]) for s in prims])

    def cover(self, faces, zlo, zhi, mat, center=(0.0, 0.0), n=10, opacity=None):
        """Paint the band zlo(angle) < z < zhi(angle) over a solid's side
        facets: a hairline, a beard, a scarf's edge. angle: degrees round the
        vertical axis through center, 0 = +f, positive towards +s."""
        for fc in faces:
            if fc.it is None or fc.bot is None:
                continue
            a0, a1 = fc.bot
            b0, b1 = fc.top
            lo, hi, any_ = [], [], False
            for i in range(n + 1):
                t = i / n
                P0, P1 = lerp(a0, a1, t), lerp(b0, b1, t)
                m = lerp(P0, P1, 0.5)
                th = math.degrees(math.atan2(m[1] - center[1], m[0] - center[0]))
                dz = P1[2] - P0[2]
                if abs(dz) < 1e-9:
                    continue
                vl = clamp((zlo(th) - P0[2]) / dz)
                vh = clamp((zhi(th) - P0[2]) / dz)
                if vh < vl:
                    vh = vl
                if vh - vl > 1e-4:
                    any_ = True
                lo.append(lerp(P0, P1, vl)); hi.append(lerp(P0, P1, vh))
            if any_:
                self._put(fc, [("poly" if opacity else "spoly", hi + lo[::-1], mat) + ((opacity,) if opacity else ())], cull=False)


def _in_convex(poly, x, y, e):
    sign = 0
    n = len(poly)
    for i in range(n):
        (ax, ay), (bx, by) = poly[i], poly[(i + 1) % n]
        c = (bx - ax) * (y - ay) - (by - ay) * (x - ax)
        if abs(c) < e:
            continue
        if sign == 0:
            sign = 1 if c > 0 else -1
        elif (c > 0) != (sign > 0):
            return False
    return True


def _prims(shapes, wk):
    """Shapes -> polygons and polylines in chart coordinates."""
    out = []
    for s in shapes:
        t = s[0]
        if t == "rect":
            _, a, b, w, h, m, *op = s
            out.append(("poly", [(a, b), (a + w, b), (a + w, b + h), (a, b + h)], m) + tuple(op))
        elif t == "poly":
            out.append(("poly", list(s[1]), s[2]) + tuple(s[3:]))
        elif t == "line":
            out.append(("line", list(s[1]), s[2], s[3] * wk))
        elif t == "ell":
            _, a, b, ra, rb, m, *op = s
            out.append(("poly", [(a + ra * math.cos(i * math.pi / 9), b + rb * math.sin(i * math.pi / 9)) for i in range(18)], m) + tuple(op))
        elif t == "ring":
            _, a, b, ra, rb, m, w = s
            out.append(("line", [(a + ra * math.cos(i * math.pi / 10), b + rb * math.sin(i * math.pi / 10)) for i in range(21)], m, w * wk))
        elif t == "arc":
            _, a, b, w, dep, m, wd = s
            pts = []
            for i in range(9):
                u = i / 8
                x = a - w / 2 + w * u
                y = b - 2 * dep * 2 * u * (1 - u)
                pts.append((x, y))
            out.append(("line", pts, m, wd * wk))
    return out


# ── poses ──────────────────────────────────────────────────────────────────
WHOLE = ("run", "jump", "squat", "kneel", "floor", "lie", "sleep")
ARMS = ("down", "hold", "phone", "point", "wave", "cheer", "hips", "lap", "knees", "belly", "fists", "think")


def _pose(o):
    """Where everything goes: pelvis offset and lean, the root frame, ankle
    targets, arm targets. Body space, h = 1."""
    pose, walk, sit = o["pose"], o["walk"], o["sit"]
    k = o["h"]
    P = dict(dpel=(0.0, 0.0, 0.0), lean=0.0, nod=0.0, root=Xf(), floor=0.0, air=0.0, legs={}, arms=None,
             foot={}, head_shift=0.0, eyes=None, shadow="stand")
    if pose in WHOLE:
        whole = pose
    elif sit:
        whole = "sit"
    else:
        whole = "stand"
    arms = pose if pose in ARMS else "down"
    if o["arms"]:
        arms = o["arms"]
    near, far = CS + HIP_S, CS - HIP_S

    if whole == "stand":
        dx = 0.27 * walk
        reach = THIGH + SHIN - 0.012
        need = math.sqrt(max(0.0, reach * reach - dx * dx))
        drop = max(0.0, HIP_Z - (ANKLE_Z + need))
        P["dpel"] = (0.0, 0.0, -drop)
        lift = 0.03 * abs(walk)
        P["legs"] = {True: dict(ankle=(CF + 0.03 + dx, near + 0.005, ANKLE_Z + (lift if walk < 0 else 0)), pole=(1, 0, 0)),
                     False: dict(ankle=(CF + 0.03 - dx, far - 0.005, ANKLE_Z + (lift if walk > 0 else 0)), pole=(1, 0, 0))}
        P["swing"] = walk
    elif whole == "sit":
        s = sit / k
        P["dpel"] = (0.0, 0.0, 0.14 - HIP_Z)
        P["floor"] = -s
        for nr, sv in ((True, near), (False, far)):
            P["legs"][nr] = dict(ankle=(CF + 0.50, sv + (0.02 if nr else -0.02), -s + ANKLE_Z), pole=(1, 0, 0.5))
        if arms == "down":
            arms = "lap"
        P["shadow"] = "sit"
    elif whole == "floor":                      # cross-legged on the floor
        P["dpel"] = (0.0, 0.0, 0.14 - HIP_Z)
        P["legs"] = {True: dict(ankle=(CF + 0.50, CS - 0.07, 0.09), pole=(0.25, 1, 0.55)),
                     False: dict(ankle=(CF + 0.36, CS + 0.09, 0.08), pole=(0.25, -1, 0.55))}
        P["foot"] = {True: ((0.2, -1, 0), (0, 0, 1)), False: ((0.2, 1, 0), (0, 0, 1))}
        P["lean"] = 0.08
        if arms == "down":
            arms = "knees"
        P["shadow"] = "floor"
    elif whole == "squat":
        P["dpel"] = (-0.12, 0.0, 0.44 - HIP_Z)
        P["lean"] = 0.42
        P["legs"] = {True: dict(ankle=(CF + 0.10, near + 0.08, ANKLE_Z + 0.02), pole=(1, 0.3, 0.3)),
                     False: dict(ankle=(CF + 0.10, far - 0.08, ANKLE_Z + 0.02), pole=(1, -0.3, 0.3))}
        P["foot"] = {True: ((1, 0.15, -0.12), (0.12, 0, 1)), False: ((1, -0.15, -0.12), (0.12, 0, 1))}
        P["nod"] = -0.25
        if arms == "down":
            arms = "knees"
        P["shadow"] = "squat"
    elif whole == "kneel":
        P["dpel"] = (-0.04, 0.0, 0.57 - HIP_Z)
        P["lean"] = 0.06
        P["legs"] = {True: dict(knee=(CF + 0.10, near, 0.105), ankle=(CF - 0.33, near, 0.10)),
                     False: dict(ankle=(CF + 0.55, far, ANKLE_Z), pole=(1, 0, 1.2))}
        P["foot"] = {True: ((-0.25, 0, -1), (-1, 0, 0.1))}
        if arms == "down":
            arms = "knees"
        P["shadow"] = "kneel"
    elif whole == "jump":
        P["air"] = o["air"] if o["air"] is not None else 0.6
        P["root"] = move((0.0, 0.0, P["air"]))
        P["legs"] = {True: dict(ankle=(CF - 0.16, near + 0.02, 0.48), pole=(1, 0, 0)),
                     False: dict(ankle=(CF - 0.02, far - 0.02, 0.30), pole=(1, 0, 0))}
        P["foot"] = {True: ((0.55, 0, -0.85), (0.85, 0, 0.55)), False: ((0.7, 0, -0.7), (0.7, 0, 0.7))}
        P["lean"] = 0.05
        if arms == "down":
            arms = "cheer"
        P["shadow"] = "jump"
    elif whole == "run":
        t = (walk + 1) / 2 if walk else 1.0
        front, back = (CF + 0.36, 0.30), (CF - 0.42, 0.52)
        air = o["air"] if o["air"] is not None else 0.1
        P["air"] = air
        P["root"] = move((0.0, 0.0, air))
        P["lean"] = 0.22
        P["dpel"] = (0.0, 0.0, -0.04)
        for nr, sv, tt in ((True, near, t), (False, far, 1 - t)):
            f = back[0] + (front[0] - back[0]) * tt
            z = back[1] + (front[1] - back[1]) * tt
            P["legs"][nr] = dict(ankle=(f, sv, z), pole=(1, 0, 0))
            pf = -0.9 * (1 - tt)
            P["foot"][nr] = ((math.cos(pf), 0, math.sin(pf)), (-math.sin(pf), 0, math.cos(pf)))
        P["swing"] = (t - 0.5) * 2
        if arms == "down":
            arms = "fists"
        P["shadow"] = "run"
    elif whole in ("lie", "sleep"):
        P["eyes"] = "closed"
        P["shadow"] = whole
        if whole == "lie":
            # on the back, head towards `facing`: body z -> F, s -> S, f -> Z
            P["root"] = Xf(((0, 0, 1), (0, 1, 0), (1, 0, 0)), (0.0, 0.0, -0.005))
            P["legs"] = {True: dict(ankle=(CF + 0.03, near + 0.02, ANKLE_Z), pole=(1, 0, 0)),
                         False: dict(ankle=(CF + 0.03, far - 0.02, ANKLE_Z), pole=(1, 0, 0))}
            P["head_shift"] = 0.15
            if arms == "down":
                arms = "belly"
        else:
            # curled on the far side, face towards the viewer: z -> F, f -> S, s -> Z
            P["root"] = Xf(((0, 0, 1), (1, 0, 0), (0, 1, 0)), (0.0, 0.0, 0.12))
            P["legs"] = {True: dict(ankle=(CF + 0.16, near, 0.40), pole=(1, 0, 0.1)),
                         False: dict(ankle=(CF + 0.06, far, 0.30), pole=(1, 0, 0.1))}
            P["lean"] = 0.1
            P["nod"] = 0.2
            if arms == "down":
                arms = "curl"
    P["arms"] = arms
    P["whole"] = whole
    if o["lean"] is not None:
        P["lean"] = o["lean"]
    if o["nod"] is not None:
        P["nod"] = o["nod"]
    return P


def _arm_target(arms, near, P, knees, swing):
    """Wrist target, elbow pole, hand direction, thumb direction, space ('u'
    upper body or 'b' body), for the near arm; the far arm mirrors it."""
    so = CS + SH_S
    sw = -0.2 * swing if near else 0.2 * swing
    if arms == "down":
        return (CF + 0.04 + sw, so + 0.035, 1.00), (-1, 0.25, 0), (0.12, -0.05, -1), (1, -0.2, 0), "u"
    if arms == "hold":
        return (CF + 0.44, so - 0.13, 1.30), (-0.4, 0.6, -1), (1, -0.3, 0.12), (0, 0, 1), "u"
    if arms == "lap":
        return (CF + 0.46, so - 0.17, 0.36), (-0.3, 0.5, -1), (1, -0.15, -0.3), (0, -0.3, 1), "b"
    if arms == "phone":
        if near:
            return (CF + 0.30, CS + 0.09, 1.44), (-0.1, 0.7, -1), (0.35, -0.45, 1), (1, -0.2, 0), "u"
        return (CF + 0.05, so + 0.035, 1.00), (-1, 0.25, 0), (0.1, -0.05, -1), (1, -0.2, 0), "u"
    if arms == "point":
        if near:
            return (CF + 0.63, so - 0.02, 1.62), (0, 0.4, -1), (1, 0, 0.02), (0, -0.4, 1), "u"
        return (CF + 0.05, so + 0.035, 1.00), (-1, 0.25, 0), (0.1, -0.05, -1), (1, -0.2, 0), "u"
    if arms == "wave":
        if near:
            return (CF - 0.04, so + 0.24, 2.20), (0.2, 1, -0.4), (0.0, 0.1, 1), (1, 0, 0.1), "u"
        return (CF + 0.05, so + 0.035, 1.00), (-1, 0.25, 0), (0.1, -0.05, -1), (1, -0.2, 0), "u"
    if arms == "cheer":
        return (CF - 0.06, so + 0.36, 2.18), (0.2, 1, -0.2), (0.0, 0.25, 1), (1, 0, 0), "u"
    if arms == "hips":
        return (CF + 0.10, CS + 0.29, 1.10), (-0.4, 1, 0.25), (0.35, -1, -0.45), (0, 0, 1), "u"
    if arms == "think":
        if near:
            return (CF + 0.40, CS + 0.05, 1.70), (0, 0.7, -1), (0.1, -0.2, 1), (1, 0, 0), "u"
        return (CF + 0.36, CS + 0.10, 1.26), (-0.3, -0.4, -1), (0.2, 1, 0), (0, 0, 1), "u"
    if arms == "belly":
        return (CF + 0.36, CS + 0.07, 1.22), (-0.2, 1, -0.4), (0.1, -1, 0), (0, 0, 1), "u"
    if arms == "fists":
        return (CF + 0.26 + sw * 1.2, so + 0.0, 1.30), (-1, 0.2, -0.3), (0.5, -0.3, 0.8), (0, -0.5, 1), "u"
    if arms == "curl":
        if near:
            return (CF + 0.46, CS + 0.12, 1.30), (-0.2, 1, -0.5), (1, -0.2, 0.2), (0, 0, 1), "u"
        return (CF + 0.42, CS - 0.05, 1.68), (0, -1, -0.3), (0.2, 0.5, 1), (1, 0, 0), "u"
    if arms == "knees":
        kn = knees[near]
        return (kn[0] + 0.10, kn[1] + (-0.04 if near else 0.04), kn[2] + 0.04), (-0.3, 1, -0.3), (1, -0.25, -0.3), (0, -0.2, 1), "b"
    raise ValueError("unknown arm pose %r (one of %s)" % (arms, ", ".join(ARMS)))


# ── the person ─────────────────────────────────────────────────────────────
def draw(sc, x, y, z, o):
    k = o["h"]
    ol = sc.new_outline("person")
    sc._olw[ol] = max(0.62, min(1.0, sc.u * k / 40))       # small people get a finer line
    rig = Rig(sc, x, y, z, o["facing"], k, "person@(%.1f,%.1f)" % (x, y), ol)
    px = sc.u * k
    o["_lod"] = 0 if px * HEAD_H < 17 else (1 if px * HEAD_H < 34 else 2)
    P = _pose(o)
    o["_whole"] = P["whole"]
    if P["eyes"] and o["eyes"] == "dot":
        o = dict(o, eyes=P["eyes"])
    top, outfit = o["top"], o["outfit"]
    bottom = o["bottom"]
    skirt = o["skirt"] or (top if outfit == "dress" else None)

    U = move(P["dpel"]).after(pitch(P["lean"], (CF, CS, HIP_Z)))     # upper body (pelvis up)
    with rig.xf(P["root"]):
        _shadow(rig, P, o)
        hips = {True: U((CF, CS + HIP_S, HIP_Z)), False: U((CF, CS - HIP_S, HIP_Z))}
        legs = {}
        for nr in (False, True):
            legs[nr] = _leg(rig, o, P, nr, hips[nr], bottom, skirt)
        knees = {nr: legs[nr][0] for nr in legs}
        with rig.xf(U):
            _torso(rig, o, skirt, P)
            _neck(rig, o)
        hands = {}
        for nr in (False, True):
            hands[nr] = _arm(rig, o, P, nr, U, knees)
        with rig.xf(U):
            H = pitch(P["nod"], (HEAD_F, CS, HEAD_Z - 0.04)).after(move((HEAD_F + P["head_shift"], CS, HEAD_Z)))
            kh = (k ** 0.5) / k if k < 1 else 1.0
            if kh != 1.0:
                H = scale(kh, (HEAD_F, CS, HEAD_Z)).after(H)
            with rig.xf(H):
                _head(rig, o)
        _held(rig, o, P, U, hands)


def _shadow(rig, P, o):
    """A soft oval on the floor under the body."""
    sh = P["shadow"]
    fl = P["floor"]
    if sh in ("stand", "run"):
        c, rf, rs = (CF + 0.06, CS), 0.36, 0.40
    elif sh == "sit":
        c, rf, rs = (CF + 0.34, CS), 0.42, 0.42
    elif sh in ("floor", "squat", "kneel"):
        c, rf, rs = (CF + 0.24, CS), 0.52, 0.50
    elif sh == "jump":
        c, rf, rs = (CF + 0.02, CS), 0.26, 0.30
    else:
        c, rf, rs = None, 0, 0
    if c is not None:
        z = fl - P["air"]
        pts = [rig.W((c[0] + rf * math.cos(t), c[1] + rs * math.sin(t), z)) for t in (i * math.pi / 10 for i in range(20))]
        with rig.sc.tag(rig.tag + " shadow"):
            rig.sc.shadow_poly(pts)
    else:
        # lying: a long oval on the floor of the local frame (z along the spine)
        cs = CF + 0.25 if sh == "sleep" else CS
        pts = [rig.L((1.25 + 1.25 * math.cos(t), cs + 0.45 * math.sin(t), 0.0)) for t in (i * math.pi / 12 for i in range(24))]
        with rig.sc.tag(rig.tag + " shadow"):
            rig.sc.shadow_poly(pts)


# ── legs and shoes ─────────────────────────────────────────────────────────
def _leg(rig, o, P, near, hip, bottom, skirt):
    spec = P["legs"][near]
    ankle = spec["ankle"]
    if "knee" in spec:
        knee = spec["knee"]
    else:
        knee, ankle = ik(hip, ankle, THIGH, SHIN, spec["pole"])
    skin = o["skin"]
    shorts = o["shorts"]
    sitting = P["whole"] in ("sit", "floor")
    r_hip, r_knee, r_calf, r_ank = 0.135, 0.098, 0.092, 0.07
    calf = lerp(knee, ankle, 0.3)
    hem = lerp(knee, ankle, 0.93)
    segs = []
    if skirt and sitting:
        # the skirt lies over the thighs to the knee
        segs.append((hip, r_hip + 0.035, knee, r_knee + 0.04, skirt, "r", "o"))
        segs += [(knee, r_knee, calf, r_calf, bottom, "f", "f"), (calf, r_calf, hem, r_ank + 0.004, bottom, "f", "f")]
    elif shorts:
        mid = lerp(hip, knee, 0.62)
        segs += [(hip, r_hip + 0.012, mid, r_hip + 0.0, bottom, "r", "o"),
                 (mid, r_hip - 0.022, knee, r_knee - 0.008, skin, "f", "f"),
                 (knee, r_knee - 0.008, calf, r_calf - 0.012, skin, "f", "f"),
                 (calf, r_calf - 0.012, hem, r_ank - 0.012, skin, "f", "f")]
    else:
        segs += [(hip, r_hip + 0.012, knee, r_knee + 0.012, bottom, "r", "f"),
                 (knee, r_knee + 0.012, calf, r_calf + 0.012, bottom, "f", "f"),
                 (calf, r_calf + 0.012, hem, r_ank + 0.018, bottom, "f", "o")]
    rig.tube(segs, "leg")
    _shoe(rig, o, P, near, ankle)
    return knee, ankle


def _shoe(rig, o, P, near, ankle):
    d, up = P["foot"].get(near, ((1, 0, 0), (0, 0, 1)))
    d, up = unit(d), unit(up)
    side = unit(cross(up, d))
    shoe = o["shoe"]
    dark = shoe in ("shoe", "navy", "pants", "steel", "maroon", "wood", "amber")
    sole_c = ("~", shoe, 0.55) if dark else "paper"
    heel = add(sub(ankle, mul(d, 0.10)), mul(up, -0.095))          # back of the heel, on the sole
    # (x along the foot, half width, height, top corner radius)
    prof = [(0.0, 0.088, 0.125, 0.045), (0.21, 0.108, 0.11, 0.05), (0.385, 0.07, 0.06, 0.03)]
    rings = [rring(add(heel, mul(d, x)), side, up, hw, hw, 0.0, h, (r, r, 0.0, 0.0), 1) for x, hw, h, r in prof]
    faces = rig.solid(rings, shoe, top=shoe, bottom=None, part="shoe")
    if abs(up[2]) > 0.9:
        zs = heel[2] + 0.028
        rig.cover(faces, lambda th: -9.0, lambda th: zs, sole_c, center=(heel[0], heel[1]), n=2)
        if o["_lod"] >= 1 and d[0] > 0.3:
            lc = ("~", shoe, 0.6) if not dark else ("~", shoe, 1.6)
            x0 = heel[0] + 0.15 * d[0]
            b = ankle[1]
            rig.paint(faces, "top", [("line", [(x0 + 0.022 * i, b - 0.03), (x0 + 0.022 * i, b + 0.03)], lc, 0.8) for i in range(3)])


# ── torso, garments, neck ──────────────────────────────────────────────────
def _torso(rig, o, skirt, P):
    top, outfit, bottom = o["top"], o["outfit"], o["bottom"]
    m = 1
    tucked = outfit in TUCKED
    # trousers' seat and waistband
    pr = [hring(CF, CS, 0.84, 0.12, 0.12, 0.215, 0.06, 0.06, m),
          hring(CF, CS, 0.98, 0.15, 0.155, 0.29, 0.08, 0.08, m),
          hring(CF, CS, 1.07, 0.146, 0.15, 0.281, 0.08, 0.08, m)]
    if skirt:
        pf = []
    else:
        pf = rig.solid(pr, bottom, top=bottom, part="hips")
    # the top: hem, waist, chest, shoulders, shoulder slope
    if tucked:
        h0 = (1.03, 0.138, 0.142, 0.27)
    elif outfit in LONG_HEM:
        h0 = (0.90, 0.17, 0.175, 0.305)
    else:
        h0 = (0.95, 0.163, 0.168, 0.302)
    rows = [h0, (1.18, 0.148, 0.148, 0.266), (1.46, 0.178, 0.155, 0.30), (1.66, 0.155, 0.145, 0.305), (1.77, 0.10, 0.10, 0.19)]
    if outfit in OPEN_FRONT:
        rows = [(z, f + 0.008, b + 0.008, w + 0.008) for z, f, b, w in rows[:-1]] + [rows[-1]]
    rings = [hring(CF, CS, z, f, b, w, 0.09, 0.09, m) for z, f, b, w in rows]
    tf = rig.solid(rings, top, top=top, part="torso")
    if skirt:
        sk = [hring(CF, CS, 0.52 if not P["whole"] in ("sit", "floor") else 0.9, 0.25, 0.25, 0.37, 0.14, 0.14, m),
              hring(CF, CS, 0.96, 0.172, 0.176, 0.31, 0.09, 0.09, m),
              hring(CF, CS, 1.13, 0.155, 0.155, 0.276, 0.09, 0.09, m)]
        if P["whole"] not in ("sit", "floor"):
            sf = rig.solid(sk, skirt, top=None, part="skirt")
            rig.paint(sf, "front", [("line", [(CS - 0.12, 0.98), (CS - 0.17, 0.56)], ("~", skirt, 0.8), 1.0),
                                    ("line", [(CS + 0.12, 0.98), (CS + 0.17, 0.56)], ("~", skirt, 0.8), 1.0)])
            rig.paint(sf, "side", [("line", [(CF + 0.02, 0.98), (CF + 0.04, 0.56)], ("~", skirt, 0.8), 1.0)])
        else:
            rig.solid(sk[1:], skirt, top=None, part="skirt")
    _outfit(rig, o, tf, pf, tucked)
    if outfit == "apron":
        _apron(rig, o)
    if outfit == "hoodie":
        _hood(rig, o)
    return tf


def _outfit(rig, o, tf, pf, tucked):
    top, outfit, inner, tie = o["top"], o["outfit"], o["inner"], o["tie"]
    dk = ("~", top, 0.78)
    lt = ("~", top, 1.18)
    c = CS
    F, B, S, T = [], [], [], []           # front, back, side, top charts
    hem = 1.03 if tucked else (0.90 if outfit in LONG_HEM else 0.95)
    # neck hole and the hem shadow on the trousers
    T.append(("ell", HEAD_F + 0.0, CS, 0.1, 0.11, ("~", top, 0.55)))
    if pf and not tucked:
        sh = ("~", o["bottom"], 0.72)
        rig.paint(pf, "front", [("rect", -1, hem - 0.045, 3, 0.045, sh)])
        rig.paint(pf, "side", [("rect", -1, hem - 0.045, 3, 0.045, sh)])
    if pf and tucked:
        belt = ("~", "navy", 1.0) if o["bottom"] not in ("navy", "pants") else ("~", "wood", 0.55)
        rig.paint(pf, "front", [("rect", -1, 0.985, 3, 0.05, belt), ("rect", c - 0.035, 0.99, 0.07, 0.04, "gold"),
                                ("line", [(c + 0.005, 0.985), (c + 0.005, 0.87)], ("~", o["bottom"], 0.75), 0.8)])
        rig.paint(pf, "side", [("rect", -1, 0.985, 3, 0.05, belt)])
        rig.paint(pf, "back", [("rect", -1, 0.985, 3, 0.05, belt)])
    elif pf:
        rig.paint(pf, "front", [("line", [(c + 0.005, 0.95), (c + 0.005, 0.87)], ("~", o["bottom"], 0.75), 0.8)])

    if outfit in ("tee", "dress", "stripes", "apron", "hivis"):
        F += [("poly", [(c - 0.12, 1.775), (c + 0.12, 1.775), (c + 0.09, 1.73), (c, 1.70), (c - 0.09, 1.73)], ("~", top, 0.86))]
        B += [("line", [(c - 0.1, 1.76), (c + 0.1, 1.76)], dk, 1.0)]
        if outfit == "dress":
            F += [("rect", -1, 1.13, 3, 0.03, dk)]
            S += [("rect", -1, 1.13, 3, 0.03, dk)]
        else:
            for ch in (F, S, B):
                ch.append(("line", [(-1, hem + 0.035), (3, hem + 0.035)], dk, 0.7))
    if outfit == "stripes":
        for i in range(7):
            z0 = hem + 0.06 + i * 0.12
            for ch in (F, S, B):
                ch.append(("rect", -1, z0, 3, 0.05, inner))
    if outfit in ("shirt", "polo", "batik", "batik_short"):
        if outfit.startswith("batik"):
            for r in range(7):
                for q in range(-1, 6):
                    a = c - 0.30 + q * 0.13 + (0.065 if r % 2 else 0)
                    b = hem + 0.08 + r * 0.12
                    shp = [("poly", [(a, b - 0.04), (a + 0.04, b), (a, b + 0.04), (a - 0.04, b)], "gold"),
                           ("ell", a, b, 0.012, 0.012, dk)]
                    F.extend(shp); B.extend(shp)
                    S.extend([("poly", [(CF - 0.2 + q * 0.13 + (0.065 if r % 2 else 0) + dx, b + dy) for dx, dy in
                                        ((0, -0.04), (0.04, 0), (0, 0.04), (-0.04, 0))], "gold")])
        # the collar: two points over the placket, a band round the neck on top
        F += [("poly", [(c - 0.115, 1.775), (c - 0.005, 1.70), (c - 0.02, 1.665), (c - 0.12, 1.72)], lt),
              ("poly", [(c + 0.115, 1.775), (c + 0.005, 1.70), (c + 0.02, 1.665), (c + 0.12, 1.72)], lt),
              ("line", [(c, 1.70), (c, hem + 0.01 if outfit != "polo" else 1.50)], dk, 0.9)]
        T.append(("ring", HEAD_F, CS, 0.105, 0.115, lt, 2.2))
        nb = 4 if outfit != "polo" else 2
        for i in range(nb):
            F.append(("ell", c + 0.016, 1.62 - i * 0.14, 0.014, 0.014, "paper"))
        if outfit == "shirt":
            F += [("rect", c + 0.08, 1.40, 0.1, 0.1, dk), ("rect", c + 0.08, 1.48, 0.1, 0.022, ("~", top, 0.7))]
        if tucked:
            F += [("line", [(c - 0.17, 1.06), (c - 0.15, 1.13)], dk, 0.7), ("line", [(c + 0.16, 1.06), (c + 0.15, 1.12)], dk, 0.7)]
        B += [("line", [(-1, 1.60), (3, 1.60)], dk, 0.8)]
        S += [("line", [(CF - 0.02, hem + 0.02), (CF - 0.02, 1.70)], dk, 0.6)]
    if outfit in ("suit", "jacket", "cardigan"):
        open_w = 0.13 if outfit != "cardigan" else 0.085
        vz = 1.30 if outfit != "cardigan" else hem
        F += [("poly", [(c - open_w, 1.78), (c + open_w, 1.78), (c + 0.02, vz), (c - 0.02, vz)] if outfit == "cardigan"
               else [(c - open_w, 1.78), (c + open_w, 1.78), (c, vz)], inner)]
        if outfit != "cardigan":
            if inner in ("shirt", "paper", "white"):
                F += [("poly", [(c - 0.055, 1.78), (c, 1.73), (c - 0.07, 1.70)], ("~", inner, 1.1)),
                      ("poly", [(c + 0.055, 1.78), (c, 1.73), (c + 0.07, 1.70)], ("~", inner, 1.1))]
            if tie and outfit == "suit":
                F += [("poly", [(c - 0.022, 1.735), (c + 0.022, 1.735), (c + 0.016, 1.70), (c - 0.016, 1.70)], ("~", tie, 0.85)),
                      ("poly", [(c - 0.016, 1.70), (c + 0.016, 1.70), (c + 0.034, 1.40), (c, 1.35), (c - 0.034, 1.40)], tie)]
            # lapels, folded back: lighter wedges along the opening
            F += [("poly", [(c - open_w, 1.78), (c - 0.04, vz + 0.02), (c - 0.085, 1.52), (c - 0.2, 1.66), (c - 0.17, 1.775)], lt),
                  ("poly", [(c + open_w, 1.78), (c + 0.04, vz + 0.02), (c + 0.085, 1.52), (c + 0.2, 1.66), (c + 0.17, 1.775)], lt)]
            F += [("line", [(c, vz), (c - 0.01, hem + 0.04), (c - 0.07, hem)], dk, 0.9)]
            F += [("ell", c + 0.02, 1.18, 0.014, 0.014, dk), ("ell", c + 0.02, 1.06, 0.014, 0.014, dk)]
            if outfit == "suit":
                F += [("rect", c + 0.12, 1.47, 0.09, 0.025, "paper"), ("line", [(c + 0.09, 1.10), (c + 0.22, 1.10)], dk, 0.8),
                      ("line", [(c - 0.22, 1.10), (c - 0.09, 1.10)], dk, 0.8)]
        else:
            F += [("line", [(c - open_w, 1.78), (c - open_w, hem)], dk, 0.9), ("line", [(c + open_w, 1.78), (c + open_w, hem)], dk, 0.9)]
            F += [("ell", c + open_w + 0.025, 1.55 - i * 0.15, 0.013, 0.013, dk) for i in range(4)]
            for ch in (F, S, B):
                ch.append(("rect", -1, hem, 3, 0.04, dk))
        B += [("line", [(c, hem), (c, hem + 0.16)], dk, 0.8)]
        S += [("line", [(CF - 0.01, hem + 0.03), (CF - 0.01, 1.68)], dk, 0.6)]
    if outfit == "hivis":
        band = "!paper"
        F += [("rect", c - 0.2, hem, 0.06, 0.8, band), ("rect", c + 0.14, hem, 0.06, 0.8, band),
              ("line", [(c, 1.70), (c, hem)], dk, 0.9)]
        for ch in (F, S, B):
            ch.append(("rect", -1, 1.17, 3, 0.06, band))
        B += [("rect", c - 0.2, hem, 0.06, 0.8, band), ("rect", c + 0.14, hem, 0.06, 0.8, band)]
        F += [("poly", [(c - 0.1, 1.775), (c + 0.1, 1.775), (c, 1.62)], o["inner"])]
    if outfit == "hoodie":
        F += [("poly", [(c - 0.16, hem + 0.06), (c + 0.16, hem + 0.06), (c + 0.12, 1.24), (c - 0.12, 1.24)], ("~", top, 0.9)),
              ("line", [(c - 0.16, hem + 0.06), (c - 0.12, 1.24), (c + 0.12, 1.24), (c + 0.16, hem + 0.06)], dk, 0.9),
              ("line", [(c - 0.05, 1.70), (c - 0.06, 1.50)], "paper", 1.1), ("line", [(c + 0.05, 1.70), (c + 0.06, 1.52)], "paper", 1.1),
              ("ell", c - 0.06, 1.50, 0.012, 0.016, "paper"), ("ell", c + 0.06, 1.52, 0.012, 0.016, "paper")]
        for ch in (F, S, B):
            ch.append(("rect", -1, hem, 3, 0.05, ("~", top, 0.85)))
    if outfit == "apron":
        pass
    rig.paint(tf, "front", F)
    rig.paint(tf, "back", B)
    rig.paint(tf, "side", S)
    rig.paint(tf, "top", T)


def _apron(rig, o):
    """An apron: a thin panel in front of the chest and thighs, with a neck strap."""
    col = o["inner"]
    rings = [rring((CF + 0.192, CS, z), (1, 0, 0), (0, 1, 0), 0.012, 0.012, w, w, (0.01,) * 4, 1)
             for z, w in ((0.52, 0.2), (1.44, 0.17))]
    af = rig.solid(rings, col, top=col, bottom=col, part="apron")
    rig.paint(af, "front", [("rect", CS - 0.1, 0.80, 0.2, 0.1, ("~", col, 0.86)),
                            ("line", [(CS - 0.1, 0.90), (CS + 0.1, 0.90)], ("~", col, 0.7), 0.8)])
    with rig.sc.tag(rig.tag + " apron strap"):
        for sg in (-1, 1):
            rig.sc.line([rig.W((CF + 0.18, CS + sg * 0.15, 1.44)), rig.W((CF + 0.12, CS + sg * 0.12, 1.77))], col, 1.6 * rig.wk)


def _hood(rig, o):
    col = ("~", o["top"], 0.92)
    pts = [(HEAD_F + 0.05, CS + 0.17, 1.775), (HEAD_F - 0.07, CS + 0.15, 1.80), (HEAD_F - 0.12, CS, 1.82),
           (HEAD_F - 0.07, CS - 0.15, 1.80), (HEAD_F + 0.05, CS - 0.17, 1.775)]
    nodes = [(p, 0.055 if i in (0, 4) else 0.075) for i, p in enumerate(pts)]
    rig.chain(nodes, col, part="hood")


def _neck(rig, o):
    sk = ("~", o["skin"], 0.86)
    rig.chain([((HEAD_F, CS, 1.70), 0.07), ((HEAD_F, CS, 1.90), 0.068)], sk, part="neck")
    if o["hair_style"] == "hijab":
        _drape(rig, o)


def _drape(rig, o):
    """A hijab's drape over the neck, shoulders and chest."""
    col = o["hair"]
    m = 2 if o["_lod"] >= 2 else 1
    rows = [(1.48, 0.205, 0.17, 0.34, 0.16), (1.62, 0.20, 0.17, 0.40, 0.16), (1.74, 0.185, 0.165, 0.425, 0.16),
            (1.83, 0.14, 0.15, 0.30, 0.12), (1.88, 0.11, 0.14, 0.24, 0.1)]
    rings = [hring(CF + 0.01, CS, z, f, b, w, r, r, m) for z, f, b, w, r in rows]
    df = rig.solid(rings, col, top=None, part="hijab drape")
    dk = ("~", col, 0.82)
    rig.paint(df, "front", [("arc", CS - 0.02, 1.72, 0.30, 0.05, dk, 0.8), ("arc", CS, 1.62, 0.36, 0.05, dk, 0.7)])
    rig.paint(df, "side", [("line", [(CF - 0.06, 1.74), (CF - 0.01, 1.52)], dk, 0.7)])


# ── arms and hands ─────────────────────────────────────────────────────────
def _arm(rig, o, P, near, U, knees):
    outfit, top, skin = o["outfit"], o["top"], o["skin"]
    sleeve = o["sleeve"] or (o["inner"] if outfit == "hivis" else top)
    cuff = o["inner"] if outfit in ("suit", "jacket") else None
    swing = P.get("swing", 0.0)
    T, pole, hd, tv, space = _arm_target(P["arms"], near, P, knees, swing)
    if not near:
        T, pole, hd, tv = mirror(T), (pole[0], -pole[1], pole[2]), (hd[0], -hd[1], hd[2]), (tv[0], -tv[1], tv[2])
    sh0 = (CF, CS + (SH_S if near else -SH_S), SH_Z)
    S = U(sh0)
    if space == "u":
        T, pole, hd, tv = U(T), U.vec(pole), U.vec(hd), U.vec(tv)
    E, Wr = ik(S, T, UPPER, FORE, pole)
    hd = unit(hd)
    short = outfit in SHORT_SLEEVES
    rs, re_, rw = 0.092, 0.07, 0.054
    seam = lerp(S, E, 0.42)
    stripes = outfit == "stripes"
    segs = []
    sl_r = 0.018
    if short:
        segs.append((S, rs + 0.012, seam, rs + 0.006, sleeve, "r", "o"))
        segs.append((seam, rs - 0.012, E, re_, skin, "f", "f"))
        segs.append((E, re_, Wr, rw, skin, "f", "f"))
    else:
        cuffp = lerp(E, Wr, 0.93)
        if stripes:
            pts = [lerp(S, E, t) for t in (0, 0.25, 0.5, 0.75, 1.0)] + [lerp(E, cuffp, t) for t in (0.33, 0.66, 1.0)]
            rads = [rs + 0.008, rs + 0.006, rs + 0.002, re_ + 0.016, re_ + sl_r, 0.068 + 0.01, 0.064 + 0.008, rw + 0.016]
            for i in range(len(pts) - 1):
                segs.append((pts[i], rads[i], pts[i + 1], rads[i + 1], sleeve if i % 2 == 0 else o["inner"],
                             "r" if i == 0 else "f", "o" if i == len(pts) - 2 else "f"))
        else:
            segs.append((S, rs + 0.008, E, re_ + sl_r, sleeve, "r", "f"))
            segs.append((E, re_ + sl_r, cuffp, rw + 0.016, sleeve, "f", "o"))
        if cuff:
            segs.append((cuffp, rw + 0.006, lerp(E, Wr, 1.0), rw + 0.004, cuff, "f", "o"))
        else:
            segs.append((cuffp, rw, Wr, rw, skin, "f", "f"))
    rig.tube(segs, "arm")
    hand = _hand(rig, o, Wr, hd, tv, P["arms"], near)
    return dict(w=Wr, d=hd, palm=add(Wr, mul(hd, 0.07)), tip=hand, e=E, s=S)


def _hand(rig, o, Wr, hd, tv, arms, near):
    skin = o["skin"]
    lod = o["_lod"]
    tv = unit(sub(tv, mul(hd, dot(tv, hd)))) if norm(tv) > 0 else (0, 0, 1)
    palm = add(Wr, mul(hd, 0.085))
    if lod == 0:
        rig.chain([(Wr, 0.054), (add(Wr, mul(hd, 0.12)), 0.046)], skin, part="hand")
        return add(Wr, mul(hd, 0.14))
    fist = arms in ("fists", "hold", "lap", "knees") or (arms == "phone" and near)
    if fist:                       # fingers curled round: a short, blunt hand
        tip = add(palm, mul(hd, 0.03))
        segs = [(Wr, 0.054, palm, 0.052, skin, "r", "f"), (palm, 0.052, add(palm, mul(hd, 0.04)), 0.045, skin, "f", "r")]
    else:                          # open hand: palm, then the fingers together
        tip = add(palm, mul(hd, 0.075))
        segs = [(Wr, 0.054, palm, 0.052, skin, "r", "f"), (palm, 0.05, tip, 0.036, skin, "f", "r")]
    t0 = add(Wr, add(mul(hd, 0.03), mul(tv, 0.035)))
    t1 = add(t0, add(mul(hd, 0.04), mul(tv, 0.035)))
    segs.append((t0, 0.025, t1, 0.02, skin, "r", "r"))
    if arms == "point" and near:
        segs.append((tip, 0.03, add(tip, mul(hd, 0.08)), 0.022, skin, "r", "r"))
    rig.tube(segs, "hand")
    return tip


# ── head, face, hair ───────────────────────────────────────────────────────
def _head(rig, o):
    lod = o["_lod"]
    m = 2 if lod >= 1 else 1
    style = o["hair_style"]
    skin = o["skin"]
    capped = style not in ("bald",)
    rows = HEAD[:-1] if capped else HEAD
    rings = [hring(0.0, 0.0, z, f, b, w, rf, rb, m) for z, f, b, w, rf, rb in rows]
    hf = rig.solid(rings, skin, top=skin, part="head")
    # ears (hidden under long hair and scarves)
    if style not in ("long", "bob", "hijab"):
        for sg in (1,):
            c = (-0.01, sg * 0.305, 0.33)
            r0 = rring(c, (1, 0, 0), (0, 0, 1), 0.065, 0.06, 0.095, 0.10, (0.05, 0.05, 0.04, 0.04), 1)
            c2 = (-0.012, sg * 0.345, 0.33)
            r1 = rring(c2, (1, 0, 0), (0, 0, 1), 0.055, 0.05, 0.085, 0.09, (0.045, 0.045, 0.035, 0.035), 1)
            ef = rig.solid([r0, r1] if sg > 0 else [r1, r0], skin, top=skin, bottom=skin, part="ear")
            if sg > 0 and lod >= 1:
                rig.paint(ef, "side", [("arc", -0.012, 0.36, 0.06, -0.025, ("~", skin, 0.72), 1.1),
                                       ("line", [(-0.035, 0.38), (-0.03, 0.30), (0.0, 0.29)], ("~", skin, 0.78), 0.9)])
    _hair(rig, o, hf)
    if not rig.away:
        _face(rig, o, hf)
    if o["glasses"]:
        g = o["glasses"]
        rig.paint(hf, "side", [("line", [(FACE_F - 0.02, 0.39), (0.0, 0.40)], g, 1.3)])


def _hairline(style):
    """(zlo, zhi) of the painted hair round the head, by angle."""
    INF = keys((0, 9.0), (180, 9.0))
    if style == "bald":
        return keys((0, 9), (62, 9), (72, 0.50), (100, 0.47), (180, 0.20)), keys((0, 9), (62, 9), (70, 0.56), (110, 0.58), (180, 0.62))
    if style in ("cap", "hardhat"):
        return keys((0, 0.56), (55, 0.52), (62, 0.44), (68, 0.36), (75, 0.36), (79, 0.47), (110, 0.47), (130, 0.22), (180, 0.16)), INF
    if style == "short":
        return keys((0, 0.565), (25, 0.545), (52, 0.50), (62, 0.44), (68, 0.36), (75, 0.36), (79, 0.47), (110, 0.47), (130, 0.24), (180, 0.16)), INF
    if style == "sidepart":
        f = keys((0, 0.55), (52, 0.50), (62, 0.44), (68, 0.36), (75, 0.36), (79, 0.47), (110, 0.47), (130, 0.24), (180, 0.16))
        return (lambda th: f(th) - (0.06 * max(0.0, 1 - abs(th + 12) / 30) if th < 18 else 0)), INF
    if style in ("quiff", "spiky"):
        return keys((0, 0.59), (28, 0.565), (52, 0.51), (62, 0.44), (68, 0.36), (75, 0.36), (79, 0.47), (110, 0.47), (130, 0.24), (180, 0.15)), INF
    if style == "curly":
        return (lambda th: keys((0, 0.55), (50, 0.47), (68, 0.30), (84, 0.44), (110, 0.44), (180, 0.10))(th)
                + 0.02 * math.cos(math.radians(th) * 14)), INF
    if style in ("bun", "ponytail", "pigtails"):
        return keys((0, 0.60), (30, 0.575), (55, 0.50), (70, 0.38), (84, 0.47), (110, 0.47), (140, 0.20), (180, 0.14)), INF
    if style in ("long", "bob"):
        return keys((0, 0.56), (20, 0.50), (40, 0.47), (58, 0.12), (180, 0.0)), INF
    if style == "hijab":
        return keys((0, 0.535), (36, 0.52), (46, 0.40), (56, 0.04), (180, -1)), INF
    return keys((0, 0.565), (180, 0.16)), INF


def _hair(rig, o, hf):
    style, hair = o["hair_style"], o["hair"]
    lod = o["_lod"]
    m = 2 if lod >= 1 else 1
    hl = ("~", hair, 1.22)
    hd = ("~", hair, 0.8)
    zlo, zhi = _hairline(style)
    rig.cover(hf, zlo, zhi, hair)
    if style not in ("bald", "hijab", "cap", "hardhat") and lod >= 1:
        # shadow cast by the fringe on the forehead
        rig.cover(hf, lambda th: zlo(th) - 0.03, zlo, ("~", o["skin"], 0.84))
    if style == "bald":
        return
    if style == "hijab":
        _hijab(rig, o, hf)
        return
    if style in ("cap", "hardhat"):
        _hat(rig, o)
        return
    t = {"curly": 0.07, "long": 0.045, "bob": 0.05}.get(style, 0.035)
    tf_ = {"quiff": 0.02, "spiky": 0.02, "bun": 0.0, "ponytail": 0.0, "pigtails": 0.0}.get(style, 0.03)
    z0 = {"bun": 0.58, "ponytail": 0.58, "pigtails": 0.58, "quiff": 0.58, "spiky": 0.58}.get(style, 0.55)

    def cring(z, grow, extra_f=0.0, shrink=1.0):
        f, b, w, rf, rb = head_dims(z)
        return hring(0.0, 0.0, z, (f + grow + extra_f) * shrink, (b + grow) * shrink, (w + grow) * shrink,
                     rf + grow * 0.5, rb + grow * 0.5, m)
    rings = [cring(z0, t * 0.5, tf_), cring((z0 + 0.64) / 2, t, tf_ * 0.8), cring(0.66, t, tf_ * 0.4)]
    f, b, w, rf, rb = head_dims(0.66)
    for zz, sh in ((HEAD_H + t * 0.55, 0.86), (HEAD_H + t, 0.58)):
        rings.append(hring(0.0, 0.0, zz, (f + t) * sh, (b + t) * sh, (w + t) * sh, (rf + t) * sh, (rb + t) * sh, m))
    cap = rig.solid(rings, hair, top=hair, part="hair")
    if lod >= 1:
        # strands and a sheen on the crown
        if style == "sidepart":
            rig.paint(cap, "top", [("line", [(0.24, -0.08), (-0.2, -0.10)], hd, 1.1)])
            rig.paint(cap, "top", [("line", [(0.2, -0.04 + 0.06 * i), (-0.15, 0.0 + 0.08 * i)], hd, 0.7) for i in range(3)])
        elif style in ("short", "quiff", "spiky", "bun", "ponytail", "pigtails"):
            rig.paint(cap, "top", [("arc", 0.06 - 0.1 * i, -0.05 + 0.1 * i, 0.16, 0.02, hd, 0.7) for i in range(2)])
        rig.paint(cap, "top", [("ell", 0.06, 0.06, 0.07, 0.05, hl, 0.55)])
        rig.paint(hf, "back", [("line", [(-0.18 + 0.09 * i, 0.60), (-0.2 + 0.09 * i, 0.30)], hd, 0.7) for i in range(5)])
    sub_ = {"long": _long, "bob": _long, "bun": _bun, "ponytail": _ponytail, "pigtails": _pigtails,
            "curly": _curly, "spiky": _spiky, "quiff": _quiff}.get(style)
    if sub_:
        sub_(rig, o, t, m)


def _long(rig, o, t, m):
    """Long hair and bobs: a shell that follows the head round the sides and
    back (open at the face), then for long hair a fall down the back and a
    lock over the near shoulder."""
    hair = o["hair"]
    style = o["hair_style"]
    hd = ("~", hair, 0.8)
    zb = 0.12 if style == "bob" else 0.02
    rows = []
    for z in (zb, 0.28, 0.50, 0.60):
        f, b, w, rf, rb = head_dims(max(z, 0.1))
        grow = t + (0.02 if z <= zb + 1e-6 and style == "bob" else 0.0)
        front = min(f + grow, FACE_F - (0.12 if z < 0.4 else 0.07))
        rows.append(hring(0.0, 0.0, z, front, b + grow, w + grow, min(rf + grow, 0.12), rb + grow, m))
    sf = rig.solid(rows, hair, top=None, bottom=hair, part="hair shell")
    rig.paint(sf, "side", [("line", [(-0.22 + 0.11 * i, 0.58), (-0.24 + 0.11 * i + 0.03, zb + 0.04)], hd, 0.7) for i in range(4)])
    rig.paint(sf, "back", [("line", [(-0.24 + 0.12 * i, 0.58), (-0.24 + 0.12 * i, zb + 0.05)], hd, 0.7) for i in range(5)])
    if style == "long":
        # the fall down the back, tapering
        rings = [rring((-0.29, 0.0, z), (1, 0, 0), (0, 1, 0), d, d, w, w, (d * 0.9,) * 4, 2)
                 for z, w, d in ((-0.44, 0.20, 0.05), (-0.2, 0.27, 0.07), (0.06, 0.31, 0.08))]
        bf = rig.solid(rings, hair, top=None, bottom=hair, part="hair back")
        rig.paint(bf, "back", [("line", [(-0.2 + 0.1 * i, 0.0), (-0.16 + 0.08 * i, -0.38)], hd, 0.7) for i in range(5)])
        # a lock falling over the near shoulder onto the chest (not when lying down)
        if o.get("_whole") not in ("lie", "sleep"):
            rig.chain([((0.10, 0.33, 0.20), 0.065), ((0.18, 0.34, -0.06), 0.07), ((0.24, 0.27, -0.24), 0.06),
                       ((0.25, 0.25, -0.46), 0.035)], hair, part="hair lock")


def _bun(rig, o, t, m):
    rig.ball((-0.12, 0.0, HEAD_H + t + 0.10), 0.14, o["hair"], part="bun")


def _ponytail(rig, o, t, m):
    hair = o["hair"]
    rig.ball((-0.33, 0.0, 0.50), 0.05, "coral", part="hair tie")
    rig.chain([((-0.38, 0.0, 0.50), 0.075), ((-0.47, 0.0, 0.34), 0.07), ((-0.45, 0.0, 0.10), 0.055),
               ((-0.38, 0.0, -0.05), 0.03)], hair, part="ponytail")


def _pigtails(rig, o, t, m):
    hair = o["hair"]
    for sg in (1, -1):
        rig.ball((-0.04, sg * 0.36, 0.48), 0.045, "coral", part="hair tie")
        rig.chain([((-0.04, sg * 0.40, 0.48), 0.07), ((-0.06, sg * 0.48, 0.32), 0.065), ((-0.05, sg * 0.47, 0.14), 0.04)],
                  hair, part="pigtail")


def _curly(rig, o, t, m):
    hair = o["hair"]
    pts = []
    for i in range(12):
        a = math.radians(30 * i + 15)
        if math.cos(a) > 0.86:
            continue
        f, b, w, rf, rb = head_dims(0.58)
        pts.append(((f + 0.05) * math.cos(a) if math.cos(a) > 0 else (b + 0.05) * math.cos(a), (w + 0.05) * math.sin(a), 0.60))
    for i in range(6):
        a = math.radians(60 * i + 30)
        pts.append((0.15 * math.cos(a), 0.15 * math.sin(a), HEAD_H + t + 0.02))
    for p in pts:
        rig.ball(p, 0.085, hair, part="curl")


def _spiky(rig, o, t, m):
    hair = o["hair"]
    for b0, w, hh in ((-0.2, 0.15, 0.13), (-0.04, 0.16, 0.18), (0.13, 0.15, 0.14)):
        f0, f1 = -0.12, 0.24
        z = HEAD_H + t * 0.9
        ring0 = [(f1, b0, z), (f1, b0 + w, z), (f0, b0 + w, z), (f0, b0, z)]
        ring1 = [(f0 + 0.02, b0 + w * 0.3, z + hh), (f0 + 0.02, b0 + w * 0.7, z + hh), (f0 - 0.04, b0 + w * 0.7, z + hh),
                 (f0 - 0.04, b0 + w * 0.3, z + hh)]
        rig.solid([ring0, ring1], hair, top=hair, part="spike")


def _quiff(rig, o, t, m):
    hair = o["hair"]
    rings = [hring(0.12, 0.0, HEAD_H + t * 0.55, 0.15, 0.16, 0.19, 0.10, 0.10, m),
             hring(0.16, 0.0, HEAD_H + t + 0.05, 0.14, 0.12, 0.15, 0.09, 0.08, m),
             hring(0.16, 0.0, HEAD_H + t + 0.075, 0.08, 0.06, 0.09, 0.05, 0.04, m)]
    qf = rig.solid(rings, hair, top=hair, part="quiff")
    rig.paint(qf, "top", [("line", [(0.28, -0.08 + 0.05 * i), (0.08, -0.07 + 0.05 * i)], ("~", hair, 0.8), 0.7) for i in range(4)])


def _hijab(rig, o, hf):
    col = o["hair"]
    m = 2 if o["_lod"] >= 1 else 1
    t = 0.045
    rings = []
    for z in (0.08, 0.28, 0.50, 0.64, HEAD_H):
        f, b, w, rf, rb = head_dims(z)
        rings.append(hring(0.0, 0.0, z, min(f + t, FACE_F - 0.04), b + t, w + t, rf + t, rb + t, m))
    rings[-1] = [(p[0], p[1], HEAD_H + t * 0.8) for p in rings[-1]]
    rings.append([(p[0] * 0.7, p[1] * 0.7, HEAD_H + t) for p in rings[-1]])
    sf = rig.solid(rings, col, top=col, part="hijab")
    dk = ("~", col, 0.82)
    rig.paint(sf, "side", [("line", [(0.12, 0.62), (0.02, 0.10)], dk, 0.8), ("line", [(-0.1, 0.66), (-0.2, 0.14)], dk, 0.8)])
    # the edge of the scarf framing the face
    zlo, _ = _hairline("hijab")
    rig.cover(hf, lambda th: zlo(th) - 0.022, zlo, ("~", col, 0.86))


def _hat(rig, o):
    style = o["hair_style"]
    col = o["hat"] or ("brand" if style == "cap" else "gold")
    m = 2 if o["_lod"] >= 1 else 1

    def r(z, grow, sh=1.0):
        f, b, w, rf, rb = head_dims(min(z, HEAD_H))
        return hring(0.0, 0.0, z, (f + grow) * sh, (b + grow) * sh, (w + grow) * sh, rf + grow * 0.5, rb + grow * 0.5, m)
    if style == "cap":
        rings = [r(0.52, 0.035), r(0.66, 0.04), r(HEAD_H + 0.04, 0.035, 0.85), r(HEAD_H + 0.085, 0.0, 0.5)]
        rings[2] = [(p[0], p[1], HEAD_H + 0.045) for p in rings[2]]
        rings[3] = [(p[0], p[1], HEAD_H + 0.085) for p in rings[3]]
        cf = rig.solid(rings, col, top=col, part="cap")
        rig.paint(cf, "front", [("ell", 0.0, 0.64, 0.05, 0.045, "paper")])
        rig.paint(cf, "side", [("line", [(0.12, 0.54), (0.02, HEAD_H + 0.04)], ("~", col, 0.8), 0.8)])
        brim = [rring((FACE_F + 0.02, 0.0, 0.53), (1, 0, 0), (0, 1, 0), 0.02, 0.22, 0.20, 0.20, (0.12, 0.02, 0.02, 0.12), 2),
                [(p[0], p[1], 0.555) for p in rring((FACE_F + 0.02, 0.0, 0.555), (1, 0, 0), (0, 1, 0), 0.02, 0.22, 0.20, 0.20,
                                                    (0.12, 0.02, 0.02, 0.12), 2)]]
        brim[0] = [(p[0], p[1], 0.525 - 0.06 * max(0.0, p[0] - FACE_F) / 0.24) for p in brim[0]]
        brim[1] = [(p[0], p[1], 0.555 - 0.06 * max(0.0, p[0] - FACE_F) / 0.24) for p in brim[1]]
        rig.solid(brim, ("~", col, 0.9), top=("~", col, 0.9), part="cap brim")
        rig.ball((0.0, 0.0, HEAD_H + 0.095), 0.025, col, part="cap button")
    else:
        brim = [r(0.55, 0.075), r(0.572, 0.075)]
        brim = [[(p[0] + (0.05 if p[0] > 0 else 0), p[1], z) for p in rr] for rr, z in zip(brim, (0.55, 0.572))]
        rig.solid(brim, col, top=col, part="hat brim")
        rings = [r(0.572, 0.045), r(0.68, 0.05), r(HEAD_H, 0.05), r(HEAD_H, 0.03, 0.84), r(HEAD_H, 0.0, 0.5)]
        for i, zz in ((2, HEAD_H + 0.06), (3, HEAD_H + 0.13), (4, HEAD_H + 0.16)):
            rings[i] = [(p[0], p[1], zz) for p in rings[i]]
        df = rig.solid(rings, col, top=col, part="hat dome")
        rig.paint(df, "front", [("rect", -0.045, 0.565, 0.09, 0.3, ("~", col, 1.15))])
        rig.paint(df, "top", [("rect", -0.3, -0.045, 0.6, 0.09, ("~", col, 1.15))])


def _face(rig, o, hf):
    skin = o["skin"]
    lod = o["_lod"]
    F = []
    eyes, mouth = o["eyes"], o["mouth"]
    E, ez = 0.125, 0.355
    ink = "_face"
    brow_c = ("~", o["hair"] if o["hair_style"] not in ("hijab", "bald") else "hair1", 0.8)
    if o["hair_style"] == "bald":
        brow_c = ("~", o["hair"], 0.7)
    if o["beard"]:
        bc = o["beard"] if o["beard"] is not True else o["hair"]
        blo = keys((0, -1), (180, -1))
        bhi = keys((0, 0.115), (16, 0.10), (28, 0.20), (50, 0.27), (64, 0.32), (75, 0.33), (82, 0.0), (180, 0.0))
        rig.cover(hf, blo, bhi, bc)
        F.append(("poly", [(-0.10, 0.165), (-0.04, 0.205), (0.0, 0.195), (0.04, 0.205), (0.10, 0.165), (0.07, 0.165),
                           (0.0, 0.18), (-0.07, 0.165)], bc))
    for sg in (-1, 1):
        ex = sg * E
        closed = eyes == "closed" or (eyes == "wink" and sg < 0)
        if lod == 0:
            if eyes == "happy":
                F.append(("arc", ex, ez - 0.005, 0.10, -0.03, ink, 1.6))
            elif closed:
                F.append(("arc", ex, ez + 0.01, 0.10, 0.022, ink, 1.4))
            else:
                F.append(("ell", ex, ez, 0.04, 0.056, ink))
                F.append(("ell", ex - 0.012, ez + 0.024, 0.013, 0.016, "!eyewhite"))
        else:
            o_, i_ = ex + sg * 0.062, ex - sg * 0.058          # outer and inner corners
            if eyes == "happy":
                F.append(("arc", ex, ez - 0.008, 0.115, -0.034, ink, 1.7))
                if lod >= 2:
                    F.append(("arc", ex, ez - 0.045, 0.08, -0.008, ("~", skin, 0.84), 0.8))
            elif closed:
                F.append(("arc", ex, ez + 0.008, 0.12, 0.024, ink, 1.6))
                if lod >= 2:
                    F += [("line", [(ex + sg * 0.035 * j, ez - 0.012 - 0.004 * abs(j)), (ex + sg * 0.045 * j, ez - 0.03 - 0.004 * abs(j))],
                           ink, 0.8) for j in (-1, 0, 1)]
            else:
                up = [(i_, ez - 0.002), (ex - sg * 0.025, ez + 0.026), (ex + sg * 0.015, ez + 0.032), (o_, ez + 0.008)]
                lo = [(o_, ez + 0.004), (ex + sg * 0.02, ez - 0.024), (ex - sg * 0.025, ez - 0.022), (i_, ez - 0.004)]
                F.append(("poly", up + lo, "!eyewhite"))
                F.append(("ell", ex + sg * 0.004, ez + 0.002, 0.025, 0.026, o["eye_color"]))
                F.append(("ell", ex + sg * 0.004, ez + 0.002, 0.012, 0.013, ink))
                F.append(("ell", ex - 0.006, ez + 0.012, 0.0075, 0.0075, "!eyewhite"))
                F.append(("line", up + [(o_ + sg * 0.014, ez + 0.016)], ink, 1.5 if lod >= 2 else 1.3))
                if lod >= 2:
                    F.append(("line", lo[1:], ("~", skin, 0.7), 0.7))
                    F.append(("line", [(i_ + sg * 0.01, ez + 0.03), (ex, ez + 0.05), (o_ - sg * 0.004, ez + 0.032)], ("~", skin, 0.8), 0.8))
        if o["brows"]:
            bi, bo = sg * 0.045, sg * 0.20
            lift = 0.0
            if mouth in ("o", "open"):
                lift = 0.012
            pts_t = [(bi, 0.455 + lift), (sg * 0.14, 0.478 + lift), (bo, 0.462)]
            pts_b = [(bo, 0.452), (sg * 0.14, 0.462 + lift), (bi, 0.428 + lift)]
            if lod == 0:
                F.append(("line", [(sg * 0.07, 0.45), (sg * 0.18, 0.46)], brow_c, 1.4))
            else:
                F.append(("poly", pts_t + pts_b, brow_c))
    # the nose: a soft wedge, shading only, and its shadow
    if lod >= 1:
        rig_nose(rig, skin)
        F += [("poly", [(0.02, 0.24), (0.075, 0.245), (0.05, 0.215), (0.0, 0.21)], ("~", skin, 0.84))]
        if lod >= 2:
            F += [("ell", -0.026, 0.232, 0.011, 0.007, ("~", skin, 0.6)), ("ell", 0.026, 0.232, 0.011, 0.007, ("~", skin, 0.6))]
    else:
        F.append(("rect", -0.02, 0.22, 0.04, 0.04, ("~", skin, 0.84)))
    # the mouth
    mx, my = 0.0, 0.15
    lipc = ("~", skin, 0.84)
    if mouth == "smile":
        if lod >= 1:
            F.append(("poly", [(-0.045, my - 0.004), (0.0, my - 0.024), (0.045, my - 0.004), (0.0, my - 0.012)], lipc))
        F.append(("arc", mx, my + 0.012, 0.14, 0.018, ink if lod == 0 else ("~", skin, 0.55), 1.05))
        if lod >= 2:
            F += [("line", [(-0.082, my + 0.016), (-0.072, my + 0.008)], ("~", skin, 0.6), 0.8),
                  ("line", [(0.082, my + 0.016), (0.072, my + 0.008)], ("~", skin, 0.6), 0.8)]
    elif mouth == "grin":
        q = [(-0.085, my + 0.015), (0.085, my + 0.015), (0.05, my - 0.04), (0.0, my - 0.052), (-0.05, my - 0.04)]
        F.append(("poly", q, "!mouth"))
        F.append(("poly", [(-0.08, my + 0.013), (0.08, my + 0.013), (0.065, my - 0.008), (-0.065, my - 0.008)], "!eyewhite"))
        if lod >= 1:
            F.append(("poly", [(-0.035, my - 0.038), (0.035, my - 0.038), (0.02, my - 0.05), (-0.02, my - 0.05)], "rose"))
        F.append(("line", q + [q[0]], ("~", skin, 0.45) if lod else ink, 1.1))
    elif mouth == "open":
        F.append(("ell", mx, my - 0.01, 0.042, 0.048, "!mouth"))
        F.append(("ell", mx, my - 0.04, 0.026, 0.014, "rose"))
    elif mouth == "o":
        F.append(("ell", mx, my - 0.008, 0.026, 0.03, "!mouth"))
        F.append(("ring", mx, my - 0.008, 0.03, 0.034, lipc, 1.4))
    elif mouth == "frown":
        F.append(("arc", mx, my - 0.012, 0.13, -0.018, ("~", skin, 0.45) if lod else ink, 1.4))
    else:
        F.append(("line", [(mx - 0.06, my), (mx + 0.06, my)], ("~", skin, 0.45) if lod else ink, 1.4))
        if lod >= 1:
            F.append(("poly", [(-0.045, my - 0.006), (0.045, my - 0.006), (0.0, my - 0.022)], lipc))
    if not o["beard"] and lod >= 2:
        F.append(("arc", 0.0, 0.07, 0.07, -0.008, ("~", skin, 0.86), 0.9))
    if o["blush"]:
        F += [("ell", -0.2, 0.25, 0.055, 0.028, "blush", 0.6), ("ell", 0.2, 0.25, 0.055, 0.028, "blush", 0.6)]
    if o["glasses"]:
        g, gw = o["glasses"], 0.085
        F.append(("ell", -E, ez, gw, 0.062, "glass", 0.22))
        F.append(("ell", E, ez, gw, 0.062, "glass", 0.22))
        for a in (-E, E):
            F.append(("ring", a, ez, gw, 0.062, g, 1.3))
        F.append(("line", [(-E + gw, ez + 0.02), (E - gw, ez + 0.02)], g, 1.3))
    rig.paint(hf, "front", F)


def rig_nose(rig, skin):
    f0 = FACE_F - 0.004
    top = (f0, 0.0, 0.405)
    tip = (f0 + 0.055, 0.0, 0.245)
    bl, br = (f0, -0.05, 0.225), (f0, 0.05, 0.225)
    under = (f0 + 0.03, 0.0, 0.215)
    sc = rig.sc
    cw = rig.W((f0 - 0.05, 0.0, 0.3))
    with sc.tag(rig.tag + " nose"), sc.outline(rig.ol, soft=True):
        for tri in ((top, tip, br), (top, bl, tip), (tip, under, br), (tip, bl, under)):
            sc.poly([rig.W(p) for p in tri], skin, snap=False, inside=cw, stroke=False)


# ── held and carried things ────────────────────────────────────────────────
def _held(rig, o, P, U, hands):
    carry, col = o["carry"], o["carry_color"]
    held, hc = o["holding"], o["hold_color"]
    hn, hf_ = hands[True], hands[False]
    if carry and P["arms"] in ("down", "phone", "point", "wave") and P["whole"] == "stand":
        g = hn["tip"]
        if carry in ("bag", "basket", "briefcase"):
            hgt = {"bag": 0.32, "basket": 0.24, "briefcase": 0.30}[carry]
            w = {"bag": 0.30, "basket": 0.36, "briefcase": 0.42}[carry]
            dep = 0.12 if carry != "basket" else 0.16
            c = (g[0], g[1] + dep / 2 - 0.02, g[2] - 0.08 - hgt / 2)
            bf = rig.box(c, (1, 0, 0), (0, 1, 0), (0, 0, 1), w / 2, dep / 2, hgt / 2, col, r=0.03, part=carry)
            hcol = ("~", col, 0.65)
            with rig.sc.tag(rig.tag + " handle"):
                rig.sc.line([rig.W((c[0] - w / 2 + 0.07, c[1], c[2] + hgt / 2)), rig.W(add(g, (0, 0.0, 0.02))),
                             rig.W((c[0] + w / 2 - 0.07, c[1], c[2] + hgt / 2))], hcol, 1.6 * rig.wk)
            if carry == "briefcase":
                rig.paint(bf, "side", [("rect", c[0] - 0.04, c[2] + hgt / 2 - 0.08, 0.08, 0.04, "gold")])
            if carry == "basket":
                rig.paint(bf, "side", [("line", [(c[0] - w / 2 + 0.03, c[2]), (c[0] + w / 2 - 0.03, c[2])], ("~", col, 0.7), 1.0)])
        elif carry == "suitcase":
            c = (CF - 0.42, CS + 0.48, 0.40)
            bf = rig.box(c, (1, 0, 0), (0, 1, 0), (0, 0, 1), 0.21, 0.12, 0.32, col, r=0.04, part="suitcase")
            rig.paint(bf, "side", [("line", [(c[0] - 0.09, 0.12), (c[0] - 0.09, 0.66)], ("~", col, 0.75), 1.0),
                                   ("line", [(c[0] + 0.09, 0.12), (c[0] + 0.09, 0.66)], ("~", col, 0.75), 1.0)])
            for wf in (c[0] - 0.14, c[0] + 0.14):
                rig.ball((wf, c[1], 0.04), 0.04, "navy", part="wheel")
            with rig.sc.tag(rig.tag + " handle"):
                rig.sc.line([rig.W((c[0] + 0.12, c[1], 0.72)), rig.W(g)], "steel", 2 * rig.wk)
    if not held:
        return
    c = hc or {"box": "wood", "tablet": "navy", "book": "coral", "clipboard": "wood", "cup": "paper",
               "phone": "navy", "plate": "paper", "laptop": "steel"}.get(held, "gold")
    if P["arms"] in ("hold", "lap", "knees"):
        mid = lerp(hn["palm"], hf_["palm"], 0.5)
        ea, eb, ec = U.vec((1, 0, 0)), U.vec((0, 1, 0)), U.vec((0, 0, 1))
        if P["arms"] in ("lap", "knees"):
            ea, eb, ec = (1, 0, 0), (0, 1, 0), (0, 0, 1)
        half_s = max(0.12, abs(hn["palm"][1] - hf_["palm"][1]) / 2 - 0.06)
        if held == "box":
            bc = add(mid, mul(ec, 0.08))
            bf = rig.box(bc, ea, eb, ec, 0.17, half_s, 0.14, c, r=0.01, part="box")
            rig.paint(bf, "top", [("line", [(bc[0] - 0.17, bc[1]), (bc[0] + 0.17, bc[1])], ("~", c, 0.7), 1.0)])
            rig.paint(bf, "front", [("rect", bc[1] - 0.06, bc[2] + 0.04, 0.12, 0.05, "paper")])
        elif held in ("tablet", "book", "clipboard", "plate", "laptop"):
            th = {"tablet": 0.018, "book": 0.04, "clipboard": 0.015, "plate": 0.015, "laptop": 0.018}[held]
            bc = add(mid, mul(ec, 0.06 + th))
            bf = rig.box(bc, ea, eb, ec, 0.15, min(half_s, 0.2), th, c, r=0.01, part=held)
            x0, y0 = bc[0], bc[1]
            if held == "tablet":
                rig.paint(bf, "top", [("rect", x0 - 0.12, y0 - min(half_s, 0.2) + 0.03, 0.24, 2 * min(half_s, 0.2) - 0.06, "!screen")])
            elif held == "clipboard":
                rig.paint(bf, "top", [("rect", x0 - 0.12, y0 - 0.15, 0.22, 0.3, "paper"), ("rect", x0 + 0.08, y0 - 0.05, 0.04, 0.1, "steel")])
            elif held == "book":
                rig.paint(bf, "front", [("rect", y0 - 0.2, bc[2] - 0.025, 0.4, 0.05, "paper")])
            elif held == "laptop":
                rig.paint(bf, "top", [("rect", x0 - 0.10, y0 - 0.14, 0.14, 0.28, ("~", c, 0.85))])
                lc = add(bc, add(mul(ea, 0.15), mul(ec, 0.13)))
                lf = rig.box(lc, ec, eb, mul(ea, -1), 0.13, min(half_s, 0.2), 0.012, c, r=0.01, part="laptop lid")
                rig.paint(lf, "front", [("ell", lc[1], lc[2], 0.025, 0.025, "!paper")])
        elif held == "cup":
            p = hn["palm"]
            rig.tube([(add(p, (0, 0, -0.06)), 0.06, add(p, (0, 0, 0.09)), 0.068, c, "f", "o")], "cup")
    elif held == "cup":
        p = hn["palm"]
        rig.tube([(add(p, (0, 0, -0.06)), 0.06, add(p, (0, 0, 0.09)), 0.068, c, "f", "o")], "cup")
    if P["arms"] == "phone" or held == "phone":
        h = hn
        d = h["d"]
        pc = add(h["palm"], mul(d, 0.04))
        face_dir = unit(sub((HEAD_F + 0.2, CS, 2.1), pc))
        rig.box(pc, unit(cross(face_dir, (0, 0, 1))) if abs(face_dir[2]) < 0.95 else (0, 1, 0), unit(cross(cross(face_dir, (0, 0, 1)), face_dir)),
                     face_dir, 0.045, 0.085, 0.01, "navy", r=0.012, part="phone")
