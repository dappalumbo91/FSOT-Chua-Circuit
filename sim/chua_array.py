"""3-node Chua ring — BOM NIC slopes, identical-node coupling.

Wrong objects (the 3% residual):
  - 1-D chain (ends are not identical; FSOT κ assumes the same D / degree)
  - Matsumoto fitted a,b = −1.143/−0.714
  - LOCK_ORDER = 0.85 (a free cut)
  - σ_c = α/φ picked after the sweep

Right objects:
  - ring / triangle (every node degree 2)
  - Ga, Gb from the Kennedy NIC resistors on the BOM
  - lock when MAD/amp ≤ φ^{-4} (hardware working-set law) and trit ≥ φ^{-1}
  - operating point σ = φ,  R_c = α R / φ
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from .fsot_engine import PHI

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
    R_nic_a_ohm: float = 2200.0  # 2.2 kΩ NIC branch
    R_nic_b_ohm: float = 3300.0  # 3.3 kΩ NIC branch

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

    @property
    def Ga(self) -> float:
        return -(1.0 / self.R_nic_a_ohm + 1.0 / self.R_nic_b_ohm)

    @property
    def Gb(self) -> float:
        return -1.0 / self.R_nic_b_ohm

    @property
    def a_dimless(self) -> float:
        return self.R_ohm * self.Ga

    @property
    def b_dimless(self) -> float:
        return self.R_ohm * self.Gb

    @property
    def sigma_phi(self) -> float:
        return PHI_F

    @property
    def R_c_phi_ohm(self) -> float:
        return self.rc_from_sigma(PHI_F)

    def sigma_from_rc(self, R_c_ohm: float) -> float:
        return self.alpha * self.R_ohm / max(R_c_ohm, 1e-9)

    def rc_from_sigma(self, sigma: float) -> float:
        return self.alpha * self.R_ohm / max(sigma, 1e-12)


def chua_h(x: np.ndarray, a: float, b: float) -> np.ndarray:
    return b * x + 0.5 * (a - b) * (np.abs(x + 1.0) - np.abs(x - 1.0))


def rhs_ring(state: np.ndarray, alpha: float, beta: float, sigma: float, a: float, b: float) -> np.ndarray:
    out = np.empty_like(state)
    xs, ys, zs = state[0::3], state[1::3], state[2::3]
    h = chua_h(xs, a, b)
    couple = np.roll(xs, 1) + np.roll(xs, -1) - 2.0 * xs
    out[0::3] = alpha * (ys - xs - h) + sigma * couple
    out[1::3] = xs - ys + zs
    out[2::3] = -beta * ys
    return out


def rk4_traj(
    n_nodes: int = 3,
    sigma: float = 0.0,
    t_end: float = 80.0,
    dt: float = 0.008,
    seed: int = 2,
    phys: PhysicalNode | None = None,
) -> dict:
    phys = phys or PhysicalNode()
    a, b = phys.a_dimless, phys.b_dimless
    rng = np.random.default_rng(seed)
    s = np.zeros(3 * n_nodes)
    for i in range(n_nodes):
        s[3 * i] = 0.1 + 0.05 * i + 0.01 * rng.normal()
        s[3 * i + 1] = 0.02 * rng.normal()
    n_steps = int(t_end / dt)
    xs = np.empty((n_steps, n_nodes))
    blew = False
    alpha, beta = phys.alpha, phys.beta
    for k in range(n_steps):
        xs[k] = s[0::3]
        k1 = rhs_ring(s, alpha, beta, sigma, a, b)
        k2 = rhs_ring(s + 0.5 * dt * k1, alpha, beta, sigma, a, b)
        k3 = rhs_ring(s + 0.5 * dt * k2, alpha, beta, sigma, a, b)
        k4 = rhs_ring(s + dt * k3, alpha, beta, sigma, a, b)
        s = s + (dt / 6.0) * (k1 + 2 * k2 + 2 * k3 + k4)
        np.clip(s, -8.0, 8.0, out=s)
        if not np.all(np.isfinite(s)):
            blew = True
            xs[k:] = np.nan
            break
    return {
        "t": np.arange(n_steps) * dt,
        "x": xs,
        "dt": dt,
        "sigma": sigma,
        "alpha": alpha,
        "beta": beta,
        "a": a,
        "b": b,
        "tau_s": phys.tau_s,
        "f_lc_hz": phys.f_lc_hz,
        "phys": phys,
        "blew_up": blew,
    }


def order_parameter(x_tail: np.ndarray) -> float:
    n = x_tail.shape[1]
    if n < 2:
        return 1.0
    corrs = []
    for i in range(n):
        for j in range(i + 1, n):
            aa = x_tail[:, i] - x_tail[:, i].mean()
            bb = x_tail[:, j] - x_tail[:, j].mean()
            denom = np.linalg.norm(aa) * np.linalg.norm(bb)
            corrs.append(0.0 if denom == 0 else float(np.dot(aa, bb) / denom))
    return float(np.mean(np.abs(corrs)))


def mean_abs_diff(x_tail: np.ndarray) -> float:
    n = x_tail.shape[1]
    diffs = [float(np.mean(np.abs(x_tail[:, i] - x_tail[:, j]))) for i in range(n) for j in range(i + 1, n)]
    return float(np.mean(diffs)) if diffs else 0.0


def trit_agreement(x_tail: np.ndarray, breakpoint: float = 1.0) -> float:
    trits = np.where(x_tail < -breakpoint, -1, np.where(x_tail > breakpoint, 1, 0))
    return float(np.mean(np.all(trits == trits[:, :1], axis=1)))


def dominant_freq_hz(x: np.ndarray, dt_dimless: float, tau_s: float) -> float:
    sig = x - np.mean(x)
    spec = np.abs(np.fft.rfft(sig))
    freqs = np.fft.rfftfreq(len(sig), d=dt_dimless * tau_s)
    spec[0] = 0.0
    return float(freqs[int(np.argmax(spec))])


def seed_locked(xt: np.ndarray, amp_ref: float) -> dict:
    finite = bool(np.all(np.isfinite(xt)))
    if not finite or amp_ref <= 0:
        return {"locked": False, "finite": False}
    amp = float(np.mean([np.std(xt[:, i]) for i in range(xt.shape[1])]))
    mad = mean_abs_diff(xt)
    trit = trit_agreement(xt)
    order = order_parameter(xt)
    railed = float(np.mean(np.abs(xt) > 7.5))
    locked = (
        mad <= amp_ref * PHI_INV4
        and trit >= PHI_INV
        and amp >= amp_ref * PHI_INV4
        and railed < 0.05
    )
    return {
        "locked": bool(locked),
        "finite": True,
        "amp": amp,
        "mad": mad,
        "mad_cut": amp_ref * PHI_INV4,
        "trit": trit,
        "trit_cut": PHI_INV,
        "order": order,
        "railed_frac": railed,
    }
