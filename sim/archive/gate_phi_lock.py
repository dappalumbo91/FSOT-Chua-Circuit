"""Green gate: at σ=φ the ring locks; at σ=0 it does not. Seed-closed cuts only."""

from __future__ import annotations

import json
from pathlib import Path

from .chua_array import PhysicalNode
from .diagnose_interface import isolated_amp, integrate, nic_slopes, seed_locked
from .fsot_engine import PHI, assert_pin

OUT = Path(__file__).resolve().parents[1] / "results" / "phi_lock_gate.json"
SEEDS = (1, 2, 3, 5, 8, 13)


def rate(sig, a, b, phys, amp_ref) -> list:
    rows = []
    for seed in SEEDS:
        xs = integrate(3, float(sig), "ring", a, b, phys, t_end=80.0, dt=0.008, seed=seed)
        xt = xs[int(0.7 * len(xs)) :]
        st = seed_locked(xt, amp_ref)
        st["seed"] = seed
        st["sigma"] = float(sig)
        rows.append(st)
    return rows


def main() -> None:
    assert_pin()
    phys = PhysicalNode()
    a, b = nic_slopes(phys.R_ohm)
    amp_ref = isolated_amp(a, b, phys)
    phi = float(PHI)
    points = {
        "open": 0.0,
        "below_phi": 1.0,
        "phi": phi,
        "phi_sq": phi * phi,
    }
    report = {"amp_ref": amp_ref, "points": {}}
    for name, sig in points.items():
        rows = rate(sig, a, b, phys, amp_ref)
        lock_rate = sum(1 for r in rows if r["locked"]) / len(rows)
        report["points"][name] = {
            "sigma": sig,
            "R_c_ohm": phys.rc_from_sigma(sig) if sig else None,
            "lock_rate": lock_rate,
            "rows": rows,
        }
        print(f"{name:10s} σ={sig:.4f}  lock_rate={lock_rate:.2f}")
    open_ok = report["points"]["open"]["lock_rate"] == 0.0
    phi_ok = report["points"]["phi"]["lock_rate"] == 1.0
    phi2_ok = report["points"]["phi_sq"]["lock_rate"] == 1.0
    report["gates"] = {
        "open_unlocked": open_ok,
        "phi_locked": phi_ok,
        "phi_sq_locked": phi2_ok,
        "overall_ok": bool(open_ok and phi_ok and phi2_ok),
    }
    print("GATES", report["gates"])
    OUT.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print("wrote", OUT)


if __name__ == "__main__":
    main()
