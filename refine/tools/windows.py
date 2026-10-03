import numpy as np, json
PHI=(1+5**.5)/2
def load(f):
    d=np.loadtxt(f,skiprows=1); r=np.unique(d[:,0]); med=np.array([np.median(d[d[:,0]==x][:,2]) for x in r])
    mn=np.array([np.min(d[d[:,0]==x][:,2]) for x in r]); return r,med,mn,d
def wins(r,med,thr=0.01):
    out=[];i=0
    while i<len(r):
        if med[i]<=thr:
            j=i
            while j+1<len(r) and med[j+1]<=thr: j+=1
            out.append((r[i],r[j])); i=j+1
        else: i+=1
    return out
res={}
for nm,f in [('wide','results/lyap_wide.tsv'),('w17','results/lyap_fine_w17.tsv'),('w10','results/lyap_fine_w10.tsv'),('r1844','results/lyap_fine_1844.tsv'),('old15_20','results/lyap_fine.tsv')]:
    try: r,med,mn,d=load(f)
    except Exception as e: print(nm,e); continue
    w=wins(r,med); res[nm]=dict(range=[float(r[0]),float(r[-1])],step=float(r[1]-r[0]),windows=[[float(a),float(b)] for a,b in w],
        any_ic_periodic=[float(x) for x,m in zip(r,mn) if m<=0.01])
    print(nm,res[nm]['range'],res[nm]['step'],'windows',w[:20]); print('  any-IC periodic pts:',len(res[nm]['any_ic_periodic']), res[nm]['any_ic_periodic'][:30])
r,med,mn,d=load('results/lyap_fine_1844.tsv'); i=np.argmin(abs(r-18.44)); print('lam1 median at 18.44:',med[i], 'min over [17.94,18.94]:',med[(r>=17.94)&(r<=18.94)].min())
json.dump(res,open('results/windows.json','w'),indent=1)
