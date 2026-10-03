# LOCK M1: FSOT minimal chaotic circuit, analytic predictions (written BEFORE any time-domain simulation)
Date: 2026-10-03, ~08:20 ET. Author pipeline: executor agent for Damian Arthur Palumbo. Authority: FSOT-2.1 pin AEB2AD (FREEZE.yaml).

## System (piecewise-linear jerk; Sprott/Linz class; one nonlinearity = one 1N4148 + resistor)
Dimensionless (time unit tau0, voltage unit U_eff):  x''' = -A x'' - x' + |x| - 1.
Circuit realisation (TL074 quad + 1 diode): |x| = 2 max(x,0) - x, so x''' = -A x'' - x' - x + 2 max(x - Vd, 0) - U.
Shifting x by Vd gives exactly the system above with U_eff = U + Vd. The diode drop only rescales voltage, NOT the dynamics (the PWL system is homogeneous in (x, U)).
=> The ONLY bifurcation parameter is A = R / R_A.

## FSOT content (zero free parameters)
- **Branch J (NEW, unvalidated hypothesis): golden damping.** A = 1/phi = 0.6180340, i.e. R_A = phi * R.
  Physical meaning: the jerk-damping path time constant R_A C is phi times the loop time constant R C. It is the same phi that sets the FSOT ring gates (sigma = phi, phi^2).
  This is a hypothesis, not a derivation from S_EM; it is falsifiable below.
- Time scale inherited from the FSOT Chua node BOM: tau0 = R C = 1800 ohm * 100 nF = 180 us (the R, C2 of FREEZE.yaml).
- Voltage unit inherited: U_eff = Bp1 = 1 V (FREEZE: Esat 23/3 V, Bp1 = 1 V). With +9 V rail feed: U = U_eff - Vd, R_c = R * 9 V / U.
- Branch L (r0, gamma) does NOT apply: this circuit has no inductor. Stated honestly; nothing borrowed from it.

## Locked analytic predictions (from the characteristic polynomials only)
P1 Equilibria: E+ = +1, E- = -1 (units U_eff).
P2 E+ (x>0): lambda^3 + A lambda^2 + lambda - 1: eigenvalues 0.58620, -0.60211 +- 1.15904 i, a saddle-focus (1D unstable, 2D stable).
   Shilnikov ratio there: |Re_s| / lambda_u = 1.0272 > 1, so the Shilnikov condition FAILS at E+.
P3 E- (x<0): lambda^3 + A lambda^2 + lambda + 1: eigenvalues -0.84162, +0.11180 +- 1.08429 i, a saddle-focus (2D unstable focus, 1D stable).
   Shilnikov ratio: Re_u / |lambda_s| = 0.1328 < 1, so the Shilnikov saddle-focus condition HOLDS at E-.
   Chaos is proven (countably many horseshoes) at any A where a homoclinic orbit to E- exists (route: find A* numerically, then a computer-assisted/interval check).
P4 Divergence = -A, so the Lyapunov spectrum sums to exactly -0.61803/tau0; lambda2 = 0 (flow).
P5 Dominant frequency ~ Im(E-) / (2 pi tau0) = 1.08429 / (2 pi * 180 us) = 958.7 Hz, band +-12 % (843–1074 Hz).
P6 (GENUINE, risky) A = 1/phi lies inside a chaotic interval: lambda1 > 0.005/tau0 for at least 4 ICs on A in {0.613, 0.618, 0.623}.
P7 (literature-informed, NOT genuine) lambda1(A = 1/phi) in [0.02, 0.07]/tau0, because Sprott reports lambda1 ~ 0.036 at A = 0.6.
P8 (loose) the attractor encircles E- = -1 V, with x spanning negative values beyond -1 and positive excursions below +3: max|x| in [2, 8] V; the bench V_x is single-sided-heavy (asymmetric attractor).
A bench knob threshold and the TL07x full-op-amp effect are locked separately in LOCK M2, before any SPICE or op-amp-model run.
