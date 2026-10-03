// fsot_chua.cpp — FSOT Chua ring: derivation + simulation, C++20, FSOT-2.1-Cpp conventions.
// Constants come from fsot::Engine (authority pin AEB2AD, header-only). Circuit numbers come
// from FSOT-Chua-Circuit hardware/netlist.json. Nothing here is fitted.
//
//   fsot_chua derive                      # exact NIC rationals, alpha, beta, a, b, c, Rc(sigma)
//   fsot_chua sweep  [model] [T] [seeds]  # 3-ring lock metrics vs sigma (TSV)
//   fsot_chua msf    [model]              # transverse Lyapunov exponent vs sigma (master stability, ring of 3)
//   fsot_chua lyap   [model]              # largest Lyapunov exponent of one node
// model: repo (3-seg, b=-6/11, as coded in sim/chua_array.py) | kennedy (exact BOM NIC, 5-seg, b=-81/110)
#include "fsot/engine.hpp"
#include "fsot_chua/branch_l.hpp"
#include <algorithm>
#include <array>
#include <cstdlib>
#include <cmath>
#include <cstdint>
#include <cstdio>
#include <numeric>
#include <random>
#include <string>
#include <string_view>
#include <vector>

namespace chua {

struct Frac {  // exact rational conductance in siemens (num/den)
  std::int64_t n, d;
  constexpr Frac norm() const { auto g = std::gcd(n < 0 ? -n : n, d); return {n / g, d / g}; }
  constexpr Frac operator+(Frac o) const { return Frac{n * o.d + o.n * d, d * o.d}.norm(); }
  constexpr Frac operator-(Frac o) const { return Frac{n * o.d - o.n * d, d * o.d}.norm(); }
  constexpr Frac scale(std::int64_t k) const { return Frac{n * k, d}.norm(); }
  double v() const { return double(n) / double(d); }
};

// FSOT-Chua-Circuit hardware/netlist.json
struct Bom {
  double R = 1800, L = 22e-3, C1 = 10e-9, C2 = 100e-9;
  std::int64_t R1 = 220, R2 = 220, R3 = 2200, R4 = 22000, R5 = 22000, R6 = 3300;
  double Bp = 1.0;  // repo trit breakpoint [V]
};

struct Nic {      // Kennedy: outer op-amp (R1 fb, R2/R3 divider), inner op-amp (R4 fb, R5/R6 divider)
  Frac Ga, Gb, Gc;
  double Esat, Bp1, Bp2;
};
inline Nic derive_nic(const Bom& b) {
  // linear-region conductance of each op-amp branch: -R2/(R1 R3), -R5/(R4 R6); saturated: +1/R1, +1/R4
  Frac out_lin{-b.R2, b.R1 * b.R3}, in_lin{-b.R5, b.R4 * b.R6}, out_sat{1, b.R1}, in_sat{1, b.R4};
  Nic n;
  n.Ga = (out_lin + in_lin).norm();   // |v| < Bp1  both linear
  n.Gb = (out_lin + in_sat).norm();   // Bp1 < |v| < Bp2  inner saturated
  n.Gc = (out_sat + in_sat).norm();   // |v| > Bp2  both saturated
  n.Esat = b.Bp * double(b.R5 + b.R6) / double(b.R6);  // rail needed so Bp1 == repo Bp (1 V)
  n.Bp1 = n.Esat * double(b.R6) / double(b.R5 + b.R6);
  n.Bp2 = n.Esat * double(b.R3) / double(b.R2 + b.R3);
  return n;
}

struct Model {  // dimensionless Chua: x'=alpha(y-x-h(x))+sigma*L(x), y'=x-y+z, z'=-beta y - gamma z
  double alpha, beta, gamma = 0, a, b, c = 0, x2 = 1e300;  // x2 = Bp2/Bp (outer breakpoint)
  double h(double x) const {
    double ax = std::fabs(x), s = x < 0 ? -1 : 1;
    if (ax < 1) return a * x;
    if (ax < x2) return s * (a + b * (ax - 1));
    return s * (a + b * (x2 - 1) + c * (ax - x2));
  }
  double hp(double x) const { double ax = std::fabs(x); return ax < 1 ? a : (ax < x2 ? b : c); }
};

inline Model make_model(std::string_view which, const Bom& bom, double r0 = 0) {
  auto nic = derive_nic(bom);
  Model m;
  m.alpha = bom.C2 / bom.C1;
  m.beta = bom.R * bom.R * bom.C2 / bom.L;
  m.gamma = m.beta * r0 / bom.R;  // inductor / gyrator series resistance r0
  m.a = bom.R * nic.Ga.v();
  if (which == "repo") { m.b = bom.R * (-1.0 / double(bom.R6)); }  // repo sim/chua_array.py: Gb = -1/R6
  else { m.b = bom.R * nic.Gb.v(); m.c = bom.R * nic.Gc.v(); m.x2 = nic.Bp2 / bom.Bp; }
  return m;
}

template <int N> struct Ring {
  const Model& m; double sigma;
  void f(const std::array<double, 3 * N>& s, std::array<double, 3 * N>& o) const {
    for (int i = 0; i < N; ++i) {
      double x = s[3 * i], y = s[3 * i + 1], z = s[3 * i + 2];
      double cpl = 0;
      if constexpr (N > 1) cpl = s[3 * ((i + 1) % N)] + s[3 * ((i + N - 1) % N)] - 2 * x;
      o[3 * i] = m.alpha * (y - x - m.h(x)) + sigma * cpl;
      o[3 * i + 1] = x - y + z;
      o[3 * i + 2] = -m.beta * y - m.gamma * z;
    }
  }
  void rk4(std::array<double, 3 * N>& s, double dt) const {
    std::array<double, 3 * N> k1, k2, k3, k4, t;
    f(s, k1); for (int j = 0; j < 3 * N; ++j) t[j] = s[j] + 0.5 * dt * k1[j];
    f(t, k2); for (int j = 0; j < 3 * N; ++j) t[j] = s[j] + 0.5 * dt * k2[j];
    f(t, k3); for (int j = 0; j < 3 * N; ++j) t[j] = s[j] + dt * k3[j];
    f(t, k4); for (int j = 0; j < 3 * N; ++j) s[j] += dt / 6 * (k1[j] + 2 * k2[j] + 2 * k3[j] + k4[j]);
  }
};

struct LockStats { double amp, mad, trit, railed; bool locked; double t_escape; double maxabs; };

// Same lock law as FSOT-Chua-Circuit sim/chua_array.seed_locked: MAD <= amp_ref*phi^-4, trit >= phi^-1,
// amp >= amp_ref*phi^-4, railed < 5 %. Tail = last 30 % (repo) of [0, T].
inline bool repo_clip = false;  // reproduce np.clip(s,-8,8) of sim/chua_array.rk4_traj
inline LockStats ring_run(const Model& m, double sigma, double T, double dt, unsigned seed, double amp_ref, double phi) {
  Ring<3> r{m, sigma};
  std::mt19937_64 g(seed); std::normal_distribution<double> nd(0, 1);
  std::array<double, 9> s{};
  for (int i = 0; i < 3; ++i) { s[3 * i] = 0.1 + 0.05 * i + 0.01 * nd(g); s[3 * i + 1] = 0.02 * nd(g); }
  long n = long(T / dt), t0 = long(0.7 * n), cnt = 0, agree = 0, rail = 0;
  if (const char* tt = std::getenv("FSOT_CHUA_TAIL_TAU")) t0 = n - long(std::atof(tt) / dt);  // locked protocol: last 500 tau
  double sx[3] = {0, 0, 0}, sxx[3] = {0, 0, 0}, mad = 0, t_esc = -1, mx = 0;
  // escape = left the double-scroll region: |x| beyond the outer breakpoint (kennedy) or beyond 8 (repo clip)
  const double xesc = m.x2 < 1e100 ? m.x2 : 8.0;
  for (long k = 0; k < n; ++k) {
    if (t_esc < 0 && (std::fabs(s[0]) > xesc || std::fabs(s[3]) > xesc || std::fabs(s[6]) > xesc || !std::isfinite(s[0]))) t_esc = k * dt;
    if (k >= t0) mx = std::max({mx, std::fabs(s[0]), std::fabs(s[3]), std::fabs(s[6])});
    if (repo_clip) for (auto& v : s) v = std::clamp(v, -8.0, 8.0);
    if (k >= t0) {
      double x[3] = {s[0], s[3], s[6]};
      int tr[3];
      for (int i = 0; i < 3; ++i) { sx[i] += x[i]; sxx[i] += x[i] * x[i]; tr[i] = x[i] < -1 ? -1 : (x[i] > 1 ? 1 : 0); if (std::fabs(x[i]) > 7.5) ++rail; }
      mad += (std::fabs(x[0] - x[1]) + std::fabs(x[0] - x[2]) + std::fabs(x[1] - x[2])) / 3;
      agree += (tr[0] == tr[1] && tr[1] == tr[2]); ++cnt;
    }
    r.rk4(s, dt);
  }
  LockStats L{};
  for (int i = 0; i < 3; ++i) L.amp += std::sqrt(std::max(0.0, sxx[i] / cnt - (sx[i] / cnt) * (sx[i] / cnt))) / 3;
  L.mad = mad / cnt; L.trit = double(agree) / cnt; L.railed = double(rail) / (3.0 * cnt);
  double cut = amp_ref * std::pow(phi, -4);
  L.locked = L.mad <= cut && L.trit >= 1 / phi && L.amp >= cut && L.railed < 0.05 && std::isfinite(L.mad);
  if (std::getenv("FSOT_CHUA_AMPCHECK")) L.locked = L.locked && mx < xesc;  // amplitude check: no escape to outer cycle
  L.t_escape = t_esc; L.maxabs = mx;
  return L;
}

inline double single_amp(const Model& m, double T, double dt) {
  Ring<1> r{m, 0}; std::array<double, 3> s{0.1, 0, 0};
  long n = long(T / dt), t0 = long(0.7 * n), c = 0; double sx = 0, sxx = 0;
  for (long k = 0; k < n; ++k) { if (k >= t0) { sx += s[0]; sxx += s[0] * s[0]; ++c; } r.rk4(s, dt); }
  return std::sqrt(sxx / c - (sx / c) * (sx / c));
}

// largest (sig_t = 0) or transverse (sig_t = 3 sigma for ring of 3) Lyapunov exponent, per tau = R C2
inline double lyap(const Model& m, double sig_t, double T = 4000, double dt = 0.005, double trans = 200) {
  std::array<double, 3> s{0.1, 0, 0}, d{1, 0.3, 0.1};
  Ring<1> r{m, 0};
  auto J = [&](const std::array<double, 3>& st, const std::array<double, 3>& v) {
    return std::array<double, 3>{(-m.alpha * (1 + m.hp(st[0])) - sig_t) * v[0] + m.alpha * v[1], v[0] - v[1] + v[2], -m.beta * v[1] - m.gamma * v[2]};
  };
  long n = long((T + trans) / dt), nt = long(trans / dt); double acc = 0;
  for (long k = 0; k < n; ++k) {
    // RK4 on (state, tangent)
    std::array<double, 3> k1, k2, k3, k4, t, j1, j2, j3, j4, u;
    r.f(s, k1); j1 = J(s, d);
    for (int i = 0; i < 3; ++i) { t[i] = s[i] + .5 * dt * k1[i]; u[i] = d[i] + .5 * dt * j1[i]; }
    r.f(t, k2); j2 = J(t, u);
    for (int i = 0; i < 3; ++i) { t[i] = s[i] + .5 * dt * k2[i]; u[i] = d[i] + .5 * dt * j2[i]; }
    r.f(t, k3); j3 = J(t, u);
    for (int i = 0; i < 3; ++i) { t[i] = s[i] + dt * k3[i]; u[i] = d[i] + dt * j3[i]; }
    r.f(t, k4); j4 = J(t, u);
    for (int i = 0; i < 3; ++i) { s[i] += dt / 6 * (k1[i] + 2 * k2[i] + 2 * k3[i] + k4[i]); d[i] += dt / 6 * (j1[i] + 2 * j2[i] + 2 * j3[i] + j4[i]); }
    double nr = std::sqrt(d[0] * d[0] + d[1] * d[1] + d[2] * d[2]);
    if (k >= nt) acc += std::log(nr);
    for (auto& v : d) v /= nr;
  }
  return acc / T;
}

}  // namespace chua

