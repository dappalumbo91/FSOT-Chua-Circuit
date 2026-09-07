# FSOT-Chua-Circuit

A **coupled Chua circuit** — in the electronics literature, a nonlinear RLC oscillator with a piecewise-linear negative resistor (the “Chua diode”), tiled here as a **3-node ring**.

This repository is a **physical application** of Fluid Spacetime Omni-Theory (FSOT). Analog voltages occupy three regions \((-1,\,0,\,+1)\). An ESP32 12-bit ADC is the observer. The prediction you can build this afternoon is a coupling resistance, not a fitted neural net.

| | |
|--|--|
| **What it is** | 3 identical Chua nodes, resistively coupled in a triangle |
| **Field name** | Coupled Chua circuit / nonlinear RLC oscillator array |
| **FSOT pin** | **D1D38A** (`vendor/fsot_compute.py`) |
| **Domain** | Electromagnetism, \(D_{\mathrm{eff}}=9\) |
| **Operating point** | \(\sigma=\varphi\), \(R_c=\alpha R/\varphi=11124.61\,\Omega\) |
| **Free parameters** | **0** |
| **License** | [Apache License 2.0](LICENSE) |
| **Author** | Damian Arthur Palumbo |

Anyone with a breadboard, two 9 V batteries, an ESP32 DevKit, and Python 3.11 can run the software gate and then the hardware experiment. Hub math lives in [FSOT-2.1-Lean](https://github.com/dappalumbo91/FSOT-2.1-Lean). **A green hub does not certify this board.** This tree re-proves its own obligations.

**Hands-on build:** [docs/BUILD_TUTORIAL.md](docs/BUILD_TUTORIAL.md) · [docs/tutorial.html](docs/tutorial.html)  
**Parts and pins:** [hardware/BOM.md](hardware/BOM.md) · [hardware/schematic.md](hardware/schematic.md)  
**Claims / kill:** [docs/CLAIMS.md](docs/CLAIMS.md)  
**Status:** [docs/STATUS.md](docs/STATUS.md)

---

## What this is trying to accomplish

1. Map FSOT **trinary states** onto real analog voltages without CPU floating-point:
   - \(V_{C1} < -1\,\mathrm{V}\) → **−1** (inhibition / damping)
   - \(\lvert V_{C1}\rvert \le 1\,\mathrm{V}\) → **0** (quiescent)
   - \(V_{C1} > +1\,\mathrm{V}\) → **+1** (excitation / emergence)
2. Predict, with **zero free parameters**, the coupling at which three identical chaotic oscillators **phase-lock**.
3. Let an independent builder **falsify that prediction** with three potentiometers and a serial log.

If pots at **11.12 kΩ** never lock, or pots at **20 kΩ** always lock, with three identical nodes and a safe ADC bias, the **application is false**. Do not retune \(\varphi\).

---

## Current stage — move forward in this order

Software and formal gates on this tree are green (`overall_ok: true`). The next kill is **hardware**.

| Step | Do this | Done when |
|------|---------|-----------|
| **1. Clone and verify** | `pip install -r requirements.txt` then `python verification/run_cross_proof.py` | `results/cross_proof_report.json` → `overall_ok: true` |
| **2. Buy the BOM** | [hardware/BOM.md](hardware/BOM.md) — TL082s, 22 mH / 10 nF / 100 nF / 1.80 kΩ, NIC resistors, three 20 kΩ pots, ESP32 DevKit V1, two 9 V batteries | Parts on the bench |
| **3. Build the triangle** | Three identical Chua islands; pots between `VC1` nodes; 100 kΩ/100 kΩ bias + 1N4148 clamps into GPIO **34 / 35 / 32**; analog ±9 V **never** on the MCU; one star ground | DMM: ADC nodes ~1.65 V with USB only |
| **4. Two-position UART test** | Flash [firmware/micropython/main.py](firmware/micropython/main.py) first (or Rust `no_std` when you have Xtensa). Set all three pots | **20 kΩ** → `FSOT_RLC_LOCK=0`. **11.12 kΩ** → `FSOT_RLC_LOCK=1` and three trits equal |
| **5. Log vs sim** | Compare UART trit series to `python -m sim.run_sim` at \(\sigma=\varphi\) | First hardware empirical row |
| **6. Optional later** | Isabelle on PATH; Rust firmware hash; PDF p.2 acoustics (Chladni / Faraday) as a **separate** Acoustics board | Not this triangle |

Rust ESP32 firmware is **source**, not compiled in CI. MicroPython is the fast serial path. See [firmware/STATUS.md](firmware/STATUS.md).

---

## Quick start (software)

```powershell
git clone https://github.com/dappalumbo91/FSOT-Chua-Circuit.git
cd FSOT-Chua-Circuit
python -m pip install -r requirements.txt
python verification/run_cross_proof.py
```

Expect `overall_ok: true`. That command does **not** need the Lean hub checkout.

| Layer | Role |
|-------|------|
| Python algebra + pin | SHA-256 prefix D1D38A, NIC rationals \(G_a=-1/1320\), \(a=-15/11\) |
| Host observer twin | Same `FSOT_RLC_*` frames as firmware |
| Chua ring ODE | Lock at \(\sigma=\varphi\); unlocked at \(\sigma=0\) and \(\sigma=1\) |
| SMT | Python bound replay + Z3 when installed |
| Lean 4 | `lake build` |
| Coq / Rocq | `formal/coq/CircuitArray.v` |
| Rust | `verification/rust_circuit_kernel` |
| TLA+ | TLC on the lock-state machine |
| Isabelle | Optional until `isabelle` is installed |

CI: [`.github/workflows/ci.yml`](.github/workflows/ci.yml).

---

## Hardware experiment (the proof)

Three **identical** nodes in a **ring** (every node degree 2). A 1-D chain is the wrong object.

```
        [ Node A ]----- 11.12 kΩ -----[ Node B ]
             \                           /
              \                         /
           11.12 kΩ                 11.12 kΩ
                \                     /
                 \                   /
                  +----[ Node C ]---+
                         |
              ESP32 ADC  A→GPIO34  B→GPIO35  C→GPIO32
```

- Analog island: ±9 V, three TL082, tanks, NIC, pots.
- Digital island: USB 5 V → DevKit 3.3 V.
- Star-ground analog GND to ESP32 GND at **one** hole.
- GPIO 34 and 35 are **input-only**. Bias: \(v_{\mathrm{ADC}}=1.65+0.5\,V_{C1}\). Clamps before every ADC pin.

Full placement: [hardware/schematic.md](hardware/schematic.md).

---

## Mathematics

Authority: `vendor/fsot_compute.py` (byte pin **D1D38A**). Seeds \(\pi,\,e,\,\varphi,\,\gamma,\,G\). No fitted Chua slopes.

**Scalar (same engine as the hub, this domain only):**

\[
S = K(T_1+T_2+T_3),\qquad
\Theta = C_{\mathrm{eff}}\,P_{\mathrm{var}}
\]

Electromagnetism: \(D_{\mathrm{eff}}=9\), \(S\approx 0.518866\), \(\Theta\approx 0.917466\). Catalog parts use the preregistered factor \(f=0.0004\) (BOM median residual **0.0208%**).

**Chua node (BOM, not Matsumoto’s fitted \(a,b\)):**

\[
\alpha=\frac{C_2}{C_1}=10,\qquad
\beta=\frac{R^2 C_2}{L},\qquad
G_a=-\frac{1}{2200}-\frac{1}{3300}=-\frac{1}{1320},\qquad
G_b=-\frac{1}{3300}
\]

\[
a=R G_a=-\frac{15}{11},\qquad
b=R G_b=-\frac{6}{11}
\]

Audio-band tank: \(R=1.80\,\mathrm{k}\Omega\), \(L=22\,\mathrm{mH}\), \(C_1=10\,\mathrm{nF}\), \(C_2=100\,\mathrm{nF}\) → \(f_{LC}\approx 3.39\,\mathrm{kHz}\).

**Dimensionless coupling and operating point:**

\[
\sigma=\frac{\alpha R}{R_c},\qquad
\sigma=\varphi \;\Rightarrow\;
R_c=\frac{\alpha R}{\varphi}=11124.61\,\Omega
\]

Lock cuts are seed-closed: trit agreement \(\ge\varphi^{-1}\), fractional disagreement \(\le\varphi^{-4}\). ODE gates (6 random initial conditions):

| \(\sigma\) | \(R_c\) | Lock rate |
|-----------:|--------:|----------:|
| 0 | open | 0 |
| 1 | 18.0 kΩ | 0 |
| \(\varphi\) | **11.12 kΩ** | **1** |
| \(\varphi^2\) | 6.88 kΩ | 1 |

A chain plus literature-fitted slopes plus an invented 0.85 lock cut produced a 3% residual. That was **wrong application**, not a missing coefficient. Map: [docs/MATH_MAP.md](docs/MATH_MAP.md).

---

## Repository layout

```
vendor/fsot_compute.py          D1D38A pin (gitattributes -text)
sim/                            ring ODE, ADC model, operating point
firmware/                       MicroPython + Rust no_std + PC twin
hardware/                       BOM, schematic, netlist
FSOTCircuit/                    Lean application priors
formal/coq|isabelle|tla         independent spines
verification/                   gauntlet, SMT, Rust kernel
docs/                           tutorial, claims, status, next
```

---

## License

Copyright 2026 Damian Arthur Palumbo.

Licensed under the Apache License, Version 2.0. See [LICENSE](LICENSE) and [NOTICE](NOTICE).
