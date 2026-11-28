import sys, numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage as ndi
def components(path, bg_thresh=228, min_area=400, close_necks=False):
    im = np.array(Image.open(path).convert('RGB')).astype(np.float32)
    L = im.mean(axis=2)
    dark = L < bg_thresh
    if close_necks:
        lab, n = ndi.label(ndi.binary_dilation(dark, iterations=3))
        for i, sl in enumerate(ndi.find_objects(lab), 1):
            comp = (lab[sl] == i) & dark[sl]
            if comp.sum() < 2000: continue
            ys = np.where(comp.any(axis=1))[0]
            y = ys[-1] - 4
            xs = np.where(comp[y])[0]
            if len(xs) >= 2:
                dark[sl][y-2:y+3, xs[0]:xs[-1]+1] = True
    # background = non-dark connected to border
    bgc = ~dark
    lab, n = ndi.label(bgc)
    border = set(np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]]))) - {0}
    bg = np.isin(lab, list(border))
    fg = ~bg
    lab, n = ndi.label(ndi.binary_dilation(fg, iterations=2))
    out = []
    for i, sl in enumerate(ndi.find_objects(lab), 1):
        m = (lab == i) & fg
        a = m.sum()
        if a < min_area: continue
        ys, xs = np.where(m)
        out.append(dict(id=len(out), box=(xs.min(), ys.min(), xs.max()+1, ys.max()+1), area=int(a), mask=m))
    return im, L, bg, out

def cut(im, L, bg, c, pad=3):
    x0, y0, x1, y1 = c['box']
    m = c['mask']
    # outer ring: distance to background small -> ink with alpha from luminance
    dist = ndi.distance_transform_edt(~bg)
    alpha = np.where(m, 1.0, 0.0)
    ring = m & (dist <= 2.0)
    alpha[ring] = np.clip((255 - L[ring]) / 160.0, 0, 1)
    rgb = im.copy()
    rgb[ring] = np.minimum(rgb[ring], 20)
    sl = (slice(max(y0-pad,0), y1+pad), slice(max(x0-pad,0), x1+pad))
    rgba = np.dstack([rgb[sl], (alpha[sl]*255)]).astype(np.uint8)
    return Image.fromarray(rgba, 'RGBA'), (max(x0-pad,0), max(y0-pad,0))

if __name__ == '__main__':
    path = sys.argv[1]; dbg = sys.argv[2]
    im, L, bg, comps = components(path, close_necks='faces' in path)
    d = Image.open(path).convert('RGB'); dr = ImageDraw.Draw(d)
    for c in comps:
        dr.rectangle(c['box'], outline=(255,0,0), width=2)
        dr.text((c['box'][0]+4, c['box'][1]+4), str(c['id']), fill=(255,0,0))
        print(c['id'], c['box'], c['area'])
    d.save(dbg)
