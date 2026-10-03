// fsot_chua/branch_l.hpp — FSOT-Circuit Branch L (lossy reactance), header-only, C++20.
//
// Derives the inductor-loss ratio gamma = beta * r0 / R of a Chua node from the FSOT 2.1 law
// (pin AEB2AD) without fitting. See docs/BRANCH_L_DERIVATION.md.
//
//   eps   = |S_D| * ALPHA                         Ledger B dressing amplitude, D = Electromagnetism
//   k     = sqrt((1 + eps)^2 - 1)                 |Z| = omega L (1 + eps)  and  |Z|^2 = r0^2 + (omega L)^2
//   r0    = k * sqrt(L / C2)          [ohm]       at the node's tank frequency omega_LC = 1/sqrt(L C2)
//   gamma = beta * r0 / R = k * sqrt(beta)  [-]   beta = R^2 C2 / L
//   Q_L   = 1 / k                     [-]         inductor quality factor at omega_LC
//
// Templated on the FSOT-2.1-Cpp number type R (double, long double, f128, mp169).
#pragma once
#include <string_view>

#include "fsot/engine.hpp"

namespace fsot::chua {

template <class R> struct BranchL {
  R eps, k, Q;
  // Ledger B amplitude for the component's routing domain (Electromagnetism by default).
  explicit BranchL(const Engine<R>& e, std::string_view domain = "Electromagnetism") {
    eps = m::fabs(e.domain_scalar(domain)) * e.ALPHA;
    k = m::sqrt(eps * (R(2) + eps));  // = sqrt((1+eps)^2 - 1) without cancellation
    Q = R(1) / k;
  }
  R r0_ohm(const R& L_h, const R& C2_f) const { return k * m::sqrt(L_h / C2_f); }
  R gamma(const R& R_ohm, const R& L_h, const R& C2_f) const {
    const R beta = R_ohm * R_ohm * C2_f / L_h;
    return k * m::sqrt(beta);
  }
};

// Kennedy NIC slopes from the BOM resistors (exact; see FSOT-Chua-Circuit docs/BRANCH_L_DERIVATION.md §1).
template <class R> struct KennedyNic {
  R Ga, Gb, Gc;  // siemens
  KennedyNic(R R1, R R2, R R3, R R4, R R5, R R6) {
    Ga = -R2 / (R1 * R3) - R5 / (R4 * R6);
    Gb = -R2 / (R1 * R3) + R(1) / R4;
    Gc = R(1) / R1 + R(1) / R4;
  }
};

}  // namespace fsot::chua
