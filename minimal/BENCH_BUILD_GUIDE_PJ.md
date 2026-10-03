# Bench guide: FSOT Path J chaotic circuit (LOCK PJ), staged with meter checkpoints

**Circuit:** x‴ = −γ_rel x″ − Θ x′ + (κ/γ_rel)|x| − 1, with γ_rel = 0.42804, Θ = 0.91751 and κ/γ_rel = 0.73505 (FSOT; lock `7524bad0…`). |x| comes from a precision half-wave rectifier, so the diode knee is divided by the op-amp gain (LOCK B).

**Files:** schematic `png/schematic_pj.png`, breadboard `png/breadboard_pj.png`, hole-by-hole steps `build_checklist_pj.md`, Falstad `falstad/fsot_pj_theta_kg.url`, SPICE `spice/mkcir_pj.py` / `spice/run_lockpj.py`.

**Expected values:** every number below comes from ngspice with the TI TL082 macro-model at E96 values (`spice/out/lockpj.json`) or from the C++ engine (`pathj/pj`).
- The Falstad export round-trips and its part values are checked by `falstad/verify_minimal.py`.
- It has **not** been run in a browser in this pass.

## 0. Parts (1 % metal-film resistors, film capacitors)
| Ref | Value | Role |
|---|---|---|
| U1 | TL074 | U1–U4: three integrators and one inverter |
| U5 | TL072 | half A is the precision rectifier; half B is unused (grounded follower) |
| Da, Db | 1N4148 | rectifier diodes (band = cathode) |
| RA | 4.22 kΩ | R/γ_rel (exact 4205.2 Ω) |
| Rw | 1.96 kΩ | R/Θ (exact 1961.8 Ω) |
| Rx | 2.43 kΩ | R/G (exact 2448.8 Ω) |
| Rr | 1.21 kΩ | R/2G (exact 1224.4 Ω) |
| Rc | 40.2 kΩ | constant term, U = 9 V × 1.8k/40.2k = 0.403 V |
| R2, R3, R4, Rf, R5, Rf5 | 1.8 kΩ | |
| C1, C2, C3 | 100 nF film | τ0 = 180 µs; match them within 2 % (cap mismatch was not simulated) |
| Cd × 4 | 100 nF ceramic | decoupling |

**Tolerance:** in C++, 29 of 32 draws with γ, B and G each off by an independent ±1 % stay chaotic (PJ8). The E96 rounding (RA +0.35 %, Rw −0.09 %, Rx −0.77 %, Rr −1.2 %) is chaotic in ngspice (89–93 distinct maxima).

**Most common misreads:** 1.8k vs 18k; 2.43k vs 24.3k; 1.21k vs 12.1k. Measure every resistor with the DMM before inserting it.

## Stage 1. Rails and decoupling (chips not inserted)
Steps 3–11 of the checklist, without U1 and U5.
- **Check:** +T to GT = +9.00 V ± 0.1 V; −B to GB = −9.00 V; GT to GB = 0 Ω.

## Stage 2. Chips, power only
Insert U1 (TL074) and U5 (TL072) with the notches LEFT, then do steps 12–18 (input grounds, unused half).
- **Supply current:** +9 V draws ≈ 8.4 mA (6 amplifiers × 1.4 mA typ, TI TL07x datasheet; ≤ 15 mA max). Much more than that means a reversed chip or a short: switch off.

## Stage 3. Precision rectifier (U5a, R5, Rf5, Da, Db)
Do steps 26 and 34–37 only.
- **Test signal:** temporarily feed row 18 (the o3 node) from a divider: +9 V – 10 kΩ – row 18 – 1 kΩ – GND, giving ≈ +0.82 V.
- **Check with that input:** TP_r (d27) ≈ −0.82 V (r = −V_in), and u5 (row 22) ≈ −1.4 V (one diode drop below r).
- **Now feed the divider from −9 V:** TP_r ≈ 0 V (|r| < 10 mV), and u5 ≈ +0.6 V.
- **If r follows the input in both polarities:** Da and Db are reversed.
- Remove the test divider.

## Stage 4. Inverter U4 (R4, Rf)
Step 32, plus R4 (step 31).
- **Test:** temporarily feed column 16 a–e (o2) with the +0.82 V divider.
- **Check:** TP_w (i10) ≈ −0.82 V.
- Remove the divider.

## Stage 5. Integrators and the summing node (close the loop)
Steps 19–25, 27–30 and 33, in that order. Rr (step 25) goes in last, with the power off.
- **Before power-on, out of circuit:** C1, C2, C3 = 100 nF ± 2 %.
- **Power on. Scope CH1 on TP_x (h18), CH2 on TP_x′ (d16), X–Y mode, 0.5 V/div.**

| Checkpoint | Expected (ngspice TL082, E96) |
|---|---|
| V(o3) range | −1.39 V … +0.85 V, irregular (no repeating period) |
| V(o2) range | −1.10 … +0.78 V |
| V(o1) range | −0.82 … +0.97 V |
| DMM DC average, o3 | ≈ −0.25 V |
| DMM DC average, o2 | ≈ −0.05 V |
| DMM DC average, o1 | ≈ −0.09 V |
| True-RMS (AC+DC) of o3 | ≈ 0.55 V |
| Frequency counter on o3 | ≈ 800 Hz (ngspice 798 Hz E96, 822 Hz exact values; C++ 822 Hz) wandering by tens of Hz |
| X–Y (o3 vs o2) | single-band folded loop, offset to negative o3 |

- **Start-up:** the attractor was reached from V(o3) = −0.3 V and from the attractor point in ngspice (PJ7). In C++, 43 of 64 random starts reach it (PJ2). If it stalls on the rail, power-cycle.

## Troubleshooting
| Symptom | Likely cause | Fix |
|---|---|---|
| o3 stuck at ±7.5 V (rail latch) | Rr or the rectifier is not connected; Db reversed; Rx missing | Recheck Stage 3, the Jr wire (a6–a27) and Rr (e5–e6); power-cycle |
| Clean periodic loop | Rw wrong. With Rw = 1.8k (B = 1) the C++ scan gives 42/64 bounded but 0/64 chaotic (non-chaotic: periodic or steady) | Measure Rw = 1.96k out of circuit |
| Rail latch right after power-on, every time | Rx wrong. With Rx = 1.8k (G = 1) the C++ scan gives 0/64 bounded | Measure Rx = 2.43k out of circuit |
| No oscillation, o3 at a constant ≈ −0.55 V (x = −1/G) | missing integrator cap or an open R2/R3 | Check C1–C3 and R2, R3 |
| Amplitude scaled up or down but the shape is right | Rc value (sets U) | Rc = 40.2 kΩ; U scales all voltages |
| Frequency far from 800 Hz | capacitor value (all three set τ0) | 100 nF film caps |
| Noisy or hum-modulated | missing decoupling or a long GND loop | Cd1/Cd2 close to the pins; join the GND rails at both ends |
