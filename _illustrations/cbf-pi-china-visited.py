"""China map for the post on how China builds so fast: the 14 Chinese jurisdictions Adjie has visited."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '.claude', 'skills', 'procedural-illustration', 'scripts'))
from pi import *  # noqa

VISITED = [  # (id, en, id-lang label)
    ('CN-BJ', 'Beijing', 'Beijing'), ('CN-TJ', 'Tianjin', 'Tianjin'), ('CN-SH', 'Shanghai', 'Shanghai'),
    ('CN-CQ', 'Chongqing', 'Chongqing'), ('CN-JS', 'Jiangsu', 'Jiangsu'), ('CN-HL', 'Heilongjiang', 'Heilongjiang'),
    ('CN-HN', 'Hunan', 'Hunan'), ('CN-SN', 'Shaanxi', 'Shaanxi'), ('CN-SC', 'Sichuan', 'Sichuan'),
    ('CN-GD', 'Guangdong', 'Guangdong'), ('CN-FJ', 'Fujian', 'Fujian'), ('TWN', 'Taiwan', 'Taiwan'),
    ('HKG', 'Hong Kong', 'Hong Kong'), ('MAC', 'Macau', 'Makau'),
]
KIND = {'CN-BJ': ('Municipality', 'Kota setingkat provinsi'), 'CN-TJ': ('Municipality', 'Kota setingkat provinsi'),
        'CN-SH': ('Municipality', 'Kota setingkat provinsi'), 'CN-CQ': ('Municipality', 'Kota setingkat provinsi'),
        'HKG': ('Special administrative region', 'Daerah administrasi khusus'),
        'MAC': ('Special administrative region', 'Daerah administrasi khusus'),
        'TWN': ('Taiwan', 'Taiwan')}

PREFS = {'CN-BJ': ('above-left', 'left'), 'CN-TJ': ('right', 'above-right'), 'CN-SH': ('right', 'below-right'),
         'HKG': ('below-right', 'right'), 'MAC': ('below-left', 'left', 'below'), 'CN-CQ': ('left',),
         'CN-JS': ('right', 'above-right'), 'CN-FJ': ('right', 'below-right'), 'TWN': ('right',)}
CALL = {'CN-BJ', 'CN-TJ', 'CN-SH', 'HKG', 'MAC'}


NARROW = {'CN-HL', 'CN-BJ', 'CN-SC', 'CN-SH', 'CN-GD', 'TWN', 'HKG'}   # labels kept on the phone layout


class VisitedMap(Map):
    def draw(self, c, lang, y0):
        full = self.labels
        if c.narrow:
            self.labels = [lb for lb in full if lb['id'] in NARROW]
        try:
            return super().draw(c, lang, y0)
        finally:
            self.labels = full

    def table(self, lang):
        head = ['', 'Type' if lang == 'en' else 'Jenis']
        rows = []
        for k, en, idn in VISITED:
            t = KIND.get(k, ('Province', 'Provinsi'))
            rows.append([en if lang == 'en' else idn, t[0] if lang == 'en' else t[1]])
        return head, rows


def build(callouts):
    return VisitedMap('admin1:CHN', projection='albers', context='world-50m', add=[('world-50m', ['HKG', 'MAC', 'TWN'])],
                      highlight={k: 'a' for k, _, _ in VISITED}, bounds=(73, 17, 135, 54),
                      labels=[{'id': k, 'text': {'en': en, 'id': idn}, 'prefs': PREFS.get(k, ()) or
                               ('right', 'left', 'above', 'below'), 'callout': k in callouts}
                              for k, en, idn in VISITED],
                      height={'w': 520, 'n': 330})


FIG = Figure(
    'cbf-pi-china-visited',
    title={'en': '14 Chinese jurisdictions I have visited',
           'id': '14 wilayah di China yang pernah saya kunjungi'},
    subtitle={'en': 'Shaded blue: places I have been to. On small screens only some are named; the data table lists all 14.',
              'id': 'Warna biru: tempat yang sudah saya kunjungi. Di layar kecil hanya sebagian wilayah yang diberi nama; keempat belas wilayah ada di tabel data.'},
    source={'en': "The author's own travel; map boundaries from Natural Earth",
            'id': 'Catatan perjalanan penulis; batas wilayah peta dari Natural Earth'},
    alt={'en': 'Map of China with 14 jurisdictions shaded: Beijing, Tianjin, Shanghai, Chongqing, Jiangsu, Heilongjiang, Hunan, Shaanxi, Sichuan, Guangdong, Fujian, Taiwan, Hong Kong and Macau',
         'id': 'Peta China dengan 14 wilayah berwarna: Beijing, Tianjin, Shanghai, Chongqing, Jiangsu, Heilongjiang, Hunan, Shaanxi, Sichuan, Guangdong, Fujian, Taiwan, Hong Kong, dan Makau'},
    kind='map', data_table=True,
    review={'type': 'a highlighted-region map: membership (visited or not), so no key and no ramp',
            'audience': 'general readers who may not know where Hunan or Shaanxi are; every shaded place is named',
            'transparency': 'all 14 visited places are shaded and named; the rest of China is shown unshaded; no claim lines, de facto Natural Earth borders',
            'standalone': 'title, subtitle, names on the shaded places and the source say what the map is',
            'outliers': 'small places (Beijing, Tianjin, Shanghai, Hong Kong, Macau) get pointer lines',
            'legend': 'no key: shaded places are named directly',
            'source': "the author's own travel; not a data series",
            'units': 'a count of places, in the title'})
FIG.add(build(CALL))
