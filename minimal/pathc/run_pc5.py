"""LOCK PC5: ngspice Kennedy-Chua single node at Branch L r0, TI TL082 models, default start. Run from FSOT-Chua-Circuit/spice."""
import sys, json, numpy as np
sys.path.insert(0, '.')
import chua_spice as cs
r0 = 18.4400497592861384; out = {}
for vr in (9.1899, 9.0):
    name = f'out/pc5_tl082_v{vr}.dat'
    d = cs.run(cs.netlist(1, r0=r0, level='tl082', vrail=vr, T_tau=556, outfile=name), name)
    t, x = d[:, 0], d[:, 1]; m = t > 0.01; x = x[m]; t = t[m]
    i = np.where((x[1:-1] > x[:-2]) & (x[1:-1] >= x[2:]))[0] + 1
    tu = np.arange(t[0], t[-1], 2e-6); xu = np.interp(tu, t, x); sp = np.abs(np.fft.rfft((xu - xu.mean()) * np.hanning(len(xu)))); fr = np.fft.rfftfreq(len(xu), 2e-6)
    out[str(vr)] = dict(xmin=float(x.min()), xmax=float(x.max()), n_distinct_maxima=int(len(np.unique(np.round(x[i], 2)))), frac_pos=float(np.mean(x > 1)), frac_neg=float(np.mean(x < -1)),
                        rail_latch=bool(np.abs(x[-len(x)//5:]).min() > 6), f_peak=float(fr[np.argmax(sp * (fr > 200))]))
print(json.dumps(out, indent=1)); json.dump(out, open('/workspace/fsot-chua/minimal/pathc/pc5.json', 'w'), indent=1)
