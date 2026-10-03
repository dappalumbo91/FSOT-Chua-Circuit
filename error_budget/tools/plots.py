import numpy as np, matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt, os, glob
R='results'; P='png'
def tsv(f):
    L=[l.rstrip('\n').split('\t') for l in open(f) if not l.startswith('#')]; h=L[0]; return h,L[1:]
def heat(f,zcol,title,out,cmap='viridis',vmin=None,vmax=None,fsot=None,mask_nan=True):
    if not os.path.exists(f) or os.path.getsize(f)==0: return
    h,L=tsv(f); a=np.array([[float(x) for x in r[:len(h)]] for r in L])
    x=np.unique(a[:,0]); y=np.unique(a[:,1]); Z=np.full((len(y),len(x)),np.nan)
    ix={v:i for i,v in enumerate(x)}; iy={v:i for i,v in enumerate(y)}
    for r in a: Z[iy[r[1]],ix[r[0]]]=r[h.index(zcol)]
    plt.figure(figsize=(6.4,4.8)); plt.pcolormesh(x,y,Z,shading='nearest',cmap=cmap,vmin=vmin,vmax=vmax); plt.colorbar(label=zcol)
    if fsot: plt.plot(*fsot,'r*',ms=14,label='FSOT Branch L operating point'); plt.legend(loc='upper right',fontsize=8)
    plt.xlabel(h[0]); plt.ylabel(h[1]); plt.title(title,fontsize=10); plt.tight_layout(); plt.savefig(f'{P}/{out}',dpi=130); plt.close()
def regime(f,title,out,fsot=None):
    if not os.path.exists(f) or os.path.getsize(f)==0: return
    h,L=tsv(f); a=np.array([[float(x) for x in r[:len(h)]] for r in L])
    x=np.unique(a[:,0]); y=np.unique(a[:,1]); Z=np.full((len(y),len(x)),np.nan)
    for r in a:
        lam,mx,x2,fp=r[2],r[3],r[4],r[5]
        if mx>=x2: c=3          # outer cycle escape
        elif mx<0.05 or lam<-0.005: c=0  # fixed point
        elif lam>0.01 and 0.15<fp<0.85: c=2  # double scroll
        elif lam>0.01: c=1.5    # single-scroll chaos
        else: c=1               # periodic
        Z[np.searchsorted(y,r[1]),np.searchsorted(x,r[0])]=c
    from matplotlib.colors import ListedColormap, BoundaryNorm
    cm=ListedColormap(['#dddddd','#9ecae1','#fdd0a2','#31a354','#de2d26']); nm=BoundaryNorm([-0.5,0.75,1.25,1.75,2.5,3.5],cm.N)
    plt.figure(figsize=(6.4,4.8)); plt.pcolormesh(x,y,Z,shading='nearest',cmap=cm,norm=nm)
    cb=plt.colorbar(ticks=[0,1,1.5,2,3]); cb.ax.set_yticklabels(['fixed pt','periodic','single-scroll chaos','double scroll','outer-cycle escape'])
    if fsot: plt.plot(*fsot,'k*',ms=14)
    plt.xlabel(h[0]); plt.ylabel(h[1]); plt.title(title,fontsize=10); plt.tight_layout(); plt.savefig(f'{P}/{out}',dpi=130); plt.close()
g0=0.150873134394159; b0=14.72727273
regime(f'{R}/map_gamma_beta.tsv','Single node regime vs (gamma, beta); star = FSOT/BOM','regime_gamma_beta.png',(g0,b0))
regime(f'{R}/map_ba_alpha.tsv','Single node regime vs (b/a, alpha)','regime_ba_alpha.png',(81/150,10))
regime(f'{R}/map_x2_gamma.tsv','Single node regime vs (x2=Bp2/Bp1, gamma)','regime_x2_gamma.png',(230/33,g0))
heat(f'{R}/map_gamma_beta.tsv','lambda1','Largest Lyapunov exponent, single node','lam1_gamma_beta.png','magma',fsot=(g0,b0))
heat(f'{R}/msfmap_gamma_alpha.tsv','sigma_c_msf','sigma_c (MSF, 3-ring) vs (gamma, alpha)','sigc_gamma_alpha.png','viridis',0,4,(g0,10))
heat(f'{R}/msfmap_gamma_ba.tsv','sigma_c_msf','sigma_c (MSF, 3-ring) vs (gamma, b/a)','sigc_gamma_ba.png','viridis',0,4,(g0,81/150))
# network maps
for f in glob.glob(f'{R}/mapnet_N_topo*.tsv'):
    if os.path.getsize(f)==0: continue
    h,L=tsv(f); 
    fig,ax=plt.subplots(1,2,figsize=(11,4.2))
    for k,tp in enumerate(['ring','all']):
        rows=[r for r in L if r[1]==tp]; Ns=sorted(set(int(r[0]) for r in rows)); sg=sorted(set(float(r[2]) for r in rows))
        Z=np.zeros((len(Ns),len(sg))); 
        for r in rows:
            i=Ns.index(int(r[0])); j=sg.index(float(r[2])); lk,sy,es,cl=int(r[4]),int(r[5]),int(r[6]),int(r[7])
            # 0 desync chaos, 1 cluster (1<clusters<N), 2 escape(outer), 3 lock
            st=3 if lk else (2 if es else (1 if 1<cl<int(r[0]) else 0)); Z[i,j]+=st
        cnt=len(set(r[3] for r in rows)); Z/=cnt
        im=ax[k].pcolormesh(sg,Ns,Z,shading='nearest',cmap='RdYlGn',vmin=0,vmax=3); ax[k].set_title(f'{tp}: mean state (0 desync,1 cluster,2 outer escape,3 LOCK)',fontsize=8)
        ax[k].set_xlabel('sigma'); ax[k].set_ylabel('N')
        lam2={ 'ring':lambda N:2-2*np.cos(2*np.pi/N),'all':lambda N:N}[tp]
        ax[k].plot([3*1.4955/lam2(N) for N in Ns],Ns,'k^--',label='MSF: 3*1.4955/lambda2'); ax[k].legend(fontsize=7)
    fig.colorbar(im,ax=ax); fig.suptitle(os.path.basename(f),fontsize=9); plt.savefig(f'{P}/'+os.path.basename(f).replace('.tsv','.png'),dpi=120); plt.close()
