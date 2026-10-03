// non-rigorous section sampler for X''' = -A X'' - B X' + G|X| - G on {X = 0, Y > 0} (geometry for the h-sets only)
#include <cstdio>
#include <cstdlib>
#include <cmath>
int main(int ac, char** av) { double A = 0.42804344605980688, B = atof(av[1]), G = atof(av[2]); double v[3] = {atof(av[3]), atof(av[4]), atof(av[5])}; int N = atoi(av[6]);
  auto f = [&](const double* s, double* d) { d[0] = s[1]; d[1] = s[2]; d[2] = -A * s[2] - B * s[1] + G * std::fabs(s[0]) - G; };
  double h = 0.001; int n = 0; long it = 0;
  while (n < N) { double k1[3], k2[3], k3[3], k4[3], t[3], o[3] = {v[0], v[1], v[2]};
    f(v, k1); for (int i = 0; i < 3; ++i) t[i] = v[i] + h / 2 * k1[i]; f(t, k2); for (int i = 0; i < 3; ++i) t[i] = v[i] + h / 2 * k2[i]; f(t, k3); for (int i = 0; i < 3; ++i) t[i] = v[i] + h * k3[i]; f(t, k4);
    for (int i = 0; i < 3; ++i) v[i] += h / 6 * (k1[i] + 2 * k2[i] + 2 * k3[i] + k4[i]); ++it;
    if (it > 500000 && o[0] < 0 && v[0] >= 0) { double s = -o[0] / (v[0] - o[0]); printf("%.15f %.15f\n", o[1] + s * (v[1] - o[1]), o[2] + s * (v[2] - o[2])); ++n; } } }
