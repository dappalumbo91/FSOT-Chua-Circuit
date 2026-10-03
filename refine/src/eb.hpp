// eb.hpp — error-budget / pressure-point toolkit for the FSOT Kennedy-Chua ring (C++20, header-only).
// Dimensionless model (same as FSOT-Chua-Circuit cpp/tools/fsot_chua.cpp):
//   x' = alpha (y - x - h(x)) + sigma * sum_j A_ij (x_j - x_i),  y' = x - y + z,  z' = -beta y - gamma z
#pragma once
#include <algorithm>
#include <atomic>
#include <cmath>
#include <cstdio>
#include <functional>
#include <numeric>
#include <random>
#include <thread>
#include <vector>

namespace eb {

constexpr double PHI = 1.6180339887498948482;

struct Model {
  double alpha = 10, beta = 1800.0 * 1800 * 100e-9 / 22e-3, gamma = 0, a = -15.0 / 11, b = -81.0 / 110, c = 909.0 / 110,
         x2 = 230.0 / 33;
  double h(double x) const {
    double ax = std::fabs(x), s = x < 0 ? -1 : 1;
    if (ax < 1) return a * x;
    if (ax < x2) return s * (a + b * (ax - 1));
    return s * (a + b * (x2 - 1) + c * (ax - x2));
  }
  double hp(double x) const { double ax = std::fabs(x); return ax < 1 ? a : (ax < x2 ? b : c); }
  static double gamma_from_r0(double r0, double R = 1800, double L = 22e-3, double C2 = 100e-9) {
    return (R * R * C2 / L) * r0 / R;
  }
};

// ---------------- MSF: one synchronous orbit, many transverse tangent vectors (one per sigma_eff) -----------
struct MsfOut { std::vector<double> lam; double maxabs; };
inline MsfOut msf(const Model& m, const std::vector<double>& sig_eff, double T, double dt, double trans, unsigned seed) {
  std::mt19937_64 g(seed); std::normal_distribution<double> nd(0, 1);
  double s[3] = {0.1 + (seed ? 0.01 * nd(g) : 0.0), seed ? 0.02 * nd(g) : 0.0, 0};
  const size_t M = sig_eff.size();
  std::vector<double> d(3 * M), acc(M, 0.0);
  for (size_t k = 0; k < M; ++k) { d[3 * k] = 1; d[3 * k + 1] = 0.3; d[3 * k + 2] = 0.1; }
  auto F = [&](const double* u, double* o) { o[0] = m.alpha * (u[1] - u[0] - m.h(u[0])); o[1] = u[0] - u[1] + u[2]; o[2] = -m.beta * u[1] - m.gamma * u[2]; };
  long n = long((T + trans) / dt), nt = long(trans / dt);
  double mx = 0;
  std::vector<double> j1(3 * M), j2(3 * M), j3(3 * M), j4(3 * M), u(3 * M);
  auto J = [&](const double* st, const double* v, double* o) {
    double hp = m.hp(st[0]);
    for (size_t k = 0; k < M; ++k) {
      const double* w = v + 3 * k; double* r = o + 3 * k;
      r[0] = (-m.alpha * (1 + hp) - sig_eff[k]) * w[0] + m.alpha * w[1];
      r[1] = w[0] - w[1] + w[2];
      r[2] = -m.beta * w[1] - m.gamma * w[2];
    }
  };
  for (long it = 0; it < n; ++it) {
    double k1[3], k2[3], k3[3], k4[3], t[3];
    F(s, k1); J(s, d.data(), j1.data());
    for (int i = 0; i < 3; ++i) t[i] = s[i] + .5 * dt * k1[i];
    for (size_t q = 0; q < 3 * M; ++q) u[q] = d[q] + .5 * dt * j1[q];
    F(t, k2); J(t, u.data(), j2.data());
    for (int i = 0; i < 3; ++i) t[i] = s[i] + .5 * dt * k2[i];
    for (size_t q = 0; q < 3 * M; ++q) u[q] = d[q] + .5 * dt * j2[q];
    F(t, k3); J(t, u.data(), j3.data());
    for (int i = 0; i < 3; ++i) t[i] = s[i] + dt * k3[i];
    for (size_t q = 0; q < 3 * M; ++q) u[q] = d[q] + dt * j3[q];
    F(t, k4); J(t, u.data(), j4.data());
    for (int i = 0; i < 3; ++i) s[i] += dt / 6 * (k1[i] + 2 * k2[i] + 2 * k3[i] + k4[i]);
    for (size_t q = 0; q < 3 * M; ++q) d[q] += dt / 6 * (j1[q] + 2 * j2[q] + 2 * j3[q] + j4[q]);
    if (it >= nt) mx = std::max(mx, std::fabs(s[0]));
    for (size_t k = 0; k < M; ++k) {
      double* w = &d[3 * k];
      double nr = std::sqrt(w[0] * w[0] + w[1] * w[1] + w[2] * w[2]);
      if (it >= nt) acc[k] += std::log(nr);
      w[0] /= nr; w[1] /= nr; w[2] /= nr;
    }
  }
  for (auto& v : acc) v /= T;
  return {acc, mx};
}

// least-squares quadratic fit lam(s) and its root nearest the sign change; NAN if none
inline double fit_root(const std::vector<double>& s, const std::vector<double>& l) {
  // linear interpolation at the last + -> - crossing as a fallback, quadratic LS refine on the window
  int idx = -1;
  for (size_t i = 0; i + 1 < s.size(); ++i) if (l[i] > 0 && l[i + 1] <= 0) idx = int(i);
  if (idx < 0) return NAN;
  double r0 = s[idx] + (s[idx + 1] - s[idx]) * l[idx] / (l[idx] - l[idx + 1]);
  // quadratic LS on all points (window chosen by caller)
  double S[5] = {0}, B[3] = {0};
  for (size_t i = 0; i < s.size(); ++i) {
    double x = s[i] - r0, p = 1;
    for (int k = 0; k < 5; ++k) { S[k] += p; if (k < 3) B[k] += p * l[i]; p *= x; }
  }
  // solve [S0 S1 S2; S1 S2 S3; S2 S3 S4] c = B
  double A[3][4] = {{S[0], S[1], S[2], B[0]}, {S[1], S[2], S[3], B[1]}, {S[2], S[3], S[4], B[2]}};
  for (int i = 0; i < 3; ++i) { int p = i; for (int r = i + 1; r < 3; ++r) if (std::fabs(A[r][i]) > std::fabs(A[p][i])) p = r;
    std::swap(A[i], A[p]); for (int r = 0; r < 3; ++r) if (r != i) { double f = A[r][i] / A[i][i]; for (int c = i; c < 4; ++c) A[r][c] -= f * A[i][c]; } }
  double c0 = A[0][3] / A[0][0], c1 = A[1][3] / A[1][1], c2 = A[2][3] / A[2][2];
  double x = 0;  // Newton from r0
  for (int k = 0; k < 20; ++k) { double fv = c0 + c1 * x + c2 * x * x, dv = c1 + 2 * c2 * x; if (dv == 0) break; x -= fv / dv; }
  return std::fabs(x) < 0.2 ? r0 + x : r0;
}

// ---------------- network ring runs -----------------------------------------------------------------------
struct Net {
  int N = 3; std::vector<std::vector<int>> nb;
  static Net ring(int N) { Net n; n.N = N; n.nb.resize(N); for (int i = 0; i < N; ++i) { n.nb[i] = {(i + 1) % N, (i + N - 1) % N}; } if (N == 2) n.nb = {{1}, {0}}; return n; }
  static Net all(int N) { Net n; n.N = N; n.nb.resize(N); for (int i = 0; i < N; ++i) for (int j = 0; j < N; ++j) if (i != j) n.nb[i].push_back(j); return n; }
  double lambda2() const;  // smallest nonzero Laplacian eigenvalue (closed forms)
  bool is_all = false;
};

struct RunCfg { double T = 2000, tail = 500, dt = 0.005, mad_cut_rel = std::pow(PHI, -4), trit_cut = 1 / PHI; bool amp_check = true; };
struct RunOut {
  bool locked = false, synced = false, escaped_tail = false; double t_escape = -1, t_sync = -1, mad = 0, amp = 0, trit = 0, maxabs = 0;
  int clusters = 0;  // connected components of pairwise-synchronised nodes in the tail
  double pair_sync_frac = 0;
};

inline void net_f(const Model& m, const Net& net, double sigma, const std::vector<double>& s, std::vector<double>& o) {
  for (int i = 0; i < net.N; ++i) {
    double x = s[3 * i], y = s[3 * i + 1], z = s[3 * i + 2], cpl = 0;
    for (int j : net.nb[i]) cpl += s[3 * j] - x;
    o[3 * i] = m.alpha * (y - x - m.h(x)) + sigma * cpl;
    o[3 * i + 1] = x - y + z;
    o[3 * i + 2] = -m.beta * y - m.gamma * z;
  }
}

inline std::vector<double> random_ic(int N, unsigned seed) {  // repo IC law (sim/chua_array.initial_state)
  std::mt19937_64 g(seed); std::normal_distribution<double> nd(0, 1);
  std::vector<double> s(3 * N, 0.0);
  for (int i = 0; i < N; ++i) { s[3 * i] = 0.1 + 0.05 * i + 0.01 * nd(g); s[3 * i + 1] = 0.02 * nd(g); }
  return s;
}

inline double single_amp(const Model& m, double T = 2000, double tail = 500, double dt = 0.005) {
  Net n = Net::ring(1); n.nb = {{}};
  std::vector<double> s = {0.1, 0, 0}, k1(3), k2(3), k3(3), k4(3), t(3);
  long N = long(T / dt), t0 = N - long(tail / dt), c = 0; double sx = 0, sxx = 0;
  for (long k = 0; k < N; ++k) {
    if (k >= t0) { sx += s[0]; sxx += s[0] * s[0]; ++c; }
    net_f(m, n, 0, s, k1); for (int j = 0; j < 3; ++j) t[j] = s[j] + .5 * dt * k1[j];
    net_f(m, n, 0, t, k2); for (int j = 0; j < 3; ++j) t[j] = s[j] + .5 * dt * k2[j];
    net_f(m, n, 0, t, k3); for (int j = 0; j < 3; ++j) t[j] = s[j] + dt * k3[j];
    net_f(m, n, 0, t, k4); for (int j = 0; j < 3; ++j) s[j] += dt / 6 * (k1[j] + 2 * k2[j] + 2 * k3[j] + k4[j]);
  }
  return std::sqrt(std::max(0.0, sxx / c - (sx / c) * (sx / c)));
}

inline RunOut net_run(const Model& m, const Net& net, double sigma, std::vector<double> s, const RunCfg& cfg, double amp_ref) {
  const int N = net.N, D = 3 * N;
  std::vector<double> k1(D), k2(D), k3(D), k4(D), t(D);
  long n = long(cfg.T / cfg.dt), t0 = n - long(cfg.tail / cfg.dt), cnt = 0, agree = 0, rail = 0;
  std::vector<double> sx(N, 0), sxx(N, 0), pmad(N * N, 0);
  double mad = 0, mx = 0, t_esc = -1, t_sync = -1;
  for (long k = 0; k < n; ++k) {
    double dmax = 0, xm = 0;
    for (int i = 0; i < N; ++i) { xm = std::max(xm, std::fabs(s[3 * i])); for (int j = i + 1; j < N; ++j) dmax = std::max(dmax, std::fabs(s[3 * i] - s[3 * j])); }
    if (t_esc < 0 && (xm > m.x2 || !std::isfinite(xm))) t_esc = k * cfg.dt;
    if (t_sync < 0 && dmax < 1e-3) t_sync = k * cfg.dt;
    if (!std::isfinite(xm)) break;
    if (k >= t0) {
      mx = std::max(mx, xm); ++cnt;
      int tr0 = s[0] < -1 ? -1 : (s[0] > 1 ? 1 : 0); bool ag = true; double md = 0; int np = 0;
      for (int i = 0; i < N; ++i) {
        double x = s[3 * i]; sx[i] += x; sxx[i] += x * x; if (std::fabs(x) > 7.5) ++rail;
        int tr = x < -1 ? -1 : (x > 1 ? 1 : 0); ag = ag && tr == tr0;
        for (int j = i + 1; j < N; ++j) { double d = std::fabs(x - s[3 * j]); md += d; pmad[i * N + j] += d; ++np; }
      }
      agree += ag; mad += np ? md / np : 0;
    }
    net_f(m, net, sigma, s, k1); for (int j = 0; j < D; ++j) t[j] = s[j] + .5 * cfg.dt * k1[j];
    net_f(m, net, sigma, t, k2); for (int j = 0; j < D; ++j) t[j] = s[j] + .5 * cfg.dt * k2[j];
    net_f(m, net, sigma, t, k3); for (int j = 0; j < D; ++j) t[j] = s[j] + cfg.dt * k3[j];
    net_f(m, net, sigma, t, k4); for (int j = 0; j < D; ++j) s[j] += cfg.dt / 6 * (k1[j] + 2 * k2[j] + 2 * k3[j] + k4[j]);
  }
  RunOut r;
  if (cnt == 0) { r.escaped_tail = true; return r; }
  for (int i = 0; i < N; ++i) r.amp += std::sqrt(std::max(0.0, sxx[i] / cnt - (sx[i] / cnt) * (sx[i] / cnt))) / N;
  r.mad = mad / cnt; r.trit = double(agree) / cnt; r.maxabs = mx; r.t_escape = t_esc; r.t_sync = t_sync; r.escaped_tail = mx >= m.x2;
  double cut = amp_ref * cfg.mad_cut_rel, railed = double(rail) / (double(N) * cnt);
  r.synced = r.mad <= cut && r.trit >= cfg.trit_cut && r.amp >= cut && railed < 0.05;
  r.locked = r.synced && (!cfg.amp_check || !r.escaped_tail);
  // clusters: union-find on pairs with mean |xi-xj| <= cut
  std::vector<int> p(N); std::iota(p.begin(), p.end(), 0);
  std::function<int(int)> fd = [&](int x) { return p[x] == x ? x : p[x] = fd(p[x]); };
  int ps = 0, pt = 0;
  for (int i = 0; i < N; ++i) for (int j = i + 1; j < N; ++j) { ++pt; if (pmad[i * N + j] / cnt <= cut) { ++ps; p[fd(i)] = fd(j); } }
  for (int i = 0; i < N; ++i) r.clusters += fd(i) == i;
  r.pair_sync_frac = pt ? double(ps) / pt : 1;
  return r;
}

// ---------------- simple thread pool parallel_for -------------------------------------------------------------
inline void parallel_for(size_t n, const std::function<void(size_t)>& fn, unsigned nth = std::thread::hardware_concurrency()) {
  std::atomic<size_t> next{0}; std::vector<std::thread> th;
  for (unsigned t = 0; t < std::max(1u, nth); ++t) th.emplace_back([&] { for (size_t i; (i = next++) < n;) fn(i); });
  for (auto& t : th) t.join();
}

}  // namespace eb
