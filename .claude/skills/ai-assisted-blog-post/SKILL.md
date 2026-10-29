---
name: ai-assisted-blog-post
description: AI-assisted blog post. Turn Adjie's concept or points into a post he approves before any of it is written. First a draft plan (title, description, outline, opening narrative, planned data, embeds, diagrams and equations, and a list of decisions for him), then one round of revision, then the full post, written per language by separate writer agents from a shared brief, with the Indonesian checked by a separate evaluator agent. Use when Adjie sends a topic, an idea, rough notes or bullet points and wants a post on this blog, or asks for an "AI-assisted blog post".
---

# AI-assisted blog post

The AI does the legwork, Adjie makes the calls. You never write the post straight from a
concept. You propose a **draft plan**, Adjie revises it and answers your questions, and
only then do you write.

```
concept / points  →  Draft plan (v1)  →  Adjie: revision + answers  →  content brief
                                              │                              │
                                              │              ┌───────────────┴───────────────┐
                                              │        EN writer agent                ID writer agent
                                              │              │                               │
                                              │              │                  ID evaluator agent (loop
                                              │              │                  until LULUS)
                                              │              └───────────────┬───────────────┘
                                              │                  consistency check, build, deliver
                                              └─ "show me another draft first" → Draft plan (v2) → …
```

## Rules for the whole flow

- **No post prose before approval.** The draft plan holds bullet points, not paragraphs.
  The one exception is the opening narrative (below), because the voice is easier to judge
  on a real paragraph than on a description of one.
- **One revision by default.** Adjie's first reply to a draft plan (his revision and his
  answers) is the go-ahead. Apply it and write the full post. Do not send a second plan or
  ask "shall I go ahead?".
- **Another draft only on request.** Send a new plan (v2, v3...) instead of writing only
  when his reply asks for it in so many words ("show me the draft again", "send another
  draft first", "kirim draft-nya lagi"). Each new plan restarts the same rule: his reply
  to it is the go-ahead, unless that reply asks for yet another draft.
- **A silent answer takes the default.** Every decision in the plan has a recommended
  option. If he skips one, use it and say so in one line when you deliver the post.
- **A revision that conflicts with the rules** (a changed slug on a live post, an
  em-dash in UI text, a URL rule in `CLAUDE.md`) is the one case where you stop and
  ask before writing. Name the conflict and offer the closest fix that keeps the rule.
- **Never invent data.** Every number in the plan has a named source you have actually
  checked, or it is marked **to verify** with where you expect to find it. Nothing marked
  to verify reaches the post unverified: check it while writing, or drop it and say so.
- **Each language is written by its own writer, from a shared brief.** Never write the
  Indonesian next to the English, and never translate one into the other. With both
  languages in one context, the English sentences pull the Indonesian into their shape
  (calques, sentence-initial conjunctions, personified cities, note-style fragments) and
  the context bloats. The posts share the message, the verdict and the verified data;
  they don't share sentences, and they may use different examples (the English compares
  Perth and Melbourne, the Indonesian Jakarta and Bali) if each carries the same point.
- **Indonesian passes the evaluator before Adjie sees it.** Every Indonesian text, the
  plan's opening narrative included, goes through `bahasa-indonesia`'s
  `scripts/cek.py` and its evaluator (`references/evaluator.md`), run by an agent that has
  not seen the English.
- Read the concept critically before planning. If the argument has a weak premise, a
  missing counterargument or a claim the data may not support, say so at the top of the
  plan. Adjie wants the weakness first, not applause.

## Step 1: Read the concept

Before writing the plan:

1. Read `README.md` (front matter, categories, embeds, KaTeX, Mermaid, extras) and the
   `adjie-writing-style` skill. For Indonesian, also the `bahasa-indonesia` skill
   (mandatory for any Indonesian, the plan's opening narrative included).
2. Look at `en/_posts/` and `id/_posts/` for related posts to link to, and for a
   `translation:` key if the topic already exists in the other language.
3. Work out the post's shape from `adjie-writing-style` (argument or explainer, personal
   story, technical notes) and its dial (humour, data, personal stake).
4. Check the data you plan to cite, enough to know the source exists and roughly what it
   says. Leave the deep reading for Step 3.

If the concept leaves out something only Adjie can know (his own numbers, his own story,
which language), put it in the decisions section. Don't guess, and don't stop to ask
before the plan either: the plan is where questions go.

## Step 2: Send the draft plan

Send it in the chat, in Markdown, using this template. Write it in the language Adjie
wrote to you in. Titles, descriptions and the opening narrative are in the **post's**
language (both, if the post is in both). The outline is the shared skeleton: its headings
say what each section asks and answers, and the writers word them in their own language.

