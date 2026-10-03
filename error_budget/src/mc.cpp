// mc.cpp — "standard circuit-design" prediction of the 3-ring sync threshold from datasheet-only inputs
// and Monte Carlo over component tolerances (C++20). Physical Kennedy circuit, normalised by NOMINAL
// tau_n = R_n C2_n, V_n = Bp1_n (=1 V), I_n = V_n/R_n:
//   x' = (C2n/C1)[(Rn/R)(y-x) - Rn g(x Vn)/Vn + sum_j (Rn/Rc)(x_j-x)]
//   y' = (C2n/C2)[(Rn/R)(x-y) + z],   z' = (Rn^2 C2n/L)[-y - (r/Rn) z]
// g: Kennedy NIC pair, Ga=-R2/(R1R3)-R5/(R4R6), Gb=1/R4-R2/(R1R3), Gc=1/R1+1/R4,
//    Bp1=Esat R6/(R5+R6), Bp2=Esat R3/(R2+R3) (Esat+ for x>0, Esat- for x<0).
// With all values nominal and r = r0 this is exactly the eb/fsot_chua dimensionless model; sigma_equiv = alpha_n Rn/Rc.
#include <cmath>
#include <cstdio>
#include <cstdlib>
#include <map>
#include <random>
#include <string>
#include <vector>
#include "eb.hpp"
using namespace eb;

struct Phys { double R = 1800, L = 22e-3, C1 = 10e-9, C2 = 100e-9, r = 0, R1 = 220, R2 = 220, R3 = 2200, R4 = 22000, R5 = 22000, R6 = 3300,
              Ep = 23.0 / 3, Em = 23.0 / 3; };
