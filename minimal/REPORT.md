# FSOT minimal chaotic circuit: answer attempt to Chua's question (2026-10-03)
Circuit: piecewise-linear jerk x''' = −A x'' − x' + |x| − 1 (Sprott/Linz class) built from 1 × TL074 + 1 × 1N4148 + 3 × 100 nF + 9 resistors.
Engines: `src/mj.cpp` (ideal, Lyapunov spectrum, bifurcation, homoclinic search), `src/oa.cpp` (full 4-op-amp model: GBW, slew, rails), ngspice (`spice/`), Falstad (`falstad/`).

## Locks (sha256, written before the corresponding runs)
| lock | content | sha256 |
|---|---|---|
| M1 | design, Branch J A = 1/φ (hypothesis), analytic eigen/Shilnikov/frequency predictions | 078343de14f49cf8116b9fb9c53ad7642bd6712e7d767903fb8733bd31df40d4 |
| M2 | bench knob edge, TL07x effect, SPICE chaos | 5a794149f2af44a1ee3ee16b110cb72f26a5bd9c535b684d175b2b1366113481 |
| J | side task: A derived from FSOT laws, independent of φ (J1 = k, J2 = γ) | 3683004b8c9d3a53325bc340d6d5eff0f37293ba245dcba0d4a960395617117f |

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
Notes:
- There is a hair-thin periodic window at A = 0.6182 in the ideal model, 0.0002 above 1/φ.
- LOCK M2's window list is approximate: the true periodic gaps are 0.549–0.563, 0.571–0.572 and 0.586–0.598. Those were facts, not predictions.

## Proof status (honest)
- **Rigorous:** the eigen-structure and divergence are exact (closed-form polynomial roots); E− is a Shilnikov-type saddle-focus.
- **Not reached:** a Shilnikov homoclinic, because none exists in the scanned range. A computer-assisted interval proof (covering relations or a topological horseshoe on a return map) is **not yet implemented**. This is the main open item.
- **Numerical:** positive λ1 across 8 seeds (ideal and full op-amp models) and broadband spectra in ngspice at R_A = 3.16 kΩ (λ ≈ 310 /s from two-run divergence).

## The FSOT content, honestly
- No FSOT law tested here derives A. 1/φ was a hypothesis: it is chaotic in the ideal PWL model, but not with a real diode.
- The φ-independent derivations (J1, J2) fail. τ0 and U_eff are inherited from the FSOT Chua BOM, not derived.
- The circuit is a valid minimal chaotic circuit, but at present it is a standard Sprott-class design, not an FSOT derivation. The bench value R_A = 3.16 kΩ is post-hoc (from ngspice).

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
