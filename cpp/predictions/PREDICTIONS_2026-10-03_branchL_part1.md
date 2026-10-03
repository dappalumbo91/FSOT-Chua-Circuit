# FSOT 2.1 Branch L — locked predictions, part 1 (written 2026-10-03, before any simulation at r0_FSOT)

Authority: vendor/fsot_compute.py sha256 AEB2ADAD6E80F487772C5DF90A2E3DDA71624AB831A6A83B94AB471AC9AAC170
Circuit: Kennedy NIC Chua (R1=R2=220, R3=2200, R4=R5=22000, R6=3300 ohm), L=22 mH, C1=10 nF, C2=100 nF, R=1800 ohm.

## Branch L law (lossy reactance)
eps = |S_EM| * ALPHA                         (Ledger B dressing of an EM-domain magnitude)
|Z_L(omega_LC)| = omega_LC*L*(1+eps),  |Z|^2 = r0^2 + (omega_LC*L)^2,  omega_LC = 1/sqrt(L*C2)
k   = sqrt((1+eps)^2 - 1) = 1/Q_L
r0  = k * sqrt(L/C2)            [ohm]
gamma = beta*r0/R = k*sqrt(beta) [dimensionless], beta = R^2*C2/L

## Locked values (golden, mpmath dps 50 == C++ f128/mp169)
S_EM   = 0.955728570095582708189529865395654231210728512
eps    = 7.72509421698849555448983476053969818103600829e-4
k      = 0.039314318183129064687502566020983012073536834
Q_L    = 25.4360255045483541132418821241996762299629374
r0     = 18.4400497592861384450777864335670599961324853 ohm
gamma  = 0.150873134394159314550636434456457763604720334
(sensitivity, Materials_Science routing: r0 = 18.42007 ohm, gamma = 0.1507097)

## Locked procedure for sigma_c (value locked in part 2 before the ring sweep)
sigma_c_pred = zero crossing (linear interpolation) of the transverse Lyapunov exponent
lambda_perp(3*sigma) of the synchronous Kennedy double scroll with gamma above;
fsot_chua msf kennedy, grid 0.025, T=3000 tau, dt=0.005, IC (0.1,0,0). First sigma with lambda_perp<0
that stays negative over the next grid points.

## Gates (lock law = repo law AND tail max|x| < x2 = Bp2/Bp = 6.97, i.e. no escape to outer cycle)
Window: 2000 tau total (last 500 tau scored), 6 seeds, dt 0.005, no clip.
G1 single node at gamma_FSOT: double scroll (lambda1 > 0, both lobes visited, no escape).   PREDICT: PASS
G2 sigma = 1 (Rc = R): no lock.                                                            PREDICT: PASS
G3 Rc = 20 kOhm (sigma = 0.9): no lock, amplitude-checked.                                 PREDICT: PASS
G4 sigma = phi^2: lock (>= 5/6 seeds).                                                     PREDICT: PASS
G5 |sigma_c_pred - sigma_c_sweep| <= 0.05, sweep threshold = smallest sigma (grid 0.025) above
   which lock rate >= 5/6 for all grid points up to phi^2.                                PREDICT: PASS
G6 sigma = phi locks  iff  sigma_c_pred < phi (consistency statement, value in part 2).

## Blindness disclosure
Before deriving Branch L the author of this file had already run an r0 sweep of the same model
(r0 = 0,10,15,20,25,30,35,40,50 ohm) and knew: all gates held at 35-40 ohm; at 20-30 ohm phi locked
but the 20 kOhm case escaped; at <= 15 ohm phi failed. r0_FSOT = 18.44 ohm falls between 15 and 20,
so by interpolation G3 and/or the phi gate are AT RISK. The PASS predictions above are what the FSOT
gates claim, not a hedged forecast. The derivation was not tuned: the only alternative considered
(1/Q = eps, r0 = 0.36 ohm) was rejected on structural grounds (it dresses an ideal loss of zero),
not on simulation outcome. Using Ledger B (f = ALPHA) as a physical loss law is a NEW-BRANCH
hypothesis; the FSOT-2.1-Cpp engine comments describe Ledger B as "not a prediction".
