# Error budget for the FSOT Branch L σc prediction (3-node Kennedy–Chua ring)

Date: 2026-10-03 (ET). Code: C++20 `src/eb.hpp`, `src/eb.cpp`, `src/mc.cpp` (build: `cmake -S . -B build -G Ninja && cmake --build build`).
Analysis: `tools/*.py` (Python is the cross-check only). Raw outputs: `results/`. Figures: `png/`. Every number below is read from those files.

Baseline (locked earlier): r0 = 18.4400497592861 Ω, γ = 0.150873134394159, σc_MSF = 1.4897 (sha256 `04ebe3f4…`, `d6bd17be…`). The earlier 2000 τ sweep reported 1.525 (5/6 rule, grid 0.025, 6 seeds). Gap = 0.035.

## 1. Measured σc with confidence interval (C++, same model, r0 = 18.44 Ω)
| estimator | value | 95 % CI | file |
|---|---|---|---|
| MSF, mean over 16 ICs (T = 20000 τ, dt = 0.005) | 1.4955 | [1.4942, 1.4968] (IC SD 0.0027) | `results/msf_fine_T20000_dt005.tsv` |
| MSF, canonical IC only (the locked procedure) | 1.4895 | – | same |
| Ring lock probability 50 % (σ50), logistic fit, 48 seeds, grid 0.001, T = 2000 τ | **1.4954** | **[1.4947, 1.4961]** (bootstrap) | `results/ring_fine_base.tsv` |
| Ring 5/6 point from the logistic fit | 1.5075 | – | same |
| Ring 5/6 rule on the fine grid | 1.511 | [1.505, 1.524] | same |
| ngspice, ideal op-amp (1 GHz pole), 3 ICs, strict "all lock above" rule | (1.52, 1.53] (1.49 and 1.50: 1/3; 1.52: 2/3) | – | `../spice/out/ring_ideal_r0_18.44.jsonl` |
| ngspice, TI TL082 macromodel (±9.19 V rails) | (1.45, 1.475] | – | `../spice/out/ring_tl082_r0_18.44.jsonl` |
| C++ single-pole TL082, GBW 3 MHz / SR 8 V/µs (datasheet min), 3 seeds | (1.44, 1.46] | – | `results/nonideal_tl082min.tsv` |
| same, GBW 5.25 MHz / SR 20 V/µs (TL08xH typ) | (1.46, 1.48] | – | `results/nonideal_tl082typ.tsv` |
| same + ADC bias load (360 kΩ to 1.98 V) | (1.44, 1.46] | – | `results/nonideal_tl082min_adcload.tsv` |
| uA741 at real time scale (GBW 1 MHz, SR 0.5 V/µs), slew-limited | (1.2, 1.3] | – | `results/nonideal_lm741_low.tsv` |
TL082 values are from TI's datasheet (https://www.ti.com/lit/ds/symlink/tl082.pdf): GBW 3 MHz (NS/PS/M) or 5.25 MHz, SR 8 V/µs min / 20 typ.

## 2. Decomposition of the 0.035 gap (1.4897 → 1.525)
| # | term | kind | shift | evidence |
|---|---|---|---|---|
| 1 | Locked MSF used one IC; the IC mean is higher | numerical | +0.0058 | 1.4895 vs 1.4955 |
| 2 | dt 0.005 → 0.0025; transient 200 → 2000 τ | numerical | −0.0007; −0.0008 (inside CI) | `msf_fine_T20000_dt0025.tsv`, `_trans2000.tsv` |
| 3 | MSF (linear) vs finite-amplitude basin race (σ50) | model | −0.0001 (none) | 1.4955 vs 1.4954 |
| 4 | 50 % point → 5/6 lock probability (window width w = 0.0075, w·ln5 = 0.012) | definition of "threshold" | +0.012 | logistic fit |
| 5 | 5/6 rule on a 0.025 grid with 6 seeds (1.500 had 2–3/6, so the next grid point 1.525 was reported) | grid/seed quantisation | +0.0175 | fine-grid rule 1.511, logistic 5/6 1.5075 |
| | **sum** | | **+0.035** | |
| – | Lock-rule constants: MAD φ⁻³/φ⁻⁵, trit 0.9, tail 200 τ | numerical | σ50 within ±0.0008 | `ring_madcut_*`, `ring_tritcut_0.9`, `ring_tail200` |
| – | Window length T = 8000 τ (tail 2000) | finite-time | σ50 = 1.5025 (+0.007) | `ring_T8000.tsv` (late escapes) |
| – | No amplitude check (outer-cycle sync read as LOCK) | rule | σ50 = 1.356 (−0.14) | `ring_noampcheck.tsv` |
| – | IC spread ε (basin study, 24 seeds) | IC protocol | σ50 = 1.4435 / 1.4606 / 1.4825 / 1.4969 / 1.5031 / 1.5211 / 1.5820 at ε = 1e−6 / 1e−4 / 0.01 / 0.1 / 0.3 / 1 / 3 | `analysis_basin.json` (ε ≤ 1e−4 has not converged in 2000 τ) |
| – | Ring eigenvalue = 3σ check: nonlinear 3-ring transverse growth crosses 0 between σ 1.46 and 1.48. MSF(3σ) crosses between 1.48 and 1.50 (T = 3000, noisy) | model check | consistent | `ringeig.tsv` |
**Three independent codes at r0 = 18.44 Ω:** locked MSF 1.4897 (IC-mean 1.4955); C++ ring σ50 1.4954; ngspice ideal 50 % crossing between 1.50 and 1.51 (1/3 at 1.49–1.50, 3/3 at 1.51; the strict rule gives (1.52, 1.53] because of one slow IC at 1.52). With real TL082s: ngspice macromodel (1.45, 1.475], C++ single-pole (1.44, 1.46]. The SPICE − MSF difference with an ideal op-amp is ≤ +0.02 and inside the 3-IC resolution. The TL082 difference is −0.03 to −0.04.

