#!/usr/bin/env python3
import json, os, glob, collections, numpy as np, matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
from chua_spice import HERE, PHI, TAU, BP2
CPP = os.path.join(HERE, "cpp_ref")  # C++ RK4 6-seed sweeps copied from the C++ r0 sweep
MSF = {0: 2.26, 20: 1.44, 35: 1.05}
fig, ax = plt.subplots(3, 1, figsize=(11, 10), sharex=True)
for a, r0 in zip(ax, (0, 20, 35)):
    rows = [json.loads(l) for l in open(f"{HERE}/out/ring_ideal_r0_{r0}.jsonl")]
    by = collections.defaultdict(list)
    for r in rows: by[r["sigma"]].append(r)
    s = sorted(by); lk = [np.mean([r["lock"] for r in by[x]]) for x in s]
    big = [np.mean([r["maxabs_tail"] > BP2 for r in by[x]]) for x in s]
    a.plot(s, lk, "o-", label="ngspice lock (agree ≤ φ⁻⁴·amp AND max|V_C1| < 6.97 V), 3 ICs", color="C0")
    a.plot(s, big, "s--", ms=4, label="ngspice: on outer large limit cycle (±7.56 V)", color="C3", alpha=.7)
    c = np.genfromtxt(f"{CPP}/r0_{r0}.tsv", skip_header=1, names=True, delimiter="\t")
    cl = np.where(c["mean_tail_maxabs"] < BP2, c["lock_rate"], 0.0)
    o = np.argsort(c["sigma"]); a.plot(c["sigma"][o], cl[o], "-", color="k", lw=1, alpha=.6, label="C++ RK4 (6 seeds), same gates")
    a.axvline(MSF[r0], color="g", ls=":", label=f"C++ master-stability σc = {MSF[r0]}")
    for g, n in [(0.9, "20k"), (1, "18k"), (PHI, "φ"), (PHI ** 2, "φ²")]: a.axvline(g, color="gray", lw=.6); a.text(g, 1.05, n, ha="center", fontsize=8)
    a.set_ylim(-0.05, 1.15); a.set_ylabel("fraction"); a.set_title(f"r0 = {r0} Ω (γ = β·r0/R = {14.7273*r0/1800:.3f}), 2000 τ, ideal op-amp clamp ±23/3 V", fontsize=10)
    a.legend(fontsize=7, loc="center left")
ax[-1].set_xlabel("σ = αR/Rc"); ax[-1].set_xlim(0, 2.75)
fig.tight_layout(); fig.savefig(f"{HERE}/plots/spice_ring_lock_vs_sigma.png", dpi=130)
# time series of the gates (seed 1, r0 = 0)
fig, ax = plt.subplots(4, 2, figsize=(13, 11), gridspec_kw=dict(width_ratios=[3, 1]))
for i, (sg, lab) in enumerate([(0.0, "open (σ=0)"), (0.9, "20 kΩ (σ=0.9)"), (PHI, "11 124.61 Ω (σ=φ)"), (PHI ** 2, "6 875.39 Ω (σ=φ²)")]):
    f = glob.glob(f"{HERE}/out/ring_ideal_r00_k1_s{sg:.5f}_seed1.dat")
    if not f: continue
    d = np.loadtxt(f[0], skiprows=1); t = d[:, 0] / TAU
    m = t > 1900
    for j, n in enumerate("ABC"): ax[i, 0].plot(t[m], d[m, 1 + 2 * j], lw=.7, label=f"V_C1{n}")
    ax[i, 0].set_title(f"ngspice ring, r0=0, Rc = {lab}: last 100 τ", fontsize=9); ax[i, 0].set_ylabel("V"); ax[i, 0].legend(fontsize=7, loc="upper right")
    ax[i, 1].plot(d[m, 1], d[m, 3], lw=.4); ax[i, 1].set_xlabel("V_C1A"); ax[i, 1].set_ylabel("V_C1B"); ax[i, 1].set_title("sync plot", fontsize=9)
ax[-1, 0].set_xlabel("t / τ (τ = 180 µs)")
fig.tight_layout(); fig.savefig(f"{HERE}/plots/spice_ring_gates_time_series.png", dpi=120)
