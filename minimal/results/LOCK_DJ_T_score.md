# Scorecard for LOCK DJ, LOCK T and LOCK T2 (each scored after its lock)

## Branch DJ (FSOT junction physics: n = 1 + S_EM = 1.955729)
Data: Vishay 1N4148 Fig. 1 (typical values), digitised by datasheets/digitize_fig1.py into datasheets/fig1_digitized.json. V_F at 25 °C: 0.498 / 0.610 / 0.728 / 0.874 V at 0.1 / 1 / 10 / 100 mA. Tempco: −2.22 / −1.85 / −1.52 / −1.16 mV/K.

| ID | prediction | observed | verdict |
|---|---|---|---|
| DJ1 V_F(10 mA) − V_F(1 mA) | 0.1157 V | 0.1183 V (+2.2 %) | **CONFIRMED**. The SPICE model's N = 1.752 would give 0.1036 V (−12 %) |
| DJ2 V_F(100 mA) − V_F(10 mA) | 0.1157 V | 0.1458 V | **FALSIFIED**, as expected: R_s is not in DJ |
| DJ3 V_F(1 mA) − V_F(0.1 mA) | 0.1157 V | 0.1117 V (−3.5 %) | **CONFIRMED** |
| DJ4 tempco change per decade | +0.388 mV/K | +0.351 mV/K (0.1 → 10 mA mean; −9.6 %) | **CONFIRMED** |
| DJ5 tempco at 1 mA (conditional on V_F; the formula is standard and n cancels) | −1.97 mV/K | −1.85 mV/K (+6 %) | confirmed. Not FSOT-specific |
| DJ6 Diodes Inc max-spec decade | 0.1157 V ±20 % | 0.140 V (+21 %) | **FALSIFIED** (narrowly; max limits, not typical values) |
| DJ-K knob with DJ | R/γ_rel = 4205 Ω rail-latches; DJ cannot reach the chaos band | rail latch (topo/bd_ic N = 1.955729); DJ chaos edge 3100 Ω (A = 0.58) | **CONFIRMED**. The DJ-re-derived knob does not reach chaos |

## LOCK T (FSOT-picked topology, A = γ_rel fixed): 16 candidates examined (7 analytic F1 + 9 F2, all simulated)
| ID | prediction | observed | verdict |
|---|---|---|---|
| Selection | winner = S-a, x''' = −γ_rel x'' − x + sgn(x) (12 parts) | — | rule applied as locked |
| T1 S-a chaotic (C++) | chaotic in ≥ 3 of 4 initial conditions | unbounded in 4 of 4 and in 12 of 12 (topo/tj_all.txt) | **FALSIFIED** |
| T2 / T3 / T5 | sum, frequency and symmetry | not applicable (no attractor) | — |
| T4 S-a in ngspice (TI TL082, 4.22 kΩ) | chaotic | rail-to-rail period-2 relaxation (2 distinct maxima, 548 Hz) | **FALSIFIED** |
| F1 (7, analytic) | none chaotic (A_eff outside the bands) | consistent with existing canonical data | analytic |
| Other F2 | S-c bounded? A-c? (open, T6) | only A-c was bounded, in 1 of 4 initial conditions (λ1 0.0162). All others unbounded | reported, not scored |

## LOCK T2 (post-hoc: small-basin attractor of the canonical jerk at A = γ_rel)
| ID | prediction | observed | verdict |
|---|---|---|---|
| T2-1 ≥ 6 of 8 initial conditions at radius 0.02 bounded and chaotic | | 0 of 8 (at radius 0.001: 6 of 8; at 0.005: 3 of 8). The basin is about 1e-3 | **FALSIFIED** |
| T2-2 sum = −γ_rel | | identity holds for the flow; not independently measured | — |
| T2-3 816 Hz (NOT blind: from the tj output) | | λ1 = 0.0156/τ0 and 0.147 crossings/τ0 on the attractor | not scored |
| T2-4 Branch D at 4205 Ω from the mapped initial condition: chaotic | | rail latch (8 of 8 initial conditions; topo/bd_ic) | **FALSIFIED** |
| T2-5 ngspice at 4205 Ω from the mapped initial condition: chaotic | | rail latch (V(o3) 3.98–7.48 V) | **FALSIFIED** |

**Bottom line:**
- DJ reproduces the Shockley decade slope and the tempco structure with zero fitted parameters (4 confirmed, 2 falsified).
- No FSOT-fixed (γ_rel) design produced a working chaotic circuit. The locked topology winner failed in C++ and in ngspice.
- The only γ_rel attractor found is a fragile, small-basin set in the ideal model, and it does not survive the real diode.