**Conclusion.** The gap is fully accounted for by numerics and the threshold definition: single-IC MSF (+0.006), the 5/6 vs 50 % definition (+0.012), and grid/seed quantisation (+0.0175).
Under the repo IC law, the MSF matches the finite-amplitude lock threshold to 1e−4. r0 does not enter the gap, because the prediction and the "measurement" share the same model.
Physical non-idealities **lower** the threshold: TL082 by 0.04–0.06 (C++ and SPICE agree), and a 741 at ×1 by about 0.25. They are hardware corrections, not explanations of the in-model gap.

### Physical sensitivities (paired ±2 % runs, 8 ICs, `results/analysis_sens.json`)
| p | p0 | dσc/dp | elasticity |
|---|---|---|---|
| γ (r0) | 0.15087 | −9.19 ± 0.31 (−0.075 per Ω) | −0.93 |
| a | −1.3636 | −0.41 | +0.37 |
| b | −0.7364 | −2.15 | +1.06 |
| c | 8.2636 | 0 | 0 |
| x2 (Bp2/Bp1) | 6.970 | 0 | 0 |
| α | 10 | +0.365 | +2.44 |
| β | 14.727 | −0.102 | −1.00 |
c and x2 have zero local effect because the synchronous orbit never reaches the outer segment. They only set where the outer cycle starts (see `png/regime_x2_gamma.png`).
A symmetric Esat has exactly zero effect.

## 3. FSOT refinements (locked BEFORE comparison)
`predictions/PREDICTIONS_2026-10-03_refinements.md`, sha256 **`0d4166786c143451cf645f65015d009f0544e0e9fd182ea3b6fbf1e725835787`**, locked 01:13 ET. The ring sims at these r0 were run afterwards.
| rank | id | r0 [Ω] | σc_MSF (locked) | Rc* | status | in-model ring σ50 (after lock) |
|---|---|---|---|---|---|---|
| 1 | P0 Branch L | 18.440 | 1.4897 (IC mean 1.4955) | 12.08 kΩ | genuine | 1.4954 |
| 2 | P1 Branch L′ (EM ⊕ Materials_Science dressing, k = 0.05558) | 26.069 | 1.2395 ± 0.0035 | 14.52 kΩ | genuine as a form; the choice of the second domain is a modelling choice | 1.2379 [1.2352, 1.2402] |
| 3 | P3 Esat | – | = P0 exactly | – | genuine (algebraic) | – |
| 4 | P2 frequency-dependent dressing r0 = k·2πf·L at the self-consistent rotation frequency f = 2551 Hz | 13.87 | 1.7002 ± 0.0069 | 10.59 kΩ | **post-hoc**, and not unique (the rms-frequency variant has no fixed point) | 1.6796 [1.6771, 1.6821] |
The in-model comparisons only test MSF ≈ σ50. That holds for P0 and P1 to ≤ 0.002, and for P2 to 0.02. P0, P1 and P2 differ only in r0, so **only hardware (a measured r_eff) can rank them** (see §4 and the bench plan).

