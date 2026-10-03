# FSOT 2.1 Branch L: the inductor-loss ratio γ and the ring lock threshold σc

Status: **new branch of the theory (hypothesis), pin AEB2AD.** The predictions were locked before any simulation at these values:
`cpp/predictions/PREDICTIONS_2026-10-03_branchL_part1.md` (sha256 `04ebe3f4…02b4f6f1`) and
`..._part2.md` (sha256 `d6bd17be…a44a4cdd`).

## 1. What γ is
In dimensionless Chua form (x = V_C1/Bp, y = V_C2/Bp, z = R·i_L/Bp, t in units of τ = R·C2) a real inductor with
series resistance r0 adds one term:

    x' = α (y − x − h(x)) + σ Σ_ring(x_j − x)
    y' = x − y + z
    z' = −β y − γ z,      β = R²C2/L,   γ = β r0 / R = r0 R C2 / L

So γ is the ratio of the inductor's ohmic loss rate (r0/L) to the circuit clock (1/τ). It has no units (Ω·Ω·F/H = 1).

## 2. The FSOT law used (Ledger B, applied to a reactance)
FSOT 2.1 dresses an observable EM-domain magnitude c₀ as c = c₀·(1 + |S_EM|·f), where f = ALPHA is the Ledger B factor
and S_EM is the Electromagnetism domain scalar (D_eff = 7, look 1 at AEB2AD). Branch L postulates:

1. **What gets dressed.** The ideal inductor has one observable magnitude: its reactance |Z₀| = ωL. Its ideal loss is zero,
   and a dressing that multiplies zero gives zero. So the dressing acts on |Z|, not on r0.
2. **Passivity.** A real inductor is Z = r0 + jωL, so |Z|² = r0² + (ωL)². The reactive part stays ωL (that is the catalog L).
   The FSOT excess in |Z| can only be a real loss, and a passive one-port cannot have a negative real part.
3. **Which ω.** The node's own tank frequency ω_LC = 1/√(L·C2). This is the frequency at which the L–C2 tank stores and
   returns energy, and the frequency at which the ring exchanges energy through the y–z loop.

So (ωL)²(1+ε)² = r0² + (ωL)², with ε = |S_EM|·ALPHA. That gives:

    k   = √((1+ε)² − 1) = √(2ε + ε²)          (= 1/Q_L, the FSOT inductor quality factor)
    r0  = k · ω_LC L = k · √(L/C2)            [Ω]
    γ   = β r0 / R = k · √β                   [dimensionless]

r0 depends only on √(L/C2), the tank's characteristic impedance. It is unchanged when C1, C2, and L are all scaled by the
same factor k_t (the ×10/×100 Tinkercad time scaling), consistent with the FSOT invariance already shown for α, β, and σ.

## 3. Values (AEB2AD, mpmath dps 50; C++ f128/mp169 bit-identical to 45 digits)
| quantity | value | units |
|---|---|---|
| S_EM | 0.955728570095582708189529865… | 1 |
| ALPHA | 8.0829…e-4 (engine) | 1 |
| ε = \|S_EM\|·ALPHA | 7.72509421698849555e-4 | 1 |
| k = 1/Q_L | 0.0393143181831290647 | 1 |
| Q_L | 25.4360255045483541 | 1 |
| √(L/C2) | 469.041575982343 | Ω |
| **r0** | **18.4400497592861384** | **Ω** |
| β | 14.7272727… | 1 |
| **γ** | **0.150873134394159315** | **1** |

Domain-routing sensitivity: with Materials_Science (D_eff 8) instead of EM, r0 = 18.42007 Ω and γ = 0.150710. That is a
0.11 % change, and none of the gates move.

Physical meaning: a 22 mH audio-band inductor with Q ≈ 25 at 3.39 kHz, i.e. about 18 Ω of effective series loss. That is a
realistic value for a ferrite-core 22 mH part (real DCR plus core loss at kHz), but it is a prediction, not a fit.
Bench check: measure Q or ESR of the actual inductor at 3.4 kHz with an LCR meter. **FSOT says Q_L = 25.44.**

## 4. σc: the lock threshold
σc_pred is defined by the master-stability function of the 3-ring. The ring Laplacian's nonzero eigenvalue is 3, so the
transverse mode sees coupling 3σ. λ⊥(σ) is the largest Lyapunov exponent of the variational equation along the
synchronous double scroll, and σc is its zero crossing. It is a deterministic functional of the FSOT/BOM inputs
(a, b, c, α, β, γ_FSOT). No closed-form seed expression is claimed.

    λ⊥(1.475) = +0.001721 /τ,   λ⊥(1.500) = −0.001210 /τ
    σc_pred = 1.4897 (±0.0125 grid)  →  Rc_crit = αR/σc = 12.08 kΩ

