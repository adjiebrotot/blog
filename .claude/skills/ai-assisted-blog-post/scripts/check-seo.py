#!/usr/bin/env python3
"""Check a post's search (SEO) and answer-engine (GEO) basics before it is pushed.

    python3 .claude/skills/ai-assisted-blog-post/scripts/check-seo.py <lang>/_posts/<file>.md [...]

The layouts already write the canonical URL, robots, hreflang, Open Graph, JSON-LD
(BlogPosting, Person, BreadcrumbList), the sitemap, the feeds and llms.txt. They can only
work with what the post gives them, so this checks the post itself:

- front matter: title, description, tags, image, image_alt, keywords, date
- slug: lowercase ASCII words with hyphens, short, in the post's language
- the answer up front: an "In short" / "Singkatnya" block with `{: .tldr}`
- question-style headings, footnoted sources, a link to a related post
- images with alt text, width and height
- the Markdown copy for AI readers (`md/<lang>-<slug>.txt`) and the social card
- the `translation:` partner, when the key is set

It prints ERROR (fix before pushing) and WARN (fix unless there is a reason, and say the
reason when you deliver). Exit code 1 if any ERROR.
"""
import datetime as dt
import os
import re
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
SITE_TITLE = "Adjie Brotot Blog"
CATEGORY_KEYS = {"finance", "engineering", "personal", "others",
                 "keuangan", "teknik", "pribadi", "lainnya"}


def front_matter(text):
    m = re.match(r"^---\n(.*?)\n---\n(.*)$", text, re.S)
    if not m:
        return None, text
    fm = {}
    for line in m.group(1).splitlines():
        if re.match(r"^\s*#", line) or ":" not in line or line.startswith(" "):
            continue
        k, v = line.split(":", 1)
        v = re.sub(r"\s+#.*$", "", v.strip()) if not v.strip().startswith('"') else v.strip()
        fm[k.strip()] = v.strip().strip('"').strip("'")
    return fm, m.group(2)


def as_list(v):
    v = (v or "").strip()
    if v.startswith("[") and v.endswith("]"):
        return [x.strip().strip('"').strip("'") for x in v[1:-1].split(",") if x.strip()]
    return [v] if v else []


def find_partner(key, here):
    for lang in ("en", "id"):
        d = os.path.join(ROOT, lang, "_posts")
        for f in os.listdir(d) if os.path.isdir(d) else []:
            p = os.path.join(d, f)
            if os.path.abspath(p) == os.path.abspath(here):
                continue
            with open(p, encoding="utf-8") as fh:
                fm, _ = front_matter(fh.read())
            if fm and fm.get("translation") == key:
                return p
    return None


