#!/usr/bin/env python3
"""Mechanical pass of the Indonesian evaluator (references/evaluator.md).

    python3 .claude/skills/bahasa-indonesia/scripts/cek.py id/_posts/<post>.md [...]

It reads the prose of a post (front matter title, description and alt text, body text,
captions, footnotes) and skips code, KaTeX, Mermaid, embeds and URLs. It prints:

- ERROR: a rule of the skill is broken. Fix every one.
- REVIEW: a pattern that is usually a calque or English habit. Read the sentence and fix
  it unless it is a deliberate choice you can defend.

It finds patterns, not quality: a clean run does not mean the text is natural. The
evaluator still reads every sentence (references/evaluator.md). Exit code 1 if any ERROR.
"""
import re
import sys

# Calques and wrong terms Adjie has corrected (references/corrections.md).
CALQUES = [
    (r"\bdikasih harga\b", "calque of 'can't be priced': tidak ternilai harganya"),
    (r"\bbuatan saya\b|\bmilik saya\b", "credit to self sounds arrogant: just name the tool"),
    (r"\bjujurkan\b", "not a word: 'yang saya harus jujur', 'di sinilah saya harus jujur'"),
    (r"(?<!imbal )\bhasil (rumah|uang)", "return is 'imbal hasil'"),
    (r"\bBegini cara\b", "'Ini cara ...'"),
    (r"\bmelakukan pengecekan\b|\bdikarenakan\b|\bterdapat sebuah\b|\bdalam rangka untuk\b",
     "heavy nominalisation: mengecek, karena, ada, untuk"),
    (r"\bharga uang\b|\bcost of money\b", "'bunga KPR'"),
    (r"\bgaji bersih dibawa pulang\b", "'gaji bersih (take-home pay)'"),
    (r"\bapel dengan apel\b", "'apple to apple'"),
    (r"\bbiaya peluang\b", "'opportunity cost'"),
    (r"\bnilai hidup\b", "'values'"),
    (r"\b(tiga|dua|empat|lima) titik\b", "data points are 'contoh', 'jenis', 'kasus'"),
    (r"\bsatu poin\b|\bpoin persentase\b", "'persen' (poin reads like a score)"),
    (r"\bjauh lebih tenang\b", "'jauh lebih moderat'"),
    (r"\banggap saja seperti\b", "'anggap saja X' (anggap already compares)"),
    (r"\bpengakuan dulu\b", "'mari jujur-jujuran dulu'"),
    (r"\bnegara kelahiran\b", "means 'country of birth'; say 'tumbuh dari kelahiran'"),
    (r"\ba\.k\.a\.", "Indonesian has 'alias'"),
    (r"\bberbentuk batu bata\b", "'bricks and mortar': 'tertanam di properti'"),
    (r"\bekor bunga\b", "'periode bunga floating di sisa tenor'"),
    (r"\bdi dunia nyata bekerja\b", "calque of 'how it works in the real world'"),
    (r"\bcukup ingin\b", "calque of 'just wants': 'baginya, cukup ...'"),
    (r"\bjadi kawan\b", "calque of 'becomes your friend'"),
    (r"\bmedian bersumber\b", "'nilai median dari sumber yang jelas'"),
    (r"\bribetnya juga nyata\b", "calque of 'the hassle is real'"),
    (r"\btidak mengklaim apa-apa\b", "calque of 'I make no claim'"),
]

# False friends: read the sentence and check the meaning.
FALSE_FRIENDS = [
    (r"\bbunga \*?flat\*?|\*flat\* \d", "in Indonesia 'bunga flat' is a calculation method; a whole-term rate is 'fixed'"),
    (r"\briil(nya)?\b", "'riil' means inflation-adjusted; for 'actual' say 'yang sebenarnya'"),
    (r"\bbatasannya\b|\bdan batasan\b", "a study's limits are 'keterbatasan'"),
    (r"\blewat \[", "a source is 'dikutip dari' or 'menurut', not 'lewat' (via)"),
    (r"^Dengan (gabung|pisah|kerja|MT|PH)\b|[.] Dengan (gabung|pisah|kerja|MT|PH)\b", "'with X' calque: 'Kalau memilih ...', 'Untuk ...'"),
    (r"\b(Garis )?(biru|oranye|hijau|merah muda) adalah\b", "a colour is not the scenario: 'garis biru menunjukkan ...'"),
    (r"\bmenganggap\b.*\b(tool|kalkulator|sistem)\b|\b(Tool|tool|sistem)\*? ini menganggap\b", "a tool calculates, it does not think"),
]

