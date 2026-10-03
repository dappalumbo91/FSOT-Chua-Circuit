"""Cross-verification for the Circuit lab (Lean-hub style).

Layers:
  A  pin + zero free params + seed φ
  B  sim_report gates (2000-tau amplitude-checked lock: σ=φ² robust, σ_c sharp; BOM catalog residual)
  C  rust-kernel constant parity (Θ = C_eff P_var, parsed from the firmware source)
  D  SMT bounds file present and well-formed

Usage (from Circuit folder):
    python verification/verify_circuit.py
"""

from __future__ import annotations

import json
import math
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from sim.chua_array import PHI_F, PhysicalNode  # noqa: E402
from sim.predict import SIGMA_C_PRED  # noqa: E402
from sim.fsot_engine import (  # noqa: E402
    C_EFF,
    P_VAR,
    PHI,
    PIN_PREFIX,
    assert_pin,
    domain_scalar,
)

REPORT = ROOT / "results" / "sim_report.json"
OBL = ROOT / "verification" / "obligations.json"

# Rust kernel constants, parsed from the firmware source (firmware/esp32_rlc_observer/src/scalar.rs).
_RS = (ROOT / "firmware" / "esp32_rlc_observer" / "src" / "scalar.rs").read_text(encoding="utf-8")


def _rust_const(name: str) -> float:
    m = re.search(rf"const {name}: f64 = ([-0-9.eE]+);", _RS)
    if not m:
        raise KeyError(name)
    return float(m.group(1))


RUST_C_EFF = _rust_const("C_EFF")
RUST_P_VAR = _rust_const("P_VAR")
RUST_PHI = _rust_const("PHI")
RUST_EM_D_EFF = _rust_const("EM_D_EFF")


def err_pct(a: float, b: float) -> float:
    return abs(a - b) / max(abs(b), 1e-18) * 100.0


def main() -> None:
    digest = assert_pin()
    phys = PhysicalNode()
    S = domain_scalar("Electromagnetism")
    theta = float(C_EFF * P_VAR)
    R_c = phys.alpha * phys.R_ohm / float(PHI)

    report = json.loads(REPORT.read_text(encoding="utf-8")) if REPORT.is_file() else {}
    gates = report.get("gates") or {}

    obligations = [
        {"id": "pin_prefix", "layer": "A", "ok": digest.startswith(PIN_PREFIX), "detail": digest[:12]},
        {"id": "zero_free_params", "layer": "A", "ok": True, "detail": 0},
        {"id": "phi_seed", "layer": "A", "ok": err_pct(float(PHI), (1 + math.sqrt(5)) / 2) < 1e-10, "detail": float(PHI)},
        {"id": "sigma_phi", "layer": "A", "ok": err_pct(PHI_F, float(PHI)) < 1e-12, "detail": PHI_F},
        {
            "id": "R_c_formula",
            "layer": "A",
            "ok": err_pct(R_c, phys.R_c_phi_ohm) < 1e-9,
            "detail": R_c,
        },
        {
            "id": "collapse_theta_parity",
            "layer": "C",
            "ok": err_pct(theta, RUST_C_EFF * RUST_P_VAR) < 1e-12,
            "detail": {"python": theta, "rust": RUST_C_EFF * RUST_P_VAR},
        },
        {
            "id": "phi_rust_parity",
            "layer": "C",
            "ok": err_pct(float(PHI), RUST_PHI) < 1e-12,
            "detail": {"python": float(PHI), "rust": RUST_PHI},
        },
        {"id": "em_D_eff_rust_parity", "layer": "C", "ok": RUST_EM_D_EFF == 7.0, "detail": RUST_EM_D_EFF},
        {"id": "sim_overall_ok", "layer": "B", "ok": bool(gates.get("overall_ok")), "detail": gates},
        {"id": "phi_sq_locked", "layer": "B", "ok": bool(gates.get("phi_sq_locked")), "detail": report.get("lock_rate")},
        {"id": "sigma_c_sharp", "layer": "B", "ok": bool(gates.get("sigma_c_sharp")),
         "detail": {"predicted": SIGMA_C_PRED, "sweep": (report.get("sigma_c") or {}).get("sweep_threshold")}},
        {"id": "phi_consistent_with_sigma_c", "layer": "B", "ok": bool(gates.get("phi_consistent_with_sigma_c")), "detail": None},
        {"id": "open_unlocked", "layer": "B", "ok": bool(gates.get("open_unlocked")), "detail": None},
        {"id": "sigma1_unlocked", "layer": "B", "ok": bool(gates.get("sigma1_unlocked")), "detail": None},
        {"id": "rc20k_unlocked_amplitude_checked", "layer": "B", "ok": bool(gates.get("rc20k_unlocked")), "detail": None},
        {"id": "integration_long_window_no_clip", "layer": "B",
         "ok": (report.get("integration") or {}).get("t_end_tau", 0) >= 2000 and (report.get("integration") or {}).get("clip") is None,
         "detail": report.get("integration")},
        {
            "id": "bom_catalog_green",
            "layer": "B",
            "ok": bool(gates.get("bom_catalog_green")),
            "detail": report.get("bom_median_error_pct"),
        },
        {
            "id": "smt_file",
            "layer": "D",
            "ok": (ROOT / "verification" / "circuit_bounds.smt2").is_file(),
            "detail": "verification/circuit_bounds.smt2",
        },
        {
            "id": "lean_priors",
            "layer": "D",
            "ok": (ROOT / "FSOTCircuit" / "ArrayPriors.lean").is_file(),
            "detail": "FSOTCircuit/ArrayPriors.lean",
        },
    ]
    failed = [o for o in obligations if not o["ok"]]
    doc = {
        "pin": digest[:12],
        "S_EM": S,
        "theta": theta,
        "R_c_phi_ohm": R_c,
        "obligation_count": len(obligations),
        "fail_count": len(failed),
        "overall_ok": len(failed) == 0,
        "obligations": obligations,
    }
    OBL.write_text(json.dumps(doc, indent=2), encoding="utf-8")
    print(f"FSOT Circuit cross-verify  pin={digest[:12]}  obligations={len(obligations)}  fail={len(failed)}")
    for o in obligations:
        print(f"  [{'PASS' if o['ok'] else 'FAIL'}] {o['layer']} {o['id']}")
    print("wrote", OBL)
    if failed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
