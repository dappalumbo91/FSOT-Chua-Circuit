// Branch D (LOCK_D1): minimal FSOT jerk with Shockley 1N4148 (zero free parameters), ideal op-amps clipped at +-Vr.
// Units: time tau0 = R C (R = 1.8k, C = 100n), voltages in V, currents in V/R.
// usage: bd RA=lo:hi:st [Tc=27] [Vs=9] [nic=3] [T=3000] [rail=7.5]   prints RA A ic l1 xmin xmax f_Hz rail
#include <cmath>
#include <cstdio>
#include <map>
#include <string>
#include <algorithm>
static std::map<std::string, std::string> AR;
static double G(const char* k, double d) { auto i = AR.find(k); return i == AR.end() ? d : std::stod(i->second); }
struct P { double A, U, Vr, nVT, RIs, a; };
static double diodeI(double o3, const P& p, double& u) {  // solve a*RIs*(e^u-1) + nVT*u = o3, monotone in u
  for (int k = 0; k < 60; ++k) {
    double e = std::exp(std::min(u, 700.0)), g = p.a * p.RIs * (e - 1) + p.nVT * u - o3, dg = p.a * p.RIs * e + p.nVT;
    double du = -g / dg; if (du > 2) du = 2; if (du < -50) du = -50; u += du; if (std::fabs(du) < 1e-13) break; }
  return p.RIs * (std::exp(u) - 1);
}
static void f(const double* s, double* d, const P& p, double& u) {
  double I = diodeI(s[2], p, u), o4 = -(s[1] + I);
  d[0] = -(p.A * s[0] + o4 + s[2] + p.U); d[1] = -s[0]; d[2] = -s[1];
  for (int i = 0; i < 3; ++i) if ((s[i] >= p.Vr && d[i] > 0) || (s[i] <= -p.Vr && d[i] < 0)) d[i] = 0;
}
static void rk4(double* s, double h, const P& p, double& u) {
  double k1[3], k2[3], k3[3], k4[3], t[3];
  f(s, k1, p, u); for (int i = 0; i < 3; ++i) t[i] = s[i] + h / 2 * k1[i];
  f(t, k2, p, u); for (int i = 0; i < 3; ++i) t[i] = s[i] + h / 2 * k2[i];
  f(t, k3, p, u); for (int i = 0; i < 3; ++i) t[i] = s[i] + h * k3[i];
  f(t, k4, p, u); for (int i = 0; i < 3; ++i) { s[i] += h / 6 * (k1[i] + 2 * k2[i] + 2 * k3[i] + k4[i]); s[i] = std::clamp(s[i], -p.Vr, p.Vr); }
}
int main(int ac, char** av) {
  for (int i = 1; i < ac; ++i) { std::string s = av[i]; auto q = s.find('='); if (q != std::string::npos) AR[s.substr(0, q)] = s.substr(q + 1); }
  const double R = 1800, C = 100e-9, tau0 = R * C, Rc = 40200, Rd = 900, Rs = 0.568, Is0 = 2.52e-9; const double N = G("N", 1.752);
  const double kB = 1.380649e-23, q = 1.602176634e-19, Tn = 300.15;
  double Tc = G("Tc", 27), TK = Tc + 273.15, Vs = G("Vs", 9), VT = kB * TK / q, VTn = kB * Tn / q;
  double Is = Is0 * std::pow(TK / Tn, 3.0 / N) * std::exp((TK / Tn - 1) * 1.11 / (N * VT));
  std::string ra = AR.count("RA") ? AR["RA"] : "3160:3160:1"; double lo, hi, st; sscanf(ra.c_str(), "%lf:%lf:%lf", &lo, &hi, &st);
  int nic = int(G("nic", 3)); double Tm = G("T", 3000), Ttr = G("Ttr", 1000), h = 0.01;
  P p{0, Vs * R / Rc, G("rail", 7.5), N * VT, R * Is, Rd / R + Rs / R};
  printf("# bd Tc=%.1f Vs=%.2f U=%.4f nVT=%.5f Is=%.4e\nRA\tA\tic\tl1\txmin\txmax\tf_Hz\trail\n", Tc, Vs, p.U, p.nVT, Is);
  for (double RA = lo; RA <= hi + 1e-9; RA += st) {
    p.A = R / RA;
    for (int ic = 0; ic < nic; ++ic) {
      double s[3] = {G("o1", 0) + G("rad", 0) * ((ic & 1) ? 1 : -1), G("o2", 0) + G("rad", 0) * ((ic & 2) ? 1 : -1), G("o3", -0.95) + 0.02 * ic * (AR.count("o3") ? 0 : 1) + G("rad", 0) * ((ic & 4) ? 1 : -1)}, w[3], u = 0, uw = 0, d0 = 1e-7, sum = 0, mx = -1e9, mn = 1e9, prev = 0; long cr = 0; bool rail = false;
      long ntr = long(Ttr / h), nm = long(Tm / h), per = long(1.0 / h);
      for (long it = 0; it < ntr; ++it) rk4(s, h, p, u);
      for (int i = 0; i < 3; ++i) w[i] = s[i]; w[0] += d0;
      for (long it = 0; it < nm; ++it) {
        rk4(s, h, p, u); rk4(w, h, p, uw);
        mx = std::max(mx, s[2]); mn = std::min(mn, s[2]);
        for (int i = 0; i < 3; ++i) if (std::fabs(s[i]) >= p.Vr - 1e-9) rail = true;
        double y = -s[1]; if (y > 0 && prev <= 0) ++cr; prev = y;
        if ((it + 1) % per == 0) { double dd = 0; for (int i = 0; i < 3; ++i) dd += (w[i] - s[i]) * (w[i] - s[i]); dd = std::sqrt(dd);
          if (dd == 0) dd = 1e-300; sum += std::log(dd / d0); for (int i = 0; i < 3; ++i) w[i] = s[i] + (w[i] - s[i]) * d0 / dd; } }
      printf("%.1f\t%.5f\t%d\t%.4f\t%.4f\t%.4f\t%.2f\t%d\n", RA, p.A, ic, sum / Tm, mn, mx, cr / Tm / tau0, int(rail)); fflush(stdout);
    }
  }
}
