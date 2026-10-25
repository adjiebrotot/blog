# Adjie Brotot Blog

Bilingual Jekyll blog at blog.adjiebrotots.com, built by GitHub Pages itself ("Deploy from
branch", `github-pages` gem). Use only plugins that GitHub Pages whitelists, and don't add
GitHub Actions. How to write a post: `README.md`. How to write it in Adjie's voice: the
`adjie-writing-style` skill (`.claude/skills/adjie-writing-style/`). To turn a concept or rough points into a
post, plan first and write after approval: the `ai-assisted-blog-post` skill
(`.claude/skills/ai-assisted-blog-post/`). For a drawn illustration (a person doing the step,
wikiHow style): the `wikihow-illustration` skill (`.claude/skills/wikihow-illustration/`),
with SVG sources in `_illustrations/`. The design tokens come from
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

Then, in `_site/`: each page has exactly one `<h1>` and valid JSON-LD; `sitemap.xml` and
`*/feed.xml` parse as XML; paired posts list each other in `hreflang`; and at 390px no page
scrolls sideways.

## Writing in Indonesian

Use the `bahasa-indonesia` skill (`.claude/skills/bahasa-indonesia/`) and the Indonesian rules
in `adjie-writing-style`: saya-kamu (never *Anda*), keep English terms that sound better,
*gak* where the context is casual.

## Page text

No em-dashes in UI text (same rule as the tool site). Every UI string lives in
`_data/i18n.yml` in both languages, never hard-coded in a layout.
