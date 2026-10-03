import numpy as np, matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
PHI=(1+5**.5)/2
def med(f):
    d=np.loadtxt(f,skiprows=1); r=np.unique(d[:,0]); return r,np.array([np.median(d[d[:,0]==x][:,2]) for x in r])
fig,ax=plt.subplots(2,1,figsize=(12,8),sharex=True)
r,m=med('results/lyap_wide.tsv'); ax[0].plot(r,m,'k-',lw=.8,label='median lambda1, step 0.1 ohm, T=10000')
for f,c in [('results/lyap_fine.tsv','b'),('results/lyap_fine_w10.tsv','g')]:
    r2,m2=med(f); ax[0].plot(r2,m2,c+'-',lw=.6,label=f.split('/')[-1])
ax[0].axhline(0.01,color='gray',ls=':'); ax[0].axvline(18.44,color='r',label='r0 = 18.44 ohm (FSOT)')
for n in range(0,7): ax[0].axvline(18.44*PHI**(-n/2),color='orange',ls='--',lw=.6)
ax[0].axvline(-1,color='orange',ls='--',lw=.6,label='18.44 phi^(-n/2) (LOCK A H3b)'); ax[0].set_ylabel('lambda1 [1/tau]'); ax[0].legend(fontsize=7); ax[0].set_xlim(0,40)
p=np.loadtxt('results/peaks_wide.tsv'); ax[1].plot(p[:,0],p[:,1],',k',alpha=.3); ax[1].axvline(18.44,color='r'); ax[1].set_xlabel('r0 [ohm]'); ax[1].set_ylabel('local maxima of x (V_C1 / 1 V)')
plt.tight_layout(); plt.savefig('png/t3_lyap_bif_wide.png',dpi=130); plt.close()
fig,ax=plt.subplots(2,1,figsize=(12,8),sharex=True)
r2,m2=med('results/lyap_fine.tsv'); ax[0].plot(r2,m2,'b.-',lw=.5,ms=2,label='step 0.01, T=20000, 3 ICs')
r3,m3=med('results/lyap_fine_1844.tsv'); ax[0].plot(r3,m3,'g.-',lw=.5,ms=2,label='step 0.005')
r4,m4=med('results/lyap_fine_w17.tsv'); ax[0].plot(r4,m4,'c.-',lw=.5,ms=2,label='step 0.005')
ax[0].axhline(0.01,color='gray',ls=':'); ax[0].axvline(18.44,color='r'); ax[0].axvspan(17.94,18.94,color='r',alpha=.08,label='H3a band 18.44 +- 0.5'); ax[0].legend(fontsize=7); ax[0].set_xlim(16.5,19.5); ax[0].set_ylabel('median lambda1')
p=np.loadtxt('results/peaks_fine.tsv'); ax[1].plot(p[:,0],p[:,1],',k',alpha=.15); ax[1].axvline(18.44,color='r'); ax[1].set_xlabel('r0 [ohm]'); ax[1].set_ylabel('local maxima of x')
plt.tight_layout(); plt.savefig('png/t3_lyap_bif_fine_16p5_19p5.png',dpi=130)