## 4. FSOT vs standard circuit-design prediction
**(1) Datasheet-only inputs.** No datasheet gives Q in the 2–4 kHz band, so the standard r is the DCR.
Würth 7447720223: 43.23 Ω typ / 55 Ω max. Bourns RLB0913-223K: 45.6 / 56. Bourns RL622-223K-RC: 56 max. Murata 22R226C: 82.5 max (links in `docs/BENCH_TEST_PLAN.md`).
Standard model at BOM values (`results/std_r0scan.tsv`, `png/standard_sigc_vs_r_datasheets.png`): double scroll up to about 38 Ω (σc falls from 2.259 at r = 0 to about 1.03 at 36 Ω).
At 40–48 Ω the node is periodic. At ≥ 50 Ω it decays to an equilibrium. **So the standard prediction for any of these chokes is "no chaotic node, no σc at all".**
The only cheap low-DCR route found is the TDK TSL1315 stack (DCR ≤ 22 Ω). Datasheet-only, that gives σc ∈ [1.39 (r = 22), 2.26 (r = 0)].
Using the cited typ/max DCR ratios of Würth (0.786) and Bourns (0.814) as an assumption gives r ≈ 17.3–22 Ω.
**(2) Monte Carlo over tolerances** (uniform ±tol, all six NIC resistors, R, C1, C2, L, DCR; σ_equiv = 18000/Rc*; `results/analysis_mc.json`, `png/mc_sigc_histograms.png`):
| scenario | double-scroll builds | σc mean ± SD | 2.5–97.5 % |
|---|---|---|---|
| A: R 1 %, C 5 %, L 10 %, r = 18.44 | 93 % | 1.545 ± 0.150 | 1.315–1.816 |
| B: R 5 %, C 10 %, L 20 %, r = 18.44 | 59 % (19 % escape to outer cycle) | 1.544 ± 0.205 | 1.228–1.887 |
| C: A + Esat asymmetry ±5 % | 98 % | 1.533 ± 0.148 | 1.309–1.815 |
| D: A with TSL stack r ∈ U[17.3, 22] | 94 % | 1.516 ± 0.160 | 1.259–1.793 |
| E: R 5 %, C 10 %, L 20 %, r ∈ U[0, 22] | 58 % | 1.732 ± 0.259 | 1.281–2.211 |
| F: A with Würth r ∈ U[43.23, 55] | 19 % | 0.974 ± 0.065 (double-scroll subset) | 0.865–1.113 |
L dominates the spread (correlation 0.76, coefficient +2.07 per unit ΔL/L), then C1 (−2.43) and R (−2.42).
The MC mean sits about 0.05 above the nominal 1.4955 because σc is convex in the parameters.
**Ring with mismatched nodes** (`results/mc_ring*.tsv`): three independently drawn nodes plus three coupling resistors. Threshold = the first grid σ (step 0.025) where 2 of 3 seeds lock for 4 consecutive grid points. With this rule the identical-node nominal ring gives 1.525.
A (R 1 %, C 5 %, L 10 %), n = 80: **1.631 ± 0.075** (2.5–97.5 %: 1.475–1.751). Node mismatch adds a mean +0.106, because the φ⁻⁴ MAD criterion needs extra coupling to pull non-identical nodes together.
B (5/10/20 %), n = 80: 1.719 ± 0.158, but only 48 % of the drawn reference nodes are double scroll, so B is mostly a "broken build" statistic.
The mismatch shift is about 3× the whole 0.035 gap. It is the largest single systematic a real bench will show, unless the nodes are matched (hand-selected C1, C2, L to about 1 %).
**(3) Comparison.** FSOT single point: 1.4897 (σ50 1.4954). Standard with r = 22 Ω max: 1.39. Standard with a nominal r of 17.3–22 Ω: about 1.39–1.55.
Unmeasured-tolerance spread: SD 0.15–0.26. FSOT and standard differ only through r, by 0.075·|r − 18.44| per Ω.
The tolerance spread is 4× larger than the whole gap under study, so a build from datasheet values cannot discriminate.
**Required bench precision:** measure r_eff(f) to ±0.5 Ω, L to ±0.5 %, C1 to ±1 %, R to ±0.1 %. Then σc_std has 1σ ≈ ±0.046 (r ±0.038, C1 ±0.024, L ±0.010).
Discrimination at 2σ is possible only if |r_meas − 18.44| ≳ 1.2 Ω. If r_meas comes out within about 1 Ω of 18.44, σc alone cannot tell them apart.
The sharper test is the direct r_eff(2.5–3.4 kHz) measurement against 18.44 Ω (P0) / 26.07 (P1) / 13.87 (P2).
**(4) Published experiment-vs-model agreement for Chua circuits:**
- Kennedy, "Robust op amp realization of Chua's circuit", Frequenz 46 (1992) 66–80, https://nonlinear.eecs.berkeley.edu/chaos/RobustOpAmpRealizationOfChuaCircuit.pdf.
  Parts were R 5 %, C 5 %, L 10 % (TOKO 10RB 18 mH, measured RL = 13.5 Ω). The experimental R-bifurcation sequence is: 2.00 k equilibrium, 1.88 k P1, 1.85 k P2, 1.84 k P4, 1.825 k P3, 1.79 k Rössler, 1.74–1.49 k double scroll, 1.40 k outer cycle.
  SPICE with the AD712 macromodel reproduces the attractors qualitatively. No numeric threshold error is reported, and Kennedy says the RL effect is small.