For a post in Indonesian (alone or with English), the Indonesian title, description and
opening narrative are not written by the context that writes the English. Spawn the
Indonesian writer agent (Step 3) with the concept and a short note of what each piece must
do, have it write them natively, and run the evaluator on them before they go into the
plan. If you cannot spawn agents, write the Indonesian pieces first, before any English
prose, and run the evaluator yourself.

```markdown
# Draft plan v1: <working title>

**Read this first:** <the one or two weakest points of the concept or argument, and
what the plan does about them. "None I can see" is allowed, but check hard first.>

## 1. Title and description
- **Language(s):** EN / ID / both (paired with `translation: <key>`)
- **Title:** "<title>"  (alt: "<second option>")
- **Description:** "<one or two plain sentences that answer the post's question>"
- **Slug:** `<slug>` → https://blog.adjiebrotots.com/<lang>/<slug>/
- **Tags:** [<finance | engineering | personal | others>]
- **Shape:** <argument / personal story / technical notes>, dial: humour <low/med/high>,
  data <...>, personal stake <...>

## 2. Outline
- **In short (TL;DR):** <the answer in one sentence>
- ## <Question-style heading>
  - <point>
  - <point>
- ## <Heading>
  - <point>
  - ### <Subheading>
    - <point>
- ## <Ending heading: back to the core question>
  - <verdict in one line, the small action>

## 3. Opening narrative
> <One or two short paragraphs, written for real in Adjie's voice: the hook, the
> character or question that carries the post. Like "Who is right, the buyer or the
> renter?" with Robert and Geoff in the Rent vs Own post. One per language, each written
> natively by its own writer; the Indonesian one has passed the evaluator.>

**Per-language examples:** <where the two posts use different characters, cities or
examples, and why each fits its readers. "Same in both" is fine.>

## 4. Features
| # | Type | What it shows | Where | Source / status |
|---|------|---------------|-------|-----------------|
| D1 | Data | <figure, with date> (EN / ID / both) | <section> | <publisher, link> / verified or **to verify** |
| T1 | Tool embed | <tool, chart, inputs> | <section> | <tool URL> |
| S1 | Screenshot | <what the image shows> | <section> | <how it will be made> |
| I1 | Illustration | <who does what, with which object> | <section> | generated with `wikihow-illustration` |
| M1 | Mermaid | <diagram type: flowchart, xychart-beta, pie...> showing <...> | <section> | <data behind it> |
| K1 | KaTeX | <the equation, in words> | <section> | <every symbol it defines> |
| X1 | Extra | table / alert / footnotes / TOC | <section> | |

## 5. For your judgement
Answer by number, e.g. "1b, 2 yes, 3: <your own words>". Anything left out takes the
recommended option.

1. **<Decision>?**
   a. <option> (recommended: <why, one line>)
   b. <option>
2. **<Yes/no decision>?** Recommended: yes, because <...>.
3. **<Something only you know>?** (no default: <what I'll do if you skip it>)

## Your reply
Send your revisions and answers in one message, and I will write the full post. If you
want to see a revised plan first, say so ("show me the draft again").
```

### What goes in each part

**Read this first.** The point of this section is to be useful, not polite: an
unsupported premise, a one-sided argument, a number that may be stale, a topic an existing
post already covers.

**Title and description.** Follow `README.md`: the description answers the question
and is what search engines and AI answers quote. The slug is permanent once it is live,
so choose it here, in the post's language, short and with the words people search for.

**Outline.** Headings are the real `##` / `###` headings you intend to use, mostly
questions. Under each, 2 to 5 short bullets: the claim, the number, the example. Mark
where each feature from section 4 sits (e.g. "→ T1").

**Opening narrative.** The only finished prose in the plan. It follows
`adjie-writing-style` (a question, an invitation to imagine or a claim to challenge; a
named everyday character if the shape uses one) and the blog rules (no em-dashes,
saya-kamu in Indonesian). For a post in both languages, each one is written natively by
its own writer, with different characters or examples if that suits each readership.

**Features.** Only what earns its place. A post needs no Mermaid or KaTeX just because
the blog can draw them. Per type:

