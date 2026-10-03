import numpy as np, matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt, sys
sys.path.insert(0,'tools'); 
exec(open('tools/closedform.py').read().split("out={}")[0])  # sstar, constants
fig,ax=plt.subplots(1,2,figsize=(11,4.5))
for k,(f,p2) in enumerate([('../error_budget/results/msfmap_gamma_alpha.tsv','alpha'),('../error_budget/results/msfmap_gamma_ba.tsv','ba')]):
    ms=[];fa=[];c=[]
    for l in open(f):
        if not (l[0].isdigit() or l[0]=='.'): continue
        r=l.split('\t'); g=float(r[0]); v=float(r[1]); sc=float(r[6]); mx=float(r[3]); lam=float(r[2])
        if not np.isfinite(sc) or sc<=0 or mx>=6.9 or lam<0.01: continue
        al=v if p2=='alpha' else 10; b=b0 if p2=='alpha' else v*a0
        ms.append(sc); fa.append(sstar(b,g,al,be0)/3); c.append(v)
    s=ax[k].scatter(fa,ms,c=c,s=12,cmap='viridis'); plt.colorbar(s,ax=ax[k],label=p2)
    m=max(max(fa),max(ms)); ax[k].plot([0,m],[0,m],'k--',lw=.8,label='y=x'); ax[k].plot([0,m],[0,1.128*m],'r:',lw=.8,label='y=phi^(1/4) x')
    ax[k].plot([1.3214],[1.4954],'r*',ms=14,label='nominal (F5a 1.3214, sigma50 1.4954)')
    ax[k].set_xlabel('F5a = s*(b)/3  (closed form)'); ax[k].set_ylabel('MSF sigma_c'); ax[k].set_title(f'grid gamma x {p2}'); ax[k].legend(fontsize=7)
plt.tight_layout(); plt.savefig('png/t5_closedform_vs_msf.png',dpi=130); plt.close()
obs=['Q_L','ring-down\n2L/r [ms]','spiral f\n[kHz]','lobe switch\n[1/s /100]','lambda1\n[1/s /1000]','max|V_C1|\n[V]','ring lock\n@sigma 1.44 [/24]']
L=[25.44,2.386,2.558,5.26,1.472,4.325,0]; Lp=[17.99,1.688,2.568,3.24,1.088,4.339,24]
x=np.arange(len(obs)); plt.figure(figsize=(10,4.2)); plt.bar(x-.2,L,.4,label='Branch L (r0 18.44 ohm)'); plt.bar(x+.2,Lp,.4,label="Branch L' (r0 26.07 ohm)")
for i in range(len(obs)): plt.text(x[i]-.2,L[i],f'{L[i]:g}',ha='center',va='bottom',fontsize=7); plt.text(x[i]+.2,Lp[i],f'{Lp[i]:g}',ha='center',va='bottom',fontsize=7)
plt.xticks(x,obs,fontsize=8); plt.yscale('symlog',linthresh=1); plt.legend(); plt.title("Target 4: L vs L' discriminating observables (LOCK B 3594a469...)"); plt.tight_layout(); plt.savefig('png/t4_L_vs_Lprime_observables.png',dpi=130)
