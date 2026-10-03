# Lock B: written 2026-10-03 (ET) BEFORE any comparison with datasheets or bench data (sim numbers from rf/eb runs listed)

## Target 2: effective C1, C2, L and FSOT reactance dressing
- k = sqrt((1+|S_EM|·ALPHA)^2 − 1) = 0.0393143 (Branch L loss angle at ω_LC = 2π·3393.19 Hz).
- **Branch C (genuine consequence IF the Ledger B dressing is universal for reactances):** every capacitor has loss angle tanδ = k = 0.0393 at ω_LC,
  so parallel loss R·G = R·ω_LC·C·k. For C1: g1p = 0.0150873; for C2: g2p = 0.150873 (= γ).
  Predicted σc_MSF: both capacitors dressed → **1.0052 ± 0.0126**; C1 only → 1.4567 ± 0.0034 (rf msf, 4 ICs, T = 6000; files results/branchC*.txt).
  Bench observable: film capacitor tanδ(3.4 kHz) = 0.039.
- Standard parasitics (sources: TI TL08xH input capacitance 2 pF differential / 1 pF common-mode, https://www.ti.com/lit/ds/symlink/tl082.pdf;
  breadboard 2–5 pF row-to-row and 20–25 pF rail-to-rail, EEVblog #568 https://www.eevblog.com/2014/01/15/eevblog-568-solderless-breadboard-capacitance/ and DigiKey TechForum https://forum.digikey.com/t/the-real-impact-of-breadboard-capacitance-on-prototype-designs/38817;
  inductor self-capacitance from SRF: C_s = 1/((2π·SRF)²·L), giving Würth 7447720223 (SRF 0.38 MHz typ) 7.97 pF and TDK TSL1315-103J (SRF ≥ 0.3 MHz) ≤ 28.1 pF):
  - ΔC1 = 2 op-amp + inputs (2 × 1–2 pF) + 2 adjacent rows (4–10 pF) + jumpers ⇒ 6–14 pF, i.e. +0.06 % to +0.14 % of 10 nF.
  - ΔC2 = coil self-capacitance (in parallel with C2) + rows ⇒ 12–38 pF ≈ +0.012 % to +0.038 %.
  - ΔL_eff/L = ω²·L·C_s at 2.55 kHz ≈ 5.7e-5 to 1.8e-4 (negligible).
  - Predicted shift (MC regression coefficients −2.43 per unit ΔC1/C1, +0.56 per ΔC2/C2): **Δσc_parasitic = −0.0015 to −0.0034** (central −0.0024).
- **Build tolerance spec implied by the README's ±0.05 falsification window** (RSS, equal allocation 0.025 per term; coefficients from MC regression and from dσc/dr = −0.075/Ω):
  L ±1.2 %, C1 ±1.0 %, R (1.8 k) ±1.0 %, C2 ±4.5 %, r_eff ±0.33 Ω. Node-to-node matching of C1, C2, L: ≤ 1 % (the mismatch MC gives +0.106 at 5/10 %).

## Target 4: Branch L (r0 = 18.440 Ω) vs Branch L′ (r0 = 26.069 Ω): predictions for the bench (ideal op-amp model, nominal BOM)
| observable | Branch L | Branch L′ | source |
|---|---|---|---|
| Q_L at 3.39 kHz (= 1/k) | 25.44 | 17.99 | analytic |
| LC ring-down amplitude time constant 2L/r | 2.386 ms | 1.688 ms | analytic |
| cycles to 1/e at 3.39 kHz (Q/π) | 8.10 | 5.73 | analytic |
| spiral (rotation) frequency | 0.4604/τ = 2558 Hz | 0.4622/τ = 2568 Hz | rf, 8 ICs, T = 20000 |
| lobe-switching rate (x crossing ±1 between lobes) | 9.46 per 100 τ = 526 /s | 5.83 per 100 τ = 324 /s | same |
| largest Lyapunov exponent | 0.265/τ = 1472 /s | 0.196/τ = 1088 /s | same |
| max abs(V_C1) | 4.325 V | 4.339 V | same |
| fraction of time with abs(V_C1) < 1 V | 0.0561 | 0.0432 | same |
| 3-ring σc (MSF; locked earlier) | 1.4897 (σ50 1.4954) | 1.2395 (σ50 1.2379) | earlier locks |
| ring at Rc = 13.3 kΩ (σ = 1.3534), 24 seeds | 0/24 lock, all escape to ±7.35 V | 24/24 lock, double scroll ±4.34 V | eb ring |
| ring at Rc = 12.5 kΩ (σ = 1.4400), 24 seeds | 0/24 lock (escape) | 24/24 lock | eb ring |
Discriminating sim test: the Rc = 13.3 kΩ ring (binary). Discriminating bench test: (i) Q / ring-down of the coil + 100 nF film tank; (ii) the Rc = 13.3 kΩ ring (escape vs lock);
(iii) the lobe-switching rate of one node (ratio L/L′ = 1.62). Spiral frequency and amplitude do NOT discriminate (differences 0.4 % and 0.3 %).
