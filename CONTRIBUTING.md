# Contributing

This is an **application** of pin D1D38A. Do not add free parameters (fitted Chua slopes, invented lock cuts, post-hoc σ_c).

1. Change math or topology → re-run `python verification/run_cross_proof.py` with `overall_ok: true`.
2. Change `vendor/fsot_compute.py` only to keep the D1D38A byte pin. `.gitattributes` marks it `-text`.
3. Hub FSOT-2.1-Lean green gates are not a substitute for this tree’s gauntlet.
