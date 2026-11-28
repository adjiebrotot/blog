"""Numbers written the way each language writes them, with one precision per series.

English: 1,234.5 · 9.0% · Rp 1.2 trillion · A$1,250
Indonesian: 1.234,5 · 9,0% · Rp1,2 triliun · A$1.250

Checklist item 3 (consistent decimals): pick `dp` once per series or axis with `dp_for()`
and pass it to every label of that series; never let each value choose its own.
"""
import math

GROUP = {'en': (',', '.'), 'id': ('.', ',')}
COMPACT = {
    'en': [(1e12, ' trillion', 'tn'), (1e9, ' billion', 'bn'), (1e6, ' million', 'm'), (1e3, ' thousand', 'k')],
    'id': [(1e12, ' triliun', ' T'), (1e9, ' miliar', ' M'), (1e6, ' juta', ' jt'), (1e3, ' ribu', ' rb')],
}
MINUS = '−'  # a real minus sign, as wide as the plus


def number(v, dp=0, lang='en', sign=False, group=True):
    if v is None or (isinstance(v, float) and math.isnan(v)):
        return '–'
    th, dec = GROUP.get(lang, GROUP['en'])
    neg = v < 0
    s = f'{abs(v):,.{dp}f}'
    s = s.replace(',', '\0').replace('.', dec).replace('\0', th if group else '')
    if neg and float(s.replace(th, '').replace(dec, '.') or 0) != 0:
        s = MINUS + s
    elif sign and v > 0:
        s = '+' + s
    return s


def pct(v, dp=1, lang='en', sign=False):
    return number(v, dp, lang, sign) + '%'


def money(v, cur='Rp', dp=0, lang='en', compact=None, sign=False):
    """cur is the symbol as written before the number: 'Rp', 'A$', 'S$', 'US$', '$', '¥'.
    compact: None, 'short' (Rp1.2tn / Rp1,2 T) or 'long' (Rp1.2 trillion / Rp1,2 triliun)."""
    body = compact_number(v, dp, lang, compact) if compact else number(abs(v), dp, lang)
    if compact:
        body = body.lstrip(MINUS)
    sp = ' ' if (lang == 'en' and cur.isalpha() and cur != 'Rp') else ''
    s = f'{cur}{sp}{body}'
    if v < 0:
        s = MINUS + s
    elif sign and v > 0:
        s = '+' + s
    return s


def compact_number(v, dp=1, lang='en', style='short'):
    for base, long, short in COMPACT.get(lang, COMPACT['en']):
        if abs(v) >= base:
            return number(v / base, dp, lang) + (long if style == 'long' else short)
    return number(v, dp, lang)


def dp_for(values, max_dp=2):
    """The fewest decimals that keep every value distinct and honest: the most any value needs,
    capped at max_dp. Use the result for the whole series."""
    need = 0
    for v in values:
        if v is None:
            continue
        for d in range(max_dp + 1):
            if abs(round(v, d) - v) < 1e-9:
                need = max(need, d)
                break
        else:
            need = max_dp
    return need


def tick(v, step, lang='en', unit='', prefix=''):
    """Axis tick text: decimals follow the step, so ticks never read 2.50, 5.00."""
    dp = 0 if step >= 1 else min(4, int(math.ceil(-math.log10(step) - 1e-9)))
    if abs(step * 10 ** dp - round(step * 10 ** dp)) > 1e-9:
        dp += 1
    return f'{prefix}{number(v, dp, lang)}{unit}'
