// oa.cpp — full op-amp model of the FSOT minimal jerk circuit (C++20). 4 op-amps (TL07x): single-pole GBW, slew, rails, anti-windup.
// Units: time tau0 = R C, voltages in V, resistances in R, caps in C. Diode: ideal with drop Vd (Shockley diode left to ngspice).
// usage: oa A=lo:hi:st gbw=3e6 sr=13 rail=7.5 tau0=180e-6 U=0.403 Vd=0.6 nic=4 T=3000   (gbw=0 -> ideal op-amps via 3-dim model check)
#include <cmath>
#include <cstdio>
#include <cstdlib>
#include <map>
#include <string>
#include <thread>
#include <vector>
#include <algorithm>
static std::map<std::string, std::string> AR;
static double G(const char* k, double d) { auto i = AR.find(k); return i == AR.end() ? d : atof(i->second.c_str()); }
static std::vector<double> rng(const std::string& s) { std::vector<double> v; double a, b, c;
  if (sscanf(s.c_str(), "%lf:%lf:%lf", &a, &b, &c) == 3) { for (double x = a; x <= b + 1e-12; x += c) v.push_back(x); } else v.push_back(atof(s.c_str())); return v; }
template <class F> void par(size_t n, F f) { unsigned T = std::max(1u, std::thread::hardware_concurrency()); std::vector<std::thread> th;
  for (unsigned t = 0; t < T; ++t) th.emplace_back([&, t] { for (size_t i = t; i < n; i += T) f(i); }); for (auto& x : th) x.join(); }
struct P { double A, W, S, Vr, U, Vd; };
// state: q1,q2,q3 = (n_i - o_i) capacitor voltages (sign: n - o), o1,o2,o3,o4
static inline double clampd(double v, double l) { return v > l ? l : (v < -l ? -l : v); }
static void f(const P& p, const double* s, double* d) {
  double o1 = s[3], o2 = s[4], o3 = s[5], o4 = s[6];
  double n1 = s[0] + o1, n2 = s[1] + o2, n3 = s[2] + o3;
  double n4 = (o2 + o4 + 2 * (o3 - p.Vd)) / 4; if (o3 - p.Vd - n4 <= 0) n4 = (o2 + o4) / 2;
  d[0] = p.A * (o1 - n1) + (o4 - n1) + (o3 - n1) + (9 - n1) * (p.U / 9);
  d[1] = (o1 - n2); d[2] = (o2 - n3);
  double no[4] = {n1, n2, n3, n4};
  for (int i = 0; i < 4; ++i) { double o = s[3 + i], r = clampd(-p.W * no[i], p.S); if ((o >= p.Vr && r > 0) || (o <= -p.Vr && r < 0)) r = 0; d[3 + i] = r; }
  // capacitor eq gives d(n-o)/dt; n is then o + q (consistent)
}
static void step(const P& p, double* s, double dt) { double k1[7], k2[7], k3[7], k4[7], t[7];
  f(p, s, k1); for (int i = 0; i < 7; ++i) t[i] = s[i] + .5 * dt * k1[i]; f(p, t, k2); for (int i = 0; i < 7; ++i) t[i] = s[i] + .5 * dt * k2[i]; f(p, t, k3);
  for (int i = 0; i < 7; ++i) t[i] = s[i] + dt * k3[i]; f(p, t, k4); for (int i = 0; i < 7; ++i) { s[i] += dt / 6 * (k1[i] + 2 * k2[i] + 2 * k3[i] + k4[i]); if (i >= 3) s[i] = clampd(s[i], p.Vr); } }
struct R_ { double l1, xmin, xmax, f; bool rail; };
static R_ run(const P& p, unsigned seed, double T, double dt) {
  double s[7] = {0, 0, 0, 0, 0, 0, -1.0 + 0.01 * seed}, u[7]; // start near E- (x = -U_eff)
  s[5] = -(p.U + p.Vd) + 0.05 + 0.01 * seed; // o3 = x
  double d0 = 1e-8, acc = 0, tr = 300; long n = long((T + tr) / dt), nt = long(tr / dt), every = long(0.5 / dt);
  for (int i = 0; i < 7; ++i) u[i] = s[i]; u[5] += d0;
  double mx = -1e9, mn = 1e9, prev = 0; long cr = 0; bool rail = false; double Ue = p.U + p.Vd;
  for (long it = 0; it < n; ++it) { step(p, s, dt); step(p, u, dt);
    if (it % every == 0) { double dd = 0; for (int i = 0; i < 7; ++i) dd += (u[i] - s[i]) * (u[i] - s[i]); dd = std::sqrt(dd); if (it >= nt) acc += std::log(dd / d0); for (int i = 0; i < 7; ++i) u[i] = s[i] + (u[i] - s[i]) * d0 / dd; }
    if (it >= nt) { double x = s[5] - p.Vd; mx = std::max(mx, x / Ue); mn = std::min(mn, x / Ue); if (std::fabs(s[5]) >= p.Vr - 1e-9) rail = true; double y = -s[4]; if (y > 0 && prev <= 0) ++cr; prev = y; } }
  return {acc / T, mn, mx, cr / T, rail};
}
int main(int ac, char** av) { for (int i = 1; i < ac; ++i) { std::string s = av[i]; auto q = s.find('='); if (q != std::string::npos) AR[s.substr(0, q)] = s.substr(q + 1); }
  auto Av = rng(AR.count("A") ? AR["A"] : "0.6180339887498949"); double gbw = G("gbw", 3e6), tau0 = G("tau0", 180e-6), sr = G("sr", 13);
  P p{0, 2 * M_PI * gbw * tau0, sr * 1e6 * tau0, G("rail", 7.5), G("U", 0.403), G("Vd", 0.6)}; int nic = int(G("nic", 4)); double T = G("T", 3000);
  double dt = std::min(0.002, 1.0 / p.W); // RK4 stability for the op-amp pole (eig ~ W/2..W)
  std::vector<R_> res(Av.size() * nic); par(res.size(), [&](size_t q) { P pp = p; pp.A = Av[q / nic]; res[q] = run(pp, unsigned(q % nic), T, dt); });
  printf("# oa W=%.1f S=%.1f Vr=%.2f U=%.3f Vd=%.2f dt=%.2e\nA\tic\tl1\txmin_Ueff\txmax_Ueff\tfreq_per_tau\trail\n", p.W, p.S, p.Vr, p.U, p.Vd, dt);
  for (size_t q = 0; q < res.size(); ++q) printf("%.5f\t%zu\t%.5f\t%.4f\t%.4f\t%.5f\t%d\n", Av[q / nic], q % nic, res[q].l1, res[q].xmin, res[q].xmax, res[q].f, res[q].rail);
}
