# Bench build guide: FSOT Kennedy–Chua node and 3-node ring (staged, with a checkpoint after every stage)

This guide goes with `build_checklist_single_node.md` / `build_checklist_ring_sigma_phi2.md` (hole-by-hole placement) and
`breadboard_single_node.png` / `breadboard_ring_sigma_phi2.png`. **Don't go on to the next stage until the current checkpoint passes.**
Every expected number below comes from `chua_netlist.py` (the BOM) and the simulations in `refine/` and `error_budget/`.
Tolerances assume 1 % resistors, 1–2 % film capacitors, and a 4½-digit DMM.

## 0. Parts, tools and the one number you must hit (r0)
| ref | value | colour code, 4-band (5 %) | colour code, 5-band (1 %) | notes |
|---|---|---|---|---|
| R1, R2 | 220 Ω | red-red-brown-gold | red-red-black-black-brown | outer NIC (U1 = TL082 half A) |
| R3 | 2.2 kΩ | red-red-red-gold | red-red-black-brown-brown | |
| R4, R5 | 22 kΩ | red-red-orange-gold | red-red-black-red-brown | inner NIC (U2 = half B) |
| R6 | 3.3 kΩ | orange-orange-red-gold | orange-orange-black-brown-brown | |
| R | 1.8 kΩ | brown-grey-red-gold | brown-grey-black-brown-brown | the Chua "R" between C1 and C2 |
| C1 | 10 nF film (PP/PET), code 103 | – | – | |
| C2 | 100 nF film, code 104 | – | – | also 2 × 100 nF decoupling per chip (ceramic is fine) |
| L | 22 mH | – | – | **total series loss r0 must be 18.44 Ω ± 0.33 Ω** (see §0.2) |
| ring: Rc | 6.8 kΩ + 75 Ω in series (σ = φ²) | blue-grey-red / violet-green-black-gold | blue-grey-black-brown-brown / violet-green-black-gold-brown | 18.0 kΩ = brown-grey-orange (σ = 1), 11.13 kΩ = 10 kΩ + 1.13 kΩ (σ = φ) |
| U | TL082 (DIP-8), one chip per node | – | – | uA741 works but lowers σc by ≈ 0.19 (see §6) |
Tools: DMM, two-channel scope (X–Y mode), dual bench supply (or two supplies in series), an LCR meter if you have one, and a function generator for §0.2 method B.

**Most common resistor misreads:** 220 Ω vs 22 kΩ (the 3rd band is brown vs orange), 2.2 kΩ vs 22 kΩ (red vs orange), 1.8 kΩ vs 18 kΩ (red vs orange).
**Measure every resistor with the DMM before you insert it.** Out of circuit it should read within ±1 % (5-band) or ±5 % (4-band).

### 0.1 Component acceptance (the FSOT tolerance spec, LOCK B `3594a469…`)
For the ±0.05 falsification window on σc to mean anything, the parts must be within:
L ±1.2 %, C1 ±1.0 %, R ±1.0 %, C2 ±4.5 %, r0 ±0.33 Ω, and node-to-node matching of C1, C2 and L within ≤ 1 % in the ring.
Measure L, C1 and C2 on an LCR meter at 1 kHz and write the values down. Sort parts into matched triples for the ring.
Sensitivities (Δσc per +1 % deviation, from the MC regression): L +0.021, C1 −0.024, R −0.024, C2 +0.006; r0: −0.075 per Ω.

### 0.2 Getting r0 = 18.44 Ω (inductor DCR + added series resistance)
r0 is the **total series loss of the inductor branch at the oscillation frequency** (≈ 2.5–3.4 kHz): coil DCR, plus AC/core loss, plus any series resistor.
In the build it sits between the inductor's cold end and GND (the "JlA" jumper position in the checklist: replace the jumper with the resistor).
- **Common radial 22 mH chokes are too lossy.** Datasheet DCR: Würth 7447720223 43.2 Ω typ / 55 Ω max; Bourns RLB0913-223K 45.6/56 Ω;
  Sumida RCH895NP-223K 44.9 Ω max; Murata 12LRS226C 70 Ω max; Murata 22R226C 82.5 Ω max. Above ≈ 40 Ω the standard model
  loses the double scroll altogether (periodic from 40 to 48 Ω, equilibrium from 50 Ω up), so **none of these can be used as-is,** and you can't
  *remove* resistance with a series part.
