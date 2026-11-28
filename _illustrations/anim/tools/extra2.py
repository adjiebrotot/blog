import numpy as np, json
from PIL import Image
meta = json.load(open('v2/pieces/meta.json'))
def hairbox(a):
    L = a[:,:,:3].mean(2); m = (L < 70) & (a[:,:,3] > 200)
    ys, xs = np.where(m); top = ys.min() + 0.45*(ys.max()-ys.min()); s = ys < top
    return [int(v) for v in (xs[s].min(), ys[s].min(), xs[s].max(), ys[s].max())]
rb = hairbox(np.array(Image.open('v2/pieces/face_neutral.png')))
fb = hairbox(np.array(Image.open('pieces/face_neutral.png')))
s = (rb[3]-rb[1]) / (fb[3]-fb[1])
for n in ['neutral','smile','laugh','proud','blink']:
    im = Image.open(f'pieces/face_{n}.png'); im = im.resize((round(im.width*s), round(im.height*s)), Image.LANCZOS)
    hb = hairbox(np.array(im))
    dx = 85 - (hb[0]+hb[2])/2 + 6; dy = rb[1] - hb[1]
    im.save(f'v2/pieces/front_{n}.png'); meta[f'front_{n}'] = dict(size=[im.width, im.height], align=[round(float(dx),1), round(float(dy),1)])
for n in ['dashes','sparkles','bubble_coin']:
    im = Image.open(f'pieces/{n}.png'); im.save(f'v2/pieces/fx_{n}.png'); meta[f'fx_{n}'] = dict(size=[im.width, im.height])
for n in ['legN','legF']:
    a = np.array(Image.open(f'v2/pieces/{n}.png')).astype(np.float32)
    y = np.arange(a.shape[0])[:, None]; a[:,:,3] *= np.clip((y - 30)/40.0, 0, 1)
    Image.fromarray(a.astype(np.uint8), 'RGBA').save(f'v2/pieces/{n}.png')
json.dump(meta, open('v2/pieces/meta.json','w'), indent=1)
print({k: v.get('align') for k, v in meta.items() if 'align' in v})
