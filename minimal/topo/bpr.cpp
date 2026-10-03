// LOCK B engine: canonical jerk x''' = -A x'' - x' - x + 2*maxe(x) - 1 with the precision-rectifier knee of LOCK B,
// maxe(x) = eps*ln(1 + e^{x/eps}) (DJ exponential junction inside the op-amp loop), eps = n V_T / (A_OL U), n = 1 + S_EM.
// usage: bpr seeds|ic  [N=16] [T=20000]
#include <cmath>
#include <cstdio>
#include <cstdlib>
#include <random>
#include <string>
#include <algorithm>
static const double A = 0.42804344605980688, SEM = 0.9557285700955828;
static double EPS;
static double maxe(double x) { double t = x / EPS; return t > 40 ? x : (t < -40 ? EPS * std::exp(t) : EPS * std::log1p(std::exp(t))); }
static void f(const double* v, double* d) { d[0] = v[1]; d[1] = v[2]; d[2] = -A * v[2] - v[1] - v[0] + 2 * maxe(v[0]) - 1; }
static void rk4(double* v, double h) { double k1[3], k2[3], k3[3], k4[3], t[3];
  f(v, k1); for (int i = 0; i < 3; ++i) t[i] = v[i] + h / 2 * k1[i]; f(t, k2); for (int i = 0; i < 3; ++i) t[i] = v[i] + h / 2 * k2[i];
  f(t, k3); for (int i = 0; i < 3; ++i) t[i] = v[i] + h * k3[i]; f(t, k4); for (int i = 0; i < 3; ++i) v[i] += h / 6 * (k1[i] + 2 * k2[i] + 2 * k3[i] + k4[i]); }
static void run(double* v, double T, const char* tag) {
  double h = 0.002, w[3], d0 = 1e-8, sum = 0, mx = -1e9, mn = 1e9, prev = 0; long cr = 0; bool bnd = true;
  for (long i = 0; i < long(500 / h) && bnd; ++i) { rk4(v, h); if (std::fabs(v[0]) > 50) bnd = false; }
  for (int i = 0; i < 3; ++i) w[i] = v[i]; w[0] += d0; long per = long(1 / h);
  for (long i = 0; i < long(T / h) && bnd; ++i) {
    rk4(v, h); rk4(w, h); if (std::fabs(v[0]) > 50) { bnd = false; break; }
    mx = std::max(mx, v[0]); mn = std::min(mn, v[0]); if (v[1] > 0 && prev <= 0) ++cr; prev = v[1];
    if ((i + 1) % per == 0) { double dd = 0; for (int k = 0; k < 3; ++k) dd += (w[k] - v[k]) * (w[k] - v[k]); dd = std::sqrt(dd); if (dd == 0) dd = 1e-300; sum += std::log(dd / d0); for (int k = 0; k < 3; ++k) w[k] = v[k] + (w[k] - v[k]) * d0 / dd; } }
  printf("%s\tbounded=%d\tl1=%.4f\txmin=%.4f\txmax=%.4f\tf_per_tau=%.5f\tf_Hz=%.1f\n", tag, int(bnd), bnd ? sum / T : NAN, mn, mx, cr / T, cr / T / 180e-6);
}
int main(int ac, char** av) {
  double kT = 1.380649e-23 * 298.15 / 1.602176634e-19, n = 1 + SEM, AOL = 2e5, U = 9.0 * 1800 / 40200; EPS = n * kT / (AOL * U);
  std::string mode = ac > 1 ? av[1] : "ic"; int N = ac > 2 ? atoi(av[2]) : 16; double T = ac > 3 ? atof(av[3]) : 20000;
  printf("# eps = %.3e\n", EPS);
  if (mode == "ic") { double v[3] = {-1.04, -0.2, 0.2}; run(v, T, "attractor_ic"); return 0; }
  std::mt19937 g(1); std::uniform_real_distribution<double> ux(-2.34, 1.45), uy(-1, 1);
  int nb = 0; for (int s = 0; s < N; ++s) { double v[3] = {ux(g), uy(g), uy(g)}; char tag[64]; snprintf(tag, 64, "seed%02d(%.3f,%.3f,%.3f)", s, v[0], v[1], v[2]); run(v, T, tag); }
}
