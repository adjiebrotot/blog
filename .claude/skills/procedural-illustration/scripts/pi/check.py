"""The 21-point presentation checklist (references/checklist.md), run on a rendered figure.

Items the drawing can prove are checked here (sizes, overlaps, frame, decimals, legend,
zero baseline, colours, contrast, decoration). Items that need judgement (is this the right
chart type, is anything cherry-picked, does it stand alone) must be answered in the spec's
`review={...}`: a missing answer is an ERROR, so nobody ships a chart without thinking about
them. Levels: ERROR blocks publishing, WARN should be fixed, REVIEW is for a human look.
"""
import re

from .figure import tr
from .tokens import hexes, contrast, cvd_distance, ROLES

# review keys and the checklist items they answer
REVIEW_KEYS = {
    'type': '19 chart type: why this form shows the relationship best',
    'audience': '20 audience: who reads it and how that shaped the detail',
    'transparency': '18 transparency: the full series/range shown, or what was left out and why',
    'standalone': '21 out of context: what a reader sees first with no post around it',
    'outliers': '12 notable points: which spikes, dips or outliers are labelled (or "none")',
}
DIAGRAM_KINDS = ('flow', 'diagram', 'engineering')

PHONES = {'360px phone': 250, '390px phone': 280, '430px phone': 320}


def _decimals(s):
    m = re.search(r'\d([.,])(\d+)(?!.*\d[.,]\d)', s)
    if not m:
        return 0
    return len(m.group(2))


