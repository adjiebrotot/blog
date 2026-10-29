#!/usr/bin/env python3
"""Find in-text references that point outside their own section.

    python3 .claude/skills/adjie-writing-style/scripts/check-references.py <post>.md [...]

The rule (adjie-writing-style, "Point only at what is in the same section"): a sentence
may point at a figure, table, chart, screenshot, list or worked example only if that thing
sits in the same section (the same `##` or `###`), in the direction the sentence says.
Otherwise the pointer goes and the sentence states its fact on its own. The one exception
is a reference to a whole section, named by its heading.

Works for English and Indonesian. It prints:

- ERROR: a pointer whose target is not in this section, in that direction, or a pointer
  to a later section. Fix every one.
- REVIEW: a back-reference ("tadi", "as I showed", "earlier") or a section name. Read it:
  it passes only if what it points at is in this same section, or if the whole section
  is what it means.

It finds patterns, not every case: "the exchange rate" can still lean on a number three
sections up. The reference-checker agent (.claude/agents/reference-checker.md) reads for
those. Exit code 1 if any ERROR.
"""
import re
import sys

# What a pointer can name, and the blocks that satisfy it.
KINDS = {
    "table": "table", "tabel": "table",
    "screenshot": "image", "image": "image", "picture": "image", "gambar": "image",
    "figure": "image", "illustration": "image", "ilustrasi": "image", "foto": "image",
    "photo": "image",
    "chart": "chart", "graph": "chart", "grafik": "chart", "diagram": "chart",
    "embed": "chart",
    "list": "list", "daftar": "list",
}
VAGUE = ("example|examples|calculation|calculations|numbers|figures|details|sum|steps|"
         "contoh|hitungan|angka|rincian|rinciannya|langkah|skenario")
NOUNS = "|".join(sorted(KINDS, key=len, reverse=True)) + "|" + VAGUE

# Forward and backward pointers. Each pattern names its direction.
POINTERS = [
    # English
    (rf"\b({NOUNS})\b[^.!?]{{0,40}}?\b(below|further down|that follows|coming up)\b", "fwd"),
    (rf"\b({NOUNS})\b[^.!?]{{0,40}}?\babove\b(?!\s+\d)", "back"),
    (r"\b(below|above)\s*[).:;,]", "bare"),
    (r"\(\s*(see )?(below|above)\s*\)", "bare"),
    (r"\b(further down|later in (this|the) post|I will show|I'll show|we'll see)\b", "later"),
    # Indonesian (di atas / di bawah are positional only next to a noun or at a clause end)
    (rf"\b({NOUNS})\b[^.!?]{{0,40}}?\bdi bawah\b(?!nya)(?!\s+(Rp|A\$|S\$|US\$|\d|PTKP|rata-rata|batas))", "fwd"),
    (rf"\b({NOUNS})\b[^.!?]{{0,40}}?\bdi atas\b(?!nya)(?!\s+(Rp|A\$|S\$|US\$|\d|PTKP|rata-rata|batas|kertas))", "back"),
    (r"\bdi (bawah|atas)( ini| tadi)?\s*[).:;,]", "bare"),
    (r"\bdi bawah ini\b|\bberikut ini\b", "fwd"),
    (r"\b(nanti|kelak) (akan )?saya (tunjukkan|bahas|jelaskan)\b|\bdi bagian (berikut|selanjutnya)\b", "later"),
]
BACKREF = [
    r"\btadi\b",
    r"\b(seperti|sebagaimana) (yang )?(sudah |telah )?(saya |kita )?(jelaskan|tunjukkan|sebut(kan)?|bahas)\b",
    r"\bsudah saya (jelaskan|tunjukkan|sebut(kan)?|bahas)\b",
    r"\bas I (showed|said|mentioned|explained|noted|wrote)\b",
    r"\bas (shown|mentioned|discussed|noted|explained) (earlier|before|above)\b",
    r"\b(earlier|previously) (in this post|I showed|I said)\b",
]
SECTION = [
    r"\b[A-Z][\w-]*( [A-Z][\w-]*)* section\b",
    r"\bthe \w+ (section|part)\b",
    r"\b(di )?bagian [A-Z\"*]",
    r"\bbagian (gabung|pisah|sebelumnya|terakhir|pertama|awal)\b",
]


