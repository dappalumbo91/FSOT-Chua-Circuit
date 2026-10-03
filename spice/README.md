# FSOT-Chua-Circuit: no-login circuit verification (ngspice + Falstad CircuitJS) and breadboard build pack

These files replace Tinkercad, which needs an Autodesk login. Everything here runs on the box with free tools:
**ngspice 44.2** (apt), **Falstad CircuitJS** (browser, no account), Python 3 (numpy, matplotlib, schemdraw 0.23).
Every number below was produced by the scripts in this folder. Nothing was copied in from somewhere else. Times are from runs on 2026-10-03 (ET).

Shared source of truth: `../chua_netlist.py` (BOM of FSOT-Chua-Circuit: R = 1.8 kΩ, C1 = 10 nF, C2 = 100 nF, L = 22 mH,
NIC R1 = R2 = 220 Ω, R3 = 2.2 kΩ, R4 = R5 = 22 kΩ, R6 = 3.3 kΩ). The Falstad circuits and the breadboard layout are generated from it and
checked against it automatically. The SPICE subcircuit `models/chua_node.lib` contains the same values.

## 1. How to run

```bash
cd spice   # from the repo root
./fetch_models.sh                 # downloads TL082 (TI SLOJ070) + uA741 macromodels, verifies SHA-256 (not committed)
python3 calibrate_rails.py        # finds the rail voltage that gives Esat = 23/3 V (Bp1 = 1 V) for each macromodel
python3 run_single.py             # single node, all op-amp levels, x1 and x10 -> out/single_node_results.json, plots/
python3 run_ring.py ideal 0 2000 out/ring_ideal_r0_0.jsonl 0 0.9 1.0 1.618033988749895 2.618033988749895 2.2 2.25 2.26 2.3
python3 summarize_ring.py out/ring_ideal_r0_0.jsonl ...   # table + sigma_c
python3 plot_ring.py              # lock-vs-sigma and gate time-series plots
python3 make_canonical.py         # hand-runnable netlists in netlists/ (cd netlists && ngspice chua_single_tl082_x10.cir)
```
`run_ring.py <opamp> <r0_ohm> <T_tau> <out.jsonl> sigma...`. Opamp is `ideal`, `gbw`, `tl082`, or `ua741`. Set `K=10` for the ×10 time-scaled build and `NP=` for the number of parallel jobs.
About 10 s per 2000 τ ring run with `ideal`, about 40 s with `tl082`.

### Op-amp levels
| level | model | rails |
|---|---|---|
| (a) `ideal` | `OPAMP_GBW`, A0 = 10⁶, GBW = 1 GHz, hard clamp ±23/3 V with anti-windup (`models/opamp_beh.lib`, written here, free to commit) | n/a |
| (a) `gbw` | same, GBW = 100 MHz | n/a |
| (b) `tl082` | TI TL082 PSpice macromodel, `SLOJ070.ZIP` → `TL082.301`, https://www.ti.com/lit/zip/sloj070, sha256(zip) = 4f27e17a…937, sha256(TL082.301) = adad2e13…9011 | **±9.1899 V** (calibrated) |
| (b) `ua741` | TI "Parts 4.01" uA741 Boyle macromodel, mirrored at KiCad-Spice-Library `Models/Manufacturer/Texas Instruments/ua741.mod`, sha256 = 75693f52…9505 | **±9.6614 V** (calibrated) |

The vendor models are **not committed**. TI's terms are not an explicit redistribution grant, so per Damian's rule `fetch_models.sh` records each source URL and checksum instead, and `.gitignore` excludes `models/vendor/`.
A memoryless clamp B-source would not converge on the NIC's algebraic loop with `uic` (Newton fails at t = 0), so level (a) uses a 1 GHz single pole.
Rail calibration (`out/rail_calibration.json`): with the TL082 at ±9.1899 V, U2 saturates at +7.6664 / −7.6669 V, giving Bp1 = +1.0000 / −1.0000 V. At ±9 V the TL082 gives Bp1 = 0.975 V and the 741 gives 0.914 V.
Optional inductor DCR: parameter `r0` in `CHUA_NODE`. ×10 build: parameter `k` (C1, C2, L × k), which leaves every dimensionless number unchanged.

## 2. Single node (σ = 0), 500 τ, statistics after 50 τ (`out/single_node_results.json`)
| op-amp, scale | V_C1 range [V] | V_C2 range [V] | lobe switches / 100 τ | V_C2 spectrum peak (×k) |
|---|---|---|---|---|
| ideal ×1 | −4.295 … +4.295 | ±0.978 | 22.4 | 2494 Hz |
| gbw 100 MHz ×1 | −4.293 … +4.263 | −0.958 … +0.976 | 24.0 | 2481 Hz |
| TL082 ×1 | −4.244 … +4.234 | ±0.95 | 16.2 | 2642 Hz |
| uA741 ×1 | −4.166 … +4.168 | ±0.908 | 14.0 | 2580 Hz |
| ideal ×10 | ±4.295 | ±0.979 | 24.7 | 237.0 Hz (2370) |
| TL082 ×10 | −4.278 … +4.275 | ±0.97 | 23.6 | 238.3 Hz (2383) |
| uA741 ×10 | −4.263 … +4.267 | ±0.965 | 21.1 | 250.6 Hz (2506) |

