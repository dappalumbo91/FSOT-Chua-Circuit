# LOCK PJ and LOCK PC scorecards, plus the Path J vs Path C comparison

## LOCK PJ (`predictions/LOCK_PJ_2026-10-03_xprime_and_slope_gains.md`, sha256 7524bad0a822198bc8444ab9e5c08dd21d2c2e45ee45773ac74ae7e78352c4f8)
- Locked before any simulation of the 49 candidates. All predictions are genuine.
- The lock also records that LOCK T's F1 theorem ("depends only on γ/√B") was wrong: there are two essential parameters, (γ/√B, G/B^{3/2}).
- **Selection (C++ `pathj/pj scan`, `pathj/scan.tsv`):** winner **B = Θ = 0.91751, G = κ/γ_rel = 0.73505**, with 43/64 chaotic seeds. Runner-up: B = S_EM, G = κ/γ_rel, with 42/64. All other 47 candidates have 0 chaotic seeds.

| ID | Prediction | Result | Verdict |
|---|---|---|---|
| PJ1 | Winner in the χ band; ≥ 3/4 in-band candidates chaotic | winner χ = 0.534 is just outside [0.547, 0.6405]; only 1/4 in-band candidates is chaotic | **falsified** |
| PJ2 | Winner basin ≥ 8/64 | 43/64 | confirmed |
| PJ3 | λ1 ∈ [0.015, 0.08]/τ0 | 0.0648 (median of the chaotic seeds; 0.0667 from the attractor point) | confirmed |
| PJ4 | f = f₋ of the winner's row ±15 % | 822.2 Hz vs 914.8 Hz (−10.1 %) | confirmed |
| PJ5 | xmin/|x₋| ∈ [−3, −1.5], xmax/|x₋| ∈ [0.8, 2] | −2.545, 1.516 | confirmed |
| PJ6 | ngspice TI TL082 from the attractor point: bounded and chaotic over 0.6 s | 110 distinct maxima, o3 ∈ [−1.397, 0.837] V (= x ∈ [−3.47, 2.08]·U, matching C++), 822 Hz | confirmed |
| PJ7 | ngspice default start V(o3) = −0.3 V reaches the attractor | 108 distinct maxima, same range, 818 Hz | confirmed |
| PJ8 | ±1 % on γ, B, G: ≥ 26/32 chaotic | 29/32 | confirmed |

Extra, not locked: with E96 values (4.22k, 1.96k, 2.43k, 1.21k) the ngspice run is still chaotic from both starts (89 and 93 distinct maxima, 798 Hz).

## LOCK PC (`predictions/LOCK_PC_2026-10-03_branchL_minimal_chua.md`, sha256 67274bb1a765c7b40ad5976f5fafed20a8e1c8defce0ec9289f01201e89b484f)
| ID | Prediction | Type | Result | Verdict |
|---|---|---|---|---|
| PC1 | ≥ 48/64 seeds on the double scroll | genuine | 34/64. The other 30 go to a coexisting outer limit cycle (max|x| = 7.35) | **falsified** |
| PC2 | λ1 = 0.245/τ ±10 % | replication | 0.2448 | confirmed |
| PC3 | f ≈ 2678 Hz ±15 % | genuine (analytic) | C++ 2547 Hz (−4.9 %); ngspice 2564 Hz | confirmed |
| PC4 | max|x| = 4.33 ±5 % | replication | 4.3251 | confirmed |
| PC5 | ngspice TL082 double scroll, no rail latch | replication | 149/154 distinct maxima, ±4.27 V (9.19 V rails) and ±4.16 V (9.0 V rails) | confirmed |
| PC6 | Tolerance ≥ 58/64 | genuine | 61/64 | confirmed |
| PC7 | Proof attempt | n/a | not reached (see below) | — |

## Comparison
| | Path J (B = Θ, G = κ/γ_rel jerk) | Path C (Kennedy–Chua, Branch L r0) |
|---|---|---|
| Parts | 2 ICs (TL074 + TL072), 2 × 1N4148, 12 R, 3 C (19, plus decoupling) | 1 IC (TL082), 8 R (incl. R_add), 2 C, 1 L (12, plus decoupling) |
| Nonlinear elements | 2 diodes inside an op-amp loop (precision \|x\|) | 2 op-amp saturations (5-segment NIC); no diodes |
| Basin (C++) | 43/64 random starts chaotic; the rest diverge | 34/64 double scroll; the rest go to a coexisting outer limit cycle |
| Start from rest | reaches the attractor (ngspice, V(o3) = −0.3 V) | reaches the double scroll (C++ and ngspice) |
| ngspice survival (TI TL082) | yes, 0.6 s, both starts; E96 also yes | yes, 0.1 s, ±9.0 and ±9.19 V rails |
| Tolerance | 29/32 at ±1 % on γ, B, G | 61/64 at the acceptance spec |
| λ1 | 0.065/τ0 (τ0 = 180 µs) | 0.245/τ (τ = 180 µs) |
| FSOT content | γ_rel, Θ and κ/γ_rel all FSOT; no knob; chosen by a locked rule | r0 and γ from Branch L; the rest of the BOM is the classic Kennedy design |
| Proof status | not reached: the generalised checker `proof/horseshoe_bg.cpp` reproduces the old map at B = G = 1, but the first P¹ h-sets failed (curved images) | not reached: needs a 3-region crossing engine (boundaries x = ±1); not built this pass |
| Bench cost | all jellybean parts (two quad/dual op-amps, small-signal diodes, 1 % resistors, film caps); no inductor | jellybean parts plus a 22 mH inductor, and r0 must be trimmed to ±0.33 Ω. No prices were looked up |
| Hardest bench step | 4 non-standard E96 resistors (all stock values) | hitting r0 = 18.44 ± 0.33 Ω (coil DCR plus R_add) |

**Both validate.** Path C is more robust: larger λ1, a long validated history, fewer parts, and ngspice/Falstad already confirmed.
- Its weak point is the coexisting outer cycle, but power-on reaches the double scroll.
- Path J is the more FSOT-pure design (every coefficient FSOT, no inductor, no r0 trim), and it is the first jerk design to survive ngspice with TI models.
