"""LOCK D2 scoring plot: Branch D (C++ bd.cpp) vs ngspice (TI TL082 + 1N4148) chaos edges, plus derived-knob points."""
import json, collections
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
def bd_edge(f):
    ch = collections.defaultdict(list)
    for l in open(f):
        if l[0].isdigit():
            r = l.split('\t'); ch[float(r[0])].append(float(r[3]) > 0.005 and r[7].strip() == '0')
    return min(k for k, v in ch.items() if any(v))
S = [json.loads(l) for l in open('spice/out/lockd2.jsonl')]
def sp_edge(tag): return min(r['RA'] for r in S if r['name'].split('_')[1] == tag and r['n_distinct_maxima'] > 40)
cases = [('27 °C, ±9 V (not blind)', 'scan_T27', 'T27'), ('0 °C', 'scan_T0', 'T0'), ('60 °C', 'scan_T60', 'T60'), ('±12 V', 'scan_Vs12', 'V12')]
b0 = bd_edge('results/bd/scan_T27.tsv'); s0 = sp_edge('T27')
fig, ax = plt.subplots(1, 2, figsize=(11, 4))
for i, (lab, f, t) in enumerate(cases):
    b = bd_edge(f'results/bd/{f}.tsv'); s = sp_edge(t)
    ax[0].bar(i - 0.2, b - b0, 0.4, color='C0', label='Branch D (C++, locked D2)' if i == 0 else None)
    ax[0].bar(i + 0.2, s - s0, 0.4, color='C1', label='ngspice TI TL082 + 1N4148' if i == 0 else None)
    print(lab, 'BD edge', b, 'shift', b - b0, '| SPICE edge', s, 'shift', s - s0)
ax[0].set_xticks(range(4)); ax[0].set_xticklabels([c[0] for c in cases], fontsize=8); ax[0].set_ylabel('chaos-edge shift ΔR_A [Ω]'); ax[0].axhline(0, color='k', lw=.5); ax[0].legend(fontsize=8)
ax[0].set_title('LOCK D2 blind edge shifts (10 Ω scan step)')
for t, c in (('T27', 'k'), ('T0', 'b'), ('T60', 'r'), ('V12', 'g')):
    v = sorted([r for r in S if r['name'].split('_')[1] == t], key=lambda r: r['RA']); ax[1].semilogy([r['RA'] for r in v], [r['n_distinct_maxima'] for r in v], 'o-', color=c, ms=3, label=t)
ax[1].axhline(40, color='gray', ls=':'); ax[1].set_xlabel('R_A [Ω]'); ax[1].set_ylabel('distinct maxima of V(o3)'); ax[1].legend(fontsize=8)
ax[1].set_title('ngspice; FSOT knob R/γ_rel = 4205 Ω: rail latch (not shown)')
plt.tight_layout(); plt.savefig('png/lockD2_edge_shifts.png', dpi=130)
