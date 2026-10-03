// mj.cpp — FSOT minimal chaotic circuit engine (C++20). PWL jerk x''' = -A x'' - x' + |x| - 1 (time tau0, volts U_eff).
// cmds: le A= nic= T=  | bif A=lo:hi:st nic= T= | homo A=lo:hi:st | peaks A=lo:hi:st T=
// Optional full op-amp model (TL07x single-pole GBW + slew + rails) per stage: gbw=Hz sr=V/us tau0=s rail=V
#include <cmath>
#include <cstdio>
#include <cstdlib>
#include <map>
#include <string>
#include <thread>
#include <vector>
#include <random>
#include <algorithm>
static std::map<std::string, std::string> AR;
static double G(const char* k, double d) { auto i = AR.find(k); return i == AR.end() ? d : atof(i->second.c_str()); }
static std::vector<double> rng(const std::string& s) { std::vector<double> v; double a, b, c;
  if (sscanf(s.c_str(), "%lf:%lf:%lf", &a, &b, &c) == 3) { for (double x = a; x <= b + 1e-12; x += c) v.push_back(x); } else v.push_back(atof(s.c_str())); return v; }
template <class F> void par(size_t n, F f) { unsigned T = std::max(1u, std::thread::hardware_concurrency()); std::vector<std::thread> th;
  for (unsigned t = 0; t < T; ++t) th.emplace_back([&, t] { for (size_t i = t; i < n; i += T) f(i); }); for (auto& x : th) x.join(); }
