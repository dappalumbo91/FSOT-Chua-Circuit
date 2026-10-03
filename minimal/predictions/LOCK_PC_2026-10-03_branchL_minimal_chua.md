# LOCK PC: Path C. Minimal Chua-family circuit on Branch L. Topology choice and predictions, locked BEFORE the new simulations

## FSOT values (validated earlier; not tuned)
- r0 = 18.4400497592861384 Ω and γ = β r0/R = 0.150873134394159315 (Branch L; tests/test_algebra.py:86-87; cpp/golden).
- BOM (chua_netlist.py): R = 1.8 kΩ, C1 = 10 nF, C2 = 100 nF, L = 22 mH, Kennedy NIC 220/220/2.2k and 22k/22k/3.3k.
- Dimensionless model (cpp/tools/fsot_chua.cpp): α = 10, β = 14.7273, a = −15/11, b = −81/110, c = 909/110, x2 = 6.9697 (breakpoint units, Bp = 1 V); τ = R·C2 = 180 µs.

## Topology choice (rule: fewest parts that keep the Branch L-validated characteristic)
- **Single-op-amp NIC: rejected.** It gives one negative slope; its outer slope is +1/R1 (passive), so it cannot produce both a = −15/11 and b = −81/110. It would be a different, unvalidated characteristic.
- **Gyrator (inductorless): optional.** It adds 1 op-amp + 4 R + 1 C to remove the coil and set r0 with a resistor (BENCH_BUILD_GUIDE route 3). This is more parts.
- **Winner: Kennedy single node.** 1 × TL082 (2 sections), 6 NIC resistors + R + R_add, C1, C2, L. That is **12 parts** (plus 2 decoupling caps). Nonlinear elements: 2 op-amp saturations; no diodes.

## Predictions
| ID | Prediction | Type | Pass band |
|---|---|---|---|
| PC1 | Basin: 64 seeds (mt19937 seed 1) uniform in x ∈ [−6, 6], y ∈ [−1, 1], z ∈ [−6, 6]; ≥ 48/64 end on the double scroll (λ1 > 0.05/τ, max|x| < x2 over 2000 τ after 200 τ transient) | genuine | as stated |
| PC2 | λ1 = 0.245/τ (cpp/results/single_r0FSOT.tsv) | replication (known) | ±10 % |
| PC3 | Dominant frequency ≈ Im λ(middle-segment equilibrium)/(2π τ) = 3.02868/(2π·180 µs) = **2678 Hz** | genuine (analytic) | ±15 % |
| PC4 | max|x| = 4.33 Bp (cpp/results/single_r0FSOT.tsv; Falstad −4.27…+4.32 V) | replication (known) | ±5 % |
| PC5 | ngspice, TI TL082 models, default start: double scroll (both lobes visited, > 40 distinct maxima, no rail latch) over 0.1 s | replication of spice/run_single.py | as stated |
| PC6 | Tolerance (C++): 64 draws with L ±1.2 %, C1 ±1 %, R ±1 %, C2 ±4.5 %, r0 ±0.33 Ω and NIC resistors ±1 % (uniform), each from the default start; ≥ 58/64 stay on the double scroll | genuine | as stated |
| PC7 | Proof: an interval-arithmetic covering-relation check (adapted from horseshoe.cpp to the 3-segment PWL Chua field with r0) is *attempted*. It is not predicted; it is reported as verified or not reached | n/a | n/a |
