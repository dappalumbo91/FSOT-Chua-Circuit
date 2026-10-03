#!/usr/bin/env python3
"""Generate and run ngspice netlists for the FSOT Kennedy-Chua node / 3-node ring.

Op-amp levels:
  ideal  : OPAMP_GBW with A0=1e6, GBW=1 GHz, hard clamp +/-Esat   [level (a), ~ideal]
  gbw    : OPAMP_GBW   (single pole, A0=1e6, GBW=100 MHz, clamp)     [level (a), dynamic]
  tl082  : TI TL082 macromodel (SLOJ070, fetched by fetch_models.sh) [level (b)]
  ua741  : uA741 macromodel (TI Parts 4.01, via KiCad-Spice-Library)  [level (b)]
"""
import math, os, subprocess, tempfile, numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
PHI = (1 + 5 ** 0.5) / 2
ESAT = 23.0 / 3.0
R, C2, ALPHA = 1800.0, 100e-9, 10.0
TAU = R * C2  # 180 us at k=1
BP2 = ESAT * 2200 / 2420  # 6.970 V

VENDOR = {"tl082": ("models/vendor/ti_sloj070/TL082.301", "TL082"),
          "ua741": ("models/vendor/ua741.mod", "UA741")}

def opa_block(level, gbw=100e6):
    if level == "ideal":
        gbw = 1e9
        level = "gbw"
    if level == "gbw":
        return [".include models/opamp_beh.lib",
                ".subckt OPA inp inn vcc vee out", f"X inp inn vcc vee out OPAMP_GBW GBW={gbw:g}", ".ends OPA"]
    f, name = VENDOR[level]
    return [f".include {f}", ".subckt OPA inp inn vcc vee out", f"X inp inn vcc vee out {name}", ".ends OPA"]

def rc_of_sigma(s):
    return ALPHA * R / s

def netlist(n_nodes=1, Rc=None, k=1.0, r0=0.0, level="ideal", vrail=9.0, T_tau=500,
            ic=None, tmax_frac=None, dt_out_frac=0.01, outfile="out.dat", gbw=100e6, title=None):
    tau = TAU * k
    T = T_tau * tau
    names = "abc"[:n_nodes]
    L = [f"* {title or 'FSOT Kennedy-Chua'}: nodes={n_nodes} Rc={Rc} k={k} r0={r0} opamp={level} rails=+/-{vrail}",
         ".include models/chua_node.lib"] + opa_block(level, gbw)
    L += [f"Vcc vcc 0 {vrail}", f"Vee vee 0 {-vrail}"]
    for n in names:
        L.append(f"X{n} {n}1 {n}2 vcc vee CHUA_NODE k={k:g} r0={r0:g}")
    if n_nodes > 1 and Rc is not None and math.isfinite(Rc):
        for i in range(n_nodes):
            a, b = names[i], names[(i + 1) % n_nodes]
            if n_nodes == 2 and i == 1: break
            L.append(f"Rc{a}{b} {a}1 {b}1 {Rc:.6g}")
    if ic is None:
        ic = [(0.1 + 0.05 * i, 0.0) for i in range(n_nodes)]
    L.append(".ic " + " ".join(f"v({n}1)={v1:.6g} v({n}2)={v2:.6g}" for n, (v1, v2) in zip(names, ic)))
    tmax = (tmax_frac or 0.002) * tau
    dto = dt_out_frac * tau
    L += [".options method=gear reltol=1e-4 abstol=1e-10 vntol=1e-7 itl4=100",
          f".tran {dto:.6g} {T:.6g} 0 {tmax:.6g} uic",
          ".control", "set filetype=ascii", "run",
          f"linearize " + " ".join(f"v({n}1) v({n}2)" for n in names),
          "set wr_singlescale", "set wr_vecnames",
          f"wrdata {outfile} " + " ".join(f"v({n}1) v({n}2)" for n in names) + (" i(vcc)" if False else ""),
          "quit", ".endc", ".end"]
    return "\n".join(L) + "\n"

def run(net, outfile, keep_as=None):
    p = os.path.join(HERE, "netlists", keep_as) if keep_as else tempfile.mktemp(suffix=".cir", dir=os.path.join(HERE, "out"))
    with open(p, "w") as f:
        f.write(net)
    r = subprocess.run(["ngspice", "-b", p], cwd=HERE, capture_output=True, text=True)
    if r.returncode != 0 or not os.path.exists(os.path.join(HERE, outfile)):
        raise RuntimeError(r.stdout[-2000:] + r.stderr[-2000:])
    if not keep_as: os.remove(p)
    d = np.loadtxt(os.path.join(HERE, outfile), skiprows=1)
    return d  # columns: t, then v(x1) v(x2) per node

def lock_metrics(d, n_nodes, tail=0.6):
    t = d[:, 0]
    i0 = int(tail * len(t))
    v1 = np.stack([d[:, 1 + 2 * i] for i in range(n_nodes)])
    x = v1[:, i0:]
    amp = x[0].std()
    mad = np.mean((np.abs(x[0] - x[1]) + np.abs(x[0] - x[2]) + np.abs(x[1] - x[2])) / 3) if n_nodes == 3 else float("nan")
    tr = np.where(x < -1, -1, np.where(x > 1, 1, 0))
    agree = np.mean((tr[0] == tr[1]) & (tr[1] == tr[2])) if n_nodes == 3 else float("nan")
    maxabs_tail = np.abs(x).max()
    esc = np.abs(v1) > BP2
    t_esc = t[np.argmax(esc.any(0))] if esc.any() else None
    mad_amp = mad / max(amp, 1e-12)
    lock = bool(mad_amp <= PHI ** -4 and maxabs_tail < BP2)
    return dict(amp=float(amp), mad_over_amp=float(mad_amp), trit_agree=float(agree),
                maxabs_tail=float(maxabs_tail), t_escape=t_esc, lock=lock)
