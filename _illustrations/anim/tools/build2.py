import base64, io, json, os
from PIL import Image
here = os.path.dirname(os.path.abspath(__file__)); root = os.path.dirname(here)
def uri(img, q=90):
    b = io.BytesIO(); img.save(b, 'WEBP', quality=q, method=6)
    return 'data:image/webp;base64,' + base64.b64encode(b.getvalue()).decode()
meta = json.load(open(f'{root}/v2/pieces/meta.json'))
pieces = {}
skip = {'head0'}
for f in sorted(os.listdir(f'{root}/v2/pieces')):
    if f.endswith('.png') and f[:-4] not in skip: pieces[f[:-4]] = uri(Image.open(f'{root}/v2/pieces/{f}'))
pieces['plate'] = uri(Image.open(f'{root}/plate.png').convert('RGB'), 86)
sheets = {}
for n, src in [('parts', 'v2/parts34.png'), ('faces', 'v2/faces34.png'), ('hands', 'v2/hands34.png')]:
    im = Image.open(f'{root}/{src}').convert('RGB'); im.thumbnail((420, 420)); sheets[n] = uri(im, 80)
im = Image.open(f'{root}/plate.png').convert('RGB'); im.thumbnail((640, 640)); sheets['plate'] = uri(im, 78)
html = open(f'{here}/template2.html').read().replace('/*PIECES*/', json.dumps(pieces)).replace('/*META*/', json.dumps(meta)).replace('/*SHEETS*/', json.dumps(sheets))
open(f'{root}/rakas-payday-v2.html', 'w').write(html); print('html', len(html)//1024, 'KB')
