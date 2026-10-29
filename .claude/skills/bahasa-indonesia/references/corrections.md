# Adjie's corrections

Adjie's own fixes to Indonesian on this blog, with the reason behind each. This is the
reference for what natural means here: read it before writing, and check a draft against
it. When he corrects something new, add the pair under the post, with the reason in his
words where he gave one, and add a rule to `SKILL.md` if the pattern is new.

## Sewa atau beli rumah (October 2026)

Translated too closely from the English twin, `rent-vs-buy-calculator-explained`.

| Before | After | Why |
| --- | --- | --- |
| hasil rumah | imbal hasil rumah | *Return* is *imbal hasil*. *Hasil* alone is just "result". |
| Begini cara mengujinya sendiri | Ini cara mengujinya sendiri | "Here is how" is *Ini cara*. |
| Sewa menang kalau gak. | Sewa menang kalau tidak. (or *enggak*) | *gak* can't stand on its own. |
| Di tool Sewa vs Beli Rumah buatan saya | Di tool Sewa vs Beli Rumah | *buatan saya* sounds arrogant in Indonesian, unless the context is really about who made it. |
| Stabilitas Robert dan kebebasan Vieri gak bisa dikasih harga, dan saya gak akan mencoba | ..., dan saya gak bisa menilai | "I won't try" translated literally is wrong. Say what fits the context. |
| Kalau semua gangguannya dibuang, pertanyaan uangnya tinggal beberapa hal: | Kalau faktor-faktor lain dibuang, pertanyaannya bisa dijawab dengan beberapa jawaban: | Bad direct translation of "strip away the noise, the money question comes down to". |
| KPR bikin kamu menikmati hasil rumah atas 100% harga | KPR bikin kamu bisa menikmati imbal hasil kenaikan harga rumah atas 100% harga dasar | Name the return precisely, and say *bisa*. |
| jadi anggap saja seperti kompas, bukan kalkulator | jadi anggap saja kompas, bukan kalkulator | *anggap* already makes the comparison. |
| sekitar satu poin di atas bunga pinjamannya | sekitar satu persen di atas bunga pinjamannya | *poin* doesn't read as a percentage point. |
| saya gak akan mengira | saya gak akan kira | Casual sentence, bare verb. |
| angka yang jauh lebih tenang | angka yang jauh lebih moderat | A "calmer" number is *moderat*. |
| rumah tangganya memilikinya | sebagian besar rumah tangga punya rumah | Say what is meant; no *-nya* chain. |
| "tunjukkan saja" | "tunjukin aja" | Casual quote, casual words. Tell casual and factual word choice apart. |
| Bacanya begini: | Cara bacanya begini: | |

Not in his list, fixed in the same pass because it is the same pattern: every *hasil rumah*
and *hasil uangmu* became *imbal hasil*, and "Kalau gak, setiap rupiah ..." became
"Kalau tidak, ...".

## #KaburAjaDulu (October 2026)

| Before | After | Why |
| --- | --- | --- |
| pekerja profesional di Perth menabung sekitar Rp32 juta sebulan | pekerja profesional di Perth bisa menabung sekitar Rp32 juta sebulan | A model result, not a fact about every professional. |
| [tool Cost of Living Comparator](...) buatan saya | [tool Cost of Living Comparator](...) | Same *buatan saya* problem. |
| dan ini bagian yang harus saya jujurkan | dan ini bagian yang saya harus jujur | *jujurkan* is not a word. |

Not in his list, fixed in the same pass because it is the same pattern: the answer "Gak."
under "Tapi apakah semua orang cocok kabur?" became "Enggak.".

## Pajak suami istri, gabung atau pisah (October 2026)

Adjie: "quite good, natural". Use this post as the model for tone.

| Before | After | Why |
| --- | --- | --- |
| Contoh di atas cuma tiga titik. | Contoh di atas cuma tiga jenis. | "Three points" (data points) is not *titik*. |

## Revision of all three posts: "an English writer, translated" (October 2026)

Adjie's diagnosis: the agent still wrote with the mindset of an English writer whose text
is then translated, made worse by writing both languages of a post in one context. He
named ten patterns; each became a rule in `SKILL.md` (and a check in `scripts/cek.py`
where a regex can catch it). His examples, and the fixes made in this pass:

