import numpy as np, json, matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt, subprocess, os
os.makedirs('png', exist_ok=True)
# 1 bifurcation vs A (C++ ideal)
d=np.genfromtxt('results/bif_A.tsv',skip_header=1); A=np.unique(d[:,0]); m=[np.nanmedian(d[d[:,0]==a][:,2]) for a in A]
plt.figure(figsize=(10,4)); plt.plot(A,m,'k.-',ms=2,lw=.5); plt.axhline(0,color='gray',lw=.5); plt.axvline(1/((1+5**.5)/2),color='r',label='Branch J A = 1/phi (LOCK M1)')
plt.axvline(0.6182,color='m',ls=':',label='hairline window 0.6182'); plt.axvline(0.0393,color='c',ls='--',label='J1 A = k (LOCK J)'); plt.axvline(0.1509,color='b',ls='--',label='J2 A = gamma (LOCK J)')
plt.axvline(1800/3070,color='orange',label='SPICE (real diode) upper chaos edge ~0.586')
plt.xlabel('A = R/R_A'); plt.ylabel('median lambda1 [1/tau0] (NaN = unbounded)'); plt.xlim(0.4,0.8); plt.legend(fontsize=7); plt.title('Ideal PWL jerk: lambda1 vs A (C++ mj, 4 ICs, T=5000)')
plt.tight_layout(); plt.savefig('png/lambda1_vs_A_cpp.png',dpi=130); plt.close()
# 2 SPICE scan vs R_A
S=[json.loads(l) for l in open('spice/out/scan_RA.jsonl')]; R=[int(s['name'][3:]) for s in S]; nd=[s['n_distinct_maxima'] for s in S]
plt.figure(figsize=(9,3.8)); plt.semilogy(R,nd,'ko-'); plt.axvline(2912.5,color='r',label='R_A = phi R = 2912.5 (LOCK M1/M2 design)'); plt.axvspan(2640,2980,color='r',alpha=.1,label='LOCK M2 B1 band for the chaos edge')
plt.axvline(3160,color='g',label='post-hoc bench value 3.16 k'); plt.xlabel('R_A [ohm]'); plt.ylabel('distinct maxima of V(o3) (1-2 = periodic, >40 = chaotic)')
plt.legend(fontsize=7); plt.title('ngspice (TI TL082 macro-model + 1N4148): period doubling 2960->3060, chaos >= 3080'); plt.tight_layout(); plt.savefig('png/spice_RA_scan.png',dpi=130); plt.close()
# 3 attractors: C++ ideal (python RK4 quick) vs SPICE
def jerk(A,T=600,dt=0.01):
    s=np.array([-0.9,0,0]); out=[]
    f=lambda s: np.array([s[1],s[2],-A*s[2]-s[1]+abs(s[0])-1])
    for i in range(int(T/dt)):
        k1=f(s);k2=f(s+.5*dt*k1);k3=f(s+.5*dt*k2);k4=f(s+dt*k3); s=s+dt/6*(k1+2*k2+2*k3+k4)
        if i*dt>200: out.append(s.copy())
    return np.array(out)
fig,ax=plt.subplots(1,3,figsize=(14,4.2))
X=jerk(0.6180339887); ax[0].plot(X[:,0],X[:,1],lw=.3); ax[0].set_title('ideal PWL, A = 1/phi (chaotic, lambda1 0.048)'); ax[0].set_xlabel('x [U_eff]'); ax[0].set_ylabel("x'")
for k,(n,t) in enumerate([('nominal','SPICE R_A 2912.5: period-2 (B4 fails)'),('ra_3160','SPICE R_A 3160: chaotic')]):
    dd=np.loadtxt(f'spice/out/{n}.dat'); m_=dd[:,0]>0.2; ax[k+1].plot(dd[m_,1],-dd[m_,3],lw=.3,color='C1' if k==0 else 'C2'); ax[k+1].set_title(t); ax[k+1].set_xlabel('V(o3) = x [V]'); ax[k+1].set_ylabel('-V(o2) ~ tau0 x\' [V]')
plt.tight_layout(); plt.savefig('png/attractors_cpp_vs_spice.png',dpi=130); plt.close()
