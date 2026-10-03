"""3-node Chua ring: Kennedy NIC slopes from the BOM, 3-segment nonlinearity, lossy inductor (FSOT Branch L).

Corrections in branch fix/aeb2ad-long-window (2026-10-03):
  - b was -R/R6 = -6/11 (wrong). The Kennedy NIC gives Gb = 1/R4 - R2/(R1 R3) = -9/22000 S,
    so b = R*Gb = -81/110. Ga = -R2/(R1 R3) - R5/(R4 R6) = -1/1320 S (a = -15/11, unchanged).
  - The outer segment is modelled: beyond Bp2 (the second op-amp saturates) the slope is
    Gc = 1/R1 + 1/R4 = +101/22000 S (c = +909/110). Esat is chosen so that Bp1 = 1 V, giving
    x2 = Bp2/Bp = 6.97.
  - np.clip(+-8) is removed. It hid the divergence of the 2-segment model and made 80 tau
    look locked. Integration now runs a long window (2000 tau) and tracks escape:
    a node that crosses x2 has left the double scroll for the outer limit cycle.
  - Lock requires no escape (tail max|x| < x2). Without that, rings that synchronise on the
    outer +-7.35 V cycle read as LOCK.
  - Inductor loss gamma = beta r0/R with r0 from FSOT 2.1 Branch L (docs/BRANCH_L_DERIVATION.md).

The lock law is otherwise unchanged: MAD <= amp_ref phi^-4, trit agreement >= phi^-1, amp >= amp_ref phi^-4, railed < 5 %.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction

import numpy as np

from .fsot_engine import PHI, branch_l

PHI_F = float(PHI)
PHI_INV = 1.0 / PHI_F
PHI_INV4 = PHI_F ** -4


@dataclass(frozen=True)
class PhysicalNode:
    R_ohm: float = 1800.0
    L_h: float = 0.022
    C1_f: float = 10e-9
    C2_f: float = 100e-9
    Bp_v: float = 1.0
    # Kennedy (1992) NIC pair, hardware/netlist.json
    R1_ohm: int = 220
    R2_ohm: int = 220
    R3_ohm: int = 2200
    R4_ohm: int = 22000
    R5_ohm: int = 22000
    R6_ohm: int = 3300
    use_branch_l: bool = True  # r0 from FSOT Branch L; False -> ideal inductor (r0 = 0)

    @property
    def alpha(self) -> float:
        return self.C2_f / self.C1_f

    @property
    def beta(self) -> float:
        return (self.R_ohm ** 2) * self.C2_f / self.L_h

    @property
    def tau_s(self) -> float:
        return self.R_ohm * self.C2_f

    @property
    def f_lc_hz(self) -> float:
        return 1.0 / (2.0 * np.pi * np.sqrt(self.L_h * self.C2_f))

    # exact conductances (siemens) as fractions
    @property
    def Ga_exact(self) -> Fraction:
        return -Fraction(self.R2_ohm, self.R1_ohm * self.R3_ohm) - Fraction(self.R5_ohm, self.R4_ohm * self.R6_ohm)

    @property
    def Gb_exact(self) -> Fraction:
        return -Fraction(self.R2_ohm, self.R1_ohm * self.R3_ohm) + Fraction(1, self.R4_ohm)

    @property
    def Gc_exact(self) -> Fraction:
        return Fraction(1, self.R1_ohm) + Fraction(1, self.R4_ohm)

    @property
    def Ga(self) -> float:
        return float(self.Ga_exact)

    @property
    def Gb(self) -> float:
        return float(self.Gb_exact)

    @property
    def Gc(self) -> float:
        return float(self.Gc_exact)

    @property
    def a_dimless(self) -> float:
        return self.R_ohm * self.Ga

    @property
    def b_dimless(self) -> float:
        return self.R_ohm * self.Gb

    @property
    def c_dimless(self) -> float:
        return self.R_ohm * self.Gc

    @property
    def esat_v(self) -> float:
        """Op-amp saturation that puts Bp1 = Esat R6/(R5+R6) at Bp_v."""
        return self.Bp_v * (self.R5_ohm + self.R6_ohm) / self.R6_ohm

    @property
    def bp2_v(self) -> float:
        return self.esat_v * self.R3_ohm / (self.R2_ohm + self.R3_ohm)

    @property
    def x2(self) -> float:
        return self.bp2_v / self.Bp_v

    @property
    def branch_l(self) -> dict:
        return branch_l(self.L_h, self.C2_f, self.R_ohm)

    @property
    def r0_ohm(self) -> float:
        return self.branch_l["r0_ohm"] if self.use_branch_l else 0.0

    @property
    def gamma(self) -> float:
        return self.beta * self.r0_ohm / self.R_ohm

    def sigma_from_rc(self, R_c_ohm: float) -> float:
        return self.alpha * self.R_ohm / max(R_c_ohm, 1e-9)

    def rc_from_sigma(self, sigma: float) -> float:
        return self.alpha * self.R_ohm / max(sigma, 1e-12)

    @property
    def R_c_phi_ohm(self) -> float:
        return self.rc_from_sigma(PHI_F)


def chua_h(x: np.ndarray, a: float, b: float, c: float, x2: float) -> np.ndarray:
    return c * x + 0.5 * (a - b) * (np.abs(x + 1.0) - np.abs(x - 1.0)) + 0.5 * (b - c) * (np.abs(x + x2) - np.abs(x - x2))


def rhs_ring(s: np.ndarray, sigma: np.ndarray, p: tuple) -> np.ndarray:
    """s has shape (batch, n_nodes, 3); sigma has shape (batch, 1)."""
    alpha, beta, gamma, a, b, c, x2 = p
    x, y, z = s[..., 0], s[..., 1], s[..., 2]
    couple = np.roll(x, 1, axis=1) + np.roll(x, -1, axis=1) - 2.0 * x if x.shape[1] > 1 else 0.0 * x
    out = np.empty_like(s)
    out[..., 0] = alpha * (y - x - chua_h(x, a, b, c, x2)) + sigma * couple
    out[..., 1] = x - y + z
    out[..., 2] = -beta * y - gamma * z
    return out


def initial_state(n_nodes: int, seed: int) -> np.ndarray:
    rng = np.random.default_rng(seed)
    s = np.zeros((n_nodes, 3))
    for i in range(n_nodes):
        s[i, 0] = 0.1 + 0.05 * i + 0.01 * rng.normal()
        s[i, 1] = 0.02 * rng.normal()
    return s


def run_batch(
    sigmas,
    seeds,
    n_nodes: int = 3,
    t_end: float = 2000.0,
    tail_tau: float = 500.0,
    dt: float = 0.005,
    phys: PhysicalNode | None = None,
    amp_ref: float | None = None,
    keep_tail: bool = False,
) -> list[dict]:
    """Integrate every (sigma, seed) pair at once (RK4, no clipping); online tail statistics.

    Returns one dict per (sigma, seed): amp, mad, trit, railed, tail_maxabs, t_escape (tau, or None),
    lobe_switches (node 0, tail), and locked (if amp_ref is given).
    """
    phys = phys or PhysicalNode()
    p = (phys.alpha, phys.beta, phys.gamma, phys.a_dimless, phys.b_dimless, phys.c_dimless, phys.x2)
    pairs = [(float(sg), int(sd)) for sg in sigmas for sd in seeds]
    B = len(pairs)
    s = np.stack([initial_state(n_nodes, sd) for _, sd in pairs])
    sig = np.array([sg for sg, _ in pairs])[:, None]
    n = int(round(t_end / dt))
    t0 = n - int(round(tail_tau / dt))
    x2 = phys.x2
    sx = np.zeros((B, n_nodes)); sxx = np.zeros((B, n_nodes))
    mad = np.zeros(B); agree = np.zeros(B); rail = np.zeros(B); mx = np.zeros(B)
    t_esc = np.full(B, np.nan); sw = np.zeros(B); lobe = np.zeros(B)
    tail = [] if keep_tail else None
    cnt = 0
    for k in range(n):
        x = s[..., 0]
        ax = np.abs(x)
        esc_now = np.isnan(t_esc) & ((ax > x2).any(axis=1) | ~np.isfinite(x).all(axis=1))
        t_esc[esc_now] = k * dt
        if k >= t0:
            cnt += 1
            sx += x; sxx += x * x
            mx = np.maximum(mx, ax.max(axis=1))
            rail += (ax > 7.5).sum(axis=1)
            tr = np.where(x < -1.0, -1, np.where(x > 1.0, 1, 0))
            agree += (tr == tr[:, :1]).all(axis=1)
            if n_nodes > 1:
                d = np.abs(x[:, :, None] - x[:, None, :])
                iu = np.triu_indices(n_nodes, 1)
                mad += d[:, iu[0], iu[1]].mean(axis=1)
            l0 = np.where(x[:, 0] > 1.0, 1.0, np.where(x[:, 0] < -1.0, -1.0, lobe))
            sw += (lobe != 0) & (l0 != lobe)
            lobe = l0
            if keep_tail:
                tail.append(x.copy())
        k1 = rhs_ring(s, sig, p)
        k2 = rhs_ring(s + 0.5 * dt * k1, sig, p)
        k3 = rhs_ring(s + 0.5 * dt * k2, sig, p)
        k4 = rhs_ring(s + dt * k3, sig, p)
        s = s + (dt / 6.0) * (k1 + 2.0 * k2 + 2.0 * k3 + k4)
    mean = sx / cnt
    amp = np.sqrt(np.maximum(sxx / cnt - mean * mean, 0.0)).mean(axis=1)
    out = []
    for i, (sg, sd) in enumerate(pairs):
        r = {
            "sigma": sg, "seed": sd,
            "finite": bool(np.isfinite(amp[i])),
            "amp": float(amp[i]), "mad": float(mad[i] / cnt), "trit": float(agree[i] / cnt),
            "railed_frac": float(rail[i] / (n_nodes * cnt)), "tail_maxabs": float(mx[i]),
            "t_escape_tau": None if np.isnan(t_esc[i]) else float(t_esc[i]),
            "escaped_in_tail": bool(mx[i] >= x2), "lobe_switches_tail": int(sw[i]),
        }
        if amp_ref is not None:
            r.update(lock_law(r, amp_ref, x2))
        if keep_tail:
            r["tail_x"] = np.array([t[i] for t in tail])
        out.append(r)
    return out


def lock_law(r: dict, amp_ref: float, x2: float) -> dict:
    cut = amp_ref * PHI_INV4
    sync = r["finite"] and r["mad"] <= cut and r["trit"] >= PHI_INV and r["amp"] >= cut and r["railed_frac"] < 0.05
    amplitude_ok = r["finite"] and r["tail_maxabs"] < x2
    return {"mad_cut": cut, "trit_cut": PHI_INV, "synchronised": bool(sync), "amplitude_ok": bool(amplitude_ok),
            "locked": bool(sync and amplitude_ok)}


def dominant_freq_hz(x: np.ndarray, dt_dimless: float, tau_s: float) -> float:
    sig = x - np.mean(x)
    spec = np.abs(np.fft.rfft(sig))
    freqs = np.fft.rfftfreq(len(sig), d=dt_dimless * tau_s)
    spec[0] = 0.0
    return float(freqs[int(np.argmax(spec))])
