import re, glob, json, os, matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
R={}
for f in glob.glob('results/opamp/*.txt'):
    s=open(f).read(); m=re.search(r'#mean sigc=(\S+) sd=(\S+) n=(\d+)',s)
    if m: R[os.path.basename(f)[:-4]]=(float(m.group(1)),float(m.group(2)),int(m.group(3)))
lock=json.load(open('results/lockC_formula.json'))
fr={'tl082':lock['tl082_3MHz']['frac'],'tl082h':lock['tl082h_5.25MHz']['frac'],'ua741_k1':lock['ua741_k1_lagonly']['frac'],'ua741_k10':lock['ua741_k10']['frac']}
spice={'0':(2.20,2.21,2.255,2.26),'20':(1.40,1.45,1.470,1.475),'35':(1.15,1.20,1.045,1.05),'18':(1.45,1.475,1.50,1.51)}  # TL082 lo,hi ; ideal lo,hi (SPICE, 50% or strict as noted in ERROR_BUDGET)
rows=[]
for r0 in ['18','0','20','35']:
    if 'ideal_r'+r0 not in R: continue
    i0=R['ideal_r'+r0][0]
    for v in ['tl082','tl082h','ua741_k1','ua741_k10']:
        k=f'{v}_r{r0}'
        if k not in R: continue
        sim=R[k][0]-i0; pred=fr[v]*i0
        rows.append(dict(r0=r0,model=v,ideal=i0,sigc=R[k][0],sd=R[k][1],d_sim=sim,d_pred=pred,miss=sim-pred))
for r in rows: print(r)
json.dump(dict(raw=R,rows=rows),open('results/opamp_table.json','w'),indent=1)
# plot
lab=[f"{r['model']}\nr0={r['r0']}" for r in rows]; import numpy as np; x=np.arange(len(rows))
plt.figure(figsize=(max(7,1.1*len(rows)),4.5))
plt.bar(x-.2,[r['d_pred'] for r in rows],.4,label='LOCK C prediction (dressed pole, adiabatic)')
plt.bar(x+.2,[r['d_sim'] for r in rows],.4,yerr=[r['sd']/2 for r in rows],label='rf 5-dim C++ MSF (post-lock)')
for j,r in enumerate(rows):
    if r['model']=='tl082' and r['r0'] in spice:
        lo,hi,il,ih=spice[r['r0']]; plt.plot([j+.45]*2,[lo-ih,hi-il],'k-',lw=3); 
plt.plot([],[],'k-',lw=3,label='SPICE TI TL082 minus SPICE ideal (interval, post-hoc)')
plt.axhline(0,color='k',lw=.5); plt.xticks(x,lab,fontsize=8); plt.ylabel('Delta sigma_c vs ideal op-amp'); plt.legend(fontsize=7); plt.title('Target 1: op-amp correction (LOCK C 86ae8340...)')
plt.tight_layout(); plt.savefig('png/t1_opamp_delta_sigc.png',dpi=130)