| Pattern | Before | After | Why |
| --- | --- | --- | --- |
| 1 Diksi | tabungan akhir bulan bisa jauh lebih besar | tabungan di akhir bulan bisa jauh lebih tebal | Lively native diction, not the dictionary word. |
| 1 Diksi | yang paling tipis justru ... | yang paling megap-megap justru ... | Same. |
| 2 Transisi | Sekarang pengakuan dulu. | Sekarang, mari jujur-jujuran dulu. | A transition that builds rapport, not a label. |
| 2 Transisi | Sampel ini bias. | Tentu saja sampel ini tidak sepenuhnya mewakili populasi secara luas (ada bias): ... | Bare and abrupt; the essay explains and stays close to the reader. |
| 3 Istilah | Setelah pajak resident dan Medicare levy, take-home sekitar A$3.769 per bulan. | Setelah dipotong pajak penghasilan untuk penduduk pajak Australia (*resident tax*) dan *Medicare levy* (iuran 2% untuk layanan kesehatan publik), gaji bersihnya sekitar A$3.769 per bulan. | Foreign administrative terms woven in, explained, in italics. |
| 3 Istilah | Progressive Wage Model (PWM), jenjang paling bawah pekerja kebersihan, S$2.080 | Singapura tidak punya upah minimum nasional. Yang ada adalah Progressive Wage Model (PWM), skema upah minimum per sektor ... | Say what the scheme is before using it. |
| 3 Istilah | **Capital freedom.** | ***Capital freedom* (kebebasan menaruh modal).** | Keep the term, italicise it, explain a very foreign one. |
| 4 Retoris | Harga nasi goreng menentukan makan siangmu. Selisih antara gaji dan pengeluaran menentukan masa depanmu. | ... tetapi harganya hanya menentukan menu makan siangmu hari ini. Selisih antara penghasilan dan pengeluaranlah yang pada akhirnya membentuk masa depanmu. | A conclusion that builds and lands. |
| 5, 8 Calque, idiom | Stabilitas Robert dan kebebasan Vieri gak bisa dikasih harga | ... tidak ternilai harganya | "can't be priced" word for word sounds like a market stall item without a price tag. |
| 6 Konjungsi | Tapi ada pertanyaan kedua yang lebih dingin ... | Meski begitu, ada pertanyaan kedua yang lebih dingin ... | English *But* at the start chops the flow. |
| 6 Konjungsi | Dan saya akui: ... | Soal rasa, saya pun mengakui ... | English *And* at the start. |
| 6 Konjungsi | Satu hal lagi, supaya adil. | Ada satu hal lagi yang perlu diingat supaya perbandingannya tidak berat sebelah. | Fragment opener from English. |
| 7 Personifikasi | Kenapa Perth bilang beli dan Jakarta bilang sewa | Di Perth lebih untung beli, di Jakarta lebih untung sewa | A city cannot *bilang*. |
| 9 Copywriting | Cinta itu urusan hati. Pajak itu urusan hitungan. Jangan biarkan yang satu mengambil keputusan untuk yang lain. | Urusan hati boleh saja diserahkan pada cinta, tetapi untuk urusan pajak, biarkan hitungan yang mengambil keputusan. | Punchy American slogan; one flowing sentence instead. |
| 9 Copywriting | Jangan mulai dari perasaan, dan jangan mulai dari harga nasi goreng. | ..., mulailah dari selisih itu, bukan dari perasaan atau dari harga sepiring nasi goreng | Same. |
| 10 Elipsis | Biar fair, bahas Perth dulu. | Agar adil, mari kita bahas Perth terlebih dahulu. | Missing subject; reads like notes. Supersedes the earlier "biar fair" preference for narrative. |
| 10 Elipsis | Sebelum masuk ke hitungan, tiga istilah dulu. | Sebelum masuk ke hitungan, ada tiga istilah yang perlu kita pahami terlebih dahulu. | Same. |

Same patterns, fixed in the same pass (not in his list):

| Before | After |
| --- | --- |
| Kenapa satu kota bilang beli, kota lain bilang sewa? | Kenapa di satu kota lebih untung beli, di kota lain lebih untung sewa? |
| Jakarta bayarnya lebih sedikit. | ..., dan di Jakarta imbalan itu lebih kecil. |
| Perth butuh sekitar $210 ribu untuk mulai | Untuk membeli di Perth, kamu butuh sekitar $210 ribu sebagai modal awal |
| Melbourne atau Bali akan bercerita lain | Hasil untuk Melbourne atau Bali bisa berbeda |
| Apa kata tool tentang Perth dan Jakarta? | Bagaimana hasil hitungan *tool* untuk Perth dan Jakarta? |
| Negara imigrasi versus negara kelahiran | Tumbuh dari imigrasi versus tumbuh dari kelahiran (*negara kelahiran* means country of birth) |
| Yang satu leverage, yang satu bocor. | Di Perth, utang ikut bekerja untuk pemiliknya, sementara di Jakarta utang justru menggerogoti kekayaan pemiliknya. |
| Ini bukan restorannya serakah. Ini upahnya. | ..., dan penyebabnya bukan restoran yang serakah, melainkan upah yang tinggi. |
| Kelihatan downgrade, kan 😅 | Kelihatannya seperti turun kelas, kan? 😅 |
| developer rekanan | pengembang rekanan bank |
| PTKP a.k.a. bagian penghasilan ... | PTKP, alias bagian penghasilan ... |
| kartu Penghematan pajak ...: dia bilang cara mana yang lebih murah | Kartu ini menunjukkan cara mana yang lebih murah |
| Saat suami dan istri sama-sama bergaji besar, ... (fragment answer) | Gabung lebih untung ketika suami dan istri sama-sama bergaji besar ... |
| tool, input, spreadsheet, fixed, floating ... (roman) | *tool*, *input*, *spreadsheet*, *fixed*, *floating* ... (italic everywhere, *tool*-nya) |
| gak in rules, tables and footnotes ("gak digabung", "gak dihitung") | tidak (factual layer) |
