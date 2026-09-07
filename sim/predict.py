"""Seed-closed predictions. No post-hoc formula shopping.

Operating point (the experiment you build):
    σ = φ
    R_c = α R / φ = (C2/C1) R / φ

Gates:
    σ = 0     → unlocked (independent chaos)
    σ = 1 < φ → unlocked
    σ = φ     → locked
    σ = φ²    → locked
"""

from __future__ import annotations

from .chua_array import PhysicalNode
from .fsot_engine import (
    COLLAPSE_THRESHOLD,
    DOMAINS,
    PHI,
    domain_scalar,
    kappa_couple,
    residual_scale,
)


def predictions(phys: PhysicalNode | None = None) -> dict:
    phys = phys or PhysicalNode()
    S = domain_scalar("Electromagnetism")
    D = float(DOMAINS["Electromagnetism"].D_eff)
    phi = float(PHI)
    sigma_phi = phi
    R_c = phys.rc_from_sigma(sigma_phi)
    return {
        "S_EM": S,
        "D_eff": D,
        "kappa": kappa_couple(S, S, D, D),
        "residual_scale_P_NEW": residual_scale(S),
        "residual_scale_EM_catalog": 1.0 + abs(S) * 0.0004,
        "collapse_threshold": COLLAPSE_THRESHOLD,
        "alpha": phys.alpha,
        "beta": phys.beta,
        "a_dimless": phys.a_dimless,
        "b_dimless": phys.b_dimless,
        "Ga_S": phys.Ga,
        "Gb_S": phys.Gb,
        "R_ohm": phys.R_ohm,
        "L_h": phys.L_h,
        "C1_f": phys.C1_f,
        "C2_f": phys.C2_f,
        "f_lc_hz": phys.f_lc_hz,
        "f_lc_fsot_catalog_hz": phys.f_lc_hz * (1.0 + abs(S) * 0.0004),
        "phi": phi,
        "operating_point": {
            "name": "sigma_equals_phi",
            "formula": "σ = φ,  R_c = α R / φ",
            "sigma": sigma_phi,
            "R_c_ohm": R_c,
            "why": (
                "Three identical fluid nodes on a closed loop. "
                "φ is the Layer-0 self-similar fold. "
                "α = C2/C1 is the catalog capacitor ratio, not a fit."
            ),
        },
        "unlocked_point": {
            "sigma": 1.0,
            "R_c_ohm": phys.rc_from_sigma(1.0),
            "note": "σ = 1 < φ must not complete-lock",
        },
    }
