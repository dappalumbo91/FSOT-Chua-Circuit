import json, subprocess
subprocess.run(['python3','tools/opamp_table.py'],check=True,capture_output=True); subprocess.run(['python3','tools/t6_budget.py'],check=True,capture_output=True)
d=json.load(open('results/opamp_table.json')); R=d['raw']; b=json.load(open('results/t6_budget.json'))
tol={'tl082':0.015,'tl082h':0.015,'ua741_k1':0.04,'ua741_k10':0.015}
t=['| r0 [Ω] | op-amp | σc ideal (rf) | σc op-amp (rf) | Δ sim | Δ LOCK C | miss | within tol? |','|---|---|---|---|---|---|---|---|']
for r in d['rows']:
    t.append(f"| {r['r0'] if r['r0']!='18' else '18.44'} | {r['model']} | {r['ideal']:.4f} | {r['sigc']:.4f} ± {r['sd']:.4f} | {r['d_sim']:+.4f} | {r['d_pred']:+.4f} | {r['miss']:+.4f} | {'yes' if abs(r['miss'])<=tol[r['model']] else 'no'} |")
g=lambda k: f"{R[k][0]-R['ideal_r18'][0]:+.3f}" if k in R else 'n/a'
s=open('REFINE_REPORT.tmpl.md').read().replace('@@OPAMP_TABLE@@','\n'.join(t)).replace('@@G2@@',g('gbw_2e6')).replace('@@G3@@',g('gbw_3e6')).replace('@@G5@@',g('gbw_5.25e6'))
s=s.replace('@@DL@@',f"{b['d_opamp_lock']:+.4f}").replace('@@DS@@',f"{b['d_opamp_sim_tl082']:+.4f}").replace('@@DH@@',f"{b['d_opamp_sim_tl08xh']:+.4f}")
s=s.replace('@@TL@@',f"{b['total_locked']:.4f}").replace('@@ML@@',f"{1.45-b['total_locked']:.3f}").replace('@@TS@@',f"{b['total_sim_tl082']:.4f}").replace('@@TH@@',f"{b['total_sim_tl08xh']:.4f}")
sc=f"{sum(1 for r in d['rows'] if abs(r['miss'])<=tol[r['model']])} of {len(d['rows'])}"; s=s.replace('@@SCORE@@',sc)
open('REFINE_REPORT.md','w').write(s); print('\n'.join(t)); print(sum(1 for r in d['rows'] if abs(r['miss'])<=tol[r['model']]),'/',len(d['rows']))
