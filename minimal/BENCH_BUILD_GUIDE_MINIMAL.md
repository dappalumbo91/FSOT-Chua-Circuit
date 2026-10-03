# Bench build guide: FSOT minimal chaotic circuit (1 × TL074, 1 × 1N4148, 3 × 100 nF film, 9 resistors)
Hole-by-hole placement: `build_checklist_minimal.md` and `png/breadboard_minimal.png`. Schematic: `png/schematic_minimal.png`.
**Don't move to the next stage until the checkpoint passes.** Measure every resistor before inserting it.
Use **R_A = 3.16 kΩ** (2.7 kΩ + 1 kΩ trimmer set to 3.16 kΩ). The locked FSOT value φ·R = 2.91 kΩ is a **period-2 limit cycle** with a real diode (ngspice). See the report.

## Parts and colour codes
| part | value | 4-band (5 %) | 5-band (1 %) |
|---|---|---|---|
| R2, R3, R4, Rf, Rw, Rx | 1.8 kΩ | brown-grey-red | brown-grey-black-brown |
| Rd | 900 Ω (two 1.8 kΩ in parallel, or 909 Ω E96 white-black-white-black-brown) | | |
| Rc | 40.2 kΩ (E96: yellow-black-red-red-brown) or 39 kΩ (orange-white-orange) | | |
| R_A | 2.7 kΩ red-violet-red + 1 kΩ trimmer | | |
| C1, C2, C3 | 100 nF film (code 104), matched within 2 % | | |
| D1 | 1N4148: the black band is the cathode | | |
| U1 | TL074 (or TL084) quad JFET op-amp; the notch is pin 1 side | | |

## Stage 1: rails (no chip)
Wire the rails and the GND tie (checklist steps 2–6, without the chip).
**Checkpoint 1:** top red rail = +9.0 V ± 0.1; bottom blue = −9.0 V ± 0.1; the two GND rails measure < 0.5 Ω apart with power off.

## Stage 2: chip, grounds and decoupling (no R or C yet)
Steps 1 and 7–10: put pins 3, 5, 10 and 12 to GND.
**Checkpoint 2 (power on):** supply current ≈ 5.6 mA typ (TL074: 1.4 mA per amplifier typ, TI datasheet), ≤ 10 mA.
Pin 4 = +9 V, pin 11 = −9 V. Outputs (pins 1, 7, 8, 14) will drift to a rail, which is normal with open inputs.

## Stage 3: U4 summer and diode alone (static check of the only nonlinearity)
Insert R4, Rf, D1, Rd and the Jx wire, but leave o2 and o3 driven from your bench: temporarily feed row 16 bottom (o2) and row 18 top (x) from a stiff source.
Expected outputs, with o4 = −(o2 + 2·max(x − Vd, 0)) and Vd ≈ 0.55–0.65 V:
| o2 | x | pin 14 (o4) |
|---|---|---|
| 0 V | 0 V | 0 V ± 0.02 |
| +1.00 V | 0 V | −1.00 V ± 0.03 |
| 0 V | +2.00 V | −2.8 V ± 0.15 (= −2·(2 − Vd)) |
| 0 V | −2.00 V | 0 V ± 0.02 (diode blocks) |
Remove the temporary sources.

## Stage 4: three integrators (passives in)
Insert C1, RA, R2, C2, R3, C3, Jn1, Rc, Rx and Rw.
**Checkpoint 4 (power off, Ω):**
| between | expected |
|---|---|
| row 10b ↔ row 11b (o1–n1) | R_A ‖ C1 → reads R_A (3.16 kΩ) after the cap charges |
| row 5b ↔ +9 V rail | 40.2 kΩ |
| row 18t ↔ row 22t, diode test | 0.55–0.7 V forward, OL reverse |

## Stage 5: power on (chaos check)
**Checkpoint 5 (scope, CH1 = TP_x j16, CH2 = TP_x' d16, X–Y mode):** these numbers are SPICE (TI macro-model) at R_A = 3.16 kΩ.
| observable | expected |
|---|---|
| V_x range | −1.75 V … +1.77 V |
| dominant frequency (FFT of V_x) | ≈ 865 Hz (ideal model 864 Hz) |
| waveform | irregular spiral; peaks never repeat (period-2 / period-4 loops = not yet chaotic) |
| λ1 | ≈ 300 /s (two-run divergence in SPICE; ideal-op-amp C++ model at A = 1/φ: 267 /s) |
**Knob test (bench-decidable):** turn R_A down slowly from 3.3 kΩ.
- ngspice says: chaos (with narrow windows near 3.12, 3.24 and 3.32 kΩ) down to ≈ 3.08 kΩ, then period-8 (3.06), period-4 (2.98–3.04) and period-2 (≤ 2.96 kΩ).
- LOCK M2 (ideal-diode model) said the edge is at 2.81 kΩ [2.64, 2.98]. The bench decides between the two.

## Troubleshooting
| symptom | cause | fix |
|---|---|---|
| everything at a rail at power-on | a non-inverting input not grounded (pins 3, 5, 10, 12) | check the black jumpers |
| chip hot | TL074 inserted backwards, so the supplies are reversed (pin 4 must be +9 V) | notch to the left; replace the chip |
| clean sine, about 0.9 kHz, growing to the rails | Rc missing (no constant) or the diode reversed | Rc from row 5b to +9 V; band of D1 toward row 22 |
| V_x sits at ≈ −0.4…−1 V, no oscillation | R_A too small (A too large → stable) or a cap shorted | check R_A ≥ 2.9 kΩ; check the caps |
| output slams to the rails | R_A far too large (A < 0.55, unbounded) or Rw/Rx swapped with Rc | R_A ≤ 3.3 kΩ; measure resistors |
| clean period-1/2/4 loop | R_A below the chaos edge | raise R_A toward 3.16–3.22 kΩ |
| wrong frequency (e.g. 8.6 kHz) | a 10 nF cap (103) instead of 100 nF (104) | check the cap codes |
| 1.8 k vs 18 k mix-up | band 3 red (1.8 k) vs orange (18 k) | measure |
| 50/60 Hz hum | scope ground not on the board's GND rail | clip to the GND rail |
