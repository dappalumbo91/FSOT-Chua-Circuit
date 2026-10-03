import numpy as np, glob, os, json, sys
R='results'; out={}
def roots(f):
    r=[float(l.split()[2]) for l in open(f) if l.startswith('#root')]; return np.array(r)
def msf_curve(f):
    d=[l.split() for l in open(f) if l[0].isdigit()]; d=np.array(d,float); return d
for f in sorted(glob.glob(f'{R}/msf_fine*.tsv'))+sorted(glob.glob(f'{R}/pred_msf*.tsv')):
    r=roots(f)
    if len(r): 
        b=np.array([np.random.default_rng(1).choice(r,len(r)).mean() for _ in range(1)])
        rng=np.random.default_rng(0); bs=[rng.choice(r,len(r)).mean() for _ in range(4000)]
        out[os.path.basename(f)]=dict(n=len(r),mean=r.mean(),sd=r.std(ddof=1),ci95=list(np.percentile(bs,[2.5,97.5])),ic0=r[0])
        print(os.path.basename(f),'n=%d mean=%.5f sd=%.5f CI95=[%.5f,%.5f] ic0=%.5f'%(len(r),r.mean(),r.std(ddof=1),*np.percentile(bs,[2.5,97.5]),r[0]))
# ring files: columns?
def ring(f):
    L=[l.rstrip('\n').split('\t') for l in open(f)]; hdr=[l for l in L if l[0].startswith('#') or l[0]=='sigma']; 
    return L
json.dump(out,open(f'{R}/analysis_msf.json','w'),indent=1)
