"""Seed-closed predictions (pin AEB2AD). No post-hoc formula shopping.

Revised 2026-10-03 (branch fix/aeb2ad-long-window), after the long-window audit:

    sigma = 0, 1, 0.9 (Rc = 20 kOhm)  -> no lock (amplitude-checked: no escape beyond Bp2)
    sigma = phi^2  (Rc = 6.875 kOhm)  -> lock            ROBUST GATE
    sigma_c = 1.4897                  -> lock threshold  SHARP PREDICTION (FSOT Branch L gamma + master stability)
    sigma = phi    (Rc = 11.12 kOhm)  -> lock, DEMOTED to a consequence of sigma_c < phi (margin 0.13 in sigma,
                                         lambda_perp(phi) = -0.016/tau). It is no longer a stand-alone FSOT claim:
                                         with the ideal (r0 = 0) Kennedy ring it does not lock (sigma_c = 2.26), and
                                         with the old b = -6/11 model its 80-tau "lock" was an artifact of np.clip(+-8).

gamma comes from FSOT 2.1 Branch L (lossy reactance): r0 = sqrt((1+|S_EM| ALPHA)^2 - 1) sqrt(L/C2) = 18.440 ohm,
gamma = beta r0/R = 0.15087. sigma_c was computed from that gamma (cpp/fsot_chua msf, grid 0.025, T = 3000 tau) and
locked in cpp/predictions/ BEFORE the ring sweep.
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

# Locked before the ring sweep (cpp/predictions/PREDICTIONS_2026-10-03_branchL_part{1,2}.md)
SIGMA_C_PRED = 1.4897
SIGMA_C_TOL = 0.05
PRED_PART1_SHA256 = "04ebe3f4e2f96eb546d494b76169d456d883635631e4ac89cf9307a302b4f6f1"
PRED_PART2_SHA256 = "d6bd17be0bf24ba5c8c7a40ea4471c72295a03886e9769bcd8d28eb9a44a4cdd"


def predictions(phys: PhysicalNode | None = None) -> dict:
    phys = phys or PhysicalNode()
    S = domain_scalar("Electromagnetism")
    D = float(DOMAINS["Electromagnetism"].D_eff)
    phi = float(PHI)
    bl = phys.branch_l
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
        "c_dimless": phys.c_dimless,
        "x2_outer_breakpoint": phys.x2,
        "Ga_S": str(phys.Ga_exact),
        "Gb_S": str(phys.Gb_exact),
        "Gc_S": str(phys.Gc_exact),
        "R_ohm": phys.R_ohm,
        "L_h": phys.L_h,
        "C1_f": phys.C1_f,
        "C2_f": phys.C2_f,
        "f_lc_hz": phys.f_lc_hz,
        "f_lc_fsot_catalog_hz": phys.f_lc_hz * (1.0 + abs(S) * 0.0004),
        "phi": phi,
        "branch_l": bl,
        "gamma": phys.gamma,
        "sharp_prediction": {
            "name": "sigma_c",
            "sigma_c": SIGMA_C_PRED,
            "tolerance": SIGMA_C_TOL,
            "R_c_crit_ohm": phys.rc_from_sigma(SIGMA_C_PRED),
            "procedure": "zero of lambda_perp(3 sigma) on the synchronous double scroll with gamma = Branch L",
            "locked_sha256": [PRED_PART1_SHA256, PRED_PART2_SHA256],
        },
        "robust_gate": {"name": "sigma_equals_phi_squared", "sigma": phi * phi, "R_c_ohm": phys.rc_from_sigma(phi * phi)},
        "demoted": {
            "name": "sigma_equals_phi",
            "sigma": phi,
            "R_c_ohm": phys.R_c_phi_ohm,
            "status": "consequence of sigma_c < phi, not a stand-alone claim",
            "evidence": [
                "old model (b=-6/11, no outer segment) diverges without np.clip(+-8); 80-tau lock was a clip artifact",
                "long window (2000 tau) ideal Kennedy ring (r0=0): phi does not lock; sigma_c(r0=0)=2.26",
                "with Branch L gamma: phi locks 6/6 but with margin sigma_c/phi = 0.92",
            ],
        },
        "unlocked_points": [
            {"sigma": 0.0, "note": "independent chaos"},
            {"sigma": 1.0, "R_c_ohm": phys.rc_from_sigma(1.0), "note": "escapes to the outer cycle; amplitude check must veto LOCK"},
            {"sigma": phys.sigma_from_rc(20000.0), "R_c_ohm": 20000.0, "note": "bench unlocked setting; amplitude check must veto LOCK"},
        ],
    }
