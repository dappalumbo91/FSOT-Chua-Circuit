// LOCK PJ engine: x''' = -g x'' - B x' + G|x| - 1. RK4 h = 0.002, transient 500, two-trajectory lambda1.
// usage: pj scan            -> all 49 FSOT (B,G) candidates, 64 seeds each (LOCK PJ selection rule)
//        pj one B G x y z [T] -> one trajectory (prints bounded, l1, xmin, xmax, f_Hz and the final state)
//        pj mc B G x y z      -> 32 tolerance draws (+-1 % on g, B, G)
#include <cmath>
#include <cstdio>
#include <cstdlib>
#include <random>
#include <string>
#include <vector>
#include <algorithm>
#include <array>
static const double g0 = 0.42804344605980688;
struct R { int bnd; double l1, mn, mx, f; double v[3]; };
static R run(double g, double B, double G, double x, double y, double z, double T) {
  auto f = [&](const double* v, double* d) { d[0] = v[1]; d[1] = v[2]; d[2] = -g * v[2] - B * v[1] + G * std::fabs(v[0]) - 1; };
  auto rk4 = [&](double* v, double h) { double k1[3], k2[3], k3[3], k4[3], t[3];
    f(v, k1); for (int i = 0; i < 3; ++i) t[i] = v[i] + h / 2 * k1[i]; f(t, k2); for (int i = 0; i < 3; ++i) t[i] = v[i] + h / 2 * k2[i];
    f(t, k3); for (int i = 0; i < 3; ++i) t[i] = v[i] + h * k3[i]; f(t, k4); for (int i = 0; i < 3; ++i) v[i] += h / 6 * (k1[i] + 2 * k2[i] + 2 * k3[i] + k4[i]); };
  double v[3] = {x, y, z}, h = 0.002, w[3], d0 = 1e-8, sum = 0, mx = -1e9, mn = 1e9, prev = 0, lim = 50 / G; long cr = 0; bool bnd = true;
  for (long i = 0; i < long(500 / h) && bnd; ++i) { rk4(v, h); if (std::fabs(v[0]) > lim) bnd = false; }
  for (int i = 0; i < 3; ++i) w[i] = v[i]; w[0] += d0; long per = long(1 / h);
  for (long i = 0; i < long(T / h) && bnd; ++i) {
    rk4(v, h); rk4(w, h); if (std::fabs(v[0]) > lim) { bnd = false; break; }
    mx = std::max(mx, v[0]); mn = std::min(mn, v[0]); if (v[1] > 0 && prev <= 0) ++cr; prev = v[1];
    if ((i + 1) % per == 0) { double dd = 0; for (int k = 0; k < 3; ++k) dd += (w[k] - v[k]) * (w[k] - v[k]); dd = std::sqrt(dd); if (dd == 0) dd = 1e-300; sum += std::log(dd / d0); for (int k = 0; k < 3; ++k) w[k] = v[k] + (w[k] - v[k]) * d0 / dd; } }
  return {int(bnd), bnd ? sum / T : NAN, mn, mx, cr / T / 180e-6, {v[0], v[1], v[2]}};
}
int main(int ac, char** av) {
  std::string mode = ac > 1 ? av[1] : "scan";
  const char* nm[7] = {"1", "K", "Theta", "kappa", "kappa/gamma_rel", "gamma_rel", "S_EM"};
  const double fs[7] = {1.0, 0.42010876364988792, 0.91751027120648765, 0.31463253730207974, 0.73504813634763333, g0, 0.9557285700955828};
  if (mode == "scan") {
    printf("B\tG\tchi\tn_chaotic/64\tn_bounded/64\tl1_median\tf_Hz_median\txmin\txmax\tbest_seed\n");
    for (int ib = 0; ib < 7; ++ib) for (int ig = 0; ig < 7; ++ig) {
      double B = fs[ib], G = fs[ig]; std::mt19937 rg(1); std::uniform_real_distribution<double> ux(-2.5 / G, 2.5 / G), uy(-1 / G, 1 / G);
      std::vector<std::array<double, 3>> S(64); for (auto& s : S) { s[0] = ux(rg); s[1] = uy(rg); s[2] = uy(rg); }
      std::vector<R> r(64);
      #pragma omp parallel for schedule(dynamic)
      for (int k = 0; k < 64; ++k) r[k] = run(g0, B, G, S[k][0], S[k][1], S[k][2], 3000);
      int nc = 0, nb = 0, bs = -1; std::vector<double> L, F; double mn = 1e9, mx = -1e9;
      for (int k = 0; k < 64; ++k) { nb += r[k].bnd; if (r[k].bnd && r[k].l1 > 0.005) { ++nc; L.push_back(r[k].l1); F.push_back(r[k].f); mn = std::min(mn, r[k].mn); mx = std::max(mx, r[k].mx); if (bs < 0) bs = k; } }
      std::sort(L.begin(), L.end()); std::sort(F.begin(), F.end());
      printf("%s\t%s\t%.4f\t%d\t%d\t%.4f\t%.1f\t%.4f\t%.4f\t%d(%.4f,%.4f,%.4f)\n", nm[ib], nm[ig], g0 * B / G, nc, nb, nc ? L[nc / 2] : NAN, nc ? F[nc / 2] : NAN, nc ? mn : NAN, nc ? mx : NAN, bs,
             bs >= 0 ? S[bs][0] : 0, bs >= 0 ? S[bs][1] : 0, bs >= 0 ? S[bs][2] : 0); fflush(stdout);
    }
    return 0;
  }
  double B = atof(av[2]), G = atof(av[3]), x = atof(av[4]), y = atof(av[5]), z = atof(av[6]);
  if (mode == "one") { double T = ac > 7 ? atof(av[7]) : 3000; R r = run(g0, B, G, x, y, z, T);
    printf("bounded=%d\tl1=%.4f\txmin=%.4f\txmax=%.4f\tf_Hz=%.1f\tend=(%.6f,%.6f,%.6f)\n", r.bnd, r.l1, r.mn, r.mx, r.f, r.v[0], r.v[1], r.v[2]); return 0; }
  if (mode == "mc") { std::mt19937 rg(7); std::uniform_real_distribution<double> u(-0.01, 0.01); int ok = 0;
    std::vector<std::array<double, 3>> P(32); for (auto& p : P) { p[0] = 1 + u(rg); p[1] = 1 + u(rg); p[2] = 1 + u(rg); }
    std::vector<R> r(32);
    #pragma omp parallel for
    for (int k = 0; k < 32; ++k) r[k] = run(g0 * P[k][0], B * P[k][1], G * P[k][2], x, y, z, 3000);
    for (int k = 0; k < 32; ++k) { int c = r[k].bnd && r[k].l1 > 0.005; ok += c; printf("draw%02d\t%.4f\t%.4f\t%.4f\tbounded=%d\tl1=%.4f\n", k, P[k][0], P[k][1], P[k][2], r[k].bnd, r[k].l1); }
    printf("MC chaotic %d/32\n", ok); }
}
