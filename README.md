# Adjie Brotot Blog

The bilingual (English / Bahasa Indonesia) blog at **https://blog.adjiebrotots.com**, built by
GitHub Pages' own Jekyll. There is no build step: add a Markdown file, push, and Pages
publishes it. The look comes from the design system of
[Adjie Brotools](https://tool.adjiebrotots.com/).

## Write a post

1. Put the file in the folder for its language, named `YYYY-MM-DD-slug.md`:
   - English: `en/_posts/2026-10-17-rent-vs-buy-calculator-explained.md` →
     `https://blog.adjiebrotots.com/en/rent-vs-buy-calculator-explained/`
   - Indonesian: `id/_posts/2026-10-17-sewa-atau-beli-rumah.md` →
     `https://blog.adjiebrotots.com/id/sewa-atau-beli-rumah/`

   The slug is the URL. Write it in the post's own language, short and with the words
   people search for. Leave the date out of it, because the URL never shows the date.
2. Start the file with front matter:

   ```yaml
   ---
   title: "Rent or buy a house? How to read the Rent vs Own calculator"
   description: "One or two plain sentences that answer the post's question. Shown under the title, in search results and to AI answer engines."
   date: 2026-10-17 09:00:00 +0800
   tags: [finance]                 # finance | engineering | personal | others (one or more)
   # Optional:
   last_modified_at: 2026-11-02    # shown as "Updated", tells search engines it changed
   image: /assets/img/my-card.png  # social preview, 1200×630 works best; else the logo
   image_alt: "What the image shows"
   translation: rent-vs-buy        # only when the same topic exists in the other language
   keywords: [rent vs buy, KPR]    # extra keywords for structured data
   ---
   ```

   Language, layout and URL come from the folder, so you never set them.
3. Write the body in Markdown (GitHub-flavoured). Raw HTML works anywhere.

### Categories

`tags:` takes the keys `finance`, `engineering`, `personal` and `others`, and a post can
carry several: `tags: [finance, engineering]` shows both pills, lists the post on both category
pages, and the first one is the breadcrumb. A label works too, in either language and any case
(`Finance`, `Keuangan`). Each key shows as
Finance / Keuangan, Engineering / Teknik, Personal / Pribadi or Others / Lainnya, and has a
page per language (`/en/category/finance/`, `/id/kategori/keuangan/`). A misspelt or unknown
tag shows as Others, so it never breaks the site. Labels and descriptions live in
`_data/categories.yml`.

### Two languages

English and Indonesian posts are separate writing. They don't need matching slugs or
matching posts. Use `translation:` only when two posts really cover the same topic. Give
both the same value, and the site then:

- tells Google they are language versions of each other (`hreflang`), so each reader is shown
  the right one
- links each post to the other one ("Baca dalam Bahasa Indonesia →") and shows the EN/ID
  button in the top bar, pointing at it

Without `translation:`, the post has no EN/ID button, because there is nothing to switch to.

### Embedding a tool

**One chart:** on any chart in Adjie Brotools, open **Share → Embed as HTML**, copy the code
(an `<iframe>`, a credit line and a short `<script>`), and paste all of it into the post on its
own lines, with a blank line before and after. The chart stays interactive, sizes itself and
follows the blog's light or dark theme.

**A whole tool page:**

```liquid
{% include tool-embed.html src="https://tool.adjiebrotots.com/rentvsownhouse/" title="Rent vs Own calculator" height="760" caption="Try your own numbers." %}
```

If pasted code ever contains `{{` or `{%`, wrap it in `{% raw %}` … `{% endraw %}`.

### Code, maths, diagrams and charts

The same Markdown the tool's [Markdown Reader](https://tool.adjiebrotots.com/mdtopdf/) reads.
KaTeX and Mermaid load only on a post that uses them.

- **Code:** a fenced block with its language (` ```python `, ` ```js `, ` ```yaml `…) is
  highlighted when the site builds, in both themes, with a Copy button.
- **Maths (LaTeX):** `$$E = mc^2$$` inside a sentence is inline. A `$$` block on its own lines
  is a centred equation:

  ```
  $$
  \int_0^\infty e^{-x^2}\,dx = \frac{\sqrt{\pi}}{2}
  $$
  ```

  A single `$` stays a dollar sign, so prices like $500 are safe.
- **Diagrams and charts:** a ` ```mermaid ` block draws a
  [Mermaid](https://mermaid.js.org/intro/) diagram: `flowchart`, `sequenceDiagram`, `gantt`,
  `pie` or `xychart-beta` (bars and lines). Colours come from the blog's theme and the tool's
  chart palette, and redraw when the reader switches theme.

  ````
  ```mermaid
  xychart-beta
    title "Net wealth"
    x-axis [Y1, Y2, Y3, Y4, Y5]
    y-axis "AUD k" 0 --> 200
    bar [20, 45, 80, 120, 170]
    line [30, 50, 70, 95, 120]
  ```
  ````
- **Footnotes:** `text[^1]`, then `[^1]: The note.` anywhere below.
- **Task lists:** `- [ ] to do` and `- [x] done`.
- **Alerts:** GitHub's `> [!NOTE]`, `> [!TIP]`, `> [!IMPORTANT]`, `> [!WARNING]` and
  `> [!CAUTION]` on the first line of a quote.

### Handy extras

- **Table of contents:** put `* TOC` on one line and `{:toc}` on the next.
- **Summary box:** add `{: .tldr}` on the line after a paragraph. `{: .note}` and
  `{: .warning}` work the same way.
- **Images:** keep them in `assets/img/`, and always write alt text:
  `![Net equity chart](/assets/img/net-equity.png)`.

### Writing for search and AI answers

- Answer the question in the `description` and the first paragraph. That text is what gets
  quoted.
- Use question-style `##` headings ("How long until buying pays off?") and short paragraphs
  under them.
- Give real numbers, sources and dates. Set `last_modified_at` when you update a post.
- Link to the relevant tool and to related posts.

## What the site gives every page

- canonical URL, `hreflang` (en / id / x-default), Open Graph and Twitter cards
- JSON-LD: `BlogPosting`, `BreadcrumbList`, `Blog`, `CollectionPage`, `WebSite`, and one
  `Person` (`https://www.adjiebrotots.com/#person`) shared with the main site and the tools
- `sitemap.xml` with language alternates, Atom feeds at `/en/feed.xml` and `/id/feed.xml`,
  `llms.txt` (index for AI crawlers), `llms-full.txt` (every post as plain text) and a
  `robots.txt` that admits search and AI crawlers
- light and dark themes (follows the reader's system until they pick one), no framework,
  one CSS file and one small script

## Preview locally

```sh
bundle install
bundle exec jekyll serve      # http://localhost:4000/en/
```

`Gemfile` pins the `github-pages` gem, so the preview matches what GitHub builds. If Sass
complains about US-ASCII, run with `LANG=C.UTF-8`.

## Publish (one-time setup)

1. Merge into `main`.
2. In GitHub, go to **Settings → Pages**. Set Source to **Deploy from a branch**, with branch
   `main` and folder `/ (root)`.
3. Set Custom domain to `blog.adjiebrotots.com` (the `CNAME` file already says so), then turn
   on **Enforce HTTPS** once the certificate is issued.
4. At your DNS provider, add `CNAME  blog  →  adjiebrotot.github.io`.
5. In Google Search Console (a Domain property for `adjiebrotots.com` covers www, tool and
   blog) and Bing Webmaster Tools, submit `https://blog.adjiebrotots.com/sitemap.xml`.

## Comments (one-time setup, then moderation)

Comments run on [giscus](https://giscus.app): each post's thread is a GitHub Discussion.
They stay off until `comments:` in `_config.yml` is filled in.

1. Create a **public** repo for them, e.g. `adjiebrotot/blog-comments`, and turn on
   **Settings → Features → Discussions**.
2. Install the [giscus app](https://github.com/apps/giscus) on that repo only.
3. On [giscus.app](https://giscus.app), enter the repo and pick the **Announcements**
   category (only you and giscus can open threads there). Copy `data-repo-id` and
   `data-category-id` into `comments:` in `_config.yml`.
4. Watch the repo with **Watch → Custom → Discussions** to get an email for every comment.

Moderating, all on GitHub:

- **Remove a comment:** its `…` menu → **Delete**, or **Hide** with a reason (spam, abuse,
  off-topic) to collapse it.
- **Stop a person:** **Settings → Blocked users** on your account. They can no longer
  comment on any of your repos.
- **Close one thread:** **Lock conversation** on that Discussion.
- **A spam wave:** the repo's **Settings → Moderation options → Interaction limits** pauses
  comments from new accounts for 24 hours up to 6 months.

Comments go live as they are written; you remove bad ones afterwards. Commenters need a
GitHub account. A thread belongs to a language and the post's `translation:` key (or its
slug when it has none), so English and Indonesian comments stay apart. Set
`comments: false` in a post's front matter to leave the section off that post. The page
doesn't contact giscus.app until the reader scrolls near the comments, so a post loads as
fast as without them.

## Files

| Path | What it is |
| --- | --- |
| `en/_posts/`, `id/_posts/` | The posts |
| `_data/categories.yml` | Category keys, labels, descriptions and URLs |
| `_data/i18n.yml` | Every word the layout shows, per language |
| `_config.yml` | Site name, author, links, URL rules |
| `_layouts/`, `_includes/` | Page templates, SEO and structured data |
| `assets/css/blog.css` | Design tokens (copied from the tool's `dark.css` / `light.css`) and styles |
| `assets/js/blog.js` | Theme button, embed theme sync, maths, diagrams, code copy, alerts, comments |
| `en/category/`, `id/kategori/` | One small file per category page |
