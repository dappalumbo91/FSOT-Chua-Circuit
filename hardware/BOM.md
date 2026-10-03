# Absolute parts list — FSOT 3-node Chua ring + ESP32

Build this on one breadboard in an afternoon. Dual ±9 V stays on the analog island. The ESP32 only ever sees 0–3.3 V.

Theory (pin AEB2AD, do not round this in the sim):

\[
\sigma_c=1.4897\Rightarrow R_c^{\ast}=\frac{\alpha R}{\sigma_c}=12.08\,\mathrm{k}\Omega\ (\text{lock threshold}),\qquad
\sigma=\varphi^2\Rightarrow R_c=\frac{10\times 1800}{\varphi^2}=6875.39\,\Omega\ (\text{robust lock})
\]

On the bench, three **20 kΩ pots** set with a DMM: **20 kΩ** (no lock), **6.88 kΩ** (lock), then step from 13 kΩ down to 11 kΩ to find the threshold (prediction 12.08 kΩ). 11.12 kΩ (\(\sigma=\varphi\)) should also lock, but it is only 8 % inside the threshold. The E-series rounding is hardware quantization, not a free parameter.

**Inductor Q is now a prediction.** FSOT 2.1 Branch L gives Q_L = 25.44 at 3.39 kHz (series loss r0 = 18.44 Ω) for the 22 mH part. Measure it (LCR meter at 3.4 kHz, or the ring-down of an L–100 nF tank) **before** the coupling test and record it. The threshold prediction assumes this loss.

## Buy list (one of everything unless noted)

### Microcontroller

| Qty | Part | Why it is here |
|----:|------|----------------|
| 1 | **ESP32-WROOM-32 DevKit V1** (30-pin, CP2102 USB-UART) | 12-bit ADC, 3.3 V logic, USB serial. Catalog `MCU_ESP32_WROOM32`. Onboard LED = GPIO 2. |

### Analog — per node × 3 (build three identical islands)

| Qty | Part | Role |
|----:|------|------|
| 3 | **22 mH** inductor, ≥ 20 mA (ferrite, Q ≈ 25 at 3.4 kHz predicted) | Chua `L`. With C2 sets audio-band \(f_{LC}\approx 3.4\,\mathrm{kHz}\). Its loss sets \(\gamma\) and therefore \(\sigma_c\). |
| 3 | **10 nF / 50 V** C0G or X7R | `C1` (fast capacitor). Catalog `C_10nF_X7R`. Sets \(\alpha=C_2/C_1=10\). |
| 3 | **100 nF / 50 V** X7R | `C2`. Catalog `C_100nF_X7R`. |
| 3 | **1.80 kΩ 1%** | Linear Chua `R`. 1.8 kΩ E96, or 1.78 kΩ + 20 Ω. |
| 3 | **220 Ω** | NIC inner pair R1, R2 (two per node → **6** total). PDF floor. |
| 3 | **2.2 kΩ** | NIC branch that sets inner slope with 3.3 kΩ. **Ga** comes from this. |
| 3 | **3.3 kΩ** | NIC R6: with R5 it sets the first breakpoint Bp1 = Esat·R6/(R5+R6) and the inner slope Ga. The middle slope is **Gb = 1/R4 − R2/(R1R3) = −9/22000 S** (the old text said −1/3.3 kΩ, which is wrong). |
| 6 | **22 kΩ** | NIC R4, R5 (two per node). PDF ceiling. |
| 3 | **TL082** or **TL072** dual JFET op-amp (DIP-8) | Negative resistor. Catalog fallback `U_LM358` works at 3 kHz; TL082 is the better analog part. **Needs ±9 V, not 3.3 V.** |
| 3 + 3 + 3 | **300 kΩ**, **100 kΩ**, **150 kΩ** 1% | ADC bias per node: 300 k series from V_C1, 100 k to 3V3, 150 k to GND → \(v=1.65+V_{C1}/6\). Keeps the outer-cycle escape (±7.35 V) inside 0–3.3 V so the LOCK amplitude check can see it. |
| 6 | **1N4148** | Clamp ADC node to 3V3 and GND. Catalog `D_1N4148`. |

### Coupling (the ring)

| Qty | Part | Role |
|----:|------|------|
| 3 | **20 kΩ potentiometer** (linear) | One between each pair of nodes (triangle). **20 kΩ** = unlocked test, **6.88 kΩ** = robust lock, sweep 13 → 11 kΩ for the threshold (12.08 kΩ predicted). |

### Power and ESP32 rails

| Qty | Part | Role |
|----:|------|------|
| 2 | **9 V battery** + snaps, or a dual ±9 V bench PSU | Analog rails only. Never into the ESP32. |
| 1 | USB cable for the DevKit | 5 V → onboard 3.3 V LDO (`PS_LDO_3V3` / AMS1117 on the DevKit). |
| 1 | **100 µF / 10 V** electrolytic | ESP32 3V3 bulk. Catalog `C_100uF_bulk_ESP`. |
| 3 | **100 nF** | Bypass at each op-amp V+ and at ESP32 3V3. Catalog `C_100nF_bypass_ESP`. |

### Breadboard kit

| Qty | Part | Role |
|----:|------|------|
| 1 | Full-size solderless breadboard (or 3 mini boards in a triangle) | One island per node. |
| 1 | Jumper wire set (M-M) | Signal, power, ADC taps. |
| 1 | Multimeter | Set the three pots; check 3.3 V; check no ±9 V on GPIO. |

Optional: 4-channel USB scope. Not required — the ESP32 *is* the logger.

## What each *function* is (why, not just the value)

| Function | Parts | FSOT reason |
|----------|-------|-------------|
| Linear tank | R, L, C1, C2 | Audio-band resonator so the 12-bit ADC can sample it. \(\alpha=C_2/C_1=10\) is a catalog ratio. |
| Negative resistor | TL082 + 220 Ω–22 kΩ NIC | Keeps the oscillator from dying. Slopes **Ga, Gb, Gc** (−1/1320, −9/22000, +101/22000 S) are *computed from these resistors*, not from Matsumoto’s fitted −1.143/−0.714. |
| Ring coupling | 3 × Rc | Identical nodes (every node degree 2). This is the object κ assumes. A chain was the 3% mistake. |
| Trit map | ±1 V breakpoints of the NIC | Negative sat = −1, inner = 0, positive sat = +1. |
| Bias + clamp | 300 k / 100 k / 150 k + 1N4148 | Double scroll ±4.33 V → 0.93–2.37 V; outer-cycle escape ±7.35 V → 0.43–2.88 V. Safe for GPIO 34/35/32 (input-only ADC1). |
| Observer | ESP32 | Bare-metal / MicroPython collapse to trits, UART `FSOT_RLC_*`. |

## Cost

PDF band **$50–$150**. Typical cart: DevKit ~$8, passives ~$20, three TL082 ~$5, two 9 V batteries ~$6, breadboard kit ~$15.
