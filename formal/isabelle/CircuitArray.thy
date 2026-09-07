theory CircuitArray
  imports Main
begin

definition circuit_D_eff :: nat where "circuit_D_eff = 9"
definition circuit_alpha :: nat where "circuit_alpha = 10"
definition circuit_R_ohm :: nat where "circuit_R_ohm = 1800"
definition circuit_R_c_phi_milliohm :: nat where "circuit_R_c_phi_milliohm = 11124610"
definition circuit_lock_rate_phi_pct :: nat where "circuit_lock_rate_phi_pct = 100"
definition circuit_lock_rate_open_pct :: nat where "circuit_lock_rate_open_pct = 0"
definition circuit_bom_median_error_ppm :: nat where "circuit_bom_median_error_ppm = 208"
definition circuit_green_gate_ppm :: nat where "circuit_green_gate_ppm = 5000"
definition nic_Ga_den :: nat where "nic_Ga_den = 1320"
definition nic_a_num :: nat where "nic_a_num = 15"
definition nic_a_den :: nat where "nic_a_den = 11"

lemma circuit_D_eff_is_electromagnetism: "circuit_D_eff = 9"
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

end
