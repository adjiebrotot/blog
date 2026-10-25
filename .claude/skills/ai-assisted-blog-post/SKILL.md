---
name: ai-assisted-blog-post
description: AI-assisted blog post. Turn Adjie's concept or points into a post he approves before any of it is written. First a draft plan (title, description, outline, opening narrative, planned data, embeds, diagrams and equations, and a list of decisions for him), then one round of revision, then the full post. Use when Adjie sends a topic, an idea, rough notes or bullet points and wants a post on this blog, or asks for an "AI-assisted blog post".
---

# AI-assisted blog post

The AI does the legwork, Adjie makes the calls. You never write the post straight from a
concept. You propose a **draft plan**, Adjie revises it and answers your questions, and
only then do you write.

```
concept / points  →  Draft plan (v1)  →  Adjie: revision + answers  →  full post
                                              │
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
- Read the concept critically before planning. If the argument has a weak premise, a
  missing counterargument or a claim the data may not support, say so at the top of the
  plan. Adjie wants the weakness first, not applause.

## Step 1: Read the concept

Before writing the plan:

1. Read `README.md` (front matter, categories, embeds, KaTeX, Mermaid, extras) and the
   `adjie-writing-style` skill. For Indonesian, also the `bahasa-indonesia` skill and the
   Indonesian rules in `adjie-writing-style`.
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
wrote to you in. Titles, descriptions, headings and the opening narrative are in the
**post's** language (both, if the post is in both).

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
> renter?" with Robert and Geoff in the Rent vs Own post.>

## 4. Features
| # | Type | What it shows | Where | Source / status |
|---|------|---------------|-------|-----------------|
| D1 | Data | <figure, with date> | <section> | <publisher, link> / verified or **to verify** |
| T1 | Tool embed | <tool, chart, inputs> | <section> | <tool URL> |
| S1 | Screenshot | <what the image shows> | <section> | <how it will be made> |
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
saya-kamu in Indonesian). For a post in both languages, write each one natively, with
different characters if that suits each readership.

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

After Adjie's reply (and no request for another draft):

1. Apply every revision and answer. Where a revision is unclear, take the reading that
   best fits his words and note it in your delivery message.
2. Verify every **to verify** figure. If one does not hold, use the correct figure or
   drop the claim, and tell him which.
3. Write the post following `README.md`, `adjie-writing-style` (run its "Check a draft"
   list) and, for Indonesian, `bahasa-indonesia`. Keep the opening narrative he approved,
   with only the edits he asked for. Every source goes in a footnote.
4. Save it as `<lang>/_posts/YYYY-MM-DD-<slug>.md`, with the `translation:` key on both
   files if the post is in two languages.
5. Run the checks in `CLAUDE.md` (`LANG=C.UTF-8 bundle exec jekyll build`, one `<h1>`,
   valid JSON-LD, feeds and sitemap parse, `hreflang` pairs, no sideways scroll at 390px).
6. Deliver: the file path(s), the defaults you applied for skipped answers, any figure you
   changed or dropped, and anything still waiting on him (an embed code, a screenshot).
   Commit and push as the session's git instructions say.

Changes he asks for after this are ordinary edits to the post, not a new round of the
flow.
