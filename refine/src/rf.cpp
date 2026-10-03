// rf.cpp — FSOT refinement toolkit (C++20). Kennedy node with explicit NIC op-amp outputs (u1 outer, u2 inner):
//   x' = alpha (y - x - h) - g1p x + sigma*cpl,  h = g1 (x - u1) + g2 (x - u2)   [g1 = R/R1, g2 = R/R4]
//   y' = x - y + z - g2p y,   z' = -beta y - gamma z
//   u_i' = clamp((G_i x - u_i)/eps_i, +-SRn)  with |u_i| <= E (anti-windup); eps_i = 0 -> u_i = clamp(G_i x, +-E)
// Units: time in tau0 = k R C2, voltages in Bp1 (= 1 V); eps_i = G_i/(2 pi GBW tau0); SRn = SR[V/s] tau0 / 1 V.
// g1p, g2p: dimensionless parallel loss conductances (R*G) on the C1 and C2 nodes ("Branch C" dressing).
#include <cmath>
#include <cstdio>
#include <cstdlib>
#include <map>
#include <string>
#include <vector>
#include "eb.hpp"
using namespace eb;

struct M5 {
  double alpha = 10, beta = 1800.0 * 1800 * 100e-9 / 22e-3, gamma = 0, g1 = 1800.0 / 220, g2 = 1800.0 / 22000, G1 = 1 + 220.0 / 2200, G2 = 1 + 22000.0 / 3300,
         E = 23.0 / 3, e1 = 0, e2 = 0, SRn = 1e30, g1p = 0, g2p = 0;
  bool lag() const { return e1 > 0 || e2 > 0; }
};
static inline double clampd(double v, double l) { return v > l ? l : (v < -l ? -l : v); }
// state: x y z u1 u2 (u ignored if no lag)
static inline void f5(const M5& m, const double* s, double* o, double cpl = 0) {
  double u1 = m.e1 > 0 ? s[3] : clampd(m.G1 * s[0], m.E), u2 = m.e2 > 0 ? s[4] : clampd(m.G2 * s[0], m.E);
  double h = m.g1 * (s[0] - u1) + m.g2 * (s[0] - u2);
  o[0] = m.alpha * (s[1] - s[0] - h - m.g1p * s[0]) + cpl; o[1] = s[0] - s[1] + s[2] - m.g2p * s[1]; o[2] = -m.beta * s[1] - m.gamma * s[2];
  for (int i = 0; i < 2; ++i) {
    double e = i ? m.e2 : m.e1, G = i ? m.G2 : m.G1, u = s[3 + i];
    if (e <= 0) { o[3 + i] = 0; continue; }
    double d = clampd((G * s[0] - u) / e, m.SRn);
    if ((u >= m.E && d > 0) || (u <= -m.E && d < 0)) d = 0;
    o[3 + i] = d;
  }
}
// Jacobian-vector product (transverse, coupling -sk on x)
static inline void j5(const M5& m, const double* s, const double* w, double* r, double sk) {
  double du1 = 0, du2 = 0;  // d u_i / d x for no-lag
  if (m.e1 <= 0) du1 = std::fabs(m.G1 * s[0]) < m.E ? m.G1 : 0;
  if (m.e2 <= 0) du2 = std::fabs(m.G2 * s[0]) < m.E ? m.G2 : 0;
  double w1 = m.e1 > 0 ? w[3] : du1 * w[0], w2 = m.e2 > 0 ? w[4] : du2 * w[0];
  double dh = m.g1 * (w[0] - w1) + m.g2 * (w[0] - w2);
  r[0] = m.alpha * (w[1] - w[0] - dh - m.g1p * w[0]) - sk * w[0]; r[1] = w[0] - w[1] + w[2] - m.g2p * w[1]; r[2] = -m.beta * w[1] - m.gamma * w[2];
  for (int i = 0; i < 2; ++i) {
    double e = i ? m.e2 : m.e1, G = i ? m.G2 : m.G1, u = s[3 + i];
    if (e <= 0) { r[3 + i] = 0; continue; }
    double d = (G * s[0] - u) / e; bool lin = std::fabs(d) < m.SRn && !((u >= m.E && d > 0) || (u <= -m.E && d < 0));
    // rail-pinned output collapses perturbations (saltation): relax tangent to 0 at rate 1/eps; slew-limited: rate fixed -> 0
    bool rail = (u >= m.E && d > 0) || (u <= -m.E && d < 0);
    r[3 + i] = lin ? (G * w[0] - w[3 + i]) / e : (rail ? -w[3 + i] / e : 0);
  }
}
struct Out { std::vector<double> lam; double maxabs, frot, lobe_rate, frac_in; };
// one synchronous orbit, M transverse tangents (sig_eff list), plus orbit observables
static Out msf5(const M5& m, const std::vector<double>& se, double T, double dt, double trans, unsigned seed) {
  std::mt19937_64 g(seed); std::normal_distribution<double> nd(0, 1);
  double s[5] = {0.1 + (seed ? 0.01 * nd(g) : 0.0), seed ? 0.02 * nd(g) : 0.0, 0, 0, 0};
  s[3] = clampd(m.G1 * s[0], m.E); s[4] = clampd(m.G2 * s[0], m.E);
  size_t M = se.size(); std::vector<double> d(5 * M, 0), acc(M, 0), k[4] = {std::vector<double>(5 * M), std::vector<double>(5 * M), std::vector<double>(5 * M), std::vector<double>(5 * M)}, u(5 * M);
  for (size_t q = 0; q < M; ++q) { d[5 * q] = 1; d[5 * q + 1] = .3; d[5 * q + 2] = .1; }
  long n = long((T + trans) / dt), nt = long(trans / dt); double mx = 0; long ycross = 0, lobes = 0, inn = 0, cnt = 0; int lobe = 0; double yprev = 0;
  auto JV = [&](const double* st, const double* v, double* o) { for (size_t q = 0; q < M; ++q) j5(m, st, v + 5 * q, o + 5 * q, se[q]); };
  for (long it = 0; it < n; ++it) {
    double a1[5], a2[5], a3[5], a4[5], t[5];
    f5(m, s, a1); JV(s, d.data(), k[0].data());
    for (int i = 0; i < 5; ++i) t[i] = s[i] + .5 * dt * a1[i]; for (size_t q = 0; q < 5 * M; ++q) u[q] = d[q] + .5 * dt * k[0][q];
    f5(m, t, a2); JV(t, u.data(), k[1].data());
    for (int i = 0; i < 5; ++i) t[i] = s[i] + .5 * dt * a2[i]; for (size_t q = 0; q < 5 * M; ++q) u[q] = d[q] + .5 * dt * k[1][q];
    f5(m, t, a3); JV(t, u.data(), k[2].data());
    for (int i = 0; i < 5; ++i) t[i] = s[i] + dt * a3[i]; for (size_t q = 0; q < 5 * M; ++q) u[q] = d[q] + dt * k[2][q];
    f5(m, t, a4); JV(t, u.data(), k[3].data());
    for (int i = 0; i < 5; ++i) s[i] += dt / 6 * (a1[i] + 2 * a2[i] + 2 * a3[i] + a4[i]);
    for (size_t q = 0; q < 5 * M; ++q) d[q] += dt / 6 * (k[0][q] + 2 * k[1][q] + 2 * k[2][q] + k[3][q]);
    if (m.e1 > 0) s[3] = clampd(s[3], m.E); if (m.e2 > 0) s[4] = clampd(s[4], m.E);
    if (it >= nt) {
      mx = std::max(mx, std::fabs(s[0])); ++cnt; inn += std::fabs(s[0]) < 1;
      if ((s[1] > 0) != (yprev > 0)) ++ycross; yprev = s[1];
      int nl = s[0] > 1 ? 1 : (s[0] < -1 ? -1 : lobe); if (nl != lobe && lobe != 0) ++lobes; lobe = nl;
    } else yprev = s[1];
    for (size_t q = 0; q < M; ++q) { double* w = &d[5 * q]; double nr = 0; for (int i = 0; i < 5; ++i) nr += w[i] * w[i]; nr = std::sqrt(nr); if (it >= nt) acc[q] += std::log(nr); for (int i = 0; i < 5; ++i) w[i] /= nr; }
  }
  for (auto& v : acc) v /= T;
  return {acc, mx, ycross / 2.0 / T, lobes / T * 100.0, double(inn) / cnt};
}
static std::map<std::string, std::string> A;
static double G(const char* k, double d) { auto it = A.find(k); return it == A.end() ? d : std::atof(it->second.c_str()); }
static std::vector<double> rng(const std::string& s) {  // lo:hi:step or comma list
  std::vector<double> v; if (s.find(':') != std::string::npos) { double lo, hi, st; std::sscanf(s.c_str(), "%lf:%lf:%lf", &lo, &hi, &st); for (double x = lo; x <= hi + 1e-12; x += st) v.push_back(x); }
  else { size_t p = 0; while (p < s.size()) { size_t q = s.find(',', p); if (q == std::string::npos) q = s.size(); v.push_back(std::atof(s.substr(p, q - p).c_str())); p = q + 1; } } return v; }
