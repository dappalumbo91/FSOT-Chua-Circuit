# LOCK D2: Branch D numbers (computed with src/bd.cpp after LOCK D1, locked BEFORE any ngspice run of these cases)

bd.cpp sha256: 4999b01432e87bc3b2eb23dc2c86f73bbf59ff1e41a8eff14bc51c6e3f1494bc. Raw output is in results/bd/*.tsv. Chaos criterion: λ1 > 0.005/τ0 and no rail contact, for any of the 3 initial conditions. Scan step is 10 Ω.

| ID | observable | Branch D prediction | blind? | pass band (ngspice TI TL082 + 1N4148) |
|---|---|---|---|---|
| D-0 | chaos edge at 27 °C, Vs = ±9 V | 3100 Ω (chaos at 3100–3490 with windows) | **NO** (ngspice ≈ 3070–3080 already known) | consistency only: within ±40 Ω |
| D-T0 | edge shift at 0 °C (.temp 0) | ΔR_edge = −50 Ω relative to 27 °C (edge 3050) | YES | ngspice shift in [−90, −10] Ω (sign and size) |
| D-T60 | edge shift at 60 °C (.temp 60) | ΔR_edge = +40 Ω (edge 3140) | YES | ngspice shift in [0, +80] Ω |
| D-V12 | edge shift at Vs = ±12 V (U = 0.537 V; Rc kept) | ΔR_edge = −40 Ω (edge 3060) | YES | ngspice shift in [−80, 0] Ω |
| K-1 | derived knob R_A = R/γ_rel = 4205 Ω (and E96 4.22 kΩ) | NOT chaotic; latches to the op-amp rail (x pinned at the rail) | YES | ngspice: not chaotic (rail latch or non-chaotic) |
| K′-1 | R_A = 2744 Ω (A = \|S_med\|) | periodic (period-1); f = 876 Hz ±3 %; x in [−1.62, 1.35] V ±5 % | YES | ngspice periodic, f within 3 % |

Consequence, stated before scoring: if K-1 holds, **the FSOT-derived knob does not produce the chaotic attractor**, and the bench guide cannot carry an FSOT-derived chaotic R_A. The chaotic R_A range then comes from the circuit model (Branch D physics), not from FSOT.
