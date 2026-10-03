# FSOT minimal chaotic circuit: answer attempt to Chua's question (2026-10-03)
Circuit: piecewise-linear jerk x''' = −A x'' − x' + |x| − 1 (Sprott/Linz class) built from 1 × TL074 + 1 × 1N4148 + 3 × 100 nF + 9 resistors.
Engines: `src/mj.cpp` (ideal, Lyapunov spectrum, bifurcation, homoclinic search), `src/oa.cpp` (full 4-op-amp model: GBW, slew, rails), ngspice (`spice/`), Falstad (`falstad/`).

## Locks (sha256, written before the corresponding runs)
| lock | content | sha256 |
|---|---|---|
| M1 | design, Branch J A = 1/φ (hypothesis), analytic eigen/Shilnikov/frequency predictions | 078343de14f49cf8116b9fb9c53ad7642bd6712e7d767903fb8733bd31df40d4 |
| M2 | bench knob edge, TL07x effect, SPICE chaos | 5a794149f2af44a1ee3ee16b110cb72f26a5bd9c535b684d175b2b1366113481 |
| J | side task: A derived from FSOT laws, independent of φ (J1 = k, J2 = γ) | 3683004b8c9d3a53325bc340d6d5eff0f37293ba245dcba0d4a960395617117f |
| D1 | no-post-hoc pass: knob A = γ_rel (R_A = 4205 Ω), secondary A = \|S_med\| (2744 Ω); τ0 and U_eff as engineering scales; Branch D = Shockley 1N4148 model (see REPO_SURVEY.md) | 9a9bd4cb83db98e088ba7898ea3272cb5cf4886f5c4d2c709a652c1df0f02ad1 |
| DJ | Branch DJ junction physics: n = 1 + S_EM, V_T = kT/q, I_s(T) ∝ T^(3/n) e^(−E_g/(n kT)); datasheet-blind decade and tempco predictions | f80d7d0d26b14cd584b19c12ead3de7d51a20bdf4e292f2c0673a05420db4467 |
| T | FSOT-picked topology: γ_rel fixed, 16 candidates, analytic screen, fewest-parts rule, so the winner is S-a | 61f259b203a56124d58b9df72323b6804f6ee7c9f332d8e12e1adfcf52ffccf7 |
| T2 | post-hoc small-basin γ_rel attractor; downstream predictions | 724228ea9cc29937f176c4150ba974667cd0a12098ae86a36a9090571526de61 |
| D2 | Branch D numbers from bd.cpp (edge at 27 °C not blind; blind edge shifts at 0 °C, 60 °C and ±12 V; knob points), locked before ngspice | 3fe1b39aa51f12a9695e51f8d3299c1d11acc582ac2e86e47d8f1a34efd3d55c |

## Scorecard
| prediction | result | verdict |
|---|---|---|
| M1 P2/P3 eigenvalues; Shilnikov ratio holds at E− (0.133), fails at E+ (1.027) | exact (polynomial roots) | holds |
| M1 P4 Σλ = −A, λ2 = 0 | −0.61803, \|λ2\| < 2e-4 (8 ICs) | holds |
| M1 P5 f = 958.7 Hz ± 12 % | 864 Hz (−9.9 %) | holds (inside band) |
| M1 P6 chaos at A = 0.613/0.618/0.623 (ideal PWL) | λ1 0.044–0.051 | holds (genuine) |
| M1 P7 λ1 ∈ [0.02, 0.07] | 0.048 | holds (literature-informed, not genuine) |
| M1 P8 amplitude | x ∈ [−2.445, 1.186] U_eff | holds |
| Shilnikov proof route | no homoclinic orbit to E− for A ∈ [0.3, 1.2] (stable manifold comes from infinity) | route unavailable |
| M2 B3 TL07x full model: \|ΔA_c\| ≤ 0.005, f ≤ 1 %, λ1 ± 15 % | ΔA_c = +0.002; f −0.1 %; λ1 +10 % (0.053) | holds; ngspice ideal-E vs TI model also agree |
| M2 B1 edge R_A,c = 2.812 kΩ [2.64, 2.98] | ideal model 2.810 kΩ, but **ngspice with a real 1N4148: ≈ 3.07 kΩ** | **falsified** (real-diode knee) |
| M2 B4 SPICE chaotic at R_A = φR = 2912.5 Ω | **period-2 limit cycle**; chaos only for R_A ≥ 3.08 kΩ | **falsified** |
| J1 A = k = 0.0393; J2 A = γ = 0.1509 | both unbounded (no attractor); distance to the 0.6182 hairline −0.579 / −0.467 | **falsified** |
| D-0 Branch D edge at 27 °C 3100 Ω (not blind) | ngspice 3080 Ω | consistent |
| D-T0 / D-T60 / D-V12 blind edge shifts −50 / +40 / −40 Ω | ngspice −40 / +50 / −20 Ω | **confirmed** (all in band) |
| K-1 FSOT knob R/γ_rel = 4205 Ω not chaotic (rail latch) | ngspice rail latch (x 3.97–7.48 V) | **confirmed: the FSOT knob gives no chaos** |
| K′-1 \|S_med\| knob 2744 Ω periodic, 876 Hz | periodic, 872 Hz | confirmed (no chaos) |

Notes:
- There is a hair-thin periodic window at A = 0.6182 in the ideal model, 0.0002 above 1/φ.
- LOCK M2's window list is approximate: the true periodic gaps are 0.549–0.563, 0.571–0.572 and 0.586–0.598. Those were facts, not predictions.

## Proof status (honest)
- **Rigorous:** the eigen-structure and divergence are exact (closed-form polynomial roots); E− is a Shilnikov-type saddle-focus.
- **Not reached:** a Shilnikov homoclinic, because none exists in the scanned range. **Interval proof (proof/, C++20):** the covering relation N_a ⇒ N_a under the x = 0 return map is VERIFIED at A = 1/φ, so a periodic orbit provably exists. A two-symbol horseshoe (proof of chaos) is **not reached**. See proof/README.md. No chaos proof is possible at the FSOT knob γ_rel, because it has no bounded attractor.
- **Numerical:** positive λ1 across 8 seeds (ideal and full op-amp models) and broadband spectra in ngspice at R_A = 3.16 kΩ (λ ≈ 310 /s from two-run divergence).

## The FSOT content, honestly
- No FSOT law tested here derives A. 1/φ was a hypothesis: it is chaotic in the ideal PWL model, but not with a real diode.
- The φ-independent derivations (J1, J2) fail. τ0 and U_eff are inherited from the FSOT Chua BOM, not derived.
- The circuit is a valid minimal chaotic circuit, but at present it is a standard Sprott-class design, not an FSOT derivation.
- **No-post-hoc pass (LOCK D1/D2):** the repo survey (REPO_SURVEY.md) finds no FSOT absolute time or voltage scales and no FSOT junction physics. The FSOT damping knob γ_rel predicts, correctly, *no chaos*. The chaotic band is a circuit-physics result: Branch D, with zero free parameters, confirmed three blind edge shifts.
- The bench value 3.16 kΩ therefore remains an engineering setpoint inside that band. It is **not** an FSOT value; it was originally post-hoc from ngspice. See results/LOCK_D_score.md and png/lockD2_edge_shifts.png.

## Comparison with Chua's circuit (Kennedy two-op-amp realisation in this repo)
| | Chua (repo node) | FSOT minimal jerk (this) | Muthuswamy–Chua (3-element) |
|---|---|---|---|
| parts (excluding decoupling) | 1 TL082, 7 R, 2 C, 1 L (22 mH, DCR-critical) = 11 | 1 TL074, 1 diode, 9 R, 3 C = 14 | L, C + memristor emulator (many op-amps or multipliers) |
| nonlinear elements | 1 (5-segment NIC) | 1 (one diode) | 1 (memristor) |
| inductor | yes (r0 must be 18.44 ± 0.33 Ω; common chokes too lossy) | **no** | yes |
| bifurcation knobs | R, r0, L, C1, C2 (σc elasticities up to 2.4) | one ratio A = R/R_A; C cancels; diode drop only rescales the amplitude (ideal) | – |
| proof strength | known: Shilnikov plus a computer-assisted proof in the literature (Galias; Matsumoto–Chua–Komuro) | eigen conditions only; CAP open | – |
| tolerance sensitivity | high (L ±1.2 %, C1 ±1 %, r0 ±0.33 Ω for ±0.05) | SPICE chaos for R_A ≈ 3.08–3.40 kΩ (windows at 3.12, 3.24, 3.32 kΩ): the bench value has −2.5 % / +7 % margin | – |
PNGs (in `png/`):
- `lambda1_vs_A_cpp.png`
- `spice_RA_scan.png`
- `attractors_cpp_vs_spice.png`
- `schematic_minimal.png`
- `breadboard_minimal.png`

## Branch DJ, FSOT topology and chaos proof (LOCK DJ, T and T2; results/LOCK_DJ_T_score.md)
- **DJ** (n = 1 + S_EM = 1.9557): the decade slope (0.1157 V predicted, 0.1183 V observed), the low-current decade and the per-decade tempco change are confirmed against Vishay Fig. 1. The 100 mA decade (series resistance) and the Diodes Inc max-spec decade are falsified. The DJ-derived knob still sits outside the chaos band. See png/lockDJ_diode.png.
- **Topology** (γ_rel fixed): 16 candidates were examined. The locked winner S-a, x‴ = −γ_rel x″ − x + sgn(x), is **falsified**: it is unbounded in C++ and runs a rail-to-rail cycle in ngspice. No FSOT-fixed design produced a working chaotic circuit, so no new schematic, breadboard or bench guide was made.
- **Proof:** at the exact FSOT knob A = γ_rel, the ideal jerk has a small-basin attractor (seen post-hoc). The C++20 interval prover verifies a **2-symbol horseshoe for P⁴, giving topological entropy ≥ ln2/4 ≈ 0.173**. See proof/README.md, proof/horseshoe_run.log and png/gammarel_section_horseshoe.png. With the real diode, this set is not reached (T2-4 and T2-5 falsified).