def blocks(lines):
    """Classify each line: heading, table, image, chart, list, para, skip."""
    out, in_fm, fence = [], False, None
    for i, raw in enumerate(lines):
        s = raw.strip()
        if i == 0 and s == "---":
            in_fm = True
            out.append("skip")
            continue
        if in_fm:
            in_fm = s != "---"
            out.append("skip")
            continue
        if fence:
            out.append(fence)
            if s.startswith("```"):
                fence = None
            continue
        if s.startswith("```"):
            fence = "chart" if "mermaid" in s else "code"
            out.append(fence)
            continue
        if re.match(r"#{2,6} ", s):
            out.append("heading")
        elif s.startswith("|"):
            out.append("table")
        elif "<iframe" in s or "{% include tool-embed" in s:
            out.append("chart")
        elif "<img" in s or re.match(r"!\[", s):
            out.append("image")
        elif re.match(r"([-*]|\d+\.)\s", s) and s != "* TOC":
            out.append("list")
        elif s.startswith("[^") or s.startswith("*[") or not s or s.startswith("<") or s.startswith("{:"):
            out.append("skip")
        else:
            out.append("para")
    return out


def section_range(kinds, i):
    start = i
    while start > 0 and kinds[start - 1] != "heading":
        start -= 1
    end = i
    while end + 1 < len(kinds) and kinds[end + 1] != "heading":
        end += 1
    return start, end


def has(kinds, lo, hi, want):
    rng = kinds[lo:hi + 1] if lo <= hi else []
    if want is None:
        # a vague "the numbers below" needs a real figure, not the bullets around it
        return any(k in ("table", "image", "chart") for k in rng)
    if want == "chart":
        return any(k in ("chart", "image") for k in rng)
    return want in rng


def prose(line):
    s = re.sub(r"`[^`]*`|\$\$.*?\$\$|\]\([^)]*\)|https?://\S+|<[^>]+>", " ", line)
    return re.sub(r"[*_]", "", s)


def check(path):
    with open(path, encoding="utf-8") as f:
        lines = f.readlines()
    kinds = blocks(lines)
    found = []
    for i, raw in enumerate(lines):
        if kinds[i] not in ("para", "list"):
            # captions and alt text can point too
            if not re.search(r"<figcaption>", raw):
                continue
        text = prose(raw)
        if "<figcaption>" in raw:
            text = prose(re.sub(r"^.*<figcaption>|</figcaption>.*$", "", raw))
        lo, hi = section_range(kinds, i)
        for pat, way in POINTERS:
            for m in re.finditer(pat, text, re.I):
                quote = m.group(0)
                # the specific noun nearest the pointer decides what must be there
                named = [n.lower() for n in re.findall(rf"\b({NOUNS})\b", quote, re.I)]
                want = next((KINDS[n] for n in reversed(named) if n in KINDS), None)
                if way == "later":
                    found.append(("ERROR", i + 1, quote, "points at a later part of the post; state the fact here or drop the pointer"))
                    continue
                if way == "bare":
                    word = m.group(0).lower()
                    way = "fwd" if ("below" in word or "bawah" in word) else "back"
                ok = has(kinds, i + 1, hi, want) if way == "fwd" else has(kinds, lo, i - 1, want)
                if not ok:
                    where = "below it" if way == "fwd" else "above it"
                    thing = want or "figure, table or chart"
                    found.append(("ERROR", i + 1, quote, f"no {thing} {where} in this section; drop the pointer and state the fact"))
        for pat in BACKREF:
            for m in re.finditer(pat, text, re.I):
                found.append(("REVIEW", i + 1, m.group(0), "back-reference: is what it points at in this same section? If not, restate the fact"))
        for pat in SECTION:
            for m in re.finditer(pat, text):
                found.append(("REVIEW", i + 1, m.group(0), "names a section: allowed only if the whole section is the referent"))
    return found


def main(paths):
    errors = 0
    for p in paths:
        for level, ln, quote, hint in check(p):
            errors += level == "ERROR"
            print(f"{level} {p}:{ln}: \"{quote}\": {hint}")
    print(f"{errors} ERROR" if errors else "no ERROR")
    return 1 if errors else 0


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    sys.exit(main(sys.argv[1:]))
