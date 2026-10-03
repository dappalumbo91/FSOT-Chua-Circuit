# Build checklist — single FSOT Kennedy–Chua node (TL082)

Board: standard 830-point (rows 1–63, holes a–e bottom / f–j top, centre gap between e and f).
Rails: top outer = **+9.19 V (red)**, top inner = **GND**, bottom inner = **GND**, bottom outer = **−9.19 V (blue)**.
If your board's rails are split in the middle (gap near row 30), bridge each rail across the gap with a short wire of the rail's colour.
Supply: two bench supplies in series (or ±9 V then trim): (+) of PS1 → top +V rail, PS1 (−)/PS2 (+) → GND rails, PS2 (−) → bottom −V rail.
**Before power-on**: set the rails so U2's saturated output reads 7.67 V (SPICE: ±9.19 V for TL082, ±9.66 V for 741 models). Bp1 = Esat·3.3/25.3 = 1.00 V.
Rail positions written '@ row N' mean the rail hole nearest row N — electrically any hole on that same rail is equivalent.
741 alternative (no TL082): use two 741s per node (U1 for R1/R2/R3, U2 for R4/R5/R6): 741 pin 3 = + (to V_C1), pin 2 = −, pin 6 = out, pin 7 = +V, pin 4 = −V; this layout is for the TL082 (one chip per node, matching the repo BOM).
Hairpin = resistor stood upright with one lead bent back down (the two holes are only 1–2 rows apart).

| Step | Part | Value | Lead 1 | Lead 2 | Notes |
|---|---|---|---|---|---|
| 1 | UA | TL082 | pin 1 → e3, pin 2 → e4, pin 3 → e5, pin 4 → e6, pin 8 → f3, pin 7 → f4, pin 6 → f5, pin 5 → f6 | | notch/dot toward the left (lower row numbers); pin 1 bottom-left |
| 2 | JvccA | red wire | g3 | top +V rail (red) @ row 3 |  |
| 3 | JveeA | blue wire | d6 | bottom −V rail (blue) @ row 6 |  |
| 4 | Jgnd | black wire | top GND rail @ row 61 | bottom GND rail @ row 61 | ties top and bottom GND rails |
| 5 | Cd+A | 100nF | h3 | top GND rail @ row 4 | decoupling, pin 8 to GND |
| 6 | Cd-A | 100nF | c6 | bottom GND rail @ row 7 | decoupling, pin 4 to GND |
| 7 | R2A | 220Ω | d3 | d4 | upright (hairpin) mount |
| 8 | R1A | 220Ω | d5 | c3 | upright (hairpin) mount |
| 9 | R3A | 2.2kΩ | c4 | bottom GND rail @ row 4 |  |
| 10 | R5A | 22kΩ | g4 | g5 | upright (hairpin) mount |
| 11 | R4A | 22kΩ | g6 | h4 | upright (hairpin) mount |
| 12 | R6A | 3.3kΩ | h5 | top GND rail @ row 5 |  |
| 13 | Jv1xA | yellow wire | h6 | c5 |  |
| 14 | Jv1hA | yellow wire | b5 | e8 |  |
| 15 | C1A | 10nF | d8 | bottom GND rail @ row 9 |  |
| 16 | RA | 1.8kΩ | c8 | e11 |  |
| 17 | C2A | 100nF | d11 | bottom GND rail @ row 11 |  |
| 18 | LA | 22mH | c11 | e13 | 22 mH; measure its DCR (= r0) |
| 19 | JlA | black wire | d13 | bottom GND rail @ row 13 | replace with r0 resistor to set γ = β·r0/R (FSOT preregistration) |

## Test points (scope probe tip; ground clip on any GND rail hole)

| TP | Signal | Hole |
|---|---|---|
| TP1A | A_V1 = V_C1 (scope X / CH1) | a5 |
| TP2A | A_V2 = V_C2 (scope Y / CH2) | b11 |
| TP3A | UA pin 7 = inner op-amp out (should rail at ±7.67 V) | i4 |

Scope: X–Y mode with CH1 = TP1 (V_C1), CH2 = TP2 (V_C2) shows the double scroll; Y-T mode at 2 ms/div (×1 values) shows lobe switching ≈ ±4.3 V on V_C1.
