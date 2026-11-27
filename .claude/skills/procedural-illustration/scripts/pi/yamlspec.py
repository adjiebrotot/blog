"""YAML specs: a standard chart without writing Python (references/yaml-specs.md).

    name: gsl-pi-real-wages
    title: {en: ..., id: ...}
    subtitle: {en: ..., id: ...}
    source: {en: ..., id: ...}
    alt: {en: ..., id: ...}
    review: {type: ..., audience: ..., transparency: ..., standalone: ..., outliers: ..., axis: ...}
    parts:
      - Line:                      # any component class name, its arguments as keys
          x: [2019, 2020, 2021]
          series: [{name: {en: Indonesia, id: Indonesia}, values: [100, 93.1, 91.0], role: hl}]

A tuple argument (a Dumbbell's names, a Map's bounds) is written as a list. Flow nodes and
edges are written as dicts: {Node: {id: a, text: ...}} / {Edge: {a: a, b: b}}.
"""
import yaml

from . import charts2d, infographic, flow, geo, iso3d
from .figure import Figure

CLASSES = {}
for mod in (charts2d, infographic, flow, geo, iso3d):
    for k in dir(mod):
        v = getattr(mod, k)
        if isinstance(v, type) and k[0].isupper():
            CLASSES[k] = v


def _build(v):
    if isinstance(v, dict) and len(v) == 1:
        (k, args), = v.items()
        if k in ('Node', 'Edge'):
            return CLASSES[k](**{a: _build(b) for a, b in args.items()})
    if isinstance(v, list):
        return [_build(x) for x in v]
    if isinstance(v, dict):
        return {k: _build(x) for k, x in v.items()}
    return v


def load_yaml(path):
    docs = list(yaml.safe_load_all(open(path, encoding='utf-8')))
    figs = []
    for d in docs:
        parts = d.pop('parts')
        fig = Figure(**d)
        for p in parts:
            (cls, args), = p.items()
            args = {k: _build(v) for k, v in (args or {}).items()}
            for k in ('names', 'bounds', 'roles', 'margin'):
                if isinstance(args.get(k), list):
                    args[k] = tuple(args[k])
            fig.add(CLASSES[cls](**args))
        figs.append(fig)
    return figs
