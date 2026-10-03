"""LOCK T analytic screen (no simulation): FSOT-fixed damping A = gamma_rel in one-nonlinearity jerk topologies.
Jerk: x''' + A x'' + B x' + C x = s*N(x) + E. Equilibria come from C x = s N(x) + E, and the linearisation is l^3 + A l^2 + B l + (C - s N'(x*)) = 0."""
import numpy as np, json
g = 0.42804344605980688  # gamma_rel (fsot-law-circuit results/design.json:3)
FS = {'1': 1.0, 'K': 0.42010876364988792, 'Theta': 0.91751027120648765, 'kappa': 0.31463253730207974, 'kappa/gamma_rel': 0.73504813634763333, 'gamma_rel': g, 'S_EM': 0.9557285700955828}
out = []
# F1: |x| family x''' + g x'' + B x' = |x| - 1. A time/amplitude rescaling gives the canonical A_eff = g/sqrt(B) (slope- and offset-invariant)
for k, B in FS.items():
    Ae = g / np.sqrt(B); band_ideal = 0.547 <= Ae <= 0.6405; band_real = 0.529 <= Ae <= 0.584
    out.append(dict(id=f'F1[B={k}]', eq=f"x'''+{g:.4f}x''+{B:.4f}x'=|x|-1", A_eff=round(Ae, 4), passes=bool(band_ideal or band_real), parts='4 op-amps, 1 diode, 9 R, 3 C (current board)', note='canonical bands from results/bif_A.tsv (ideal) and the ngspice scan (real diode)'))
# F2: unit-coefficient topologies
def parts(N, B):
    if N == 'sgn': op = 3 + 1 + (1 if B else 0); R = 2 + 1 + 1 + 1 + (2 if B else 0); return op, 0, R  # R2,R3, RA, Rx, Rs(+ inverter pair)
    op = 4; R = 2 + 1 + 1 + 1 + 2 + (1 if B else 0); return op, 1, R  # |x|: summer U4 (Rf, Rd), Rc
F2 = [('S-a', 0, 1, 'sgn', +1, 0), ('S-b', 0, 1, 'sgn', -1, 0), ('S-c', 1, 1, 'sgn', +1, 0), ('S-d', 1, 1, 'sgn', -1, 0), ('S-e', 1, 0, 'sgn', +1, 0), ('S-f', 0, 0, 'sgn', +1, 0),
      ('A-a', 0, 0, 'abs', +1, -1), ('A-b', 0, 0, 'abs', -1, +1), ('A-c', 1, 0, 'abs', -1, +1)]
for cid, B, C, N, s, E in F2:
    eqs = []
    for side in (+1, -1):  # x>0 and x<0
        Np, N0 = (0.0, side * 1.0) if N == 'sgn' else (float(side), 0.0)  # N = Np*x + N0 on this side
        a = C - s * Np; b = s * N0 + E
        if abs(a) > 1e-12:
            x = b / a
            if x * side > 0: eqs.append((x, np.roots([1, g, B, a])))
    sf = []
    for x, r in eqs:
        rr = [z for z in r if abs(z.imag) < 1e-12]; cc = [z for z in r if abs(z.imag) >= 1e-12]
        if len(cc) == 2 and len(rr) == 1:
            lr = rr[0].real; sig = cc[0].real
            if lr * sig < 0: sf.append(abs(sig) / abs(lr))
    unstable_all = bool(eqs) and all(max(z.real for z in r) > 0 for _, r in eqs)
    passes = len(eqs) >= 2 and unstable_all and len(sf) == len(eqs) and all(q < 1 for q in sf)
    op, d, R = parts(N, B)
    out.append(dict(id=cid, eq=f"x'''+{g:.4f}x''+{B}x'+{C}x={'+' if s > 0 else '-'}{'sgn(x)' if N == 'sgn' else '|x|'}{'' if E == 0 else ('%+d' % E)}",
                    equilibria=[round(x, 4) for x, _ in eqs], eig=[[complex(round(z.real, 4), round(z.imag, 4)).__repr__() for z in r] for _, r in eqs],
                    shilnikov_ratio=[round(q, 4) for q in sf], all_unstable=unstable_all, passes=bool(passes), parts=f'{op} op-amps, {d} diode, {R} R, 3 C', score=op + d + R + 3))
json.dump(out, open('screen.json', 'w'), indent=1)
for o in out: print(o['id'], o['passes'], o.get('A_eff', ''), o.get('equilibria', ''), o.get('shilnikov_ratio', ''), o['parts'])
