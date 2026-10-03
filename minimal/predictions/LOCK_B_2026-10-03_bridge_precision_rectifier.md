# LOCK B: bridging ideal and hardware at A = γ_rel. Derivation and blind predictions, locked before any simulation of this design

## Dimensionless knee group
For the existing board, ε = n·V_T / U_eff ≈ 1.9557 · 25.69 mV / (0.403 + 0.6 V) ≈ 0.05 (Branch DJ). This rounds the |x| corner, and at γ_rel it destroys the small-basin set (LOCK T2-4 and T2-5, falsified).
- FSOT has **no voltage scale** (REPO_SURVEY §b). So no FSOT-derived U_eff exists, and FSOT cannot fix ε through U_eff. Choosing U_eff to make ε equal some FSOT ratio would be an unmotivated pick, so it is rejected.
- The only FSOT-consistent choice is **ε → 0, a precision rectifier**: the diode sits inside an op-amp loop, and the knee becomes ε_PR = n·V_T / (A_OL · U).
  - n = 1 + S_EM (DJ), A_OL = 200 V/mV (TL07x typical datasheet value), U = 9 V · R/R_c = 0.403 V.
  - That gives ε_PR ≈ 0.0503 / (2e5 · 0.403) ≈ **6.2e-7**.
  - The circuit then realises the ideal canonical jerk at A = γ_rel to about 1e-6. Its dynamics are independent of U, because the system is homogeneous.

## Design (B-PR), no free parameters
x''' = −γ_rel x'' − x' − x + 2·max(x, 0) − 1, which is the canonical |x| − 1.
- U1: summing integrator with inputs R_A = R/γ_rel = 4.22 kΩ (E96; the exact value is 4205.2 Ω) from o1, R from o3 (−x), R from o4 (−x'), R/2 = 900 Ω from r (+2·max), and R_c = 40.2 kΩ from +9 V (−U).
- U2 and U3: integrators.
- U4: unity inverter, o4 = −o2 = U·x'.
- U5: precision half-wave rectifier, r = −max(x, 0) (R_in = R_f = 1.8 kΩ, 2 × 1N4148).
- Total: 5 op-amp sections (TL074 + TL072), 2 diodes, R = 1.8 kΩ, C = 100 nF, τ0 = 180 µs.
- State map: o3 = U·x, o2 = −U·x′, o1 = U·x″.

## Blind predictions (C++ = topo/bpr.cpp with the DJ soft knee of width ε_PR; ngspice uses TI TL082 models and 1N4148)
| ID | prediction | band |
|---|---|---|
| B1 | C++, started on the attractor (canonical (−1.04, −0.2, 0.2)): bounded, λ1 = 0.0156/τ0 (= 86.7 /s) | λ1 ±20 % |
| B2 | dominant frequency 0.147/τ0 = **817 Hz** | ±5 % |
| B3 | amplitude: x ∈ [−2.339, 1.448]·U, i.e. V(o3) ∈ [−0.943, 0.584] V | ±5 % |
| B4 | **basin is NOT usable:** of 16 seeds drawn uniformly (RNG seed 1) in the attractor bounding box x ∈ [−2.34, 1.45], x′ ∈ [−1, 1], x″ ∈ [−1, 1], **≤ 2** stay bounded (C++). Reason: as ε → 0 the basin tends to the ideal one, which is about 1e-3 wide (T2) | ≤ 2/16 |
| B5 | ngspice from the mapped attractor initial condition: bounded and chaotic (> 40 distinct maxima). Note: the TL07x finite-gain-bandwidth shift is ΔA ≈ +0.002 (M2 B3); whether the thin set survives that is uncertain | as stated |
| B6 | ngspice from the default start (V(o3) = −0.3 V): escapes to the rail (not chaotic) | as stated |

Consequence, stated before testing: even if B1–B3 and B5 hold, B4 says the γ_rel attractor is **not a usable bench design** (no usable basin). Step 3 (building) is triggered only if B4 is falsified *and* B5 holds.
