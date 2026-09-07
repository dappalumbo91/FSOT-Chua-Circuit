# Build tutorial — prove FSOT lock on a breadboard

This is the afternoon experiment. You are not tuning a neural net. You are building three identical analog oscillators, tying them in a **triangle**, and checking two pot settings against the golden ratio.

Pin **D1D38A**. Zero free parameters. If it fails, you used the wrong object — you do not add a coefficient.

![Bench overview](images/bench_triangle_overview.jpg)

*Layout idea: three analog islands in a loop, ESP32 as the logger, 9 V batteries off to the analog side. The photo is a mood board (it shows extra trimmers). Your BOM uses **three** coupling pots.*

---

## 0. Why this circuit exists

FSOT trits are \((-1,0,+1)\). A Chua oscillator’s voltage already lives in three regions:

| Voltage at \(V_{C1}\) | Trit | Name |
|-----------------------|------|------|
| \(< -1\,\mathrm{V}\) | \(-1\) | inhibition / damping |
| \(\lvert V\rvert\le 1\,\mathrm{V}\) | \(0\) | quiescent / inner |
| \(> +1\,\mathrm{V}\) | \(+1\) | excitation / emergence |

The ESP32 12-bit ADC is the observer. Coupling is the T³ / \(\kappa\) interaction: when three **identical** nodes share a closed loop, they lock at the Layer-0 fold \(\varphi\).

\[
\sigma=\varphi,\qquad R_c=\frac{\alpha R}{\varphi}=\frac{10\times 1800}{\varphi}=11124.61\,\Omega
\]

Set the three pots there. That is the prediction.

---

## 1. What the 3% taught us (do not skip)

The first sim used:

1. A **chain** A—B—C (ends are not the same as the middle).
2. Literature Chua slopes \(a,b=-1.143,-0.714\) (those are **fits**).
3. An invented lock cut `0.85`.
4. Then \(\alpha/\varphi\) picked because it was close.

That is the opposite of the theory. The remedy:

| Must be | Is |
|---------|----|
| Identical nodes | **Ring / triangle**, degree 2 each |
| Slopes from parts | Kennedy NIC **2.2 kΩ ∥ 3.3 kΩ** → \(G_a,G_b\) |
| Seed-closed lock | trit \(\ge\varphi^{-1}\), MAD/amp \(\le\varphi^{-4}\) |
| Operating point named first | \(\sigma=\varphi\) |

After that, 6/6 random initial conditions lock at \(\varphi\) and none lock at \(\sigma=1\). BOM catalog residual at Electromagnetism is **0.0208%**.

---

## 2. Parts (absolute)

Full buy list with function: [`../hardware/BOM.md`](../hardware/BOM.md).

**You cannot skip:**

- 3 × TL082 (or TL072) dual op-amps — they **need ±9 V**
- 3 × 22 mH, 10 nF, 100 nF, 1.80 kΩ
- NIC resistors per node: 2×220 Ω, 2.2 kΩ, 2×22 kΩ, 3.3 kΩ
- 3 × 20 kΩ pots (the triangle)
- 6 × 100 kΩ + 6 × 1N4148 (ESP32 safety)
- 1 × ESP32-WROOM-32 DevKit V1
- 2 × 9 V batteries (analog only)

![One analog node](images/chua_node_macro.jpg)

*One island: op-amp, inductor, capacitors, resistor cluster, two 100 kΩ resistors toward the ADC jumper.*

---

## 3. Where things go

Pin-accurate notes: [`../hardware/schematic.md`](../hardware/schematic.md).

### Power (two islands)

| Island | Source | Touches |
|--------|--------|---------|
| Analog | ±9 V batteries | All three TL082 V+ / V−, analog GND |
| Digital | USB 5 V → DevKit 3.3 V | ESP32 only |
| Star ground | **one** jumper | Analog GND hole ↔ ESP32 GND |

If a 9 V lead hits GPIO 34, that pad is dead. Leave empty breadboard rows between the batteries and the DevKit.

### ESP32 DevKit V1 (USB facing you)

![ESP32 ADC wires](images/esp32_devkit_adc_wires.jpg)

**Left header** (the ADC side on a 30-pin DOIT board):

