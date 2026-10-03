"""Lock fraction vs sigma at the FSOT value r0 = 18.44 ohm: C++ (48 seeds), ngspice ideal + TL082 (3 ICs), MSF."""
import json, os, collections, numpy as np, matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
H = os.path.dirname(os.path.abspath(__file__)); EB = os.path.dirname(H); SP = os.path.join(os.path.dirname(EB), 'spice', 'out')
rows = [l.split('\t') for l in open(os.path.join(EB, 'results', 'ring_fine_base.tsv')) if l[0].isdigit()]
s = np.array([float(r[0]) for r in rows]); lk = np.array([int(r[3]) for r in rows]); us = np.unique(s)
plt.figure(figsize=(8, 4.6)); plt.plot(us, [lk[s == u].mean() for u in us], '-', lw=1, color='k', label='C++ RK4, 48 seeds, grid 0.001 (sigma50 = 1.4954)')
for f, lab, c in [('ring_ideal_r0_18.44.jsonl', 'ngspice ideal op-amp, 3 ICs', 'C0'), ('ring_tl082_r0_18.44.jsonl', 'ngspice TI TL082 macromodel, 3 ICs', 'C3')]:
    p = os.path.join(SP, f)
    if not os.path.exists(p): continue
    by = collections.defaultdict(list)
    for l in open(p): r = json.loads(l); by[r['sigma']].append(r['lock'])
    x = sorted(by); plt.plot(x, [np.mean(by[k]) for k in x], 'o--', color=c, label=lab)
plt.axvline(1.4897, color='g', ls=':', label='FSOT locked MSF sigma_c = 1.4897')
plt.axhline(5 / 6, color='gray', lw=.5); plt.xlim(1.39, 1.63); plt.ylim(-0.05, 1.05)
plt.xlabel('sigma = alpha R / Rc'); plt.ylabel('lock fraction'); plt.title('3-ring lock vs coupling at r0 = 18.44 ohm (FSOT Branch L), 2000 tau', fontsize=10)
plt.legend(fontsize=7, loc='lower right'); plt.tight_layout(); plt.savefig(os.path.join(EB, 'png', 'lock_vs_sigma_r0_18p44.png'), dpi=130)