- **Route 1 (recommended): low-DCR 22 mH + series resistor.** Use a low-DCR 22 mH coil (for example Solen air-core S1222.0, 22.0 mH,
  0.99 Ω DCR per the Solen product page; any toroid or pot-core coil wound to 22 mH with DCR < 15 Ω also works). Then add
  R_add = 18.44 Ω − r_coil. Example: r_coil = 0.99 Ω → R_add = 17.45 Ω, built as 15 Ω + 2.4 Ω (1 % metal film, 17.4 Ω) plus a
  0.1 Ω trim, or as 17.4 Ω E96 alone (error −0.05 Ω, inside the ±0.33 Ω spec). Keep air-core coils ≥ 30 cm apart and away from the
  transformer of the supply (they pick up hum and couple to each other).
- **Route 2: series lower-L coils.** L adds and DCR adds, so pick parts whose DCR sum is below 18.44 Ω and pad the rest with a resistor.
  Check the datasheet sum first: for example RCH895NP-103K (10 mH, 22.0 Ω max) + RCH895NP-123K (12 mH, 25.0 Ω max) = 22 mH but 47 Ω, which is too high.
  Mount series coils at right angles to each other (mutual coupling changes L).
- **Route 3: synthetic inductor (gyrator).** An op-amp gyrator 22 mH whose series loss is a real resistor you set to 18.44 Ω
  (inductorless Chua circuits are established in the literature, e.g. Torres & Aguirre 2000). Its exact r0 is set by a resistor, but it adds two more op-amp poles.
- **Measuring r0 (do both):**
  A. DCR: DMM 4-wire (or 2-wire minus the lead resistance) across coil + R_add → **18.44 ± 0.33 Ω**.
     Copper changes by +0.39 %/K, so measure at the temperature the circuit will run at. With Route 1, almost all of r0 is a 50 ppm/K film resistor.
  B. Effective AC loss (this is what the dynamics actually see): build the tank L (+R_add) ‖ C2 = 100 nF alone, with no op-amp, no R and no C1.
     Drive it from a 50 Hz square wave through 100 kΩ and watch V_C2 on the scope. Expected ringing at f0 = 1/(2π√(L·C2)) = **3393 Hz**.
     The envelope decays with τ_env = 1/(r0/2L + 1/(2·Rs·C2)), Rs = 100 kΩ. For r0 = 18.44 Ω: **τ_env = 2.13 ms** (2.386 ms with the source correction removed).
     That corresponds to Q_L = ωL/r0 = **25.4**. If you measure τ_env < 1.9 ms, core loss is adding resistance; reduce R_add until τ_env = 2.13 ms.
     (Branch L′, r0 = 26.07 Ω, would give τ_env 1.56 ms (1.688 ms corrected), Q_L 18.0. This is the bench test that separates L from L′; see refine/REFINE_REPORT.md, Target 4.)

## 1. Stage 1: rails and ground (no parts other than wires and decoupling)
1. Place the jumpers: top GND rail ↔ bottom GND rail. If your board's rails are split at the middle, bridge them.
2. Connect the supplies: PS1(+) → top red rail; PS1(−) and PS2(+) → both GND rails; PS2(−) → bottom blue rail. **The supplies must be split.**
   A single 18 V supply with no ground midpoint won't work.
3. **Checkpoint 1 (no chip yet):**
| measure (DMM black on GND) | expected |
|---|---|
| top red rail | +9.19 V ± 0.05 V |
| bottom blue rail | −9.19 V ± 0.05 V |
| red ↔ blue | 18.38 V ± 0.1 V |
| GND rail top ↔ GND rail bottom (Ω, power off) | < 0.5 Ω |
Fine trim comes in Stage 2: the inner op-amp's saturated output must read **±7.67 V**, because that sets the breakpoint Bp1 = 1.00 V.

