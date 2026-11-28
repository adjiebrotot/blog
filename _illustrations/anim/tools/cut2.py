import json, os, sys, numpy as np
from PIL import Image
from scipy import ndimage as ndi
sys.path.insert(0, 'tools')
from seg import components, cut
os.makedirs('v2/pieces', exist_ok=True)
meta = {}
def save_img(arr, name, extra=None):
    Image.fromarray(arr, 'RGBA').save(f'v2/pieces/{name}.png')
    meta[name] = dict(size=[arr.shape[1], arr.shape[0]], **(extra or {}))

# body pieces and hands: flood-fill masks
for sheet, mp in {
  'parts34': {'head0':0,'armF':1,'armN':2,'torso':3,'handF':4,'handN':5,'legF':6,'legN':7,'hips':8},
  'hands34': {'handN_phone':0,'handN_fist':1,'handN_thumb':2,'handF_wave':3,'handF_wave2':4,'handF_fist':5,'handF_open':6,'handN_palm':7},
}.items():
    im, L, bg, comps = components(f'v2/{sheet}.png')
    for name, i in mp.items():
        img, off = cut(im, L, bg, comps[i])
        a = np.array(img); save_img(a, name, dict(off=list(map(int, off)), sheet=sheet))

# heads: row-span fill, then normalise by the hair box
im = np.array(Image.open('v2/faces34.png').convert('RGB')).astype(np.float32)
L = im.mean(2)
names = ['neutral','blink','smile','laugh','surprise','worried','talk','proud','excited','down','down_worried','down_surprise']
boxes = [(64,38,228,270),(428,38,592,270),(788,38,950,270),(58,289,239,515),(422,289,604,515),(781,289,964,515),
         (58,532,243,760),(423,532,608,760),(781,532,967,760),(59,776,248,1007),(425,777,613,1008),(782,777,970,1007)]
heads = {}
for n, (x0,y0,x1,y1) in zip(names, boxes):
    sub = im[y0-3:y1+3, x0-3:x1+3]; l = L[y0-3:y1+3, x0-3:x1+3]
    dark = l < 200
    lab, k = ndi.label(ndi.binary_dilation(dark, iterations=2))
    sizes = ndi.sum(np.ones_like(l), lab, range(1, k+1)); big = 1 + int(np.argmax(sizes))
    comp = (lab == big)
    mask = np.zeros_like(comp)
    for y in range(comp.shape[0]):
        xs = np.where(comp[y])[0]
        if len(xs): mask[y, xs[0]:xs[-1]+1] = True
    mask = ndi.binary_erosion(mask, iterations=1)
    alpha = mask.astype(np.float32)
    edge = mask & ~ndi.binary_erosion(mask, iterations=2)
    alpha[edge] = np.clip((255 - l[edge]) / 160, 0, 1)
    rgb = sub.copy(); rgb[edge] = np.minimum(rgb[edge], 20)
    hair = (l < 70) & mask
    ys, xs = np.where(hair)
    # hair box from the top 45% of the head (ignores dark mouths)
    top = ys.min() + 0.45 * (ys.max() - ys.min())
    sel = ys < top
    hb = [xs[sel].min(), ys[sel].min(), xs[sel].max(), ys[sel].max()]
    heads[n] = (np.dstack([rgb, alpha*255]).astype(np.uint8), hb)
# reference: neutral; scale every head so its hair width matches, align hair box top-left
ref_w = heads['neutral'][1][2] - heads['neutral'][1][0]
ref = heads['neutral'][1]
for n, (a, hb) in heads.items():
    s = ref_w / (hb[2] - hb[0])
    img = Image.fromarray(a, 'RGBA')
    img = img.resize((round(img.width*s), round(img.height*s)), Image.LANCZOS)
    # offset so that hair box top-left lands on the reference hair box top-left
    dx = ref[0] - hb[0]*s; dy = ref[1] - hb[1]*s
    arr = np.array(img)
    save_img(arr, 'face_'+n, dict(align=[round(dx,1), round(dy,1)], scale=round(s,3)))
json.dump(meta, open('v2/pieces/meta.json','w'), indent=1)
# contact sheet
names = list(meta); W=1500; x=y=10; rowh=0
cs = Image.new('RGBA', (W, 2000), (60,110,70,255))
for n in names:
    p = Image.open(f'v2/pieces/{n}.png')
    if x + p.width > W: x = 10; y += rowh + 10; rowh = 0
    cs.alpha_composite(p, (x, y)); x += p.width + 10; rowh = max(rowh, p.height)
cs.crop((0,0,W,y+rowh+10)).save('v2/contact.png'); print(names)
