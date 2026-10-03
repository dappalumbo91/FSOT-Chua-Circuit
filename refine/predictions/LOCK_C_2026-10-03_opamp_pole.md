# LOCK C — op-amp correction to sigma_c (Target 1)   locked 2026-10-03 02:13 ET
Locked BEFORE reading any results/opamp/*.txt other than ideal_r0.txt and ideal_r18.txt (ideal baselines only).

## Derivation (FSOT-dressed pole -> effective C1)
Single-pole op-amp: u_i' = (G_i x - u_i)/eps_i, eps_i = G_i/(2 pi GBW tau0), tau0 = R C2 = 180 us.
Adiabatic elimination (eps << 1): u_i = G_i x - eps_i G_i x'. Then h = h0(x) + K x' with
K = g1 G1 eps1 + p_in g2 G2 eps2  (outer NIC always linear; inner NIC only linear for |x|<1, p_in = 0.056 from LOCK B).
x' (1 + alpha K) = alpha (y - x - h0) + sigma*cpl  =>  alpha' = alpha/(1+alpha K) AND sigma' = sigma/(1+alpha K).
Physically: the finite-GBW pole adds an effective capacitance dC1/C1 = alpha K across C1.
With the locked alpha-elasticity e_alpha = +2.44 (sigma_c ~ alpha^2.44 locally):
    Delta sigma_c / sigma_c  =  -(e_alpha - 1) * delta,   delta = alpha K / (1 + alpha K)
Units: eps, K, delta dimensionless; GBW in Hz, tau0 in s. Parameter-free (datasheet GBW: TL082 3 MHz typ [TI], TL08xH 5.25 MHz; uA741 1 MHz).
Slew rate is NOT in the formula (TL082 SRn = 1440/tau0 >> |G2 x'|; 741 SRn = 90/tau0 is marginal, so 741 k=1 is a lower bound on |Delta|).
Ledger-B GBW dressing (eps -> eps(1 - |S_EM| ALPHA), |S_EM| ALPHA = 7.725e-4): changes Delta by < 0.01% of itself -> 0.0000.

## Locked predictions (baseline: ideal 5-dim model at r0 = 18.44 ohm, sigma_c = 1.49702, T = 3000, 4 ICs)
| case | delta | Delta sigma_c / sigma_c | Delta sigma_c @ r0 18.44 | sigma_c |
|---|---|---|---|---|
| TL082 3 MHz / 8 V/us | 0.02910 | -0.0419 | -0.0627 | 1.4343 |
| TL08xH 5.25 MHz / 20 V/us | 0.01684 | -0.0243 | -0.0363 | 1.4607 |
| uA741 1 MHz (k=1, lag only) | 0.0825 | -0.1188 | -0.1778 | 1.3192 (upper bound; slew lowers further) |
| uA741 k=10 (C x10) | 0.00891 | -0.0128 | -0.0192 | 1.4778 |
| Branch N (FSOT NIC delay tau_N = r0 C2, e_add = 0.010244) | 0.481 | formula out of range | < -0.3 or loss of synchronisable double scroll | — |
For other r0 the same fraction applies (assumes e_alpha ~ 2.44 there; flagged assumption).
Tolerance for "match": |predicted - simulated Delta| <= 0.015 (TL082) / 0.04 (741 k=1).

## Disclosure / labels
- vs rf 5-dim C++ runs (results/opamp, not yet read): GENUINE.
- vs SPICE TI-model sigma_c (1.45,1.475] and eb C++ single-pole (1.44,1.46] / (1.46,1.48]: POST-HOC (known before this lock).
- This correction is standard circuit physics; the FSOT content is only the "dressed pole" reading and the Branch N proposal.