# Places and things that cannot speak, followed by a verb of speech or will.
PLACE = (r"(kota|negara|negeri|pasar|market|wilayah|kawasan|daerah|provinsi|Perth|Jakarta|"
         r"Bali|Melbourne|Sydney|Singapura|Australia|Indonesia|Jepang|Bandung|Surabaya|"
         r"Medan|Yogyakarta|Batam|London|Tokyo)")
PERSONIFICATION = re.compile(
    rf"\b{PLACE}\s+(?:\w+\s+)?(bilang|berkata|mengatakan|menyarankan|bercerita|menjawab|"
    rf"berpendapat|menyuruh|bayarnya)\b|\bapa kata\s+(kota|negara|pasar|kompas|tool|"
    rf"grafik|data)\b", re.I)
# Weaker: a city that "needs" or "chooses". Natural for a state, odd for a city or market.
PERSONIFICATION_SOFT = re.compile(rf"\b{PLACE}\s+(butuh|memilih|ingin|mau)\b", re.I)

# English words the blog keeps: they must be in italics (*tool*, *tool*-nya).
FOREIGN = [
    "tool", "tools", "take-home pay", "take-home", "rental yield", "leverage",
    "opportunity cost", "breakeven", "values", "market", "hot", "input", "fixed",
    "floating", "flat", "deal", "downgrade", "spreadsheet", "screenshot", "browser",
    "freelance", "stress test", "apple to apple", "holistic thinking",
    "liquid asset thinking", "cost-saving thinking", "replacement level", "resident",
    "work permit", "work pass", "developed market", "capital freedom", "developer",
    "public service", "relief", "superannuation", "permanent resident", "disposable income",
    "cost of living",
]
# Proper names and tool labels that contain those words but are not italicised.
PROPER = [
    "Sensitivity Analysis tool", "Cost of Living Comparator", "Quick Start", "Stress Test",
    "Adjie Brotools", "Adjie Brotot Tools", "Risk-Free Rate",
]

CONJ_START = re.compile(
    r"^(Dan|Tapi|Tetapi|Namun|Jadi|Karena|Sehingga|Atau|Sedangkan|Lalu|Terus|Makanya|"
    r"Soalnya|Padahal|Toh)\b")
CONJ_HARD = {"Dan", "Tapi", "Sehingga", "Atau", "Terus", "Makanya", "Soalnya", "Toh"}

findings = []


def add(level, path, line, cat, text, hint=""):
    findings.append((level, path, line, cat, text.strip(), hint))


def strip_markup(s):
    s = re.sub(r"`[^`]*`", " ", s)
    s = re.sub(r"\$\$.*?\$\$", " X ", s)
    s = re.sub(r"\]\([^)]*\)", "]", s)          # link targets
    s = re.sub(r"\[\^[^\]]+\]", "", s)           # footnote refs
    s = re.sub(r"https?://\S+", " ", s)
    s = re.sub(r"<em>(.*?)</em>", r"*\1*", s)
    s = re.sub(r"<[^>]+>", " ", s)
    return s


def remove_italics(s):
    s = re.sub(r"<em>.*?</em>", " ", s)
    s = re.sub(r"(?<![*\w])\*(?!\*)([^*\n]+?)\*(?!\*)", " ", s)
    s = re.sub(r"(?<![_\w])_([^_\n]+?)_(?![_\w])", " ", s)
    return s


def sentences(text):
    text = re.sub(r"\*\*|__", "", text)
    text = re.sub(r"(?<![*\w])\*(?!\*)|(?<!\*)\*(?![*\w])", "", text)
    parts = re.split(r"(?<=[.!?])\s+(?=[\"'(*\[A-Z0-9])", text.strip())
    return [p.strip() for p in parts if p.strip()]