- Masante, "Experimental Realization and Synchronization of a Chua Circuit", UC Davis course report 2017 (not peer-reviewed), https://csc.ucdavis.edu/~chaos/courses/poci/Projects2017/Masante/NCASO2017_report_Dany-Masante_ChuaCircuit.pdf.
  Experiment vs simulation: 11.81–18.81 % relative error in bifurcation resistances. The P3/P4 pair sits at 1677/1669 Ω in experiment vs 1993/1992 Ω numerically.
- de Magistris, di Bernardo, Petrarca, NOLTA IEICE 4(4) 462 (2013), https://www.jstage.jst.go.jp/article/nolta/4/4/4_462/_pdf/-char/en.
  Inductorless nodes with 0.1 % parts. Desynchronisation thresholds of 4-node networks are "in excellent agreement" with MSF. This is graphical only; no percentage is given.
- Burbano-L., Yaghouti, Petrarca, de Magistris, di Bernardo, IEEE TCAS-I 67(3) 927 (2020), https://www.iris.unina.it/retrieve/c0afa78d-1b73-494f-9de4-3e82775de6fc/Synchronization_in_Multiplex_Networks_of_Chuas_Circuits_Theory_and_Experiments.pdf.
  Measured sync loss at Rlink > 783 Ω vs MSF 687 Ω, i.e. α 22.97 vs 26.17. That is 14 % in resistance, 12 % in coupling.
So the standard method's documented real-world precision is about 10–20 % in the bifurcation or coupling resistance, and about 12–14 % in the best controlled sync experiment.
Our required ±3 % (±0.046 in σc) is about 4× tighter than anything published. It is plausible only with every component measured.

## 5. Pressure-point map (`png/`)
- `regime_gamma_beta.png`: the BOM/FSOT point (γ 0.151, β 14.73) sits in the double-scroll band. Outer-cycle escape starts about 14 % lower in β (L +16 %).
  Single-scroll/periodic starts about 24 % higher in β. **β (i.e. L) is the sensitive direction**, and it is why 19 % of the L ±20 % builds escape.
  γ alone tolerates 0 to about 0.3 at β = 14.7.
- `regime_ba_alpha.png`, `regime_x2_gamma.png`: b/a and α show the classic narrow double-scroll band. x2 below about 4.4 pushes the orbit onto the outer segment. In γ there are narrow periodic windows at γ ≈ 0.08 (r ≈ 10 Ω, also seen in `std_r0scan.tsv`) and γ ≈ 0.14 (r ≈ 17 Ω, grid 0.02, canonical IC, T = 1000). The second sits right next to the FSOT point and makes the single node fragile there. A bench r_eff of about 17 Ω could show a periodic, not chaotic, node.
- `sigc_gamma_alpha.png`, `sigc_gamma_ba.png`: σc_MSF falls with γ and b/a and rises with α. The gradients match §2.
- `mapnet_N_topo*.png` (N = 3–6, ring vs all-to-all, γ = 0.10 / 0.151 / 0.213): the 5/6 thresholds at γ 0.151 are ring 1.6 / 2.3 / 3.3 / 4.6 and all-to-all 1.6 / 1.2 / 1.0 / 0.8 (grid 0.1).
  MSF scaling 3·1.4955/λ2 gives 1.50 / 2.24 / 3.25 / 4.49 and 1.50 / 1.12 / 0.90 / 0.75. Cluster states (1 < clusters < N, not locked) appear mainly in the N = 6 ring near threshold (14 runs at γ 0.151, 41 at γ 0.213). Ring N = 6 at γ = 0.10 does not lock below σ = 5.
- Robust: lock-rule constants, dt, ADC loading, c, and symmetric Esat. Sensitive: L (β), C1 (α), r (γ), the amplitude check, and the IC spread.

## Refined budget (2026-10-03, see refine/REFINE_REPORT.md, Target 6)
| term | value |
|---|---|
| ideal C++ MSF, IC-mean | 1.4955 |
| op-amp TL082: LOCK C formula / rf sim / TL08xH sim | −0.0627 / −0.0194 / −0.0401 |
| parasitics (LOCK B) | −0.0024 |
| refined total, locked route / sim TL082 / sim TL08xH | 1.4304 / 1.4737 / 1.4530 |
| SPICE TI TL082 at r0 18.44 Ω | (1.45, 1.475] |
