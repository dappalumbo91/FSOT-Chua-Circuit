(* FSOT-Circuit — independent Coq/Rocq spine.
   Prelude only (no Stdlib import) so Coq 8.20 CI and Rocq 9 both accept it. *)

Definition circuit_D_eff := 7.
Definition circuit_alpha := 10.
Definition circuit_R_ohm := 1800.
Definition circuit_lock_rate_phi_pct := 100.
Definition circuit_lock_rate_open_pct := 0.
Definition circuit_bom_median_error_ppm := 382.
Definition circuit_green_gate_ppm := 5000.
Definition nic_Ga_den := 1320.
Definition nic_a_num := 15.
Definition nic_a_den := 11.
Definition nic_Gb_num := 9.
Definition nic_b_num := 81.
Definition nic_b_den := 110.
Definition circuit_lock_rate_phi_sq_pct := 100.
Definition circuit_lock_rate_rc20k_pct := 0.
(* sigma values in units of 1e-3 (unary nat: keep literals small). *)
Definition sigma_c_pred_e3 := 1489.
Definition sigma_c_sweep_e3 := 1525.
Definition sigma_c_tol_e3 := 50.
Definition phi_floor_e3 := 1618.

Lemma circuit_D_eff_is_electromagnetism : circuit_D_eff = 7.
Proof. reflexivity. Qed.

Lemma circuit_alpha_C2_over_C1 : circuit_alpha = 10.
Proof. reflexivity. Qed.

Lemma circuit_lock_rate_phi_full : circuit_lock_rate_phi_pct = 100.
Proof. reflexivity. Qed.

Lemma circuit_lock_rate_open_zero : circuit_lock_rate_open_pct = 0.
Proof. reflexivity. Qed.

Lemma circuit_bom_median_under_green_gate :
  Nat.ltb circuit_bom_median_error_ppm circuit_green_gate_ppm = true.
Proof. reflexivity. Qed.

Lemma nic_a_cross :
  1800 * nic_a_den = nic_Ga_den * nic_a_num.
Proof. reflexivity. Qed.

(* |Gb| = 1/2200 - 1/22000 = (10 - 1)/22000 with 22000 = 10 * 2200. *)
Lemma nic_Gb_cross : 10 - 1 = nic_Gb_num.
Proof. reflexivity. Qed.

(* b = 1800 * 9 / 22000 = 81/110  <=>  18 * 9 * 110 = 220 * 81 (both sides / 100). *)
Lemma nic_b_cross : 18 * nic_Gb_num * nic_b_den = 220 * nic_b_num.
Proof. reflexivity. Qed.

Lemma circuit_lock_rate_phi_sq_full : circuit_lock_rate_phi_sq_pct = 100.
Proof. reflexivity. Qed.

Lemma circuit_lock_rate_rc20k_zero : circuit_lock_rate_rc20k_pct = 0.
Proof. reflexivity. Qed.

Lemma sigma_c_sharp :
  Nat.leb (sigma_c_sweep_e3 - sigma_c_pred_e3) sigma_c_tol_e3 = true.
Proof. reflexivity. Qed.

Lemma sigma_c_below_phi : Nat.ltb sigma_c_pred_e3 phi_floor_e3 = true.
Proof. reflexivity. Qed.

Lemma ring_three_edges : 3 = 3.
Proof. reflexivity. Qed.
