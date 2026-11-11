---
name: brotools-embed
description: Embed a chart (or a whole tool) from Adjie Brotools (tool.adjiebrotots.com) in a post, without the tool repo and without asking Adjie for the code. Opens the tool on the LIVE site on the post's scenario, writes the exact "Share → Embed as HTML" code, every figure the chart draws, the tool's own results text, and screenshots of the embed as the blog shows it (light and dark, desktop and phone), so the post can be written from the numbers the reader will see. Use when a plan or a post has a tool embed, when Adjie asks to embed, show or link a tool or chart in a post, or when a post needs figures that one of the tools computes.
---

# Adjie Brotools embeds

An embed is the tool's chart written down as data: the code from **Share → Embed as HTML**
carries the scenario and every figure inside its link, and the tool site's embed viewer draws
it. Nothing on the blog computes anything. This skill makes that code itself, from the live
site, and shows you the result first, so the prose, tables and claims around the chart are
written from what the reader will actually see.

```
scenario (#load link)  →  charts  →  embed  →  read data.md, tool.txt, look at the PNGs
                       →  write the section from them  →  paste embed.html  →  build, shot
```

Everything runs against `https://tool.adjiebrotots.com/` with the container's Chromium. The
tool repo is not needed. The output goes to `_build/brotools/<name>/` (ignored by git and by
Jekyll): it is working material, not a post asset.

## 1. Pick the tool and the page

- The tools and their AI pages: `curl -s https://tool.adjiebrotots.com/llms.txt`.
- **Language.** The embed's words (title, legend, axis, view buttons, credit line) come from
  the page it is made on. Rent vs Own and Pisah vs Gabung have Indonesian pages
  (`/rentvsownhouse/id/`, `/pisahvsgabung/id/`): an Indonesian post embeds from those. Every
  other tool is English only; an Indonesian post may still embed it, but say so in the plan
  so Adjie can decide (an English chart in an Indonesian post).
- A post in two languages gets **one embed per language**, from the same scenario, so the
  figures match and only the words differ.

## 2. Build the scenario as a `#load` link

The scenario is the same link an AI assistant writes for the tool:

```
https://tool.adjiebrotots.com/<tool>/#load&v=1&qs=<quick start>&<key>=<value>&...
```

Read the tool's live reference for its keys, units, ranges and Quick Starts:

```sh
curl -s https://tool.adjiebrotots.com/<tool>/ai/skill/references/<tool>.md      # keys, example
curl -s https://tool.adjiebrotots.com/<tool>/ai/skill/references/params.json    # ranges, defaults
```

(`…/ai/skill/SKILL.md` itself is served as `SKILL.html`; the references are plain text.)

- Every input comes from the plan's evidence rows (a sourced figure, with its date) or is a
  stated assumption. The post names the inputs that matter, so the reader can see what the
  chart assumes. A tool's output is model output: it is evidence of what the model computes
  under those inputs, never of what will happen (`adjie-writing-style/references/editorial-safeguards.md`).
- Start from the nearest Quick Start (`qs=`) and send only what differs.
- `why.<key>` and `note` are shown on the tool page only, not in the embed: leave them out.
- A tool with no AI reference (no `/ai/` page) can still be embedded on its defaults. For any
  other scenario there, ask Adjie for the code from his own Share menu.

## 3. See what the page offers

```sh
node .claude/skills/brotools-embed/scripts/brotools.mjs charts '<#load link>'
```

It prints the **inputs table** (each key the link set, as the tool read it, plus unknown keys,
clamped values and errors) and the **charts** on the page: each chart's key, title and the
views its card offers (a metric select, a row of buttons). Fix the link until every key is
applied and nothing is unknown or clamped, unless clamping is what you meant.

Quote the link in single quotes in the shell: it contains `&`.

## 4. Make the embed

```sh
node .claude/skills/brotools-embed/scripts/brotools.mjs embed '<#load link>' \
     --chart chartCanvas --view "Net Benefit vs Cash" --name <post-slug>-<what>
```

| Option | Use |
| --- | --- |
| `--chart KEY` | the chart from `charts` (default: the first chart shown) |
| `--view TEXT` | set a view first (a select option or a button with these words); repeat for several |
| `--include VALUE` | tick an "Include:" choice of the embed dialog (a tool that offers one) |
| `--name NAME` | folder under `_build/brotools/` |
| `--wait SECONDS` | longest wait for the tool to finish (default 45; an optimiser may need more) |
| `--light` | take it while the tool is light (default dark; the blog switches it either way) |

