# FSOT 2.1 Branch L — locked predictions, part 2 (2026-10-03, before the ring sweep at r0_FSOT)

Supersedes nothing; extends part 1, sha256 04ebe3f4e2f96eb546d494b76169d456d883635631e4ac89cf9307a302b4f6f1.

Inputs: gamma_FSOT = 0.150873134394159 (r0 = 18.4400497592861 ohm), Kennedy b = -81/110, a = -15/11, c = 909/110,
alpha = 10, beta = 14.7272727..., x2 = Bp2/Bp = 6.97.
Run: FSOT_CHUA_R0=18.4400497592861384 fsot_chua msf kennedy (data: msf_r0FSOT_2026-10-03.tsv, same directory).
Single node lambda1 (fsot_chua lyap, T=3000) = 0.251832 / tau  (> 0, consistent with G1; G1 also needs lobe switching
and no escape, which is checked in the sweep).

lambda_perp(sigma=1.475) = +0.001721, lambda_perp(sigma=1.500) = -0.001210, negative for every grid point up to 3.0.

## sigma_c_pred = 1.4897  (linear interpolation; grid resolution +-0.0125)
Rc_crit = alpha*R/sigma_c = 12083 ohm (lock predicted for Rc < ~12.1 kOhm).

## G6 resolved: sigma_c_pred (1.4897) < phi (1.6180) -> PREDICT sigma = phi LOCKS (but with a small margin,
lambda_perp(phi) = -0.0159 / tau, sync time ~ 1/0.016 ~ 60 tau, so it must lock inside the 2000 tau window).
G5: PREDICT the 2000 tau sweep threshold lies in [1.44, 1.54].
