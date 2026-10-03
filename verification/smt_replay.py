"""Python replay of verification/circuit_bounds.smt2.

Always available (mpmath). Does not replace Z3 in CI; it is the clone-local
bound check when `z3` is not installed.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from sim.chua_array import PHI_F, PhysicalNode
from sim.fsot_engine import PHI, assert_pin, domain_scalar
from sim.predict import SIGMA_C_PRED, SIGMA_C_TOL


def main() -> None:
    assert_pin()
    phys = PhysicalNode()
    phi = float(PHI)
    rc2 = phys.rc_from_sigma(PHI_F ** 2)
    S = domain_scalar("Electromagnetism")
    bom = abs(S) * 0.0004 * 100.0
    assert 1.6 < phi < 1.62, phi
    assert 6870.0 < rc2 < 6880.0, rc2
    assert 0.0 <= bom < 0.5, bom
    assert SIGMA_C_PRED < phi
    assert phys.r0_ohm > 0.0
    rep = ROOT / "results" / "sim_report.json"
    if rep.is_file():
        r = json.loads(rep.read_text(encoding="utf-8"))
        thr = r["sigma_c"]["sweep_threshold"]
        assert thr is not None and abs(thr - SIGMA_C_PRED) <= SIGMA_C_TOL, thr
    print(f"FSOT_CIRCUIT_SMT_REPLAY_OK phi={phi:.15f} Rc_phi_sq={rc2:.10f} bom={bom:.12f} sigma_c={SIGMA_C_PRED}")


if __name__ == "__main__":
    main()
