"""Independent Python cross-check of the C++ rf lyap: ideal Kennedy node, lambda1 by tangent RK4."""
import math, sys, json
a=10.; b=1800*1800*100e-9/22e-3; g1=1800/220; g2=1800/22000; G1=1.1; G2=1+22000/3300; E=23/3
def cl(v): return max(-E,min(E,v))
def f(s,gam):
    x,y,z=s; h=g1*(x-cl(G1*x))+g2*(x-cl(G2*x)); return (a*(y-x-h), x-y+z, -b*y-gam*z)
def jv(s,w,gam):
    x=s[0]; d1=G1 if abs(G1*x)<E else 0; d2=G2 if abs(G2*x)<E else 0
    dh=g1*(1-d1)+g2*(1-d2); return (a*(w[1]-w[0]-dh*w[0]), w[0]-w[1]+w[2], -b*w[1]-gam*w[2])
def lyap(r0,T=4000,dt=0.005,tr=300):
    gam=b*r0/1800; s=[0.1,0,0]; w=[1,.3,.1]; acc=0; n=int((T+tr)/dt)
    for i in range(n):
        k1=f(s,gam); q1=jv(s,w,gam)
        s2=[s[j]+.5*dt*k1[j] for j in range(3)]; w2=[w[j]+.5*dt*q1[j] for j in range(3)]; k2=f(s2,gam); q2=jv(s2,w2,gam)
        s3=[s[j]+.5*dt*k2[j] for j in range(3)]; w3=[w[j]+.5*dt*q2[j] for j in range(3)]; k3=f(s3,gam); q3=jv(s3,w3,gam)
        s4=[s[j]+dt*k3[j] for j in range(3)]; w4=[w[j]+dt*q3[j] for j in range(3)]; k4=f(s4,gam); q4=jv(s4,w4,gam)
        s=[s[j]+dt/6*(k1[j]+2*k2[j]+2*k3[j]+k4[j]) for j in range(3)]; w=[w[j]+dt/6*(q1[j]+2*q2[j]+2*q3[j]+q4[j]) for j in range(3)]
        nr=math.sqrt(sum(v*v for v in w)); w=[v/nr for v in w]
        if i*dt>=tr: acc+=math.log(nr)
    return acc/T
out={r:lyap(r) for r in map(float,sys.argv[1:])}
print(json.dumps(out))
