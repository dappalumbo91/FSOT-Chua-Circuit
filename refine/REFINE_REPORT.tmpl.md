# FSOT pressure-point refinement (Targets 1–7), 2026-10-03
Primary engine: `src/rf.cpp` (C++20; Kennedy node with explicit single-pole NIC op-amps; build with `cmake -S . -B build -G Ninja && cmake --build build`).
Python cross-checks: `tools/xcheck_lyap.py`, `tools/bench_numbers.py`, `tools/closedform.py`.
Every prediction was locked and sha256-hashed **before** the comparison it is scored against:
| lock | file | sha256 |
|---|---|---|
| A (windows, closed form) | predictions/LOCK_A_2026-10-03_window_and_closedform.md | 400cdd10ee9b28bc7970f0891037755a80a7d59ca7cff69e1e20a7ebc1eaef4b |
| B (parasitics, tolerance, L vs L′) | predictions/LOCK_B_2026-10-03_parasitics_and_LvsLprime.md | 3594a469bbc6345a9e4e56724ff81f23c81d7d13c2f9f4a99ad94186ac81f79c |
| C (op-amp dressed pole) | predictions/LOCK_C_2026-10-03_opamp_pole.md | 86ae8340e12bd690c2e56d2b35fb508945c0907f5cfaefb3179c7d19782680f6 |
Verify with `sha256sum predictions/LOCK_*.md`. There is **no bench data yet**. "Measured" below means independent simulation (ngspice with TI models, eb C++ ring).

## Target 1: op-amp correction (LOCK C; genuine vs the rf runs, post-hoc vs SPICE)
Derivation: a single-pole op-amp gives u = Gx − εGẋ, so the NIC adds an effective capacitance ΔC1/C1 = αK with K = g1G1ε1 + p_in·g2G2ε2.
Both α and σ are divided by (1+αK), giving Δσc/σc = −(e_α − 1)·αK/(1+αK) with e_α = 2.44. The formula has no free parameters (datasheet GBW).
The Ledger-B GBW dressing changes this by < 0.01 %, i.e. 0.0000.
A bug in rf was found and fixed before any scored comparison: rail-pinned op-amp tangents were frozen when they should collapse.
In the ε→0 limit the buggy model gave σc 1.28 instead of the ideal 1.50. The buggy outputs are kept in `results/opamp_buggy_v1/` and were never scored.
@@OPAMP_TABLE@@
SPICE (TI TL082 macro-model) Δ vs SPICE ideal (interval arithmetic): r0 = 0: [−0.060, −0.045]; 18.44: [−0.060, −0.025]; 20: [−0.075, −0.020]; 35: [+0.100, +0.155].
**Verdict:**
- The adiabatic dressed-pole formula is **falsified as a quantitative predictor.** Only @@SCORE@@ cases fall within the locked tolerance (TL08xH and 741 at r0 = 18.44).
- It gets the wrong sign at r0 = 35 Ω, where both rf and SPICE show the TL082 *raising* σc by about +0.1.
- σc(GBW) is non-monotonic at r0 = 18.44 (rf, lag only): 2 MHz @@G2@@, 3 MHz @@G3@@, 5.25 MHz @@G5@@, 741 at k = 10 (≈10 MHz equivalent) +0.003. A first-order formula can't capture that. The TL08xH correction even changes sign between r0 = 18.44 (−0.040) and r0 = 20 (+0.022), so at the ±0.04 level the op-amp correction is structurally sensitive. Slew rate is irrelevant for TL082/TL08xH: lag-only gives 1.4824 vs 1.4777 at 3 MHz and 1.4568 vs 1.4570 at 5.25 MHz.
- The parameter-free rf 5-dim simulation does track SPICE: r0 = 20 inside the interval; r0 = 0, 18.44 and 35 within 0.003–0.014 of the interval edges.
- Branch N (FSOT NIC delay τ_N = r0·C2 = 1.844 µs) makes the node collapse to an equilibrium (λ1 = −0.29, no oscillation) with ideal or TL082 op-amps.
  That matches LOCK C's "loss of double scroll". But working TL082 Chua builds are routine in the literature, so **Branch N is disfavoured by existing bench practice**. A dedicated bench check is still listed in the guide.
