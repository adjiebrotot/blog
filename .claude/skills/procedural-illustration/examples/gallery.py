"""Every component once, with made-up example numbers (not data: never publish these).
The catalogue and the engine's own test:

    python3 .claude/skills/procedural-illustration/scripts/render.py \\
        .claude/skills/procedural-illustration/examples/gallery.py --out <scratchpad>/gallery

Copy the closest figure into _illustrations/<prefix>-pi-<subject>.py and replace the data.
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))
from pi import *  # noqa

R = {'type': 'example', 'audience': 'example', 'transparency': 'example numbers', 'standalone': 'example',
     'outliers': 'example', 'order': 'largest first', 'axis': 'example', 'legend': 'example', 'cvd': 'labels'}
SRC = 'Example numbers, not data'


def fig(name, title, sub, **kw):
    return Figure(f'gallery-{name}', title={'en': title}, subtitle={'en': sub} if sub else None,
                  source={'en': SRC}, alt={'en': title}, langs=('en',), review=R, **kw)


FIGS = []

# 1 ranked horizontal bars with flags, a highlighted subject and a reference line
f = fig('bars-h', 'Indonesia pays its leader far more than its peers', "Leader's pay as a multiple of the median wage")
f.add(Bars([{'label': n, 'value': v, 'flag': c, 'role': r} for n, v, c, r in [
    ('Philippines', 20.8, 'PHL', 'a'), ('Indonesia', 18.8, 'IDN', 'hl'), ('Australia', 8.4, 'AUS', 'base'),
    ('Japan', 8.3, 'JPN', 'base'), ('Thailand', 8.0, 'THA', 'a'), ('United States', 7.8, 'USA', 'base'),
    ('Vietnam', 3.8, 'VNM', 'a'), ('China', 1.9, 'CHN', 'base')]],
    fmt={'dp': 1, 'unit': '×'}, ref=[{'value': 8.4, 'label': {'en': 'Australia'}}],
    annotate=[{'at': 1, 'text': {'en': 'President plus allowances'}}]))
FIGS.append(f)

# 2 columns over time
f = fig('bars-v', 'Liabilities tripled in three years', 'Total liabilities, Rp trillion, end of year')
f.add(Bars([{'label': str(y), 'value': v, 'role': 'hl' if y == 2018 else 'a'} for y, v in
            zip(range(2015, 2025), [60.4, 98.4, 156.2, 197.5, 207.2, 212.5, 215.5, 215.6, 213.1, 188.7])],
           orient='v', fmt={'dp': 1}, unit={'en': 'Rp trillion'}, narrow_orient='v',
           annotate=[{'at': 3, 'text': {'en': '3.3× the 2015 level'}}]))
FIGS.append(f)

# 3 stacked and grouped bars
f = fig('bars-stack', 'Where the budget goes', 'Spending by function, Rp trillion')
f.add(Bars([{'label': '2023', 'values': [400, 300, 200]}, {'label': '2024', 'values': [450, 320, 230]},
            {'label': '2025', 'values': [500, 310, 260]}], orient='h', mode='stack',
           series=[{'name': 'Transfers', 'role': 's1'}, {'name': 'Ministries', 'role': 's3'},
                   {'name': 'Interest', 'role': 'hl'}], fmt={'dp': 0}))
FIGS.append(f)

# 4 index lines with a band, a reference and a note
f = fig('line', "Indonesia's real wage is still below 2019", 'Average wage over consumer prices, 2019 = 100')
f.add(Line([2019, 2020, 2021, 2022, 2023, 2024, 2025], [
    {'name': 'Australia', 'values': [100, 100.8, 99.9, 96.5, 94.9, 95.4, 95.9], 'role': 'base'},
    {'name': 'Indonesia', 'values': [100, 93.1, 91.0, 97.8, 97.7, 98.3, 98.3], 'role': 'hl'}],
    y={'domain': [88, 104], 'zero': False, 'fmt': {'dp': 1}, 'unit': 'Index, 2019 = 100', 'step': 4},
    ref=[{'value': 100, 'label': '2019 level'}], bands=[{'from': 2020, 'to': 2021, 'label': 'Pandemic'}],
    annotate=[{'x': 2021, 'series': 1, 'text': 'Low point: 91.0'}]))
FIGS.append(f)

# 5 stacked area
f = fig('area', 'Solar overtakes coal in new capacity', 'New capacity added, GW')
f.add(Line(list(range(2018, 2026)), [
    {'name': 'Coal', 'values': [5, 5, 4, 4, 3, 3, 2, 2], 'role': 'base'},
    {'name': 'Gas', 'values': [2, 2, 2, 3, 3, 3, 3, 3], 'role': 's3'},
    {'name': 'Solar', 'values': [0.5, 1, 1.5, 2, 3, 4.5, 6, 8], 'role': 'hl'}], stack=True,
    y={'fmt': {'dp': 1}, 'unit': 'GW'}))
FIGS.append(f)

# 6 scatter
f = fig('scatter', 'Richer countries pay their leaders less, relative to wages', 'Each dot is a country')
pts = [('IDN', 4.9, 18.8), ('PHL', 3.9, 20.8), ('AUS', 64, 8.4), ('JPN', 33, 8.3), ('THA', 7, 8.0),
       ('USA', 85, 7.8), ('VNM', 4.3, 3.8), ('CHN', 12.6, 1.9), ('NOR', 87, 3.3), ('GBR', 52, 4.5)]
f.add(Scatter([{'x': x, 'y': y, 'label': c, 'role': 'hl' if c == 'IDN' else 'base', 'show_label': c in ('PHL', 'USA')}
               for c, x, y in pts], x={'title': 'GDP per person, US$ thousand', 'zero': True},
              y={'title': 'Pay multiple', 'zero': True}, trend=True))
FIGS.append(f)

# 7 dumbbell and slope
f = fig('dumbbell', 'Poverty fell everywhere, fastest in Vietnam', 'Share below US$4.20 a day, %')
f.add(Dumbbell([{'label': n, 'a': a, 'b': b, 'flag': c, 'role': 'hl' if c == 'IDN' else None} for n, c, a, b in [
    ('Vietnam', 'VNM', 40.1, 9.2), ('Indonesia', 'IDN', 52.3, 15.5), ('Philippines', 'PHL', 45.0, 25.8)]],
    names=('2010', '2024'), fmt={'dp': 1}))
FIGS.append(f)
f = fig('slope', 'Rankings swap after the reform', 'Score out of 100')
f.add(Slope([{'label': 'Jakarta', 'a': 62, 'b': 71, 'role': 'hl'}, {'label': 'Surabaya', 'a': 70, 'b': 66},
             {'label': 'Medan', 'a': 55, 'b': 58}], names=('2020', '2025')))
FIGS.append(f)

# 8 donut, waffle, stats
f = fig('donut', 'Most of the levy is never refunded', 'Share of the levy, 2025')
f.add(Donut([{'label': 'Kept by the state', 'value': 62, 'role': 'hl'}, {'label': 'Refunded', 'value': 30, 'role': 'a'},
             {'label': 'Still in dispute', 'value': 8, 'role': 'base'}], centre={'value': '62%', 'label': 'kept'}))
FIGS.append(f)
f = fig('waffle', 'Three in five workers are informal', 'Share of employed people, 2025')
f.add(Waffle([{'label': 'Informal: no contract, no social security', 'value': 59, 'role': 'hl'}], rest='Formal'))
FIGS.append(f)
f = fig('stats', 'The project in three numbers', None)
f.add(Stats([{'value': 'Rp 114 T', 'label': 'cost, a third over budget', 'role': 'hl', 'icon': 'banknote'},
             {'value': '142 km', 'label': 'Jakarta to Bandung', 'role': 'a', 'icon': 'train'},
             {'value': '45 min', 'label': 'from 3 hours by car', 'role': 'a', 'icon': 'clock'}]))
FIGS.append(f)

# 9 unit charts: icon grid and stacked towers
f = fig('units-grid', 'Days of minimum wage for one phone', 'Working days at the minimum wage, 2026')
f.add(Units([{'label': 'Jakarta', 'value': 104, 'flag': 'IDN', 'role': 'hl'},
             {'label': 'Singapore', 'value': 25, 'flag': 'SGP', 'role': 'a'},
             {'label': 'Perth', 'value': 12, 'flag': 'AUS', 'role': 'a'}],
            icon='phone', key='= 1 working day', unit=' days'))
FIGS.append(f)
f = fig('units-stack', 'Days of minimum wage for one phone', 'One slab = one working day, 2026')
f.add(Units([{'label': 'Jakarta', 'value': 104, 'flag': 'IDN', 'role': 'hl'},
             {'label': 'Singapore', 'value': 25, 'flag': 'SGP', 'role': 'a'},
             {'label': 'Perth', 'value': 12, 'flag': 'AUS', 'role': 'a'}],
            icon='phone', arrange='stack', unit=' days'))
FIGS.append(f)
f = fig('compare', 'The new debt is eight times the old', 'Area is proportional to the amount')
f.add(Compare([{'label': '2015', 'value': 1, 'text': 'Rp 25 T', 'role': 'base'},
               {'label': '2024', 'value': 8, 'text': 'Rp 200 T', 'role': 'hl'}]))
FIGS.append(f)
f = fig('timeline', 'From plan to first train', None)
f.add(Timeline([{'date': '2015', 'text': 'Japan and China bid; China wins'}, {'date': '2016', 'text': 'Groundbreaking'},
                {'date': '2019', 'text': 'Cost overrun found', 'role': 'hl'}, {'date': '2023', 'text': 'First paying passengers'}]))
FIGS.append(f)

# 10 flowchart: a cycle with an entry and a failure branch
f = fig('flow', 'How land pays for the line', None, kind='flow')
f.add(Flow([Node('a', 'State owns the land', role='start', near=('b', 'l'), w=150),
            Node('b', 'Government builds the line with borrowed money', role='key'),
            Node('c', 'Land near the line rises in value'),
            Node('d', 'Land-use rights sold to developers'),
            Node('e', 'Sales repay the debt and fund the next line'),
            Node('f', 'Nobody comes: land does not sell, the debt stays', role='warn', near=('d', 'br'), w=190)],
           [Edge('a', 'b'), Edge('b', 'c'), Edge('c', 'd'), Edge('d', 'e'), Edge('e', 'b'),
            Edge('c', 'f', text='no jobs, no reason to move', dashed=True, role='hl')],
           cycle={'ids': ['b', 'c', 'd', 'e'], 'cx': 0.5, 'r': 130}))
FIGS.append(f)

# 11 maps: provinces highlighted, a world choropleth
f = fig('map-admin1', 'Five provinces visited', None, kind='map')
f.add(Map('admin1:CHN', projection='albers', context='world-50m',
          highlight={k: 'a' for k in ['CN-BJ', 'CN-SH', 'CN-GD', 'CN-SC', 'CN-YN']},
          labels=[{'id': k, 'text': t} for k, t in [('CN-BJ', 'Beijing'), ('CN-SH', 'Shanghai'),
                                                     ('CN-GD', 'Guangdong'), ('CN-SC', 'Sichuan'), ('CN-YN', 'Yunnan')]],
          bounds=(73, 17, 135, 54)))
FIGS.append(f)
f = fig('map-world', 'Where the minimum wage buys a phone fastest', 'Working days for one phone', kind='map')
f.add(Map('world-110m', projection='equal-earth', values={'IDN': 104, 'AUS': 12, 'SGP': 25, 'USA': 15, 'IND': 160,
                                                          'BRA': 70, 'DEU': 11, 'CHN': 45, 'ZAF': 60, 'NGA': 210},
          bins=[20, 40, 80, 120], value_fmt={'dp': 0}, key='working days', bounds=(-170, -58, 180, 84)))
FIGS.append(f)

# 12 3D: bars over two categories, a surface, unit blocks
f = fig('bars3d', 'Peak load by season and hour', 'GW')
f.add(Bars3D(['Wet', 'Dry'], ['6:00', '12:00', '18:00', '22:00'], [[20, 24, 31, 25], [22, 27, 34, 26]],
             roles=['base', 'a'], label=[(1, 2)], fmt={'dp': 0}))
FIGS.append(f)
f = fig('surface', 'Loan cost rises with rate and term', 'Total interest as a share of the loan')
f.add(Surface3D(list(range(5, 31, 5)), [3, 5, 7, 9, 11], f=lambda t, r: t * r / 2.0,
                axes=('Term, years', 'Rate, %', 'Interest, %'), fmt={'dp': 0}))
FIGS.append(f)
f = fig('blocks', 'A year of rice', 'One cube = 10 kg')
f.add(Blocks3D([{'label': 'Indonesia', 'value': 11, 'role': 'hl'}, {'label': 'Japan', 'value': 5, 'role': 'a'}],
               base=3, unit=' cubes'))
FIGS.append(f)

# 13 single-line diagram with animated flow
f = fig('sld', 'A substation feeding two loads', '150 kV / 20 kV', kind='engineering')
sld = SLD(width=10, height=6)


@sld.build
def _(s, lang, narrow):
    s.grid_infeed((5, 0.6), label='Grid', side='right')
    s.wire([(5, 0.6), (5, 1.4)])
    s.bus((1, 1.4), (9, 1.4), label='150 kV')
    s.wire([(5, 1.4), (5, 3.0)])
    s.breaker((5, 2.1), label='CB')
    s.flow((5, 1.6), (5, 2.9))
    t = s.transformer((5, 3.5), label='60 MVA', side='right')
    s.wire([t[1], (5, 4.6)])
    s.bus((2, 4.6), (8, 4.6), label='20 kV')
    for x in (3, 7):
        s.wire([(x, 4.6), (x, 5.6)])
        s.load((x, 5.6))
    s.flow_label((5.5, 2.1), ['48 MW', '12 Mvar'], up=False, role='a')


f.add(sld)
FIGS.append(f)
