"""kad: berapa hari kerja dengan upah minimum untuk membeli iPhone 18 Pro (menggantikan blok Mermaid)."""
import sys, os
sys.path.insert(0, os.path.join(os.getcwd(), '.claude', 'skills', 'procedural-illustration', 'scripts'))
from pi import *  # noqa

# Hari kerja = harga / (gaji bersih upah minimum per bulan / 21,7 hari kerja), dibulatkan, seperti di tulisan.
rows = [
    {'label': 'Jakarta', 'value': 104, 'flag': 'IDN', 'role': 'hl', 'text': '104 hari'},
    {'label': 'Singapura', 'value': 25, 'flag': 'SGP', 'role': 'a', 'text': '25 hari'},
    {'label': 'Perth', 'value': 12, 'flag': 'AUS', 'role': 'a', 'text': '12 hari'},
]

FIG = Figure(
    'kad-pi-iphone-days',
    title={'id': 'Harga satu iPhone setara 104 hari kerja upah minimum di Jakarta, tetapi hanya 12 hari di Perth'},
    subtitle={'id': 'Hari kerja berupah minimum bersih untuk membeli satu iPhone 18 Pro, harga Oktober 2026'},
    note={'id': 'Singapura tidak punya upah minimum nasional; yang dipakai adalah upah dasar pekerja kebersihan menurut Progressive Wage Model.'},
    source='refs',
    alt={'id': 'Tiga menara ikon ponsel, satu ikon untuk satu hari kerja. Menara Jakarta setinggi 104 ikon, '
               'Singapura 25, dan Perth 12. Pekerja berupah minimum di Jakarta harus bekerja sekitar 4,2 kali lebih lama daripada pekerja di Singapura '
               'dan 8,7 kali lebih lama daripada pekerja di Perth untuk membeli satu iPhone 18 Pro.'},
    langs=('id',),
    review={
        'type': 'Menara ikon ponsel (unit chart bertumpuk): tinggi menara sebanding dengan jumlah hari, dan selisih 104 lawan 12 langsung terasa. Cocok untuk tiga kota dengan angka yang berbeda jauh.',
        'audience': 'Pembaca umum: satuan "hari kerja" dan ponsel dikenal semua orang; tanpa singkatan di dalam gambar.',
        'transparency': 'Ketiga kota dihitung dengan cara yang sama (harga resmi dalam mata uang setempat dibagi gaji bersih harian upah minimum, 21,7 hari kerja per bulan); angka sama persis dengan tulisan. Pengertian upah minimum tiap kota dijelaskan di catatan.',
        'standalone': 'Judul, subjudul, catatan dan sumber menjelaskan seluruh perbandingan tanpa membaca tulisan.',
        'outliers': 'Jakarta (104 hari) adalah yang disorot dan diberi warna merah; Perth (12 hari) adalah yang terendah, tertulis jelas di atas menaranya.',
        'order': 'Dari yang terbanyak ke yang tersedikit (Jakarta, Singapura, Perth), karena tinggi menara menurun dan selisih terbesar terbaca dari kiri ke kanan.',
        'legend': 'Kunci "satu ikon ponsel = satu hari kerja" wajib agar satuannya jelas.',
        'cvd': 'Setiap menara diberi nama, bendera dan angka, jadi warna bukan satu-satunya petunjuk.',
    },
)
FIG.add(Units(rows, icon='phone', per=1, arrange='stack',
              key={'id': '= 1 hari kerja'}, unit={'id': ' hari'}))
FIGS = [FIG]
