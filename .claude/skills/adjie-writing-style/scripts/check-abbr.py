#!/usr/bin/env python3
"""Find abbreviations that have no <abbr> definition.

    python3 .claude/skills/adjie-writing-style/scripts/check-abbr.py <post>.md [...]

The rule (adjie-writing-style, "Abbreviations"): every abbreviation, acronym or short form
in a post is defined once with kramdown's `*[TERM]: meaning` line, which renders every use of
it as <abbr title="meaning">. Kramdown matches the exact term, whole word, case-sensitive, so
`MPs` needs its own line next to `MP`. Works for English and Indonesian.

It prints:

- ERROR: an all-caps term (DPR, KPR, Q2, TK/0, S&P, AFL-CIO...) or a known short form
  (dkk, e.g...) that is used but not defined. Define it, or, if it is a brand and not an
  abbreviation, add `<!-- abbr-ok: TERM -->` anywhere in the post.
- WARN: a definition the post never uses (stale), or a definition written twice.

Not checked, on purpose: very obvious ones (vs, US, UK, TV, PDF, a.k.a, dll), currency symbols and number suffixes (Rp, A$, 850k, 1.27bn), roman
numerals, and mixed-case short forms such as Kemenkeu or MaPS. Those are the writer's call, so
read the post once for them. Exit code 1 if any ERROR.
"""
import re
import sys

# Lowercase short forms the all-caps scan cannot see. Add to this list when a new one turns up.
SHORT_FORMS = ["dkk", "dsb", "dst", "e.g", "i.e", "approx", "yg", "dgn"]
# Markers and labels that are not abbreviations of anything the reader needs explained, and
# abbreviations so obvious that a tooltip is clutter (vs, a.k.a, dll are not in SHORT_FORMS).
SKIP = {"TOC", "NOTE", "TIP", "IMPORTANT", "WARNING", "CAUTION",
        "US", "UK", "AS", "TV", "PDF", "SUV", "SUVs", "ID", "OK", "AI"}

DEF = re.compile(r"^\*\[([^\]]+)\]:\s*(.*)$")
TOKEN = re.compile(r"(?<![\w/@.#$&-])([A-Z][A-Z0-9]*[A-Z0-9](?:[/&-][A-Za-z0-9]+)*s?)(?![\w])")
SHORT = re.compile(r"(?<![\w.])(" + "|".join(re.escape(s) for s in SHORT_FORMS) + r")(?![\w])")


def strip_markdown(lines):
    """Yield (line number, text) for the prose a reader sees and kramdown scans."""
    in_front = False
    in_code = False
    for n, line in enumerate(lines, 1):
        if n == 1 and line.strip() == "---":
            in_front = True
            continue
        if in_front:
            if line.strip() == "---":
                in_front = False
            continue
        if line.lstrip().startswith(("```", "~~~")):
            in_code = not in_code
            continue
        if in_code or DEF.match(line):
            continue
        s = re.sub(r"<!--.*?-->", "", line)
        s = re.sub(r"!\[[^\]]*\]\([^)]*\)", "", s)           # image alt text is never wrapped
        s = re.sub(r"\[\^[^\]]*\]", "", s)                    # footnote marks
        s = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", s)        # link text stays, target goes
        s = re.sub(r"https?://\S+", "", s)
        s = re.sub(r"`[^`]*`", "", s)
        s = re.sub(r"<[^>]+>", " ", s)                        # tags and their attributes
        s = re.sub(r"\$\$.*?\$\$", "", s)
        yield n, s


def check(path):
    text = open(path, encoding="utf-8").read()
    lines = text.split("\n")
    defs, found = {}, []
    for n, line in enumerate(lines, 1):
        m = DEF.match(line)
        if m:
            term = m.group(1)
            if term in defs:
                found.append(("WARN", n, term, f"defined twice (first at line {defs[term]})"))
            defs[term] = n
    ok = set()
    for m in re.finditer(r"<!--\s*abbr-ok:\s*([^>]*?)\s*-->", text):
        ok.update(t.strip() for t in m.group(1).split(","))

    used, seen = set(), set()
    for n, s in strip_markdown(lines):
        for term in defs:
            if re.search(r"(?<![\w])" + re.escape(term) + r"(?![\w])", s):
                used.add(term)
        for m in TOKEN.finditer(s):
            tok = m.group(1)
            if tok in SKIP or tok in ok or tok in defs or tok in seen:
                continue
            if re.fullmatch(r"[IVXLC]+", tok):                # roman numerals
                continue
            if re.match(r"(RM|Rp|AU|NZ|HK|SG|CN|US|UK)\d", tok) or re.match(r"\d", tok):
                continue                                      # currency-prefixed amounts
            # PH/MT, KPR-nya, BPS-Statistics: every all-caps part must be defined, the rest is a suffix
            parts = [p for p in re.split(r"[/&-]", tok) if p and not p.isdigit()]
            caps = [p for p in parts if re.fullmatch(r"[A-Z][A-Z0-9]*s?", p)]
            if len(parts) > 1 and caps and all(p in defs for p in caps):
                continue
            if len(re.findall(r"[A-Z]", tok)) < 2:
                continue
            if re.match(r"\.[A-Za-z]", s[m.end():m.end() + 2]):
                continue                                      # GOV.UK: a domain name, not an abbreviation
            seen.add(tok)
            found.append(("ERROR", n, tok, "abbreviation without a *[%s]: definition" % tok))
        for m in SHORT.finditer(s):
            tok = m.group(1)
            if tok in defs or tok in ok or tok in seen:
                continue
            seen.add(tok)
            found.append(("ERROR", n, tok, "short form without a *[%s]: definition" % tok))
    for term, n in defs.items():
        if term not in used:
            found.append(("WARN", n, term, "defined but never used in the post"))
    return sorted(found, key=lambda f: (f[1], f[2]))


def main(paths):
    errors = 0
    for path in paths:
        print(f"== {path}")
        for level, n, term, msg in check(path):
            errors += level == "ERROR"
            print(f"  {level} line {n}: {term}: {msg}")
    print(f"{errors} ERROR" if errors else "no ERROR")
    return 1 if errors else 0


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    sys.exit(main(sys.argv[1:]))
