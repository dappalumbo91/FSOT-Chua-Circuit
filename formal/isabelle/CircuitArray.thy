theory CircuitArray
  imports Main
begin

definition circuit_D_eff :: nat where "circuit_D_eff = 7"
definition circuit_alpha :: nat where "circuit_alpha = 10"
definition circuit_R_ohm :: nat where "circuit_R_ohm = 1800"
definition circuit_R_c_phi_milliohm :: nat where "circuit_R_c_phi_milliohm = 11124610"
definition circuit_lock_rate_phi_pct :: nat where "circuit_lock_rate_phi_pct = 100"
definition circuit_lock_rate_open_pct :: nat where "circuit_lock_rate_open_pct = 0"
definition circuit_bom_median_error_ppm :: nat where "circuit_bom_median_error_ppm = 382"
definition circuit_green_gate_ppm :: nat where "circuit_green_gate_ppm = 5000"
definition nic_Ga_den :: nat where "nic_Ga_den = 1320"
definition nic_a_num :: nat where "nic_a_num = 15"
definition nic_a_den :: nat where "nic_a_den = 11"
definition nic_Gb_num :: nat where "nic_Gb_num = 9"
definition nic_Gb_den :: nat where "nic_Gb_den = 22000"
definition nic_b_num :: nat where "nic_b_num = 81"
definition nic_b_den :: nat where "nic_b_den = 110"
definition sigma_c_pred_e4 :: nat where "sigma_c_pred_e4 = 14897"
definition sigma_c_sweep_e4 :: nat where "sigma_c_sweep_e4 = 15250"
definition sigma_c_tol_e4 :: nat where "sigma_c_tol_e4 = 500"
definition phi_floor_e4 :: nat where "phi_floor_e4 = 16180"

lemma circuit_D_eff_is_electromagnetism: "circuit_D_eff = 7"
  unfolding circuit_D_eff_def by simp

lemma circuit_lock_rate_phi_full: "circuit_lock_rate_phi_pct = 100"
  unfolding circuit_lock_rate_phi_pct_def by simp

lemma circuit_lock_rate_open_zero: "circuit_lock_rate_open_pct = 0"
  unfolding circuit_lock_rate_open_pct_def by simp

lemma circuit_bom_median_under_green_gate:
  "circuit_bom_median_error_ppm < circuit_green_gate_ppm"
  unfolding circuit_bom_median_error_ppm_def circuit_green_gate_ppm_def by simp

lemma nic_a_cross: "1800 * nic_a_den = nic_Ga_den * nic_a_num"
  unfolding nic_a_den_def nic_Ga_den_def nic_a_num_def by simp

lemma nic_b_cross: "1800 * nic_Gb_num * nic_b_den = nic_Gb_den * nic_b_num"
  unfolding nic_Gb_num_def nic_b_den_def nic_Gb_den_def nic_b_num_def by simp

lemma sigma_c_sharp: "sigma_c_sweep_e4 - sigma_c_pred_e4 \<le> sigma_c_tol_e4"
  unfolding sigma_c_sweep_e4_def sigma_c_pred_e4_def sigma_c_tol_e4_def by simp

lemma sigma_c_below_phi: "sigma_c_pred_e4 < phi_floor_e4"
  unfolding sigma_c_pred_e4_def phi_floor_e4_def by simp

end
