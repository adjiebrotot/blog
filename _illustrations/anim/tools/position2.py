import cv2, numpy as np, json
from PIL import Image
ref = cv2.imread('v2/n34b.png', cv2.IMREAD_GRAYSCALE).astype(np.float32)
lay = json.load(open('v2/layout.json'))
S = (lay['head0']['scale'] + lay['torso']['scale']) / 2
print('global scale', S)
def place(n, rots=np.arange(-10, 10.1, 1.0), region=None):
    rgba = np.array(Image.open(f'v2/pieces/{n}.png'))
    best = None
    for r in rots:
        h, w = rgba.shape[:2]
        M = cv2.getRotationMatrix2D((w/2, h/2), -r, S)
        c, s_ = abs(M[0,0]), abs(M[0,1]); nw, nh = int(w*c + h*s_) + 2, int(w*s_ + h*c) + 2
        M[0,2] += nw/2 - w/2; M[1,2] += nh/2 - h/2
        t = cv2.warpAffine(rgba, M, (nw, nh), flags=cv2.INTER_LINEAR, borderValue=(0,0,0,0))
        g = cv2.cvtColor(t[:,:,:3], cv2.COLOR_RGB2GRAY).astype(np.float32); m = (t[:,:,3] > 200).astype(np.float32)
        x0, y0, x1, y1 = region
        area = ref[y0:y1, x0:x1]
        if area.shape[0] < nh or area.shape[1] < nw: continue
        res = cv2.matchTemplate(area, g, cv2.TM_SQDIFF, mask=m)
        res = res / m.sum()
        mn, _, loc, _ = cv2.minMaxLoc(res)
        if best is None or mn < best[0]:
            A = np.vstack([M, [0,0,1]]); T = np.array([[1,0,x0+loc[0]],[0,1,y0+loc[1]],[0,0,1]])
            best = (mn, r, (T @ A)[:2].tolist())
    print(n, 'rot', best[1], 'err', round(best[0], 1))
    lay[n] = dict(M=best[2], scale=S, rot=best[1], method='template')
regions = {'armN': (230, 250, 420, 820), 'armF': (520, 250, 680, 820), 'hips': (300, 560, 620, 860),
           'legN': (280, 560, 520, 1180), 'legF': (420, 560, 680, 1180), 'handF': (540, 580, 680, 800)}
for n, reg in regions.items(): place(n, region=reg)
json.dump(lay, open('v2/layout.json','w'), indent=1)
base = Image.open('v2/n34b.png').convert('RGBA'); comp = Image.new('RGBA', base.size, (255,255,255,255))
for n in ['armF','handF','legF','hips','legN','torso','head0','armN','handN']:
    M = np.array(lay[n]['M']); rgba = np.array(Image.open(f'v2/pieces/{n}.png'))
    w = cv2.warpAffine(rgba, M, base.size, flags=cv2.INTER_LINEAR, borderValue=(0,0,0,0))
    comp.alpha_composite(Image.fromarray(w, 'RGBA'))
side = Image.new('RGB', (base.width*2, base.height), 'white'); side.paste(base.convert('RGB'), (0,0)); side.paste(comp.convert('RGB'), (base.width, 0))
side.save('v2/compare2.png')
