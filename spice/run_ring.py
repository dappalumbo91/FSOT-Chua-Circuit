#!/usr/bin/env python3
"""3-node Kennedy-Chua ring, coupling Rc on the V_C1 nets (A-B, B-C, C-A); sigma = alpha*R/Rc.
Usage: run_ring.py <opamp level> <r0_ohm> <T_tau> <out.jsonl> sigma [sigma ...]   (sigma=0 -> open ring)
Lock law (task spec): mean pairwise |dV_C1| over the last 40 % <= phi^-4 * std(V_C1A)  AND  max|V_C1| (tail) < Bp2 = 6.970 V."""
import json, os, sys, numpy as np
from multiprocessing import Pool
from chua_spice import *
RAIL = json.load(open(os.path.join(HERE, "out", "rail_calibration.json")))
SEEDS = (1, 2, 3)

def ics(seed):
    g = np.random.default_rng(seed)
    return [(0.1 + 0.05 * i + 0.01 * g.standard_normal(), 0.02 * g.standard_normal()) for i in range(3)]

def job(a):
    lvl, r0, T, sg, seed, k = a
    Rc = rc_of_sigma(sg) if sg > 0 else None
    tag = f"ring_{lvl}_r0{r0:g}_k{k:g}_s{sg:.5f}_seed{seed}"
    out = f"out/{tag}.dat"
    keep = f"{tag}.cir" if seed == 1 else None
    d = run(netlist(3, Rc=Rc, k=k, r0=r0, level=lvl, vrail=RAIL.get(lvl, {}).get("rail_V", 9.0), T_tau=T, ic=ics(seed),
                    outfile=out, title=tag), out, keep_as=keep)
    m = lock_metrics(d, 3)
    if m["t_escape"] is not None: m["t_escape_tau"] = m.pop("t_escape") / (TAU * k)
    else: m.pop("t_escape"); m["t_escape_tau"] = None
    if not (seed == 1 and any(abs(sg - g) < 1e-9 for g in GATES)): os.remove(os.path.join(HERE, out))
    return dict(opamp=lvl, r0=r0, k=k, T_tau=T, sigma=sg, Rc=Rc, seed=seed, **m)

GATES = {0.0, 0.9, 1.0, PHI, PHI ** 2}
if __name__ == "__main__":
    lvl, r0, T, outp = sys.argv[1], float(sys.argv[2]), float(sys.argv[3]), sys.argv[4]
    k = float(os.environ.get("K", "1"))
    sig = [float(s) for s in sys.argv[5:]]
    jobs = [(lvl, r0, T, s, sd, k) for s in sig for sd in (SEEDS if s > 0 else SEEDS[:1])]
    with Pool(int(os.environ.get("NP", "7"))) as p, open(outp, "a") as f:
        for r in p.imap_unordered(job, jobs):
            f.write(json.dumps(r) + "\n"); f.flush()
            print(f"s={r['sigma']:.4f} seed={r['seed']} lock={r['lock']} mad/amp={r['mad_over_amp']:.3g} max={r['maxabs_tail']:.2f} esc={r['t_escape_tau']}", flush=True)