def run(fig, lang):
    out = []
    add = lambda lv, item, msg: out.append((lv, item, msg))
    kind = fig.kind
    is_diagram = kind in DIAGRAM_KINDS
    # 1 source: a link to the post's References section (source='refs'); none for the author's own
    # experience or reasoning (say so in review['source']); never a long list of sources on the figure
    if not fig.source and not fig.review.get('source'):
        add('ERROR', 1, "no source: source='refs' (links to the post's References), or, for the author's own "
                        "experience or reasoning, no source and review['source'] saying so")
    elif isinstance(fig.source, (str, dict)) and fig.source != 'refs' and len(tr(fig.source, lang) or '') > 40:
        add('ERROR', 1, "the source line is long: use source='refs'; the full sources live in the post's References")
    # 2 labels and units: list every word for proofreading
    texts = sorted({t['text'] for cvs in fig.last[lang].values() for t in cvs.texts})
    add('REVIEW', 2, f'proofread every label ({len(texts)}): ' + ' | '.join(x.replace('\n', ' ') for x in texts))
    has_unit = bool(fig.subtitle) or any(getattr(p, 'unit', None) or (getattr(p, 'y', None) or {}).get('unit')
                                         for p in fig.parts)
    if not has_unit and not is_diagram and not fig.review.get('units'):
        add('WARN', 2, 'no unit stated: say it in the subtitle or the axis unit label (%, Rp trillion, days)')
    # 3 decimals
    for p in fig.parts:
        labs = p.value_labels()
        if labs:
            dps = {_decimals(x) for x in labs if re.search(r'\d', x)}
            if len(dps) > 1:
                add('ERROR', 3, f'{type(p).__name__}: mixed decimals {sorted(dps)} in its value labels; '
                                'give fmt={"dp": n}')
    # 4 text size (min size is checked per layout in figure.drawing_issues) + phone size report
    for layout, c in fig.last[lang].items():
        if layout == 'n' and c.texts:
            smallest = min(t['size'] for t in c.texts)
            sizes = ', '.join(f'{k} {smallest * w / c.W:.1f}px' for k, w in PHONES.items())
            add('OK', 4, f'smallest text on phones: {sizes}')
    # 5 redundant text
    if fig.subtitle and tr(fig.subtitle, lang) and tr(fig.subtitle, lang).strip().lower() == tr(fig.title, lang).strip().lower():
        add('ERROR', 5, 'subtitle repeats the title')
    for layout, c in fig.last[lang].items():
        seen = {}
        for t in c.texts:
            if t['kind'] in ('label', 'note', 'axis') and len(t['text']) > 3:
                seen[t['text']] = seen.get(t['text'], 0) + 1
        rep = [k for k, v in seen.items() if v > 2]
        if rep:
            add('WARN', 5, f'[{layout}] the same words drawn {max(seen.values())} times: {rep[:3]}; say it once')
    # 6 decoration: the engine draws none; catch anything pasted in
    for layout, c in fig.last[lang].items():
        raw = ''.join(c.els) + ''.join(c.defs)
        if re.search(r'Gradient|<filter|drop-shadow|blur\(', raw):
            add('ERROR', 6, f'[{layout}] gradient, filter or shadow in the drawing: flat fills only')
        if re.search(r'#[0-9a-fA-F]{3,6}\b', re.sub(r'url\(#[^)]*\)|href="#[^"]*"|id="[^"]*"', '', raw)):
            add('ERROR', 17, f'[{layout}] a hard-coded colour: paint with roles (tokens.py)')
    # 7 title
    t = tr(fig.title, lang) or ''
    if not t:
        add('ERROR', 7, 'no title')
    elif len(t) > 95:
        add('WARN', 7, f'title is {len(t)} characters: keep it under ~90, move detail to the subtitle')
    # 8 subtitle: the metric and unit, short; nothing the drawing already shows, nothing about the screen
    sub = tr(fig.subtitle, lang) or ''
    if sub and len(sub) > 90:
        add('WARN', 8, f'subtitle is {len(sub)} characters: say the metric and unit in under ~90; cut what the '
                       'chart already shows (the years on the axis, what the colours mean)')
    if re.search(r'\b(screen|layar|tap|hover|click|klik|scroll|table|tabel|legend|shaded|warna|colou?r)', sub, re.I):
        add('ERROR', 8, 'the subtitle explains the drawing or the interface (screens, tables, colours): cut it')
    # 9 overlaps / frame / min size
    for lv, m in fig.drawing_issues(lang):
        add(lv, 9 if 'overlap' in m else 4 if 'px' in m and 'under' in m else 10, m)
    # 10 spacing
    for layout, c in fig.last[lang].items():
        H = c.H if c.H is not None else c.maxy
        ratio = H / c.W
        if layout == 'w' and not 0.1 <= ratio <= 1.3:
            add('WARN', 10, f'[w] height/width {ratio:.2f}: the wide layout reads best between 0.35 and 0.9')
        if layout == 'n' and ratio > 3.2:
            add('WARN', 10, f'[n] height/width {ratio:.2f}: very tall on a phone; trim rows or split the figure')
    # 11 legend
    for p in fig.parts:
        if getattr(p, 'legend', False) and not fig.review.get('legend'):
            add('WARN', 11, f'{type(p).__name__} uses a key: label the data directly, or say in review["legend"] '
                            'why a key reads better')
    # 13 axes
    for p in fig.parts:
        y = getattr(p, 'y', None)
        if isinstance(y, dict) and not y.get('zero', getattr(p, 'stack', False)) and not fig.review.get('axis'):
            add('ERROR', 13, f'{type(p).__name__}: the value axis does not start at zero; explain why in '
                             'review["axis"] (and say so on the chart: an index base, a range label)')
    # 14 order
    for p in fig.parts:
        if type(p).__name__ in ('Bars', 'Units') and getattr(p, 'orient', 'h') == 'h' and not fig.review.get('order'):
            add('ERROR', 14, f'{type(p).__name__}: say how the rows are ordered and why in review["order"] '
                             '(largest first, chronological, grouped...)')
    # 15 and 16 colours: roles used, separation, contrast
    used = set()
    for c in fig.last[lang].values():
        raw = ''.join(c.els)
        used |= set(re.findall(r'var\(--pi-([\w-]+)\)', raw))
    data_roles = [r for r in used if r in ('hl', 'a', 'base', 'gold', 'teal', 'pos', 'neg', 's1', 's2', 's3', 's4', 's5')]
    if len(data_roles) > 4:
        add('WARN', 15, f'{len(data_roles)} data colours ({", ".join(sorted(data_roles))}): highlight one thing, '
                        'grey the rest')
    for theme in ('dark', 'light'):
        h = hexes(theme)
        for i, a in enumerate(sorted(data_roles)):
            for b in sorted(data_roles)[i + 1:]:
                d = cvd_distance(h[a], h[b])
                if d < 12 and not fig.review.get('cvd'):
                    add('WARN', 16, f'[{theme}] {a} and {b} are close for colour-blind readers (dE {d:.0f}): '
                                    'label them directly or use a dash/marker, and say so in review["cvd"]')
        for r in used:
            if r.endswith('-ink') or r in ('ink', 'label'):
                cr = contrast(h[r], h['bg'])
                if cr < 4.5:
                    add('ERROR', 16, f'[{theme}] text colour {r} is {cr:.1f}:1 on the card (needs 4.5)')
    # 12, 18, 19, 20, 21: judgement, answered in review
    for k, what in REVIEW_KEYS.items():
        if k == 'outliers' and is_diagram:
            continue
        if not fig.review.get(k):
            add('ERROR', int(what.split()[0]), f'answer review["{k}"]: {what}')
        else:
            add('OK', int(what.split()[0]), f'{k}: {fig.review[k]}')
    # 21 alt text
    if not tr(fig.alt, lang):
        add('ERROR', 21, 'no alt text in this language: alt={...} says what the figure shows and its main point')
    out.sort(key=lambda r: (['ERROR', 'WARN', 'REVIEW', 'OK'].index(r[0]), r[1]))
    return out
