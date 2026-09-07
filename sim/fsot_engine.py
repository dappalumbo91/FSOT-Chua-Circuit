"""FSOT scalar pin for the Circuit lab.

Authority is **this repo** `vendor/fsot_compute.py` (SHA-256 prefix D1D38A).
Byte-identical to FSOT-2.1-Lean GitHub main. This application does not
inherit the hub's green gates — it re-proves its own obligations.
"""

from __future__ import annotations

import hashlib
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VENDOR = ROOT / "vendor"
if str(VENDOR) not in sys.path:
    sys.path.insert(0, str(VENDOR))

from fsot_compute import (  # type: ignore
    A_BLEED,
    A_IN,
    B_IN,
    C_EFF,
    C_FACTOR,
    CHAOS,
    DOMAINS,
    K,
    P_NEW,
    P_VAR,
    PHI,
    PI,
    POOF,
    ScalarInput,
    SUCTION,
    THETA_S,
    compute_scalar,
)

PIN_PREFIX = "D1D38A"
COLLAPSE_THRESHOLD = float(C_EFF * P_VAR)
DOMAIN_NAME = "Electromagnetism"
PIN_PATH = VENDOR / "fsot_compute.py"

__all__ = [
    "A_BLEED",
    "A_IN",
    "B_IN",
    "C_EFF",
    "C_FACTOR",
    "CHAOS",
    "COLLAPSE_THRESHOLD",
    "DOMAINS",
    "DOMAIN_NAME",
    "K",
    "P_NEW",
    "P_VAR",
    "PHI",
    "PI",
    "PIN_PREFIX",
    "POOF",
    "SUCTION",
    "THETA_S",
    "assert_pin",
    "compute_scalar",
    "domain_scalar",
    "kappa_couple",
    "residual_scale",
    "snapshot",
    "trinary_from_scalar",
    "trinary_from_voltage",
]


def pin_sha256() -> str:
    return hashlib.sha256(PIN_PATH.read_bytes()).hexdigest().upper()


def assert_pin() -> str:
    digest = pin_sha256()
    if not digest.startswith(PIN_PREFIX):
        raise RuntimeError(
            f"FSOT pin mismatch: expected SHA-256 prefix {PIN_PREFIX}, got {digest[:12]}"
        )
    cert = VENDOR / "fsot_compute_AUTHORITY_PIN.json"
    if cert.is_file():
        import json

        doc = json.loads(cert.read_text(encoding="utf-8"))
        want = str(doc.get("certificate_authority") or "").upper()
        if want and want != digest:
            raise RuntimeError(f"pin file {want[:12]} != vendor bytes {digest[:12]}")
    return digest


def domain_scalar(name: str = DOMAIN_NAME) -> float:
    cfg = DOMAINS[name]
    s = ScalarInput(
        D_eff=cfg.D_eff,
        recent_hits=cfg.hits,
        delta_psi=cfg.delta_psi,
        delta_theta=cfg.delta_theta,
        observed=cfg.observed,
    )
    return float(compute_scalar(s))


def residual_scale(S: float) -> float:
    return 1.0 + abs(S) * float(P_NEW)


def kappa_couple(S_i: float, S_j: float, D_i: float, D_j: float) -> float:
    return float(
        A_BLEED * POOF * abs(S_i) * abs(S_j) / (1.0 + abs(D_i - D_j) / 25.0)
    )


class TrinaryState:
    def __init__(self, trit: int, label: str):
        self.trit = trit
        self.label = label


def trinary_from_scalar(S: float) -> TrinaryState:
    if abs(S) < COLLAPSE_THRESHOLD:
        return TrinaryState(0, "0")
    if S > 0.0:
        return TrinaryState(1, "+1")
    return TrinaryState(-1, "-1")


def trinary_from_voltage(v: float, breakpoint: float = 1.0) -> TrinaryState:
    if v < -breakpoint:
        return TrinaryState(-1, "-1")
    if v > breakpoint:
        return TrinaryState(1, "+1")
    return TrinaryState(0, "0")


def snapshot() -> dict:
    digest = assert_pin()
    S_em = domain_scalar("Electromagnetism")
    cfg = DOMAINS[DOMAIN_NAME]
    return {
        "pin": PIN_PREFIX,
        "sha256": digest,
        "free_parameters": 0,
        "domain": DOMAIN_NAME,
        "D_eff": int(cfg.D_eff),
        "delta_psi": float(cfg.delta_psi),
        "observed": bool(cfg.observed),
        "S_electromagnetism": S_em,
        "K": float(K),
        "PHI": float(PHI),
        "PI": float(PI),
        "P_NEW": float(P_NEW),
        "C_EFF": float(C_EFF),
        "P_VAR": float(P_VAR),
        "C_FACTOR": float(C_FACTOR),
        "A_BLEED": float(A_BLEED),
        "A_IN": float(A_IN),
        "B_IN": float(B_IN),
        "POOF": float(POOF),
        "SUCTION": float(SUCTION),
        "CHAOS": float(CHAOS),
        "THETA_S": float(THETA_S),
        "collapse_threshold": COLLAPSE_THRESHOLD,
        "residual_scale_EM": residual_scale(S_em),
        "kappa_identical_EM": kappa_couple(S_em, S_em, float(cfg.D_eff), float(cfg.D_eff)),
        "scalar_trinary": trinary_from_scalar(S_em).label,
    }
