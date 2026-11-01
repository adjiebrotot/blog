# Adjie Brotot Blog

Bilingual Jekyll blog at blog.adjiebrotots.com, built by GitHub Pages itself ("Deploy from
branch", `github-pages` gem). Use only plugins that GitHub Pages whitelists, and don't add
GitHub Actions. How to write a post: `README.md`. How to write it in Adjie's voice: the
`adjie-writing-style` skill (`.claude/skills/adjie-writing-style/`). To turn a concept or rough points into a
post, plan first and write after approval: the `ai-assisted-blog-post` skill
(`.claude/skills/ai-assisted-blog-post/`). For an illustration (a person doing the step,
wikiHow style): the `wikihow-illustration` skill (`.claude/skills/wikihow-illustration/`),
made with an image model on OpenRouter, prompts kept in `_illustrations/`. The design tokens come from
`../tool/dark.css` and `light.css` (tool repo, `_ref/design-reference.md`).

## Published URLs are permanent

Search engines, feeds, other sites and AI answers keep the old address, so a change must
never break a URL that is already live.

- **A post's slug never changes** once it is published. Fix a title in `title:`, not in the
  filename. If a slug has to change, add a `redirect_from:` list (the `jekyll-redirect-from`
  plugin, which GitHub Pages ships) with the old path.
- **Category keys** (`finance`, `engineering`, `personal`, `others`) and the category page
  URLs in `_data/categories.yml` are frozen. Reword labels and descriptions freely. A new
  category is a new key, plus one page per language.
- **Language folders** `/en/` and `/id/` are fixed. A third language gets its own folder, a
  block in `_data/i18n.yml`, a `defaults` entry in `_config.yml` and an entry in `languages`.
- **The `translation:` key** pairs posts across languages. Change it on both posts at once,
  or not at all.
- **`site.author.id`** (`https://www.adjiebrotots.com/#person`) is the entity id shared with
  www and tool. Keep it.

## Checks before pushing

```sh
LANG=C.UTF-8 bundle exec jekyll build
```

Every post you touched, in any language, passes
`python3 .claude/skills/adjie-writing-style/scripts/check-references.py <file>` (no ERROR):
a sentence points only at a figure, table, chart or example in its own section, never at
one in another section ("the screenshot below" three sections up is wrong). A new or
rewritten post also passes the reference-checker agent (`.claude/agents/reference-checker.md`)
and `python3 .claude/skills/ai-assisted-blog-post/scripts/check-seo.py <file>` (no ERROR),
and has its `md/<lang>-<slug>.txt` stub.

Then, in `_site/`: each page has exactly one `<h1>` and valid JSON-LD; `sitemap.xml` and
`*/feed.xml` parse as XML; paired posts list each other in `hreflang`; and at 390px no page
scrolls sideways.

## Writing in Indonesian

**Mandatory:** load the `bahasa-indonesia` skill (`.claude/skills/bahasa-indonesia/`) before
writing, translating or editing any Indonesian text (posts, front matter, captions, alt text,
`_data/` strings), even a one-word fix. One voice: written Jakarta Indonesian with the flow of
an opinion column, saya-kamu (never *Anda*), no regional languages, foreign terms in italics.
Write it natively from the case, never by translating the English post sentence by sentence.

- **Before pushing,** Indonesian passes `python3 .claude/skills/bahasa-indonesia/scripts/cek.py
  <file>` (no ERROR) and the evaluator in `references/evaluator.md`, run by an agent that has
  not read the English.
- **A post in both languages** is written by two writer agents from one language-neutral brief,
  in parallel, never by one context writing both (`ai-assisted-blog-post`, Step 3). The two may
  use different examples as long as the message and the verified numbers match.

## Page text

No em-dashes in UI text (same rule as the tool site). Every UI string lives in
`_data/i18n.yml` in both languages, never hard-coded in a layout.