static const Phys NOM{};
struct NP { double k1, k2, gR, kb, rr, a, b, c, p1, p2, m1, m2; };  // m1,m2: negative-side breakpoints (positive numbers)
static NP np_of(const Phys& p) {
  NP q; double Rn = NOM.R, C2n = NOM.C2, Vn = NOM.Ep * NOM.R6 / (NOM.R5 + NOM.R6);
  q.k1 = C2n / p.C1; q.k2 = C2n / p.C2; q.gR = Rn / p.R; q.kb = Rn * Rn * C2n / p.L; q.rr = p.r / Rn;
  double Ga = -p.R2 / (p.R1 * p.R3) - p.R5 / (p.R4 * p.R6), Gb = 1 / p.R4 - p.R2 / (p.R1 * p.R3), Gc = 1 / p.R1 + 1 / p.R4;
  q.a = Rn * Ga; q.b = Rn * Gb; q.c = Rn * Gc;
  q.p1 = p.Ep * p.R6 / (p.R5 + p.R6) / Vn; q.p2 = p.Ep * p.R3 / (p.R2 + p.R3) / Vn;
  q.m1 = p.Em * p.R6 / (p.R5 + p.R6) / Vn; q.m2 = p.Em * p.R3 / (p.R2 + p.R3) / Vn;
  return q;
}
static inline double hN(const NP& q, double x) {  // Rn g(x Vn)/Vn
  if (x >= 0) { if (x < q.p1) return q.a * x; if (x < q.p2) return q.a * q.p1 + q.b * (x - q.p1); return q.a * q.p1 + q.b * (q.p2 - q.p1) + q.c * (x - q.p2); }
  double ax = -x; if (ax < q.m1) return q.a * x; if (ax < q.m2) return -(q.a * q.m1 + q.b * (ax - q.m1)); return -(q.a * q.m1 + q.b * (q.m2 - q.m1) + q.c * (ax - q.m2));
}
static inline double hpN(const NP& q, double x) { double ax = std::fabs(x), b1 = x >= 0 ? q.p1 : q.m1, b2 = x >= 0 ? q.p2 : q.m2; return ax < b1 ? q.a : (ax < b2 ? q.b : q.c); }
static inline void fN(const NP& q, const double* u, double* o) {
  o[0] = q.k1 * (q.gR * (u[1] - u[0]) - hN(q, u[0])); o[1] = q.k2 * (q.gR * (u[0] - u[1]) + u[2]); o[2] = q.kb * (-u[1] - q.rr * u[2]);
}
// MSF in kappa = Rn/Rc: transverse row0 gets -k1*kappa*lam2. Returns lam per kappa, and single-node diagnostics.
struct MsfR { std::vector<double> lam; double maxabs, minx, maxx; };
static MsfR msfN(const NP& q, const std::vector<double>& kap, double lam2, double T, double dt, double trans) {
  double s[3] = {0.1, 0, 0}; size_t M = kap.size(); std::vector<double> d(3 * M), acc(M, 0), j[4] = {std::vector<double>(3 * M), std::vector<double>(3 * M), std::vector<double>(3 * M), std::vector<double>(3 * M)}, u(3 * M);
  for (size_t k = 0; k < M; ++k) { d[3 * k] = 1; d[3 * k + 1] = .3; d[3 * k + 2] = .1; }
  auto J = [&](const double* st, const double* v, double* o) { double hp = hpN(q, st[0]);
    for (size_t k = 0; k < M; ++k) { const double* w = v + 3 * k; double* r = o + 3 * k;
      r[0] = q.k1 * (-q.gR * w[0] - hp * w[0] + q.gR * w[1]) - q.k1 * kap[k] * lam2 * w[0];
      r[1] = q.k2 * (q.gR * (w[0] - w[1]) + w[2]); r[2] = q.kb * (-w[1] - q.rr * w[2]); } };
  long n = long((T + trans) / dt), nt = long(trans / dt); double mx = 0, mn = 1e9, Mx = -1e9;
  for (long it = 0; it < n; ++it) {
    double k1[3], k2[3], k3[3], k4[3], t[3];
    fN(q, s, k1); J(s, d.data(), j[0].data());
    for (int i = 0; i < 3; ++i) t[i] = s[i] + .5 * dt * k1[i]; for (size_t z = 0; z < 3 * M; ++z) u[z] = d[z] + .5 * dt * j[0][z];
    fN(q, t, k2); J(t, u.data(), j[1].data());
    for (int i = 0; i < 3; ++i) t[i] = s[i] + .5 * dt * k2[i]; for (size_t z = 0; z < 3 * M; ++z) u[z] = d[z] + .5 * dt * j[1][z];
    fN(q, t, k3); J(t, u.data(), j[2].data());
    for (int i = 0; i < 3; ++i) t[i] = s[i] + dt * k3[i]; for (size_t z = 0; z < 3 * M; ++z) u[z] = d[z] + dt * j[2][z];
    fN(q, t, k4); J(t, u.data(), j[3].data());
    for (int i = 0; i < 3; ++i) s[i] += dt / 6 * (k1[i] + 2 * k2[i] + 2 * k3[i] + k4[i]);
    for (size_t z = 0; z < 3 * M; ++z) d[z] += dt / 6 * (j[0][z] + 2 * j[1][z] + 2 * j[2][z] + j[3][z]);
    if (it >= nt) { mx = std::max(mx, std::fabs(s[0])); mn = std::min(mn, s[0]); Mx = std::max(Mx, s[0]); }
    for (size_t k = 0; k < M; ++k) { double* w = &d[3 * k]; double nr = std::sqrt(w[0] * w[0] + w[1] * w[1] + w[2] * w[2]); if (it >= nt) acc[k] += std::log(nr); w[0] /= nr; w[1] /= nr; w[2] /= nr; }
  }
  for (auto& v : acc) v /= T; return {acc, mx, mn, Mx};
}
// classify isolated node: 0=fixed point/decay, 1=double scroll (both signs, chaotic), 2=single scroll / periodic, 3=outer cycle
static int classify(const NP& q, const MsfR& m) {
  if (m.maxabs < 1e-3) return 0;
  if (m.maxabs > std::min(q.p2, q.m2)) return 3;
  if (m.minx < -std::min(q.m1, 1.0) * 0.5 && m.maxx > std::min(q.p1, 1.0) * 0.5 && m.lam[0] > 0.01) return 1;
  return 2;
}
static double sigc_of(const NP& q, double* lam1, int* cls, double T = 6000) {
  std::vector<double> kap; kap.push_back(0); for (double s = 0.30; s <= 6.0001; s += 0.05) kap.push_back(s / 10.0);
  auto r = msfN(q, kap, 3, T, 0.005, 300); *lam1 = r.lam[0]; *cls = classify(q, r);
  std::vector<double> ks(kap.begin() + 1, kap.end()), ls(r.lam.begin() + 1, r.lam.end());
  int idx = -1; for (size_t i = 0; i + 1 < ls.size(); ++i) if (ls[i] > 0 && ls[i + 1] <= 0) idx = int(i);
  if (idx < 0) return ls.front() <= 0 ? 0.0 : NAN;
  // local refine: fine grid +-0.06 in sigma around the crossing
  double s0 = 10 * (ks[idx] + (ks[idx + 1] - ks[idx]) * ls[idx] / (ls[idx] - ls[idx + 1]));
  std::vector<double> kf, sf; for (int i = -6; i <= 6; ++i) { sf.push_back(s0 + 0.01 * i); kf.push_back(sf.back() / 10); }
  auto rf = msfN(q, kf, 3, T, 0.005, 300); double root = fit_root(sf, rf.lam); return std::isnan(root) ? s0 : root;
}
// heterogeneous 3-ring lock (bench-like): per-node NP, per-edge kappa_ij
static bool ring_lock(const std::vector<NP>& nq, const double kc[3][3], unsigned seed, double T = 2000, double tail = 500, double dt = 0.005) {
  auto s = random_ic(3, seed); std::vector<double> k1(9), k2(9), k3(9), k4(9), t(9);
  auto F = [&](const std::vector<double>& u, std::vector<double>& o) {
    for (int i = 0; i < 3; ++i) { fN(nq[i], &u[3 * i], &o[3 * i]); double c = 0; for (int j = 0; j < 3; ++j) if (j != i) c += kc[i][j] * (u[3 * j] - u[3 * i]); o[3 * i] += nq[i].k1 * c; } };
  long N = long(T / dt), t0 = N - long(tail / dt); double mad = 0, amp = 0, mx = 0; long cnt = 0; double bmin = 1e9; for (auto& q : nq) bmin = std::min({bmin, q.p2, q.m2});
  for (long k = 0; k < N; ++k) {
    F(s, k1); for (int j = 0; j < 9; ++j) t[j] = s[j] + .5 * dt * k1[j]; F(t, k2); for (int j = 0; j < 9; ++j) t[j] = s[j] + .5 * dt * k2[j];
    F(t, k3); for (int j = 0; j < 9; ++j) t[j] = s[j] + dt * k3[j]; F(t, k4); for (int j = 0; j < 9; ++j) s[j] += dt / 6 * (k1[j] + 2 * k2[j] + 2 * k3[j] + k4[j]);
    if (!std::isfinite(s[0]) || std::fabs(s[0]) > 1e3) return false;
    if (k >= t0) { double m = (s[0] + s[3] + s[6]) / 3; for (int i = 0; i < 3; ++i) { mad += std::fabs(s[3 * i] - m); amp += std::fabs(s[3 * i]); mx = std::max(mx, std::fabs(s[3 * i])); } ++cnt; }
  }
  return mx < bmin && amp > 0 && mad / amp < std::pow(PHI, -4) && amp / (3.0 * cnt) > std::pow(PHI, -4);
}
static std::map<std::string, std::string> parse(int ac, char** av) { std::map<std::string, std::string> m; for (int i = 2; i < ac; ++i) { std::string s = av[i]; auto e = s.find('='); if (e != std::string::npos) m[s.substr(0, e)] = s.substr(e + 1); } return m; }
static double G(const std::map<std::string, std::string>& m, const char* k, double d) { auto it = m.find(k); return it == m.end() ? d : std::atof(it->second.c_str()); }

