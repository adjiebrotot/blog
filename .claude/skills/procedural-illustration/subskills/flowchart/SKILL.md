# Flowcharts, cycles and processes

`Flow`, `Node`, `Edge` (`scripts/pi/flow.py`). Replaces Mermaid flowcharts. Gallery: `flow`.

```python
Flow(nodes, edges, cycle=None, node_w=None, row_gap=None, centre=None)
Node(id, text, col=0, row=0, role='node', w=None, sub=None, icon=None, corners='rrrr', near=None, gap=None)
Edge(a, b, text=None, dashed=False, role=None, sides=None, animate=False)
```

## Layout

- **Grid** (wide layout): `col`, `row` (fractions allowed, e.g. `col=0.5` to centre under two
  columns). Edges route at right angles through the gaps: down from the bottom to the top of
  the next row, across between neighbours. `sides='rl'` forces the ports (t, b, l, r).
- **Cycle**: `cycle={'ids': [...], 'cx': 0.5, 'r': 130}` puts those nodes round a circle
  clockwise from the top, and every edge from one to the next is an arc. `centre=` writes a
  short label in the middle (what the loop is).
- **Hanging nodes**: `near=('b', 'l')` puts an entry or a branch beside another node
  (l, r, t, b, or a corner tl, tr, bl, br). Use it for the entry into a cycle and for a
  failure path out of it.
- **Narrow layout** (automatic): one column in the order the nodes are listed. An edge to the
  next node is a short arrow; one that skips ahead runs down the right lane; one back up (a
  loop) runs up the left lane. List the nodes in reading order, branch last.

## Roles

| Role | Look | Use |
| --- | --- | --- |
| `start` | filled blue, light text | the entry point, the given |
| `key` | blue tint, blue border, semi-bold | the step the post is about |
| `node` | quiet box | the other steps |
| `hl` | red tint, red border | an outcome the post warns about |
| `warn` | red tint, dashed red border | a possible failure, a risk |
| `muted` | grey tint, no border | an aside |
| `plain` | no box | a free label |

Edges: solid for what happens by rule, `dashed=True` for what may happen, `role='hl'` for the
failure path, `text` on the edge for the condition ("no jobs, no reason to move").
`animate=True` moves dashes along the edge (a flow of money, power, goods); readers who prefer
reduced motion see it still.

## Writing the boxes

- One idea per box, 3 to 9 words; a verb when it is an action ("Government sells land-use
  rights"). Longer detail goes to `sub=` (smaller, muted) or the post.
- Boxes of three lines or fewer are centred; longer is left-aligned (MM rule); better to cut.
- Five to eight nodes. More: split into two figures or group steps.
- A real example in a box (a city, a project) is the evidence for the loop: put it in the
  failure box or as `sub`, not as a box of its own.