int main(int argc, char** argv) {
  using namespace chua;
  fsot::Engine<double> e;
  const double phi = e.PHI;
  std::string cmd = argc > 1 ? argv[1] : "derive";
  std::string model = argc > 2 ? argv[2] : "kennedy";
  Bom bom;
  double r0 = 0;
  // r0: FSOT Branch L by default (docs/BRANCH_L_DERIVATION.md); FSOT_CHUA_R0=<ohm> overrides (0 = ideal inductor).
  r0 = double(fsot::chua::BranchL<double>(e).r0_ohm(bom.L, bom.C2));
  if (const char* env = std::getenv("FSOT_CHUA_R0")) r0 = std::atof(env);
  Model m = make_model(model, bom, r0);

  if (cmd == "derive") {
    auto nic = derive_nic(bom);
    const auto& em = e.domain("Electromagnetism");
    double S = e.domain_scalar("Electromagnetism"), th = double(e.C_EFF * e.P_VAR);
    std::printf("authority_pin\t%s\n", std::string(fsot::AUTHORITY_PIN_PREFIX).c_str());
    std::printf("EM_D_eff\t%d\nEM_look\t%.17g\nS_EM\t%.17g\nTheta=C_EFF*P_VAR\t%.17g\nS_EM_trit\t%d\n", em.D_eff, double(em.delta_psi), S, th,
                std::fabs(S) < th ? 0 : (S > 0 ? 1 : -1));
    std::printf("ALPHA(LedgerB f)\t%.17g\nLedgerB_residual_pct(|S|*ALPHA)\t%.6g\n", double(e.ALPHA), std::fabs(S) * double(e.ALPHA) * 100);
    std::printf("kappa_identical=A_BLEED*POOF*S^2\t%.17g\n", double(e.A_BLEED * e.POOF) * S * S);
    std::printf("phi\t%.17g\n", phi);
    std::printf("Ga_S\t%lld/%lld\t%.10g\nGb_S\t%lld/%lld\t%.10g\nGc_S\t%lld/%lld\t%.10g\n", (long long)nic.Ga.n, (long long)nic.Ga.d, nic.Ga.v(),
                (long long)nic.Gb.n, (long long)nic.Gb.d, nic.Gb.v(), (long long)nic.Gc.n, (long long)nic.Gc.d, nic.Gc.v());
    auto a = nic.Ga.scale(1800), b = nic.Gb.scale(1800), c = nic.Gc.scale(1800);
    std::printf("a=R*Ga\t%lld/%lld\nb=R*Gb\t%lld/%lld\nc=R*Gc\t%lld/%lld\n", (long long)a.n, (long long)a.d, (long long)b.n, (long long)b.d, (long long)c.n, (long long)c.d);
    std::printf("repo_b(-R/R6)\t-6/11\nEsat_for_Bp1=1V\t%.10g\nBp2_V\t%.10g\n", nic.Esat, nic.Bp2);
    std::printf("alpha\t%.10g\nbeta\t%.10g\ntau=RC2_s\t%.6g\nf_LC_Hz\t%.6f\n", m.alpha, m.beta, bom.R * bom.C2, 1 / (2 * M_PI * std::sqrt(bom.L * bom.C2)));
    for (double sg : {1.0, phi, phi * phi}) std::printf("Rc(sigma=%.6f)_ohm\t%.6f\n", sg, m.alpha * bom.R / sg);
    return 0;
  }
  if (cmd == "single") {  // single node: T tau, report lambda1, lobe occupancy, switches, max|x|, escape
    double T = argc > 3 ? std::atof(argv[3]) : 2000, dt = argc > 4 ? std::atof(argv[4]) : 0.005;
    Ring<1> r{m, 0}; std::array<double, 3> s{0.1, 0, 0};
    long n = long(T / dt), pos = 0, cnt = 0, sw = 0; int lobe = 0; double mx = 0;
    for (long k = 0; k < n; ++k) {
      r.rk4(s, dt);
      if (k > n / 10) { ++cnt; pos += s[0] > 0; mx = std::max(mx, std::fabs(s[0]));
        int l = s[0] > 1 ? 1 : (s[0] < -1 ? -1 : lobe); if (lobe && l != lobe) ++sw; lobe = l; }
    }
    std::printf("T_tau\t%g\nlambda1_per_tau\t%.6f\nfrac_x_pos\t%.4f\nlobe_switches\t%ld\nmax_abs_x\t%.4f\nx2\t%.4f\nescaped\t%d\n",
                T, lyap(m, 0, T), double(pos) / cnt, sw, mx, m.x2, int(mx > m.x2));
    return 0;
  }
  if (cmd == "lyap") { std::printf("lambda1_per_tau\t%.6f\n", lyap(m, 0)); return 0; }
  if (cmd == "msf") {
    std::printf("sigma\tlambda_perp_per_tau\n");
    for (double sg = 0; sg <= 3.0001; sg += 0.025) std::printf("%.4f\t%.6f\n", sg, lyap(m, 3 * sg, 3000));
    return 0;
  }
  if (cmd == "sweep") {
    double T = argc > 3 ? std::atof(argv[3]) : 80.0;           // repo default t_end = 80
    double dt = argc > 4 ? std::atof(argv[4]) : 0.008;         // repo default dt
    repo_clip = std::getenv("FSOT_CHUA_CLIP8") != nullptr;
    double amp_ref = single_amp(m, T, dt);
    std::vector<unsigned> seeds{1, 2, 3, 5, 8, 13};
    std::vector<double> sig;
    double sgrid = std::getenv("FSOT_CHUA_SGRID") ? std::atof(std::getenv("FSOT_CHUA_SGRID")) : 0.05;
    for (double s = 0; s <= 3.0001; s += sgrid) sig.push_back(s);
    for (double s : {0.9, 1.0, 18000.0 / 11130, 18000.0 / 11000, phi, phi * phi}) sig.push_back(s);
    std::printf("# model=%s T=%g dt=%g amp_ref=%.6f r0=%g clip8=%d seeds=1,2,3,5,8,13\n", model.c_str(), T, dt, amp_ref, r0, int(repo_clip));
    std::printf("sigma\tlock_rate\tmean_mad_over_amp\tmean_trit\tescaped_frac\tmin_t_escape_tau\tmean_tail_maxabs\n");
    for (double s : sig) {
      int locks = 0, esc = 0; double rel = 0, tr = 0, tmin = 1e300, mxa = 0;
      for (auto sd : seeds) {
        auto L = ring_run(m, s, T, dt, sd, amp_ref, phi); locks += L.locked;
        rel += std::isfinite(L.mad) ? L.mad / std::max(L.amp, 1e-12) : NAN; tr += L.trit; mxa += L.maxabs;
        if (L.t_escape >= 0) { ++esc; tmin = std::min(tmin, L.t_escape); }
      }
      double ns = double(seeds.size());
      std::printf("%.6f\t%.4f\t%.6g\t%.4f\t%.4f\t%.4g\t%.4g\n", s, locks / ns, rel / ns, tr / ns, esc / ns, esc ? tmin : -1.0, mxa / ns);
    }
    return 0;
  }
  if (cmd == "trace") {  // trace model sigma T seed dt : x_A x_B x_C every 1 tau
    double sg = std::atof(argv[3]), T = std::atof(argv[4]); unsigned sd = unsigned(std::atoi(argv[5]));
    double dt = argc > 6 ? std::atof(argv[6]) : 0.005;
    Ring<3> r{m, sg};
    std::mt19937_64 g(sd); std::normal_distribution<double> nd(0, 1);
    std::array<double, 9> s{};
    for (int i = 0; i < 3; ++i) { s[3 * i] = 0.1 + 0.05 * i + 0.01 * nd(g); s[3 * i + 1] = 0.02 * nd(g); }
    long n = long(T / dt), every = long(std::lround(0.05 / dt));
    std::printf("t\txA\txB\txC\tyA\tzA\n");
    for (long k = 0; k <= n; ++k) { if (k % every == 0) std::printf("%.3f\t%.6g\t%.6g\t%.6g\t%.6g\t%.6g\n", k * dt, s[0], s[3], s[6], s[1], s[2]); r.rk4(s, dt); }
    return 0;
  }
  std::fprintf(stderr, "unknown command\n");
  return 1;
}
