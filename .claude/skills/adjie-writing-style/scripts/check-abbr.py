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
- ERROR: a definition that is not needed, so the tooltip is clutter: a physical or
  currency unit (MW, km, NOK, RMB, CN as in CN¥), an everyday term every reader of that
  language already knows (DPR, UU, PNS, HP, S2 in Indonesian; PM, MP, EU, CEO in English),
  or a code that abbreviates nothing (golongan IV/e). Delete the `*[TERM]:` line.
- REVIEW: a defined term used more than 3 times. Ask whether it is a generic term that even
  the least specialised reader knows; if so, delete its definition (the rule of thumb in
  CLAUDE.md, "Abbreviations").
- WARN: a definition the post never uses (stale), or a definition written twice.

Not checked, on purpose: currency symbols and number suffixes (Rp, A$, 850k, 1.27bn), roman
numerals, and mixed-case short forms such as Kemenkeu or MaPS. Those are the writer's call, so
read the post once for them. The language comes from the path (`id/` is Indonesian,
anything else English). Exit code 1 if any ERROR.
"""
import re
import sys

# Lowercase short forms the all-caps scan cannot see. Add to this list when a new one turns up.
SHORT_FORMS = ["dkk", "dsb", "dst", "e.g", "i.e", "approx", "yg", "dgn"]
# Markers and labels that are not abbreviations of anything the reader needs explained, and
# abbreviations so obvious that a tooltip is clutter (vs, a.k.a, dll are not in SHORT_FORMS).
SKIP = {"TOC", "NOTE", "TIP", "IMPORTANT", "WARNING", "CAUTION",
        "US", "UK", "AS", "TV", "PDF", "SUV", "SUVs", "ID", "OK", "AI"}
# Physical and currency units: never defined, in any language.
UNITS = {
    # currency codes and prefixes
    "IDR", "USD", "AUD", "SGD", "MYR", "EUR", "GBP", "JPY", "CNY", "RMB", "HKD", "NZD",
    "THB", "PHP", "VND", "INR", "KRW", "CAD", "CHF", "NOK", "SEK", "DKK", "TWD", "BRL",
    "CN",  # as in CN¥ (other prefixes, A$ S$ HK$, are caught by the amount rule)
    # physical units
    "km", "cm", "mm", "m", "kg", "g", "ha", "km2", "m2", "MW", "GW", "TW", "kW", "kWh",
    "MWh", "GWh", "TWh", "kV", "Hz", "MHz", "GHz", "KB", "MB", "GB", "TB", "mph", "kph",
    "rpm", "psi", "dB", "mAh",
}
# Everyday terms the readers of each language already know: a tooltip on them is clutter.
# Add a term here when it appears often and every reader knows it (CLAUDE.md, "Abbreviations").
EVERYDAY_ANY = {"UN", "EU", "ASEAN", "COVID", "CNN", "CNBC", "BBC", "FAQ", "CEO", "NATO",
                "ATM", "SMS", "GPS", "USB", "DIY", "VIP", "HR", "IT"}
EVERYDAY = {
    "id": EVERYDAY_ANY | {
        "DPR", "MPR", "UU", "PNS", "ASN", "HP", "S1", "S2", "S3", "SD", "SMP", "SMA", "SMK",
        "KTP", "SIM", "NIK", "BUMN", "PT", "CV", "Tbk", "RI", "TNI", "Polri", "KRL", "MRT",
        "LRT", "BBM", "PHK", "UMKM", "DKI", "BPJS", "PLN", "LSM", "DP", "KPR", "PBB", "WNI",
        "WNA", "PDB", "HI", "Pemda", "pemda", "Plt", "Plt.", "Presiden", "BPS", "APBN",
        "Jabodetabek", "IKN", "KAI", "NPWP",
    },
    "en": EVERYDAY_ANY | {"PM", "MP", "MPs", "NGO", "NGOs", "GDP"},
}
# Codes that abbreviate nothing: a civil-service grade (golongan IV/e, III/a).
NOT_ABBR = re.compile(r"(?:I|II|III|IV)/[a-e]")

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


def lang_of(path):
    return "id" if re.search(r"(^|/)id/", path) else "en"


def not_needed(term, lang):
    if term in SKIP or term in UNITS or term in EVERYDAY[lang] or NOT_ABBR.fullmatch(term):
        return True
    return False


def check(path):
    lang = lang_of(path)
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

    used, seen, count = set(), set(), {}
    for n, s in strip_markdown(lines):
        for term in defs:
            k = len(re.findall(r"(?<![\w])" + re.escape(term) + r"(?![\w])", s))
            if k:
                used.add(term)
                count[term] = count.get(term, 0) + k
        for m in TOKEN.finditer(s):
            tok = m.group(1)
            if tok in SKIP or tok in ok or tok in defs or tok in seen or not_needed(tok, lang):
                continue
            if NOT_ABBR.match(tok):
                continue
            if re.fullmatch(r"[IVXLC]+", tok):                # roman numerals
                continue
            if re.match(r"(RM|Rp|AU|NZ|HK|SG|CN|US|UK)\d", tok) or re.match(r"\d", tok):
                continue                                      # currency-prefixed amounts
            # PH/MT, KPR-nya, BPS-Statistics: every all-caps part must be defined, the rest is a suffix
            parts = [p for p in re.split(r"[/&-]", tok) if p and not p.isdigit()]
            caps = [p for p in parts if re.fullmatch(r"[A-Z][A-Z0-9]*s?", p)]
            if len(parts) > 1 and caps and all(p in defs or not_needed(p, lang) for p in caps):
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
        if not_needed(term, lang):
            found.append(("ERROR", n, term, "definition not needed (a unit, an everyday "
                          "term or not an abbreviation): delete this line"))
        elif count.get(term, 0) > 3:
            found.append(("REVIEW", n, term, f"used {count[term]} times: if every reader "
                          "knows it, delete the definition"))
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
