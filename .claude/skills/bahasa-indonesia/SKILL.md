---
name: bahasa-indonesia
description: Mandatory for every piece of Indonesian on this blog. Load it before writing, translating, rewriting, editing or reviewing any Indonesian text, however small - a post in id/, its title, description or keywords, a caption or alt text, an Indonesian string in _data/i18n.yml or _data/categories.yml, a plan or opening narrative in Indonesian, or a reply to Adjie in Indonesian. It fixes the one voice the blog uses (written Jakarta Indonesian, saya-kamu, the flow of an Indonesian opinion column), which words are casual and which are factual, the finance terms, how to italicise and explain foreign terms, the English habits to remove (calques, sentence-initial conjunctions, personified cities, note-style fragments, slogan copy), and the rigorous evaluator every Indonesian text must pass, with Adjie's own corrections as the reference.
---

# Bahasa Indonesia for this blog

**Mandatory.** Load this skill before you write or touch any Indonesian text in this repo.
It applies to a one-word fix too: most of Adjie's corrections were one or two words. It
works on top of `adjie-writing-style` (the moves, the stance); this skill decides the words
and the shape of the sentences, and it wins where the two disagree.

Read [`references/corrections.md`](references/corrections.md) every time. It is Adjie's
own before-and-after list, the best evidence of what he wants. When he corrects
Indonesian again, add the pair there (and a rule here if it is a new pattern). When a newer
correction contradicts an older one, the newer one wins: change the older rule.

Nothing in Indonesian is finished until it passes the evaluator: the script
[`scripts/cek.py`](scripts/cek.py), then the full read in
[`references/evaluator.md`](references/evaluator.md), done by someone who has not seen the
English (see "Evaluate before handing over").

## The root problem: an English writer, translated

Every mistake Adjie has flagged has one cause: the text was thought in English and then
put into Indonesian words. It gets worse when one agent writes both languages of a post in
one go, because the English sentences sit in context and pull the Indonesian into their
shape. So:

- **Think in Indonesian from the start.** The writer is an Indonesian columnist explaining
  a case to Indonesian readers, not a translator of an English article.