static M5 model_from_args() {
  M5 m; double r0 = G("r0", 18.4400497592861384), k = G("k", 1), tau0 = k * 1800 * 100e-9;
  m.gamma = (1800.0 * 1800 * 100e-9 / 22e-3) * r0 / 1800; if (A.count("gamma")) m.gamma = G("gamma", 0);
  double gbw = G("gbw", 0), sr = G("sr", 0);  // Hz, V/us
  if (gbw > 0) { m.e1 = m.G1 / (2 * M_PI * gbw * tau0); m.e2 = m.G2 / (2 * M_PI * gbw * tau0); }
  double ek = G("eps_nic", 0); if (ek > 0) { m.e1 = std::sqrt(m.e1 * m.e1 + ek * ek); m.e2 = std::sqrt(m.e2 * m.e2 + ek * ek); }  // add an extra lag in quadrature? (see doc) -> overridden by lagmode
  if (A.count("e_add")) { m.e1 += G("e_add", 0); m.e2 += G("e_add", 0); }  // series lags add (first-order approx of two cascaded poles)
  if (sr > 0) m.SRn = sr * 1e6 * tau0;
  m.g1p = G("g1p", 0); m.g2p = G("g2p", 0); m.alpha = G("alpha", m.alpha); m.beta = G("beta", m.beta);
  return m;
}
int main(int ac, char** av) {
  std::string cmd = ac > 1 ? av[1] : ""; for (int i = 2; i < ac; ++i) { std::string s = av[i]; auto e = s.find('='); if (e != std::string::npos) A[s.substr(0, e)] = s.substr(e + 1); }
  if (cmd == "msf") {  // sigma_c over nic ICs for one model
    M5 m = model_from_args(); auto sg = rng(A.count("sig") ? A["sig"] : "1.30:1.70:0.005"); int nic = int(G("nic", 4));
    double emin = std::min(m.e1 > 0 ? m.e1 : 1, m.e2 > 0 ? m.e2 : 1), dt = std::min(G("dt", 0.005), emin / 4), T = G("T", 6000);
    std::vector<double> se; se.push_back(0); for (double s : sg) se.push_back(3 * s);
    std::vector<Out> o(nic); parallel_for(nic, [&](size_t i) { o[i] = msf5(m, se, T, dt, 200, unsigned(i)); });
    std::printf("# msf5 e1=%.6g e2=%.6g SRn=%.6g gamma=%.8f g1p=%.5g g2p=%.5g dt=%.6g T=%g\n", m.e1, m.e2, m.SRn, m.gamma, m.g1p, m.g2p, dt, T);
    double sum = 0, ss = 0; int nn = 0;
    for (int i = 0; i < nic; ++i) { std::vector<double> l(o[i].lam.begin() + 1, o[i].lam.end()); double r = fit_root(sg, l);
      std::printf("ic=%d sigc=%.5f lam1=%.5f maxabs=%.4f frot_per_tau=%.5f lobes_per100tau=%.3f frac_inner=%.4f\n", i, r, o[i].lam[0], o[i].maxabs, o[i].frot, o[i].lobe_rate, o[i].frac_in);
      if (G("curve", 0) > 0) { std::printf("curve ic=%d", i); for (size_t q = 0; q < sg.size(); ++q) std::printf(" %.4f:%.4f", sg[q], l[q]); std::printf("\n"); }
      if (std::isfinite(r)) { sum += r; ss += r * r; ++nn; } }
    double mu = sum / nn; std::printf("#mean sigc=%.5f sd=%.5f n=%d\n", mu, nn > 1 ? std::sqrt((ss - nn * mu * mu) / (nn - 1)) : 0, nn); return 0;
  }
  if (cmd == "lyap") {  // single-node lam1 and observables vs r0 (sync manifold = single node)
    auto rs = rng(A["r0s"]); int nic = int(G("nic", 3)); double T = G("T", 20000);
    struct R { double r0; std::vector<Out> o; }; std::vector<R> res(rs.size() * nic);
    for (size_t i = 0; i < rs.size(); ++i) for (int j = 0; j < nic; ++j) res[i * nic + j].r0 = rs[i];
    parallel_for(res.size(), [&](size_t q) { M5 m; m.gamma = (1800.0 * 1800 * 100e-9 / 22e-3) * res[q].r0 / 1800; res[q].o = {msf5(m, {0.0}, T, 0.005, 500, unsigned(q % nic))}; });
    std::printf("r0\tic\tlam1\tmaxabs\tfrot_per_tau\tlobes_per100tau\tfrac_inner\n");
    for (size_t q = 0; q < res.size(); ++q) { auto& o = res[q].o[0]; std::printf("%.4f\t%zu\t%.6f\t%.4f\t%.5f\t%.3f\t%.4f\n", res[q].r0, q % nic, o.lam[0], o.maxabs, o.frot, o.lobe_rate, o.frac_in); }
    return 0;
  }
  if (cmd == "peaks") {  // bifurcation diagram: local maxima of x on the attractor vs r0
    auto rs = rng(A["r0s"]); double T = G("T", 3000); std::vector<std::vector<double>> pk(rs.size());
    parallel_for(rs.size(), [&](size_t i) { M5 m; m.gamma = (1800.0 * 1800 * 100e-9 / 22e-3) * rs[i] / 1800; double s[5] = {0.1, 0, 0, 0, 0}, dt = 0.005, xp = 0, xpp = 0;
      long n = long((T + 1000) / dt);
      for (long it = 0; it < n; ++it) { double a1[5], a2[5], a3[5], a4[5], t[5]; f5(m, s, a1); for (int j = 0; j < 5; ++j) t[j] = s[j] + .5 * dt * a1[j]; f5(m, t, a2); for (int j = 0; j < 5; ++j) t[j] = s[j] + .5 * dt * a2[j];
        f5(m, t, a3); for (int j = 0; j < 5; ++j) t[j] = s[j] + dt * a3[j]; f5(m, t, a4); for (int j = 0; j < 5; ++j) s[j] += dt / 6 * (a1[j] + 2 * a2[j] + 2 * a3[j] + a4[j]);
        if (it * dt > 1000 && xp > xpp && xp >= s[0] && xp > 0) pk[i].push_back(xp); xpp = xp; xp = s[0]; } });
    for (size_t i = 0; i < rs.size(); ++i) for (double v : pk[i]) std::printf("%.4f\t%.5f\n", rs[i], v);
    return 0;
  }
  if (cmd == "ring") {  // nonlinear 3-ring with the same node model: lock fraction vs sigma (repo lock law + amplitude check)
    M5 m = model_from_args(); auto sg = rng(A["sig"]); int ns = int(G("seeds", 12)); double T = G("T", 2000), tail = 500;
    double emin = std::min(m.e1 > 0 ? m.e1 : 1, m.e2 > 0 ? m.e2 : 1), dt = std::min(0.005, emin / 4);
    double x2 = 230.0 / 33; std::vector<int> lk(sg.size() * ns);
    parallel_for(lk.size(), [&](size_t q) { double sig = sg[q / ns]; auto ic = random_ic(3, unsigned(q % ns + 1)); double s[15];
      for (int i = 0; i < 3; ++i) { s[5 * i] = ic[3 * i]; s[5 * i + 1] = ic[3 * i + 1]; s[5 * i + 2] = ic[3 * i + 2]; s[5 * i + 3] = clampd(m.G1 * s[5 * i], m.E); s[5 * i + 4] = clampd(m.G2 * s[5 * i], m.E); }
      auto F = [&](const double* u, double* o) { for (int i = 0; i < 3; ++i) { double c = u[5 * ((i + 1) % 3)] + u[5 * ((i + 2) % 3)] - 2 * u[5 * i]; f5(m, u + 5 * i, o + 5 * i, sig * c); } };
      long n = long(T / dt), t0 = n - long(tail / dt); double mad = 0, amp = 0, mx = 0; long c = 0; double k1[15], k2[15], k3[15], k4[15], t[15];
      for (long it = 0; it < n; ++it) { F(s, k1); for (int j = 0; j < 15; ++j) t[j] = s[j] + .5 * dt * k1[j]; F(t, k2); for (int j = 0; j < 15; ++j) t[j] = s[j] + .5 * dt * k2[j];
        F(t, k3); for (int j = 0; j < 15; ++j) t[j] = s[j] + dt * k3[j]; F(t, k4); for (int j = 0; j < 15; ++j) s[j] += dt / 6 * (k1[j] + 2 * k2[j] + 2 * k3[j] + k4[j]);
        if (it >= t0) { double mu = (s[0] + s[5] + s[10]) / 3; for (int i = 0; i < 3; ++i) { mad += std::fabs(s[5 * i] - mu); amp += std::fabs(s[5 * i]); mx = std::max(mx, std::fabs(s[5 * i])); } ++c; } }
      lk[q] = mx < x2 && mad / amp < std::pow(PHI, -4); });
    std::printf("# ring5 e1=%.6g e2=%.6g SRn=%.6g gamma=%.8f\nsigma\tlocked\tn\n", m.e1, m.e2, m.SRn, m.gamma);
    for (size_t i = 0; i < sg.size(); ++i) { int c = 0; for (int j = 0; j < ns; ++j) c += lk[i * ns + j]; std::printf("%.4f\t%d\t%d\n", sg[i], c, ns); }
    return 0;
  }
  std::fprintf(stderr, "cmds: msf lyap peaks ring\n"); return 1;
}
