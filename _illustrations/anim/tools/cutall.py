import json, numpy as np, sys
sys.path.insert(0, 'tools')
from seg import components, cut
from PIL import Image
import os
os.makedirs('pieces', exist_ok=True)
meta = {}
def save(sheet, comps_ids, name, comps, im, L, bg):
    if isinstance(comps_ids, int): comps_ids = [comps_ids]
    m = np.zeros_like(bg)
    for i in comps_ids: m |= comps[i]['mask']
    ys, xs = np.where(m)
    c = dict(mask=m, box=(xs.min(), ys.min(), xs.max()+1, ys.max()+1))
    img, off = cut(im, L, bg, c)
    img.save(f'pieces/{name}.png')
    meta[name] = dict(sheet=sheet, off=[int(off[0]), int(off[1])], size=list(img.size))
maps = {
 'parts': {'torso':0,'upperR':2,'upperL':3,'hips':4,'foreR':5,'foreL':6,'legR':7,'legL':8,'handR':9,'handL':10},
 'faces': {f'face_{k}':i for i,k in enumerate(['neutral','blink','smile','laugh','surprise','read','ah','oo','proud'])},
 'props': {'handR_wave':0,'handR_phone':1,'handR_thumb':2,'handR_fist':3,'handL_stop':4,'bubble_coin':5,'bubble_bulb':6,'handL_fist':7,
           'dashes':[10,11,12,13,14,17,18],'sparkles':[8,9,15],'shadow':16},
}
for sheet, mp in maps.items():
    im, L, bg, comps = components(sheet+'.png', close_necks=(sheet=='faces'))
    for name, ids in mp.items(): save(sheet, ids, name, comps, im, L, bg)
json.dump(meta, open('pieces/meta.json','w'), indent=1)
# contact sheet on a coloured bg
names = list(meta)
W = 1400; x=y=10; rowh=0
cs = Image.new('RGBA', (W, 1500), (60,110,70,255))
for n in names:
    p = Image.open(f'pieces/{n}.png')
    if x + p.width > W: x = 10; y += rowh + 10; rowh = 0
    cs.alpha_composite(p, (x, y)); x += p.width + 10; rowh = max(rowh, p.height)
cs.crop((0,0,W,y+rowh+10)).save('contact.png')
print(names)
