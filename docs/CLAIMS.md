# Claims and non-claims — FSOT-Circuit

This repository is an **application**. It vendors pin D1D38A and **re-proves its own obligations**. A green hub does not make this board true.

## Claims (this tree)

| Claim | Kind | Kill |
|-------|------|------|
| Vendor `fsot_compute.py` SHA-256 starts with D1D38A | pin | `python tests/test_algebra.py` |
| Zero free parameters in the operating point | proved (policy) | any fitted a,b / lock cut / σ_c |
| NIC \(G_a=-1/1320\), \(a=-15/11\) from BOM resistors | proved (rational) | Lean / Coq / algebra tests |
| Ring of 3 identical nodes; \(\sigma=\varphi\) locks; \(\sigma=1\) does not | numerically verified | `python -m sim.run_sim` |
| BOM catalog residual at Electromagnetism ≤ 0.5% | empirical | median in `results/sim_report.json` |
| ESP32 bias map keeps ±2 V inside 0–3.3 V | numerically verified | ADC suite |
| Multi-prover spine (Python · Lean · Coq · SMT · Rust · TLA) | process | `python verification/run_cross_proof.py` |

## Non-claims

- Hub 472/472 green gates are **not** this repo’s result.
- Hardware lock on a physical breadboard is **not** yet a measured empirical row. The ODE is the current measurement. Solder is the next kill.
- Isabelle is shipped as source; it is not a required layer until `isabelle` is on PATH.
- Firmware flash success is not a math gate. Rust ESP32 crate is **source only** until Xtensa/espup is used (`firmware/STATUS.md`).

## Falsify

1. Pin prefix not D1D38A after a clean clone.
2. `run_cross_proof.py` `overall_ok: false`.
3. Breadboard: pots at 11.12 kΩ never lock, or 20 kΩ always locks, with copies of the three nodes.
