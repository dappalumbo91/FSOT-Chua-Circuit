// horseshoe_bg: horseshoe.cpp generalised to x''' = -A x'' - B x' + G|x| - 1 (LOCK PJ winner), in scaled coordinates X = G x (equilibria X = +-1).
// FSOT_B / FSOT_G give the exact binary64 values of B and G.
// Computer-assisted proof of chaos (C++20, interval arithmetic, no external deps) for the ideal FSOT minimal jerk
//   x''' = -A x'' - x' + |x| - 1   at the FSOT knob A = gamma_rel = 0.42804344605980688 (fsot-law-circuit results/design.json:3).
// Section S = {x = 0, x' > 0}; P = H_- o H_+ (linear flows v(t) = v* + e^{Mt}(v0 - v*) in x>0 / x<0, v* = (+-1,0,0)).
// Crossing times: strict sign checks on a 1/32 grid, then an interval Newton contraction on [t_a, t_b] (x strictly monotone there).
// Images: first-order (mean-value) form P^k(B) in P^k(c) + [prod J_i(B_i)] (B - c), with J = (I - f(v1) e0^T / y1) e^{M t*} restricted to (y,z).
// Covering relations (Zgliczynski-Gidea, u = s = 1, Thm 16 sufficient conditions) between h-sets N = c + u U + s S:
//   (a) u-edges map to u_M < -1 and u_M > +1 (opposite sides); (b) image avoids M+ = {|u_M| <= 1, |s_M| = 1};
//   (c) image of the central line s = 0 avoids {|u_M| <= 1, |s_M| >= 1}.
// A transition graph with spectral radius rho > 1 under P^k gives topological entropy >= ln(rho)/k (symbolic dynamics on the invariant set).
#include "iv.hpp"
#include <array>
#include <cstdio>
#include <cstdlib>
#include <vector>
#include <string>
#include <fstream>
#include <sstream>
#include <cmath>
using V = std::array<I, 3>;
using Mx = std::array<std::array<I, 3>, 3>;
static I A_, B_(1.0), G_(1.0);
static const double H = 1.0 / 32;
static Mx mul(const Mx& a, const Mx& b) { Mx c; for (int i = 0; i < 3; ++i) for (int j = 0; j < 3; ++j) { I s(0); for (int k = 0; k < 3; ++k) s = s + a[i][k] * b[k][j]; c[i][j] = s; } return c; }
static V mv(const Mx& a, const V& v) { V r; for (int i = 0; i < 3; ++i) { I s(0); for (int k = 0; k < 3; ++k) s = s + a[i][k] * v[k]; r[i] = s; } return r; }
static Mx Mof(int sg) { Mx m; for (auto& r : m) for (auto& e : r) e = I(0); m[0][1] = I(1); m[1][2] = I(1); m[2][0] = G_ * I(double(sg)); m[2][1] = -B_; m[2][2] = -A_; return m; }
static Mx expT(const Mx& M, I T, int off) {  // sum (M T)^n/(n+off)! + rigorous remainder; T may be any small interval
  const int N = 16; Mx S, P; for (int i = 0; i < 3; ++i) for (int j = 0; j < 3; ++j) { P[i][j] = I(i == j ? 1.0 : 0.0); S[i][j] = I(0); }
  I fact(1); for (int k = 2; k <= off; ++k) fact = fact * I(double(k)); I Tn(1);
  for (int n = 0; n <= N; ++n) { for (int i = 0; i < 3; ++i) for (int j = 0; j < 3; ++j) S[i][j] = S[i][j] + P[i][j] * Tn / fact; P = mul(P, M); Tn = Tn * T; fact = fact * I(double(n + 1 + off)); }
  double nm = 0; for (int i = 0; i < 3; ++i) { double r = 0; for (int j = 0; j < 3; ++j) r += M[i][j].mag(); nm = std::max(nm, r); }
  double q = I::up(nm * T.mag() * 1.0000001); if (q >= 1) { fprintf(stderr, "expT: step too large\n"); exit(3); }
  double rem = 1; for (int k = 0; k < N + 1; ++k) rem *= q; rem /= fact.lo; rem /= (1 - q / (N + 2)); rem = I::up(rem * 1.000001);
  for (auto& r : S) for (auto& e : r) e = e + I(-rem, rem);
  return S;
}
static Mx hullM(const Mx& a, const Mx& b) { Mx c; for (int i = 0; i < 3; ++i) for (int j = 0; j < 3; ++j) c[i][j] = hull(a[i][j], b[i][j]); return c; }
static Mx expAny(const Mx& M, I T) {  // e^{M T} for any interval T >= -tiny: power of short steps to T.lo, then a hull over chunks of width <= 0.1
  if (T.mag() <= 0.12) return expT(M, T, 0);
  double lo = std::max(0.0, T.lo); int m = int(std::ceil(lo / 0.1)); Mx E; for (int i = 0; i < 3; ++i) for (int j = 0; j < 3; ++j) E[i][j] = I(i == j ? 1.0 : 0.0);
  if (m > 0) { Mx st = expT(M, I(lo) / I(double(m)), 0); for (int k = 0; k < m; ++k) E = mul(E, st); }
  I rest = T - I(lo); double W = std::max(rest.hi, 0.0); int nc = std::max(1, int(std::ceil(W / 0.1))); I d = I(W) / I(double(nc));
  Mx st = expT(M, d, 0), rng = expT(M, I(std::min(rest.lo, 0.0), d.hi), 0); Mx out = mul(E, rng), Ek = E;
  for (int k = 1; k < nc; ++k) { Ek = mul(Ek, st); out = hullM(out, mul(Ek, rng)); }
  return out;
}
static I isect(I a, I b) { return {std::max(a.lo, b.lo), std::min(a.hi, b.hi)}; }
struct Half { bool ok; I y, z; Mx J2; int b; };  // section-to-section step; (y,z) here are the two free coordinates of the target section; b = crossed functional
static Mx Mp, Mm, Ehp, Ehm, Erp, Erm, Php, Phm;
static void init() { Mp = Mof(1); Mm = Mof(-1); Ehp = expT(Mp, I(H), 0); Ehm = expT(Mm, I(H), 0); Erp = expT(Mp, I(0, H), 0); Erm = expT(Mm, I(0, H), 0);
  Php = mul(Mp, expT(Mp, I(0, H), 1)); Phm = mul(Mm, expT(Mm, I(0, H), 1)); }
