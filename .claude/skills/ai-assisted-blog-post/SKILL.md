---
name: ai-assisted-blog-post
description: AI-assisted blog post. Turn Adjie's concept or points into a post he approves before any of it is written. First a draft plan (title, description, outline, opening narrative, planned data, embeds, diagrams and equations, and a list of decisions for him), then explicit primary-intention approval and selective tone choices, then the full post, written per language by separate writer agents from a shared brief, with explicit wording preferences saved, a fresh substantive editor for each language, the Indonesian checked by a separate evaluator agent and every post checked by a reference-checker agent for pointers to other sections and by an SEO/GEO check (search words, title and description length, the answer up front, sources, links). Use when Adjie sends a topic, an idea, rough notes or bullet points and wants a post on this blog, or asks for an "AI-assisted blog post".
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
                                              │      reference-checker agent per post (loop until PASS)
                                              │                  substantive review, consistency check, build, deliver
                                              └─ "show me another draft first" → Draft plan (v2) → …
```

## Rules for the whole flow

- Read `.claude/skills/adjie-writing-style/references/editorial-safeguards.md` and
  `.claude/skills/adjie-writing-style/references/voice-preferences.md` first. They govern evidence,
  personal provenance, material conditions, purposeful repetition and explicit approvals.
- **Ask the primary intention during planning.** State the proposed primary reader
  outcome and ask Adjie to confirm or choose: explanation, decision support, practical
  tutorial, personal reflection, opinion/persuasion, or his own intention. A reply that
  leaves this unanswered is not enough to finalise a new post: ask one focused follow-up.
  Do not silently default this decision. Identify the secondary aims and material to omit,
  split into another article or put in tool documentation.
- **Offer targeted tone choices.** For genuinely doubtful passages or Indonesian word
  choices, add a short alternatives section to the plan. Keep meaning and evidence fixed;
  explain the tone trade-off and allow his own wording. No arbitrary quota. Explicit
  choices are persisted in the preference references, not merely noted in chat. Silence
  is not approval and must never become learned evidence.
- **Fresh substantive editorial review in every language.** Follow Step 3g before final
  assembly. Evidence and natural reading matter more than a clean script run.

- **No full post before approval.** The plan uses bullets except for the opening narrative
  and short, targeted tone/word-choice alternatives. These samples let Adjie judge actual
  wording; they are not permission to write the whole post before approval.
- **One revision by default.** Adjie's first reply to a draft plan (his revision and his
  answers) is the go-ahead once the primary intention is explicit and any required factual
  or personal confirmations are settled or the affected material is omitted. Apply it and
  write. Do not request redundant approval; ask only a focused unresolved question.
- **Another draft only on request.** Send a new plan (v2, v3...) instead of writing only
  when his reply asks for it in so many words ("show me the draft again", "send another
  draft first", "kirim draft-nya lagi"). Each new plan restarts the same rule: his reply
  to it is the go-ahead once required decisions are settled, unless that reply asks for another draft.
- **Defaults have limits.** Optional production decisions may use the recommended default
  when skipped; disclose it at delivery. Primary intention has no silent default. Unknown
  personal claims are omitted if unconfirmed. Acceptable existing wording may remain when
  a preference option is skipped, but record it as unapproved, not a learned choice.
  Unresolved meaning, accuracy or necessary voice conflicts require a focused question.
- **A revision that conflicts with the rules** (a changed slug on a live post, an
  em-dash in UI text, a URL rule in `CLAUDE.md`) needs a focused clarification,
  as do unresolved primary intention, necessary evidence or personal confirmations. Name the conflict and offer the closest fix that keeps the rule.
- **Never invent data or autobiography.** Each factual number has a checked source or is
  marked to verify. Scenario assumptions are explicitly assumptions; model outputs carry
  reproducible inputs and conditions. Unknown memories, dialogue, motives and feelings are
  marked for author confirmation, never guessed. Unverified facts and unconfirmed personal
  material do not reach publication. Follow the safeguards rather than relabelling them.
- **Each language is written by its own writer, from a shared brief.** Never write the
  Indonesian next to the English, and never translate one into the other. With both
  languages in one context, the English sentences pull the Indonesian into their shape
  (calques, sentence-initial conjunctions, personified cities, note-style fragments) and
  the context bloats. The posts share the message, the verdict and the verified data;
  they don't share sentences, and they may use different examples (the English compares
  Perth and Melbourne, the Indonesian Jakarta and Bali) if each carries the same point.
- **Every section stands on its own.** A sentence points only at a figure, table, chart,
  screenshot or example in its own section (`adjie-writing-style`, "Point only at what is
  in the same section"). Plan each feature into the section that talks about it, and never
  write "see below", "as I showed" or "details in the X section" across sections. Every
  post passes `adjie-writing-style`'s `scripts/check-references.py` and the
  reference-checker agent (`.claude/agents/reference-checker.md`) before Adjie sees it.
- **Every abbreviation is wrapped in `<abbr>`.** Each post defines every acronym, code and
  short form it uses with a `*[TERM]: meaning` line (`CLAUDE.md`, "Abbreviations"), in its own
  language. The writer adds the line as it writes, the brief lists the abbreviations the
  facts bring (agencies, taxes, units), and the post passes `adjie-writing-style`'s
  `scripts/check-abbr.py` before Adjie sees it. Where the sentence already spells a term out
  beside its abbreviation, that one occurrence is `<span markdown="0">ABBR</span>`, so it
  gets no redundant tooltip.
- **Indonesian passes the evaluator before Adjie sees it.** Every Indonesian text, the
  plan's opening narrative included, goes through `bahasa-indonesia`'s
  `scripts/cek.py` and its evaluator (`references/evaluator.md`), run by an agent that has
  not seen the English.
- **No persona in the opening unless Adjie asks.** The opening narrative does not
  introduce an invented, named character or give a place a voice
  (`adjie-writing-style`, "Open with the case, not a persona"). If a parable would help,
  offer it as a decision in "For your judgement", with "no parable" as the default.
- **Only what the argument needs.** The plan evidence ledger holds the figures that prove a
  point, not every figure the research found. A side example gets its one fact (the city
  has an LRT), not its opening date, length, stations and ridership. The writers and the
  final review apply `adjie-writing-style`'s "Every sentence earns its place".
- **Sonnet does the work, Opus only orchestrates.** Spawn every writer, evaluator,
  reference-checker and research agent with `model: "sonnet"` (the Agent tool's `model`
  parameter). The main context, which plans, talks to Adjie, merges the results and
  makes the final calls, may run on Opus; it does not write the posts itself. Use Opus
  for a sub-agent only when Adjie asks for it.
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
3. Read the explicit preference references. Identify the proposed primary outcome, likely
   scope choices and genuinely doubtful passages to ask about in the plan.
4. Work out the post's shape from `adjie-writing-style` (argument or explainer, personal
   story, technical notes) and its dial (humour, data, personal stake).
5. Check the data you plan to cite, enough to know the source exists and roughly what it
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
opening narrative and any tone-choice samples are not written by the context that
writes the English. Spawn the
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
- **Description:** "<one or two plain sentences that set up the question and make the reader curious, without the answer>"
- **Slug:** `<slug>` → https://blog.adjiebrotots.com/<lang>/<slug>/
- **Tags:** [<finance | engineering | personal | politics | others>]
- **Shape:** <argument / personal story / technical notes>, dial: humour <low/med/high>,
  data <...>, personal stake <...>

## 2. Intention, scope and outline
- **Primary reader outcome to confirm:** <one intention and why>
- **Secondary aims:** <supporting aims, not another full article>
- **Scope boundary:** <what belongs here; what to omit, split or link as documentation>
- **Primary intention question:** <confirm this intention, select another, or give your own;
  no silent default>
- **In short (TL;DR):** <summary intent and material conditions; bullets only at this stage>
- ## <Clear question, statement or label>
  - <point>
  - <point>
- ## <Heading>
  - <point>
  - ### <Subheading>
    - <point>
- ## <Ending heading appropriate to the primary intention>
  - <ending appropriate to the primary intention; action only if useful>

## 3. Opening narrative
> <One or two short paragraphs, written for real in Adjie's voice: the hook, the
> question or the real case that carries the post, stated plainly, with no persona or
> personified place unless Adjie asked for one. One per language, each written natively
> by its own writer; the Indonesian one has passed the evaluator.>

**Per-language examples:** <where the two posts use different characters, cities or
examples, and why each fits its readers. "Same in both" is fine.>

## 4. Features
| # | Type | What it shows | Where | Source / status |
|---|------|---------------|-------|-----------------|
| D1 | Evidence | <claim/figure, class, date, material conditions> (EN / ID / both) | <section> | <checked source or model inputs; assumptions identified; personal confirmation status> |
| T1 | Tool embed | <tool, chart, inputs> | <section> | <tool URL> |
| S1 | Screenshot | <what the image shows> | <section> | <how it will be made> |
| I1 | Illustration | <who does what, with which object> | <section> | generated with `wikihow-illustration` |
| M1 | Mermaid | <diagram type: flowchart, xychart-beta, pie...> showing <...> | <section> | <data behind it> |
| K1 | KaTeX | <the equation, in words> | <section> | <every symbol it defines> |
| X1 | Extra | table / alert / footnotes / TOC | <section> | |

## 5. Tone and wording choices, if genuinely in doubt
| ID | Passage context | Option A | Option B | Trade-off / recommendation |
| --- | --- | --- | --- | --- |
| V1 | <what the short passage does> | <actual short wording> | <same meaning, different tone> | <why the choice matters> |

Choose an option, keep existing acceptable wording, or supply your own. Both options keep
facts and conditions identical. No choices needed is a valid outcome. Indonesian samples
are written and evaluated natively, without reading English prose. Unresolved stylistic
preferences are suggestions, not invented author approvals.

## 6. For your judgement
Answer by decision number and tone ID, e.g. "1: decision support, 2a, V1: my wording ...". Optional production decisions left out take the recommended option. Primary intention
needs an explicit answer; skipped tone choices are not approvals.

1. **Primary intention?** <confirm the proposed outcome, choose another, or give your own>
   No silent default; this needs an explicit answer before the full post.
2. **<Decision>?**
   a. <option> (recommended: <why, one line>)
   b. <option>
3. **<Yes/no decision>?** Recommended: yes, because <...>.
4. **<Something only you know>?** (no default: <what I'll do if you skip it>)

## Your reply
Send your revisions and answers, including your primary intention and any wording choices,
in one message. Once necessary confirmations are settled, I will write the full post. If you
want to see a revised plan first, say so ("show me the draft again").
```

