// LOCK PC engine: dimensionless Kennedy-Chua node at Branch L (alpha = C2/C1, beta = R^2 C2/L, gamma = beta r0/R, NIC slopes from the BOM).
// usage: pc basin | pc mc | pc one x y z
#include <cmath>
#include <cstdio>
#include <cstdlib>
#include <random>
#include <string>
#include <vector>
#include <array>
#include <algorithm>
struct M { double al, be, ga, a, b, c, x2;
  double h(double x) const { double ax = std::fabs(x), s = x < 0 ? -1 : 1; if (ax < 1) return a * x; if (ax < x2) return s * (a + b * (ax - 1)); return s * (a + b * (x2 - 1) + c * (ax - x2)); } };
static M make(double R, double C1, double C2, double L, double r0, double R1, double R2, double R3, double R4, double R5, double R6) {
  double Ga = -R2 / (R1 * R3) - R5 / (R4 * R6), Gb = -R2 / (R1 * R3) + 1 / R4, Gc = 1 / R1 + 1 / R4;
  double Esat = 1.0 * (22000.0 + 3300.0) / 3300.0;  // rail fixed by the nominal BOM (Bp1 = 1 V); toleranced dividers move the breakpoints
  double Bp1 = Esat * R6 / (R5 + R6), Bp2 = Esat * R3 / (R2 + R3);
  M m; m.al = C2 / C1; m.be = R * R * C2 / L; m.ga = m.be * r0 / R; m.a = R * Ga; m.b = R * Gb; m.c = R * Gc; m.x2 = Bp2 / Bp1;
  // rescale x by Bp1: the breakpoint stays at 1 in units of Bp1
  return m; }
struct Res { int ds; double l1, mx; int pos, neg; double f; };
static Res run(const M& m, double x, double y, double z, double T = 2000, double Ttr = 200) {
  auto f = [&](const double* v, double* d) { d[0] = m.al * (v[1] - v[0] - m.h(v[0])); d[1] = v[0] - v[1] + v[2]; d[2] = -m.be * v[1] - m.ga * v[2]; };
  auto rk4 = [&](double* v, double h) { double k1[3], k2[3], k3[3], k4[3], t[3];
    f(v, k1); for (int i = 0; i < 3; ++i) t[i] = v[i] + h / 2 * k1[i]; f(t, k2); for (int i = 0; i < 3; ++i) t[i] = v[i] + h / 2 * k2[i];
    f(t, k3); for (int i = 0; i < 3; ++i) t[i] = v[i] + h * k3[i]; f(t, k4); for (int i = 0; i < 3; ++i) v[i] += h / 6 * (k1[i] + 2 * k2[i] + 2 * k3[i] + k4[i]); };
  double v[3] = {x, y, z}, h = 0.005, w[3], d0 = 1e-8, sum = 0, mx = 0, prev = 0; int pos = 0, neg = 0; long cr = 0;
  for (long i = 0; i < long(Ttr / h); ++i) rk4(v, h);
  for (int i = 0; i < 3; ++i) w[i] = v[i]; w[0] += d0; long per = long(1 / h);
  for (long i = 0; i < long(T / h); ++i) { rk4(v, h); rk4(w, h); mx = std::max(mx, std::fabs(v[0])); pos += v[0] > 1; neg += v[0] < -1;
    if (v[1] > 0 && prev <= 0) ++cr; prev = v[1];
    if ((i + 1) % per == 0) { double dd = 0; for (int k = 0; k < 3; ++k) dd += (w[k] - v[k]) * (w[k] - v[k]); dd = std::sqrt(dd); if (dd == 0) dd = 1e-300; sum += std::log(dd / d0); for (int k = 0; k < 3; ++k) w[k] = v[k] + (w[k] - v[k]) * d0 / dd; } }
  double l1 = sum / T; int ds = l1 > 0.05 && mx < m.x2 && pos > 0 && neg > 0;
  return {ds, l1, mx, pos, neg, cr / T / 180e-6}; }
int main(int ac, char** av) {
  const double r0 = 18.4400497592861384; std::string mode = ac > 1 ? av[1] : "one";
  M nom = make(1800, 10e-9, 100e-9, 22e-3, r0, 220, 220, 2200, 22000, 22000, 3300);
  printf("# alpha=%.4f beta=%.4f gamma=%.6f a=%.6f b=%.6f c=%.6f x2=%.4f\n", nom.al, nom.be, nom.ga, nom.a, nom.b, nom.c, nom.x2);
  if (mode == "one") { double x = ac > 2 ? atof(av[2]) : 0.1, y = ac > 3 ? atof(av[3]) : 0, z = ac > 4 ? atof(av[4]) : 0; Res r = run(nom, x, y, z);
    printf("double_scroll=%d\tl1=%.4f\tmax|x|=%.4f\tf_Hz=%.1f\n", r.ds, r.l1, r.mx, r.f); return 0; }
  if (mode == "basin") { std::mt19937 g(1); std::uniform_real_distribution<double> ux(-6, 6), uy(-1, 1); std::vector<std::array<double, 3>> S(64); for (auto& s : S) { s[0] = ux(g); s[1] = uy(g); s[2] = ux(g); }
    std::vector<Res> r(64);
    #pragma omp parallel for schedule(dynamic)
    for (int k = 0; k < 64; ++k) r[k] = run(nom, S[k][0], S[k][1], S[k][2]);
    int n = 0; for (int k = 0; k < 64; ++k) { n += r[k].ds; printf("seed%02d\t%.3f\t%.3f\t%.3f\tds=%d\tl1=%.4f\tmax=%.3f\tf=%.1f\n", k, S[k][0], S[k][1], S[k][2], r[k].ds, r[k].l1, r[k].mx, r[k].f); }
    printf("BASIN double scroll %d/64\n", n); return 0; }
  if (mode == "mc") { std::mt19937 g(7); auto U = [&](double t) { return 1 + std::uniform_real_distribution<double>(-t, t)(g); };
    std::vector<M> P; for (int k = 0; k < 64; ++k) { double L = 22e-3 * U(0.012), C1 = 10e-9 * U(0.01), R = 1800 * U(0.01), C2 = 100e-9 * U(0.045), rr = r0 + std::uniform_real_distribution<double>(-0.33, 0.33)(g);
      double q[6]; double nomr[6] = {220, 220, 2200, 22000, 22000, 3300}; for (int i = 0; i < 6; ++i) q[i] = nomr[i] * U(0.01); P.push_back(make(R, C1, C2, L, rr, q[0], q[1], q[2], q[3], q[4], q[5])); }
    std::vector<Res> r(64);
    #pragma omp parallel for schedule(dynamic)
    for (int k = 0; k < 64; ++k) r[k] = run(P[k], 0.1, 0, 0);
    int n = 0; for (int k = 0; k < 64; ++k) n += r[k].ds; printf("MC double scroll %d/64\n", n); }
}
