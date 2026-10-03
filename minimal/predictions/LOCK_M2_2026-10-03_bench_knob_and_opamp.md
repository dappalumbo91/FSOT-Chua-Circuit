# LOCK M2: bench knob threshold and TL07x effect (written after the ideal C++ runs, BEFORE any SPICE, full-op-amp-model or Falstad run)
Date: 2026-10-03 ET. Inputs: ideal C++ engine (src/mj.cpp) results/bif_A.tsv, bif_A_fine.tsv, LE at A = 1/phi.
Scoring of LOCK M1 (078343de…): P1–P4 hold (sum of LEs −0.61803 = −A exactly; λ2 ≈ 0); P5 864 Hz inside the 843–1074 band (−9.9 %);
P6 holds (λ1 = 0.044–0.051 at 0.613/0.618/0.623); P7 0.048 inside [0.02, 0.07]; P8 holds (x in [−2.445, +1.186]).
The Shilnikov route is NOT available: the 1D stable manifold of E− escapes to −∞ in backward time for every A in [0.3, 1.2] (results/homo_Eminus.tsv), and E+ fails the ratio test.
A rigorous proof must use a computer-assisted (interval) horseshoe / covering relation instead.

## Ideal-model facts (C++, 4 ICs, T = 5000–10000 τ0)
- Chaos for A in [0.547, 0.640], with periodic windows at 0.5486–0.564, 0.585–0.599, 0.6136–0.6140, 0.6182 (hair-thin), 0.6254, 0.6314–0.6328, 0.636–0.6394.
- Unbounded below A ≈ 0.547 (the bench output rails). Periodic above 0.640.
- At A = 1/phi: λ1 = 0.048/τ0 = 267 /s; f = 0.1555/τ0 = 864 Hz; V_x in [−2.45, +1.19] × U_eff.

## Locked bench predictions (TL074, R = 1.80 kΩ, C = 100 nF, R_A = phi·R = 2.912 kΩ)
B1 Knob: replace R_A by 2.7 kΩ + 1 kΩ trimmer. Coming down from high R_A (low A), the attractor rails (escape) at R_A > 3.29 kΩ, is chaotic between,
   and the **upper chaos edge (period-doubling to a limit cycle) is at R_A,c = R/0.640 = 2.812 kΩ, 95 % band [2.64, 2.98] kΩ**
   (A = R C/(R_A C1); RSS of 1 % R, 1 % R_A, 2 % C1/C plus coefficient mismatch, ×2 → ±6 %).
B2 At the nominal R_A = 2.912 kΩ: f = 864 Hz ± 3 % (C tolerance), λ1 = 267 /s ± 15 %, V_x min = −2.45 U_eff, max = +1.19 U_eff,
   U_eff = U + Vd with U = 9 V·R/R_c. With R_c = 40.2 kΩ (U = 0.403 V) and Vd(1N4148, ~0.1–1 mA) = 0.55–0.65 V: U_eff = 0.95–1.05 V.
B3 TL074 full op-amp model (GBW 3 MHz, SR 13 V/µs, rails ±(9 − 1.5) V): the shift of the upper chaos edge is |ΔA_c| ≤ 0.005 (≤ 0.8 %),
   f shifts ≤ 1 %, and λ1 stays within ±15 % at A = 1/phi.
   Reason: integrator ε = 1/(2π·GBW·τ0) = 2.9e-4 and the slew demand max|dV/dt| ≈ 2.5 V·2π·864 Hz = 0.014 V/µs ≪ 13 V/µs. This is a genuine prediction; the full model decides.
B4 ngspice (TI TL074 macro-model + 1N4148 Shockley model) reproduces chaos at R_A = 2.912 kΩ (positive λ1 from the time series, or a broadband spectrum) and an upper chaos edge inside the B1 band.
