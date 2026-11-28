import base64, io, json, os
from PIL import Image
here = os.path.dirname(os.path.abspath(__file__)); root = os.path.dirname(here)
def uri(img, q=88):
    b = io.BytesIO(); img.save(b, 'WEBP', quality=q, method=6)
    return 'data:image/webp;base64,' + base64.b64encode(b.getvalue()).decode()
assets = {}
for f in sorted(os.listdir(f'{root}/pieces')):
    if f.endswith('.png') and f != 'shadow.png':
        assets[f[:-4]] = uri(Image.open(f'{root}/pieces/{f}'))
assets['plate'] = uri(Image.open(f'{root}/plate.png').convert('RGB'), 86)
sheets = {}
for n in ['parts', 'faces', 'props']:
    im = Image.open(f'{root}/{n}.png').convert('RGB'); im.thumbnail((420, 420)); sheets[n] = uri(im, 80)
im = Image.open(f'{root}/plate.png').convert('RGB'); im.thumbnail((640, 640)); sheets['plate'] = uri(im, 78)
html = open(f'{here}/template.html').read().replace('/*ASSETS*/', json.dumps(assets)).replace('/*SHEETS*/', json.dumps(sheets))
open(f'{root}/rakas-payday.html', 'w').write(html)
print('html', len(html)//1024, 'KB')
