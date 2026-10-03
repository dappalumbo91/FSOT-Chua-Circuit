# LOCK DJ: Branch DJ (FSOT junction physics). Locked before digitising any datasheet curve or running any simulation

## Derivation (new branch; inputs: FSOT-2.1 S_EM and SI constants)
- **Thermal-voltage role:** V_T = k_B T/q, the SI Boltzmann factor. FSOT adds nothing here, and the branch keeps it unchanged.
- **Ideality:** n = 1 + S_EM, where S_EM = 0.9557285700955828 (FREEZE.yaml; FSOT-2.1 Electromagnetism scalar, FSOT-2.1-Cpp include/fsot/engine.hpp:160). So **n = 1.955729**.
  - Physical reading: the forward current is diffusion injection (n = 1, the Shockley limit) plus an EM-mediated recombination channel (n = 2, the Sah–Noyce–Shockley limit). Its weight is the FSOT EM coupling S_EM.
  - The limits are correct: S_EM → 0 gives ideal Shockley, and S_EM → 1 gives pure recombination.
- **Saturation-current scaling:** I_s(T) ∝ T^(3/n) · exp(−E_g/(n k_B T)). The diffusion part ∝ n_i² and the recombination part ∝ n_i, interpolated by the same n. E_g(Si) = 1.12 eV is a measured material constant and is not an FSOT output.
- **Not derivable:** the absolute I_s, because it needs junction area and doping, which FSOT does not supply. Series resistance R_s is not derived either. So DJ predicts **differences and slopes, not absolute V_f**.
- **Disclosure:**
  - The SPICE N = 1.752 for the 1N4148 and the textbook range 1 ≤ n ≤ 2 were known when the rule was written.
  - The Vishay Fig. 1 plot was *viewed* (page render) before this lock but **not digitised**.
  - The rule n = 1 + S_EM was fixed before the view.

## Real observables (scored after this lock)
- Vishay 1N4148 datasheet, Rev. 1.6, 07-Nov-2024: https://www.vishay.com/docs/81857/1n4148.pdf, sha256 aefe85400a427ed886a4e1c88205ceabb9f9b38044b29c6acee4bb00146a44b7. Fig. 1 gives typical V_F vs T_j at I_F = 0.1, 1, 10 and 100 mA.
- Diodes Inc BAV16W/1N4148W datasheet (ds30086): https://www.diodes.com/assets/Datasheets/ds30086.pdf, sha256 39c16a6888bdab22418e93e17182174aad763a66957a4632e70c944194e3fc08. Maximum V_F: 0.715 V at 1 mA, 0.855 V at 10 mA, 1.0 V at 50 mA, 1.25 V at 150 mA.

## Predictions (25 °C)
| ID | observable | DJ prediction | pass band |
|---|---|---|---|
| DJ1 | V_F(10 mA) − V_F(1 mA), Vishay Fig. 1 typical | n V_T ln10 = **0.11570 V** | ±10 % ([0.1041, 0.1273]) |
| DJ2 | V_F(100 mA) − V_F(10 mA), Vishay typical | 0.11570 V (DJ has no R_s, so this should be exceeded) | ±10 % (expected to FAIL if R_s matters) |
| DJ3 | V_F(1 mA) − V_F(0.1 mA), Vishay typical | 0.11570 V | ±10 % |
| DJ4 | the tempco gets less negative per decade of current: d(dV_F/dT)/d log10 I | +n k ln10 / q = **+0.388 mV/K per decade** | ±25 % |
| DJ5 | tempco at 1 mA, given the measured V_F(1 mA, 25 °C) (conditional) | (V_F − E_g/q − 3 V_T)/T | ±20 % |
| DJ6 | Diodes Inc max-spec decade 1 → 10 mA (secondary; maximum limits, not typical) | 0.1157 V | ±20 % |
| DJ-K | jerk knob with DJ: A = R/R_A is still γ_rel. DJ only changes the knee softness (nV_T = 50.25 mV vs SPICE 45.3 mV) | R/γ_rel = 4205 Ω stays outside the chaos band (rail latch). DJ cannot reach chaos because the band edge is at A ≈ 0.58 | bd.cpp with N = 1.955729 (I_s held at the netlist value, disclosed): rail latch at 4205 Ω |