### What goes in each part

**Read this first.** The point of this section is to be useful, not polite: an
unsupported premise, a one-sided argument, a number that may be stale, a topic an existing
post already covers. Flag data and mechanics that change the argument, not clichés, sayings,
figures of speech, rough guesses or Adjie's own experience: readers know those for what they
are, and the post never "corrects" them or carries a disclaimer for them.

**Title and description.** Follow `README.md`: the description is a hook that makes the
reader curious (the question, the surprise) and does not give the answer away; the answer
goes in the post's first paragraph. The slug is permanent once it is live,
so choose it here, in the post's language, short and with the words people search for.
Plan them for search and answer engines too (the "Search and answer engines" rules below):
the title with a 60-character SEO target when natural, keeping the main search words clear, the description at
110 to 160 characters as a metadata target, and 3 to 8 keywords in the post's language.

**Outline.** Headings are proposed `##` / `###` headings: questions, statements or short
labels, whichever best identifies the section and supports the primary intention. Under each, 2 to 5 short bullets: the claim, the number, the example. Mark
where each feature from section 4 sits (e.g. "→ T1"). A feature sits in the section whose
text talks about it. If two sections need the same figure, give the earlier one the number
in words and the later one the figure, or repeat the figure; never plan "see the chart in
section X".

**Opening narrative.** Alongside short tone-choice samples, this is the finished prose
allowed in the plan. It follows
`adjie-writing-style` (a question, an invitation to imagine or a claim to challenge) and
the blog rules (no em-dashes,
saya-kamu in Indonesian). For a post in both languages, each one is written natively by
its own writer, with different characters or examples if that suits each readership.

