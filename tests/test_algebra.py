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
    assert digest.startswith("AEB2AD"), digest[:12]


def test_nic_exact_rationals() -> None:
    p = PhysicalNode()
    from fractions import Fraction as F

    assert p.Ga_exact == F(-1, 1320)
    assert p.Gb_exact == F(-9, 22000)  # was -1/3300 (wrong): Gb = 1/R4 - R2/(R1 R3)
    assert p.Gc_exact == F(101, 22000)
    assert abs(p.a_dimless - (-15.0 / 11.0)) < 1e-12
    assert abs(p.b_dimless - (-81.0 / 110.0)) < 1e-12
    assert abs(p.c_dimless - (909.0 / 110.0)) < 1e-12
    assert abs(p.esat_v - 23.0 / 3.0) < 1e-12 and abs(p.bp2_v - 230.0 / 33.0) < 1e-12


def test_rc_phi() -> None:
    p = PhysicalNode()
    phi = (1.0 + math.sqrt(5.0)) / 2.0
    rc = p.alpha * p.R_ohm / phi
    assert abs(rc - p.R_c_phi_ohm) < 1e-9
    assert 11124.0 < rc < 11125.0
    assert abs(float(PHI) - phi) < 1e-12


def test_bias_roundtrip() -> None:
    import numpy as np

    from sim import adc_model

    assert abs(adc_model.GAIN - 1.0 / 6.0) < 1e-15 and abs(adc_model.MID - 1.65) < 1e-12
    v = np.array([-7.35, -4.33, -1.0, 0.0, 1.0, 4.33, 7.35])  # outer cycle, double scroll, breakpoints
    assert adc_model.vc1_to_adc_volts(v).min() > 0.0 and adc_model.vc1_to_adc_volts(v).max() < 3.3
    rec = decode(encode(v))
    assert float(np.max(np.abs(rec - v))) < 0.0025  # 12-bit at 1/6 gain: LSB/2 = 2.0 mV
    # the old 100k/100k/100k network: v = 1.1 + V/3, not the documented 1.65 + V/2
    rs = rp = rg = 100e3
    par = lambda a, b: a * b / (a + b)
    assert abs(par(rp, rg) / (rs + par(rp, rg)) - 1 / 3) < 1e-12 and abs(3.3 * par(rs, rg) / (rp + par(rs, rg)) - 1.1) < 1e-12


def test_trinary_breakpoints() -> None:
    assert trinary_from_voltage(-1.01).trit == -1
    assert trinary_from_voltage(0.0).trit == 0
    assert trinary_from_voltage(1.01).trit == 1


def test_em_domain() -> None:
    S = domain_scalar("Electromagnetism")
    assert abs(S - 0.9557285700955828) < 1e-12  # AEB2AD: D_eff 7 (nest), look 1
    assert abs(COLLAPSE_THRESHOLD - 0.9175102712064876) < 1e-15
    assert abs(S) >= COLLAPSE_THRESHOLD  # scalar trit +1 (was 0 at D1D38A)


def test_branch_l() -> None:
    from sim.fsot_engine import branch_l

    p = PhysicalNode()
    bl = branch_l(p.L_h, p.C2_f, p.R_ohm)
    # golden: cpp/golden/branch_l_AEB2AD.tsv (mpmath dps 50 == C++ f128/mp169)
    assert abs(bl["eps"] - 7.72509421698849555e-4) < 1e-18
    assert abs(bl["r0_ohm"] - 18.4400497592861384) < 1e-12
    assert abs(bl["gamma"] - 0.150873134394159315) < 1e-15
    assert abs(bl["Q_L"] - 25.4360255045483541) < 1e-11
    assert abs(p.gamma - bl["gamma"]) < 1e-15
    # time-scaling invariance of r0 (C1, C2, L all x10)
    assert abs(branch_l(p.L_h * 10, p.C2_f * 10, p.R_ohm)["r0_ohm"] - bl["r0_ohm"]) < 1e-12


def test_locked_predictions() -> None:
    import hashlib

    from sim.predict import PRED_PART1_SHA256, PRED_PART2_SHA256

    d = ROOT / "cpp" / "predictions"
    assert hashlib.sha256((d / "PREDICTIONS_2026-10-03_branchL_part1.md").read_bytes()).hexdigest() == PRED_PART1_SHA256
    assert hashlib.sha256((d / "PREDICTIONS_2026-10-03_branchL_part2.md").read_bytes()).hexdigest() == PRED_PART2_SHA256


def main() -> None:
    tests = [
        test_pin,
        test_nic_exact_rationals,
        test_rc_phi,
        test_bias_roundtrip,
        test_trinary_breakpoints,
        test_em_domain,
        test_branch_l,
        test_locked_predictions,
    ]
    for fn in tests:
        fn()
        print("PASS", fn.__name__)
    print("OK  algebra suite", len(tests))


if __name__ == "__main__":
    main()
