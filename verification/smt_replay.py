"""Python replay of verification/circuit_bounds.smt2.

Always available (mpmath). Does not replace Z3 in CI; it is the clone-local
bound check when `z3` is not installed.
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from sim.chua_array import PhysicalNode
from sim.fsot_engine import PHI, assert_pin, domain_scalar


def main() -> None:
    assert_pin()
    phys = PhysicalNode()
    phi = float(PHI)
    rc = phys.R_c_phi_ohm
    S = domain_scalar("Electromagnetism")
    bom = abs(S) * 0.0004 * 100.0
    assert 1.6 < phi < 1.62, phi
    assert 11100.0 < rc < 11150.0, rc
    assert 0.0 <= bom < 0.5, bom
    print(f"FSOT_CIRCUIT_SMT_REPLAY_OK phi={phi:.15f} Rc={rc:.10f} bom={bom:.12f}")


if __name__ == "__main__":
    main()
