"""The blog's design tokens, read from assets/css/blog.css (the single source of truth).

Figures never carry a hex colour: they paint with roles (`hl`, `a`, `base`, `s1`...), written
as `var(--pi-<role>)`, so one SVG follows the reader's theme. This module resolves the roles
to hex for previews and for the checks (contrast, colour-blind separation).

    from pi.tokens import hexes, contrast, cvd_distance
    hexes('dark')['hl']   -> '#F05252'
"""
import math, os, re

BLOG = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', '..'))
CSS = os.path.join(BLOG, 'assets', 'css', 'blog.css')

ROLES = ['ink', 'label', 'grid', 'axis', 'bg', 'hl', 'hl-soft', 'a', 'a-soft', 'base', 'base-soft',
         'gold', 'teal', 'pos', 'neg', 's1', 's2', 's3', 's4', 's5', 'seq1', 'seq2', 'seq3', 'seq4',
         'seq5', 'div1', 'div2', 'div3', 'div4', 'div5', 'land', 'land-ctx', 'land-line', 'node', 'node-line', 'shade', 'light',
         'hl-ink', 'a-ink', 'base-ink', 'gold-ink', 'teal-ink', 's1-ink', 's2-ink', 's3-ink', 's4-ink', 's5-ink']
# Every role the engine accepts, plus the page tokens a figure may borrow.
PAGE = ['text', 'muted', 'panel', 'bg', 'border', 'border-strong', 'accent', 'accent-strong', 'accent2',
        'accent3', 'gold', 'positive', 'negative', 'chart-text', 'chart-grid']


def _blocks(css):
    dark, light = {}, {}
    for sel, body in re.findall(r'(:root(?:\.light)?)\s*\{([^}]*)\}', css):
        target = light if sel == ':root.light' else dark
        for k, v in re.findall(r'--([\w-]+)\s*:\s*([^;]+);', body):
            target[k] = v.strip()
    return dark, light


def _resolve(name, table, fallback, depth=0):
    v = table.get(name, fallback.get(name))
    if v is None or depth > 8:
        return None
    m = re.fullmatch(r'var\(--([\w-]+)\)', v)
    if m:
        return _resolve(m.group(1), table, fallback, depth + 1)
    return v


_cache = {}


def tokens(theme='dark'):
    if theme not in _cache:
        dark, light = _blocks(open(CSS, encoding='utf-8').read())
        merged = dict(dark)
        merged.update(light)
        _cache['dark'] = {k: _resolve(k, dark, dark) for k in dark}
        _cache['light'] = {k: _resolve(k, merged, dark) for k in merged}
    return _cache[theme]


def hexes(theme='dark'):
    t = tokens(theme)
    return {r: t.get('pi-' + r) for r in ROLES}


def paint(role):
    """CSS paint for a role: 'hl' -> var(--pi-hl); a page token: 'text' -> var(--text);
    'none' stays none."""
    if role in (None, 'none', 'transparent'):
        return 'none'
    if role.startswith('#') or role.startswith('var('):
        raise ValueError(f'paint with a role, not a colour: {role}')
    if role in ROLES:
        return f'var(--pi-{role})'
    if role in PAGE:
        return f'var(--{role})'
    raise ValueError(f'unknown colour role {role!r}; roles: {", ".join(ROLES)}')


# ── colour maths ───────────────────────────────────────────────────────────
def rgb(h):
    h = h.lstrip('#')
    if len(h) == 3:
        h = ''.join(c * 2 for c in h)
    return tuple(int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))


def _lin(c):
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def luminance(h):
    r, g, b = (_lin(c) for c in rgb(h))
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contrast(a, b):
    la, lb = sorted((luminance(a), luminance(b)), reverse=True)
    return (la + 0.05) / (lb + 0.05)


# Colour-vision deficiency simulation (Machado et al. 2009, severity 1.0) in linear RGB.
_CVD = {
    'protan': [[0.152286, 1.052583, -0.204868], [0.114503, 0.786281, 0.099216], [-0.003882, -0.048116, 1.051998]],
    'deutan': [[0.367322, 0.860646, -0.227968], [0.280085, 0.672501, 0.047413], [-0.011820, 0.042940, 0.968881]],
    'tritan': [[1.255528, -0.076749, -0.178779], [-0.078411, 0.930809, 0.147602], [0.004733, 0.691367, 0.303900]],
}


def simulate(h, kind):
    v = [_lin(c) for c in rgb(h)]
    m = _CVD[kind]
    out = [max(0.0, min(1.0, sum(m[i][j] * v[j] for j in range(3)))) for i in range(3)]
    return out


def _lab(lin):
    r, g, b = lin
    x = (0.4124 * r + 0.3576 * g + 0.1805 * b) / 0.95047
    y = (0.2126 * r + 0.7152 * g + 0.0722 * b)
    z = (0.0193 * r + 0.1192 * g + 0.9505 * b) / 1.08883
    f = lambda t: t ** (1 / 3) if t > 0.008856 else 7.787 * t + 16 / 116
    fx, fy, fz = f(x), f(y), f(z)
    return 116 * fy - 16, 500 * (fx - fy), 200 * (fy - fz)


def delta_e(a, b, kind=None):
    """CIE76 distance between two hex colours, optionally as a colour-blind reader sees them."""
    la = simulate(a, kind) if kind else [_lin(c) for c in rgb(a)]
    lb = simulate(b, kind) if kind else [_lin(c) for c in rgb(b)]
    return math.dist(_lab(la), _lab(lb))


def cvd_distance(a, b):
    """The smallest distance between two colours across normal vision and the three deficiencies."""
    return min(delta_e(a, b, k) for k in (None, 'protan', 'deutan', 'tritan'))


def ink(role):
    """The text colour that goes with a fill role: 'hl' -> 'hl-ink' (4.5:1 on the card), else 'ink'."""
    return role + '-ink' if role and role + '-ink' in ROLES else ('label' if role in ('base-soft', 'grid') else 'ink')