int main(int ac, char** av) {
  if (ac < 2) { std::fprintf(stderr, "mc r0scan|mc|point ...\n"); return 1; }
  std::string cmd = av[1]; auto A = parse(ac, av);
  if (cmd == "point") {  // single physical point: r= L= ...
    Phys p; p.r = G(A, "r", 0); p.L = G(A, "L", p.L); p.R = G(A, "R", p.R); p.Ep = G(A, "Ep", p.Ep); p.Em = G(A, "Em", p.Em);
    double l1; int cls; double sc = sigc_of(np_of(p), &l1, &cls, G(A, "T", 10000));
    std::printf("r=%.4f L=%.5g R=%.1f sigc=%.5f Rc*=%.1f lam1=%.5f class=%d\n", p.r, p.L, p.R, sc, 10 * NOM.R / sc, l1, cls); return 0;
  }
  if (cmd == "r0scan") {
    double lo = G(A, "lo", 0), hi = G(A, "hi", 90), st = G(A, "step", 2); std::vector<double> rs; for (double r = lo; r <= hi + 1e-9; r += st) rs.push_back(r);
    std::vector<std::string> out(rs.size());
    parallel_for(int(rs.size()), [&](int i) { Phys p; p.r = rs[i]; double l1; int cls; double sc = sigc_of(np_of(p), &l1, &cls, G(A, "T", 6000));
      char b[256]; std::snprintf(b, 256, "%.3f\t%.6f\t%.5f\t%.5f\t%d\t%.1f", rs[i], Model::gamma_from_r0(rs[i]), sc, l1, cls, 10 * NOM.R / sc); out[i] = b; });
    std::printf("# r_ohm\tgamma\tsigc_msf\tlam1_node\tclass(0=fp,1=double-scroll,2=other,3=outer)\tRc*_ohm\n"); for (auto& s : out) std::printf("%s\n", s.c_str()); return 0;
  }
  if (cmd == "mc") {
    // tolerances are +-tol as UNIFORM half-widths (worst-case style); dist=normal uses tol as 3 sigma
    int n = int(G(A, "n", 400)); double tR = G(A, "tolR", 0.01), tC = G(A, "tolC", 0.05), tL = G(A, "tolL", 0.10), tE = G(A, "tolE", 0.0);
    double rlo = G(A, "rlo", 0), rhi = G(A, "rhi", 0); bool normal = A.count("dist") && A["dist"] == "normal"; bool ring = G(A, "ring", 0) != 0;
    unsigned seed0 = unsigned(G(A, "seed", 1)); bool hetero = G(A, "hetero", 1) != 0;
    std::vector<std::string> out(n);
    parallel_for(n, [&](int k) {
      std::mt19937_64 g(seed0 * 1000003ULL + k); std::uniform_real_distribution<double> U(-1, 1); std::normal_distribution<double> Nd(0, 1);
      auto dev = [&](double t) { return normal ? t / 3 * Nd(g) : t * U(g); };
      auto draw = [&]() { Phys p; p.R *= 1 + dev(tR); p.R1 *= 1 + dev(tR); p.R2 *= 1 + dev(tR); p.R3 *= 1 + dev(tR); p.R4 *= 1 + dev(tR); p.R5 *= 1 + dev(tR); p.R6 *= 1 + dev(tR);
        p.C1 *= 1 + dev(tC); p.C2 *= 1 + dev(tC); p.L *= 1 + dev(tL); std::uniform_real_distribution<double> Ur(rlo, rhi); p.r = rhi > rlo ? Ur(g) : rlo;
        double e = dev(tE); p.Ep *= 1 + e / 2; p.Em *= 1 - e / 2; return p; };
      Phys p0 = draw(); NP q0 = np_of(p0); double l1; int cls; double sc = sigc_of(q0, &l1, &cls);
      char b[512]; int w = std::snprintf(b, 512, "%d\t%.2f\t%.4g\t%.4g\t%.4g\t%.3f\t%.6f\t%.5f\t%d", k, p0.R, p0.C1, p0.C2, p0.L, p0.r, p0.Ep / p0.Em, sc, cls);
      if (ring) {  // three independently drawn nodes + 3 coupling resistors (tolR); threshold on sigma grid, majority of 3 seeds
        std::vector<NP> nq(3); for (int i = 0; i < 3; ++i) nq[i] = hetero ? np_of(draw()) : q0;
        double ce[3]; for (double& c : ce) c = 1 + dev(tR);
        double thr = NAN; int consec = 0;
        for (double s = 1.0; s <= 3.0001; s += 0.025) {
          double kc[3][3] = {{0, ce[0], ce[2]}, {ce[0], 0, ce[1]}, {ce[2], ce[1], 0}}; for (auto& r : kc) for (double& v : r) v *= s / 10.0;
          int ok = 0; for (unsigned sd = 1; sd <= 3; ++sd) ok += ring_lock(nq, kc, sd);
          if (ok >= 2) { if (consec == 0) thr = s; if (++consec >= 4) break; } else { consec = 0; thr = NAN; }
        }
        std::snprintf(b + w, 512 - w, "\t%.4f", thr);
      }
      out[k] = b; });
    std::printf("# k\tR\tC1\tC2\tL\tr_ohm\tEp/Em\tsigc_msf_equiv\tclass%s\n", ring ? "\tring_thr_equiv" : ""); for (auto& s : out) std::printf("%s\n", s.c_str()); return 0;
  }
  if (cmd == "dump") {  // single node x(t), every 'every' steps, after transient
    Phys p; p.r = G(A, "r", 0); NP q = np_of(p); double dt = 0.005, T = G(A, "T", 20000), tr = G(A, "trans", 500); int ev = int(G(A, "every", 10));
    double s[3] = {0.1, 0, 0}, k1[3], k2[3], k3[3], k4[3], t[3]; long n = long((T + tr) / dt), nt = long(tr / dt);
    for (long it = 0; it < n; ++it) { fN(q, s, k1); for (int i = 0; i < 3; ++i) t[i] = s[i] + .5 * dt * k1[i]; fN(q, t, k2); for (int i = 0; i < 3; ++i) t[i] = s[i] + .5 * dt * k2[i];
      fN(q, t, k3); for (int i = 0; i < 3; ++i) t[i] = s[i] + dt * k3[i]; fN(q, t, k4); for (int i = 0; i < 3; ++i) s[i] += dt / 6 * (k1[i] + 2 * k2[i] + 2 * k3[i] + k4[i]);
      if (it >= nt && (it - nt) % ev == 0) std::printf("%.6f %.6f %.6f\n", s[0], s[1], s[2]); }
    return 0;
  }
  return 1;
}
