"""Find the wrong object behind the 3% residual.

Forbidden: invent σ_c = α/φ after seeing the sweep.
Required (APPLY.md): name the measured object, pick the domain fold,
residual-scale. Lock cut must be seed-closed, not 0.85.
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np

from .chua_array import PhysicalNode, chua_h, mean_abs_diff, order_parameter, trit_agreement
from .fsot_engine import (
    COLLAPSE_THRESHOLD,
    DOMAINS,
    P_NEW,
    PHI,
    assert_pin,
    domain_scalar,
    kappa_couple,
    residual_scale,
    snapshot,
)

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "results" / "interface_diagnosis.json"

# BOM NIC (Kennedy two-NIC parallel). Inner: both linear. Outer: 2.2 k branch saturates.
R_NIC_INNER_A = 2200.0
R_NIC_INNER_B = 3300.0
GA = -(1.0 / R_NIC_INNER_A + 1.0 / R_NIC_INNER_B)  # S
GB = -(1.0 / R_NIC_INNER_B)  # S
BP = 1.0
PHI_INV = 1.0 / float(PHI)
# Hardware spine (ENGINEERING_HARDWARE_CODE_DIRECTION): working-set fraction ≤ φ^{-4}.
# Fractional node disagreement MAD/amp is that working-set object. Not a fitted lock cut.
PHI_INV4 = float(PHI) ** -4


def nic_slopes(R_ohm: float) -> tuple[float, float]:
    """Dimensionless a, b from the BOM NIC, not Matsumoto fitted −1.143/−0.714."""
    return R_ohm * GA, R_ohm * GB


def rhs_ring(state, alpha, beta, sigma, a, b):
    n = state.size // 3
    out = np.empty_like(state)
    xs, ys, zs = state[0::3], state[1::3], state[2::3]
    h = chua_h(xs, a=a, b=b)
    couple = np.roll(xs, 1) + np.roll(xs, -1) - 2.0 * xs
    dx = alpha * (ys - xs - h) + sigma * couple
    dy = xs - ys + zs
    dz = -beta * ys
    out[0::3], out[1::3], out[2::3] = dx, dy, dz
    return out


def rhs_chain(state, alpha, beta, sigma, a, b):
    n = state.size // 3
    out = np.empty_like(state)
    xs, ys, zs = state[0::3], state[1::3], state[2::3]
    h = chua_h(xs, a=a, b=b)
    couple = np.zeros_like(xs)
    if n >= 2:
        couple[0] += xs[1] - xs[0]
        couple[-1] += xs[-2] - xs[-1]
        for i in range(1, n - 1):
            couple[i] += (xs[i - 1] - xs[i]) + (xs[i + 1] - xs[i])
    dx = alpha * (ys - xs - h) + sigma * couple
    dy = xs - ys + zs
    dz = -beta * ys
    out[0::3], out[1::3], out[2::3] = dx, dy, dz
    return out


def integrate(n_nodes, sigma, topology, a, b, phys, t_end=90.0, dt=0.008, seed=2):
    rng = np.random.default_rng(seed)
    s = np.zeros(3 * n_nodes)
    for i in range(n_nodes):
        s[3 * i] = 0.1 + 0.05 * i + 0.01 * rng.normal()
        s[3 * i + 1] = 0.02 * rng.normal()
    n_steps = int(t_end / dt)
    xs = np.empty((n_steps, n_nodes))
    rhs = rhs_ring if topology == "ring" else rhs_chain
    alpha, beta = phys.alpha, phys.beta
    for k in range(n_steps):
        xs[k] = s[0::3]
        k1 = rhs(s, alpha, beta, sigma, a, b)
        k2 = rhs(s + 0.5 * dt * k1, alpha, beta, sigma, a, b)
        k3 = rhs(s + 0.5 * dt * k2, alpha, beta, sigma, a, b)
        k4 = rhs(s + dt * k3, alpha, beta, sigma, a, b)
        s = s + (dt / 6.0) * (k1 + 2 * k2 + 2 * k3 + k4)
        np.clip(s, -8.0, 8.0, out=s)
        if not np.all(np.isfinite(s)):
            xs[k:] = np.nan
            break
    return xs


def isolated_amp(a, b, phys) -> float:
    xs = integrate(1, 0.0, "chain", a, b, phys, t_end=80.0, seed=1)
    tail = xs[int(0.7 * len(xs)) :, 0]
    return float(np.std(tail[np.isfinite(tail)]))


def seed_locked(xt, amp_ref: float) -> dict:
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
        and amp >= amp_ref * PHI_INV4  # still a working set, not the dead origin
        and amp <= 8.0  # below rail clip
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


def onset_of(topology, a, b, phys, amp_ref, lo, hi, steps=10):
    for _ in range(steps):
        mid = 0.5 * (lo + hi)
        xs = integrate(3, mid, topology, a, b, phys)
        xt = xs[int(0.7 * len(xs)) :]
        if seed_locked(xt, amp_ref)["locked"]:
            hi = mid
        else:
            lo = mid
    return hi


def lle_isolated(a, b, phys, steps=8000, dt=0.02) -> float:
    """Benettin largest Lyapunov of one node (classical, no fit)."""
    alpha, beta = phys.alpha, phys.beta
    s = np.array([0.1, 0.0, 0.0])
    d = np.array([1e-8, 0.0, 0.0])
    acc = 0.0
    n_acc = 0

    def f(u):
        x, y, z = u
        h = chua_h(np.array([x]), a=a, b=b)[0]
        return np.array([alpha * (y - x - h), x - y + z, -beta * y])

    for k in range(steps):
        k1 = f(s)
        k2 = f(s + 0.5 * dt * k1)
        k3 = f(s + 0.5 * dt * k2)
        k4 = f(s + dt * k3)
        s = s + (dt / 6.0) * (k1 + 2 * k2 + 2 * k3 + k4)
        np.clip(s, -8.0, 8.0, out=s)
        if k < 1500:
            continue
        sp = s + d
        k1 = f(sp)
        k2 = f(sp + 0.5 * dt * k1)
        k3 = f(sp + 0.5 * dt * k2)
        k4 = f(sp + dt * k3)
        sp = sp + (dt / 6.0) * (k1 + 2 * k2 + 2 * k3 + k4)
        d = sp - s
        dist = float(np.linalg.norm(d))
        if dist <= 0:
            d = np.array([1e-8, 0.0, 0.0])
            continue
        acc += np.log(dist / 1e-8)
        n_acc += 1
        d *= 1e-8 / dist
    return float(acc / (n_acc * dt)) if n_acc else float("nan")


def err_pct(computed, measured) -> float:
    return abs(computed - measured) / max(abs(measured), 1e-18) * 100.0


def main() -> None:
    digest = assert_pin()
    snap = snapshot()
    phys = PhysicalNode()
    a, b = nic_slopes(phys.R_ohm)
    S = domain_scalar("Electromagnetism")
    r_pnew = residual_scale(S)
    r_em_panel = 1.0 + abs(S) * 0.0004  # preregistered EM catalog factor
    kappa = kappa_couple(S, S, 9.0, 9.0)
    amp_ref = isolated_amp(a, b, phys)
    lle = lle_isolated(a, b, phys)

    # Classical conductance objects from the NIC (siemens → R_c).
    classical = {
        "1_over_abs_Ga": 1.0 / abs(GA),
        "1_over_abs_Gb": 1.0 / abs(GB),
        "1_over_abs_Ga_minus_Gb": 1.0 / abs(GA - GB),
        "2_over_abs_Ga": 2.0 / abs(GA),
        "1_over_abs_Ga_times_lambda2_ring": 1.0 / (abs(GA) * 3.0),
        "1_over_abs_Ga_times_lambda2_path": 1.0 / (abs(GA) * 1.0),
    }

    rows = []
    for topology in ("chain", "ring"):
        # Coarse then bisect.
        probe = [0.0, 0.5, 1.0, 1.5, 2.0, 3.0, 4.0, 5.0, 6.0, 8.0, 12.0]
        last_unlocked, first_locked = 0.0, None
        probes = []
        for sig in probe:
            xs = integrate(3, sig, topology, a, b, phys)
            xt = xs[int(0.7 * len(xs)) :]
            st = seed_locked(xt, amp_ref)
            st.update(sigma=sig, R_c=phys.rc_from_sigma(sig), topology=topology)
            probes.append(st)
            if st["locked"] and first_locked is None:
                first_locked = sig
            if not st["locked"]:
                last_unlocked = sig
        onset = None
        if first_locked is not None:
            onset = onset_of(topology, a, b, phys, amp_ref, last_unlocked, first_locked)
        rows.append(
            {
                "topology": topology,
                "onset_sigma": onset,
                "onset_R_c_ohm": None if onset is None else phys.rc_from_sigma(onset),
                "probes": probes,
            }
        )

    ring = next(r for r in rows if r["topology"] == "ring")
    chain = next(r for r in rows if r["topology"] == "chain")
    measured_Rc = ring["onset_R_c_ohm"]

    object_table = []
    if measured_Rc is not None:
        for name, Rc_class in classical.items():
            # APPLY.md: computed = classical × (1+|S| P_NEW)  (mechanistic interface)
            # and catalog-style tiny EM factor for comparison (should be too small to be the lock object).
            for label, scale in (("P_NEW_interface", r_pnew), ("EM_catalog_f", r_em_panel)):
                computed = Rc_class * scale
                object_table.append(
                    {
                        "classical_object": name,
                        "scale": label,
                        "R_c_classical": Rc_class,
                        "R_c_computed": computed,
                        "R_c_measured_ring": measured_Rc,
                        "error_pct": err_pct(computed, measured_Rc),
                    }
                )
            object_table.append(
                {
                    "classical_object": name,
                    "scale": "bare_classical",
                    "R_c_classical": Rc_class,
                    "R_c_computed": Rc_class,
                    "R_c_measured_ring": measured_Rc,
                    "error_pct": err_pct(Rc_class, measured_Rc),
                }
            )
        object_table.sort(key=lambda d: d["error_pct"])

    diagnosis = {
        "pin": digest[:12],
        "wrong_application": [
            "onset formula α/φ was picked after the sweep (formula shopping)",
            "LOCK_ORDER=0.85 was a free cut; seed-closed is trit≥1/φ and MAD≤amp/φ^5",
            "Matsumoto a,b = −1.143/−0.714 are literature fits; BOM NIC sets Ga,Gb",
            "3-node chain is not identical-node κ (ends degree 1); ring/K3 is",
        ],
        "nic": {
            "Ga_S": GA,
            "Gb_S": GB,
            "a_dimless": a,
            "b_dimless": b,
            "R_ohm": phys.R_ohm,
            "alpha": phys.alpha,
            "beta": phys.beta,
        },
        "S_EM": S,
        "P_NEW": float(P_NEW),
        "residual_P_NEW": r_pnew,
        "residual_EM_catalog": r_em_panel,
        "kappa": kappa,
        "collapse_theta": COLLAPSE_THRESHOLD,
        "phi_inv": PHI_INV,
        "phi_inv4": PHI_INV4,
        "isolated_amp": amp_ref,
        "lle_isolated": lle,
        "classical_R_c_ohm": classical,
        "chain": {k: v for k, v in chain.items() if k != "probes"},
        "ring": {k: v for k, v in ring.items() if k != "probes"},
        "chain_probes": chain["probes"],
        "ring_probes": ring["probes"],
        "object_table": object_table[:12],
        "best_object": object_table[0] if object_table else None,
    }
    OUT.write_text(json.dumps(diagnosis, indent=2), encoding="utf-8")
    print("pin", diagnosis["pin"])
    print("NIC Ga", GA, "Gb", GB, "a", a, "b", b)
    print("amp_ref", amp_ref, "LLE", lle)
    print("chain onset", chain["onset_sigma"], "R_c", chain["onset_R_c_ohm"])
    print("ring  onset", ring["onset_sigma"], "R_c", ring["onset_R_c_ohm"])
    if object_table:
        print("BEST object", object_table[0])
        print("top 5:")
        for row in object_table[:5]:
            print(
                f"  {row['classical_object']:40s} {row['scale']:18s} "
                f"Rc_comp={row['R_c_computed']:.1f} meas={row['R_c_measured_ring']:.1f} "
                f"err={row['error_pct']:.3f}%"
            )
    print("wrote", OUT)


if __name__ == "__main__":
    main()