## 2. Stage 2: op-amp and NIC (negative resistor) only; no C1, R, C2 or L yet
Insert the TL082 (notch to the left; pin 1 bottom-left), its two 100 nF decoupling capacitors (pin 8 → GND, pin 4 → GND), and R1–R6 plus the two yellow V1 jumpers, exactly as in the checklist.
Name the nodes: V1 = pins 3 and 5 (the C1 node), O1 = pin 1, N1 = pin 2, O2 = pin 7, N2 = pin 6.
**Checkpoint 2a (power on, V1 jumpered to GND):**
| point | expected |
|---|---|
| supply current per chip (+ rail) | 2.8 mA typ, ≤ 5.6 mA (TI TL082: 1.4 mA typ / 2.5 mA max per amplifier) |
| pin 8 / pin 4 | +9.19 / −9.19 V |
| O1 (pin 1) | 0 V ± 30 mV (input offset × 1.1) |
| O2 (pin 7) | 0 V ± 0.1 V (offset × 7.67) |
**Checkpoint 2b: drive V1 from a *stiff* source** (bench supply channel or a 1.5 V cell; a resistor divider is NOT stiff enough, because the NIC's
negative conductance −0.758 mS will pull it away). Replace the V1–GND jumper with the source and put the DMM in series in mA mode:
| V1 | O1 (pin 1) | O2 (pin 7) | current into V1 from the source |
|---|---|---|---|
| +0.500 V | +0.550 V ± 0.01 | +3.83 V ± 0.08 | −0.379 mA ± 3 % (the current flows *out of* the NIC: negative resistance) |
| −0.500 V | −0.550 V | −3.83 V | +0.379 mA |
| +1.500 V | +1.650 V ± 0.02 | **+7.67 V** (railed; trim both supplies symmetrically until it reads 7.67 V ± 0.03) | −0.962 mA ± 3 % |
| −1.500 V | −1.650 V | **−7.67 V** | +0.962 mA |
Gains are G1 = 1 + R2/R3 = 1.100 and G2 = 1 + R5/R6 = 7.667. Inner slope Ga = −0.758 mS; outer slope Gb = −0.409 mS; breakpoint 1.00 V.
If the current sign comes out positive at +0.5 V (behaving like a normal resistor), the feedback goes to the wrong input; see §5.

## 3. Stage 3: passive network (no oscillation yet)
Power off. Remove the V1 source. Insert C1 (V1 → GND), R (V1 → V2), C2 (V2 → GND), L (V2 → cold end), and r0/R_add (cold end → GND).
**Checkpoint 3 (power off, DMM Ω):**
| between | expected |
|---|---|
| V2 ↔ GND | r_coil + R_add = 18.44 Ω ± 0.33 (the DC path through L) |
| V1 ↔ V2 | ≈ 1.05 kΩ in circuit (1.8 kΩ ‖ the NIC strings via GND; R alone out of circuit: 1.80 kΩ ± 1 %) |
| V1 ↔ GND | ≈ 1.0–1.1 kΩ (R + r0 = 1.82 kΩ ‖ R1+R2+R3 = 2.64 kΩ ‖ R4+R5+R6 = 47.3 kΩ; unpowered chip may shift it slightly) |
| C1, C2 out of circuit | 10.0 nF ± 1 %, 100 nF ± 4.5 % |

## 4. Stage 4: single node, power on (chaos check)
**Checkpoint 4 (scope, 10× probes, ground clip on a GND rail):**
| observable | expected, ideal op-amp | expected with TL082 (rf 5-dim model) | pass band |
|---|---|---|---|
| V_C1 peak (TP1, pin 3) | ±4.33 V | ±4.28 V | 4.1–4.45 V |
| V_C1 local maxima band | 2.4–4.3 V (bifurcation plot) | same | |
| V_C1 true-RMS (DMM AC) | 2.53 V | – | 2.3–2.8 V |
| V_C1 DC mean (DMM DC) | ≈ 0 V (wanders ±0.3 V) | same | |
| V_C2 peak (TP2) | ±0.84 V | – | 0.75–0.95 V |
| i_L peak | 3.5 mA | – | well below any coil's rating |
| dominant spectral line (scope FFT of V_C1) | 2.56–2.58 kHz | 2.60 kHz | ± 3 % |
| lobe-switching rate (jumps of V_C1 from the > +1 V lobe to the < −1 V lobe or back, per s) | 526 /s | ≈ 500 /s | ± 15 % |
| O2 (pin 7) | railed at ±7.67 V for 94 % of the time | same | |
| X–Y (CH1 V_C1, CH2 V_C2) | double scroll | | |
If you see a single scroll, a limit cycle, or a dot instead, use §5. The *nominal* design is chaotic: λ1 = 0.26/τ0 = 1450 /s.
Narrow periodic windows exist at r0 = 18.208–18.211 Ω and 18.660–18.661 Ω (width ≤ 0.004 Ω), and a wide one at 16.98–17.26 Ω
(see refine/png/t3_lyap_bif_fine_16p5_19p5.png). If you land in a window, a 0.1 Ω change in R_add (or 1 K of coil temperature) moves you out of it.

