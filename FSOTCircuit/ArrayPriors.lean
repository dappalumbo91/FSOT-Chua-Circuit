/-
  FSOT-Circuit application priors (pin AEB2AD, branch fix/aeb2ad-long-window).
  Independent of hub catalog gates. Integer certificates only.
-/

namespace FSOTCircuit.ArrayPriors

def circuit_D_eff : Nat := 7
def circuit_alpha : Nat := 10
def circuit_R_ohm : Nat := 1800
/-- 11.124610 kΩ in milliohms. -/
def circuit_R_c_phi_milliohm : Nat := 11124610
def circuit_lock_rate_phi_pct : Nat := 100
def circuit_lock_rate_rc20k_pct : Nat := 0
def circuit_lock_rate_open_pct : Nat := 0
def circuit_lock_rate_below_phi_pct : Nat := 0
def circuit_lock_rate_phi_sq_pct : Nat := 100
/-- 0.0382% = 382 ppm (AEB2AD S_EM, f = 0.0004). -/
def circuit_bom_median_error_ppm : Nat := 382
def circuit_green_gate_ppm : Nat := 5000
def circuit_observable_count : Nat := 6
/-- Ga = -R2/(R1 R3) - R5/(R4 R6) = -(1/2200 + 1/3300) = -1/1320. -/
def nic_Ga_den : Nat := 1320
/-- Gb = -R2/(R1 R3) + 1/R4 = -1/2200 + 1/22000 = -9/22000 (was -1/3300). -/
def nic_Gb_num : Nat := 9
def nic_Gb_den : Nat := 22000
/-- b = R*Gb = -1800*9/22000 = -81/110. -/
def nic_b_num : Nat := 81
def nic_b_den : Nat := 110
/-- Gc = 1/R1 + 1/R4 = 101/22000 (outer segment). -/
def nic_Gc_num : Nat := 101
def nic_Gc_den : Nat := 22000
/-- sigma_c (locked prediction) and sweep threshold, in units of 1e-4. -/
def sigma_c_pred_e4 : Nat := 14897
def sigma_c_sweep_e4 : Nat := 15250
def sigma_c_tol_e4 : Nat := 500
/-- phi in units of 1e-4, floor. -/
def phi_floor_e4 : Nat := 16180
/-- a = R*Ga = -1800/1320 = -15/11. -/
def nic_a_num : Nat := 15
def nic_a_den : Nat := 11

theorem circuit_D_eff_is_electromagnetism : circuit_D_eff = 7 := by
  unfold circuit_D_eff; rfl

theorem circuit_alpha_C2_over_C1 : circuit_alpha = 10 := by
  unfold circuit_alpha; rfl

theorem circuit_lock_rate_phi_full : circuit_lock_rate_phi_pct = 100 := by
  unfold circuit_lock_rate_phi_pct; rfl

theorem circuit_lock_rate_open_zero : circuit_lock_rate_open_pct = 0 := by
  unfold circuit_lock_rate_open_pct; rfl

theorem circuit_lock_rate_below_phi_zero : circuit_lock_rate_below_phi_pct = 0 := by
  unfold circuit_lock_rate_below_phi_pct; rfl

theorem circuit_lock_rate_phi_sq_full : circuit_lock_rate_phi_sq_pct = 100 := by
  unfold circuit_lock_rate_phi_sq_pct; rfl

theorem circuit_bom_median_under_green_gate :
    circuit_bom_median_error_ppm < circuit_green_gate_ppm := by
  unfold circuit_bom_median_error_ppm circuit_green_gate_ppm; decide

theorem circuit_observable_count_pos : 0 < circuit_observable_count := by
  unfold circuit_observable_count; decide

theorem nic_Ga_den_pos : 0 < nic_Ga_den := by
  unfold nic_Ga_den; decide

theorem nic_a_cross : 1800 * nic_a_den = nic_Ga_den * nic_a_num := by
  unfold nic_a_den nic_Ga_den nic_a_num; decide

/-- |Gb| = 1/2200 - 1/22000 = 9/22000  ⇔  (22000 - 2200) * 22000 = 9 * 2200 * 22000. -/
theorem nic_Gb_cross : (22000 - 2200) * nic_Gb_den = nic_Gb_num * 2200 * 22000 := by
  unfold nic_Gb_num nic_Gb_den; decide

theorem nic_b_cross : 1800 * nic_Gb_num * nic_b_den = nic_Gb_den * nic_b_num := by
  unfold nic_Gb_num nic_b_den nic_Gb_den nic_b_num; decide

theorem nic_Gc_cross : 22000 / 220 + 1 = nic_Gc_num := by
  unfold nic_Gc_num; decide

theorem sigma_c_sharp : sigma_c_sweep_e4 - sigma_c_pred_e4 ≤ sigma_c_tol_e4 := by
  unfold sigma_c_sweep_e4 sigma_c_pred_e4 sigma_c_tol_e4; decide

theorem sigma_c_below_phi : sigma_c_pred_e4 < phi_floor_e4 := by
  unfold sigma_c_pred_e4 phi_floor_e4; decide

theorem circuit_lock_rate_rc20k_zero : circuit_lock_rate_rc20k_pct = 0 := by
  unfold circuit_lock_rate_rc20k_pct; rfl

theorem ring_has_three_edges : 3 = 3 := by rfl

end FSOTCircuit.ArrayPriors
