"""Text measurement in the blog's own fonts, without a browser.

The widths of every glyph of DM Sans (400 to 700) and DM Mono (400, 500) were measured in
Chromium at eight sizes, because DM Sans has an optical-size axis: small text is set wider
than large text. `width()` interpolates between the measured sizes and applies the average
kerning, so a label's box is within about 2% of what the browser draws.
"""
import json, os, re

_M = json.load(open(os.path.join(os.path.dirname(__file__), '..', '..', 'assets', 'metrics.json'),
                    encoding='utf-8'))
_SIZES = _M['sizes']
SAFETY = 1.03  # a little air so two labels never touch even where kerning differs


def _font(weight, mono):
    if mono:
        return _M['fonts']['mono500' if weight >= 500 else 'mono400']
    w = min((400, 500, 600, 700), key=lambda k: abs(k - weight))
    return _M['fonts'][f'sans{w}']


def _em(text, table):
    w = table['w']
    total = 0
    for ch in text:
        v = w.get(ch)
        if v is None:
            v = 1000 if ord(ch) > 0x2E80 else 560  # CJK full width, anything else ~ a lowercase letter
        total += v
    return total * table['kern'] / 1000.0


def width(text, size=14, weight=400, mono=False):
    """Advance width of `text` in px at `size` px."""
    text = str(text)
    if not text:
        return 0.0
    f = _font(weight, mono)
    lo = max([s for s in _SIZES if s <= size] or [_SIZES[0]])
    hi = min([s for s in _SIZES if s >= size] or [_SIZES[-1]])
    a = _em(text, f[str(lo)])
    if hi == lo:
        em = a
    else:
        b = _em(text, f[str(hi)])
        em = a + (b - a) * (size - lo) / (hi - lo)
    return em * size * SAFETY


def wrap(text, max_w, size=14, weight=400, mono=False):
    """Greedy word wrap into lines no wider than max_w (a long word gets its own line)."""
    words = re.split(r'(\s+)', str(text).strip())
    lines, cur = [], ''
    for w in words:
        if not w:
            continue
        if w.isspace():
            if cur:
                cur += ' '
            continue
        trial = cur + w
        if cur and width(trial.rstrip(), size, weight, mono) > max_w:
            lines.append(cur.rstrip())
            cur = w
        else:
            cur = trial
    if cur.strip():
        lines.append(cur.rstrip())
    out = []
    for ln in lines:  # explicit line breaks in the source
        out += ln.split('\n')
    return out or ['']


def block(text, max_w, size=14, weight=400, lh=1.25, mono=False):
    """Wrapped lines plus the block's width and height."""
    lines = wrap(text, max_w, size, weight, mono)
    w = max(width(l, size, weight, mono) for l in lines)
    return lines, w, len(lines) * size * lh
