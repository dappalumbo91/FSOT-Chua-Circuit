# LOCK B scorecard: ideal-to-hardware bridge (precision rectifier)

Lock: `predictions/LOCK_B_2026-10-03_bridge_precision_rectifier.md`, sha256 `f5e71c49916b523a1fcb8879d390821dbc6318b04e2c5c45a296ba89786998f4`. It was locked before any B-PR simulation. All predictions are genuine (blind).

Derivation (summary from the lock): FSOT fixes dimensionless ratios but no voltage scale, so it cannot set U_eff. ε = nV_T/U_eff therefore cannot be pinned by choosing U_eff. The FSOT-consistent route is ε → 0: a precision rectifier divides the knee by the open-loop gain, ε_PR = nV_T/(A_OL·U) = 6.23e-7, with n = 1 + S_EM = 1.9557 (Branch DJ), A_OL = 2e5 and U = 0.403 V. Design B-PR: 5 op-amp sections (TL074 + TL072), 2 × 1N4148, RA = 4.22k (R/γ_rel).

| ID | Prediction | Engine | Result | Verdict |
|---|---|---|---|---|
| B1 | Bounded from the mapped attractor IC, λ1 = 0.0156/τ0 ± 20 % | C++ `topo/bpr ic` | bounded, λ1 = 0.0149 | confirmed |
| B2 | f = 817 Hz ± 5 % | C++ | 815.8 Hz | confirmed |
| B3 | x ∈ [−2.339, 1.448]·U | C++ | [−2.3391, 1.4480] | confirmed |
| B4 | Basin not usable: ≤ 2/16 seeds bounded | C++ `topo/bpr seeds 16` | 1/16 (seed10). Post-score extra: 2/64 at T = 3000 | confirmed (negative for buildability) |
| B5 | ngspice (TI TL082 macro-models, D1N4148) from the attractor IC: bounded, chaotic | `spice/run_lockb.py` | irregular for about 5 cycles, then rail latch at 6.06 ms (o3 = +7.48 V) | **falsified** |
| B6 | ngspice from the default start V(o3) = −0.3 V: escapes to the rail | ngspice | rail latch at 3.56 ms | confirmed |

ngspice start-up note: with `uic`, the macro-model output stages overrode both the node `.ic` and the capacitor `IC=` values, so the state actually started near (−0.08, 0.04, 0.04) V. The final netlist (`spice/mkcir_bpr.py`) holds every node at a consistent operating point (`.ic` on o1..o4, r and n1..n5, no `uic`). The trace starts exactly at the mapped IC (−0.419, 0.081, 0.081) V. All three start-up methods rail-latched, so the verdict does not depend on the method.

Conclusion: the precision rectifier removes the knee problem in the C++ model (B1–B3 hold with ε ≈ 6e-7). However, the γ_rel attractor is so thin that the finite-GBW/slew TI macro-model throws the trajectory out of the basin within about 5 cycles. Step 3 (build, proof on the smooth DJ field, Falstad, schematic, breadboard, bench guide) is **not triggered**. B4 holds and B5 failed.
