"""Master-stability function of the 3-ring (Python cross-check of cpp/fsot_chua.cpp `msf`).

The ring Laplacian has nonzero eigenvalue 3, so the transverse mode sees coupling 3*sigma.
lambda_perp(sigma) is the largest Lyapunov exponent of the variational equation along the
synchronous orbit (same orbit for every sigma, so every sigma is integrated in one pass).
sigma_c is the zero crossing. Usage: python -m sim.msf [T] [sigma_lo sigma_hi step]
"""

from __future__ import annotations

import sys

import numpy as np

from .chua_array import PhysicalNode


def hprime(x: float, a: float, b: float, c: float, x2: float) -> float:
    ax = abs(x)
    return a if ax < 1.0 else (b if ax < x2 else c)


def lambda_perp(sigmas, T: float = 3000.0, dt: float = 0.005, trans: float = 200.0, phys: PhysicalNode | None = None) -> np.ndarray:
    phys = phys or PhysicalNode()
    al, be, ga = phys.alpha, phys.beta, phys.gamma
    a, b, c, x2 = phys.a_dimless, phys.b_dimless, phys.c_dimless, phys.x2
    st = 3.0 * np.asarray(sigmas, dtype=float)
    s = np.array([0.1, 0.0, 0.0])
    d = np.tile(np.array([1.0, 0.3, 0.1]), (st.size, 1))

    def f(v):
        x, y, z = v
        h = c * x + 0.5 * (a - b) * (abs(x + 1) - abs(x - 1)) + 0.5 * (b - c) * (abs(x + x2) - abs(x - x2))
        return np.array([al * (y - x - h), x - y + z, -be * y - ga * z])

    def J(v, u):
        g = -al * (1.0 + hprime(v[0], a, b, c, x2)) - st
        return np.stack([g * u[:, 0] + al * u[:, 1], u[:, 0] - u[:, 1] + u[:, 2], -be * u[:, 1] - ga * u[:, 2]], axis=1)

    n, nt = int((T + trans) / dt), int(trans / dt)
    acc = np.zeros(st.size)
    for k in range(n):
        k1 = f(s); j1 = J(s, d)
        t = s + 0.5 * dt * k1; u = d + 0.5 * dt * j1
        k2 = f(t); j2 = J(t, u)
        t = s + 0.5 * dt * k2; u = d + 0.5 * dt * j2
        k3 = f(t); j3 = J(t, u)
        t = s + dt * k3; u = d + dt * j3
        k4 = f(t); j4 = J(t, u)
        s = s + dt / 6 * (k1 + 2 * k2 + 2 * k3 + k4)
        d = d + dt / 6 * (j1 + 2 * j2 + 2 * j3 + j4)
        nr = np.sqrt((d * d).sum(axis=1))
        if k >= nt:
            acc += np.log(nr)
        d = d / nr[:, None]
    return acc / T


def sigma_c(sigmas, lam) -> float | None:
    """First grid crossing + -> - after which lambda_perp stays negative; linear interpolation."""
    sigmas, lam = np.asarray(sigmas), np.asarray(lam)
    for i in range(len(lam) - 1):
        if lam[i] > 0 and (lam[i + 1:] < 0).all():
            return float(sigmas[i] + (sigmas[i + 1] - sigmas[i]) * lam[i] / (lam[i] - lam[i + 1]))
    return None


if __name__ == "__main__":
    T = float(sys.argv[1]) if len(sys.argv) > 1 else 3000.0
    lo, hi, step = (float(v) for v in sys.argv[2:5]) if len(sys.argv) > 4 else (1.30, 1.70, 0.025)
    sg = np.round(np.arange(lo, hi + 1e-9, step), 6)
    lam = lambda_perp(sg, T=T)
    for a_, b_ in zip(sg, lam):
        print(f"{a_:.4f}\t{b_:.6f}")
    print(f"sigma_c\t{sigma_c(sg, lam)}")
