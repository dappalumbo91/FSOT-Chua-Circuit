# Build checklist: FSOT minimal chaotic circuit (TL074, 830-point breadboard)

Rails: top outer **+9 V (red)**, top inner GND, bottom inner GND, bottom outer **-9 V (blue)**. '+T@13' = top red rail hole at row 13.

| Step | Part | Value | Lead 1 | Lead 2 | Notes |
|---|---|---|---|---|---|
| 1 | U1 | TL074 (14-pin) | e10..e16 / f10..f16 |  | notch LEFT; pin 1 = e10 (bottom-left), pin 14 = f10 |
| 2 | J+ | red wire | a13 | +T@13 | pin 4 V+ -> +9 V rail |
| 3 | J- | blue wire | j13 | -B@13 | pin 11 V- -> -9 V rail |
| 4 | Jg | black wire | GT@60 | GB@60 | tie the two GND rails |
| 5 | Cd+ | 100 nF | +T@12 | GT@12 | decoupling |
| 6 | Cd- | 100 nF | -B@14 | GB@14 | decoupling |
| 7 | Jg3 | black wire | d12 | GB@12 | pin 3 IN1+ -> GND |
| 8 | Jg5 | black wire | d14 | GB@15 | pin 5 IN2+ -> GND |
| 9 | Jg12 | black wire | g12 | GT@11 | pin 12 IN4+ -> GND |
| 10 | Jg10 | black wire | g14 | GT@15 | pin 10 IN3+ -> GND |
| 11 | C1 | 100 nF | a10 | a11 | U1 integrator cap (o1-n1) |
| 12 | RA | 3160 ohm | b10 | b11 | THE KNOB: 2.7k + 1k trimmer |
| 13 | Jn1 | yellow wire | c11 | a5 | extends node n1 to row 5 |
| 14 | Rc | 40.2 k | b5 | +T@5 | constant: 9 V * 1.8k/40.2k = 0.403 V |
| 15 | Rx | 1.8 k | c5 | j18 | x feedback (o3 -> n1), via o3 extension row 18 |
| 16 | Rw | 1.8 k | d5 | j10 | o4 -> n1 |
| 17 | R2 | 1.8 k | c10 | b15 | o1 -> n2 |
| 18 | C2 | 100 nF | a15 | a16 | U2 integrator cap |
| 19 | R3 | 1.8 k | b16 | g15 | o2 -> n3 (crosses the gap) |
| 20 | C3 | 100 nF | h15 | h16 | U3 integrator cap |
| 21 | R4 | 1.8 k | c16 | g11 | o2 -> n4 (crosses the gap) |
| 22 | Rf | 1.8 k | h10 | h11 | U4 feedback |
| 23 | Jx | green wire | i16 | f18 | o3 = x -> row 18 (x test point) |
| 24 | D1 | 1N4148 | g18 | g22 | anode (no band) row 18, cathode (black band) row 22 |
| 25 | Rd | 900 ohm (2 x 1.8k in parallel, or 909 E96) | h22 | i11 | dn -> n4 |

| Test point | hole |
|---|---|
| TP_x (V_o3, scope CH1) | j16 |
| TP_x' (V_o2 = -tau0 x', CH2) | d16 |
| TP_x'' (V_o1) | d10 |
| TP_w (V_o4) | i10 |
