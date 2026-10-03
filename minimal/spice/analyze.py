import numpy as np, sys, json
def load(n):
    d=np.loadtxt(f'out/{n}.dat'); t=d[:,0]; x=d[:,1]; return t,x
def stats(n, t0=0.1):
    t,x=load(n); m=t>t0; t=t[m]; x=x[m]
    tu=np.arange(t[0],t[-1],2e-6); xu=np.interp(tu,t,x)
    sp=np.abs(np.fft.rfft((xu-xu.mean())*np.hanning(len(xu)))); fr=np.fft.rfftfreq(len(xu),2e-6); k=np.argmax(sp*(fr>100))
    i=np.where((xu[1:-1]>xu[:-2])&(xu[1:-1]>=xu[2:]))[0]+1; pk=xu[i]
    nd=len(np.unique(np.round(pk,2)))
    # spectral flatness in 100 Hz - 5 kHz as broadband indicator
    band=(fr>100)&(fr<5000); flat=float(np.exp(np.mean(np.log(sp[band]+1e-30)))/np.mean(sp[band]))
    return dict(name=n,xmin=float(xu.min()),xmax=float(xu.max()),f_peak=float(fr[k]),n_distinct_maxima=int(nd),n_maxima=int(len(pk)),flatness=flat)
def lyap(a,b):
    ta,xa=load(a); tb,xb=load(b); tu=np.arange(0.01,min(ta[-1],tb[-1]),2e-6); d=np.abs(np.interp(tu,ta,xa)-np.interp(tu,tb,xb))+1e-12
    ld=np.log(d); i=np.where(d>0.3)[0]; te=tu[i[0]] if len(i) else tu[-1]
    m=(tu<te)&(d>1e-6)
    if m.sum()<100: return dict(lam_per_s=None)
    p=np.polyfit(tu[m],ld[m],1); return dict(lam_per_s=float(p[0]),fit_window_s=[float(tu[m][0]),float(te)])
if __name__=='__main__':
    out=[stats(n) for n in sys.argv[1:]]
    for o in out: print(json.dumps(o))
