# Bench test plan: FSOT Branch L vs standard circuit theory on cheap hardware (ESP32 + basic parts)

Written 2026-10-03 (ET). Model numbers come from `../results/` (C++ `eb`/`mc`) and `../../spice` (ngspice). Datasheet links point to manufacturer PDFs.

## 0. What the bench decides
FSOT Branch L: the inductor behaves as a series loss r0 = 18.440 Ω (γ = 0.15087). That gives σc = 1.4897, i.e. Rc* = 18000 Ω/σc = 12.08 kΩ.
Standard theory: σc follows the **measured** loss r_eff and the measured L, C1, C2, R of the actual parts.
Sensitivities at the BOM point (bench units, σ_equiv = 18000/Rc*, from the Monte Carlo regression `results/mc_A_*.tsv`, R² = 0.82):
dσ/d(ΔL/L) = +2.07, dσ/d(ΔC1/C1) = −2.43, dσ/d(ΔR/R) = −2.42, dσ/d(ΔC2/C2) = +0.56. In r: dσc/dr = −0.075/Ω locally (paired ±2 % γ runs), secant 18.44→26.07 Ω = −0.034/Ω.
**Test: measure r_eff(f), L, C1, C2, R. Compute σc_std from those numbers. Then compare the bench threshold with σc_std and with 1.4897.**

### Datasheet finding: common 22 mH chokes are too lossy
| part | L | DCR | source |
|---|---|---|---|
| Würth 7447720223 | 22 mH ±5 % | 43.23 Ω typ / 55 Ω max | https://www.we-online.com/components/products/datasheet/7447720223.pdf |
| Bourns RLB0913-223K | 22 mH ±10 % | 45.6 Ω typ / 56 Ω max, Q ≥ 30 @ 79.6 kHz | https://www.bourns.com/docs/Product-Datasheets/RLB0913.pdf |
| Bourns RL622-223K-RC | 22 mH ±10 % | 56 Ω max, Q ≥ 30 @ 79.6 kHz | https://www.bourns.com/docs/Product-Datasheets/rl622_series.pdf |
| Murata 22R226C (2200R) | 22 mH ±10 % | 82.5 Ω max, Q 100 @ 50 kHz | https://www.mouser.co.uk/datasheet/2/281/1/kmp_2200r-2487124.pdf |
| TDK TSL1315RA-103JR24 / -222JR55 | 10 mH / 2.2 mH ±5 % | 10 Ω / 2 Ω max | https://storage.sea.com.ua/tech_info/tdk/e532_tsl1315.pdf (Digi-Key lists the 10 mH part as obsolete, so stock is limited) |

With R = 1.8 kΩ the standard model (`results/std_r0scan.tsv`, `png/standard_sigc_vs_r_datasheets.png`) loses the double scroll for r ≳ 40 Ω.
At 40–48 Ω the node is periodic. At ≥ 50 Ω it settles to a stable equilibrium.
**So none of the 43–82 Ω chokes gives a chaotic node at the BOM values.** No datasheet lists Q in the 2–4 kHz band, so only the DCR can be used from the datasheet.
Options:
1. **Low-DCR stack:** 2× TSL1315-103J + 1× TSL1315-222J in series = 22.2 mH, DCR ≤ 22 Ω. Space the coils ≥ 3 cm apart and orient them at right angles.
   This is the only build where FSOT's r0 is a claim about a physical part, and step 1 tests it directly.
2. Gyrator (inductorless Chua, Torres & Aguirre, Electron. Lett. 36, 2000): r is chosen by hand, so this only calibrates the standard model.
3. Keep a 43–56 Ω choke and lower R. That changes β and γ, so the FSOT number for R = 1.8 kΩ no longer applies.

## 1. Inductor r_eff and Q at 2.5–3.4 kHz (ESP32)
(a) **Driven divider:** ESP32 DAC (GPIO25) → 1 kΩ 0.1 % Rs → coil → GND. ADC1 on both coil ends through the repo bias network (v = 1.65 + V/6).
Excite with a sine at 1.0, 2.0, 2.55, 3.0 and 3.39 kHz. Use I2S ADC sampling at ≥ 40 kS/s and lock-in demodulation over ≥ 1000 periods.
Compute Z = Rs·V_L/(V_s − V_L), then r_eff = Re Z and L = Im Z/ω. Calibrate against 22 Ω and 47 Ω 0.1 % resistors to remove sample-skew phase. Target: r ±0.5 Ω, L ±0.5 %.
(b) **Ring-down:** coil ‖ 100 nF film capacitor (measured). Kick it through 10 kΩ from a GPIO and fit the ADC envelope e^(−t/τd). Then Q = π f τd and r_eff = ωL/Q.
(c) DCR: 4-wire measurement, or a DMM on the 200 Ω range.
**Decision here:** compare r_eff(2.55 kHz) and r_eff(3.39 kHz) with 18.44 Ω (P0), 26.07 Ω (P1, L′) and 13.87 Ω (P2, post-hoc).
P2 implies r_eff ∝ f, so the ratio r_eff(3.39)/r_eff(2.55) should be 1.33. For copper plus ferrite, expect r_eff ≈ DCR with a small rise.

