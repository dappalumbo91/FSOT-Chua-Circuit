#!/usr/bin/env python3
"""Single Kennedy-Chua node (sigma=0): double scroll check for every op-amp level, x1 and x10."""
import json, os, sys, numpy as np, matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
from chua_spice import *
RAIL = json.load(open(os.path.join(HERE, "out", "rail_calibration.json")))
T_TAU = 500
cases = [("ideal", 1), ("gbw", 1), ("tl082", 1), ("ua741", 1), ("ideal", 10), ("tl082", 10), ("ua741", 10)]
res = {}; data = {}
for lvl, k in cases:
    vr = RAIL[lvl]["rail_V"] if lvl in RAIL else 9.0
    tag = f"single_{lvl}_k{k}"
    net = netlist(1, k=k, level=lvl, vrail=vr, T_tau=T_TAU, outfile=f"out/{tag}.dat", title=tag)
    d = run(net, f"out/{tag}.dat", keep_as=f"{tag}.cir")
    t, v1, v2 = d[:, 0], d[:, 1], d[:, 2]
    m = t > 50 * TAU * k
    s = np.sign(v1[m]); s = s[np.abs(v1[m]) > 0.5]
    sw = int(np.sum(s[1:] != s[:-1]))
    x = v2[m] - v2[m].mean(); dt = t[1] - t[0]
    F = np.abs(np.fft.rfft(x * np.hanning(len(x)))); f = np.fft.rfftfreq(len(x), dt)
    fpk = float(f[np.argmax(F[1:]) + 1])
    res[tag] = dict(opamp=lvl, k=k, rail_V=vr, v1_min=float(v1[m].min()), v1_max=float(v1[m].max()), v1_rms=float(np.sqrt(np.mean(v1[m]**2))),
                    v2_min=float(v2[m].min()), v2_max=float(v2[m].max()), lobe_switches=sw, switches_per_100tau=sw / ((T_TAU - 50) / 100),
                    v2_spectrum_peak_Hz=fpk, v2_peak_Hz_times_k=fpk * k, double_scroll=bool(sw > 10 and v1[m].min() < -1 and v1[m].max() > 1),
                    escaped_outer=bool(np.abs(v1).max() > BP2))
    data[tag] = (t, v1, v2, f, F)
    print(tag, json.dumps(res[tag]))
json.dump(res, open(os.path.join(HERE, "out", "single_node_results.json"), "w"), indent=1)
# plots
fig, ax = plt.subplots(2, 2, figsize=(12, 10))
for a, tag in zip(ax.flat, ["single_ideal_k1", "single_tl082_k1", "single_ua741_k1", "single_tl082_k10"]):
    t, v1, v2, *_ = data[tag]; m = t > 50 * TAU * res[tag]["k"]
    a.plot(v1[m], v2[m], lw=0.25, color="navy"); a.set_xlabel("V(C1) [V]"); a.set_ylabel("V(C2) [V]")
    r = res[tag]; a.set_title(f"{tag}: V_C1 {r['v1_min']:.2f}..{r['v1_max']:.2f} V, {r['lobe_switches']} switches/{T_TAU-50}τ")
    a.grid(alpha=.3)
fig.suptitle("ngspice: Kennedy-Chua node, BOM values, Esat=23/3 V (rails calibrated), double scroll")
fig.tight_layout(); fig.savefig(os.path.join(HERE, "plots", "spice_double_scroll.png"), dpi=130)
fig, ax = plt.subplots(3, 1, figsize=(12, 9))
t, v1, v2, f, F = data["single_tl082_k1"]
m = (t > 100 * TAU) & (t < 200 * TAU)
ax[0].plot(t[m] * 1e3, v1[m], lw=.6); ax[0].set_ylabel("V(C1) [V]"); ax[0].axhline(1, ls=":", c="k"); ax[0].axhline(-1, ls=":", c="k")
ax[1].plot(t[m] * 1e3, v2[m], lw=.6, c="C1"); ax[1].set_ylabel("V(C2) [V]"); ax[1].set_xlabel("t [ms]")
ax[2].semilogy(f, F, lw=.6); ax[2].set_xlim(0, 8000); ax[2].set_xlabel("f [Hz]"); ax[2].set_ylabel("|FFT V(C2)|")
ax[2].set_title(f"spectrum peak {res['single_tl082_k1']['v2_spectrum_peak_Hz']:.0f} Hz")
ax[0].set_title("ngspice, TL082 macromodel, rails ±%.3f V, x1" % RAIL["tl082"]["rail_V"])
fig.tight_layout(); fig.savefig(os.path.join(HERE, "plots", "spice_time_series_spectrum_tl082.png"), dpi=130)
