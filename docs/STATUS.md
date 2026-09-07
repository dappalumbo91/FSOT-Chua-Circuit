# Status — FSOT-Circuit (this tree only)

**Date:** 2026-09-07  
**Pin:** D1D38A (`vendor/fsot_compute.py`)  
**inherits_hub_overall_ok:** false

## What is closed

- Operating point \(\sigma=\varphi\), \(R_c=11124.61\,\Omega\), 3-node **ring**
- NIC slopes from BOM rationals, not Matsumoto fits
- Independent gauntlet: Python · SMT bounds · Z3 (when present) · Lean · Coq · Rust · TLA+
- Tutorial + BOM + DevKit pin map
- CI workflow for a GitHub clone

## What is not closed

| Item | Why |
|------|-----|
| Physical breadboard lock | Not soldered. ODE is the current measurement. |
| ESP32 firmware compile/flash | Xtensa toolchain; not in CI |
| Isabelle | Source shipped; tool not on PATH |
| Hub catalog panel | This repo stays independent until you choose to absorb it |
| PDF p.2 acoustics / Chladni / Faraday | Deferred |

Kill command after a clean clone: `python verification/run_cross_proof.py`
