// Computer-assisted proof (C++20, interval arithmetic) for the ideal FSOT minimal jerk x''' = -A x'' - x' + |x| - 1 at A = 1/phi (LOCK M1).
// Section S = {x = 0}. P = P_- o P_+ where P_+ is the flight through x>0 (equilibrium x*=+1) and P_- the flight through x<0 (x*=-1).
// In each half the flow is linear: v(t) = v* + e^{Mt}(v0 - v*). e^{M[0,h]} is enclosed by a Taylor series plus a rigorous remainder.
// Mode "map y z": point (thin-interval) evaluation of P.  Mode "check file": verify covering relations between h-sets (parallelograms).
#include "iv.hpp"
#include <cstdio>
#include <cstdlib>
#include <vector>
#include <string>
#include <fstream>
#include <sstream>
#include <optional>
#include <array>
using V = std::array<I, 3>;
using Mx = std::array<std::array<I, 3>, 3>;
#include <array>
static I A_;  // damping parameter (interval)
static const double H = 1.0 / 32; static int NSUB = 1024; static int nsub_env = [](){ if (auto e = getenv("NSUB")) NSUB = atoi(e); return 0; }();
static Mx mul(const Mx& a, const Mx& b) { Mx c; for (int i = 0; i < 3; ++i) for (int j = 0; j < 3; ++j) { I s(0); for (int k = 0; k < 3; ++k) s = s + a[i][k] * b[k][j]; c[i][j] = s; } return c; }
static V mv(const Mx& a, const V& v) { V r; for (int i = 0; i < 3; ++i) { I s(0); for (int k = 0; k < 3; ++k) s = s + a[i][k] * v[k]; r[i] = s; } return r; }
static Mx Mof(int sg) { Mx m; for (auto& r : m) for (auto& e : r) e = I(0); m[0][1] = I(1); m[1][2] = I(1); m[2][0] = I(double(sg)); m[2][1] = I(-1); m[2][2] = -A_; return m; }
// enclosure of sum_n (M T)^n / (n+off)!  for T = [t0,t1] subset [0,h], off = 0 (exp) or 1 (phi1)
static Mx expT(const Mx& M, I T, int off) {
  const int N = 14; Mx S, P; for (int i = 0; i < 3; ++i) for (int j = 0; j < 3; ++j) { P[i][j] = I(i == j ? 1.0 : 0.0); S[i][j] = I(0); }
  I fact(1); for (int k = 2; k <= off; ++k) fact = fact * I(double(k));
  I Tn(1);
  for (int n = 0; n <= N; ++n) {
    for (int i = 0; i < 3; ++i) for (int j = 0; j < 3; ++j) S[i][j] = S[i][j] + P[i][j] * Tn / fact;
    P = mul(P, M); Tn = Tn * T; fact = fact * I(double(n + 1 + off));
  }
  // remainder: |entries| <= ||M T||^(N+1)/(N+1+off)! / (1 - ||MT||/(N+2))
  double nm = 0; for (int i = 0; i < 3; ++i) { double r = 0; for (int j = 0; j < 3; ++j) r += M[i][j].mag(); nm = std::max(nm, r); }
  double q = I::up(nm * T.mag() * 1.0000001); double rem = 1; for (int k = 0; k < N + 1; ++k) rem *= q; rem /= fact.lo; rem /= (1 - q / (N + 2)); rem = I::up(rem * 1.000001);
  for (auto& r : S) for (auto& e : r) e = e + I(-rem, rem);
  return S;
}
struct Half { bool ok; I y, z, t; };
// flight from {x=0, sg*y>0} through region sg*x>0 back to x=0
static Half half(I y0, I z0, int sg) {
  Mx M = Mof(sg); V D{I(-double(sg)), y0, z0};  // v0 - v*, with x0 = 0, v* = (sg,0,0)
  if (!(sg * y0.lo > 0 || sg * y0.hi < 0)) return {false};
  if ((sg > 0 && y0.lo <= 0) || (sg < 0 && y0.hi >= 0)) return {false};
  // step 0: x(t)/t = e0^T M phi1(M tau) D  must have sign sg on tau in [0,h]
  Mx Ph = mul(M, expT(M, I(0, H), 1)); I xt = mv(Ph, D)[0]; if (!(sg > 0 ? xt.lo > 0 : xt.hi < 0)) return {false};
  Mx Eh = expT(M, I(H), 0), Er = expT(M, I(0, H), 0), Ek = Eh;  // Ek encloses e^{M t_k}, t_k = k h
  bool inwin = false; I yw, zw; int ka = 0;
  for (int k = 1; k < int(60 / H); ++k) {
    Mx W = mul(Ek, Er); V r = mv(W, D); I x = r[0] + I(double(sg));
    bool pos = sg > 0 ? x.lo > 0 : x.hi < 0;
    if (!inwin) {
      if (pos) { Ek = mul(Ek, Eh); continue; }
      inwin = true; ka = k; yw = r[1]; zw = r[2];
    } else { yw = hull(yw, r[1]); zw = hull(zw, r[2]); }
    if (!(sg > 0 ? r[1].hi < 0 : r[1].lo > 0)) return {false};  // x strictly monotone in the window
    Ek = mul(Ek, Eh);
    I xe = mv(Ek, D)[0] + I(double(sg));                      // x at t_{k+1}
    if (sg > 0 ? xe.hi < 0 : xe.lo > 0) {  // refine: keep only sub-intervals of [t_ka, t_{k+1}] whose x-range contains 0
      Mx Ea = Ek; Mx Einv = Eh; (void)Einv;  // recompute E(t_ka)
      Mx E0; for (int i = 0; i < 3; ++i) for (int j = 0; j < 3; ++j) E0[i][j] = I(i == j ? 1.0 : 0.0);
      for (int q = 0; q < ka; ++q) E0 = mul(E0, Eh);
      int nsub = NSUB * (k + 1 - ka); double w = (k + 1 - ka) * H / nsub; bool any = false; I yr, zr;
      Mx Es = expT(M, I(w), 0), Ew = expT(M, I(0, w), 0), Ec = E0;
      for (int q = 0; q < nsub; ++q) { V rr = mv(mul(Ec, Ew), D); I xx = rr[0] + I(double(sg));
        if (xx.contains0()) { if (!any) { yr = rr[1]; zr = rr[2]; any = true; } else { yr = hull(yr, rr[1]); zr = hull(zr, rr[2]); } }
        Ec = mul(Ec, Es); }
      (void)Ea; if (!any) return {false};
      return {true, yr, zr, I(ka * H, (k + 1) * H)}; }
  }
  return {false};
}
struct Ret { bool ok; I y, z; };
static Ret P(I y, I z) { Half a = half(y, z, +1); if (!a.ok) return {false}; Half b = half(a.y, a.z, -1); if (!b.ok) return {false}; return {true, b.y, b.z}; }
// h-set: c + u U + s S, u,s in [-1,1]
struct HS { double cy, cz, Uy, Uz, Sy, Sz; };
static void coords(const HS& m, I y, I z, I& u, I& s) {  // solve [U S](u,s) = p - c  (2x2 inverse, interval)
  I det = I(m.Uy) * I(m.Sz) - I(m.Sy) * I(m.Uz); I dy = y - I(m.cy), dz = z - I(m.cz);
  u = (dy * I(m.Sz) - dz * I(m.Sy)) / det; s = (I(m.Uy) * dz - I(m.Uz) * dy) / det;
}
static Ret Pk(I y, I z, int k) { Ret r{true, y, z}; for (int i = 0; i < k && r.ok; ++i) r = P(r.y, r.z); return r; }
// verify N =P^k=> M : (i) |s_M| < 1 on P^k(N); (ii) u_M < -1 on one u-edge and > +1 on the other
static bool cover(const HS& n, const HS& m, int k, int nu, int ns, double& worst) {
  auto box = [&](double u0, double u1, double s0, double s1) {
    I u(u0, u1), s(s0, s1); return std::pair<I, I>{I(n.cy) + u * I(n.Uy) + s * I(n.Sy), I(n.cz) + u * I(n.Uz) + s * I(n.Sz)}; };
  worst = 0; int sideL = 0, sideR = 0;
  std::vector<Ret> res(size_t(nu) * ns);
  #pragma omp parallel for schedule(dynamic)
  for (int idx = 0; idx < nu * ns; ++idx) { int a = idx / ns, b = idx % ns;
    double u0 = -1 + 2.0 * a / nu, u1 = -1 + 2.0 * (a + 1) / nu, s0 = -1 + 2.0 * b / ns, s1 = -1 + 2.0 * (b + 1) / ns;
    auto [y, z] = box(u0, u1, s0, s1); res[idx] = Pk(y, z, k); }
  for (int a = 0; a < nu; ++a) for (int b = 0; b < ns; ++b) {
    double u0 = -1 + 2.0 * a / nu, u1 = -1 + 2.0 * (a + 1) / nu, s0 = -1 + 2.0 * b / ns, s1 = -1 + 2.0 * (b + 1) / ns;
    Ret r = res[size_t(a) * ns + b]; if (!r.ok) { printf("  undefined image at u[%g,%g] s[%g,%g]\n", u0, u1, s0, s1); return false; }
    I u, s; coords(m, r.y, r.z, u, s); worst = std::max(worst, s.mag()); if (s.mag() >= 1) { printf("  |s|>=1 at u[%g,%g] s[%g,%g]: s=[%g,%g]\n", u0, u1, s0, s1, s.lo, s.hi); return false; }
    if (a == 0) { int sd = u.hi < -1 ? -1 : (u.lo > 1 ? 1 : 0); if (sd == 0 || (sideL && sd != sideL)) { printf("  left edge not outside: u=[%g,%g]\n", u.lo, u.hi); return false; } sideL = sd; }
    if (a == nu - 1) { int sd = u.hi < -1 ? -1 : (u.lo > 1 ? 1 : 0); if (sd == 0 || (sideR && sd != sideR)) { printf("  right edge not outside: u=[%g,%g]\n", u.lo, u.hi); return false; } sideR = sd; }
  }
  return sideL == -sideR;
}
int main(int ac, char** av) {
  I s5(I::dn(std::sqrt(5.0)), I::up(std::sqrt(5.0))); I phi = (I(1) + s5) / I(2); A_ = I(1) / phi;  // A = 1/phi, rigorous
  std::string mode = ac > 1 ? av[1] : "check";
  if (mode == "map") { for (int i = 2; i + 1 < ac; i += 2) { Ret r = P(I(atof(av[i])), I(atof(av[i + 1]))); printf("%d [%.9f,%.9f] [%.9f,%.9f]\n", r.ok, r.y.lo, r.y.hi, r.z.lo, r.z.hi); } return 0; }
  if (mode == "line") {  // y grid along z = a y + b
    double a = atof(av[2]), b = atof(av[3]); for (double y = 0.05; y <= 1.8; y += 0.005) { Ret r = P(I(y), I(a * y + b)); if (r.ok) printf("%.4f %.6f %.6f\n", y, r.y.mid(), r.z.mid()); } return 0; }
  // check: file lines "name cy cz Uy Uz Sy Sz" then "cover N M k nu ns"
  std::ifstream f(ac > 2 ? av[2] : "hsets.txt"); std::string line; std::vector<std::pair<std::string, HS>> H_; int fails = 0, n = 0;
  auto get = [&](const std::string& s) -> HS { for (auto& p : H_) if (p.first == s) return p.second; throw 1; };
  while (std::getline(f, line)) {
    std::istringstream is(line); std::string w; if (!(is >> w) || w[0] == '#') continue;
    if (w == "cover") { std::string a, b; int k, nu, ns; is >> a >> b >> k >> nu >> ns; double worst; bool ok = cover(get(a), get(b), k, nu, ns, worst);
      printf("%s =P^%d=> %s : %s (max|s|=%.4f)\n", a.c_str(), k, b.c_str(), ok ? "VERIFIED" : "FAILED", worst); ++n; if (!ok) ++fails; }
    else { HS h; is >> h.cy >> h.cz >> h.Uy >> h.Uz >> h.Sy >> h.Sz; H_.push_back({w, h}); }
  }
  printf("A in [%.17g, %.17g]; %d/%d covering relations verified\n", A_.lo, A_.hi, n - fails, n);
  return fails ? 1 : 0;
}
