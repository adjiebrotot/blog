---
name: bahasa-indonesia
description: Mandatory for every piece of Indonesian on this blog. Load it before writing, translating, rewriting, editing or reviewing any Indonesian text, however small - a post in id/, its title, description or keywords, a caption or alt text, an Indonesian string in _data/i18n.yml or _data/categories.yml, a plan or opening narrative in Indonesian, or a reply to Adjie in Indonesian. It fixes the one voice the blog uses (written Jakarta Indonesian, saya-kamu), which words are casual and which are factual, the finance terms, the English terms to keep, and the calques that come from translating the English post, with Adjie's own corrections as the reference.
---

# Bahasa Indonesia for this blog

**Mandatory.** Load this skill before you write or touch any Indonesian text in this repo,
and run the checklist at the end before you hand it over. This applies to a one-word fix
too: most of Adjie's corrections were one or two words. It works on top of
`adjie-writing-style` (the moves, the stance, the rhythm); this skill decides the words.

Read [`references/corrections.md`](references/corrections.md) every time. It is Adjie's
own before-and-after list, the best evidence of what he wants. When he corrects
Indonesian again, add the pair there (and a rule here if it is a new pattern).

## One voice

Written Jakarta Indonesian: how an educated Jakartan talks to a friend he respects,
written down. There is no other dialect, register preset or regional option.

- **Jakarta, not Betawi and not Jaksel slang.** The sentence frame is standard
  Indonesian; Jakarta casual words colour it. No regional languages (Javanese, Sundanese
  and so on) and no regional styles. If a post quotes someone who speaks one, quote them
  exactly and don't imitate it anywhere else.
- **saya and kamu.** Adjie is *saya*. The reader is *kamu*, and its possessive is *-mu*
  ("caramu memandang kekayaan", not "cara Anda memandang kekayaan"). Never *Anda*, never
  *gue/lo*, and never two address forms in one post.
- **Particles sparingly.** *sih*, *kok*, *kan*, *dong*, *deh*, *nih* only where they do
  a job (a contrast, a shared assumption, a soft push), at most once in a paragraph.
- **Humble about his own work.** Adjie built the tools, but the text doesn't keep saying
  so (see "No bragging" below).

## Write it native, never translated

Most Indonesian posts here have an English twin. The English is a source of facts, not of
sentences. Each mistake Adjie flagged came from following the English word by word.

1. Read one English paragraph, then look away and say its point in one Indonesian
   sentence, the way you would say it to a friend in Jakarta.
2. Write the paragraph from that point, keeping the numbers, the case and the sources.
3. Read every sentence cold. If it only makes sense because you know the English behind
   it, rewrite it.

Never keep the English sentence structure: subject-verb-object with an English idiom
dropped into Indonesian words is the main source of *bahasa terjemahan*.

## Calques to catch

Each line is a pattern Adjie corrected (examples in `references/corrections.md`).

