# cpp/ — C++20 layer (FSOT-2.1-Cpp conventions, pin AEB2AD)

| Path | What |
|------|------|
| `include/fsot_chua/branch_l.hpp` | Header-only `BranchL<R>` (ε, k = 1/Q_L, r0, γ) and `KennedyNic<R>`, templated on the FSOT-2.1-Cpp number types |
| `tests/test_branch_l.cpp` | Golden test vs `golden/branch_l_AEB2AD.tsv` (Python/mpmath dps 50) at double, long double, `__float128`, `cpp_bin_float<169>` |
| `tools/dump_branch_l_golden.py` | Regenerates the golden from `vendor/fsot_compute.py` (asserts the AEB2AD hash) |
| `tools/fsot_chua.cpp` | `derive`, `single`, `lyap`, `msf`, `sweep`, `trace` for the dimensionless ring. r0 defaults to Branch L; `FSOT_CHUA_R0=<ohm>` overrides it (0 = ideal). `FSOT_CHUA_AMPCHECK=1` turns on the no-escape lock law, `FSOT_CHUA_TAIL_TAU` sets the scored tail, `FSOT_CHUA_SGRID` the σ step, and `FSOT_CHUA_CLIP8=1` reproduces the old ±8 clip |
| `tools/fsot_chua_nonideal.cpp` | Dimensional ring with single-pole op-amps (GBW, slew, rails), r0, ADC Thevenin load, and time scaling |
| `predictions/` | Locked predictions (part 1: γ and gates; part 2: σc), each with its `.sha256`, written before the ring sweep |
| `results/` | Outputs at r0 = 18.44 Ω: MSF, 2000 τ sweep, single node, non-ideal runs |

```
cmake -S cpp -B cpp/build -G Ninja            # fetches FSOT-2.1-Cpp @ e3e3e23 (AEB2AD); or -DFSOT_CPP_DIR=...
cmake --build cpp/build && ctest --test-dir cpp/build
FSOT_CHUA_AMPCHECK=1 FSOT_CHUA_TAIL_TAU=500 FSOT_CHUA_SGRID=0.025 cpp/build/fsot_chua_sim sweep kennedy 2000 0.005
cpp/build/fsot_chua_sim msf kennedy
```
