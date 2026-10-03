import numpy as np, glob, os, json, sys
from scipy.optimize import minimize
R='results'
def load(f):
    rows=[l.split('\t') for l in open(f) if l[0].isdigit()]
    s=np.array([float(r[0]) for r in rows]); lk=np.array([int(r[3]) for r in rows]); esc=np.array([int(r[5]) for r in rows]); sy=np.array([int(r[4]) for r in rows])
    return s,lk,esc,sy
def fit(s,y):
    def nll(p):
        z=(s-p[0])/abs(p[1]); q=1/(1+np.exp(-z)); q=np.clip(q,1e-9,1-1e-9); return -(y*np.log(q)+(1-y)*np.log(1-q)).sum()
    r=minimize(nll,[np.median(s),0.01],method='Nelder-Mead'); return r.x[0],abs(r.x[1])
def thr56(s,y):
    us=np.unique(s); p=np.array([y[s==u].mean() for u in us]); ok=p>=5/6
    for i in range(len(us)):
        if ok[i:].all(): return us[i]
    return np.nan
res={}
for f in sorted(glob.glob(f'{R}/ring_*.tsv')):
    try: s,lk,esc,sy=load(f)
    except Exception as e: continue
    if len(s)==0: continue
    m50,w=fit(s,lk); t=thr56(s,lk)
    rng=np.random.default_rng(0); us=np.unique(s); bs=[];bt=[]
    for _ in range(300):
        idx=np.concatenate([rng.choice(np.where(s==u)[0],(s==u).sum()) for u in us]); a,_=fit(s[idx],lk[idx]); bs.append(a); bt.append(thr56(s[idx],lk[idx]))
    # sigma where p=5/6 from logistic
    s56=m50+w*np.log(5)
    res[os.path.basename(f)]=dict(n_per_sigma=int((s==us[0]).sum()),sigma50=m50,width=w,ci50=list(np.percentile(bs,[2.5,97.5])),sigma56_logistic=s56,thr56_rule=t,thr56_ci=list(np.nanpercentile(bt,[2.5,97.5])),
        sync_any50=fit(s,sy)[0])
    r=res[os.path.basename(f)]
    print('%-28s n=%d sigma50=%.4f [%.4f,%.4f] w=%.4f s56log=%.4f rule56=%.4f [%.4f,%.4f] sync50(any)=%.4f'%(os.path.basename(f),r['n_per_sigma'],m50,*r['ci50'],w,s56,t,*r['thr56_ci'],r['sync_any50']))
json.dump(res,open(f'{R}/analysis_ring.json','w'),indent=1)
