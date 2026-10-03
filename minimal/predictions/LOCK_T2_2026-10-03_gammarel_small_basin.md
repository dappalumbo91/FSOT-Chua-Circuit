# LOCK T2: small-basin attractor at the FSOT knob A = γ_rel. Discovered post-hoc; downstream predictions locked before testing

## What was seen (post-hoc, disclosed)
- Candidate A-c, x''' = −γ_rel x'' − x' + 1 − |x|, was not predicted by LOCK T (T6). It came out bounded with λ1 ≈ 0.015/τ0 in 1 of 4 initial conditions (topo/tj_all.txt), and stayed so over 30 000 τ0.
- A-c is exactly the canonical minimal jerk x''' = −A x'' − x' + |x| − 1 under x → −x. So **the existing board at A = R/R_A = γ_rel (R_A = 4205 Ω) has a chaotic attractor in the ideal model, with a small basin.**
- The earlier statement "unbounded for A < 0.547" (results/bif_A.tsv) was incomplete: it used only 4 initial conditions.
- SciPy cross-check (rtol 1e-10, initial condition (−1.04, −0.2, 0.2), 6000 τ0): bounded, x ∈ [−2.339, 1.448].
- Poincaré section x = 0 (upward): two thin bands at y = x' ∈ [1.9113, 1.9149] ∪ [1.9190, 1.9269], mean return time 13.62 τ0. The two-return map on the left band is unimodal.
- LOCK T's winner S-a was **falsified** (unbounded for all initial conditions), so the selection rule produced no working design. Selecting the γ_rel attractor is a post-hoc pick and is labelled as such.

## Predictions, locked before running
| ID | prediction | band |
|---|---|---|
| T2-1 | ideal C++ (topo/tj) from 8 initial conditions within 0.02 of the point (x, x', x'') = (−1.04, −0.2, 0.2): ≥ 6 stay bounded with λ1 > 0.005/τ0 | as stated |
| T2-2 | Lyapunov sum = −γ_rel (identity) | ±0.005 |
| T2-3 | dominant frequency of x ≈ 1/(13.62 τ0 / 2) per crossing pair → about 0.147/τ0 = **816 Hz** at τ0 = 180 µs (two loops per 2-band cycle) | ±10 % |
| T2-4 | Branch D (bd.cpp, real 1N4148) at R_A = 4205 Ω, started on the image of the ideal attractor: bounded and chaotic. Reason: Branch D shifted the canonical band edge by only about −0.05 in A | λ1 > 0.005/τ0, no rail |
| T2-5 | ngspice (TI TL082 + 1N4148) at R_A = 4205 Ω with the same mapped initial condition: chaotic (> 40 distinct maxima) | as stated |
| T2-6 | from the old initial condition (V(o3) = −0.5 V) the circuit still rail-latches. This was already seen, so it is NOT blind | |