What it writes in `_build/brotools/<name>/`:

| File | What it is for |
| --- | --- |
| `embed.html` | the code to paste: iframe, credit line, sizing script. Exactly what Share → Embed as HTML gives |
| `data.md` | every view of the chart as a table, marking the one the embed opens on (long series sampled) |
| `data.json` | the same, every point, for exact figures |
| `tool.txt` | the tool page's visible text: its verdict, summary cards and notes for this scenario |
| `inputs.md` | the inputs table from step 3 |
| `link.txt` | the link back: the whole tool, opened on this scenario and view ("try your own numbers") |
| `tool.png` | the chart's card on the tool page |
| `embed-{light,dark}-{760,390}.png` | the embed in a post-like column, desktop and phone |

**Look at the PNGs** (Read them) before you use the embed: the right view, a readable legend,
nothing cut off at 390px, the line or bar the section talks about clearly visible. If it is
wrong, change the view or the scenario and run it again.

## 5. Write from it

- **Figures in the text are the tool's figures.** Take them from `data.md`/`data.json` and
  `tool.txt`, rounded the way the tool shows them (`tool.txt` has its own formatting, such as
  `−$4.5k`). Never recompute a figure by hand next to a chart that shows another one.
- Say what the chart shows in words in the same section: the answer first, then the one or two
  points on the chart worth reading (the crossover year, the end value, the gap). A short
  table of the key figures under the embed, as in `en/_posts/2026-10-31-is-debt-bad.md`,
  works when the reader needs exact numbers.
- The embed sits in the section that talks about it, and only that section points at it
  ("the chart below"), per `check-references.py`.
- The views the reader can switch to are in `data.md` too: mention one only if the section
  uses it, and say which button shows it.
- Name the scenario's key inputs and their sources in the text or the caption, so the chart is
  not read as a forecast.
- For a two-language post, put `data.md` and `tool.txt` (and the inputs) in the
  language-neutral brief, so both writer agents work from the same figures
  (`ai-assisted-blog-post`, Step 3). The orchestrator makes the embeds; the writers paste the
  `embed.html` of their language.

## 6. Paste it

Paste `embed.html` as it is, on its own lines, with a blank line before and after. Never edit
the `src` (the scenario is compressed inside it) and never shorten it: a long code is the
chart's data. If the code ever contains `{{` or `{%`, wrap it in `{% raw %}` … `{% endraw %}`.
The blog adds the theme to the link at run time (`assets/js/blog.js`), so the same code
follows the reader's light or dark mode.

A whole tool page (not one chart) uses the include instead, as `README.md` shows:
`{% include tool-embed.html src="https://tool.adjiebrotots.com/<tool>/" title="…" height="760" caption="…" %}`.
For a tool that shares itself whole (the Random Picker), `embed` already writes that kind of
code (an iframe of the tool page): either works.

## 7. Check it in the built post

```sh
LANG=C.UTF-8 bundle exec jekyll build
(cd _site && python3 -m http.server 4000 >/dev/null 2>&1 &)
node .claude/skills/brotools-embed/scripts/brotools.mjs shot http://localhost:4000/en/<slug>/ --width 390 --theme dark --out _build/brotools/<name>/post-390-dark.png
```

`shot` saves a full-page picture and says whether the page scrolls sideways (it must not at
390px). Look at the embed in the post in both themes.

## Things to know

- **An embed is frozen.** It draws the data it was made with, so a later change to the tool's
  model never changes a published chart, and the figures in the post stay true to it. To
  update the numbers, make a new embed and update the text with it.
- **A plan's embed row** (`ai-assisted-blog-post`, section 4 of the plan) names the tool,
  the chart, the view and the `#load` link, and the plan can show `embed-light-760.png` as a
  preview. Adjie may still send his own code; use his if he does.
- **Charts that are not on the page at load** (inside a popup, or drawn only after Run or
  Generate) are not listed by `charts`. Embed the whole tool, or ask Adjie.
- **Market-data tools** (DCA Scenario Explorer) fetch prices when they open; the embed carries
  the prices of that day. Heavy optimisers may need `--wait 120`.
- The page's errors, if any, are printed at the end. A page error or a `dialog:` line means
  the scenario did not run cleanly: fix it before using the figures.