All seven runs are **double scroll** with no escape past Bp2 = 6.97 V.
Comparison with the C++/Python plan: V_C1 ±4.29 V and V_C2 ±0.98 V are reproduced exactly by the ideal model. The plan's "≈ 20 switches / 100 τ" matches 22–25.
The spectral peak of a chaotic signal is broad, and over 450 τ the FFT resolution is 12 Hz. The peak sits at 2.37–2.49 kHz (ideal) against the plan's 2.3–2.4 kHz.
With the real macromodels at ×1, amplitude drops by 1–3 % and lobe switching slows. This is the slew/GBW effect the plan predicted for the 741 at ×1. At ×10 both macromodels return to within 0.5 % of ideal.
Plots: `plots/spice_double_scroll.png` and `plots/spice_time_series_spectrum_tl082.png`.

## 3. 3-node ring (Rc on V_C1 nets), 2000 τ (0.36 s at ×1)
Initial conditions: three asymmetric sets, v1 = 0.1 + 0.05·i + 0.01·N(0,1) and v2 = 0.02·N(0,1) (numpy seeds 1, 2, 3).
**Lock law**, evaluated on the last 40 %: mean pairwise |ΔV_C1| ≤ φ⁻⁴ · std(V_C1A) **and** max|V_C1| < 6.97 V. A run that fails only the amplitude condition is on the outer large limit cycle, measured here at ±7.56 V and 3028 Hz.
σc is the smallest grid σ above which every grid point and every IC locks.

### σc from SPICE vs C++
| r0 | γ = β·r0/R | SPICE ideal | SPICE TL082 | C++ direct (6 seeds, 2000 τ) | C++ master-stability |
|---|---|---|---|---|---|
| 0 Ω | 0 | **(2.255, 2.26]** | **(2.20, 2.21]** | (2.20, 2.30] (2.25: 5/6) | **2.26** |
| 20 Ω | 0.164 | **(1.470, 1.475]** | **(1.40, 1.45]** | (1.45, 1.50] | **1.44** |
| 35 Ω | 0.286 | **(1.045, 1.05]** (first locks at 1.035; 1.045 is 1/3) | **(1.15, 1.20]** | (1.05, 1.10] | **1.05** |

At r0 = 0 the near-threshold locks (2.26–2.275) are intermittent: mean agreement error is 2–5 % of amplitude. Clean sync (error < 10⁻⁴) starts around σ = 2.30.

### Gate outcomes (3 ICs each)
| Rc | σ | ideal r0=0 | TL082 r0=0 | TL082 ×10 r0=0 | ideal r0=20 | TL082 r0=20 | ideal r0=35 | TL082 r0=35 |
|---|---|---|---|---|---|---|---|---|
| open | 0 | chaos, no lock | chaos | chaos | chaos | chaos | chaos | chaos |
| 20 kΩ | 0.9 | large cycle (escape ≥ 17 τ) | large cycle (23 τ) | large cycle (20 τ) | large cycle (44 τ) | large cycle (62 τ) | **unlocked double scroll** | **unlocked double scroll** |
| 18 kΩ | 1 | large cycle | large cycle | large cycle | large cycle | large cycle | unlocked | unlocked |
| 11 124.61 Ω | φ | **large cycle (52 τ)** | **large cycle (56 τ)** | **large cycle (51 τ)** | lock 3/3 | lock 3/3 | lock 3/3 | lock 3/3 |
| 6 875.39 Ω | φ² | **lock 3/3** | **lock 3/3** | **lock 3/3** | lock 3/3 | lock 3/3 | lock 3/3 | lock 3/3 |

uA741 macromodel, ×10, r0 = 0 (rails ±9.6614 V): open = chaos, 20 kΩ / 18 kΩ / φ = large cycle (escape at 27 / 26 / 59 τ), φ² = lock 3/3, the same verdicts as the TL082 and the ideal model.
One non-monotonic point: with the ideal op-amp at r0 = 35 Ω, σ = 0.8 (22.5 kΩ) escaped to the large cycle in 3/3 runs (from 161 τ), while 0.5 and 0.9 stayed on the double scroll.

"Large cycle" means every node is on ±7.5 V with trits in 100 % agreement. Trit-only firmware would report LOCK=1 here, which is a false lock.
**The repo's four gates (σ=0 no lock, 20 kΩ/18 kΩ no lock, φ lock, φ² lock) all hold only at r0 ≈ 35 Ω**, with both the ideal op-amp and the TL082. That is the same r0 dependence the C++ work found.
With an ideal inductor (r0 = 0), σ = φ is **falsified** in SPICE, and σ = φ² is the robust prediction.
Plots: `plots/spice_ring_lock_vs_sigma.png` (SPICE vs C++ vs MSF) and `plots/spice_ring_gates_time_series.png`.
Raw results are in `out/ring_*.jsonl` and `out/ring_summary.json`.

