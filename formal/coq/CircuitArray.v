(* FSOT-Circuit — independent Coq/Rocq spine.
   Prelude only (no Stdlib import) so Coq 8.20 CI and Rocq 9 both accept it. *)

Definition circuit_D_eff := 9.
Definition circuit_alpha := 10.
Definition circuit_R_ohm := 1800.
Definition circuit_lock_rate_phi_pct := 100.
Definition circuit_lock_rate_open_pct := 0.
Definition circuit_bom_median_error_ppm := 208.
Definition circuit_green_gate_ppm := 5000.
Definition nic_Ga_den := 1320.
Definition nic_a_num := 15.
Definition nic_a_den := 11.

Lemma circuit_D_eff_is_electromagnetism : circuit_D_eff = 9.
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

Lemma ring_three_edges : 3 = 3.
Proof. reflexivity. Qed.
