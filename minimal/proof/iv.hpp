// Minimal rigorous interval arithmetic: every op is computed in round-to-nearest, then the bounds are widened outward by one ulp (nextafter).
// IEEE-754 +,-,*,/ are correctly rounded, so the true result always lies inside. No libm transcendental calls are used.
#pragma once
#include <cmath>
#include <algorithm>
#include <limits>
struct I {
  double lo, hi;
  I(double a = 0) : lo(a), hi(a) {}
  I(double a, double b) : lo(a), hi(b) {}
  static double dn(double x) { return std::nextafter(x, -std::numeric_limits<double>::infinity()); }
  static double up(double x) { return std::nextafter(x, std::numeric_limits<double>::infinity()); }
  double mid() const { return 0.5 * (lo + hi); }
  double wid() const { return hi - lo; }
  double mag() const { return std::max(std::fabs(lo), std::fabs(hi)); }
  bool contains0() const { return lo <= 0 && hi >= 0; }
};
inline I operator+(I a, I b) { return {I::dn(a.lo + b.lo), I::up(a.hi + b.hi)}; }
inline I operator-(I a, I b) { return {I::dn(a.lo - b.hi), I::up(a.hi - b.lo)}; }
inline I operator-(I a) { return {-a.hi, -a.lo}; }
inline I operator*(I a, I b) {
  double p[4] = {a.lo * b.lo, a.lo * b.hi, a.hi * b.lo, a.hi * b.hi};
  return {I::dn(*std::min_element(p, p + 4)), I::up(*std::max_element(p, p + 4))};
}
inline I operator/(I a, I b) {  // requires 0 not in b
  double p[4] = {a.lo / b.lo, a.lo / b.hi, a.hi / b.lo, a.hi / b.hi};
  return {I::dn(*std::min_element(p, p + 4)), I::up(*std::max_element(p, p + 4))};
}
inline I hull(I a, I b) { return {std::min(a.lo, b.lo), std::max(a.hi, b.hi)}; }
