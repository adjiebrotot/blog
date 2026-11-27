"""The land-finance loop of the post on how China builds so fast, in English and Indonesian.
The two posts' flows differ a little (the Indonesian failure branch leaves from the building step and has
two boxes), so each language is its own Figure with the same name: files are <name>-en and <name>-id."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '.claude', 'skills', 'procedural-illustration', 'scripts'))
from pi import *  # noqa

REVIEW = {'type': 'a cycle with an entry and a failure branch: the claim is a loop that repays itself, and where it breaks',
          'audience': 'general readers: plain words, no abbreviations in the boxes',
          'transparency': 'every step of the loop in the post is a box; the failure path is dashed and conditional',
          'standalone': 'title, subtitle, the boxes and the edge condition tell the whole loop without the post',
          'source': "a diagram of the author's own reasoning, built from the post's text and its cited sources; it is not a data series",
          'units': 'a diagram with no quantities'}


def loop_en():
    nodes = [Node('a', 'State owns the land', role='start', near=('b', 't'), w=170),
             Node('b', 'Government builds rail, roads and metro, borrowing through local financing vehicles', role='key', w=230),
             Node('c', 'Land near the new line rises in value'),
             Node('d', 'Government sells land-use rights to developers'),
             Node('e', 'Revenue repays the debt and funds the next project'),
             Node('f', 'Land does not sell, the debt stays (Yujiapu)', role='warn', near=('b', 'r'), w=190, gap=60)]
    edges = [Edge('a', 'b'), Edge('b', 'c'), Edge('c', 'd'), Edge('d', 'e'), Edge('e', 'b'),
             Edge('c', 'f', text='nobody comes: no jobs, no reason', dashed=True, role='hl')]
    return Flow(nodes, edges, cycle={'ids': ['b', 'c', 'd', 'e'], 'cx': 0.36, 'r': 130})


def loop_id():
    nodes = [Node('a', 'Negara menguasai tanah', role='start', near=('b', 't'), w=170),
             Node('b', 'Pemerintah daerah membangun rel, jalan, dan metro dengan utang', role='key', w=230),
             Node('c', 'Harga tanah di sekitarnya naik'),
             Node('d', 'Hak guna tanah dijual ke pengembang'),
             Node('e', 'Hasilnya melunasi utang dan membiayai proyek berikutnya'),
             Node('f', 'Tidak ada yang datang: tidak ada pekerjaan, tidak ada alasan untuk pindah', role='warn', near=('b', 'r'), w=190, gap=60),
             Node('g', 'Tanah tidak laku, utang tetap menumpuk, seperti di Yujiapu', role='warn', near=('c', 'r'), w=190, gap=60)]
    edges = [Edge('a', 'b'), Edge('b', 'c'), Edge('c', 'd'), Edge('d', 'e'), Edge('e', 'b'),
             Edge('b', 'f', dashed=True, role='hl'), Edge('f', 'g', dashed=True, role='hl')]
    return Flow(nodes, edges, cycle={'ids': ['b', 'c', 'd', 'e'], 'cx': 0.36, 'r': 130})


FIG_EN = Figure('cbf-pi-land-finance-loop',
                title={'en': 'In China, selling land repays the debt that built the line'},
                subtitle={'en': 'The loop works only if people and jobs follow the new line'},
                alt={'en': 'Flowchart. The state owns the land. The government borrows through local financing vehicles to build rail, roads and metro; land near the new line rises in value; the government sells land-use rights to developers; the revenue repays the debt and funds the next project, which starts the loop again. If nobody comes, with no jobs and no reason to move, the land does not sell and the debt stays, as at Yujiapu.'},
                langs=('en',), kind='flow', data_table=False, review=REVIEW)
FIG_EN.add(loop_en())
FIG_ID = Figure('cbf-pi-land-finance-loop',
                title={'id': 'Di China, penjualan tanah melunasi utang yang membangun jalur'},
                subtitle={'id': 'Putaran ini hanya berjalan kalau penduduk dan pekerjaan menyusul jalur baru'},
                alt={'id': 'Diagram alur. Negara menguasai tanah. Pemerintah daerah membangun rel, jalan, dan metro dengan utang; harga tanah di sekitarnya naik; hak guna tanah dijual ke pengembang; hasilnya melunasi utang dan membiayai proyek berikutnya, lalu putaran dimulai lagi. Kalau tidak ada yang datang karena tidak ada pekerjaan dan tidak ada alasan untuk pindah, tanah tidak laku dan utang tetap menumpuk, seperti di Yujiapu.'},
                langs=('id',), kind='flow', data_table=False, review=REVIEW)
FIG_ID.add(loop_id())
FIGS = [FIG_EN, FIG_ID]
