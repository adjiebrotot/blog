"""Total liabilities of four state construction companies, 2015-2024 (footnote karya)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '.claude', 'skills', 'procedural-illustration', 'scripts'))
from pi import *  # noqa

YEARS = list(range(2015, 2025))
VALS = [60.4, 98.4, 156.2, 197.5, 207.2, 212.5, 215.5, 215.6, 213.1, 188.7]

FIG = Figure(
    'gsl-pi-soe-liabilities',
    title={'en': 'Four state builders more than tripled their liabilities in three years',
           'id': 'Liabilitas empat BUMN Karya naik lebih dari tiga kali lipat dalam tiga tahun'},
    subtitle={'en': 'Combined liabilities of Waskita Karya, Wijaya Karya, Adhi Karya and PP',
              'id': 'Liabilitas gabungan Waskita Karya, Wijaya Karya, Adhi Karya, dan PP'},
    source='refs',
    alt={'en': 'Column chart of combined liabilities of four state construction companies: Rp60.4 trillion in 2015, Rp197.5 trillion in 2018, above Rp200 trillion until 2023, Rp188.7 trillion in 2024.',
         'id': 'Grafik kolom total liabilitas gabungan empat BUMN Karya: Rp60,4 triliun pada 2015, Rp197,5 triliun pada 2018, di atas Rp200 triliun sampai 2023, dan Rp188,7 triliun pada 2024.'},
    langs=('en', 'id'),
    review={
        'type': 'Columns: one value per year, a time series where the level and its jump are the point.',
        'audience': 'General readers: company names spelled out in the subtitle, unit in the subtitle and axis.',
        'transparency': 'All ten years shown from zero; the sum of the four companies, per-company figures are in the post footnote.',
        'standalone': 'Title, subtitle, values on columns, the labelled 2015 to 2018 rise and the source carry the point.',
        'outliers': 'The 2015 to 2018 tripling (60.4 to 197.5) is highlighted and annotated; later years are context.',
        'order': 'Chronological, 2015 to 2024, left to right.',
    },
)
FIG.add(Bars(
    [{'label': str(y), 'value': v, 'role': 'hl' if y in (2015, 2018) else 'a'} for y, v in zip(YEARS, VALS)],
    orient='v', fmt={'dp': 1}, narrow_orient='v',
    unit={'en': 'Rp trillion', 'id': 'Rp triliun'},
    annotate=[{'at': 3, 'text': {'en': '3.3× the 2015 level', 'id': '3,3 kali tingkat 2015'}}],
))