- **Never write Indonesian next to the English.** A bilingual post is written from a shared,
  language-neutral brief (headings' intent, points, data, sources) by a separate Indonesian
  writer who never reads the English draft. The flow lives in `ai-assisted-blog-post`,
  Step 3. If you must work alone, write the Indonesian first, from the brief, before any
  English prose for the post exists in your context.
- **The English is facts, not sentences.** When you only have an English source (an old
  post, a paper), read a paragraph, look away, and say its point in one Indonesian
  sentence the way you would say it to a friend in Jakarta. Write from that point, keeping
  the numbers, the case and the sources.
- **Examples may differ.** The Indonesian post may use its own characters, cities and
  examples (Jakarta vs Bali where the English says Perth vs Melbourne), as long as it
  carries the same message and every number is sourced. Choose what an Indonesian reader
  knows.
- **Read every sentence cold.** If it only makes sense because you know the English behind
  it, or if it back-translates word for word into a natural English sentence, rewrite it.

## One voice

Written Jakarta Indonesian with the flow of a good Indonesian opinion column or personal
essay: how an educated Jakartan writes to readers he respects. Whole sentences that link
into each other, warm and direct, with casual words for colour. There is no other dialect,
register preset or regional option.

- **Jakarta, not Betawi and not Jaksel slang.** The sentence frame is standard
  Indonesian; Jakarta casual words colour it. No regional languages (Javanese, Sundanese
  and so on) and no regional styles. If a post quotes someone who speaks one, quote them
  exactly and don't imitate it anywhere else.
- **saya and kamu.** Adjie is *saya*. The reader is *kamu*, and its possessive is *-mu*
  ("caramu memandang kekayaan", not "cara Anda memandang kekayaan"). Never *Anda*, never
  *gue/lo*, and never two address forms in one post. *Kita* and *mari kita* bring the
  reader along ("mari kita bahas Perth terlebih dahulu").
- **Particles sparingly.** *sih*, *kok*, *kan*, *dong*, *deh*, *nih* only where they do
  a job (a contrast, a shared assumption, a soft push), at most once in a paragraph.
- **Humble about his own work.** Adjie built the tools, but the text doesn't keep saying
  so (see "No bragging" below).

## Sentences that flow

English blog prose is built from short, self-contained sentences. Indonesian essay prose
links clauses into longer sentences with *yang*, *sehingga*, *karena*, *sementara*,
*padahal*, *meski*, and moves between paragraphs with a real transition. Write the
Indonesian way.

### Don't open sentences with a conjunction out of habit

English writers start sentences with *And*, *But*, *So*, *Because*. Carried into
Indonesian ("Tapi ...", "Dan ...", "Jadi ...", "Karena ..."), it chops the text into
pieces. The fixes, in order of preference:

1. **Join it to the sentence before:** "..., tetapi ...", "..., sehingga ...", "...,
   padahal ...".
2. **Open with a real transition that says how the ideas relate:** *Meski begitu*,
   *Sebaliknya*, *Artinya*, *Dengan kata lain*, *Pertanyaannya*, *Lain ceritanya dengan*,
   *Ditambah lagi*, *Itulah sebabnya*.
3. **Restructure** so the sentence starts with its subject.

| Wrong | Right |
| --- | --- |
| "Tapi ada pertanyaan kedua yang lebih dingin ..." | "Meski begitu, ada pertanyaan kedua yang lebih dingin ..." |
| "Dan saya akui: nasi goreng Rp20 ribuan itu rasanya memang lebih enak." | "Soal rasa, saya pun mengakui nasi goreng Rp20 ribuan di sini memang lebih nendang." |
| "Satu hal lagi, supaya adil." | "Ada satu hal lagi yang perlu diingat supaya perbandingannya tidak berat sebelah." |

Limits: *Dan*, *Tapi*, *Sehingga*, *Atau* never open a sentence in body text. *Namun*,
*Jadi* and *Karena* (as a whole subordinate clause: "Karena tidak mau sekadar beropini,
saya ...") at most once per section. A deliberate exception is the last heading's return to
the core question ("Jadi, sewa atau beli?"). `cek.py` counts them.

### No note-style shorthand

English bullet-point habits drop the subject, the verb and the connectors, which leaves
sentences that read like draft notes. Every sentence in a paragraph needs its subject, its
verb and its link to what came before.

| Wrong | Right |
| --- | --- |
| "Biar fair, bahas Perth dulu." | "Agar adil, mari kita bahas Perth terlebih dahulu." |
| "Sebelum masuk ke hitungan, tiga istilah dulu." | "Sebelum masuk ke hitungan, ada tiga istilah yang perlu kita pahami terlebih dahulu." |
| "Sampel ini bias." | "Tentu saja sampel ini tidak sepenuhnya mewakili populasi secara luas (ada bias)." |
| "Sekarang soal pembiayaan." | "Sekarang kita beralih ke soal pembiayaan." |
| "Saat suami dan istri sama-sama bergaji besar." (as the answer under a heading) | "Gabung lebih untung ketika suami dan istri sama-sama bergaji besar." |

Labels are fine where they are labels: a bold lead-in in a list, a caption, a chart title,
"**Perth, 30 tahun.**".

### No slogan copy

Two or three short contrasting sentences in a row ("Love is the heart's business. Taxes
are maths.") is the hook of American marketing and motivational writing. In an Indonesian
finance essay it reads as forced (*cringe*) and empty. Say it in one flowing compound
sentence; the punch comes from the idea, not from the full stops.

| Wrong | Right |
| --- | --- |
| "Cinta itu urusan hati. Pajak itu urusan hitungan. Jangan biarkan yang satu mengambil keputusan untuk yang lain." | "Urusan hati boleh saja diserahkan pada cinta, tetapi untuk urusan pajak, biarkan hitungan yang mengambil keputusan." |
| "Jangan mulai dari perasaan, dan jangan mulai dari harga nasi goreng. Mulai dari selisih." | "Kalau kamu sedang menimbang untuk pindah, mulailah dari selisih itu, bukan dari perasaan atau dari harga sepiring nasi goreng." |
| "Ini bukan restorannya serakah. Ini upahnya." | "..., dan penyebabnya bukan restoran yang serakah, melainkan upah yang tinggi." |
| "Yang satu leverage, yang satu bocor." | "Di Perth, utang ikut bekerja untuk pemiliknya, sementara di Jakarta utang justru menggerogoti kekayaan pemiliknya." |

A post may keep one short line for effect, once, after a long explanation. Not two in a
row, and never three.

### Transitions that build rapport

The personal essay holds its reader through closeness. Open a paragraph or a turn in the
argument the way a person talks to someone sitting across the table, not with a bare
label.

| Abrupt | Warm |
| --- | --- |
| "Sekarang pengakuan dulu." | "Sekarang, mari jujur-jujuran dulu." |
| "Nah, keberatannya: ..." | "Mungkin kamu akan menyanggah: ..." |
| "Balik ke Robert dan Vieri." | "Mari kembali ke Robert dan Vieri." |
| "Ini hitungan kasarnya." | "Hitungan kasarnya seperti ini." |

### Endings that land

The closing lines carry the post. Give the final thought room: one or two full sentences
that build to the point, with emphasis carried by the structure (*-lah*, *hanya ... yang*,
*pada akhirnya*), not by fragments.

- "Harga nasi goreng menentukan makan siangmu. Selisih antara gaji dan pengeluaran
  menentukan masa depanmu." → "Nasi goreng di Jakarta memang lebih murah dan lebih enak,
  tetapi harganya hanya menentukan menu makan siangmu hari ini. Selisih antara penghasilan
  dan pengeluaranlah yang pada akhirnya membentuk masa depanmu."

## Idiomatic diction

Choose the word an Indonesian columnist would pick, not the dictionary equivalent of the
English one. Lively native diction is what separates an essay from machine translation.

| Flat (translated) | Idiomatic |
| --- | --- |
| tabungan ... bisa jauh lebih besar | tabungan ... bisa jauh lebih tebal |
| yang paling tipis justru ... (the one with least margin) | yang paling megap-megap justru ... |
| kelihatan downgrade | kelihatannya seperti turun kelas |
| menandatangani cicilan | meneken cicilan |
| sebulan cuma 250 porsi | sebulan kamu cuma kebagian 250 porsi |
| ungkapan kecewa | luapan kekecewaan |
| menambah orang dari luar negeri | bertambah karena kedatangan orang dari luar negeri |
| harganya dilempar ke pembeli | biaya itu diteruskan ke pembeli |

### Idioms and fixed phrases

An English idiom translated word for word ("can't be priced", "priceless") becomes a
phrase that means something else in Indonesian: "gak bisa dikasih harga" sounds like a
market stall item without a price tag, not like something worth more than numbers. Use
the Indonesian fixed phrase: *tidak ternilai harganya*, *nilainya melampaui angka di atas
kertas*, *tidak bisa diukur dengan materi*. When no Indonesian idiom fits, say the meaning
plainly. A joke that doesn't travel gets a different joke.

### Places don't talk

"Perth says buy", "London thinks", "the market tells us" simplify data in English. In
Indonesian a city is a place: it cannot *bilang*, *berkata*, *menyarankan*, *bercerita*,
*butuh* or *membayar*. Name the actor (buyers, the market's conditions, the numbers) or
use a place adverbial.

| Wrong | Right |
| --- | --- |
| "Kenapa Perth bilang beli dan Jakarta bilang sewa" | "Di Perth lebih untung beli, di Jakarta lebih untung sewa" |
| "Kenapa satu kota bilang beli, kota lain bilang sewa?" | "Kenapa di satu kota lebih untung beli, di kota lain lebih untung sewa?" |
| "Jakarta bayarnya lebih sedikit." | "... dan di Jakarta imbalan itu lebih kecil." |
| "Perth butuh sekitar $210 ribu untuk mulai" | "Untuk membeli di Perth, kamu butuh sekitar $210 ribu" |
| "Melbourne atau Bali akan bercerita lain" | "Hasil untuk Melbourne atau Bali bisa berbeda" |
| "Apa kata tool tentang Perth?" | "Bagaimana hasil hitungan *tool* untuk Perth?" |

A state acting as a state is fine ("Australia menetapkan gaji minimum ...", "Indonesia
butuh lebih banyak insinyur"). So is an institution that does speak ("UBS mencatat",
"DJP mengingatkan"). A tool's card shows, not says: "Kartu ini menunjukkan ...".

## Calques to catch

Each line is a pattern Adjie corrected (examples in `references/corrections.md`).

| English shape | Wrong (calque) | Right |
| --- | --- | --- |
| "Here is how to ..." | "Begini cara mengujinya" | "Ini cara mengujinya" |
| "Here's how to read it:" | "Bacanya begini:" | "Cara bacanya begini:" (*begini* needs a real noun phrase in front of it) |
| "Strip away the noise and the question comes down to ..." | "Kalau semua gangguannya dibuang, pertanyaan uangnya tinggal ..." | "Kalau faktor-faktor lain dikesampingkan, pertanyaannya bisa dijawab lewat ..." |
| "... and I won't try" | "dan saya gak akan mencoba" | Say what the speaker can't do in context: "dan saya tidak dalam posisi untuk menilainya" |
| "can't be priced", "priceless" | "gak bisa dikasih harga" | "tidak ternilai harganya" |
| "I would not extrapolate it" | "saya gak akan mengira" | "saya gak akan kira" |
| "a far calmer 4.5%" | "jauh lebih tenang" | "jauh lebih moderat" (figurative adjectives on numbers become finance words: *moderat*, *konservatif*, *agresif*) |
| "it is a compass, not a calculator" | "anggap saja seperti kompas" | "anggap saja kompas" (*anggap* already makes it a comparison) |
| "households owned them" | "rumah tangganya memilikinya" | "sebagian besar rumah tangga punya rumah" (name the thing; no *-nya* chains standing for English pronouns) |
| "this is the part I have to be honest about" | "bagian yang harus saya jujurkan" | "di sinilah saya harus jujur" (don't invent *-kan* verbs to fit the English) |
| "a professional in Perth saves Rp32m" (a model result) | "menabung sekitar Rp32 juta" | "bisa menabung sekitar Rp32 juta" (a hypothetical or a model result takes *bisa*/*akan*, not a bare verb) |
| "the examples above are only three points" | "cuma tiga titik" | "cuma tiga jenis" (data points are *contoh*, *jenis* or *kasus*, never *titik*) |
| "out-earns its loan by about a point" | "satu poin di atas" | "satu persen di atas" (*poin* reads like a score) |
| "what the house earns" | "hasil rumah" | "imbal hasil rumah" (see the finance terms) |
| "a confession first" | "Sekarang pengakuan dulu." | "Sekarang, mari jujur-jujuran dulu." |
| "immigration country versus birth country" | "negara kelahiran" (means *country of birth*) | "tumbuh dari imigrasi versus tumbuh dari kelahiran" |
| "X, a.k.a. Y" | "PTKP a.k.a. ..." | "PTKP, alias ..." (Indonesian has *alias*) |
| "the card tells you which is cheaper" | "dia bilang cara mana yang lebih murah" | "kartu ini menunjukkan cara mana yang lebih murah" |

Also from the general rules for Indonesian:

- No *yang mana* or *di mana* as a relative pronoun (from *which*, *where*). Split the
  sentence, or use *yang*, *tempat*, *ketika*. ("negara tempat kita tinggal", not "negara
  di mana kita tinggal".)
- No heavy nominalisation: "mengecek", not "melakukan pengecekan"; "karena", not
  "dikarenakan oleh"; "ada", not "terdapat sebuah"; "untuk", not "dalam rangka untuk".
- No passive chains copied from English. Indonesian passive is natural (*dipotong
  kantornya*), but put the doer in when English leaves it out and the reader needs it.

## Foreign terms: italics and explanations

Keep a foreign term when it is the word people really use, or when the exact term matters
for the data (an English term is better than an Indonesian one nobody uses). Mark it and
make it understandable:

- **Italics for every foreign word** that Indonesian has not absorbed: *tool*, *input*,
  *take-home pay*, *rental yield*, *leverage*, *opportunity cost*, *breakeven*, *values*,
  *market*, *hot*, *fixed*, *floating*, *flat*, *deal*, *spreadsheet*, *screenshot*,
  *browser*, *freelance*, *stress test*, *apple to apple*, *resident*, *work permit*. Every
  occurrence, in body text, lists, tables and link text (`[*tool* Pisah vs Gabung](...)`).
  A suffix stays roman after a hyphen: `*tool*-nya`, `*input*-nya`, `*browser*-mu`.
  Inside a bold label: `**_Leverage_.**`. In an HTML caption: `<em>floating</em>`. Alt
  text, `title:` and `description:` cannot hold italics: write them without.
- **Not italic:** words in KBBI (*versus*, *data*, *investasi*, *properti*), names of
  institutions, programmes, products and tools (Reserve Bank of Australia, Progressive Wage
  Model, Employment Pass, Cost of Living Comparator, Sensitivity Analysis tool), and the
  tools' own UI labels, which are bold (**Quick Start**, **Suku Bunga Bebas Risiko**).
- **Explain a very foreign term at first mention,** in parentheses or with *alias*, then
  use it bare: *capital freedom* (kebebasan menaruh modal), *replacement level* (sekitar
  2,1 anak per perempuan, tingkat yang membuat jumlah penduduk tetap stabil), *rental
  yield* alias sewa setahun dibagi harga rumah.
- **Weave foreign administrative terms into the sentence.** A foreign country's system
  confuses readers when its terms are dropped in bare. Say what the thing is and what it
  does for the comparison, in the flow of the sentence:
  - "Setelah pajak resident dan Medicare levy, take-home sekitar A$3.769" → "Setelah
    dipotong pajak penghasilan untuk penduduk pajak Australia (*resident tax*) dan
    *Medicare levy* (iuran 2% untuk layanan kesehatan publik), gaji bersihnya sekitar
    A$3.769 per bulan."
  - "Progressive Wage Model (PWM), jenjang paling bawah pekerja kebersihan, S$2.080" →
    "Singapura tidak punya upah minimum nasional. Yang ada adalah Progressive Wage Model
    (PWM), skema upah minimum per sektor yang naik mengikuti jenjang keterampilan."
  - "batas gaji minimum visa kerja terampil (dulu TSMIT, sekarang Core Skills Income
    Threshold)" → "untuk visa kerja terampil, Australia menetapkan gaji minimum yang
    disebut Core Skills Income Threshold (CSIT), dulu dikenal sebagai TSMIT."
  - "CPF 20%" → "iuran CPF (Central Provident Fund, tabungan pensiun wajib) sebesar 20%".
- **Prefer the Indonesian word where Indonesians really use it:** *pengembang* (not
  *developer*), *gaji bersih* for take-home in running text (with *take-home pay* glossed
  once), *layanan publik* (not *public service*), *turun kelas* (not *downgrade*), *izin
  kerja* (with *work permit* when the exact type matters), *KPR* (not *mortgage*), *agar
  adil* or *supaya adil* (not *biar fair* in narrative; keep *biar fair* for quoted
  speech).

Don't translate a term just because a dictionary word exists: *values* (not *nilai
hidup*), *tool* (for the Adjie Brotools tools, never *alat*), *opportunity cost* (not
*biaya peluang*), *input* (not *masukan*), *market* and *hot* in a casual sentence ("Itu
*market* yang sangat *hot*", not "pasar yang sangat panas"), *holistic thinking*, *liquid
asset thinking*, *breakeven*, *leverage*, *apple to apple* (not *apel dengan apel*),
*deal*, *Stress Test* and *Quick Start* when they are the tool's labels.

Spelling with English words: a suffix takes a hyphen ("*input*-nya", "*tool*-nya",
"KPR-nya", "*browser*-mu"); an Indonesian prefix on an English verb takes one too
("di-*deploy*"). Prefer an Indonesian verb when one is natural ("menginvestasikan").

## No bragging

"My tool" or "the calculator I built" does not become "*buatan saya*" or "*milik saya*".
In Indonesian that sounds arrogant. Just name it: "Di *tool* Sewa vs Beli Rumah, ...".
Say Adjie made something only when the sentence is about the making ("Saya membuat *tool*
ini sebagai ekonom berlatar perbankan").

## Casual words versus factual words

The blog runs on two layers, and a phrase stays in one of them.

- **Casual layer:** asides, opinions, jokes, quoted speech, a reader's inner voice,
  question headings ("Gimana caramu memandang kekayaan?").
- **Factual layer:** definitions, rules, numbers being stated, how-to steps, tables,
  footnotes, the disclaimer at the end, a quoted legal or official term.

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
| supaya, agar | biar |
| mengira, berpikir, mengatakan | kira, pikir, bilang (bare verb after *gak*, *akan*, *mau*, *bakal*) |

The narrative is mostly the neutral column: *tidak*, *hanya*, *ingin*, *tetapi*, with
casual words (*gak*, *cuma*, *bikin*, *punya*) used where the sentence is an aside or an
opinion. Rules, steps, tables and footnotes use *tidak*. The stronger casual forms
(*aja*, *udah*, *-in* verbs, particles) belong in quoted speech and asides.

- **Keep a phrase consistent.** Casual verb with casual particle: "tunjukin aja", not
  "tunjukkan saja" in a casual quote, and not "tunjukin saja".
- **Quoted speech is fully casual.** "dari *tunjukin aja* sampai *biar saya bongkar*".

### *gak* never stands alone

*gak* must be followed by the word it negates: "gak mau", "gak bisa", "gak jadi beli".
When the negation stands on its own (an answer, the end of a sentence, an elliptical
"if not"), use *enggak* in a casual spot or *tidak* in a factual one.

- "Sewa menang kalau gak." → "Sewa menang kalau tidak."
- "Kalau gak, setiap rupiah pinjaman jadi beban." → "Kalau tidak, ..."
- "Tapi apakah semua orang cocok kabur? Gak." → "Tentu tidak."

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
| fixed / floating rate | *fixed*, *floating* | tetap, mengambang |
| rental yield | *rental yield*, alias sewa setahun dibagi harga | hasil sewa |
| percentage point (casual prose) | persen | poin |
| take-home pay | gaji bersih, glossed once as *take-home pay* | gaji bersih dibawa pulang, a bare "take-home" |
| home equity | ekuitas rumah (nilai rumah dikurangi sisa utang KPR) at first mention | |
| property developer | pengembang | developer |
| tax terms | the official Indonesian term (PTKP, PKP, SPT, kurang bayar) | an English gloss |

Use the tool's own labels exactly as the tool shows them (**Quick Start**, **Suku Bunga
Bebas Risiko**, **Uang tunai**), even when the prose around them is casual.

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
- A title or a heading that changes keeps the slug (see `CLAUDE.md`); redraw the post's
  social card with `node _build/og.mjs` when the title changes.

## Evaluate before handing over

Writing and judging are two jobs. The writer cannot see their own calques, and an agent
that has read the English twin reads a calque as fine. So:

1. **Run the script** on every Indonesian file you touched:

   ```sh
   python3 .claude/skills/bahasa-indonesia/scripts/cek.py id/_posts/<post>.md
   ```

   Fix every ERROR. Every REVIEW line is a sentence to read again and fix unless the
   choice is deliberate and defensible.
2. **Run the evaluator** in [`references/evaluator.md`](references/evaluator.md): a
   sentence-by-sentence read through ten lenses, with a written verdict. For a new post or
   a rewrite, the evaluator is a fresh agent that has not seen the English (spawn one with
   the prompt in that file). For a small edit, run it yourself on the changed paragraphs
   and the ones around them.
3. **Loop until it passes:** apply the findings, run the script again, and send the
   changed paragraphs back to the evaluator until the verdict is LULUS. Don't hand the
   text to Adjie, commit or push before then.
4. When Adjie corrects something the evaluator passed, add the pair to
   `references/corrections.md`, the rule here, and the pattern to `scripts/cek.py` if a
   regex can catch it.
