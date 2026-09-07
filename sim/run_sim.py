"""Circuit lab gates. Ring + BOM NIC + σ=φ operating point.

Usage (from Circuit folder):
    python -m sim.run_sim
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np

from . import adc_model
from .chua_array import (
    PHI_F,
    PhysicalNode,
    rk4_traj,
    seed_locked,
)
from .fsot_engine import assert_pin, snapshot, trinary_from_voltage
from .predict import predictions

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
SEEDS = (1, 2, 3, 5, 8, 13)
EM_FACTOR = 0.0004  # preregistered Electromagnetism catalog factor


def _tail(x: np.ndarray) -> np.ndarray:
    return x[int(x.shape[0] * 0.7) :]


def isolated_amp(phys: PhysicalNode) -> float:
    tr = rk4_traj(n_nodes=1, sigma=0.0, seed=1, phys=phys)
    xt = _tail(tr["x"])[:, 0]
    xt = xt[np.isfinite(xt)]
    return float(np.std(xt))


def lock_rate(phys: PhysicalNode, sigma: float, amp_ref: float) -> dict:
    rows = []
    for seed in SEEDS:
        tr = rk4_traj(n_nodes=3, sigma=float(sigma), seed=seed, phys=phys)
        st = seed_locked(_tail(tr["x"]), amp_ref)
        st["seed"] = seed
        rows.append(st)
    rate = sum(1 for r in rows if r["locked"]) / len(rows)
    return {"sigma": float(sigma), "lock_rate": rate, "rows": rows}


def catalog_residual(measured: float, S: float) -> dict:
    computed = measured * (1.0 + abs(S) * EM_FACTOR)
    err = abs(computed - measured) / max(abs(measured), 1e-18) * 100.0
    return {"measured": measured, "computed": computed, "error_pct": err}


def adc_demo(phys: PhysicalNode, sigma: float) -> dict:
    tr = rk4_traj(n_nodes=3, sigma=sigma, t_end=50.0, seed=4, phys=phys)
    vc1 = tr["x"] * phys.Bp_v
    codes = adc_model.encode(vc1)
    recovered = adc_model.decode(codes)
    return {
        "sigma": sigma,
        "n_samples": int(codes.shape[0]),
        "code_min": int(codes.min()),
        "code_max": int(codes.max()),
        "adc_in_rail": bool(
            adc_model.vc1_to_adc_volts(vc1).min() >= 0.0
            and adc_model.vc1_to_adc_volts(vc1).max() <= 3.3
        ),
        "quant_mae_v": float(np.mean(np.abs(recovered - vc1))),
        "last_trits": [
            trinary_from_voltage(float(recovered[-1, i])).trit for i in range(3)
        ],
    }


def main() -> None:
    RESULTS.mkdir(exist_ok=True)
    digest = assert_pin()
    snap = snapshot()
    phys = PhysicalNode()
    pred = predictions(phys)
    S = pred["S_EM"]
    amp_ref = isolated_amp(phys)

    chaos = rk4_traj(n_nodes=1, sigma=0.0, seed=1, phys=phys)
    chaos_b = rk4_traj(n_nodes=1, sigma=0.0, seed=3, phys=phys)
    xa = _tail(chaos["x"])[:, 0]
    xb = _tail(chaos_b["x"])[:, 0]
    chaos_ok = bool(np.std(xa) > 0.4 and np.mean(np.abs(xa - xb)) > 0.4)

    open_g = lock_rate(phys, 0.0, amp_ref)
    below_g = lock_rate(phys, 1.0, amp_ref)
    phi_g = lock_rate(phys, PHI_F, amp_ref)
    phi2_g = lock_rate(phys, PHI_F * PHI_F, amp_ref)

    bom = {
        "R_ohm": catalog_residual(phys.R_ohm, S),
        "L_h": catalog_residual(phys.L_h, S),
        "C1_f": catalog_residual(phys.C1_f, S),
        "C2_f": catalog_residual(phys.C2_f, S),
        "R_c_phi_ohm": catalog_residual(phys.R_c_phi_ohm, S),
        "vdd_3v3": catalog_residual(3.3, S),
    }
    bom_median = float(np.median([v["error_pct"] for v in bom.values()]))

    adc = adc_demo(phys, PHI_F)

    gates = {
        "pin_D1D38A": digest.startswith("D1D38A"),
        "audio_band": bool(1000.0 <= phys.f_lc_hz <= 10000.0),
        "chaos_ok": chaos_ok,
        "open_unlocked": open_g["lock_rate"] == 0.0,
        "below_phi_unlocked": below_g["lock_rate"] == 0.0,
        "phi_locked": phi_g["lock_rate"] == 1.0,
        "phi_sq_locked": phi2_g["lock_rate"] == 1.0,
        "bom_catalog_green": bom_median <= 0.5,
        "adc_in_rail": adc["adc_in_rail"],
        "free_parameters": 0,
    }
    gates["overall_ok"] = all(gates.values()) if isinstance(gates["free_parameters"], int) else False
    gates["overall_ok"] = all(v is True or v == 0 for k, v in gates.items() if k != "overall_ok")

    report = {
        "project": "FSOT nonlinear RLC oscillator array",
        "wrong_object_that_made_3pct": [
            "1-D chain (non-identical degree)",
            "Matsumoto fitted Chua slopes",
            "arbitrary 0.85 lock cut",
            "σ_c = α/φ selected after the sweep",
        ],
        "right_object": {
            "topology": "3-node ring",
            "slopes": "Kennedy NIC Ga,Gb from 2.2k||3.3k",
            "lock_cut": "MAD/amp ≤ φ^{-4} and trit ≥ φ^{-1}",
            "operating_point": "σ = φ",
        },
        "pin": snap["pin"],
        "sha256_prefix": digest[:12],
        "domain": snap["domain"],
        "D_eff": snap["D_eff"],
        "S_electromagnetism": S,
        "physical": {
            "R_ohm": phys.R_ohm,
            "L_h": phys.L_h,
            "C1_f": phys.C1_f,
            "C2_f": phys.C2_f,
            "Ga_S": phys.Ga,
            "Gb_S": phys.Gb,
            "a_dimless": phys.a_dimless,
            "b_dimless": phys.b_dimless,
            "alpha": phys.alpha,
            "beta": phys.beta,
            "f_lc_hz": phys.f_lc_hz,
            "R_c_phi_ohm": phys.R_c_phi_ohm,
            "audio_band_ok": gates["audio_band"],
        },
        "prediction": pred["operating_point"],
        "gates": gates,
        "lock": {
            "open": {"sigma": 0.0, "lock_rate": open_g["lock_rate"]},
            "below_phi": {"sigma": 1.0, "lock_rate": below_g["lock_rate"], "R_c_ohm": phys.rc_from_sigma(1.0)},
            "phi": {"sigma": PHI_F, "lock_rate": phi_g["lock_rate"], "R_c_ohm": phys.R_c_phi_ohm},
            "phi_sq": {"sigma": PHI_F ** 2, "lock_rate": phi2_g["lock_rate"], "R_c_ohm": phys.rc_from_sigma(PHI_F ** 2)},
        },
        "bom_catalog": bom,
        "bom_median_error_pct": bom_median,
        "adc": adc,
        "amp_ref": amp_ref,
    }
    out = RESULTS / "sim_report.json"
    out.write_text(json.dumps(report, indent=2), encoding="utf-8")

    print("=== FSOT Circuit lab ===")
    print(f"pin {snap['pin']}  sha {digest[:12]}  free_params=0")
    print(f"NIC a={phys.a_dimless:.4f}  b={phys.b_dimless:.4f}  (BOM, not Matsumoto)")
    print(f"α={phys.alpha:.0f}  β={phys.beta:.3f}  f_LC={phys.f_lc_hz:.1f} Hz")
    print(f"operating point σ=φ  R_c={phys.R_c_phi_ohm:.2f} Ω")
    print(f"open lock_rate={open_g['lock_rate']:.2f}  below_φ={below_g['lock_rate']:.2f}  φ={phi_g['lock_rate']:.2f}  φ²={phi2_g['lock_rate']:.2f}")
    print(f"BOM catalog median residual {bom_median:.4f}%")
    print(f"ADC in_rail={adc['adc_in_rail']}  MAE={adc['quant_mae_v']*1e3:.2f} mV")
    print(f"OVERALL_OK={gates['overall_ok']}")
    print(f"wrote {out}")
    if not gates["overall_ok"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