| Node | Pin | Function |
|------|-----|----------|
| A \(V_{C1}\) after bias | **GPIO 34** | ADC1_CH6, **input only** |
| B | **GPIO 35** | ADC1_CH7, input only |
| C | **GPIO 32** | ADC1_CH4 |
| Ground | **GND** (beside VIN) | Star point |
| LED (do not wire) | GPIO 2 | Onboard, firmware lock lamp |

GPIO 34 and 35 **cannot** be outputs. They have no internal pull-ups. That is why they are the right ADC pins.

### Triangle coupling

```
A ---- pot AB (11.12 kΩ) ---- B
 \                           /
  \                         /
   pot CA                 pot BC
    \                     /
     \                   /
      -------- C --------
```

Each pot sits between two `VC1` nodes, **before** the 100 kΩ bias network.

### Bias (per node, the only ESP32 interface)

```
VC1 -- 100k --+-- GPIO
              |
             100k to GND
              |
             100k to 3V3
              + 1N4148 to 3V3
              + 1N4148 to GND
```

Map: \(v_{\mathrm{ADC}}=1.65+0.5\,V_{C1}\). A ±2 V swing stays inside 0.65–2.65 V.

---

## 4. Build order (do not power analog first)

1. Seat the three TL082s. Wire ±9 V **but do not connect batteries yet**.
2. Build node A tank: R, L, C1, C2, NIC resistors. Repeat B, C. Keep the three islands copies of each other.
3. Wire the three pots into a triangle on the three `VC1` nets.
4. Wire the three bias networks. Check with a DMM that each ADC node is ~1.65 V with analog power still **off** (only USB 3.3 V).
5. USB-power the ESP32. Flash firmware (`firmware/README.md`). Confirm `FSOT_RLC_HARDWARE_BOOT=ok`.
6. **Then** connect 9 V batteries. If the DevKit resets or smells, disconnect immediately — a clamp or bias is wrong.
7. DMM the three pots to **11.12 kΩ**. Watch UART.

---

## 5. The two tests that prove the model

| Test | All three pots | Must happen |
|------|----------------|-------------|
| Unlocked | 20 kΩ (\(\sigma\approx 0.9<\varphi\)) | `FSOT_RLC_LOCK=0`, trits mix, LED blinks |
| Locked | **11.12 kΩ** (\(\sigma=\varphi\)) | `FSOT_RLC_LOCK=1`, three trits equal |

If unlocked looks locked, you have a ground loop or the pots are not actually 20 kΩ. If locked never happens, the three nodes are not copies (wrong R or C on one island) or analog rails are collapsing.

You do **not** turn a pot until a 3% residual goes away. The prediction is the 11.12 kΩ setting.

---

## 6. What the firmware is doing

Same collapse as the Lean ESP32 observer: \(\Theta=C_{\mathrm{eff}}P_{\mathrm{var}}\). Voltage trits use the Chua breakpoints \(\pm 1\,\mathrm{V}\). Frames:

```
FSOT_RLC_NODE|i|adc_code|volts|trit
FSOT_RLC_LOCK=0|1
```

Host twin (no board): `python firmware/host_observer.py`.

---

## 7. Cross-verify (same spirit as FSOT-2.1-Lean)

```powershell
python -m sim.run_sim
python verification\verify_circuit.py
z3 verification\circuit_bounds.smt2
```

| Layer | Artifact |
|-------|----------|
| A pin / seeds | `sim/fsot_engine.py` SHA prefix `D1D38A` |
| B ODE + catalog | `results/sim_report.json` `overall_ok` |
| C rust Θ / φ parity | `verification/verify_circuit.py` |
| D SMT | `verification/circuit_bounds.smt2` |
| D Lean integers | `formal/CircuitArrayPriors.lean` |

The full seven-way gauntlet (Coq / Isabelle / F* / TLA+) lives in the Lean hub. This lab exports the same obligation shape so it can be absorbed as a panel there.

---

## 8. Safety

- ±9 V analog, 3.3 V digital, one star ground.
- Clamps on every ADC node before you ever connect GPIO.
- GPIO 34/35 are input-only — never `digitalWrite` them.
- Disconnect batteries before unplugging USB.
