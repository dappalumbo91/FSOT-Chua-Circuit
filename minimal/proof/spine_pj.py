"""Non-rigorous geometry for the PJ horseshoe: median spine z(y) of the attractor section, then P^k along it (horseshoe_bg map)."""
import numpy as np, subprocess, os, sys
env = dict(os.environ, FSOT_B='0.91751027120648765', FSOT_G='0.73504813634763333')
P = np.loadtxt('sec_pj.txt'); y, z = P[:, 0], P[:, 1]
k = int(sys.argv[1]) if len(sys.argv) > 1 else 1
ys = np.linspace(0.02, 1.90, 377); zs = []
for v in ys:
    m = np.abs(y - v) < 0.01; zs.append(np.median(z[m]) if m.sum() > 3 else np.nan)
zs = np.array(zs); ok = ~np.isnan(zs); ys, zs = ys[ok], zs[ok]
args = []
for a, b in zip(ys, zs): args += ['%.12f' % a, '%.12f' % b]
o = subprocess.run(['./horseshoe_bg', 'map', str(k)] + args, capture_output=True, text=True, env=env).stdout.splitlines()
img = []
for l in o:
    if l.startswith('1'): img.append(float(l.split('y=[')[1].split(',')[0]))
    else: img.append(np.nan)
np.save(f'spine_pj_k{k}.npy', np.c_[ys, zs, img])
for a, b, c in zip(ys[::8], zs[::8], np.array(img)[::8]): print('%.3f %.4f -> %.4f' % (a, b, c))
