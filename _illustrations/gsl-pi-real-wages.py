"""Real wages, Indonesia vs Australia, 2019 = 100 (how-governments-lie-with-statistics, footnote realwage)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '.claude', 'skills', 'procedural-illustration', 'scripts'))
from pi import *  # noqa

FIG = Figure(
    'gsl-pi-real-wages',
    title={'en': "Indonesia's real wage still buys 1.7% less than in 2019",
           'id': 'Upah riil di Indonesia masih 1,7% di bawah tingkat 2019'},
    subtitle={'en': 'Average wage divided by consumer prices, index, 2019 = 100, 2019 to 2025',
              'id': 'Rata-rata upah dibagi indeks harga konsumen, 2019 = 100, 2019 sampai 2025'},
    source={'en': 'Author calculation from BPS (Sakernas), ABS and the World Bank; Australia 2025 uses three quarters',
            'id': 'Hitungan penulis dari data BPS (Sakernas), ABS, dan Bank Dunia; data Australia 2025 baru mencakup tiga triwulan'},
    alt={'en': 'Line chart of real wages, 2019 = 100. Indonesia falls to 91.0 in 2021 and ends 2025 at 98.3, below 2019. Australia ends at 95.9, lower still.',
         'id': 'Grafik garis upah riil, 2019 = 100. Indonesia turun ke 91,0 pada 2021 lalu naik ke 98,3 pada 2025, masih di bawah 2019. Australia turun ke 95,9 pada 2025, lebih rendah lagi.'},
    langs=('en', 'id'),
    review={
        'type': 'Line chart: two series over seven years against a base of 100; the trend and the gap to 2019 are the point.',
        'audience': 'General readers: "real wage" is explained in the subtitle as wage divided by prices; no abbreviations in the drawing.',
        'transparency': 'Full 2019 to 2025 series for both countries, same base year; the post footnote gives the sources and that Australia 2025 uses three quarters.',
        'standalone': 'Title, subtitle, direct labels, the labelled low and the source say the whole story without the post.',
        'outliers': 'Indonesia low point 2021 (91.0) is annotated; the 2019 level is the dashed reference line.',
        'axis': 'The y axis starts at 88, not zero: an index of 100 in 2019 compares unlike series, the reference line marks the base, and a zero axis would flatten differences of a few points.',
    },
)
FIG.add(Line(
    [2019, 2020, 2021, 2022, 2023, 2024, 2025],
    [{'name': {'en': 'Australia', 'id': 'Australia'}, 'values': [100, 100.8, 99.9, 96.5, 94.9, 95.4, 95.9], 'role': 'base'},
     {'name': {'en': 'Indonesia', 'id': 'Indonesia'}, 'values': [100, 93.1, 91.0, 97.8, 97.7, 98.3, 98.3], 'role': 'hl'}],
    y={'domain': [88, 104], 'zero': False, 'fmt': {'dp': 1}, 'step': 4,
       'unit': {'en': 'Index, 2019 = 100', 'id': 'Indeks, 2019 = 100'}},
    ref=[{'value': 100, 'label': {'en': '2019 level', 'id': 'Tingkat 2019'}}],
    annotate=[{'x': 2021, 'series': 1, 'text': {'en': 'Low point: 91.0', 'id': 'Titik terendah: 91,0'}}],
))
