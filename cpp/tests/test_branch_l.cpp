// Golden test: Branch L (C++ header) vs Python/mpmath cross-check (golden/branch_l_AEB2AD.tsv).
#include <cstdio>
#include <fstream>
#include <sstream>
#include <string>
#include <vector>

#include "fsot_chua/branch_l.hpp"

using namespace fsot;
struct Row { std::string dom, name, val; };

template <class R> int run(const std::vector<Row>& rows, double tol) {
  Engine<R> eng;
  const R Rr(1800), L = real_traits<R>::lit("0.022"), C2 = real_traits<R>::lit("1e-7");
  int fails = 0; double worst = 0;
  chua::KennedyNic<R> nic(R(220), R(220), R(2200), R(22000), R(22000), R(3300));
  for (auto& r : rows) {
    R got;
    if (r.dom == "NIC") got = r.name == "Ga" ? nic.Ga : (r.name == "Gb" ? nic.Gb : nic.Gc);
    else {
      chua::BranchL<R> b(eng, r.dom);
      if (r.name == "S") got = eng.domain_scalar(r.dom);
      else if (r.name == "eps") got = b.eps;
      else if (r.name == "k") got = b.k;
      else if (r.name == "Q_L") got = b.Q;
      else if (r.name == "r0_ohm") got = b.r0_ohm(L, C2);
      else got = b.gamma(Rr, L, C2);
    }
    const long double g = std::stold(r.val), c = static_cast<long double>(got);
    const double rel = double(fabsl(c - g) / fabsl(g));
    if (rel > worst) worst = rel;
    if (rel > tol) { ++fails; std::printf("FAIL %s %s %s got %.20Lg want %s rel %.3g\n", real_traits<R>::name(), r.dom.c_str(), r.name.c_str(), c, r.val.c_str(), rel); }
  }
  std::printf("%-12s rows=%zu fails=%d max_rel=%.3g (tol %.0e)\n", real_traits<R>::name(), rows.size(), fails, worst, tol);
  return fails;
}

int main(int argc, char** argv) {
  std::ifstream in(argc > 1 ? argv[1] : "golden/branch_l_AEB2AD.tsv");
  std::vector<Row> rows; std::string line;
  while (std::getline(in, line)) {
    if (line.empty() || line[0] == '#') continue;
    std::istringstream ss(line); Row r;
    std::getline(ss, r.dom, '\t'); std::getline(ss, r.name, '\t'); std::getline(ss, r.val, '\t');
    rows.push_back(r);
  }
  if (rows.empty()) { std::puts("no golden rows"); return 2; }
  int f = run<double>(rows, 1e-12) + run<long double>(rows, 1e-15);
#if defined(FSOT_HAVE_FLOAT128)
  f += run<f128>(rows, 1e-17);  // compared through long double
#endif
#if defined(FSOT_HAVE_BOOST_MP)
  f += run<mp169>(rows, 1e-17);
#endif
  std::puts(f ? "BRANCH_L_GOLDEN=FAIL" : "BRANCH_L_GOLDEN=OK");
  return f ? 1 : 0;
}
