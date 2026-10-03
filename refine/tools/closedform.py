import numpy as np, json
be0=1800**2*100e-9/22e-3; a0=-15/11; b0=-81/110
def sstar(m,g,al,be):
    ok=lambda s:(lambda A:(1+g+A>0) and (A*(g+be)-al*g>0) and ((1+g+A)*(g+be+A*(1+g)-al)>A*(g+be)-al*g))(al*(1+m)+s)
    if ok(0): return 0.0
    prev=0.0
    for s in np.arange(0.01,40,0.01):   # smallest s (first entry into the Hurwitz set), then bisection refine
        if ok(s):
            lo,hi=prev,s
            for _ in range(40):
                mid=(lo+hi)/2; lo,hi=(lo,mid) if ok(mid) else (mid,hi)
            return hi
        prev=s
    return np.nan
out={}
g0=be0*18.4400497592861384/1800
F5a=sstar(b0,g0,10,be0)/3; pin=0.0560
F5b=(pin*sstar(a0,g0,10,be0)+(1-pin)*sstar(b0,g0,10,be0))/3
out['base']=dict(gamma=g0,s_b=sstar(b0,g0,10,be0),s_a=sstar(a0,g0,10,be0),F5a=F5a,F5b=F5b,p_in=pin,sigma50=1.4954,dev_a=F5a/1.4954-1,dev_b=F5b/1.4954-1)
print(out['base'])
for f,p2 in [('../error_budget/results/msfmap_gamma_alpha.tsv','alpha'),('../error_budget/results/msfmap_gamma_ba.tsv','ba')]:
    L=[l.split('\t') for l in open(f) if l[0].isdigit() or l[0]=='.']
    ms=[];fa=[]
    for r in L:
        g=float(r[0]); v=float(r[1]); sc=float(r[6]); mx=float(r[3]); lam=float(r[2])
        if not np.isfinite(sc) or sc<=0 or mx>=6.9 or lam<0.01: continue
        al=v if p2=='alpha' else 10; b=b0 if p2=='alpha' else v*a0
        ms.append(sc); fa.append(sstar(b,g,al,be0)/3)
    ms=np.array(ms);fa=np.array(fa); r=np.corrcoef(ms,fa)[0,1]; ratio=ms/fa
    out[f.split('/')[-1]]=dict(n=len(ms),corr=r,ratio_mean=ratio.mean(),ratio_sd=ratio.std(),rel_err_mean=np.mean(np.abs(fa/ms-1)))
    print(f.split('/')[-1],out[f.split('/')[-1]])
json.dump(out,open('results/closedform.json','w'),indent=1,default=float)
