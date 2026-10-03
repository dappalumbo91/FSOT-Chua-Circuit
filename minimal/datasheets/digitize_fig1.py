"""Digitise Vishay 1N4148 Fig. 1 (typical V_F vs T_j) from the 400-dpi render of page 2 (crop fig1.png). Calibration uses the plot frame: left edge = -40 C, right = 160 C, bottom = 0 V, top = 1.0 V."""
import numpy as np, json
from PIL import Image
a = np.asarray(Image.open('fig1.png').convert('RGB')).astype(int); H, W, _ = a.shape
dark = (a.sum(2) < 150)
cols = np.where(dark.sum(0) > 0.6 * H * 0.75)[0]; rows = np.where(dark.sum(1) > 0.5 * W * 0.6)[0]
x0, x1 = cols.min(), cols.max(); y0, y1 = rows.min(), rows.max()  # frame
T = lambda px: -40 + (px - x0) / (x1 - x0) * 200
V = lambda py: 1.0 - (py - y0) / (y1 - y0) * 1.0
R, G, B = a[..., 0], a[..., 1], a[..., 2]
masks = {'100mA': (R > 200) & (G < 80) & (B < 80), '10mA': (G > 150) & (R < 140) & (B < 120), '1mA': (R > 220) & (G > 70) & (G < 150) & (B < 90), '0.1mA': (B > 180) & (R < 120) & (G > 100) & (G < 190)}
out = {}
for k, m in masks.items():
    ys, xs = np.where(m); keep = (xs > x0 + 3) & (xs < x1 - 3); xs, ys = xs[keep], ys[keep]
    t = T(xs); v = V(ys); p = np.polyfit(t, v, 1)
    out[k] = dict(V25=float(np.polyval(p, 25)), tempco_mV_per_K=float(p[0] * 1e3), npix=int(len(xs)))
out['frame_px'] = [int(x0), int(x1), int(y0), int(y1)]
print(json.dumps(out, indent=1)); json.dump(out, open('fig1_digitized.json', 'w'), indent=1)
