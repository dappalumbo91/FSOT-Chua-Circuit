# Build checklist — 3-node ring, σ = φ² (Rc = 6.8 kΩ + 75 Ω)

Board: standard 830-point (rows 1–63, holes a–e bottom / f–j top, centre gap between e and f).
Rails: top outer = **+9.19 V (red)**, top inner = **GND**, bottom inner = **GND**, bottom outer = **−9.19 V (blue)**.
If your board's rails are split in the middle (gap near row 30), bridge each rail across the gap with a short wire of the rail's colour.
Supply: two bench supplies in series (or ±9 V then trim): (+) of PS1 → top +V rail, PS1 (−)/PS2 (+) → GND rails, PS2 (−) → bottom −V rail.
**Before power-on**: set the rails so U2's saturated output reads 7.67 V (SPICE: ±9.19 V for TL082, ±9.66 V for 741 models). Bp1 = Esat·3.3/25.3 = 1.00 V.
Rail positions written '@ row N' mean the rail hole nearest row N — electrically any hole on that same rail is equivalent.
741 alternative (no TL082): use two 741s per node (U1 for R1/R2/R3, U2 for R4/R5/R6): 741 pin 3 = + (to V_C1), pin 2 = −, pin 6 = out, pin 7 = +V, pin 4 = −V; this layout is for the TL082 (one chip per node, matching the repo BOM).
Hairpin = resistor stood upright with one lead bent back down (the two holes are only 1–2 rows apart).

Other gates: swap the three Rc pairs → σ = φ: 10 kΩ + 1.13 kΩ (E96) = 11 130 Ω (target 11 124.61 Ω); σ = 1: 18 kΩ + jumper; σ = 0.9: 20 kΩ + jumper; open: remove the three coupling wires JcA/JcB/JcC.

