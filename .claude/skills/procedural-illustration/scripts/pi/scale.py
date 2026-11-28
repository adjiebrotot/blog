"""Scales: data value -> pixel. Nice ticks (1, 2, 2.5, 5 x 10^n) like Chart.js draws them."""
import math


def nice_step(span, n=5):
    if span <= 0:
        return 1
    raw = span / max(1, n)
    mag = 10 ** math.floor(math.log10(raw))
    for m in (1, 2, 2.5, 5, 10):
        if raw <= m * mag + 1e-12:
            return m * mag
    return 10 * mag


class Linear:
    """Linear scale. `zero=True` (the default for bars and areas) keeps 0 in the domain:
    checklist item 13. A line chart may leave zero out, and then the frame says so."""

    def __init__(self, lo, hi, r0, r1, zero=True, nice=True, ticks=5, step=None):
        if zero:
            lo, hi = min(lo, 0), max(hi, 0)
        if lo == hi:
            hi = lo + 1
        self.step = step or nice_step(hi - lo, ticks)
        if nice:
            lo = math.floor(lo / self.step + 1e-9) * self.step
            hi = math.ceil(hi / self.step - 1e-9) * self.step
        self.lo, self.hi, self.r0, self.r1 = lo, hi, r0, r1
        self.zero_based = lo <= 0 <= hi

    def __call__(self, v):
        return self.r0 + (v - self.lo) / (self.hi - self.lo) * (self.r1 - self.r0)

    def ticks(self):
        out, v = [], self.lo
        while v <= self.hi + self.step * 1e-6:
            out.append(round(v, 10))
            v += self.step
        return out


class Band:
    """Categories in order, each a band; `inner` is the gap between bars as a share of the step."""

    def __init__(self, keys, r0, r1, inner=0.3, outer=0.15):
        self.keys = list(keys)
        n = len(self.keys)
        self.step = (r1 - r0) / max(1, n - inner + 2 * outer)
        self.bw = self.step * (1 - inner)
        self.start = r0 + self.step * outer
        self.r0, self.r1 = r0, r1

    def __call__(self, k):
        i = self.keys.index(k) if k in self.keys else int(k)
        return self.start + i * self.step

    def mid(self, k):
        return self(k) + self.bw / 2
