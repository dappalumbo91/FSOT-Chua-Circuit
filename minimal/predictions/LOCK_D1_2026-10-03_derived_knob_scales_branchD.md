# LOCK D1: FSOT-derived knob, scales and Branch D model (locked BEFORE any new simulation)

Date: 2026-10-03. M1, M2 and J stay intact. This lock uses only existing FSOT results listed in ../REPO_SURVEY.md.

## D1.1 Knob A (genuine, derived without reference to the chaos band)
In units of τ0, the jerk term A·x'' is a linear relaxation (damping) rate. The only FSOT quantity already applied in hardware as a relaxation rate per unit time scale is the transport-law coefficient
γ_rel = 0.42804344605980688 (fsot-law-circuit/docs/DESIGN.md:33, results/design.json:3, from fsot_dynamics.py).
**Branch K: A = γ_rel = 0.428043.** This gives R_A = R/γ_rel = 1800/0.428043 = **4205.2 Ω** (nearest E96 value: 4.22 kΩ, A = 0.4265).

Secondary candidate (Branch K′, Rule O, the free-running unobserved node): A = |S_med| ≈ 0.656 (DESIGN.md:29), so R_A ≈ 2744 Ω.

Disclosure: both candidates were chosen after the chaos band [0.547, 0.6405] (ideal) and ngspice edge ≈ 3.07 kΩ were already known. They were chosen on the physical-role argument above, not to fit the band. Neither value lies inside a known chaotic band.

## D1.2 Scales τ0 and U_eff (no FSOT prediction claimed)
Following the fsot-law-circuit precedent (DESIGN.md:19-20, "engineering voltage scale; cancels from every dimensionless prediction"), τ0 = R·C = 1.8 kΩ·100 nF = 180 µs and U_eff = U + V_D, with U = 9 V·R/R_c = 0.403 V, are **engineering units, not FSOT outputs**. No FSOT repo derives an absolute circuit time or voltage.

## D1.3 Branch D (diode knee): zero free parameters, standard junction physics
No FSOT treatment of junctions exists (survey §c). Branch D therefore uses the physical Shockley law with the frozen netlist model (spice/mkcir.py:9): Is = 2.52 nA, N = 1.752, Rs = 0.568 Ω, V_T = k_B T/q, and Is(T) from the standard SPICE law (XTI = 3, EG = 1.11 eV, Tnom = 27 °C).
The summer current I (in units of V/R) solves o3 = I·(Rd/R) + I·Rs/R + N·V_T·ln(1 + I/(R·Is)), and o4 = −(o2 + I). Ideal op-amps are used; outputs clip at ±7.5 V (as in oa.cpp).
Engine: src/bd.cpp (C++20, RK4).
Equations: do1 = −(A o1 + o4 + o3 + U), do2 = −o1, do3 = −o2, in units of τ0.

## D1.4 Qualitative predictions locked now (from existing data only, no new runs)
- P-K1 (genuine, blind for ngspice): at R_A = 4205 Ω and 4.22 kΩ the circuit is **NOT chaotic**. The ideal model is unbounded at A = 0.428 (results/bif_A.tsv, which shows no bounded orbit for A < 0.547), so the real circuit is expected to run into the op-amp rails or a rail-limited relaxation cycle. **This means the FSOT-derived knob is predicted not to give the chaotic bench attractor.**
- P-K′1 (genuine, blind): at R_A = 2744 Ω the circuit is periodic (ideal: A > 0.6405 is periodic).
- P-D0 (NOT blind): Branch D reproduces a downward shift of the edge to about 3.07 kΩ. This value was already known from ngspice, so it is only a consistency check.
- Numerical Branch D predictions for new blind observables (the edge at T = 0 °C and 60 °C, plus λ1, frequency and amplitude) are computed with bd.cpp after this lock. They will be locked in LOCK_D2 before any ngspice run of those observables.