## 2. Esat and breakpoints
Measure the Chua-diode I–V at σ = 0: drive through a 10 kΩ pot from ±9 V and read current across a 100 Ω shunt. Fit Bp1, Bp2, Ga, Gb, Gc.
BOM values: Bp1 = 1.000 V, Bp2 = 6.97 V at Esat = 23/3 V.
A symmetric Esat has exactly zero effect on σc (x2 = R3/(R2+R3)·(R5+R6)/R6). Only asymmetry matters. The MC with ±5 % asymmetry shifted the mean by −0.012, within MC sampling error (±0.012).
Measure V_sat+ and V_sat− of each TL082. The TI datasheet gives only ±12 V min / ±13.5 V typ at ±15 V, RL = 10 kΩ: https://www.ti.com/lit/ds/symlink/tl082.pdf

## 3. σc sweep with fixed resistors
Rc = 18000/σ. E96 1 % values: 12.7 k (1.417), 12.4 k (1.452), 12.1 k (1.488), 11.8 k (1.525), 11.5 k (1.565), 11.3 k (1.593), 11.0 k (1.636).
For fine steps, use 11.0 k plus a 2 kΩ 10-turn trimmer per link, set to ±5 Ω with a DMM (σ ±0.0006).
Run ≥ 20 power cycles per σ. Use the firmware LOCK rule (trit agreement ≥ 1/φ over 1024 samples AND |V_C1| < Bp2), then fit a logistic to get σ50 and the 5/6 point.
Expected window width in the model is ≈ 0.007 in σ.
Initial conditions matter: σ50 = 1.483, 1.497, 1.521 and 1.582 for IC spreads ε = 0.01, 0.1, 1 and 3 (`results/analysis_basin.json`). Log the first 50 ms after power-on.

## 4. Precision needed
- σc_std uncertainty with measured parts (r ±0.5 Ω → ±0.038, C1 ±1 % → ±0.024, L ±0.5 % → ±0.010, R ±0.1 % → ±0.002) is about **±0.046 (1σ, RSS)**.
- FSOT and standard differ by about 0.075·|r_meas − 18.44|. Separating them at 2σ needs |r_meas − 18.44| ≳ 1.2 Ω. Closer than that, the direct r_eff measurement in step 1 is the sharper test.
- With datasheet tolerances only (R 1 %, C 5 %, L 10 %), the bench σc spread is SD 0.15 (95 %: 1.32–1.82). That cannot discriminate anything at the 0.035 level.
- Op-amp bias: in the C++ single-pole model, a TL082 (3 MHz, 8 V/µs) gives a threshold in (1.44, 1.46], against (1.50, 1.52] for an ideal op-amp. ngspice with the TI macromodel is in `../../spice`. A 741 at ×1 is slew-limited, with threshold in (1.2, 1.3], so do not use it.

- **Node mismatch.** A ring of three independently drawn nodes (R 1 %, C 5 %, L 10 %) needs σ = 1.631 ± 0.075 to lock under the firmware-style rule, against 1.525 for identical nodes (`results/mc_ringA_hetero.tsv`).
  Hand-match C1, C2 and L across nodes to ~1 %, or σ_bench will sit about 0.1 high whatever the theory.

## 5. Parts (quantities; prices not verified)
ESP32-WROOM-32 DevKit ×1–2 · TL082 ×3 (+2) · TSL1315RA-103JR24 ×6 + TSL1315RA-222JR55 ×3 (or 43–56 Ω chokes for a standard-only control) ·
10 nF C0G/film ×3 and 100 nF film ×3 (buy spares and hand-select to ±1 %) · 1 % resistors: 220 Ω ×6, 2.2 k ×3, 22 k ×6, 3.3 k ×3, 1.8 k ×3, Rc set 11.0–12.7 k ×3 each, 2 kΩ 10-turn trimmers ×3 ·
0.1 % 1 kΩ, 22 Ω, 47 Ω · bias dividers 300k/100k/150k ×3 · ±9 V supply, breadboard, DMM.
**Cost: not price-checked in this pass, so no figure is given.**
