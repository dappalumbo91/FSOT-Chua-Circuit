"""Fast, no-ODE certificates. These must pass even if the Chua sweep is skipped."""

from __future__ import annotations

import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from sim.adc_model import decode, encode
from sim.chua_array import PhysicalNode
from sim.fsot_engine import (
    COLLAPSE_THRESHOLD,
    PHI,
    assert_pin,
    domain_scalar,
    trinary_from_voltage,
)


def test_pin() -> None:
    digest = assert_pin()
    assert digest.startswith("D1D38A"), digest[:12]


def test_nic_exact_rationals() -> None:
    p = PhysicalNode()
    assert abs(p.Ga - (-1.0 / 1320.0)) < 1e-15
    assert abs(p.Gb - (-1.0 / 3300.0)) < 1e-15
    assert abs(p.a_dimless - (-15.0 / 11.0)) < 1e-12
    assert abs(p.b_dimless - (-6.0 / 11.0)) < 1e-12
    assert abs(1800 * 11 - 1320 * 15) < 1e-9


def test_rc_phi() -> None:
    p = PhysicalNode()
    phi = (1.0 + math.sqrt(5.0)) / 2.0
    rc = p.alpha * p.R_ohm / phi
    assert abs(rc - p.R_c_phi_ohm) < 1e-9
    assert 11124.0 < rc < 11125.0
    assert abs(float(PHI) - phi) < 1e-12


def test_bias_roundtrip() -> None:
    import numpy as np

    v = np.array([-2.0, -1.0, 0.0, 1.0, 2.0])
    rec = decode(encode(v))
    assert rec.min() > -2.1 and rec.max() < 2.1
    assert float(np.max(np.abs(rec - v))) < 0.002  # 12-bit


def test_trinary_breakpoints() -> None:
    assert trinary_from_voltage(-1.01).trit == -1
    assert trinary_from_voltage(0.0).trit == 0
    assert trinary_from_voltage(1.01).trit == 1


def test_em_domain() -> None:
    S = domain_scalar("Electromagnetism")
    assert abs(S - 0.5188655207983146) < 1e-9
    assert abs(S) < COLLAPSE_THRESHOLD


def main() -> None:
    tests = [
        test_pin,
        test_nic_exact_rationals,
        test_rc_phi,
        test_bias_roundtrip,
        test_trinary_breakpoints,
        test_em_domain,
    ]
    for fn in tests:
        fn()
        print("PASS", fn.__name__)
    print("OK  algebra suite", len(tests))


if __name__ == "__main__":
    main()