**Features.** Only what earns its place. A post needs no Mermaid or KaTeX just because
the blog can draw them. Per type:

- **Evidence:** the figure or claim, its evidence class, date, provenance and material
  conditions. Scenario assumptions remain assumptions; personal details require confirmation. Prefer the primary source (statistics
  office, central bank, the company's own report) over a news summary.
- **Tool embed:** which Adjie Brotools tool (https://tool.adjiebrotots.com/), which chart
  and which inputs. A single chart is pasted from the tool's **Share → Embed as HTML**,
  and that code encodes the inputs, so ask Adjie for it in section 6 unless he has already
  sent it. A whole tool page uses `{% include tool-embed.html ... %}` (see `README.md`).
- **Screenshot:** what it shows, its alt text, and whether Adjie supplies it or you
  capture it (the container has Playwright and Chromium). It goes in `assets/img/`.
  Prefer an embed when the reader would want to change the numbers.
- **Illustration:** a wikiHow-style picture of one person doing one action, generated with the
  `wikihow-illustration` skill. Give the brief (action, who, framing) and its alt text.
  Use it where the reader has to imagine a person doing something, not where a chart or a
  screenshot shows the real thing.
- **Mermaid:** the diagram type and the data or steps it draws. Charts use
  `xychart-beta` or `pie` and need real numbers from a checked evidence row, with model inputs and assumptions where applicable.
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

Keep it to the decisions that matter, usually 3 to 7 production decisions plus the required primary-intention question and any genuinely useful tone choices. Don't ask what the README or the
style skill already decides.

### Search and answer engines (SEO and GEO)

The layouts already write the canonical URL, hreflang, Open Graph, JSON-LD, the sitemap,
the feeds and `llms.txt`. What only the post can supply, every plan and every writer
covers. `scripts/check-seo.py` checks mechanical basics, not evidence, intention,
voice or editorial quality:

- **Reader-first search words, in the post's language.** Find the phrase the reader actually types or
  asks ("is debt bad", "pajak suami istri gabung atau pisah"), and put it in the slug, the
  title and description where natural. Use it in the body where it helps the reader; no
  first-sentence or heading quota and no repeated exact-match phrase for its own sake.
- **Title metadata target: 60 characters or fewer.** If the voice needs a longer title,
  keep it and add a concise, accurate `seo_title:`. This is a presentation target, not a
  reason to strip meaning or promise more than the post supports.
- **Description at 110 to 160 characters,** still the hook from `README.md`.
- **Useful summary.** Keep the In short block (`{: .tldr}`), targeting 40 to 90 words.
  Match it to the approved intention and preserve material conditions beside its claim.
  If the target cannot hold an accurate answer, narrow the claim or explain a justified
  exception; never remove a decision-changing condition to satisfy a word count.
- **Clear headings and progression.** Questions, statements and short labels are equally
  acceptable. Answer directly when useful, but no requirement to answer in the first
  sentence under every heading. Let evidence and narrative build in a meaningful sequence.
- **Evidence with provenance.** Factual figures have checked sources and relevant dates.
  Model outputs and assumptions remain distinguishable from facts; personal material is
  supplied or confirmed. Follow the safeguards, not a citation-count or number quota.
- **Links.** At least one link in the text to the most related post on the blog (in the
  same language), and a link to the Adjie Brotools tool the post uses.
- **Images.** A social card (`node _build/og.mjs`), `image_alt`, and alt text, width and
  height on every image.
- **A Markdown copy:** the `md/<lang>-<slug>.txt` stub (`md/README.txt`).
- **3 to 8 `keywords:`** in the post's language: the question, the local terms, the tool's
  name.

## Step 3: Write the post

After Adjie's reply (and no request for another draft), you are the editor: you prepare
the brief, the writers write, the language evaluator and substantive editor judge, and you put it together.

### 3a. Settle the facts

1. Apply explicit decisions. Ask about ambiguity in intention, facts, personal material
   or necessary tone conflicts; optional production defaults may be disclosed. Persist
   approved preferences under Step 3b now, before briefing writers.
2. Verify every to-verify figure and settle evidence classes/material conditions. If
   one does not hold, use the supported figure or drop the claim and tell him. Omit
   unconfirmed personal material rather than inventing it.

### 3b. Persist explicit preferences

Do this immediately after the author reply, before briefing writers, and again for any
later explicit choice. Save exact selections or own wording with date, language, context,
reason if supplied, scope and provenance in
`.claude/skills/adjie-writing-style/references/voice-preferences.md`. For Indonesian also save to
`.claude/skills/bahasa-indonesia/references/word-preferences.md`; add actual corrections to corrections.md
when appropriate. Never promote evaluator choices or silent defaults to author preferences.
A contextual selection is not a global replacement rule. Repeated consistent choices or
explicit instruction can justify a broader preference. If a mandatory style rule conflicts
with an explicit new preference, update its context-specific exception consistently.
Accuracy and material conditions cannot be waived as a tone choice.

### 3c. Write the content brief

Save it as a file in your scratchpad (`brief.md`). It is language-neutral: points, not
sentences, so no writer inherits another language's phrasing. Write the points as short
notes in the language you think in, never as draft prose.

- **Primary intention and scope:** the explicitly approved reader outcome, secondary aims,
  scope boundary, excluded material and chosen ending type.
- **Tone decisions:** exact author selections, passage context and approved scope, plus
  unresolved acceptable wording retained without claiming approval.
- **Personal provenance:** supplied or confirmed material and confirmation evidence; mark
  omissions and never delegate invented autobiography to writers.
- **Message:** the post's question, its answer in one line, the verdict and an ending that fits the
  primary intention; a small action only when useful. These are identical in every language.
- **Shape and dial** from the plan, and the stance (where Adjie concedes, where he is
  sharp).
- **Sections,** in order: what each one asks and answers, its points, which data and
  features go in it. Heading intent, not heading wording. Each section's points are
  self-contained: a number it needs is listed under it, even if another section has it
  too, because a sentence may not send the reader to another section.
- **Evidence ledger:** each claim/figure ID, evidence class, checked source passage/table,
  date, units, population/definition, provenance, material conditions and shared or
  language-specific status. Model outputs include tool inputs, horizon, real/nominal basis
  and uncertainty; assumptions remain labelled. Interpretations identify their supporting
  evidence and limits. A writer uses only settled material from this ledger.
- **Per-language choices:** characters, cities, examples and jokes for each language, as
  approved in the plan. Where the plan left them shared, a writer may still choose a
  closer example for its readers, if it sources every new number and says so.
- **Fixed pieces:** front matter that must match (date, tags, `translation:` key, image),
  slugs, embed codes, screenshots, illustrations, links to related posts, and each
  language's approved opening narrative.

Prepare separate writer views (`brief-en.md`, `brief-id.md`) from the shared ledger.
Each contains only its own approved opening, actual tone alternatives and author wording,
plus the shared factual intents and that language-specific evidence. Do not put finished
English and Indonesian prose together in the file either writer reads. The Indonesian
evaluator receives only Indonesian passages and applicable preferences; never the English
twin, English tone samples or English draft opening.

### 3d. Two writers, in parallel

Spawn one writer agent per language in the same turn (Agent tool, in the background,
`model: "sonnet"`). Each gets only its language-specific brief view, its own slug and file path, and its own
skills:

- **English writer:** `README.md`, `adjie-writing-style`; writes `en/_posts/<file>`.
- **Indonesian writer:** loads `bahasa-indonesia` first, then `README.md` and
  `adjie-writing-style`; writes `id/_posts/<file>` natively, as an Indonesian columnist
  writing for Indonesian readers, and runs `scripts/cek.py` until it shows no ERROR. It is
  told not to open the English file and not to translate from the brief's wording.

Each writer follows the "Search and answer engines" rules in Step 2 and runs
`python3 .claude/skills/ai-assisted-blog-post/scripts/check-seo.py <file>` until it shows
no ERROR (and fixes every WARN it can). Each writer runs `adjie-writing-style`'s "Check a draft" list, keeps its approved opening
narrative unless an evidence or material-condition correction is necessary; flag any such
change to Adjie rather than preserving an inaccurate opening. Put sources in footnotes. Each
writer does the conciseness pass (`adjie-writing-style`, "Every sentence earns its
place") on its finished draft before it reports back: it deletes every sentence the
argument does not use, with its footnote and its now-unused `*[TERM]:` lines. Each
writer is told the same-section rule and runs
`python3 .claude/skills/adjie-writing-style/scripts/check-references.py <file>` until it
shows no ERROR. Each writer defines every abbreviation it uses with a `*[TERM]: meaning`
line in its own language and runs
`python3 .claude/skills/adjie-writing-style/scripts/check-abbr.py <file>` until it shows no
ERROR.

If you cannot spawn agents, write the Indonesian post first, from the brief alone, run
3e on it, and only then write the English.

### 3e. Evaluate the Indonesian

Spawn a fresh evaluator agent (`model: "sonnet"`) with the prompt in `bahasa-indonesia`'s
`references/evaluator.md`. It must not be the writer and must not read the English. Send
its findings to the Indonesian writer (SendMessage) or apply them yourself, run
`scripts/cek.py` again, and send the changed paragraphs back to the evaluator. Repeat until
the verdict is LULUS. Keep the last report for the delivery message.

### 3f. Check the references

For each post, spawn a fresh reference-checker agent (`subagent_type: reference-checker`, which runs on Sonnet,
or a general-purpose agent told to follow `.claude/agents/reference-checker.md`), in
parallel, with only the post's path. Apply every finding: delete the pointer and let the
sentence state its fact. An Indonesian fix is written under `bahasa-indonesia`, runs
`scripts/cek.py`, and goes back to the Indonesian evaluator with its neighbouring
paragraphs. Repeat until the checker says PASS.

### 3g. Substantive review, all languages

Spawn a fresh substantive-editor agent using `.claude/agents/substantive-editor.md`, one per
post, with the full post, approved primary intention and evidence ledger. Give an Indonesian
editor the Indonesian material and ledger without the English twin or English draft prose.
If agents are unavailable, do a separate full editorial pass and disclose that independence
was unavailable. Resolve must-fix findings by research, the smallest supported edit, omission
or a focused author question. Do not weaken evidence to make a punchline work.
Editorial suggestions may be retained or offered as targeted author wording choices.
Changed Indonesian passages return through cek.py and the evaluator; changed facts return
through substantive review. Preserve the final report and any unresolved author decisions.

### 3h. Put it together

1. **Cut what the reader doesn't need.** Read each post once more only for
   "Every sentence earns its place" (`adjie-writing-style`). Too much detail on a side
   example is the mistake Adjie corrects most after delivery ("LRT Palembang mulai
   melayani penumpang pada 1 Agustus 2018 ... 4,63 juta penumpang" in a post about how
   China builds). Delete such sentences in both posts, run `check-abbr.py`, and send an
   Indonesian paragraph you changed back through `cek.py` and its evaluator. Any change
   to evidence, claims or conditions returns to substantive review before final PASS.
2. **Consistency, not alignment.** Compare the two posts on the message, the verdict, the
   shared numbers, the sources and the fixed pieces. Never compare them sentence by
   sentence, and never "fix" one to mirror the other's wording or examples.
3. Make sure both files are saved as `<lang>/_posts/YYYY-MM-DD-<slug>.md`, with the
   `translation:` key on both if the post is in two languages.
4. Add the `md/<lang>-<slug>.txt` stub for each post, then run the checks in `CLAUDE.md`
   (`LANG=C.UTF-8 bundle exec jekyll build`, `scripts/check-seo.py` with no ERROR, one
   `<h1>`, valid JSON-LD, feeds and sitemap parse, `hreflang` pairs, no sideways scroll at
   390px). List any WARN you left, with the reason.
5. Deliver: the file path(s), approved primary intention, substantive-editor verdict, saved
   preference-reference paths and any optional wording still awaiting an explicit choice;
   also include the defaults you applied for skipped answers, any figure you
   changed or dropped, where the two languages use different examples, the evaluator's
   verdict and any finding you chose not to apply, and anything still waiting on him (an
   embed code, a screenshot). Commit and push as the session's git instructions say.
6. Remind him of the one step only he can do, once the post is live: in Google Search
   Console, URL Inspection → paste each post URL → **Request indexing** (Google does not
   take IndexNow), and `node ../tool/_ref/indexnow.mjs <post URL>` for Bing.

Changes he asks for after this are ordinary edits to the post, not a new round of the
flow. An edit to the Indonesian still runs `scripts/cek.py` and the evaluator on the
changed paragraphs before it is pushed, and any edit, in any language, runs
`check-references.py` again: moving or deleting a figure can strand a "below" in another
section. Any edit also runs `check-abbr.py` again: a new sentence may bring an abbreviation
that has no `*[TERM]: meaning` line yet.

### Workflow summary

Concept → plan with intention, scope and selective tone choices → explicit intention and
necessary confirmations → persist approved preferences → evidence ledger → native writers
→ language and pointer checks → fresh substantive review → final technical checks → delivery.
Keep rhetorical devices and occasional announcements, but never make them mandatory.

Small post edits receive a scoped substantive check of changed claims and neighbouring
paragraphs. A changed intention or major rewrite restarts the planning and full-review flow.
Do not expose private author notes or approval provenance in the public post; keep them in
the brief or references and disclose sensitive wording only with author permission.
