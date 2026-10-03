# REPO_SURVEY: applied FSOT math relevant to the minimal jerk circuit (2026-10-03)

Repos were listed with `gh repo list dappalumbo91 --limit 200`, which returned about 40 repos. These were read read-only: FSOT-2.1-Cpp (pin AEB2AD), FSOT-2.1-Lean, FSOT-2.0-code, FSOT-Materials and fsot-law-circuit. In the table, *path:line* refers to the clones under /workspace.

## (a) Dimensionless control and damping ratios
| finding | where |
|---|---|
| The FSOT circuit precedent maps each law term directly onto a resistor ratio with no knobs: K = 0.420108763649888 gives R_f = K·R | fsot-law-circuit/docs/DESIGN.md:29, results/design.json:3 |
| Θ = C_EFF·P_VAR = 0.917510271 is used as a resistor-ratio threshold | fsot-law-circuit/results/design.json:3; FSOT-2.1-Cpp/include/fsot/engine.hpp:129 (P_VAR) |
| S = K(T1+T2+T3). S_obs ≈ +0.955 and S_med ≈ −0.656 are output levels, chosen through Rule O (observer ring). T3 ≈ 2e-17 is dropped | fsot-law-circuit/docs/DESIGN.md:29,93; engine.hpp:189-210 (observed branch of T1) |
| **The transport law dS/dt = κ∂²S − γ_rel(S−S_eq) is mapped to the RC relaxation law. γ_rel = 0.42804344605980688 is FSOT's damping (relaxation) rate per unit time scale; κ = 0.31463253730207974 and κ/γ_rel = 0.73504813634763333** | fsot-law-circuit/docs/DESIGN.md:33, results/design.json:3 (from fsot_dynamics.py) |
| Bleed-off term t_r = τ_L·ln((S_obs−S_med)/(S_obs−Θ)) | fsot-law-circuit/predictions/LOCK_B_2026-10-03_bench_bands.md:20 |
| Constants used by the Chua repo: S_EM = 0.9557285700955828, k = 0.0393143, γ = 0.1508731 (Branch L) | FSOT-Chua-Circuit FREEZE.yaml |
| Engine constants: ALPHA = ln π/(e φ^13), THETA_S, P_VAR, CHAOS = GAMMA_C/OMEGA | FSOT-2.1-Cpp/include/fsot/engine.hpp:117,123,129,133 |
| Domain D_eff values: Electromagnetism 4, Condensed_Matter 9, Thermodynamics 10 | FSOT-2.1-Cpp/include/fsot/core.hpp:19-22 |

## (b) Time scales and voltage scales
- fsot-law-circuit, DESIGN.md:19-20: U = 2.495 V (TL431) is "the engineering voltage scale and cancels from every dimensionless prediction". τ_L = R_L·C = 0.100 s is the time scale. Predictions are made in units of τ_L and U, e.g. "P2 period T = 11.289 τ_L" at DESIGN.md:52.
- FSOT-Chua-Circuit: τ0 and the voltage scale come from the BOM (RC and the Esat/Bp breakpoints, FREEZE.yaml). FSOT supplies only the dimensionless ratios.
- **Conclusion:** none of the surveyed repos derives an absolute time or voltage from FSOT for a circuit. The established FSOT practice is that τ0 and U_eff are engineering units that cancel, and only dimensionless quantities are predicted.

## (c) Semiconductor, diode and junction physics
- **No FSOT treatment of Shockley, thermal voltage, ideality or exponential junction behaviour was found** (searched with rg -i "shockley|thermal voltage|ideality|diode|junction|kT/q" across all clones).
- The closest items are domain labels only. FSOT-2.0-code fsot/compute.py:307,409 contains HVAC_Thermal_Systems and Semiconductor_Physics_Public_Panel, both mapped to `term1.quirkMod`, a generic scalar with no I–V law. FSOT-2.1-Lean README.md:719 lists semiconductor panels. FSOT-2.1-Cpp engine.hpp:168 maps Condensed_Matter to A_BLEED/E.
- FSOT-Materials has no diode or junction model.

## (d) Chaos, Lyapunov and bifurcation
- closed_forms.gen.inc:46 gives Feigenbaum δ = (e² − γ^(1/3))/(1/φ + 1/√φ) ≈ 4.6692; :48 gives α; :139-141 give alternate forms.
- FSOT-2.0-code compute.py:1025 (mirrored in FSOT-2.1-Lean kaggle/.../fsot_compute.py:726) gives Henon_Lyapunov = φ·(γ√2/e)/ln π·0.99 ≈ 0.4192. This value carries a 0.99 factor and is specific to the Hénon map.
- engine.hpp:172,176 gives CHAOS = GAMMA_C/OMEGA as the domain scalar for Meteorology, Atmospheric and Geophysics, and CHAOS/2 for Seismology.
- No FSOT result covers jerk or Chua flows, Shilnikov chaos, or interval proofs.

## What this implies for the minimal circuit
1. A knob derived from FSOT must be a dimensionless FSOT scalar, and its physical role must match. A x'' is a linear damping or relaxation term measured in units of τ0. The only FSOT quantity already applied in hardware as a relaxation rate per time unit is **γ_rel = 0.428043** (fsot-law-circuit DESIGN.md:33). Rule O offers a secondary candidate: the free-running, unobserved node level |S_med| ≈ 0.656 (DESIGN.md:29).
2. τ0 and U_eff follow the fsot-law-circuit precedent: they are engineering scales and are not FSOT predictions. This statement is honest and is not a derivation.
3. Branch D (diode knee) has no FSOT precedent. The only option with zero free parameters is standard junction physics: Shockley with V_T = k_B T/q and the 1N4148 model parameters already in the frozen netlist (spice/mkcir.py:9). The FSOT contribution there is nil, and the report says so.
