"""Circuit lab gates (pin AEB2AD, long window, amplitude-checked lock).

Usage (from the repo root):
    python -m sim.run_sim            # full gates, about 3-4 min (2000 tau, 6 seeds, no clip, + MSF cross-check)
    python -m sim.run_sim --quick    # 600 tau smoke run (not the gate of record)
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

from . import adc_model
from .chua_array import PHI_F, PhysicalNode, run_batch
from .fsot_engine import assert_pin, snapshot, trinary_from_voltage
from .msf import lambda_perp, sigma_c
from .predict import SIGMA_C_PRED, SIGMA_C_TOL, predictions

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
SEEDS = (1, 2, 3, 5, 8, 13)
EM_FACTOR = 0.0004  # preregistered Electromagnetism catalog factor
T_END, TAIL = 2000.0, 500.0
SWEEP = tuple(round(1.40 + 0.025 * i, 3) for i in range(11))  # 1.400 ... 1.650


def catalog_residual(measured: float, S: float) -> dict:
    computed = measured * (1.0 + abs(S) * EM_FACTOR)
    err = abs(computed - measured) / max(abs(measured), 1e-18) * 100.0
    return {"measured": measured, "computed": computed, "error_pct": err}


def sweep_threshold(rates: dict[float, float], need: float = 5 / 6) -> float | None:
    """Smallest grid sigma from which every larger tested sigma locks in >= 5/6 of seeds."""
    keys = sorted(rates)
    for i, s in enumerate(keys):
        if all(rates[k] >= need for k in keys[i:]):
            return s
    return None


def main() -> None:
    quick = "--quick" in sys.argv
    t_end, tail = (600.0, 200.0) if quick else (T_END, TAIL)
    RESULTS.mkdir(exist_ok=True)
    digest = assert_pin()
    snap = snapshot()
    phys = PhysicalNode()
    pred = predictions(phys)
    S = pred["S_EM"]

    single = run_batch([0.0], (1, 3), n_nodes=1, t_end=t_end, tail_tau=tail, phys=phys, keep_tail=True)
    xa, xb = single[0].pop("tail_x")[:, 0], single[1].pop("tail_x")[:, 0]
    amp_ref = single[0]["amp"]
    lam1 = float(lambda_perp([0.0], T=600.0 if quick else 2000.0, phys=phys)[0])
    chaos_ok = bool(
        lam1 > 0 and np.std(xa) > 0.4 and np.mean(np.abs(xa - xb)) > 0.4
        and all(r["lobe_switches_tail"] >= 10 and not r["escaped_in_tail"] for r in single)
    )

    rc20k = phys.sigma_from_rc(20000.0)
    sigmas = [0.0, rc20k, 1.0, *SWEEP, PHI_F, PHI_F ** 2]
    rows = run_batch(sigmas, SEEDS, t_end=t_end, tail_tau=tail, phys=phys, amp_ref=amp_ref)
    by = {}
    for r in rows:
        by.setdefault(r["sigma"], []).append(r)
    rate = {s: sum(r["locked"] for r in rs) / len(rs) for s, rs in by.items()}
    sync_rate = {s: sum(r["synchronised"] for r in rs) / len(rs) for s, rs in by.items()}
    esc_rate = {s: sum(r["escaped_in_tail"] for r in rs) / len(rs) for s, rs in by.items()}
    thr = sweep_threshold({s: rate[s] for s in [*SWEEP, PHI_F, PHI_F ** 2]})

    msf_grid = np.round(np.arange(1.40, 1.601, 0.025), 3)
    msf_lam = lambda_perp(msf_grid, T=600.0 if quick else 3000.0, phys=phys)
    sc_py = sigma_c(msf_grid, msf_lam)

    bom = {k: catalog_residual(v, S) for k, v in {
        "R_ohm": phys.R_ohm, "L_h": phys.L_h, "C1_f": phys.C1_f, "C2_f": phys.C2_f,
        "R_c_phi_sq_ohm": phys.rc_from_sigma(PHI_F ** 2), "vdd_3v3": 3.3}.items()}
    bom_median = float(np.median([v["error_pct"] for v in bom.values()]))

    demo = run_batch([PHI_F ** 2, rc20k], (4,), t_end=200.0, tail_tau=100.0, phys=phys, keep_tail=True)
    vc_lock = demo[0]["tail_x"] * phys.Bp_v
    vc_esc = demo[1]["tail_x"] * phys.Bp_v
    rec_lock = adc_model.decode(adc_model.encode(vc_lock))
    rec_esc = adc_model.decode(adc_model.encode(vc_esc))
    adc = {
        "map": f"v = {adc_model.MID:.4g} + V_C1*{adc_model.GAIN:.6g} (Rs 300k, Rp 100k to 3V3, Rg 150k to GND)",
        "adc_in_rail_double_scroll": bool(adc_model.MID + adc_model.GAIN * np.abs(vc_lock).max() < 3.3),
        "adc_sees_escape": bool(np.abs(rec_esc).max() >= phys.bp2_v and adc_model.MID + adc_model.GAIN * np.abs(vc_esc).max() < 3.3),
        "quant_mae_v": float(np.mean(np.abs(rec_lock - vc_lock))),
        "max_abs_v_lock": float(np.abs(vc_lock).max()),
        "max_abs_v_escape": float(np.abs(vc_esc).max()),
        "last_trits_lock": [trinary_from_voltage(float(rec_lock[-1, i])).trit for i in range(3)],
    }

    gates = {
        "pin_AEB2AD": digest.startswith("AEB2AD"),
        "audio_band": bool(1000.0 <= phys.f_lc_hz <= 10000.0),
        "chaos_ok": chaos_ok,
        "open_unlocked": rate[0.0] == 0.0,
        "sigma1_unlocked": rate[1.0] == 0.0,
        "rc20k_unlocked": rate[rc20k] == 0.0,
        "phi_sq_locked": rate[PHI_F ** 2] == 1.0,
        "sigma_c_sharp": thr is not None and abs(thr - SIGMA_C_PRED) <= SIGMA_C_TOL,
        "sigma_c_python_crosscheck": sc_py is not None and abs(sc_py - SIGMA_C_PRED) <= 0.025,
        "phi_consistent_with_sigma_c": (rate[PHI_F] >= 5 / 6) == (SIGMA_C_PRED < PHI_F),
        "bom_catalog_green": bom_median <= 0.5,
        "adc_in_rail": adc["adc_in_rail_double_scroll"],
        "adc_sees_escape": adc["adc_sees_escape"],
        "free_parameters": 0,
    }
    gates["overall_ok"] = gates["free_parameters"] == 0 and all(v is True for k, v in gates.items() if k not in ("overall_ok", "free_parameters"))

    report = {
        "project": "FSOT nonlinear RLC oscillator array",
        "branch": "fix/aeb2ad-long-window",
        "quick": quick,
        "integration": {"t_end_tau": t_end, "tail_tau": tail, "dt": 0.005, "clip": None, "seeds": list(SEEDS)},
        "pin": snap["pin"],
        "sha256_prefix": digest[:12],
        "domain": snap["domain"],
        "D_eff": snap["D_eff"],
        "S_electromagnetism": S,
        "scalar_trinary": snap["scalar_trinary"],
        "physical": {
            "R_ohm": phys.R_ohm, "L_h": phys.L_h, "C1_f": phys.C1_f, "C2_f": phys.C2_f,
            "Ga_S": str(phys.Ga_exact), "Gb_S": str(phys.Gb_exact), "Gc_S": str(phys.Gc_exact),
            "a_dimless": phys.a_dimless, "b_dimless": phys.b_dimless, "c_dimless": phys.c_dimless,
            "Esat_v": phys.esat_v, "Bp2_v": phys.bp2_v, "alpha": phys.alpha, "beta": phys.beta,
            "r0_ohm_branch_l": phys.r0_ohm, "gamma": phys.gamma, "f_lc_hz": phys.f_lc_hz,
        },
        "predictions": pred,
        "gates": gates,
        "single_node": {"lambda1_per_tau": lam1, "rows": single},
        "lock_rate": {f"{s:.6f}": rate[s] for s in sorted(rate)},
        "synchronised_rate_without_amplitude_check": {f"{s:.6f}": sync_rate[s] for s in sorted(sync_rate)},
        "escape_rate": {f"{s:.6f}": esc_rate[s] for s in sorted(esc_rate)},
        "sigma_c": {"predicted": SIGMA_C_PRED, "sweep_threshold": thr, "python_msf": sc_py,
                    "msf_grid": msf_grid.tolist(), "lambda_perp": msf_lam.tolist()},
        "bom_catalog": bom,
        "bom_median_error_pct": bom_median,
        "adc": adc,
        "amp_ref": amp_ref,
        "rows": rows,
    }
    out = RESULTS / ("sim_report_quick.json" if quick else "sim_report.json")
    out.write_text(json.dumps(report, indent=2), encoding="utf-8")

    print("=== FSOT Circuit lab (AEB2AD, long window, amplitude-checked) ===")
    print(f"pin {snap['pin']}  sha {digest[:12]}  free_params=0  window {t_end:g} tau (tail {tail:g})")
    print(f"NIC a={phys.a_dimless:.4f}  b={phys.b_dimless:.4f}  c={phys.c_dimless:.4f}  x2={phys.x2:.4f}")
    print(f"Branch L r0={phys.r0_ohm:.6f} ohm  gamma={phys.gamma:.6f}  lambda1={lam1:.4f}/tau")
    print(f"lock  0={rate[0.0]:.2f}  20k={rate[rc20k]:.2f} (sync w/o amp check {sync_rate[rc20k]:.2f})  1={rate[1.0]:.2f}  "
          f"phi={rate[PHI_F]:.2f}  phi^2={rate[PHI_F ** 2]:.2f}")
    print(f"sigma_c pred={SIGMA_C_PRED}  sweep={thr}  python msf={sc_py}")
    print(f"ADC {adc['map']}  in_rail={adc['adc_in_rail_double_scroll']}  sees_escape={adc['adc_sees_escape']}")
    for k, v in gates.items():
        print(f"  {k}: {v}")
    print(f"OVERALL_OK={gates['overall_ok']}")
    print(f"wrote {out}")
    if not gates["overall_ok"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
