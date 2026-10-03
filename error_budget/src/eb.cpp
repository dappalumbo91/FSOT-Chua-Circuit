// eb.cpp — commands for the sigma_c error budget and pressure-point maps. Args are key=value.
//   msf     sig=lo:hi:step lam2=3 T=3000 dt=0.005 trans=200 nic=1 [model keys]
//   ring    sig=lo:hi:step seeds=24 N=3 topo=ring T=2000 tail=500 dt=0.005 madcut= tritcut= ampcheck=1 [model keys]
//   basin   sig=lo:hi:step eps=e1,e2,.. seeds=24 [run keys]
//   sens    params=gamma,a,... rel=0.02 nic=4 T=6000 sig=1.40:1.60:0.01
//   ringeig sig=lo:hi:step T=1000
//   map1    p1=name:lo:hi:n p2=name:lo:hi:n T=1000
//   msfmap  p1=... p2=... sig=0:4:0.05 T=1500
//   mapnet  Ns=3,4,5,6 topos=ring,all sig=lo:hi:step seeds=8 T=1500 tail=300
// model keys: alpha beta gamma r0 a b c x2 ba (b = ba*a)
#include "eb.hpp"
#include <cstdlib>
#include <map>
#include <sstream>
#include <string>

using namespace eb;
using Args = std::map<std::string, std::string>;

static std::vector<double> range(const std::string& s) {  // lo:hi:step or comma list
  std::vector<double> v;
  if (s.find(':') != std::string::npos) {
    double lo, hi, st; std::sscanf(s.c_str(), "%lf:%lf:%lf", &lo, &hi, &st);
    long n = std::lround((hi - lo) / st);
    for (long i = 0; i <= n; ++i) v.push_back(lo + i * st);
  } else { std::stringstream ss(s); std::string t; while (std::getline(ss, t, ',')) v.push_back(std::atof(t.c_str())); }
  return v;
}
static std::vector<std::string> split(const std::string& s) { std::vector<std::string> v; std::stringstream ss(s); std::string t; while (std::getline(ss, t, ',')) v.push_back(t); return v; }
static double get(const Args& a, const std::string& k, double d) { auto it = a.find(k); return it == a.end() ? d : std::atof(it->second.c_str()); }
static std::string gets(const Args& a, const std::string& k, const std::string& d) { auto it = a.find(k); return it == a.end() ? d : it->second; }

static const double R0_FSOT = 18.4400497592861384;
static void set_param(Model& m, const std::string& k, double v) {
  if (k == "alpha") m.alpha = v; else if (k == "beta") m.beta = v; else if (k == "gamma") m.gamma = v;
  else if (k == "r0") m.gamma = Model::gamma_from_r0(v); else if (k == "a") m.a = v; else if (k == "b") m.b = v;
  else if (k == "c") m.c = v; else if (k == "x2") m.x2 = v; else if (k == "ba") m.b = v * m.a;
  else { std::fprintf(stderr, "unknown param %s\n", k.c_str()); std::exit(2); }
}
static double get_param(const Model& m, const std::string& k) {
  if (k == "alpha") return m.alpha; if (k == "beta") return m.beta; if (k == "gamma") return m.gamma; if (k == "a") return m.a;
  if (k == "b") return m.b; if (k == "c") return m.c; if (k == "x2") return m.x2; if (k == "ba") return m.b / m.a;
  if (k == "r0") return m.gamma / Model::gamma_from_r0(1.0);
  return NAN;
}
static Model model_from(const Args& a) {
  Model m; m.gamma = Model::gamma_from_r0(R0_FSOT);
  for (const char* k : {"alpha", "beta", "a", "b", "c", "x2", "gamma", "r0", "ba"}) if (a.count(k)) set_param(m, k, get(a, k, 0));
  return m;
}
static RunCfg cfg_from(const Args& a) {
  RunCfg c; c.T = get(a, "T", 2000); c.tail = get(a, "tail", 500); c.dt = get(a, "dt", 0.005);
  c.mad_cut_rel = get(a, "madcut", c.mad_cut_rel); c.trit_cut = get(a, "tritcut", c.trit_cut); c.amp_check = get(a, "ampcheck", 1) != 0;
  return c;
}
static double sigc_msf(const Model& m, const std::vector<double>& sig, double lam2, double T, double dt, double trans, unsigned seed) {
  std::vector<double> se; for (double s : sig) se.push_back(lam2 * s);
  auto o = msf(m, se, T, dt, trans, seed);
  return fit_root(sig, o.lam);
}