def words(s):
    return re.findall(r"[\w'-]+", s)


def prose_blocks(path, lines):
    """Yield (line_no, kind, text). kind: fm, heading, para, item, table, caption, alt."""
    in_fm = in_code = in_math = False
    block, start = [], 0

    def flush():
        nonlocal block
        if block:
            yield start, "para", " ".join(block)
        block = []

    for i, raw in enumerate(lines, 1):
        line = raw.rstrip("\n")
        s = line.strip()
        if i == 1 and s == "---":
            in_fm = True
            continue
        if in_fm:
            if s == "---":
                in_fm = False
                continue
            m = re.match(r"(title|description|image_alt):\s*\"?(.*?)\"?$", s)
            if m:
                yield i, "fm", m.group(2)
            continue
        if s.startswith("```"):
            in_code = not in_code
            continue
        if in_code:
            continue
        if s == "$$":
            in_math = not in_math
            continue
        if in_math:
            continue
        for alt in re.findall(r'alt="([^"]+)"', line):
            yield i, "alt", alt
        for cap in re.findall(r"<figcaption>(.*?)</figcaption>", line):
            yield i, "caption", cap
        if (not s or s.startswith("<") or s.startswith("{:") or s.startswith("*[")
                or s == "* TOC" or re.match(r"^\|?\s*-{3}", s)):
            yield from flush()
            continue
        if s.startswith("#"):
            yield from flush()
            yield i, "heading", s.lstrip("#").strip()
            continue
        if s.startswith("|"):
            yield from flush()
            yield i, "table", s
            continue
        m = re.match(r"^(?:[-*]|\d+\.)\s+(.*)", s)
        if m or s.startswith("[^") or s.startswith(">"):
            yield from flush()
            text = m.group(1) if m else re.sub(r"^(\[\^[^\]]+\]:|>\s*(\[!\w+\])?)", "", s)
            yield i, "item", text
            continue
        if not block:
            start = i
        block.append(s)
    yield from flush()


