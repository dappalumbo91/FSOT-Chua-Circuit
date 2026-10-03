# Claims and non-claims — FSOT-Circuit

This repository is an **application**. It vendors pin AEB2AD and **re-proves its own obligations**. A green hub does not make this board true.

## Claims (this tree)

| Claim | Kind | Kill |
|-------|------|------|
| Vendor `fsot_compute.py` SHA-256 starts with AEB2AD | pin | `python tests/test_algebra.py` |
| Zero free parameters in the operating point | proved (policy) | any fitted a,b / lock cut / σ_c |
| NIC \(G_a=-1/1320\), \(G_b=-9/22000\), \(G_c=101/22000\) (\(a=-15/11\), \(b=-81/110\), \(c=909/110\)) from BOM resistors | proved (rational) | Lean / Coq / algebra tests |
| Inductor loss \(\gamma=0.15087\) (\(r_0=18.44\,\Omega\), \(Q_L=25.44\)) from FSOT 2.1 Branch L | **new-branch hypothesis** (derived, not fitted) | LCR / ring-down Q of the 22 mH part at 3.39 kHz |
| Lock threshold \(\sigma_c=1.4897\) (locked before the sweep; sha256 `04ebe3f4…`, `d6bd17be…`) | **sharp prediction**, numerically verified (sweep 1.525) | `python -m sim.run_sim`; bench pot sweep, \(R_c^{\ast}\) in 11.70–12.50 kΩ |
| Ring of 3 identical nodes; \(\sigma=\varphi^2\) locks; \(\sigma=0\), 1 and \(R_c=20\,\mathrm{k}\Omega\) do not (2000 τ, amplitude-checked) | numerically verified (robust gate) | `python -m sim.run_sim` |
| \(\sigma=\varphi\) locks | **demoted**: consequence of \(\sigma_c<\varphi\) only. Ideal inductor: does not lock (\(\sigma_c=2.26\)); the old 80 τ “lock” was a `np.clip(±8)` artifact | same |
| BOM catalog residual at Electromagnetism ≤ 0.5% | empirical | median in `results/sim_report.json` |
| ESP32 bias map \(1.65+V/6\) keeps the double scroll (±4.33 V) and the escape cycle (±7.35 V) inside 0–3.3 V | numerically verified | ADC suite |
| Multi-prover spine (Python · Lean · Coq · SMT · Rust · TLA) | process | `python verification/run_cross_proof.py` |

## Non-claims

- Hub 472/472 green gates are **not** this repo’s result.
- Hardware lock on a physical breadboard is **not** yet a measured empirical row. The ODE is the current measurement. Solder is the next kill.
- Isabelle is shipped as source; it is not a required layer until `isabelle` is on PATH.
- Firmware flash success is not a math gate. Rust ESP32 crate is **source only** until Xtensa/espup is used (`firmware/STATUS.md`).

## Falsify

1. Pin prefix not AEB2AD after a clean clone.
2. `run_cross_proof.py` `overall_ok: false`.
3. Breadboard: pots at 6.88 kΩ never lock, or 20 kΩ reads LOCK with the amplitude condition, or the threshold falls outside 11.70–12.50 kΩ, with copies of the three nodes.
4. Inductor Q at 3.39 kHz far from 25.44 falsifies Branch L. Then \(\sigma_c\) must be recomputed from the measured \(r_0\) (`FSOT_CHUA_R0=<ohm> cpp/build/fsot_chua_sim msf kennedy`), and that is a measurement, not an FSOT prediction.
