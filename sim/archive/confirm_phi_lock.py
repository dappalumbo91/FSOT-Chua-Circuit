"""Confirm ring onset vs φ across IC seeds. No new coefficient."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np

from .chua_array import PhysicalNode
from .diagnose_interface import (
    isolated_amp,
    integrate,
    nic_slopes,
    onset_of,
    seed_locked,
)
from .fsot_engine import PHI, assert_pin

OUT = Path(__file__).resolve().parents[1] / "results" / "phi_lock_confirm.json"


def main() -> None:
    assert_pin()
    phys = PhysicalNode()
    a, b = nic_slopes(phys.R_ohm)
    amp_ref = isolated_amp(a, b, phys)
    phi = float(PHI)
    pred_Rc = phys.rc_from_sigma(phi)

    seeds = [1, 2, 3, 5, 8]
    at_phi = []
    for seed in seeds:
        xs = integrate(3, phi, "ring", a, b, phys, t_end=80.0, dt=0.008, seed=seed)
        xt = xs[int(0.7 * len(xs)) :]
        st = seed_locked(xt, amp_ref)
        st["seed"] = seed
        at_phi.append(st)

    per_seed = []
    for seed in seeds:
        lo, hi = 1.45, 1.80
        for _ in range(8):
            mid = 0.5 * (lo + hi)
            xs = integrate(3, mid, "ring", a, b, phys, t_end=80.0, dt=0.008, seed=seed)
            xt = xs[int(0.7 * len(xs)) :]
            if seed_locked(xt, amp_ref)["locked"]:
                hi = mid
            else:
                lo = mid
        per_seed.append(hi)

    mean_sigma = float(np.mean(per_seed))
    std_sigma = float(np.std(per_seed))
    mean_Rc = phys.rc_from_sigma(mean_sigma)
    err = abs(pred_Rc - mean_Rc) / mean_Rc * 100.0
    err_sig = abs(phi - mean_sigma) / mean_sigma * 100.0
    phi_lock_rate = float(np.mean([1.0 if r["locked"] else 0.0 for r in at_phi]))

    doc = {
        "phi": phi,
        "pred_R_c_ohm": pred_Rc,
        "formula": "σ_c = φ,  R_c = α R / φ  (3 identical nodes on a ring, BOM NIC)",
        "amp_ref": amp_ref,
        "lock_at_phi_by_seed": at_phi,
        "phi_lock_rate": phi_lock_rate,
        "onset_sigma_by_seed": per_seed,
        "onset_sigma_mean": mean_sigma,
        "onset_sigma_std": std_sigma,
        "onset_R_c_mean": mean_Rc,
        "error_pct_R_c": err,
        "error_pct_sigma": err_sig,
        "green_half_pct": err <= 0.5,
        "aspiration_0_05": err <= 0.05,
    }
    OUT.write_text(json.dumps(doc, indent=2), encoding="utf-8")
    print(f"φ={phi:.12f}  pred R_c={pred_Rc:.4f} Ω")
    print(f"lock at σ=φ rate {phi_lock_rate:.2f} over seeds {seeds}")
    print(f"onset σ mean={mean_sigma:.6f} std={std_sigma:.6f}  vs φ err={err_sig:.4f}%")
    print(f"onset R_c mean={mean_Rc:.4f} vs pred {pred_Rc:.4f}  err={err:.4f}%  green={err<=0.5}")
    print("wrote", OUT)


if __name__ == "__main__":
    main()
