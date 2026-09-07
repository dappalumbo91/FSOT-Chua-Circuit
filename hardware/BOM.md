# Absolute parts list — FSOT 3-node Chua ring + ESP32

Build this on one breadboard in an afternoon. Dual ±9 V stays on the analog island. The ESP32 only ever sees 0–3.3 V.

Theory operating point (do not round this in the sim):

\[
\sigma=\varphi,\qquad R_c=\frac{\alpha R}{\varphi}=\frac{10\times 1800}{\varphi}=11124.61\,\Omega
\]

On the bench, three **20 kΩ pots** set with a DMM to **11.12 kΩ** (or 10.0 kΩ + 1.13 kΩ 1%). The E-series rounding is hardware quantization, not a free parameter.

## Buy list (one of everything unless noted)

### Microcontroller

| Qty | Part | Why it is here |
|----:|------|----------------|
| 1 | **ESP32-WROOM-32 DevKit V1** (30-pin, CP2102 USB-UART) | 12-bit ADC, 3.3 V logic, USB serial. Catalog `MCU_ESP32_WROOM32`. Onboard LED = GPIO 2. |

### Analog — per node × 3 (build three identical islands)

| Qty | Part | Role |
|----:|------|------|
| 3 | **22 mH** inductor, ≥ 20 mA | Chua `L`. With C2 sets audio-band \(f_{LC}\approx 3.4\,\mathrm{kHz}\). |
| 3 | **10 nF / 50 V** C0G or X7R | `C1` (fast capacitor). Catalog `C_10nF_X7R`. Sets \(\alpha=C_2/C_1=10\). |
| 3 | **100 nF / 50 V** X7R | `C2`. Catalog `C_100nF_X7R`. |
| 3 | **1.80 kΩ 1%** | Linear Chua `R`. 1.8 kΩ E96, or 1.78 kΩ + 20 Ω. |
| 3 | **220 Ω** | NIC inner pair R1, R2 (two per node → **6** total). PDF floor. |
| 3 | **2.2 kΩ** | NIC branch that sets inner slope with 3.3 kΩ. **Ga** comes from this. |
| 3 | **3.3 kΩ** | NIC branch that remains in the outer slope. **Gb = −1/3.3 kΩ**. |
| 6 | **22 kΩ** | NIC R4, R5 (two per node). PDF ceiling. |
| 3 | **TL082** or **TL072** dual JFET op-amp (DIP-8) | Negative resistor. Catalog fallback `U_LM358` works at 3 kHz; TL082 is the better analog part. **Needs ±9 V, not 3.3 V.** |
| 6 | **100 kΩ 1%** | Bias divider to 1.65 V (two per node). Catalog `R_100k_1pct`. |
| 6 | **1N4148** | Clamp ADC node to 3V3 and GND. Catalog `D_1N4148`. |

### Coupling (the ring)

| Qty | Part | Role |
|----:|------|------|
| 3 | **20 kΩ potentiometer** (linear) | One between each pair of nodes (triangle). Set to **11.12 kΩ** for the lock test, **20 kΩ** for the unlocked test. |

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
| 1 | Multimeter | Set the three pots to 11.12 kΩ; check 3.3 V; check no ±9 V on GPIO. |

Optional: 4-channel USB scope. Not required — the ESP32 *is* the logger.

## What each *function* is (why, not just the value)

| Function | Parts | FSOT reason |
|----------|-------|-------------|
| Linear tank | R, L, C1, C2 | Audio-band resonator so the 12-bit ADC can sample it. \(\alpha=C_2/C_1=10\) is a catalog ratio. |
| Negative resistor | TL082 + 220 Ω–22 kΩ NIC | Keeps the oscillator from dying. Inner/outer slopes **Ga, Gb** are *computed from these resistors*, not from Matsumoto’s fitted −1.143/−0.714. |
| Ring coupling | 3 × Rc | Identical nodes (every node degree 2). This is the object κ assumes. A chain was the 3% mistake. |
| Trit map | ±1 V breakpoints of the NIC | Negative sat = −1, inner = 0, positive sat = +1. |
| Bias + clamp | 100 kΩ + 100 kΩ + 1N4148 | ±2 V Chua swing → 0.65–2.65 V, safe for GPIO 34/35/32 (input-only ADC1). |
| Observer | ESP32 | Bare-metal / MicroPython collapse to trits, UART `FSOT_RLC_*`. |

## Cost

PDF band **$50–$150**. Typical cart: DevKit ~$8, passives ~$20, three TL082 ~$5, two 9 V batteries ~$6, breadboard kit ~$15.
