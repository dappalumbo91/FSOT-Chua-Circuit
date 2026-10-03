import json, matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
d=json.load(open('results/opamp_table.json')); R=d['raw']
base=1.4955; par=-0.0024
lockd=json.load(open('results/lockC_formula.json'))
d_lock=lockd['tl082_3MHz']['frac']*1.49702
d_sim=R['tl082_r18'][0]-R['ideal_r18'][0]; d_simh=R['tl082h_r18'][0]-R['ideal_r18'][0]
rows=[('ideal MSF IC-mean (error_budget)',base),('+ op-amp TL082, LOCK C formula (genuine)',base+d_lock),('+ parasitics, LOCK B (genuine)',base+d_lock+par),
      ('alt: + op-amp TL082 rf 5-dim sim (post-lock)',base+d_sim+par),('alt: + op-amp TL08xH rf sim',base+d_simh+par)]
out=dict(base=base,d_opamp_lock=d_lock,d_opamp_sim_tl082=d_sim,d_opamp_sim_tl08xh=d_simh,d_par=par,
 total_locked=base+d_lock+par,total_sim_tl082=base+d_sim+par,total_sim_tl08xh=base+d_simh+par,def_offset_5of6=0.012)
json.dump(out,open('results/t6_budget.json','w'),indent=1); print(json.dumps(out,indent=1))
plt.figure(figsize=(9,4.2)); y=range(len(rows))
plt.barh(list(y),[v for _,v in rows],color=['gray','C0','C0','C2','C2']); plt.yticks(list(y),[n for n,_ in rows],fontsize=8)
for i,(_,v) in enumerate(rows): plt.text(v+0.001,i,f'{v:.4f}',va='center',fontsize=8)
plt.axvspan(1.45,1.475,color='orange',alpha=.3,label='SPICE TI TL082 (1.45,1.475]'); plt.axvspan(1.44,1.46,color='purple',alpha=.15,label='eb C++ single-pole ring (1.44,1.46]')
plt.axvline(1.4954,color='k',ls='--',label='C++ ideal ring sigma50 1.4954'); plt.xlim(1.40,1.51); plt.legend(fontsize=7,loc='lower left'); plt.title('Target 6: refined sigma_c budget at r0 = 18.44 ohm (sigma50 definition)')
plt.tight_layout(); plt.savefig('png/t6_refined_budget.png',dpi=130)
