# FSOT refinement predictions — locked 2026-10-03 (ET) BEFORE any comparison

Locked before any ring/basin simulation at these r0 values and before any hardware measurement.
The only FSOT input is the vendored FSOT 2.1 authority (sim/fsot_engine.py, pinned): S_EM = 0.9557285700955828,
S_MS (Materials_Science) = 0.9536594523121079, ALPHA = 0.0008082937414140405. Circuit: Kennedy BOM, L = 22 mH, C2 = 100 nF,
C1 = 10 nF, R = 1800 ohm. sigma = alpha R / Rc, so Rc* = 18000 ohm / sigma_c.
Procedure for every sigma_c below: MSF of the 3-ring transverse mode (Laplacian eigenvalue 3), eb msf, RK4 dt = 0.005,
T = 10000 tau, transient 200 tau, 8 ICs (IC 0 canonical), quadratic root per IC. Value = mean ± SD over ICs.

| id | refinement | r0 (ohm) | gamma | sigma_c (MSF) | Rc* (ohm) | status |
|---|---|---|---|---|---|---|
| P0 | Branch L baseline (already locked 04ebe3f4…, d6bd17be…) | 18.4400497592861 | 0.150873134394 | 1.4897 | 12083 | genuine (locked earlier) |
| P1 | Branch L′: composed dressing eps = (abs(S_EM)+abs(S_MS))·ALPHA, k = sqrt((1+eps)^2-1) = 0.0555794448961 | 26.0690704262999823 | 0.2132923943970 | 1.2395 ± 0.0035 | 14522 | genuine as a FORM (proposed before this sweep); the choice of Materials_Science as the second domain is a modelling choice, not forced by FSOT |
| P2 | Frequency-dependent dressing: abs(Z(omega)) = (1+eps)·omega·L, so r0(f) = k·2πf·L, f = self-consistent scroll-rotation frequency (zero-crossing rate of vC2) on the isolated attractor; fixed point f = 2551 Hz | 13.87 (± 0.03 from the iteration) | 0.1135 | 1.7002 ± 0.0069 | 10587 | POST-HOC: proposed after seeing that the measured ring threshold sits above the MSF value (direction known). The alternative weighting (rms frequency of the i_L spectrum) has NO fixed point (iterates 9.4 ↔ 10.7 ohm, a periodic window near r = 10 ohm), so the procedure is not unique |
| P3 | Op-amp Esat (ideal, symmetric) | — | — | identical to P0 (exact) | — | genuine, algebraic: x2 = (R3/(R2+R3))·(R5+R6)/R6 has no Esat; Esat only rescales voltage |

Hardware reading: a bench with an inductor whose effective series resistance at the operating band equals the listed r0 should show the ring
lock threshold near Rc* × (1.4897/1.525) (that factor is the in-model MSF→ring gap measured at P0; transferring it to P1/P2 is an assumption).
In-model, r0 refinements change BOTH the MSF prediction and the simulated ring threshold, so they cannot explain the in-model 0.035 gap.
They only matter when compared with hardware.
