# Status — FSOT-Circuit (this tree only)

**Date:** 2026-10-03 (branch fix/aeb2ad-long-window)  
**Pin:** AEB2AD (`vendor/fsot_compute.py`, re-vendored from D1D38A)  
**inherits_hub_overall_ok:** false

## What is closed

- Sharp prediction \(\sigma_c=1.4897\) (FSOT Branch L \(\gamma\) + master stability), locked before the sweep; 2000 τ sweep threshold 1.525
- Robust gate \(\sigma=\varphi^2\) (6.88 kΩ) locks; 0, 1, 20 kΩ do not (amplitude-checked)
- \(\sigma=\varphi\) demoted (see CLAIMS)
- NIC slopes from BOM rationals with the corrected \(G_b=-9/22000\) and the outer segment
- Long-window (2000 τ) integration, no clip; firmware LOCK has the amplitude condition
- ADC bias corrected (300 k / 100 k / 150 k, \(1.65+V/6\))
- C++20 layer (`cpp/`): Branch L golden at double / long double / f128 / mp169
- Independent gauntlet: Python · SMT bounds · Z3 (when present) · Lean · Coq · Rust · TLA+
- Tutorial + BOM + DevKit pin map
- CI workflow for a GitHub clone

## What is not closed

| Item | Why |
|------|-----|
| Physical breadboard lock | Not soldered. ODE is the current measurement. |
| Inductor Q measurement | Branch L predicts Q_L = 25.44 at 3.39 kHz; not yet measured |
| ESP32 firmware compile/flash | Xtensa toolchain; not in CI |
| Isabelle | Source shipped; tool not on PATH |
| Hub catalog panel | This repo stays independent until you choose to absorb it |
| PDF p.2 acoustics / Chladni / Faraday | Deferred |

Kill command after a clean clone: `python verification/run_cross_proof.py`
