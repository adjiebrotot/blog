import cv2, numpy as np, json
from PIL import Image
ref = cv2.imread('v2/n34b.png', cv2.IMREAD_GRAYSCALE)
sift = cv2.SIFT_create(contrastThreshold=0.02, edgeThreshold=20)
kr, dr = sift.detectAndCompute(ref, None)
flann = cv2.FlannBasedMatcher(dict(algorithm=1, trees=5), dict(checks=60))
out = {}
for n in ['head0','torso','armN','armF','handN','handF','hips','legN','legF']:
    rgba = np.array(Image.open(f'v2/pieces/{n}.png'))
    g = cv2.cvtColor(rgba[:,:,:3], cv2.COLOR_RGB2GRAY)
    g = np.where(rgba[:,:,3] > 0, g, 255).astype(np.uint8)
    m = (rgba[:,:,3] > 128).astype(np.uint8) * 255
    kp, d = sift.detectAndCompute(g, m)
    if d is None or len(kp) < 4: print(n, 'few kp'); continue
    ms = flann.knnMatch(d, dr, k=2)
    good = [a for a, b in ms if a.distance < 0.8 * b.distance]
    src = np.float32([kp[a.queryIdx].pt for a in good]); dst = np.float32([kr[a.trainIdx].pt for a in good])
    if len(good) < 4: print(n, 'few matches', len(good)); continue
    M, inl = cv2.estimateAffinePartial2D(src, dst, method=cv2.RANSAC, ransacReprojThreshold=4)
    s = float(np.hypot(M[0,0], M[1,0])); r = float(np.degrees(np.arctan2(M[1,0], M[0,0])))
    out[n] = dict(M=M.tolist(), scale=s, rot=r, inliers=int(inl.sum()), matches=len(good))
    print(f'{n:6s} scale {s:.3f} rot {r:6.2f} inliers {int(inl.sum())}/{len(good)} t=({M[0,2]:.0f},{M[1,2]:.0f})')
json.dump(out, open('v2/layout.json','w'), indent=1)
# composite on the reference for checking
base = Image.open('v2/n34b.png').convert('RGBA'); comp = Image.new('RGBA', base.size, (255,255,255,255))
order = ['armF','handF','legF','hips','legN','torso','head0','armN','handN']
for n in order:
    if n not in out: continue
    M = np.array(out[n]['M'])
    rgba = np.array(Image.open(f'v2/pieces/{n}.png'))
    w = cv2.warpAffine(rgba, M, base.size, flags=cv2.INTER_LINEAR, borderValue=(0,0,0,0))
    comp.alpha_composite(Image.fromarray(w, 'RGBA'))
side = Image.new('RGB', (base.width*2, base.height), 'white'); side.paste(base.convert('RGB'), (0,0)); side.paste(comp.convert('RGB'), (base.width, 0))
side.save('v2/compare.png')
