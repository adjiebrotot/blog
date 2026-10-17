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

`tags:` takes the keys `finance`, `engineering`, `personal` and `others`. Each one shows as
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
- links each post to the other one ("Baca dalam Bahasa Indonesia →") and points the EN/ID
  button at it

Without `translation:`, the EN/ID button goes to the other language's home page.

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

## Files

| Path | What it is |
| --- | --- |
| `en/_posts/`, `id/_posts/` | The posts |
| `_data/categories.yml` | Category keys, labels, descriptions and URLs |
| `_data/i18n.yml` | Every word the layout shows, per language |
| `_config.yml` | Site name, author, links, URL rules |
| `_layouts/`, `_includes/` | Page templates, SEO and structured data |
| `assets/css/blog.css` | Design tokens (copied from the tool's `dark.css` / `light.css`) and styles |
| `assets/js/blog.js` | Theme button and embed theme sync |
| `en/category/`, `id/kategori/` | One small file per category page |
