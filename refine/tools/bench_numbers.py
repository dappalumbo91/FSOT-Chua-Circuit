"""Python cross-check: bench observables of the ideal node at r0=18.44 (V_C1, V_C2 in volts with Bp1=1 V; i_L = z*1V/R)."""
import numpy as np, json
a=10.; b=1800*1800*100e-9/22e-3; g1=1800/220; g2=1800/22000; G1=1.1; G2=1+22000/3300; E=23/3
def run(r0,T=3000,dt=0.002,tr=300):
    gam=b*r0/1800
    def f(s):
        x,y,z=s; h=g1*(x-np.clip(G1*x,-E,E))+g2*(x-np.clip(G2*x,-E,E)); return np.array([a*(y-x-h),x-y+z,-b*y-gam*z])
    s=np.array([0.1,0,0]); n=int((T+tr)/dt); out=[]
    for i in range(n):
        k1=f(s);k2=f(s+.5*dt*k1);k3=f(s+.5*dt*k2);k4=f(s+dt*k3); s=s+dt/6*(k1+2*k2+2*k3+k4)
        if i*dt>=tr and i%5==0: out.append(s.copy())
    X=np.array(out); tau=1800*100e-9
    x,y,z=X.T; fs=1/(5*dt*tau); sp=np.abs(np.fft.rfft(x*np.hanning(len(x)))); fr=np.fft.rfftfreq(len(x),1/fs)
    pk=fr[np.argmax(sp*(fr>500))]
    return dict(r0=r0,Vc1_max=float(abs(x).max()),Vc1_rms=float(np.sqrt((x**2).mean())),Vc1_mean=float(x.mean()),
        Vc2_max=float(abs(y).max()),Vc2_rms=float(np.sqrt((y**2).mean())),iL_max_mA=float(abs(z).max()/1800*1e3),iL_rms_mA=float(np.sqrt((z**2).mean())/1800*1e3),
        O2_frac_railed=float((abs(G2*x)>=E).mean()),spec_peak_Hz=float(pk))
print(json.dumps([run(18.4400497592861384),run(0.0)],indent=1))