## 4. Falstad CircuitJS (`../falstad/`)
`gen_falstad.py` writes `chua_single_node.txt`, `chua_ring_sigma_phi2.txt` and `chua_ring_sigma_phi.txt` (File → Import From Text), along with `*.url` (`?ctz=`, LZString `compressToEncodedURIComponent`, pure-Python port in `lzstring_uri.py`).
- The op-amps are Falstad ideal op-amps with max/min output set to **±7.6667 V**. Each node has two, matching the TL082 halves.
- Each capacitor is set so its initial voltage starts the oscillation: A/B/C = 0.1/0.15/0.2 V on C1.
- The X–Y scope shows V(C1A) vs V(C2A). The ring has a second X–Y scope, V_C1A vs V_C1B, where a diagonal line means lock.
- Timestep: 0.25 µs (fixed).

`verify_falstad.py` checks five things:
1. Element codes and token counts against pfalstad/circuitjs1 sources: `r`, `c`, `l`, `a`, `g`, `w`, `207`, `o`, `$`.
2. It rebuilds connectivity the way CircuitJS does (posts, wires, labelled nodes, ground). The op-amp pins are (−) = (x1, y1−16), (+) = (x1, y1+16), out = (x2, y2).
3. The rebuilt nets match `chua_netlist.py`.
4. The scope X/Y elements are C1A/C2A, both grounded.
5. The `?ctz=` string round-trips through Falstad's own `war/lz-string.min.js`.

Result: ALL OK. The Python LZString port is byte-identical to the JS library on random test strings.
`falstad_live_check.py` loads the URL in real Chrome against the live falstad.com and records labelled-node voltages each frame:
- **single node**: 44 elements loaded. Over 120 ms of sim time, V_C1 ranged −4.274 … +4.275 V and V_C2 −0.974 … +0.967 V, a double scroll (`shots/chua_single_node_live.png`).
- **ring σ = φ²**: 141 elements. Over 1383 τ, mean pairwise ΔV/amp = 2.1×10⁻¹⁴ and max |V_C1| = 4.24 V, so it **locks** (`shots/chua_ring_sigma_phi2_live.png`, diagonal sync trace).
- **ring σ = φ**: escapes to the large cycle at 69.5 τ, max |V_C1| = 7.56 V. Same verdict as SPICE.

## 5. Breadboard build pack (`../build_visuals/`)
- `schematic_single_node.{png,svg,pdf}` and `schematic_ring_sigma_phi2.{png,svg,pdf}` (schemdraw): part values, TL082 pin numbers, net labels, and test points.
- `breadboard_single_node.{png,svg,pdf}` and `breadboard_ring_sigma_phi2.{png,svg,pdf}`: a standard 830-point board, with every lead placed in a specific hole.
  - Wire colours: red +V, blue −V, black GND, yellow V_C1 links, green/orange/purple for the A/B/C coupling wires.
  - Magenta rings mark the test points.
  - The ring uses one TL082 per node, all three nodes on one board, and a coupling area at rows 45–61 where each Rc is 6.8 kΩ + 75 Ω.
- `build_checklist_single_node.md` (19 steps) and `build_checklist_ring_sigma_phi2.md` (66 steps): row and column for every lead, plus a test-point table.
- `connectivity_report.json`: the layout is generated from the same netlist structure and then re-checked at the hole level (strips, rails, jumpers). Nets match for both boards: 9 and 24 nets.
  - Two deliberate miswiring mutations were both detected.
- The TL082 matches the repo BOM (one dual op-amp per node). A 741 alternative is noted on every sheet: two 741s per node, pin 3 = +, pin 2 = −, pin 6 = out, rails ±9.66 V.

## 4. r0 = 18.44 Ω (FSOT Branch L), added 2026-10-03 (ET)
`run_r0FSOT.sh` (2000 τ, 3 ICs, the same lock law as §3):
| op-amp | σc (strict rule: every IC locks at all larger grid σ) | lock fractions |
|---|---|---|
| ideal (1 GHz pole) | (1.52, 1.53] | 1.46–1.48: 0/3 · 1.49: 1/3 · 1.50: 1/3 · 1.51: 3/3 · 1.52: 2/3 · ≥ 1.53: 3/3 |
| TI TL082 macromodel, ±9.19 V | (1.45, 1.475] | 1.40–1.45: 0/3 · ≥ 1.475: 3/3 |
For comparison, the C++ RK4 with 48 seeds gives σ50 = 1.4954 [1.4947, 1.4961], and the locked FSOT MSF value is 1.4897.
The ideal SPICE crossing (1/3 at 1.49–1.50) matches the C++ 50 % point. The strict 3-IC rule reads higher because a single slow IC at 1.52 counts against it.
The TL082 lowers the threshold by about 0.05, in line with the C++ single-pole TL082 model ((1.44, 1.46]).
Plot: `../error_budget/png/lock_vs_sigma_r0_18p44.png`. Full error budget: `../error_budget/ERROR_BUDGET.md`.
Note: `cpp_ref/` holds the C++ 6-seed sweep tables that `plot_ring.py` overlays. The vendor models are fetched by `fetch_models.sh` (not committed).
