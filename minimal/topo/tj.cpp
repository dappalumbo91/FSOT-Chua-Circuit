// LOCK T engine: x''' = -A x'' - B x' - C x + s*N(x) + E, N in {sgn, abs}; RK4 + two-trajectory Lyapunov (lambda1) + tangent-free sum check via divergence.
// usage: tj A B C s N(sgn|abs) E [nic=4] [T=4000]   prints ic l1 xmin xmax meanx f_per_tau bounded
#include <cmath>
#include <cstdio>
#include <cstdlib>
#include <string>
#include <algorithm>
struct P { double A, B, C, s, E; bool sg; };
static void f(const double* v, double* d, const P& p) {
  double N = p.sg ? (v[0] > 0 ? 1.0 : (v[0] < 0 ? -1.0 : 0.0)) : std::fabs(v[0]);
  d[0] = v[1]; d[1] = v[2]; d[2] = -p.A * v[2] - p.B * v[1] - p.C * v[0] + p.s * N + p.E;
}
static void rk4(double* v, double h, const P& p) { double k1[3], k2[3], k3[3], k4[3], t[3];
  f(v, k1, p); for (int i = 0; i < 3; ++i) t[i] = v[i] + h / 2 * k1[i]; f(t, k2, p); for (int i = 0; i < 3; ++i) t[i] = v[i] + h / 2 * k2[i];
  f(t, k3, p); for (int i = 0; i < 3; ++i) t[i] = v[i] + h * k3[i]; f(t, k4, p); for (int i = 0; i < 3; ++i) v[i] += h / 6 * (k1[i] + 2 * k2[i] + 2 * k3[i] + k4[i]); }
int main(int ac, char** av) {
  if (ac < 7) return 1;
  P p{atof(av[1]), atof(av[2]), atof(av[3]), atof(av[4]), atof(av[6]), std::string(av[5]) == "sgn"};
  int nic = ac > 7 ? atoi(av[7]) : 4; double T = ac > 8 ? atof(av[8]) : 4000, h = 0.002, Ttr = 500;
  double x0 = ac > 11 ? atof(av[9]) : NAN, y0 = ac > 11 ? atof(av[10]) : 0, z0 = ac > 11 ? atof(av[11]) : 0, rad = ac > 12 ? atof(av[12]) : 0.02;
  for (int ic = 0; ic < nic; ++ic) {
    double v[3] = {0.3 + 0.37 * ic * (ic % 2 ? -1 : 1), 0.1 * ic, -0.2};
    if (!std::isnan(x0)) { double o[8][3] = {{1,1,1},{1,1,-1},{1,-1,1},{1,-1,-1},{-1,1,1},{-1,1,-1},{-1,-1,1},{-1,-1,-1}}; v[0] = x0 + rad * o[ic % 8][0]; v[1] = y0 + rad * o[ic % 8][1]; v[2] = z0 + rad * o[ic % 8][2]; }
    double ww_unused, w[3], d0 = 1e-8, sum = 0, mx = -1e9, mn = 1e9, mean = 0, prev = 0; long cr = 0, n = 0; bool bnd = true;
    for (long i = 0; i < long(Ttr / h) && bnd; ++i) { rk4(v, h, p); if (std::fabs(v[0]) > 1e3) bnd = false; }
    for (int i = 0; i < 3; ++i) w[i] = v[i]; w[0] += d0;
    long per = long(1 / h);
    for (long i = 0; i < long(T / h) && bnd; ++i) {
      rk4(v, h, p); rk4(w, h, p); if (std::fabs(v[0]) > 1e3) { bnd = false; break; }
      mx = std::max(mx, v[0]); mn = std::min(mn, v[0]); mean += v[0]; ++n; if (v[1] > 0 && prev <= 0) ++cr; prev = v[1];
      if ((i + 1) % per == 0) { double dd = 0; for (int k = 0; k < 3; ++k) dd += (w[k] - v[k]) * (w[k] - v[k]); dd = std::sqrt(dd); if (dd == 0) dd = 1e-300;
        sum += std::log(dd / d0); for (int k = 0; k < 3; ++k) w[k] = v[k] + (w[k] - v[k]) * d0 / dd; } }
    printf("%d\t%.4f\t%.4f\t%.4f\t%.4f\t%.5f\t%d\n", ic, bnd ? sum / T : NAN, mn, mx, n ? mean / n : NAN, cr / T, int(bnd));
  }
}