- **Data:** the figure, its date and its publisher. Prefer the primary source (statistics
  office, central bank, the company's own report) over a news summary.
- **Tool embed:** which Adjie Brotools tool (https://tool.adjiebrotots.com/), which chart
  and which inputs. A single chart is pasted from the tool's **Share → Embed as HTML**,
  and that code encodes the inputs, so ask Adjie for it in section 5 unless he has already
  sent it. A whole tool page uses `{% include tool-embed.html ... %}` (see `README.md`).
- **Screenshot:** what it shows, its alt text, and whether Adjie supplies it or you
  capture it (the container has Playwright and Chromium). It goes in `assets/img/`.
  Prefer an embed when the reader would want to change the numbers.
- **Illustration:** a wikiHow-style picture of one person doing one action, generated with the
  `wikihow-illustration` skill. Give the brief (action, who, framing) and its alt text.
  Use it where the reader has to imagine a person doing something, not where a chart or a
  screenshot shows the real thing.
- **Mermaid:** the diagram type and the data or steps it draws. Charts use
  `xychart-beta` or `pie` and need real numbers from a D row.
- **KaTeX:** the equation in words or LaTeX, and the symbols it defines. A simple sum for
  emphasis stays in the sentence as text (see `adjie-writing-style`).
- **Extras:** comparison tables, `> [!NOTE]` alerts, footnotes for sources, `* TOC`.

**For your judgement.** Real choices that change the post, each with options and a
recommendation. Typical ones:

- one language or both; if both, which goes first
- which of two angles or titles
- whether to include his personal numbers or story (and what they are)
- a feature that could go either way (a diagram vs a table, an embed vs a screenshot)
- how sharp to be on a contested point
- length: a focused post or the full guide
- anything you'd otherwise have to assume about him

Keep it to the decisions that matter, usually 3 to 7. Don't ask what the README or the
style skill already decides.

## Step 3: Write the post

After Adjie's reply (and no request for another draft), you are the editor: you prepare
the brief, the writers write, the evaluator judges, and you put it together.

### 3a. Settle the facts

1. Apply every revision and answer. Where a revision is unclear, take the reading that
   best fits his words and note it in your delivery message.
2. Verify every **to verify** figure. If one does not hold, use the correct figure or
   drop the claim, and tell him which.

### 3b. Write the content brief

Save it as a file in your scratchpad (`brief.md`). It is language-neutral: points, not
sentences, so no writer inherits another language's phrasing. Write the points as short
notes in the language you think in, never as draft prose.

- **Message:** the post's question, its answer in one line, the verdict and the small
  action at the end. These are identical in every language.
- **Shape and dial** from the plan, and the stance (where Adjie concedes, where he is
  sharp).
- **Sections,** in order: what each one asks and answers, its points, which data and
  features go in it. Heading intent, not heading wording.
- **Data table:** every figure with its date, publisher and URL, marked shared or
  language-specific. A writer may use only figures from this table.
- **Per-language choices:** characters, cities, examples and jokes for each language, as
  approved in the plan. Where the plan left them shared, a writer may still choose a
  closer example for its readers, if it sources every new number and says so.
- **Fixed pieces:** front matter that must match (date, tags, `translation:` key, image),
  slugs, embed codes, screenshots, illustrations, links to related posts, and each
  language's approved opening narrative.

### 3c. Two writers, in parallel

Spawn one writer agent per language in the same turn (Agent tool, in the background).
Each gets only the brief, its own slug and file path, and its own skills:

- **English writer:** `README.md`, `adjie-writing-style`; writes `en/_posts/<file>`.
- **Indonesian writer:** loads `bahasa-indonesia` first, then `README.md` and
  `adjie-writing-style`; writes `id/_posts/<file>` natively, as an Indonesian columnist
  writing for Indonesian readers, and runs `scripts/cek.py` until it shows no ERROR. It is
  told not to open the English file and not to translate from the brief's wording.

Each writer runs `adjie-writing-style`'s "Check a draft" list, keeps its approved opening
narrative with only the edits Adjie asked for, and puts every source in a footnote.

If you cannot spawn agents, write the Indonesian post first, from the brief alone, run
3d on it, and only then write the English.

### 3d. Evaluate the Indonesian

Spawn a fresh evaluator agent with the prompt in `bahasa-indonesia`'s
`references/evaluator.md`. It must not be the writer and must not read the English. Send
its findings to the Indonesian writer (SendMessage) or apply them yourself, run
`scripts/cek.py` again, and send the changed paragraphs back to the evaluator. Repeat until
the verdict is LULUS. Keep the last report for the delivery message.

### 3e. Put it together

1. **Consistency, not alignment.** Compare the two posts on the message, the verdict, the
   shared numbers, the sources and the fixed pieces. Never compare them sentence by
   sentence, and never "fix" one to mirror the other's wording or examples.
2. Make sure both files are saved as `<lang>/_posts/YYYY-MM-DD-<slug>.md`, with the
   `translation:` key on both if the post is in two languages.
3. Run the checks in `CLAUDE.md` (`LANG=C.UTF-8 bundle exec jekyll build`, one `<h1>`,
   valid JSON-LD, feeds and sitemap parse, `hreflang` pairs, no sideways scroll at 390px).
4. Deliver: the file path(s), the defaults you applied for skipped answers, any figure you
   changed or dropped, where the two languages use different examples, the evaluator's
   verdict and any finding you chose not to apply, and anything still waiting on him (an
   embed code, a screenshot). Commit and push as the session's git instructions say.

Changes he asks for after this are ordinary edits to the post, not a new round of the
flow. An edit to the Indonesian still runs `scripts/cek.py` and the evaluator on the
changed paragraphs before it is pushed.