## 5. Troubleshooting
| symptom | likely cause | check / fix |
|---|---|---|
| nothing anywhere, chip cold | rails not connected, or the split GND rail isn't bridged | Checkpoint 1; bridge rails at mid-board |
| chip hot, rails sag | TL082 inserted backwards (pin 4 ↔ pin 8 reversed) | notch to the left; pin 8 = +9.19 V; replace the chip if it got hot |
| both outputs stuck at a rail at power-on with V1 grounded | + and − inputs swapped (pins 2↔3 or 5↔6 crossed); the NIC becomes a positive-feedback latch | pin 3 and pin 5 go to V1; pins 2 and 6 go to the R2/R3 and R5/R6 junctions |
| Checkpoint 2b current has the wrong sign | feedback resistors swapped (R1↔R3 or R4↔R6) | R1, R4 from V1 to output; R2, R5 output → −input; R3, R6 −input → GND |
| O2 rails at ±8.x V instead of 7.67 V | rails too high | trim symmetrically until 7.67 V (rail-to-output drop is chip-specific) |
| O2 gain 0.1× or 10× off | 22 kΩ ↔ 2.2 kΩ, or 3.3 kΩ ↔ 33 kΩ swapped (band 3 colour) | measure each resistor; red-red-orange = 22 k, red-red-red = 2.2 k |
| oscillation is a clean sine, ~2.5–3.4 kHz, ±4 V or smaller | r0 too high (lossy inductor, e.g. a 43–82 Ω choke) or R too high | Checkpoint 3: V2↔GND must be 18.4 Ω; see §0.2 |
| no oscillation, V_C1 sits at ≈ ±2.5 V or 0 | r0 ≥ 50 Ω, missing ground on the L cold end, or C2 open | check the cold-end connection and r0 |
| single scroll (one lobe only) | R slightly high, or r0 a bit high | try R = 1.75 kΩ, or lower r0 toward 18.4 Ω |
| periodic double loop | r0 in a periodic window (16.98–17.26 Ω, or narrow at 18.21/18.66 Ω) | change R_add by 0.1–0.3 Ω |
| large hum at 50/60 Hz | missing ground on the scope or the board; air-core coil near a transformer | ground clip on the GND rail; move the coil |
| ring won't lock at σ = φ² | node mismatch > 1 %; Rc wired to V2 instead of V1; one node not chaotic on its own | pass Checkpoint 4 per node; Rc goes between the V1 nodes (pins 3/5) |
| works with 741 but σc shifted down by ≈ 0.2 | 741 GBW 1 MHz / slew 0.5 V/µs | expected: rf model gives σc 1.304 vs 1.497 ideal (see §6) |

## 6. Stage 5: three-node ring
1. Build nodes B and C exactly like A. Each node must pass Checkpoint 4 **on its own** (coupling wires removed). The three V_C1 spectra should agree within 2 %.
2. Matching: the three C1 within 1 %, the three C2 within 1 %, and the three L within 1 % of each other (the MC gives +0.106 on σc at 5–10 % mismatch).
3. Fit the coupling resistors between the V1 nodes (ring A–B, B–C, C–A). σ = α·R/Rc = 18 000 Ω / Rc.
**Checkpoint 5 (scope X–Y: CH1 = V_C1A, CH2 = V_C1B):**
| Rc | σ | expected | |
|---|---|---|---|
| open | 0 | three independent double scrolls; X–Y is a filled square | |
| 18.0 kΩ | 1.000 | no sync (filled blob) | |
| 12.5 kΩ | 1.440 | no lock (sim: 0/24 seeds lock with ideal op-amps at Branch L) | |
| 12.04 kΩ | 1.4954 | threshold: σ50, 50 % of starts lock (ideal op-amps) | |
| ≈ 12.2 kΩ | ≈ 1.478 | threshold predicted with TL082 (rf MSF; see refine report) | |
| 11.13 kΩ | φ = 1.618 | lock: X–Y collapses to a thin diagonal line | |
| 6.875 kΩ | φ² = 2.618 | lock (the FSOT design point) | |
"Lock" means |V_A − V_B| < 0.15 × |V_A| sustained, with all nodes still chaotic at ±4.3 V. A ring that collapses to a fixed point or rails at ±7.35 V is **not** locked.
Op-amp effect on the threshold: TL082 −0.019 (3 MHz datasheet GBW) to −0.040 (TL08xH); uA741 −0.19. Parasitic capacitance −0.002.

## 7. What to record (for the FSOT test)
r0 (DCR and τ_env), L, C1, C2, R per node; supply rails; O2 rail voltage; V_C1 peak, RMS, spectral peak and lobe rate per node;
and the lock fraction vs Rc over 10 power-cycles per Rc (σ = 1.40 to 1.60 in 0.02 steps). Branch L predicts the threshold at Rc ≈ 12.0–12.2 kΩ;
Branch L′ (r0 = 26.07 Ω) predicts locking already at Rc = 13.3 kΩ (σ = 1.353).
