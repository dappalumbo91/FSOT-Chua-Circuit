# Build checklist: FSOT Path J circuit (TL074 + TL072, 830-point breadboard)

Rails: top outer **+9 V (red)**, top inner GND, bottom inner GND, bottom outer **-9 V (blue)**. '+T@13' = top red rail hole at row 13.

| Step | Part | Value | Hole 1 | Hole 2 | Note |
|---|---|---|---|---|---|
| 1 | U1 | TL074 (14-pin) | e10..e16 / f10..f16 |  | notch LEFT; pin 1 = e10, pin 7 = e16, pin 8 = f16, pin 14 = f10 |
| 2 | U5 | TL072 (8-pin) | e22..e25 / f22..f25 |  | notch LEFT; pin 1 = e22, pin 4 = e25, pin 5 = f25, pin 8 = f22 |
| 3 | J+ | red wire | a13 | +T@13 | TL074 pin 4 V+ -> +9 V |
| 4 | J- | blue wire | j13 | -B@13 | TL074 pin 11 V- -> -9 V |
| 5 | J2+ | red wire | j22 | +T@22 | TL072 pin 8 V+ -> +9 V |
| 6 | J2- | blue wire | a25 | -B@25 | TL072 pin 4 V- -> -9 V |
| 7 | Jg | black wire | GT@30 | GB@30 | tie the two GND rails at the right end |
| 8 | Cd1+ | 100 nF | +T@12 | GT@12 | decoupling TL074 |
| 9 | Cd1- | 100 nF | -B@14 | GB@14 | decoupling TL074 |
| 10 | Cd2+ | 100 nF | +T@21 | GT@21 | decoupling TL072 |
| 11 | Cd2- | 100 nF | -B@26 | GB@26 | decoupling TL072 |
| 12 | Jg3 | black wire | d12 | GB@12 | TL074 pin 3 IN1+ -> GND |
| 13 | Jg5 | black wire | d14 | GB@15 | TL074 pin 5 IN2+ -> GND |
| 14 | Jg12 | black wire | g12 | GT@11 | TL074 pin 12 IN4+ -> GND |
| 15 | Jg10 | black wire | g14 | GT@15 | TL074 pin 10 IN3+ -> GND |
| 16 | Jg24 | black wire | b24 | GB@24 | TL072 pin 3 IN1+ -> GND |
| 17 | Jg25 | black wire | j25 | GT@25 | TL072 pin 5 IN2+ -> GND (unused half) |
| 18 | J67 | short wire | g24 | g23 | TL072 pin 6 -> pin 7 (unused half as grounded follower) |
| 19 | C1 | 100 nF film | a10 | a11 | U1 integrator cap (o1-n1) |
| 20 | RA | 4.22 k (R/gamma_rel) | b10 | b11 | x'' gain gamma_rel |
| 21 | Jn1 | yellow wire | c11 | a5 | extends node n1 to row 5 |
| 22 | Rc | 40.2 k | b5 | +T@5 | constant: 9 V x 1.8k/40.2k = 0.403 V (= U) |
| 23 | Rx | 2.43 k (R/G, G = kappa/gamma_rel) | c5 | j18 | x term (o3 -> n1) |
| 24 | Rw | 1.96 k (R/B, B = Theta) | d5 | j10 | x' term (o4 -> n1) |
| 25 | Rr | 1.21 k (R/2G) | e5 | e6 | rectifier term (r -> n1); row 6 = node r |
| 26 | Jr | white wire | a6 | a27 | node r: row 6 <-> row 27 |
| 27 | R2 | 1.8 k | c10 | b15 | o1 -> n2 |
| 28 | C2 | 100 nF film | a15 | a16 | U2 integrator cap |
| 29 | R3 | 1.8 k | b16 | g15 | o2 -> n3 (crosses the gap) |
| 30 | C3 | 100 nF film | h15 | h16 | U3 integrator cap |
| 31 | R4 | 1.8 k | c16 | g11 | o2 -> n4 (crosses the gap) |
| 32 | Rf | 1.8 k | h10 | h11 | U4 feedback: o4 = -o2 |
| 33 | Jx | green wire | i16 | f18 | o3 = x -> row 18 (x test point) |
| 34 | R5 | 1.8 k | g18 | b23 | o3 -> n5 (rectifier input) |
| 35 | Rf5 | 1.8 k | c23 | c27 | n5 -> r (rectifier feedback) |
| 36 | Da | 1N4148 | d22 | d23 | anode u5 (row 22), cathode/band n5 (row 23) |
| 37 | Db | 1N4148 | b27 | b22 | anode r (row 27), cathode/band u5 (row 22) |

| Test point | hole |
|---|---|
| TP_x (V_o3, CH1) | h18 |
| TP_x' (V_o2 = -U x', CH2) | d16 |
| TP_x'' (V_o1) | d10 |
| TP_w (V_o4) | i10 |
| TP_r | d27 |