// free coordinates of section {v_a = 0}: a = 0 (x): (y, z); a = 1 (y): (x, z)
static int fc(int a, int i) { return a == 0 ? (i == 0 ? 1 : 2) : (i == 0 ? 0 : 2); }
// One sub-flight inside the half-space sg*x > 0, starting on {v_a = 0} with free coordinates (p, q), until the first zero of x (exit) or of y (extremum).
static Half sub(int a, I p, I q, int sg) {
  const Mx& M = sg > 0 ? Mp : Mm; const Mx& Eh = sg > 0 ? Ehp : Ehm; const Mx& Er = sg > 0 ? Erp : Erm; const Mx& Ph = sg > 0 ? Php : Phm;
  V v0; v0[a] = I(0); v0[fc(a, 0)] = p; v0[fc(a, 1)] = q;
  if (a == 1 && !(sg > 0 ? v0[0].lo > 0 : v0[0].hi < 0)) return {false};    // start must be inside the region
  V D = v0; D[0] = D[0] - I(double(sg));                                          // v0 - v*, v* = (sg, 0, 0)
  I d0 = mv(Ph, D)[a];                                                            // v_a(t)/t on [0, h]
  if (d0.contains0()) return {false}; int sa = d0.lo > 0 ? 1 : -1;
  // initial sign of the other functional
  int ob = 1 - a; I o0 = v0[ob]; if (ob == 0) o0 = v0[0];
  Mx Ek = Eh; int ka = -1, kb = -1, b = -1; Mx Ea;
  auto fval = [&](const V& r, int idx) { return idx == 0 ? r[0] + I(double(sg)) : r[idx]; };
  int sgn[2]; sgn[a] = sa; { I t = (a == 0 ? v0[1] : v0[0]); if (t.contains0()) return {false}; sgn[ob] = t.lo > 0 ? 1 : -1; }
  if (a == 0) sgn[1] = (v0[1].lo > 0 ? 1 : -1);
  for (int k = 1; k < int(60 / H); ++k) {
    V r = mv(mul(Ek, Er), D);
    bool s0 = sgn[0] > 0 ? fval(r, 0).lo > 0 : fval(r, 0).hi < 0, s1 = sgn[1] > 0 ? r[1].lo > 0 : r[1].hi < 0;
    if (ka < 0) {
      if (s0 && s1) { Ek = mul(Ek, Eh); continue; }
      if (!s0 && !s1) return {false};
      b = s0 ? 1 : 0; ka = k; Ea = Ek;
    } else { bool so = (b == 0) ? s1 : s0; if (!so) return {false}; }
    I der = r[b + 1]; if (der.contains0()) return {false};                         // d/dt v_b = v_{b+1} (x' = y, y' = z): strictly monotone in the window
    if ((der.lo > 0 ? 1 : -1) != -sgn[b]) return {false};
    Ek = mul(Ek, Eh); V re = mv(Ek, D); I fe = fval(re, b);
    if (sgn[b] > 0 ? fe.lo > 0 : fe.hi < 0) { ka = k + 1; Ea = Ek; continue; }
    if (sgn[b] > 0 ? fe.hi < 0 : fe.lo > 0) { kb = k + 1; break; }
  }
  if (kb < 0) return {false};
  I tau(0, (kb - ka) * H);
  for (int it = 0; it < 200; ++it) {
    double tm = tau.mid(); V rm = mv(mul(Ea, expAny(M, I(tm))), D); I X = fval(rm, b);
    I Y = mv(mul(Ea, expAny(M, tau)), D)[b + 1]; if (Y.contains0()) return {false};
    I nt = isect(tau, I(tm) - X / Y); if (nt.lo > nt.hi) return {false};
    bool stall = nt.wid() >= 0.999 * tau.wid(); tau = nt; if (stall && it > 8) break;
  }
  Mx E = mul(Ea, expAny(M, tau)); V w = mv(E, D);                                  // v1 - v*
  V v1 = w; v1[0] = w[0] + I(double(sg)); v1[b] = I(0);
  V f{w[1], w[2], M[2][0] * w[0] + M[2][1] * w[1] + M[2][2] * w[2]};             // f(v1) = M (v1 - v*)
  if (f[b].contains0()) return {false};
  Mx J; for (int r = 0; r < 3; ++r) for (int c = 0; c < 3; ++c) J[r][c] = E[r][c] - f[r] * E[b][c] / f[b];
  Mx J2; for (auto& rr : J2) for (auto& e : rr) e = I(0);
  for (int i = 0; i < 2; ++i) for (int j = 0; j < 2; ++j) J2[i][j] = J[fc(b, i)][fc(a, j)];
  if (getenv("DBGJ") && p.wid() > 0) fprintf(stderr, "sub a%d->b%d sg %d in w %.1e %.1e tau w %.1e J w %.1e %.1e %.1e %.1e |J| %.2f %.2f %.2f %.2f\n", a, b, sg, p.wid(), q.wid(), tau.wid(), J2[0][0].wid(), J2[0][1].wid(), J2[1][0].wid(), J2[1][1].wid(), J2[0][0].mag(), J2[0][1].mag(), J2[1][0].mag(), J2[1][1].mag());
  return {true, v1[fc(b, 0)], v1[fc(b, 1)], J2, b};
}
// x=0 to x=0 half-flight through the region sg*x > 0, factorised at every extremum (y = 0) to keep each linear flight short.
static Half half(I y0, I z0, int sg) {
  int a = 0; I p = y0, q = z0; I Jc[2][2] = {{I(1), I(0)}, {I(0), I(1)}};
  for (int n = 0; n < 12; ++n) {
    Half h = sub(a, p, q, sg); if (!h.ok) return {false};
    I nn[2][2]; for (int i = 0; i < 2; ++i) for (int j = 0; j < 2; ++j) nn[i][j] = h.J2[i][0] * Jc[0][j] + h.J2[i][1] * Jc[1][j];
    for (int i = 0; i < 2; ++i) for (int j = 0; j < 2; ++j) Jc[i][j] = nn[i][j];
    p = h.y; q = h.z; a = h.b;
    if (a == 0) { Mx J2; for (auto& rr : J2) for (auto& e : rr) e = I(0); for (int i = 0; i < 2; ++i) for (int j = 0; j < 2; ++j) J2[i][j] = Jc[i][j]; return {true, p, q, J2, 0}; }
  }
  return {false};
}
struct Img { bool ok; I y, z; I J[2][2]; };
static bool step_thin(I& y, I& z, int sg, Half* hJ) {  // mean-value step for a thin box; optionally returns the Jacobian enclosure over it
  Half h = half(y, z, sg); if (!h.ok) return false; double my = y.mid(), mz = z.mid(); Half c = half(I(my), I(mz), sg); if (!c.ok) return false;
  I ny = c.y + h.J2[0][0] * (y - I(my)) + h.J2[0][1] * (z - I(mz)), nz = c.z + h.J2[1][0] * (y - I(my)) + h.J2[1][1] * (z - I(mz));
  y = isect(ny, h.y); z = isect(nz, h.z); if (hJ) *hJ = h; return true;
}
// Affine (Lohner-type, without QR) propagation: image = c_k + Jacc * Delta, Delta = B - mid(B); intermediate boxes for the Jacobian are c_i + Jacc_i * Delta.
static Img Pk(I y, I z, int k) {
  double my = y.mid(), mz = z.mid(); I dy = y - I(my), dz = z - I(mz);
  Img r{true, I(my), I(mz), {{I(1), I(0)}, {I(0), I(1)}}};
  bool thin = (y.wid() == 0 && z.wid() == 0);
  for (int i = 0; i < 2 * k; ++i) {
    int sg = (i % 2 == 0) ? +1 : -1;
    I by = r.y + r.J[0][0] * dy + r.J[0][1] * dz, bz = r.z + r.J[1][0] * dy + r.J[1][1] * dz;  // enclosure of the current image
    Half hb; if (thin) { if (!step_thin(r.y, r.z, sg, &hb)) { r.ok = false; return r; } }
    else { hb = half(by, bz, sg); if (!hb.ok) { r.ok = false; return r; } if (!step_thin(r.y, r.z, sg, nullptr)) { r.ok = false; return r; } }
    I n[2][2]; for (int a = 0; a < 2; ++a) for (int b = 0; b < 2; ++b) n[a][b] = hb.J2[a][0] * r.J[0][b] + hb.J2[a][1] * r.J[1][b];
    for (int a = 0; a < 2; ++a) for (int b = 0; b < 2; ++b) r.J[a][b] = n[a][b];
  }
  if (!thin) { I fy = r.y + r.J[0][0] * dy + r.J[0][1] * dz, fz = r.z + r.J[1][0] * dy + r.J[1][1] * dz; r.y = fy; r.z = fz; }
  return r;
}
// Preconditioned affine propagation: the set is c + G (du, ds), with G = DP * [U S] carried column-wise (the U column grows, the S column
// contracts), so interval products never multiply large non-normal partial Jacobians (the wrapping that killed the plain affine form).
struct Img2 { bool ok; I cy, cz; I G[2][2]; };
static Img2 Pk2(double cy, double cz, const double G0[2][2], I du, I ds, int k) {
  Img2 r{true, I(cy), I(cz), {{I(G0[0][0]), I(G0[0][1])}, {I(G0[1][0]), I(G0[1][1])}}};
  for (int i = 0; i < 2 * k; ++i) {
    int sg = (i % 2 == 0) ? +1 : -1;
    I by = r.cy + r.G[0][0] * du + r.G[0][1] * ds, bz = r.cz + r.G[1][0] * du + r.G[1][1] * ds;
    Half hb = half(by, bz, sg); if (!hb.ok) { r.ok = false; return r; }
    if (!step_thin(r.cy, r.cz, sg, nullptr)) { r.ok = false; return r; }
    I n[2][2]; for (int a = 0; a < 2; ++a) for (int b = 0; b < 2; ++b) n[a][b] = hb.J2[a][0] * r.G[0][b] + hb.J2[a][1] * r.G[1][b];
    for (int a = 0; a < 2; ++a) for (int b = 0; b < 2; ++b) r.G[a][b] = n[a][b];
  }
  return r;
}
struct HS { double cy, cz, Uy, Uz, Sy, Sz; };
static void tocoords(const HS& m, I dy, I dz, I& u, I& s) {  // [U S]^{-1} (dy, dz)
  I det = I(m.Uy) * I(m.Sz) - I(m.Sy) * I(m.Uz);
  u = (dy * I(m.Sz) - dz * I(m.Sy)) / det; s = (I(m.Uy) * dz - I(m.Uz) * dy) / det;
}
static int K_;
static bool cover(const HS& n, const HS& m, int nu, int ns, double& worst, std::string& why) {
  struct R { bool ok; I u, s; };
  std::vector<R> res(size_t(nu) * ns);
  #pragma omp parallel for schedule(dynamic)
  for (int idx = 0; idx < nu * ns; ++idx) {
    int a = idx / ns, b = idx % ns; double du = 1.0 / nu, ds = 1.0 / ns, uc = -1 + (2 * a + 1) * du, sc = -1 + (2 * b + 1) * ds;
    double cy = n.cy + uc * n.Uy + sc * n.Sy, cz = n.cz + uc * n.Uz + sc * n.Sz;
    I Du(-du, du), Ds(-ds, ds);
    double G0[2][2] = {{n.Uy, n.Sy}, {n.Uz, n.Sz}};
    Img2 im = Pk2(cy, cz, G0, Du, Ds, K_);
    if (!im.ok) { res[idx] = {false}; continue; }
    I u1, s1, gu0, gs0, gu1, gs1; tocoords(m, im.cy - I(m.cy), im.cz - I(m.cz), u1, s1);
    tocoords(m, im.G[0][0], im.G[1][0], gu0, gs0); tocoords(m, im.G[0][1], im.G[1][1], gu1, gs1);  // M-coordinates of the two columns
    I u2 = gu0 * Du + gu1 * Ds, s2 = gs0 * Du + gs1 * Ds;
    res[idx] = {true, u1 + u2, s1 + s2};
  }
  worst = 0; int sideL = 0, sideR = 0;
  for (int a = 0; a < nu; ++a) for (int b = 0; b < ns; ++b) {
    const R& r = res[size_t(a) * ns + b]; char buf[200];
    if (!r.ok) { snprintf(buf, 200, "undefined image (box %d,%d)", a, b); why = buf; return false; }
    bool inU = !(r.u.hi < -1 || r.u.lo > 1);
    if (inU) { worst = std::max(worst, r.s.mag()); if (r.s.hi >= 1 && r.s.lo <= 1) { snprintf(buf, 200, "touches s=+1 at box %d,%d s=[%.4f,%.4f] u=[%.4f,%.4f]", a, b, r.s.lo, r.s.hi, r.u.lo, r.u.hi); why = buf; return false; }
               if (r.s.lo <= -1 && r.s.hi >= -1) { snprintf(buf, 200, "touches s=-1 at box %d,%d s=[%.4f,%.4f] u=[%.4f,%.4f]", a, b, r.s.lo, r.s.hi, r.u.lo, r.u.hi); why = buf; return false; } }
    bool central = (-1 + 2.0 * b / ns <= 0) && (-1 + 2.0 * (b + 1) / ns >= 0);
    if (central && inU && r.s.mag() >= 1) { snprintf(buf, 200, "central line leaves strip at box %d: s=[%.4f,%.4f] u=[%.4f,%.4f]", a, r.s.lo, r.s.hi, r.u.lo, r.u.hi); why = buf; return false; }
    if (a == 0) { int sd = r.u.hi < -1 ? -1 : (r.u.lo > 1 ? 1 : 0); if (sd == 0 || (sideL && sd != sideL)) { snprintf(buf, 200, "left edge not outside: u=[%.4f,%.4f]", r.u.lo, r.u.hi); why = buf; return false; } sideL = sd; }
    if (a == nu - 1) { int sd = r.u.hi < -1 ? -1 : (r.u.lo > 1 ? 1 : 0); if (sd == 0 || (sideR && sd != sideR)) { snprintf(buf, 200, "right edge not outside: u=[%.4f,%.4f]", r.u.lo, r.u.hi); why = buf; return false; } sideR = sd; }
  }
  if (sideL != -sideR) { why = "edges on the same side"; return false; }
  return true;
}
int main(int ac, char** av) {
  A_ = I(0.42804344605980688);  // FSOT gamma_rel as the exact binary64 parameter value
  if (const char* e = getenv("FSOT_A")) A_ = I(atof(e));
  if (const char* e = getenv("FSOT_B")) B_ = I(atof(e));
  if (const char* e = getenv("FSOT_G")) G_ = I(atof(e));
  init();
  std::string mode = ac > 1 ? av[1] : "check";
  if (mode == "box") { int k = atoi(av[2]); double y = atof(av[3]), z = atof(av[4]), d = atof(av[5]); Img r = Pk(I(y - d, y + d), I(z - d, z + d), k);
    printf("%d y=[%.12f,%.12f] z=[%.12f,%.12f]\n", r.ok, r.y.lo, r.y.hi, r.z.lo, r.z.hi); return 0; }
  if (mode == "map") { int k = atoi(av[2]); for (int i = 3; i + 1 < ac; i += 2) { Img r = Pk(I(atof(av[i])), I(atof(av[i + 1])), k);
      printf("%d y=[%.12f,%.12f] z=[%.12f,%.12f] J=[[%.5f %.5f][%.5f %.5f]]\n", r.ok, r.y.lo, r.y.hi, r.z.lo, r.z.hi, r.J[0][0].mid(), r.J[0][1].mid(), r.J[1][0].mid(), r.J[1][1].mid()); } return 0; }
  std::ifstream f(ac > 2 ? av[2] : "golden.txt"); std::string line; std::vector<std::pair<std::string, HS>> hs; std::vector<std::pair<int, int>> edges; int fails = 0, n = 0; K_ = 1;
  auto idx = [&](const std::string& s) { for (size_t i = 0; i < hs.size(); ++i) if (hs[i].first == s) return int(i); fprintf(stderr, "unknown %s\n", s.c_str()); exit(2); };
  while (std::getline(f, line)) {
    std::istringstream is(line); std::string w; if (!(is >> w) || w[0] == '#') continue;
    if (w == "iterate") { is >> K_; continue; }
    if (w == "cover") { std::string a, b; int nu, ns; is >> a >> b >> nu >> ns; double worst; std::string why;
      bool ok = cover(hs[idx(a)].second, hs[idx(b)].second, nu, ns, worst, why); ++n;
      printf("%s =P^%d=> %s : %s (max|s| on |u|<=1: %.4f) %s\n", a.c_str(), K_, b.c_str(), ok ? "VERIFIED" : "FAILED", worst, ok ? "" : why.c_str()); fflush(stdout);
      if (ok) edges.push_back({idx(a), idx(b)}); else ++fails; continue; }
    HS h; is >> h.cy >> h.cz >> h.Uy >> h.Uz >> h.Sy >> h.Sz; hs.push_back({w, h});
  }
  // spectral radius of the verified transition matrix (power iteration; reported as a lower bound via a Collatz-Wielandt estimate)
  int m = int(hs.size()); std::vector<double> x(m, 1.0), y(m);
  for (int it = 0; it < 2000; ++it) { std::fill(y.begin(), y.end(), 0.0); for (auto& e : edges) y[e.first] += x[e.second]; double s = 0; for (double v : y) s = std::max(s, v); if (s == 0) break; for (int i = 0; i < m; ++i) x[i] = y[i] / s; }
  std::fill(y.begin(), y.end(), 0.0); for (auto& e : edges) y[e.first] += x[e.second];
  double lb = 1e300; for (int i = 0; i < m; ++i) if (x[i] > 1e-12) lb = std::min(lb, y[i] / x[i]); if (lb == 1e300) lb = 0;
  printf("A = [%.17g, %.17g]; %d/%d covering relations verified under P^%d; transition-matrix spectral radius >= %.6f; entropy(P) >= ln(rho)/%d = %.6f\n",
         A_.lo, A_.hi, n - fails, n, K_, lb, K_, lb > 1 ? std::log(lb) / K_ : 0.0);
  return (fails == 0 && lb > 1) ? 0 : 1;
}