# ring lock curve
for f,lab in [('ring_fine_base.tsv','T=2000'),('ring_T8000.tsv','T=8000'),('ring_noampcheck.tsv','no amplitude check')]:
    p=f'{R}/{f}'
    if not os.path.exists(p): continue
    rows=[l.split('\t') for l in open(p) if l[0].isdigit()]; s=np.array([float(r[0]) for r in rows]); lk=np.array([int(r[3]) for r in rows])
    us=np.unique(s); plt.plot(us,[lk[s==u].mean() for u in us],'.-',label=lab,ms=3)
plt.axvline(1.4897,c='r',ls='--',label='locked MSF 1.4897'); plt.axvline(1.525,c='k',ls=':',label='earlier 5/6 @0.025 grid'); plt.axhline(5/6,c='gray',lw=.5)
plt.xlabel('sigma'); plt.ylabel('lock fraction (48 seeds)'); plt.legend(fontsize=7); plt.title('3-ring lock probability, r0 = 18.44 ohm'); plt.tight_layout(); plt.savefig(f'{P}/ring_lock_probability.png',dpi=130); plt.close()
# standard r0 curve with datasheet DCR bands
if os.path.exists(f'{R}/std_r0scan.tsv'):
    a=np.array([[float(x) for x in l.split('\t')[:5]] for l in open(f'{R}/std_r0scan.tsv') if l[0].isdigit()])
    plt.figure(figsize=(7,4.5)); m=a[:,4]==1; plt.plot(a[m,0],a[m,2],'o-',label='sigma_c MSF (double scroll)'); plt.plot(a[~m,0],np.where(a[~m,2]>0,a[~m,2],np.nan),'x',c='gray',label='not double scroll')
    for lo,hi,lab,c in [(43.23,55,'Wurth 7447720223 typ..max','C1'),(45.6,56,'Bourns RLB0913-223K typ..max','C2'),(82.5,82.5,'Murata 22R226C max','C3'),(0,22,'2x TDK TSL1315-103J + 222J (max 22)','C4')]:
        plt.axvspan(lo,max(hi,lo+0.6),alpha=.2,color=c,label=lab)
    plt.axvline(18.44,c='r',ls='--',label='FSOT r0 18.44'); plt.axvline(13.5,c='k',ls=':',label='Kennedy 1992 measured RL 13.5 (18 mH)')
    plt.xlabel('inductor series resistance r (ohm)'); plt.ylabel('sigma_c (3-ring, MSF)'); plt.ylim(0,2.5); plt.legend(fontsize=6.5); plt.tight_layout(); plt.savefig(f'{P}/standard_sigc_vs_r_datasheets.png',dpi=130); plt.close()
# MC histograms
fig,ax=plt.subplots(figsize=(7,4.2))
for f in sorted(glob.glob(f'{R}/mc_[A-F]_*.tsv')):
    rows=[l.split('\t') for l in open(f) if l[0].isdigit()]
    if not rows: continue
    v=np.array([float(r[7]) for r in rows if int(r[8])==1 and float(r[7])>0])
    if len(v)>5: ax.hist(v,bins=40,range=(0.8,2.6),histtype='step',label=f'{os.path.basename(f)[3:-4]} (n_ds={len(v)}/{len(rows)})')
ax.axvline(1.4897,c='r',ls='--',label='FSOT locked 1.4897'); ax.set_xlabel('sigma_c equivalent (= 18000/Rc*)'); ax.legend(fontsize=6); plt.tight_layout(); plt.savefig(f'{P}/mc_sigc_histograms.png',dpi=130); plt.close()
print(sorted(os.listdir(P)))