Lock for Rc < 12.08 kΩ. φ (11.12 kΩ) lies just inside, with λ⊥(φ) = −0.0159/τ. φ² (6.88 kΩ) is deep inside, with
λ⊥ = −0.13/τ.

## 5. Rejected alternative
1/Q_L = ε (r0 = ε·√(L/C2) = 0.36 Ω). It treats the dressing as additive on a quantity whose ideal value is zero, which is
inconsistent with the multiplicative law c = c₀(1+|S|f). It was rejected on that structural ground before any simulation
at either value.

## 6. Disclosure
* Before deriving Branch L, the author knew from an r0 sweep that the gates hold for r0 ≈ 35–40 Ω and that r0 = 15–20 Ω
  was marginal. Blindness is therefore partial. The derivation was not tuned toward that window, and it actually lands
  outside it (18.44 Ω). The result is reported as it fell.
* The FSOT-2.1-Cpp engine describes Ledger B (f = ALPHA) as a catalog dressing, "not a prediction". Using it as a physical
  loss law is the new-branch hypothesis that the bench measurement of Q_L tests.

## 7. Outcome (simulation after the lock, 2000 τ, 6 seeds, dt 0.005, no clip, amplitude-checked lock)
| gate | predicted | measured | result |
|---|---|---|---|
| G1 single-node double scroll | PASS | λ1 = 0.245/τ, 171 lobe switches, max\|x\| 4.33 < x2 6.97 | PASS |
| G2 σ = 1 no lock | PASS | lock 0/6 (all 6 escape to the synchronized outer cycle, max\|x\| 7.35) | PASS (needs amplitude check) |
| G3 20 kΩ (σ = 0.9) no lock | PASS | lock 0/6 (escape, outer cycle) | PASS (needs amplitude check) |
| G4 σ = φ² lock | PASS | 6/6 | PASS |
| G5 σc_pred vs sweep | \|Δ\| ≤ 0.05 | sweep threshold 1.525 (σ = 1.500: 3/6; ≥ 1.525: 6/6) vs 1.4897; Δ = 0.035 | PASS |
| (cross-check) Python MSF and ring | — | `sim/msf.py` σc = 1.4892; `sim/run_sim.py` threshold 1.525 (1.475: 1/6, 1.500: 2/6) | agrees |
| G6 σ = φ locks iff σc < φ | lock | 6/6 | PASS |

Caveat on G2 and G3: without the amplitude check, those rings synchronize on the outer ±7.35 V limit cycle, and the old
lock law plus the old firmware would read LOCK. The amplitude condition (no tail sample beyond Bp2) is therefore part of
the gate and of the firmware.

## 8. Non-ideal check (C++ `fsot_chua_nonideal`, 2000 τ, r0 = 18.44 Ω)
Single-pole 741-class op-amps (GBW 1 MHz, SR 0.5 V/µs) at ×10 time scaling, with and without the corrected ADC load
(Thevenin 360 kΩ to 1.98 V):
- σ = 0.9 and σ = 1: all seeds escape to the outer cycle (±7.34 V) with trits equal. The amplitude check vetoes LOCK.
- σ = 1.5: locks on the double scroll (3/3, MAD/amp ≤ 0.05).
- σ = φ and σ = φ²: lock 3/3.
- Ideal op-amp, ×1: σ = 1.5 gives 2/3 locked and 1/3 escaped (the threshold region). φ and φ² lock 3/3.
Files: `cpp/results/nonideal_*.tsv`.

## 9. If the bench says otherwise (the next FSOT-consistent branch)
Branch L ties σc to one measurable number, Q_L(3.39 kHz) = 25.44. If the measured Q differs:
1. Branch L is falsified as a loss law. Report it; do not refit.
2. The FSOT-consistent next step is **Branch L′**: route the inductor through the domain of its physical loss mechanism
   (core = Materials_Science, D_eff 8, already shown: r0 = 18.42 Ω; winding = Electromagnetism). Then compose the
   dressings multiplicatively, (1+ε_EM)(1+ε_MS), which is the same Ledger B law applied once per orifice the
   reactance passes. That gives k = √((1+ε_EM)²(1+ε_MS)² − 1) ≈ 0.0556, r0 ≈ 26.1 Ω. That is a prediction to lock
   **before** the measurement, not after.
