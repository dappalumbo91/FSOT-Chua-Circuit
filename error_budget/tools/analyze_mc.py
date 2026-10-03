import numpy as np, glob, os, json
out={}
for f in sorted(glob.glob('results/mc_*.tsv')):
    rows=[l.split('\t') for l in open(f) if l[0].isdigit()]
    if not rows: continue
    sc=np.array([float(r[7]) for r in rows]); cl=np.array([int(r[8]) for r in rows])
    ok=(cl==1)&np.isfinite(sc)&(sc>0)
    d=dict(n=len(rows),frac_double_scroll=float((cl==1).mean()),class_counts={int(k):int((cl==k).sum()) for k in np.unique(cl)})
    if ok.sum()>2:
        s=sc[ok]; d.update(mean=s.mean(),sd=s.std(ddof=1),p2_5=np.percentile(s,2.5),p50=np.median(s),p97_5=np.percentile(s,97.5),min=s.min(),max=s.max())
    if len(rows[0])>9:
        rt=np.array([float(r[9]) for r in rows]); g=np.isfinite(rt); d.update(ring_n=int(g.sum()),ring_mean=rt[g].mean() if g.any() else None,ring_sd=rt[g].std(ddof=1) if g.sum()>1 else None,
            ring_p2_5=np.percentile(rt[g],2.5) if g.any() else None, ring_p97_5=np.percentile(rt[g],97.5) if g.any() else None)
    out[os.path.basename(f)]=d; print(os.path.basename(f), {k:(round(v,4) if isinstance(v,float) else v) for k,v in d.items()})
json.dump(out,open('results/analysis_mc.json','w'),indent=1,default=float)