| Step | Part | Value | Lead 1 | Lead 2 | Notes |
|---|---|---|---|---|---|
| 1 | UA | TL082 | pin 1 → e3, pin 2 → e4, pin 3 → e5, pin 4 → e6, pin 8 → f3, pin 7 → f4, pin 6 → f5, pin 5 → f6 | | notch/dot toward the left (lower row numbers); pin 1 bottom-left |
| 2 | UB | TL082 | pin 1 → e17, pin 2 → e18, pin 3 → e19, pin 4 → e20, pin 8 → f17, pin 7 → f18, pin 6 → f19, pin 5 → f20 | | notch/dot toward the left (lower row numbers); pin 1 bottom-left |
| 3 | UC | TL082 | pin 1 → e31, pin 2 → e32, pin 3 → e33, pin 4 → e34, pin 8 → f31, pin 7 → f32, pin 6 → f33, pin 5 → f34 | | notch/dot toward the left (lower row numbers); pin 1 bottom-left |
| 4 | JvccA | red wire | g3 | top +V rail (red) @ row 3 |  |
| 5 | JveeA | blue wire | d6 | bottom −V rail (blue) @ row 6 |  |
| 6 | JvccB | red wire | g17 | top +V rail (red) @ row 17 |  |
| 7 | JveeB | blue wire | d20 | bottom −V rail (blue) @ row 19 |  |
| 8 | JvccC | red wire | g31 | top +V rail (red) @ row 31 |  |
| 9 | JveeC | blue wire | d34 | bottom −V rail (blue) @ row 34 |  |
| 10 | Jgnd | black wire | top GND rail @ row 61 | bottom GND rail @ row 61 | ties top and bottom GND rails |
| 11 | Cd+A | 100nF | h3 | top GND rail @ row 4 | decoupling, pin 8 to GND |
| 12 | Cd-A | 100nF | c6 | bottom GND rail @ row 7 | decoupling, pin 4 to GND |
| 13 | R2A | 220Ω | d3 | d4 | upright (hairpin) mount |
| 14 | R1A | 220Ω | d5 | c3 | upright (hairpin) mount |
| 15 | R3A | 2.2kΩ | c4 | bottom GND rail @ row 4 |  |
| 16 | R5A | 22kΩ | g4 | g5 | upright (hairpin) mount |
| 17 | R4A | 22kΩ | g6 | h4 | upright (hairpin) mount |
| 18 | R6A | 3.3kΩ | h5 | top GND rail @ row 5 |  |
| 19 | Jv1xA | yellow wire | h6 | c5 |  |
| 20 | Jv1hA | yellow wire | b5 | e8 |  |
| 21 | C1A | 10nF | d8 | bottom GND rail @ row 9 |  |
| 22 | RA | 1.8kΩ | c8 | e11 |  |
| 23 | C2A | 100nF | d11 | bottom GND rail @ row 11 |  |
| 24 | LA | 22mH | c11 | e13 | 22 mH; measure its DCR (= r0) |
| 25 | JlA | black wire | d13 | bottom GND rail @ row 13 | replace with r0 resistor to set γ = β·r0/R (FSOT preregistration) |
| 26 | Cd+B | 100nF | h17 | top GND rail @ row 18 | decoupling, pin 8 to GND |
| 27 | Cd-B | 100nF | c20 | bottom GND rail @ row 21 | decoupling, pin 4 to GND |
| 28 | R2B | 220Ω | d17 | d18 | upright (hairpin) mount |
| 29 | R1B | 220Ω | d19 | c17 | upright (hairpin) mount |
| 30 | R3B | 2.2kΩ | c18 | bottom GND rail @ row 18 |  |
| 31 | R5B | 22kΩ | g18 | g19 | upright (hairpin) mount |
| 32 | R4B | 22kΩ | g20 | h18 | upright (hairpin) mount |
| 33 | R6B | 3.3kΩ | h19 | top GND rail @ row 19 |  |
| 34 | Jv1xB | yellow wire | h20 | c19 |  |
| 35 | Jv1hB | yellow wire | b19 | e22 |  |
| 36 | C1B | 10nF | d22 | bottom GND rail @ row 22 |  |
| 37 | RB | 1.8kΩ | c22 | e25 |  |
| 38 | C2B | 100nF | d25 | bottom GND rail @ row 25 |  |
| 39 | LB | 22mH | c25 | e27 | 22 mH; measure its DCR (= r0) |
| 40 | JlB | black wire | d27 | bottom GND rail @ row 27 | replace with r0 resistor to set γ = β·r0/R (FSOT preregistration) |
| 41 | Cd+C | 100nF | h31 | top GND rail @ row 31 | decoupling, pin 8 to GND |
| 42 | Cd-C | 100nF | c34 | bottom GND rail @ row 35 | decoupling, pin 4 to GND |
| 43 | R2C | 220Ω | d31 | d32 | upright (hairpin) mount |
| 44 | R1C | 220Ω | d33 | c31 | upright (hairpin) mount |
| 45 | R3C | 2.2kΩ | c32 | bottom GND rail @ row 31 |  |
| 46 | R5C | 22kΩ | g32 | g33 | upright (hairpin) mount |
| 47 | R4C | 22kΩ | g34 | h32 | upright (hairpin) mount |
| 48 | R6C | 3.3kΩ | h33 | top GND rail @ row 33 |  |
| 49 | Jv1xC | yellow wire | h34 | c33 |  |
| 50 | Jv1hC | yellow wire | b33 | e36 |  |
| 51 | C1C | 10nF | d36 | bottom GND rail @ row 36 |  |
| 52 | RC | 1.8kΩ | c36 | e39 |  |
| 53 | C2C | 100nF | d39 | bottom GND rail @ row 39 |  |
| 54 | LC | 22mH | c39 | e41 | 22 mH; measure its DCR (= r0) |
| 55 | JlC | black wire | d41 | bottom GND rail @ row 41 | replace with r0 resistor to set γ = β·r0/R (FSOT preregistration) |
| 56 | JcA | green wire | b8 | f45 | A_V1 to coupling area |
| 57 | JcB | orange wire | b22 | f53 | B_V1 to coupling area |
| 58 | JcC | purple wire | b36 | f61 | C_V1 to coupling area |
| 59 | JcA' | green wire | g45 | e45 |  |
| 60 | JcC' | purple wire | g61 | e61 |  |
| 61 | RcAB_1 | 6.8kΩ | h45 | f49 | RcAB part 1 |
| 62 | RcAB_2 | 75Ω | g49 | g53 | RcAB part 2 |
| 63 | RcBC_1 | 6.8kΩ | h53 | f57 | RcBC part 1 |
| 64 | RcBC_2 | 75Ω | g57 | h61 | RcBC part 2 |
| 65 | RcCA_1 | 6.8kΩ | d61 | e53 | RcCA part 1 |
| 66 | RcCA_2 | 75Ω | d53 | d45 | RcCA part 2 |

## Test points (scope probe tip; ground clip on any GND rail hole)

| TP | Signal | Hole |
|---|---|---|
| TP1A | A_V1 = V_C1 (scope X / CH1) | a5 |
| TP2A | A_V2 = V_C2 (scope Y / CH2) | b11 |
| TP3A | UA pin 7 = inner op-amp out (should rail at ±7.67 V) | i4 |
| TP1B | B_V1 = V_C1 (scope X / CH1) | a19 |
| TP2B | B_V2 = V_C2 (scope Y / CH2) | b25 |
| TP3B | UB pin 7 = inner op-amp out (should rail at ±7.67 V) | i18 |
| TP1C | C_V1 = V_C1 (scope X / CH1) | a33 |
| TP2C | C_V2 = V_C2 (scope Y / CH2) | b39 |
| TP3C | UC pin 7 = inner op-amp out (should rail at ±7.67 V) | i32 |

Scope: X–Y mode with CH1 = TP1 (V_C1), CH2 = TP2 (V_C2) shows the double scroll; Y-T mode at 2 ms/div (×1 values) shows lobe switching ≈ ±4.3 V on V_C1.