def check(path):
    with open(path, encoding="utf-8") as f:
        lines = f.readlines()
    conj_total, word_total = 0, 0
    for ln, kind, raw in prose_blocks(path, lines):
        text = strip_markup(raw)
        plain = re.sub(r"[*_]", "", text)

        # Hard rules.
        if re.search(r"[—–]", raw):
            add("ERROR", path, ln, "em-dash", plain, "colon, comma, parentheses or full stop")
        if re.search(r"\bAnda\b", plain):
            add("ERROR", path, ln, "Anda", plain, "the reader is kamu")
        if re.search(r"\b(gue|gua|lu|elo)\b", plain, re.I):
            add("ERROR", path, ln, "gue/lo", plain, "saya-kamu only")
        if re.search(r"\bgak\s*([.,!?;:)\"]|$)", plain):
            add("ERROR", path, ln, "gak standalone", plain, "enggak (casual) or tidak")
        if re.search(r"\b(nggak|ngga|ga)\b", plain):
            add("ERROR", path, ln, "spelling", plain, "gak / enggak")
        for pat, hint in CALQUES:
            if re.search(pat, raw, re.I):
                add("ERROR", path, ln, "known calque", plain, hint)
        for pat, hint in FALSE_FRIENDS:
            if re.search(pat, raw):
                add("REVIEW", path, ln, "false friend / calque", plain, hint)
        if PERSONIFICATION.search(plain):
            add("ERROR", path, ln, "personified place", plain,
                "a city or market cannot speak: 'di Perth lebih untung membeli'")
        elif PERSONIFICATION_SOFT.search(plain):
            add("REVIEW", path, ln, "personified place?", plain,
                "fine for a state ('Indonesia butuh'), not for a city or a market")

        # Relative yang mana / di mana.
        for sent in sentences(plain):
            if re.search(r"\byang mana\s+\w", sent) and not sent.endswith("?"):
                add("REVIEW", path, ln, "yang mana", sent, "split the sentence or use yang")
            if re.search(r"\w,?\s+di mana\b(?!\s*(pun|-mana))", sent) and not sent.endswith("?"):
                add("REVIEW", path, ln, "di mana", sent, "tempat, ketika, or split")

        # Foreign words without italics (alt text cannot hold italics).
        t = "" if kind == "alt" else remove_italics(text)
        for p in PROPER:
            t = t.replace(p, " ")
        for w in FOREIGN:
            for m in re.finditer(rf"(?<![\w*-]){re.escape(w)}(?![\w*])", t):
                ctx = t[max(0, m.start() - 30):m.end() + 30].replace("\n", " ")
                add("REVIEW", path, ln, "foreign term not italic", ctx,
                    f"*{w}* (and *{w}*-nya); proper names and tool labels stay roman")
        if re.search(r"\*[^*\s][^*]*\*(nya|mu|ku)\b", raw):
            add("REVIEW", path, ln, "suffix on italic term", plain, "*tool*-nya, with a hyphen")

        if kind in ("table", "fm", "caption", "alt"):
            continue
        sents = sentences(plain)
        word_total += len(words(plain))

        # Sentence-initial conjunctions.
        starts = []
        for sent in sents:
            m = CONJ_START.match(sent)
            if m:
                starts.append(m.group(1))
                conj_total += 1
                if m.group(1) in CONJ_HARD and kind != "heading":
                    add("REVIEW", path, ln, f"starts with '{m.group(1)}'", sent,
                        "join it to the previous sentence or open with a real transition")
        if len(starts) >= 2:
            add("REVIEW", path, ln, "conjunction-heavy paragraph",
                " / ".join(s[:50] for s in sents if CONJ_START.match(s)),
                "at most one sentence-initial conjunction per paragraph")

        # Slogan runs: three or more short sentences in a row.
        run = []
        for sent in sents + [""]:
            if sent and len(words(sent)) <= 6:
                run.append(sent)
                continue
            if len(run) >= 3:
                add("REVIEW", path, ln, "slogan run (short sentences)", " ".join(run),
                    "one flowing compound sentence, not ad copy")
            run = []
        # Mirrored slogan: "X itu urusan A. Y itu urusan B."
        if re.search(r"\b(\w+) itu urusan \w+\.\s+\w+ itu urusan", plain):
            add("REVIEW", path, ln, "mirrored slogan", plain, "one compound sentence")

        # Note-style fragments.
        for sent in sents:
            n = len(words(sent))
            if kind == "heading":
                continue
            if n <= 7 and re.search(r"\bdulu[.!]$", sent) and not re.search(r"\b(mari|saya|kita|kamu)\b", sent, re.I):
                add("REVIEW", path, ln, "note-style fragment", sent,
                    "give it a subject and a verb: 'mari kita bahas Perth terlebih dahulu'")
            elif n <= 3 and kind == "para" and not re.search(r"[?]$", sent):
                add("REVIEW", path, ln, "very short sentence", sent,
                    "keep only if it is a deliberate punch (one per section)")
    itulah = sum(len(re.findall(r"\bItulah\b", l)) for l in lines)
    if itulah > 2:
        add("REVIEW", path, 0, "connective tic", f"'Itulah' opens {itulah} sentences",
            "vary the transitions; each one must point at the right reason")
    if word_total:
        rate = conj_total * 1000 / word_total
        level = "REVIEW" if rate > 8 else "INFO"
        add(level, path, 0, "conjunction density",
            f"{conj_total} sentence-initial conjunctions in {word_total} words "
            f"({rate:.1f} per 1000)", "aim for 8 or fewer per 1000 words")


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return 2
    for path in sys.argv[1:]:
        check(path)
    order = {"ERROR": 0, "REVIEW": 1, "INFO": 2}
    for level, path, ln, cat, text, hint in sorted(findings, key=lambda f: (f[1], order[f[0]], f[2])):
        print(f"{level:6} {path}:{ln}  [{cat}] {text[:160]}")
        if hint:
            print(f"       -> {hint}")
    errors = sum(1 for f in findings if f[0] == "ERROR")
    reviews = sum(1 for f in findings if f[0] == "REVIEW")
    print(f"\n{errors} error(s), {reviews} to review.")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