def check(path):
    errors, warns = [], []
    E, W = errors.append, warns.append
    with open(path, encoding="utf-8") as fh:
        text = fh.read()
    fm, body = front_matter(text)
    if fm is None:
        print(f"{path}\n  ERROR: no front matter")
        return 1

    name = os.path.basename(path)
    m = re.match(r"^(\d{4}-\d{2}-\d{2})-(.+)\.md$", name)
    lang = os.path.basename(os.path.dirname(os.path.dirname(os.path.abspath(path))))
    slug = m.group(2) if m else ""
    if not m:
        E("filename is not YYYY-MM-DD-slug.md")

    # Slug: the URL forever, and a ranking signal. Short, lowercase, words people search.
    if slug and not re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*", slug):
        E(f"slug '{slug}': use lowercase ASCII words joined by single hyphens")
    words = slug.split("-") if slug else []
    if len(words) > 6:
        W(f"slug has {len(words)} words: keep it to the 2 to 6 words people search for")
    if any(w in {"the", "a", "an", "and", "of", "yang", "dan", "di", "ke"} for w in words) and len(words) > 4:
        W("slug carries filler words (the, a, of, yang, dan...): drop them")

    # Title: Google shows about 60 characters. head.html drops the blog name when
    # "title | Adjie Brotot Blog" runs longer, so the title itself must fit.
    title = fm.get("title", "")
    shown = fm.get("seo_title") or title
    if not title:
        E("no title")
    elif len(shown) > 60:
        W(f"title is {len(shown)} characters, Google cuts it near 60: shorten it, or add a "
          "seo_title of 60 or fewer that keeps the main search words first")
    elif len(shown) < 20:
        W(f"title is only {len(shown)} characters: say what the post answers")

    # Description: the snippet in search results and the summary answer engines quote.
    desc = fm.get("description", "")
    if not desc:
        E("no description")
    elif len(desc) > 160:
        W(f"description is {len(desc)} characters, Google cuts it near 155 to 160: "
          "keep the hook and the main search words in the first 150")
    elif len(desc) < 70:
        W(f"description is only {len(desc)} characters: aim for 110 to 160")
    if desc and title and desc.strip().lower() == title.strip().lower():
        E("description repeats the title")
    if "—" in title + desc:
        E("em-dash in the title or description")

    tags = as_list(fm.get("tags"))
    if not tags:
        E("no tags: the post falls into Others and gets no category breadcrumb")
    for t in tags:
        if t.lower() not in CATEGORY_KEYS:
            W(f"tag '{t}' is not a category key: it shows as Others")

    kws = as_list(fm.get("keywords"))
    if len(kws) < 3:
        W("fewer than 3 keywords: list the phrases people type or ask, in the post's language "
          "(the question, the tool's name, the local terms)")

    # Date: Jekyll does not publish a post dated in the future until the next build after it.
    try:
        d = dt.datetime.strptime(fm.get("date", "")[:19], "%Y-%m-%d %H:%M:%S")
        if d > dt.datetime.now() + dt.timedelta(hours=12):
            W(f"date {fm['date']} is in the future: GitHub Pages skips the post until a build after that time")
    except ValueError:
        E("date is not 'YYYY-MM-DD HH:MM:SS +0800'")

    # Social card and its alt text: shared links, Discover and image results.
    img = fm.get("image", "")
    if not img:
        W("no image: the post uses the generic blog card. Draw one with `node _build/og.mjs`")
    elif not os.path.exists(os.path.join(ROOT, img.lstrip("/"))):
        E(f"image {img} does not exist")
    if img and not fm.get("image_alt"):
        W("no image_alt")

    # The answer first: answer engines quote the opening that answers the question.
    if not re.search(r"\{:\s*\.tldr\s*\}", body):
        W("no 'In short' / 'Singkatnya' block with {: .tldr}: answer the question in the first paragraph")
    else:
        tldr = body.split("{: .tldr}")[0].strip().split("\n\n")[-1]
        n = len(re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", tldr).split())
        if n > 120:
            W(f"the In short block is {n} words: answer engines quote 40 to 90 well")

    heads = re.findall(r"^(##+)\s+(.+)$", body, re.M)
    h2 = [h for lvl, h in heads if lvl == "##" and not re.match(r"(References|Referensi)\b", h)]
    if len(h2) < 3:
        W(f"only {len(h2)} sections (##): a post that answers one question in several steps "
          "reads and ranks better with 3 or more")
    q = [h for h in h2 if h.rstrip().endswith("?")]
    if h2 and len(q) * 2 < len(h2):
        W(f"{len(q)} of {len(h2)} section headings are questions: phrase most of them as the "
          "question a reader would type or ask")
    if re.search(r"^#\s", body, re.M):
        E("a '# heading' in the body: the layout writes the only <h1> from the title")

    if re.search(r"\d", body) and "[^" not in body:
        W("numbers but no footnoted sources: cite each figure with a footnote to its publisher")

    if not re.search(r"\]\((/(en|id)/|https://blog\.adjiebrotots\.com/)", body):
        W("no link to another post on this blog: link the most related one in the text")

    for img_tag in re.findall(r"<img\b[^>]*>", body):
        if not re.search(r'\balt="[^"]+"', img_tag):
            E(f"image without alt text: {img_tag[:80]}")
        if not (re.search(r"\bwidth=", img_tag) and re.search(r"\bheight=", img_tag)):
            W(f"image without width and height (layout shift): {img_tag[:80]}")
    for alt, src in re.findall(r"!\[([^\]]*)\]\(([^)]+)\)", body):
        if not alt.strip():
            E(f"Markdown image without alt text: {src}")

    # The Markdown copy at <post URL>index.md, linked from <head> and llms.txt.
    if slug and not os.path.exists(os.path.join(ROOT, "md", f"{lang}-{slug}.txt")):
        W(f"no md/{lang}-{slug}.txt stub: the post has no Markdown copy for AI readers (md/README.txt)")

    key = fm.get("translation")
    if key and not find_partner(key, path):
        W(f"translation: {key} has no partner post yet, so no hreflang pair")

    print(path)
    for e in errors:
        print(f"  ERROR: {e}")
    for w in warns:
        print(f"  WARN: {w}")
    if not errors and not warns:
        print("  OK")
    return 1 if errors else 0


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(2)
    sys.exit(max(check(p) for p in sys.argv[1:]))
