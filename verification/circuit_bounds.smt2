; FSOT Circuit array — SMT bounds (Z3 / CVC5). Linear arithmetic only.
; Frozen numbers from results/sim_report.json (pin D1D38A).

(set-logic QF_LRA)

(declare-const phi Real)
(declare-const Rc Real)
(declare-const bom_residual_pct Real)
(declare-const lock_rate_phi Real)
(declare-const lock_rate_open Real)

(assert (= phi 1.618033988749895))
(assert (= Rc 11124.611797498106))
(assert (= bom_residual_pct 0.020754620831932584))
(assert (= lock_rate_phi 1.0))
(assert (= lock_rate_open 0.0))

(assert (> phi 1.6))
(assert (< phi 1.62))
(assert (> Rc 11100.0))
(assert (< Rc 11150.0))
(assert (< bom_residual_pct 0.5))
(assert (>= bom_residual_pct 0.0))
(assert (= lock_rate_phi 1.0))
(assert (= lock_rate_open 0.0))

(check-sat)
(get-value (phi Rc bom_residual_pct lock_rate_phi))