// ideal 3-dim
static inline void f3(double A, const double* s, double* o) { o[0] = s[1]; o[1] = s[2]; o[2] = -A * s[2] - s[1] + std::fabs(s[0]) - 1; }
static inline void j3(double A, const double* s, const double* w, double* o) { o[0] = w[1]; o[1] = w[2]; o[2] = -A * w[2] - w[1] + (s[0] >= 0 ? 1 : -1) * w[0]; }
struct LE { double l[3], xmax, xmin, freq; bool esc; };
static LE lyap(double A, unsigned seed, double T, double dt = 0.01, double tr = 500) {
  std::mt19937_64 g(seed); std::normal_distribution<double> nd(0, 1);
  double s[3] = {-1 + 0.1 + 0.05 * nd(g), 0.05 * nd(g), 0.05 * nd(g)}, W[9] = {1, 0, 0, 0, 1, 0, 0, 0, 1}, acc[3] = {0, 0, 0};
  long n = long((T + tr) / dt), nt = long(tr / dt); double mx = -1e9, mn = 1e9; long cross = 0; double prev = 0; bool esc = false;
  for (long it = 0; it < n; ++it) {
    double k1[3], k2[3], k3[3], k4[3], t[3]; double q1[9], q2[9], q3[9], q4[9], u[9];
    auto JV = [&](const double* st, const double* w, double* o) { for (int c = 0; c < 3; ++c) j3(A, st, w + 3 * c, o + 3 * c); };
    f3(A, s, k1); JV(s, W, q1);
    for (int i = 0; i < 3; ++i) t[i] = s[i] + .5 * dt * k1[i]; for (int i = 0; i < 9; ++i) u[i] = W[i] + .5 * dt * q1[i]; f3(A, t, k2); JV(t, u, q2);
    for (int i = 0; i < 3; ++i) t[i] = s[i] + .5 * dt * k2[i]; for (int i = 0; i < 9; ++i) u[i] = W[i] + .5 * dt * q2[i]; f3(A, t, k3); JV(t, u, q3);
    for (int i = 0; i < 3; ++i) t[i] = s[i] + dt * k3[i]; for (int i = 0; i < 9; ++i) u[i] = W[i] + dt * q3[i]; f3(A, t, k4); JV(t, u, q4);
    for (int i = 0; i < 3; ++i) s[i] += dt / 6 * (k1[i] + 2 * k2[i] + 2 * k3[i] + k4[i]);
    for (int i = 0; i < 9; ++i) W[i] += dt / 6 * (q1[i] + 2 * q2[i] + 2 * q3[i] + q4[i]);
    if (std::fabs(s[0]) > 1e3) { esc = true; break; }
    // Gram-Schmidt every step
    for (int c = 0; c < 3; ++c) { double* w = W + 3 * c; for (int d = 0; d < c; ++d) { double* v = W + 3 * d; double p = w[0] * v[0] + w[1] * v[1] + w[2] * v[2]; for (int i = 0; i < 3; ++i) w[i] -= p * v[i]; }
      double nr = std::sqrt(w[0] * w[0] + w[1] * w[1] + w[2] * w[2]); if (it >= nt) acc[c] += std::log(nr); for (int i = 0; i < 3; ++i) w[i] /= nr; }
    if (it >= nt) { mx = std::max(mx, s[0]); mn = std::min(mn, s[0]); if ((s[1] > 0) && (prev <= 0)) ++cross; prev = s[1]; } else prev = s[1];
  }
  LE r{}; for (int c = 0; c < 3; ++c) r.l[c] = esc ? NAN : acc[c] / T; r.xmax = mx; r.xmin = mn; r.freq = cross / T; r.esc = esc; return r;
}
// homoclinic to E- (x=-1): 1D stable manifold, traced in backward time; returns min distance to E- after leaving radius 0.5
static double homo(double A, int branch, double* tret) {
  // 1D stable manifold of E- traced backward; at the first local minimum of |s-E-| after leaving r=0.3, return the signed
  // component along v_s (left-eigenvector projection, i.e. signed distance to E-'s 2D unstable plane). Zero => homoclinic.
  double l = -0.8; for (int i = 0; i < 100; ++i) { double p = ((l + A) * l + 1) * l + 1, dp = (3 * l + 2 * A) * l + 1; l -= p / dp; }
  // companion matrix M=[[0,1,0],[0,0,1],[-1,-1,-A]] (x<0 region); left eigenvector w: w M = l w -> w = (1, (l+A) l + 1 ... ) solve
  // w = (w0,w1,w2): -w2 = l w0 ; w0 - w2 = l w1 ; w1 - A w2 = l w2  => w2 = 1, w1 = l + A, w0 = -l
  double w[3] = {-l, l + A, 1}, v[3] = {1, l, l * l}, nv = std::sqrt(1 + l * l + l * l * l * l), e = 1e-7 * branch;
  double s[3] = {-1 + e * v[0] / nv, e * v[1] / nv, e * v[2] / nv}, dt = -0.001; bool left = false; double dprev = 1e9, dpp = 1e9;
  for (long it = 0; it < 2000000; ++it) { double k1[3], k2[3], k3[3], k4[3], t[3];
    f3(A, s, k1); for (int i = 0; i < 3; ++i) t[i] = s[i] + .5 * dt * k1[i]; f3(A, t, k2); for (int i = 0; i < 3; ++i) t[i] = s[i] + .5 * dt * k2[i]; f3(A, t, k3);
    for (int i = 0; i < 3; ++i) t[i] = s[i] + dt * k3[i]; f3(A, t, k4); for (int i = 0; i < 3; ++i) s[i] += dt / 6 * (k1[i] + 2 * k2[i] + 2 * k3[i] + k4[i]);
    double d = std::sqrt((s[0] + 1) * (s[0] + 1) + s[1] * s[1] + s[2] * s[2]); if (d > 0.3) left = true;
    if (left && dprev < dpp && dprev < d && dprev < 1.5) { *tret = -it * dt; return (w[0] * (s[0] + 1) + w[1] * s[1] + w[2] * s[2]); }
    dpp = dprev; dprev = d; if (std::fabs(s[0]) > 50) break; }
  *tret = -1; return NAN;
}
int main(int ac, char** av) {
  std::string cmd = ac > 1 ? av[1] : ""; for (int i = 2; i < ac; ++i) { std::string s = av[i]; auto p = s.find('='); if (p != std::string::npos) AR[s.substr(0, p)] = s.substr(p + 1); }
  std::string As = AR.count("A") ? AR["A"] : "0.6180339887498949"; auto Av = rng(As); int nic = int(G("nic", 8)); double T = G("T", 20000);
  if (cmd == "le" || cmd == "bif") {
    std::vector<LE> R(Av.size() * nic); par(R.size(), [&](size_t q) { R[q] = lyap(Av[q / nic], unsigned(q % nic + 1), T); });
    printf("A\tic\tl1\tl2\tl3\tsum\txmin\txmax\tfreq_per_tau\n");
    for (size_t q = 0; q < R.size(); ++q) { auto& r = R[q]; printf("%.5f\t%zu\t%.5f\t%.5f\t%.5f\t%.5f\t%.4f\t%.4f\t%.5f\n", Av[q / nic], q % nic, r.l[0], r.l[1], r.l[2], r.l[0] + r.l[1] + r.l[2], r.xmin, r.xmax, r.freq); }
    return 0; }
  if (cmd == "homo") { std::vector<double> d(Av.size() * 2), tt(Av.size() * 2);
    par(d.size(), [&](size_t q) { d[q] = homo(Av[q / 2], q % 2 ? 1 : -1, &tt[q]); });
    printf("A\tdmin_branch-\tt-\tdmin_branch+\tt+\n"); for (size_t i = 0; i < Av.size(); ++i) printf("%.6f\t%.3e\t%.2f\t%.3e\t%.2f\n", Av[i], d[2 * i], tt[2 * i], d[2 * i + 1], tt[2 * i + 1]); return 0; }
  fprintf(stderr, "cmds: le bif homo\n"); return 1;
}