| English shape | Wrong (calque) | Right |
| --- | --- | --- |
| "Here is how to ..." | "Begini cara mengujinya" | "Ini cara mengujinya" |
| "Here's how to read it:" | "Bacanya begini:" | "Cara bacanya begini:" (*begini* needs a real noun phrase in front of it) |
| "Strip away the noise and the question comes down to ..." | "Kalau semua gangguannya dibuang, pertanyaan uangnya tinggal ..." | "Kalau faktor-faktor lain dibuang, pertanyaannya bisa dijawab dengan ..." |
| "... and I won't try" | "dan saya gak akan mencoba" | Say what the speaker can't do in context: "dan saya gak bisa menilai" |
| "I would not extrapolate it" | "saya gak akan mengira" | "saya gak akan kira" |
| "a far calmer 4.5%" | "jauh lebih tenang" | "jauh lebih moderat" (figurative adjectives on numbers become finance words: *moderat*, *konservatif*, *agresif*) |
| "it is a compass, not a calculator" | "anggap saja seperti kompas" | "anggap saja kompas" (*anggap* already makes it a comparison) |
| "households owned them" | "rumah tangganya memilikinya" | "sebagian besar rumah tangga punya rumah" (name the thing; no *-nya* chains standing for English pronouns) |
| "this is the part I have to be honest about" | "bagian yang harus saya jujurkan" | "bagian yang saya harus jujur" (don't invent *-kan* verbs to fit the English) |
| "a professional in Perth saves Rp32m" (a model result) | "menabung sekitar Rp32 juta" | "bisa menabung sekitar Rp32 juta" (a hypothetical or a model result takes *bisa*/*akan*, not a bare verb) |
| "the examples above are only three points" | "cuma tiga titik" | "cuma tiga jenis" (data points are *contoh*, *jenis* or *kasus*, never *titik*) |
| "out-earns its loan by about a point" | "satu poin di atas" | "satu persen di atas" (*poin* reads like a score) |
| "what the house earns" | "hasil rumah" | "imbal hasil rumah" (see the finance terms) |

Also from the general rules for Indonesian:

- No *yang mana* or *di mana* as a relative pronoun (from *which*, *where*). Split the
  sentence, or use *yang*, *tempat*, *ketika*.
- No heavy nominalisation: "mengecek", not "melakukan pengecekan"; "karena", not
  "dikarenakan oleh"; "ada", not "terdapat sebuah"; "untuk", not "dalam rangka untuk".
- No passive chains copied from English. Indonesian passive is natural (*dipotong
  kantornya*), but put the doer in when English leaves it out and the reader needs it.

## No bragging

"My tool" or "the calculator I built" does not become "*buatan saya*" or "*milik saya*".
In Indonesian that sounds arrogant. Just name it: "Di tool Sewa vs Beli Rumah, ...".
Say Adjie made something only when the sentence is about the making ("Itulah alasan saya
membuat tool ini", "Saya membuat tool ini sebagai ekonom berlatar perbankan").

## Casual words versus factual words

The blog runs on two layers, and a phrase stays in one of them.

- **Casual layer:** asides, opinions, jokes, transitions, quoted speech, a reader's inner
  voice, question headings ("Gimana caramu memandang kekayaan?").
- **Factual layer:** definitions, rules, numbers being stated, how-to steps, the
  disclaimer at the end, a quoted legal or official term.

| Factual / neutral | Casual |
| --- | --- |
| tidak | gak (inside a sentence); enggak (when it stands alone) |
| saja | aja |
| tunjukkan, buatkan (-kan) | tunjukin, bikinin (-in) |
| membuat | bikin |
| memiliki | punya |
| ingin | pengin |
| hanya | cuma |
| bagaimana | gimana |
| supaya | biar |
| mengira, berpikir, mengatakan | kira, pikir, bilang (bare verb after *gak*, *akan*, *mau*, *bakal*) |

The blog's default narrative already mixes in *gak*, *cuma*, *bikin*, *biar*, *pengin*,
*tapi*. The stronger casual forms (*aja*, *udah*, *-in* verbs, particles) belong in
quoted speech and asides.

- **Keep a phrase consistent.** Casual verb with casual particle: "tunjukin aja", not
  "tunjukkan saja" in a casual quote, and not "tunjukin saja".
- **Quoted speech is fully casual.** "dari *tunjukin aja* sampai *biar saya bongkar*".

### *gak* never stands alone

*gak* must be followed by the word it negates: "gak mau", "gak bisa", "gak jadi beli".
When the negation stands on its own (an answer, the end of a sentence, an elliptical
"if not"), use *enggak* in a casual spot or *tidak* in a factual one.

- "Sewa menang kalau gak." → "Sewa menang kalau tidak."
- "Kalau gak, setiap rupiah pinjaman jadi beban." → "Kalau tidak, ..."
- "Tapi apakah semua orang cocok kabur? Gak." → "... Enggak."

Use *gak* for the casual in-sentence form, *enggak* for the casual standalone form. Not
*nggak* or *ga*.

## Finance terms

| Concept | Say | Not |
| --- | --- | --- |
| return, what something earns | imbal hasil | hasil |
| return on price growth | imbal hasil kenaikan harga | hasil harga |
| the full price (leverage base) | harga dasar | harga |
| mortgage, mortgage rate | KPR, bunga KPR ("Berapa bunga KPR-nya?") | cost of money, harga uang |
| down payment | DP | uang muka, except the tool's own label "Uang Muka (DP)" |
| fixed / floating rate | fixed, floating | tetap, mengambang |
| rental yield | rental yield, a.k.a. sewa setahun dibagi harga | hasil sewa |
| percentage point (casual prose) | persen | poin |
| take-home pay | take-home | gaji bersih dibawa pulang |
| tax terms | the official Indonesian term (PTKP, PKP, SPT, kurang bayar) | an English gloss |

Use the tool's own labels exactly as the tool shows them (**Quick Start**, **Suku Bunga
Bebas Risiko**, **Uang tunai**), even when the prose around them is casual.

## Keep English where it sounds better

Don't translate a term just because a dictionary word exists. Jakartans say these in
English, so the blog does: *values* (not *nilai hidup*), *tool* (for the Adjie Brotools
tools, never *alat*), *opportunity cost* (not *biaya peluang*), *input* (not *masukan*),
*market* and *hot* in a casual sentence ("Itu market yang sangat hot", not "pasar yang
sangat panas"), *holistic thinking*, *liquid asset thinking*, *breakeven*, *leverage*,
*apple to apple* (not *apel dengan apel*), *versus* (not *lawan*), *deal*, *downgrade*,
*Stress Test*, *Quick Start*.

But don't keep English where Indonesians already say something else: "biar fair" (not
"keberatan yang wajar" for "a fair objection"), "batasannya" (not "batas-batas yang
jujur"), *KPR* (not *mortgage*).

Spelling with English words: a suffix takes a hyphen ("input-nya", "tool-nya",
"KPR-nya", "browser-mu"); an Indonesian prefix on an English verb takes one too
("di-deploy"). Prefer an Indonesian verb when one is natural ("menginvestasikan").

## Numbers and format

- Decimal comma, thousands dot: 3,95%, Rp1,27 miliar, A$855.000.
- Rupiah: follow the post's existing style (*Rp32 juta* or *Rp 1,27 miliar*) and keep it
  the same through the post.
- *juta*, *miliar*, *triliun* in words; *ribu* in words after a currency in casual prose
  ("A$850 ribu").
- Dates: "17 Oktober 2026".
- Never change code, URLs, front matter keys, KaTeX, Mermaid or embed parameters for
  language reasons. Translate only the prose and the human-readable labels around them.

## Blog rules that apply in Indonesian too

- No em-dashes (colon, comma, parentheses or a full stop instead).
- Every UI string in both languages lives in `_data/i18n.yml`.
- Idioms must make sense in Indonesian. "Masukannya yang milik tempat itu" is a
  word-for-word of the English; "Bedanya ada di input-nya, dan input itu ikut kotanya" is
  what a person says. A joke that doesn't travel gets a different joke.

## Check before handing over

Go through the Indonesian text sentence by sentence:

1. Would a Jakartan say this sentence out loud to a friend? If it only makes sense with
   the English in mind, rewrite it.
2. *saya-kamu* all the way through, no *Anda*, no *gue/lo*.
3. No *gak* standing alone; *enggak* or *tidak* there instead.
4. Each phrase in one layer: casual words in casual spots, factual words in factual ones,
   no "tunjukin saja".
5. No *buatan saya* or similar credit unless the sentence is about making the thing.
6. Finance terms from the table (*imbal hasil*, *bunga KPR*, *persen*).
7. Hypotheticals and model results carry *bisa* or *akan*.
8. No invented affixed words (*jujurkan*), no *-nya* chains, no *yang mana*/*di mana*.
9. No em-dashes, numbers in Indonesian format, code and URLs untouched.
10. Compare against `references/corrections.md`: none of those mistakes is back.
