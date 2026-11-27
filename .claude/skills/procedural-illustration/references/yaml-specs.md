# YAML specs

A standard chart needs no Python. Save `_illustrations/<name>.yml` and render it like a `.py`
spec. Top-level keys are the `Figure` arguments; `parts` lists components by class name with
their arguments. Several figures can share a file, separated by `---`.

```yaml
name: gsl-pi-soe-liabilities
title: {en: State builders tripled their debt in three years, id: "..."}
subtitle: {en: "Total liabilities of WSKT, WIKA, ADHI and PTPP, Rp trillion, end of year", id: "..."}
source: {en: Company annual reports (consolidated balance sheets), id: "..."}
alt: {en: "Column chart ...", id: "..."}
review:
  type: columns, one stock per year
  audience: general readers; values written on the columns
  transparency: every year 2015-2024, no gaps
  standalone: the title gives the finding, the annotation the size
  outliers: the 2018 jump is labelled
parts:
  - Bars:
      orient: v
      fmt: {dp: 1}
      unit: {en: Rp trillion, id: Rp triliun}
      items:
        - {label: "2015", value: 60.4, role: a}
        - {label: "2018", value: 197.5, role: hl}
      annotate:
        - {at: 1, text: {en: 3.3 times 2015, id: "..."}}
```

Tuples (a `Dumbbell`'s `names`, a `Map`'s `bounds`) are lists. Flowchart nodes and edges:
`nodes: [{Node: {id: a, text: {...}, role: start}}]`, `edges: [{Edge: {a: a, b: b}}]`.
Anything needing a function (a custom `x_fmt`, `@fig.draw`) needs a `.py` spec.