- "Real op-amp lowers σc by 0.04–0.06": rf gives −0.019 (TL082, 3 MHz) / −0.040 (TL08xH) at 18.44 Ω; SPICE gives −0.025 to −0.060. Band supported: −0.02 to −0.06.
PNG: png/t1_opamp_delta_sigc.png

## Target 2: effective C1, C2, L with parasitics; tolerance spec (LOCK B, genuine)
- ΔC1 = 6–14 pF and ΔC2 = 12–38 pF (sources: TI datasheet input capacitance; breadboard 2–5 pF row-to-row per EEVblog #568 and the DigiKey TechForum).
  Coil C_s from SRF: 7.97 pF (Würth), ≤ 28.1 pF (TSL1315). Result: **Δσc = −0.0024 [−0.0015, −0.0034]**.
- ΔL_eff/L = ω²LC_s = 4.5e-5 to 1.6e-4 (the lock text says 5.7e-5 to 1.8e-4, an arithmetic slip in the lock; negligible either way).
- Branch C (universal FSOT reactance dressing, tanδ = k = 0.0393 → σc 1.0052) is **falsified** by the WIMA MKP2 datasheet:
  tanδ < 5e-4 @ 1 kHz and < 8e-4 @ 10 kHz, 49–79× below the prediction. So the FSOT dressing, if it exists, has to be inductor-specific (Branch L).
- Build tolerance spec for ±0.05 on σc: L ±1.2 %, C1 ±1.0 %, R ±1.0 %, C2 ±4.5 %, r0 ±0.33 Ω, node matching ≤ 1 %.

## Target 3: periodic windows (LOCK A H3a/b/c)
Median λ1 over 3–5 ICs, T = 20 000 τ, steps down to 0.001 Ω. Periodic means median λ1 ≤ 0.01.
| window | r0 range [Ω] | width |
|---|---|---|
| W1 | 9.59–10.18 | 0.59 Ω |
| W2 | 16.98–17.255 | 0.275 Ω |
| narrow | 18.208–18.211 | ≈ 0.004 Ω |
| narrow | 18.660–18.661 | ≈ 0.002 Ω |
| others (single 0.1 Ω grid points) | 0.4, 5.0, 12.4, 21.1, 23.8, 31.6, 33.0, 37.9 | ≤ 0.1 Ω |
- λ1(18.44) = 0.262/τ0 (C++), and 0.257 in the independent Python cross-check. Python also confirms 9.85 and 17.1 Ω are periodic (λ1 ≈ 2e-5).
- **H3a (no window within ±0.5 Ω): FALSIFIED.** Two hair-thin windows sit 0.23 Ω below and 0.22 Ω above 18.44 Ω.
  Margins: −1.25 % / +1.2 % to the narrow windows, and −1.19 Ω (−6.4 %) to the wide W2.
  In practice copper drift (0.072 Ω/K for an all-copper r0) sweeps across a 0.004 Ω window in < 0.1 K, so they're invisible on the bench. 18.44 Ω is robustly chaotic.
- **H3b (centres ≈ 18.44·φ^(−n/2) within ±2 %): FAIL.** W2 centre 17.12 is −7.2 % from n = 0; W1 centre 9.885 is +10.3 % from n = 3 (8.959).
- **H3c (W2/W1 = φ ± 3 %): FAIL.** The ratio is 1.732 (+7.0 %). It happens to sit near √3, which is noted only as a post-hoc observation, not a claim.
- Ring lock vs σ (24 seeds, `results/ring_vs_sigma_r*.tsv`): first full lock at σ = 1.60 for r0 = 17.1 (inside W2) vs 1.55 at 18.44, 18.21 and 18.66.
  Lock fractions at σ = 1.50: 13/24 at 18.44, 12/24 at 18.21, 23/24 at 18.66.
PNG: png/t3_lyap_bif_wide.png, png/t3_lyap_bif_fine_16p5_19p5.png

## Target 4: Branch L vs L′ discriminating tests (LOCK B, genuine; awaiting the bench)
| observable | L (r0 18.44) | L′ (r0 26.07) |
|---|---|---|
| Q_L | 25.44 | 17.99 |
| ring-down 2L/r | 2.386 ms | 1.688 ms |
| spiral frequency | 2558 Hz | 2568 Hz |
| lobe switching | 526 /s | 324 /s |
| λ1 | 1472 /s | 1088 /s |
| max abs V_C1 | 4.325 V | 4.339 V |
| frac abs V_C1 < 1 V | 0.056 | 0.043 |
| ring @ Rc 13.3 kΩ (σ 1.353) | 0/24 lock (escape) | 24/24 lock |
- Sim test: the Rc = 13.3 kΩ ring is binary.
- Bench tests:
  - (i) tank ring-down through 100 kΩ: τ_env 2.13 ms (L) vs 1.56 ms (L′);
  - (ii) the Rc = 13.3 kΩ ring;
  - (iii) lobe rate ratio 1.62.
- Spiral frequency and amplitude do not discriminate between L and L′.
PNG: png/t4_L_vs_Lprime_observables.png

## Target 5: closed-form σc seed (LOCK A F5a/F5b; genuine)
s* is the smallest coupling that makes J_m − s·e1e1ᵀ Hurwitz.
- F5a = s*(b)/3 = **1.3214** (−11.6 % vs 1.4954); F5b = **1.3172** (−11.9 %).
- Over the γ×α grid: corr 0.93, MSF/F5a = 1.28 ± 0.17. Over the γ×(b/a) grid: corr 0.89, ratio 1.70 ± 1.40.
- **Verdict:** this is a useful lower-bound-like seed. A constant FSOT factor (φ^(1/4) = 1.128 against the needed 1.132) fits only the nominal point, so it is post-hoc and rejected.
PNG: png/t5_closedform_vs_msf.png

## Target 6: refined error budget at r0 = 18.44 Ω (σ50 definition)
| term | value | label |
|---|---|---|
| ideal C++ MSF, mean over 16 ICs | 1.4955 | baseline |
| op-amp TL082, LOCK C formula | @@DL@@ | genuine (falsified) |
| op-amp TL082, rf 5-dim sim | @@DS@@ | post-lock sim |
| op-amp TL08xH, rf sim | @@DH@@ | post-lock sim |
| parasitics (LOCK B) | −0.0024 | genuine |
| definition 5/6 vs 50 % | +0.012 (0 for σ50) | – |
| **refined total, locked route** | **@@TL@@** | vs SPICE TL082 (1.45, 1.475]: misses by ≥ @@ML@@ |
| **refined total, sim route TL082 / TL08xH** | **@@TS@@ / @@TH@@** | both inside the SPICE interval; eb ring (1.44, 1.46]: TL08xH inside, TL082 +0.014 |
| ideal C++ ring σ50 | 1.4954 [1.4947, 1.4961] | reference |
No bench measurement exists yet. The bench must report rails, r0 (DCR and τ_env), the actual op-amp, and the lock fraction vs Rc (see the build guide).
PNG: png/t6_refined_budget.png

## Target 7: bench build guide
`build_visuals/BENCH_BUILD_GUIDE.md` (repo) covers:
- staged build with checkpoints: rails; NIC static test with expected O1/O2 and the negative current; passive network Ω checks; chaos signatures; ring Rc ladder;
- troubleshooting table with colour codes;
- r0 = 18.44 Ω assembly. Common 22 mH chokes are 43–82 Ω, which is too lossy, so use a low-DCR coil plus a series film resistor, or a gyrator, and verify by DCR and by tank ring-down τ_env = 2.13 ms.
