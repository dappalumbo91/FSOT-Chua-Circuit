# LOCK J: Branch J, an attempt to DERIVE the jerk damping A from FSOT-2.1 (independent of 1/phi). Side task, labelled.
Date: 2026-10-03 ~08:20 ET. M1/M2 are untouched.
Disclosure: the ideal chaos range A in [0.547, 0.6405] (with windows, and a hairline window at 0.6182) is ALREADY known from the M2 runs.
So this lock fixes the derivation rules and their values before they are compared with that known range; it cannot be a blind test.
Rule for choosing candidates: only reuse FSOT laws that already have a physical reading in this repo (no scanning of constants).

J1 (Branch L law applied to the damping path): the jerk-damping term A·x'' is the loss of the second integrator loop, read as a lossy reactance with
    Q = 1/k, where k = sqrt((1 + |S_EM|·ALPHA)^2 - 1) = 0.0393143 (ALPHA = ln(pi)/(e·phi^13), S_EM = 0.9557286).   => A_J1 = k = 0.0393143.
J2 (the validated Chua-node loss ratio reused as the dimensionless damping): A_J2 = gamma = k·sqrt(beta) = 0.1508731.
tau0 (derived, not hypothesised): tau0 = R C, with R and C the FSOT Chua-node BOM values (R = 1.8 kOhm, C2 = 100 nF) -> 180 us. This is inherited from FREEZE, not new physics.
U_eff: Bp1 = Esat·R6/(R5+R6)... = 1.000 V (FREEZE nic.Esat_V = 23/3, Bp1 = 1 V), inherited.
Predictions: J1 and J2 each predict a chaotic attractor at their A value (i.e. A inside [0.547, 0.6405]).
