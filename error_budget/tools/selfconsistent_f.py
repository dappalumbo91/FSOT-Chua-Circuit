"""Self-consistent frequency-dependent Branch-L r0: r0(f) = k * 2*pi*f*L, f measured on the single-node attractor at r0(f).
Variant 'rot': f = zero-crossing rate of y (vC2) = scroll rotation frequency. Variant 'rms': f = sqrt(<f^2>) of the i_L (z) power spectrum."""
import subprocess, sys, numpy as np, json
from mpmath import mp, mpf, sqrt
mp.dps = 40
S_EM = mpf('0.9557285700955828'); ALPHA = mpf('0.0008082937414140405')  # repo fsot_engine (vendored authority) values
k = sqrt((1 + abs(S_EM) * ALPHA) ** 2 - 1); L = 0.022; C2 = 100e-9; tau = 1800 * C2; dts = 0.05 * tau
fLC = 1 / (2 * np.pi * np.sqrt(L * C2))
def meas(r):
    out = subprocess.run(['./build/mc', 'dump', f'r={r:.12f}', 'T=40000', 'every=10'], capture_output=True, text=True).stdout
    d = np.array([list(map(float, l.split())) for l in out.splitlines()])
    y = d[:, 1]; frot = np.sum(np.diff(np.sign(y)) != 0) / 2 / (len(y) * dts)
    z = d[:, 2] - d[:, 2].mean(); seg = 2 ** 15; w = np.hanning(seg); P = 0
    for i in range(0, len(z) - seg, seg // 2): P = P + np.abs(np.fft.rfft(z[i:i + seg] * w)) ** 2
    f = np.fft.rfftfreq(seg, dts); m = f > 0; frms = np.sqrt((f[m] ** 2 * P[m]).sum() / P[m].sum())
    return frot, frms, np.abs(d[:, 0]).max()
res = {}
for var in ['rot', 'rms']:
    r = float(k) * np.sqrt(L / C2); hist = []
    for it in range(8):
        frot, frms, mx = meas(r); f = frot if var == 'rot' else frms
        rn = float(k) * 2 * np.pi * f * L; hist.append((r, f, mx)); print(var, it, f'r={r:.4f} f={f:.1f} maxabs={mx:.3f} -> r_new={rn:.4f}', flush=True)
        if abs(rn - r) < 1e-3: r = rn; break
        r = 0.5 * r + 0.5 * rn
    res[var] = {'r0_ohm': r, 'f_Hz': f, 'history': hist}
res['k'] = float(k); res['f_LC'] = fLC
json.dump(res, open('results/selfconsistent_f.json', 'w'), indent=1)
