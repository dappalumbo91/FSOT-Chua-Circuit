// fsot_chua_nonideal.cpp — dimensional Kennedy-Chua ring with Tinkercad-relevant non-idealities (C++20).
// Each NIC op-amp is a single-pole 741 model (A0, GBW, slew SR, rails +/-Esat); inductor (or gyrator)
// has series resistance r0; optional ADC bias loading (Thevenin Rth to Vth); time scaling k (C1,C2,L x k).
// Usage: fsot_chua_nonideal <k> <GBW_Hz|0=ideal> <SR_V_per_us> <r0_ohm> <Esat_V> <Rload_ohm|0> <Vload_V> <T_tau> [sigma...]
#include "fsot/engine.hpp"
#include <algorithm>
#include <array>
#include <cmath>
#include <cstdio>
#include <cstdlib>
#include <random>
#include <vector>

struct P {
  double R = 1800, L = 22e-3, C1 = 10e-9, C2 = 100e-9;           // FSOT-Chua-Circuit netlist.json
  double R1 = 220, R2 = 220, R3 = 2200, R4 = 22000, R5 = 22000, R6 = 3300;
  double A0 = 2e5, GBW = 1e6, SR = 0.5e6, Esat = 23.0 / 3.0, r0 = 0, k = 1, Rl = 0, Vl = 0;
};

constexpr int N = 3, NS = 5;  // per node: v1, v2, iL, vo_outer, vo_inner
using St = std::array<double, N * NS>;

void f(const P& p, double Rc, bool ideal, const St& s, St& o) {
  const double c1 = p.C1 * p.k, c2 = p.C2 * p.k, l = p.L * p.k;
  const double gout = 1 + p.R2 / p.R3, gin = 1 + p.R5 / p.R6, wp = 2 * M_PI * p.GBW / p.A0;
  for (int i = 0; i < N; ++i) {
    const double* x = &s[NS * i];
    double v1 = x[0], v2 = x[1], iL = x[2], vo1 = x[3], vo2 = x[4], d4 = 0, d5 = 0;
    if (ideal) { vo1 = std::clamp(gout * v1, -p.Esat, p.Esat); vo2 = std::clamp(gin * v1, -p.Esat, p.Esat); }
    else {
      d4 = std::clamp(wp * (p.A0 * (v1 - vo1 / gout) - vo1), -p.SR, p.SR);
      d5 = std::clamp(wp * (p.A0 * (v1 - vo2 / gin) - vo2), -p.SR, p.SR);
      if ((vo1 >= p.Esat && d4 > 0) || (vo1 <= -p.Esat && d4 < 0)) d4 = 0;
      if ((vo2 >= p.Esat && d5 > 0) || (vo2 <= -p.Esat && d5 < 0)) d5 = 0;
    }
    double inr = (v1 - vo1) / p.R1 + (v1 - vo2) / p.R4;
    double cpl = 0;
    if (std::isfinite(Rc)) cpl = (s[NS * ((i + 1) % N)] + s[NS * ((i + N - 1) % N)] - 2 * v1) / Rc;
    double il = p.Rl > 0 ? (v1 - p.Vl) / p.Rl : 0;
    double* y = &o[NS * i];
    y[0] = ((v2 - v1) / p.R - inr + cpl - il) / c1;
    y[1] = ((v1 - v2) / p.R + iL) / c2;
    y[2] = (-v2 - p.r0 * iL) / l;
    y[3] = d4; y[4] = d5;
  }
}

