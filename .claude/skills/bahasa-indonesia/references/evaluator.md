# Indonesian evaluator

The rigorous check every Indonesian text on this blog passes before it reaches Adjie, a
commit or a push. Its one question: **does this read as if an Indonesian columnist wrote
it, or as an English article put into Indonesian words?** Anything that sounds translated
is a finding, even if it is grammatical.

## Who runs it

- **A fresh agent for a new post or a rewrite.** The evaluator must not be the writer, and
  must not have read the English twin, the English plan or the brief's English wording: an
  agent that knows the English reads a calque as normal. Give it only the Indonesian file
  and this skill.
- **Yourself, for a small edit:** the changed paragraphs and one paragraph either side.
- **On Sonnet.** Spawn the evaluator agent with `model: "sonnet"`; the main context
  (Opus) only orchestrates and applies the findings.
- **Report fat as well as calques.** A sentence that piles on detail the argument does not
  use (a side example's opening date, length, stations, ridership or funder) is a
  *wajib* finding: propose deleting it (`adjie-writing-style`, "Every sentence earns its
  place"). So is an opening that introduces an invented character or a personified place
  when the brief did not ask for one.

Prompt for the evaluator agent (fill in the path):

> You are the Indonesian evaluator for blog.adjiebrotots.com. Do not read any file in
> `en/` and do not look for an English version of this post. Read
> `.claude/skills/bahasa-indonesia/SKILL.md`, `references/corrections.md` and
> `references/evaluator.md` in that skill, then evaluate `<id/_posts/....md>` exactly as
> `evaluator.md` describes. Be strict: when in doubt, report it. Do not edit the file.
> Return the report in the format of `evaluator.md`.

## Preference-aware judgement

Keep the ten lenses and native-language checks. Read `references/word-preferences.md`
and the shared voice preference reference. Apply explicit approvals in their recorded
contexts. Do not invent author selections or generalise one choice globally.

The column and back-translation tests are diagnostic prompts, not standalone proof of an
error. For an uncertain acceptable word or tone, report a **pilihan Adjie** with actual
short alternatives, identical facts/conditions, and the trade-off. Ask through the
orchestrator; do not edit or log a preference yourself. A plain word is not an error solely
because a livelier synonym exists. An author-approved contextual exception takes priority
over an older style preference; technical meaning and genuine clarity remain protected.

Retain genuine language rules and established corrections. Do not remove conjunction,
fragment or register guidance wholesale. If an explicit choice conflicts with a style-only
rule, have the orchestrator record a scoped exception and keep rule/checker guidance in
sync. Pending optional word choices alone do not block publication of acceptable text;
uncertain meaning or a necessary unresolved rule conflict does require clarification.

## Step 1: the script

```sh
python3 .claude/skills/bahasa-indonesia/scripts/cek.py <file>
```

Every ERROR is a *wajib* finding unless a recorded author-approved style-only exception
applies and the conflicting rule/checker is updated consistently. Accuracy exceptions
are not permitted. Read every REVIEW line in its paragraph and decide: a
finding, or a deliberate choice (say which and why in the report). The script only finds
patterns; a clean run proves nothing about flow or diction.

## Step 2: the read

Read the whole text once for the argument, then again **paragraph by paragraph, sentence by
sentence**, including the title, description, TL;DR, headings, list items, table cells,
captions, alt text and footnotes. For each sentence ask the two tests, then the ten lenses.

**The two tests**

1. **The column test.** Would this sentence appear, unchanged, in a Kompas or Tirto opinion
   column by an educated Jakartan? If an editor there would rewrite it, it is a finding.
2. **The back-translation test.** Translate the sentence word for word into English. If the
   result is a natural English sentence, the Indonesian was probably built from English:
   look hard at its structure, its idiom and its subject.

**The ten lenses** (report each finding under one of them)

1. **Diksi.** Is there a livelier, more idiomatic word a native writer would choose?
   (*lebih tebal* for savings, *megap-megap* for the one barely coping, *turun kelas*,
   *meneken*.) Flat dictionary equivalents warrant inspection; acceptable alternative diction is a suggestion or author choice, not automatically an error.
2. **Transisi dan kedekatan.** Does each paragraph and each turn open with a transition
   that builds rapport ("Sekarang, mari jujur-jujuran dulu", "Mungkin kamu akan
   menyanggah"), or does it start abruptly with a label?
3. **Istilah asing dan teknis.** Every foreign word in italics (except names, KBBI words and
   tool labels). A very foreign term explained at first mention. A foreign administrative
   term (*take-home pay*, *resident tax*, Progressive Wage Model, Core Skills Income
   Threshold) woven into the sentence with what it is and why it matters, not dropped in
   bare.
4. **Penekanan retoris.** Do the rhetorical lines and the closing paragraph land? The
   ending should fit the approved intention in natural full sentences. A memorable
   rhetorical point is optional; do not insert a slogan merely to pass the evaluator.
5. **Calque struktur.** English word order, English subject-verb-object frames, invented
   affixed words, *-nya* chains standing for English pronouns, *yang mana*/*di mana* as
   relatives, heavy nominalisation, bare verbs where a model result needs *bisa*/*akan*.
6. **Konjungsi di awal kalimat.** *Dan*, *Tapi*, *Sehingga*, *Atau* opening a sentence in
   body text; *Namun*, *Jadi*, *Karena* more than once in a section; any paragraph with two.
7. **Personifikasi.** A city, a market, a chart, a card or a compass that *bilang*,
   *menyarankan*, *bercerita*, *butuh* or *membayar*.
8. **Idiom literal.** An English idiom or fixed phrase translated word for word ("gak bisa
   dikasih harga", "di dua ujung", "makan waktu" where "butuh waktu" is meant).
9. **Gaya copywriting.** Two or three short contrasting sentences in a row, slogans,
   motivational hooks. One flowing compound sentence instead.
10. **Elipsis dan gaya catatan.** A sentence missing its subject, verb or connector that
    reads like a note ("Biar fair, bahas Perth dulu.", "tiga istilah dulu"). Labels in
    lists, captions and table cells are fine.

**Also check** the house rules: *saya-kamu* only; *gak* never standing alone; casual and
factual words each in their layer; finance terms from the table (*imbal hasil*, *bunga
KPR*, *persen* versus *poin persentase*); no *buatan saya*; numbers in Indonesian format; no em-dashes; none of the
mistakes in `corrections.md` is back. Every pointer (*di bawah*, *di atas*, *tadi*,
*seperti yang sudah saya jelaskan*, *tabel itu*, *contoh tadi*, *kurs tadi*) points at
something in the same `##` or `###` section, in that direction, or at a whole section named
by its heading (`adjie-writing-style`, "Point only at what is in the same section"); one
that reaches into another section is *wajib*, and its *Usulan* states the fact without the
pointer. A suggestion of yours must not add such a pointer either. And the meaning: a rewrite must not change a number,
a claim, a source or the post's verdict.

## Step 3: the report

Write it in Indonesian, in this format.

```markdown
# Evaluasi: <file>

**Vonis:** LULUS | BELUM LULUS
**Cakupan:** <n> paragraf, <n> butir daftar, <n> sel tabel, <n> catatan kaki dibaca
**Skrip:** <n> ERROR, <n> REVIEW (<n> jadi temuan, <n> disengaja: alasan singkat)

| # | Baris | Lensa | Tingkat | Kutipan | Usulan | Alasan |
|---|---|---|---|---|---|---|
| 1 | 21 | 10 Elipsis | wajib | "Biar fair, bahas Perth dulu." | "Agar adil, mari kita bahas Perth terlebih dahulu." | Tanpa subjek, terbaca seperti catatan. |

**Pola berulang:** <a pattern that shows up more than twice, so the writer fixes the
habit, not only the instances>
```

- **wajib**: a rule of the skill is broken, or the sentence has a specific idiomatic, clarity or meaning defect revealed by the tests. The
  verdict is BELUM LULUS while any *wajib* finding is open.
- **saran**: the sentence is acceptable, but a better native option exists.
- Every *Usulan* is a complete replacement sentence that keeps the numbers and the claim,
  so the writer can apply it as it is.
- Report coverage honestly. A report that skips the tables, captions or footnotes is not a
  pass.

## Step 4: the loop

The writer (or the main agent) applies every *wajib* finding and the *saran* it agrees
with, runs the script again, and sends the changed paragraphs back. Don't paste a
suggestion in blindly: read the new sentence together with the one before and after it,
because a pasted fix often repeats a word or a fact from its neighbour (the second round on
the first three posts found exactly that). The evaluator checks
those paragraphs and the ones around them, and issues a new verdict. Repeat until LULUS.
If the writer disagrees with a *wajib* finding after two rounds, list the disagreement for
Adjie in the delivery message instead of looping further.

### Preference choices in the report

Add a separate table where needed: passage/line, existing wording, alternative wording,
trade-off, already-approved reference ID (if any), and status: ask / retain acceptable
wording / explicit approval required to change a rule. Include a **pilihan Adjie** category
beside wajib and saran. No fabricated choice, inferred preference from silence, or automatic
promotion of your suggestion. All replacements preserve evidence classes and material
conditions under the shared editorial safeguards. The orchestrator saves explicit choices.
