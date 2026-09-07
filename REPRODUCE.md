# Reproduce FSOT-Circuit (independent of the hub working tree)

```powershell
git clone <this-repo>
cd FSOT-Circuit
python -m pip install -r requirements.txt
python verification/run_cross_proof.py
```

Expect `results/cross_proof_report.json` → `overall_ok: true`.

`--fast` skips the ~20 s Chua sweep (algebra + formal only). CI and a scientist clone must run **without** `--fast`.

## Tools the gauntlet will use if present

| Layer | Tool |
|-------|------|
| A algebra + pin | Python 3.11, numpy, mpmath |
| B ODE gates | same |
| SMT bounds | `python verification/smt_replay.py` (always) + `z3` (CI / if installed) |
| Lean | `lake` / Lean 4.33.1 (`lean-toolchain`) |
| Coq | `coqc` (Rocq 9 `From Stdlib` preamble) |
| Rust | `cargo` |
| TLA+ | `java` + vendored `tools/tla/tla2tools.jar` |
| Isabelle | optional |

Missing optional Isabelle is SKIP, not FAIL. Missing a **required** tool is FAIL — install it; do not skip.

## Pin

`vendor/fsot_compute.py` must hash to prefix **D1D38A**. File is marked `-text` in `.gitattributes` so Git does not CRLF-break the pin.