int main(int argc, char** argv) {
  if (argc < 9) { std::fprintf(stderr, "see header\n"); return 1; }
  fsot::Engine<double> e;
  const double phi = e.PHI;
  P p; p.k = std::atof(argv[1]); p.GBW = std::atof(argv[2]); p.SR = std::atof(argv[3]) * 1e6;
  p.r0 = std::atof(argv[4]); p.Esat = std::atof(argv[5]); p.Rl = std::atof(argv[6]); p.Vl = std::atof(argv[7]);
  double Ttau = std::atof(argv[8]);
  bool ideal = p.GBW <= 0;
  std::vector<double> sig;
  for (int a = 9; a < argc; ++a) sig.push_back(std::atof(argv[a]));
  if (sig.empty()) sig = {0.0, 0.9, 1.0, phi, 2.0, 2.265, 2.4, phi * phi};
  const double tau = p.R * p.C2 * p.k;
  const double dt = ideal ? 0.002 * tau : std::min(0.002 * tau, 0.05 / (2 * M_PI * p.GBW / 7.67));
  const double alpha = p.C2 / p.C1;
  std::printf("# k=%g GBW=%g SR=%gV/us r0=%g Esat=%g Rload=%g Vload=%g T=%g tau dt=%.3g s ideal=%d\n", p.k, p.GBW, p.SR / 1e6, p.r0, p.Esat, p.Rl, p.Vl, Ttau, dt, int(ideal));
  std::printf("sigma\tseed\tv1_min\tv1_max\trms\tlobe_switches_tail\tmad_over_amp\ttrit_agree\tescaped\tmax_slew_inner_V_per_us\n");
  const double gout = 1 + p.R2 / p.R3, bp2 = p.Esat / gout;
  for (double sg : sig) {
    for (unsigned seed : {1u, 2u, 3u}) {
      double Rc = sg > 0 ? alpha * p.R / sg : INFINITY;
      std::mt19937_64 g(seed); std::normal_distribution<double> nd(0, 1);
      St s{};
      for (int i = 0; i < N; ++i) { s[NS * i] = 0.1 + 0.05 * i + 0.01 * nd(g); s[NS * i + 1] = 0.02 * nd(g); }
      long n = long(Ttau * tau / dt), t0 = long(0.6 * n), cnt = 0, agree = 0, sw = 0; int last = 0;
      double mn = 1e9, mx = -1e9, sxx = 0, sx = 0, mad = 0, slew = 0, vin_prev = 0; bool esc = false;
      St k1, k2, k3, k4, t;
      for (long kk = 0; kk < n; ++kk) {
        f(p, Rc, ideal, s, k1); for (int j = 0; j < N * NS; ++j) t[j] = s[j] + .5 * dt * k1[j];
        f(p, Rc, ideal, t, k2); for (int j = 0; j < N * NS; ++j) t[j] = s[j] + .5 * dt * k2[j];
        f(p, Rc, ideal, t, k3); for (int j = 0; j < N * NS; ++j) t[j] = s[j] + dt * k3[j];
        f(p, Rc, ideal, t, k4); for (int j = 0; j < N * NS; ++j) s[j] += dt / 6 * (k1[j] + 2 * k2[j] + 2 * k3[j] + k4[j]);
        for (int i = 0; i < N; ++i) { s[NS * i + 3] = std::clamp(s[NS * i + 3], -p.Esat, p.Esat); s[NS * i + 4] = std::clamp(s[NS * i + 4], -p.Esat, p.Esat); }
        double vin = ideal ? std::clamp((1 + p.R5 / p.R6) * s[0], -p.Esat, p.Esat) : s[4];
        if (kk > 0) slew = std::max(slew, std::fabs(vin - vin_prev) / dt);
        vin_prev = vin;
        double x0 = s[0], x1 = s[NS], x2 = s[2 * NS];
        if (std::fabs(x0) > bp2 || std::fabs(x1) > bp2 || std::fabs(x2) > bp2) esc = true;
        if (kk >= t0) {
          mn = std::min(mn, x0); mx = std::max(mx, x0); sx += x0; sxx += x0 * x0; ++cnt;
          mad += (std::fabs(x0 - x1) + std::fabs(x0 - x2) + std::fabs(x1 - x2)) / 3;
          auto tr = [](double v) { return v < -1 ? -1 : (v > 1 ? 1 : 0); };
          agree += (tr(x0) == tr(x1) && tr(x1) == tr(x2));
          if (std::fabs(x0) > 0.5) { int sgn = x0 > 0 ? 1 : -1; if (last && sgn != last) ++sw; last = sgn; }
        }
      }
      double amp = std::sqrt(std::max(0.0, sxx / cnt - (sx / cnt) * (sx / cnt)));
      std::printf("%.4f\t%u\t%.3f\t%.3f\t%.3f\t%ld\t%.3g\t%.3f\t%d\t%.3f\n", sg, seed, mn, mx, std::sqrt(sxx / cnt), sw, (mad / cnt) / std::max(amp, 1e-12), double(agree) / cnt, int(esc), slew * 1e-6);
      if (sg == 0) break;
    }
  }
  return 0;
}
