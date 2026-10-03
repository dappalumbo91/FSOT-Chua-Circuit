"""Path J analytic screen (no simulation). Family x''' + g x'' + B x' = G|x| - 1 with g = gamma_rel and B, G from the applied FSOT set.
Rescaling (t -> t sqrt(B), x -> x/G scale) gives the 2-parameter normal form x''' + a x'' + x' = q(|x| - 1/q...) ; essential pair (a, q) = (g/sqrt(B), G/B^1.5).
Heuristic chaos index (Routh-Hurwitz at x- = -1/G: stable iff g*B > G): chi = g*B/G, compared with the canonical ideal chaos band chi in [0.547, 0.6405] (results/bif_A.tsv, G = B = 1)."""
import numpy as np, json, itertools
g = 0.42804344605980688
FS = {'1': 1.0, 'K': 0.42010876364988792, 'Theta': 0.91751027120648765, 'kappa': 0.31463253730207974, 'kappa/gamma_rel': 0.73504813634763333, 'gamma_rel': g, 'S_EM': 0.9557285700955828}
out = []
for (kb, B), (kg, G) in itertools.product(FS.items(), FS.items()):
    chi = g * B / G
    em = np.roots([1, g, B, G]); ep = np.roots([1, g, B, -G])  # at x- and x+
    cm = em[np.abs(em.imag) > 1e-12]; om = float(abs(cm[0].imag)) if len(cm) else 0.0
    unstable = bool(max(em.real) > 0 and max(ep.real) > 0)
    out.append(dict(B=kb, G=kg, Bv=B, Gv=G, chi=chi, a=g / np.sqrt(B), q=G / B ** 1.5, in_band=bool(0.547 <= chi <= 0.6405), unstable=unstable,
                    omega_minus=om, f_Hz=om / (2 * np.pi * 180e-6), eq_minus=-1 / G, re_minus=float(max(em.real))))
json.dump(out, open('screen_j.json', 'w'), indent=1)
for o in sorted(out, key=lambda o: o['chi']):
    if o['in_band']: print(f"{o['B']:16s} {o['G']:16s} chi={o['chi']:.4f} f={o['f_Hz']:.1f}Hz x-={o['eq_minus']:.3f} unstable={o['unstable']}")
print(sum(o['in_band'] for o in out), 'in band of', len(out))
