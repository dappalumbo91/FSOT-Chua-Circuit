# Where to go next

Order is the experiment, not more coefficients.

## 1. Confirm the public clone (this repo)

https://github.com/dappalumbo91/FSOT-Chua-Circuit

A scientist clone must pass `python verification/run_cross_proof.py` **without** the Lean hub tree. Watch GitHub Actions on `main`.

## 2. Buy the BOM and build the triangle

[`hardware/BOM.md`](../hardware/BOM.md). Dual ±9 V analog, USB 3.3 V digital, one star ground. Three 20 kΩ pots.

## 3. Two-position UART test (the actual kill)

Flash MicroPython first (`firmware/micropython/main.py`) if you want serial today; Rust `no_std` when the Xtensa toolchain is on the machine.

| Pots | Must see |
|------|----------|
| 20 kΩ | `FSOT_RLC_LOCK=0` |
| 11.12 kΩ | `FSOT_RLC_LOCK=1`, three trits equal |

If that fails with three identical nodes and safe ADC bias, the **application** is false — do not retune \(\varphi\).

## 4. Log vs sim

Pipe UART into `firmware/host_observer.py` (or a small decoder) and compare trit time series to `python -m sim.run_sim` at \(\sigma=\varphi\). That is the first hardware empirical row.

## 5. Optional rigor

- Install Isabelle and drop the SKIP (`formal/isabelle/CircuitArray.thy`)
- Compile `firmware/esp32_rlc_observer` with espup and add a firmware-hash note (still not a lock proof)
- Absorb a residual panel into FSOT-2.1-Lean **after** the breadboard row exists

## 6. PDF page 2 (later)

Ultrasonic levitation / Chladni / Faraday are **Acoustics** domain, same pin, different board. Do not mix them into this triangle until the RLC lock test has a measured row.