int main(int argc, char** argv) {
  if (argc < 2) { std::fprintf(stderr, "usage: eb <cmd> key=value...\n"); return 1; }
  std::string cmd = argv[1]; Args A;
  for (int i = 2; i < argc; ++i) { std::string s = argv[i]; auto p = s.find('='); if (p != std::string::npos) A[s.substr(0, p)] = s.substr(p + 1); }
  Model m = model_from(A);
  std::printf("# cmd=%s alpha=%.10g beta=%.10g gamma=%.10g a=%.10g b=%.10g c=%.10g x2=%.10g\n", cmd.c_str(), m.alpha, m.beta, m.gamma, m.a, m.b, m.c, m.x2);

  if (cmd == "msf") {
    auto sig = range(gets(A, "sig", "1.40:1.60:0.005")); double lam2 = get(A, "lam2", 3), T = get(A, "T", 3000), dt = get(A, "dt", 0.005), tr = get(A, "trans", 200);
    int nic = int(get(A, "nic", 1));
    std::vector<std::vector<double>> L(nic); std::vector<double> mx(nic);
    std::vector<double> se; for (double s : sig) se.push_back(lam2 * s);
    parallel_for(nic, [&](size_t i) { auto o = msf(m, se, T, dt, tr, unsigned(i)); L[i] = o.lam; mx[i] = o.maxabs; });
    std::printf("ic\tsigma\tlambda_perp\n");
    for (int i = 0; i < nic; ++i) for (size_t k = 0; k < sig.size(); ++k) std::printf("%d\t%.6f\t%.7f\n", i, sig[k], L[i][k]);
    for (int i = 0; i < nic; ++i) std::printf("#root\t%d\t%.6f\tmaxabs=%.4f\n", i, fit_root(sig, L[i]), mx[i]);
    return 0;
  }
  if (cmd == "ring" || cmd == "basin") {
    auto sig = range(gets(A, "sig", "1.45:1.60:0.005")); int ns = int(get(A, "seeds", 24)), N = int(get(A, "N", 3));
    Net net = gets(A, "topo", "ring") == "all" ? Net::all(N) : Net::ring(N);
    RunCfg c = cfg_from(A); double amp_ref = single_amp(m, c.T, c.tail, c.dt);
    std::vector<double> eps = cmd == "basin" ? range(gets(A, "eps", "1e-6,1e-3,1e-2,0.1,0.3,1")) : std::vector<double>{-1};
    struct Job { double s, e; int seed; RunOut r; };
    std::vector<Job> jobs; for (double e : eps) for (double s : sig) for (int k = 1; k <= ns; ++k) jobs.push_back({s, e, k, {}});
    // basin ICs: points on the single-node attractor (transient 500 + seed-dependent extra time), plus a
    // zero-mean transverse perturbation of norm eps across the nodes
    std::vector<std::vector<double>> att(ns + 1);
    if (cmd == "basin") {
      for (int k = 1; k <= ns; ++k) {
        Net one = Net::ring(1); one.nb = {{}}; RunCfg c1; std::vector<double> s1 = {0.1, 0, 0}, k1(3), k2(3), k3(3), k4(3), t(3);
        long n = long((500 + 7.31 * k) / 0.005);
        for (long q = 0; q < n; ++q) { net_f(m, one, 0, s1, k1); for (int j = 0; j < 3; ++j) t[j] = s1[j] + .0025 * k1[j]; net_f(m, one, 0, t, k2); for (int j = 0; j < 3; ++j) t[j] = s1[j] + .0025 * k2[j]; net_f(m, one, 0, t, k3); for (int j = 0; j < 3; ++j) t[j] = s1[j] + .005 * k3[j]; net_f(m, one, 0, t, k4); for (int j = 0; j < 3; ++j) s1[j] += .005 / 6 * (k1[j] + 2 * k2[j] + 2 * k3[j] + k4[j]); }
        att[k] = s1;
      }
    }
    parallel_for(jobs.size(), [&](size_t i) {
      auto& j = jobs[i]; std::vector<double> s;
      if (cmd == "ring") s = random_ic(N, unsigned(j.seed));
      else {
        std::mt19937_64 g(1000 + j.seed); std::normal_distribution<double> nd(0, 1);
        s.assign(3 * N, 0); std::vector<double> p(3 * N); double nr = 0;
        for (int q = 0; q < 3 * N; ++q) p[q] = nd(g);
        for (int d = 0; d < 3; ++d) { double mu = 0; for (int q = 0; q < N; ++q) mu += p[3 * q + d] / N; for (int q = 0; q < N; ++q) p[3 * q + d] -= mu; }
        for (double v : p) nr += v * v; nr = std::sqrt(nr);
        for (int q = 0; q < N; ++q) for (int d = 0; d < 3; ++d) s[3 * q + d] = att[j.seed][d] + j.e * p[3 * q + d] / nr;
      }
      j.r = net_run(m, net, j.s, s, c, amp_ref);
    });
    std::printf("# amp_ref=%.6f N=%d topo=%s T=%g tail=%g dt=%g madcut=%g tritcut=%g ampcheck=%d\n", amp_ref, N, gets(A, "topo", "ring").c_str(), c.T, c.tail, c.dt, c.mad_cut_rel, c.trit_cut, int(c.amp_check));
    std::printf("sigma\teps\tseed\tlocked\tsynced\tescaped_tail\tt_escape\tt_sync\tmad\tamp\ttrit\tmaxabs\tclusters\tpair_sync_frac\n");
    for (auto& j : jobs) std::printf("%.6f\t%g\t%d\t%d\t%d\t%d\t%.2f\t%.2f\t%.4g\t%.4f\t%.4f\t%.4f\t%d\t%.3f\n", j.s, j.e, j.seed, int(j.r.locked), int(j.r.synced), int(j.r.escaped_tail), j.r.t_escape, j.r.t_sync, j.r.mad, j.r.amp, j.r.trit, j.r.maxabs, j.r.clusters, j.r.pair_sync_frac);
    return 0;
  }
  if (cmd == "sens") {
    auto names = split(gets(A, "params", "gamma,a,b,c,x2,alpha,beta")); double rel = get(A, "rel", 0.02);
    int nic = int(get(A, "nic", 4)); double T = get(A, "T", 6000); auto sig = range(gets(A, "sig", "1.40:1.60:0.01"));
    struct Job { int p, sgn, ic; double root; };
    std::vector<Job> jobs;
    for (int ic = 0; ic < nic; ++ic) jobs.push_back({-1, 0, ic, 0});
    for (int p = 0; p < int(names.size()); ++p) for (int sg : {-1, 1}) for (int ic = 0; ic < nic; ++ic) jobs.push_back({p, sg, ic, 0});
    parallel_for(jobs.size(), [&](size_t i) {
      Model mm = m; auto& j = jobs[i];
      if (j.p >= 0) { double v = get_param(m, names[j.p]); set_param(mm, names[j.p], v * (1 + j.sgn * rel)); }
      j.root = sigc_msf(mm, sig, 3, T, 0.005, 200, unsigned(j.ic));
    });
    std::printf("param\tsign\tic\tvalue\tsigma_c\n");
    for (auto& j : jobs) std::printf("%s\t%d\t%d\t%.10g\t%.6f\n", j.p < 0 ? "base" : names[j.p].c_str(), j.sgn, j.ic, j.p < 0 ? 0 : get_param(m, names[j.p]) * (1 + j.sgn * rel), j.root);
    return 0;
  }
  if (cmd == "ringeig") {  // full nonlinear 3-ring: growth of a tiny transverse perturbation vs MSF at 3 sigma
    auto sig = range(gets(A, "sig", "1.0:2.0:0.1")); double T = get(A, "T", 1000);
    std::vector<double> lam(sig.size());
    parallel_for(sig.size(), [&](size_t q) {
      Net net = Net::ring(3); std::vector<double> s(9), k1(9), k2(9), k3(9), k4(9), t(9);
      std::vector<double> u = {0.1, 0, 0}; Net one = Net::ring(1); one.nb = {{}};
      for (long k = 0; k < long(200 / 0.005); ++k) { net_f(m, one, 0, u, k1); for (int j = 0; j < 3; ++j) t[j] = u[j] + .0025 * k1[j]; net_f(m, one, 0, t, k2); for (int j = 0; j < 3; ++j) t[j] = u[j] + .0025 * k2[j]; net_f(m, one, 0, t, k3); for (int j = 0; j < 3; ++j) t[j] = u[j] + .005 * k3[j]; net_f(m, one, 0, t, k4); for (int j = 0; j < 3; ++j) u[j] += .005 / 6 * (k1[j] + 2 * k2[j] + 2 * k3[j] + k4[j]); }
      const double e0 = 1e-8; double pert[9] = {1, .3, .1, -.5, -.15, -.05, -.5, -.15, -.05}, pn = 0; for (double v : pert) pn += v * v; pn = std::sqrt(pn);
      for (int i = 0; i < 9; ++i) s[i] = u[i % 3] + e0 * pert[i] / pn;
      double acc = 0; long steps = long(T / 0.005), every = 200;
      for (long k = 1; k <= steps; ++k) {
        net_f(m, net, sig[q], s, k1); for (int j = 0; j < 9; ++j) t[j] = s[j] + .0025 * k1[j];
        net_f(m, net, sig[q], t, k2); for (int j = 0; j < 9; ++j) t[j] = s[j] + .0025 * k2[j];
        net_f(m, net, sig[q], t, k3); for (int j = 0; j < 9; ++j) t[j] = s[j] + .005 * k3[j];
        net_f(m, net, sig[q], t, k4); for (int j = 0; j < 9; ++j) s[j] += .005 / 6 * (k1[j] + 2 * k2[j] + 2 * k3[j] + k4[j]);
        if (k % every == 0) {  // renormalise the transverse part about the node mean
          double mu[3] = {0, 0, 0}, nr = 0; for (int i = 0; i < 9; ++i) mu[i % 3] += s[i] / 3;
          for (int i = 0; i < 9; ++i) nr += (s[i] - mu[i % 3]) * (s[i] - mu[i % 3]); nr = std::sqrt(nr);
          acc += std::log(nr / e0);
          for (int i = 0; i < 9; ++i) s[i] = mu[i % 3] + (s[i] - mu[i % 3]) * e0 / nr;
        }
      }
      lam[q] = acc / T;
    });
    std::vector<double> se; for (double s : sig) se.push_back(3 * s);
    auto o = msf(m, se, T, 0.005, 200, 0);
    std::printf("sigma\tlambda_ring_nonlinear\tlambda_msf_3sigma\n");
    for (size_t q = 0; q < sig.size(); ++q) std::printf("%.4f\t%.6f\t%.6f\n", sig[q], lam[q], o.lam[q]);
    return 0;
  }
  if (cmd == "map1" || cmd == "msfmap") {
    auto P = [&](const std::string& k) { auto v = split(gets(A, k, "")); return std::make_tuple(v[0], std::atof(v[1].c_str()), std::atof(v[2].c_str()), std::atoi(v[3].c_str())); };
    auto [n1, lo1, hi1, c1] = P("p1"); auto [n2, lo2, hi2, c2] = P("p2"); double T = get(A, "T", cmd == "map1" ? 1000 : 1500);
    auto sig = range(gets(A, "sig", "0:4:0.05"));
    struct Cell { double v1, v2, lam1, mx, sigc; double lobe; };
    std::vector<Cell> cells;
    for (int i = 0; i < c1; ++i) for (int j = 0; j < c2; ++j) cells.push_back({lo1 + (hi1 - lo1) * i / std::max(1, c1 - 1), lo2 + (hi2 - lo2) * j / std::max(1, c2 - 1), 0, 0, NAN, 0});
    parallel_for(cells.size(), [&](size_t q) {
      Model mm = m; auto& c = cells[q]; set_param(mm, n1, c.v1); set_param(mm, n2, c.v2);
      std::vector<double> se = {0.0};
      if (cmd == "msfmap") for (double s : sig) se.push_back(3 * s);
      auto o = msf(mm, se, T, 0.005, 200, 0);
      c.lam1 = o.lam[0]; c.mx = o.maxabs;
      if (cmd == "msfmap") { std::vector<double> l(o.lam.begin() + 1, o.lam.end()); c.sigc = fit_root(sig, l); if (l.front() <= 0) c.sigc = 0; }
      // lobe occupancy on the single node
      Net one = Net::ring(1); one.nb = {{}}; std::vector<double> s = {0.1, 0, 0}, k1(3), k2(3), k3(3), k4(3), t(3); long pos = 0, cnt = 0;
      for (long k = 0; k < long(600 / 0.005); ++k) { net_f(mm, one, 0, s, k1); for (int j = 0; j < 3; ++j) t[j] = s[j] + .0025 * k1[j]; net_f(mm, one, 0, t, k2); for (int j = 0; j < 3; ++j) t[j] = s[j] + .0025 * k2[j]; net_f(mm, one, 0, t, k3); for (int j = 0; j < 3; ++j) t[j] = s[j] + .005 * k3[j]; net_f(mm, one, 0, t, k4); for (int j = 0; j < 3; ++j) s[j] += .005 / 6 * (k1[j] + 2 * k2[j] + 2 * k3[j] + k4[j]);
        if (k > long(200 / 0.005)) { ++cnt; pos += s[0] > 0; } if (!std::isfinite(s[0])) break; }
      c.lobe = cnt ? double(pos) / cnt : NAN;
    });
    std::printf("%s\t%s\tlambda1\tmaxabs\tx2\tfrac_pos\tsigma_c_msf\n", n1.c_str(), n2.c_str());
    for (auto& c : cells) { Model mm = m; set_param(mm, n1, c.v1); set_param(mm, n2, c.v2); std::printf("%.6g\t%.6g\t%.5f\t%.4f\t%.4f\t%.4f\t%.5f\n", c.v1, c.v2, c.lam1, c.mx, mm.x2, c.lobe, c.sigc); }
    return 0;
  }
  if (cmd == "mapnet") {
    auto Ns = range(gets(A, "Ns", "3,4,5,6")); auto topos = split(gets(A, "topos", "ring,all")); auto sig = range(gets(A, "sig", "0:5:0.1"));
    int ns = int(get(A, "seeds", 8)); RunCfg c = cfg_from(A); if (!A.count("T")) c.T = 1500; if (!A.count("tail")) c.tail = 300;
    double amp_ref = single_amp(m, c.T, c.tail, c.dt);
    struct Job { int N; std::string topo; double s; int seed; RunOut r; };
    std::vector<Job> jobs; for (double N : Ns) for (auto& tp : topos) for (double s : sig) for (int k = 1; k <= ns; ++k) jobs.push_back({int(N), tp, s, k, {}});
    parallel_for(jobs.size(), [&](size_t i) { auto& j = jobs[i]; Net net = j.topo == "all" ? Net::all(j.N) : Net::ring(j.N); j.r = net_run(m, net, j.s, random_ic(j.N, unsigned(j.seed)), c, amp_ref); });
    std::printf("# amp_ref=%.6f T=%g tail=%g\nN\ttopo\tsigma\tseed\tlocked\tsynced\tescaped_tail\tclusters\tpair_sync_frac\tmaxabs\tt_escape\n", amp_ref, c.T, c.tail);
    for (auto& j : jobs) std::printf("%d\t%s\t%.4f\t%d\t%d\t%d\t%d\t%d\t%.3f\t%.4f\t%.2f\n", j.N, j.topo.c_str(), j.s, j.seed, int(j.r.locked), int(j.r.synced), int(j.r.escaped_tail), j.r.clusters, j.r.pair_sync_frac, j.r.maxabs, j.r.t_escape);
    return 0;
  }
  std::fprintf(stderr, "unknown cmd\n"); return 1;
}
