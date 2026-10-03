"""Generate ngspice netlists for the FSOT minimal jerk circuit (TL082 TI macro-model as the TL07x/TL08x JFET proxy; 1N4148)."""
import sys
PHI=(1+5**.5)/2
def cir(RA, ic=-0.5, tstop=0.6, name='jerk', model='ti'):
    opa = '.include models/vendor/ti_sloj070/TL082.301' if model=='ti' else ''
    X = (lambda p,m,o: f"XU{o} {p} {m} vcc vee {o} TL082") if model=='ti' else (lambda p,m,o: f"E{o} {o} 0 {p} {m} 1e6")
    return f"""* FSOT minimal chaotic circuit: x''' = -A x'' - x' + |x| - 1, A = R/RA (R = 1.8k, C = 100n, tau0 = 180us)
{opa}
.model D1N4148 D(Is=2.52n Rs=0.568 N=1.752 Cjo=4p M=0.4 tt=20n BV=100)
Vcc vcc 0 9
Vee vee 0 -9
* U1: summing integrator (out o1 = tau0^2 x'')
RA o1 n1 {RA:.4g}
Rw o4 n1 1.8k
Rx o3 n1 1.8k
Rc vcc n1 40.2k
C1 n1 o1 100n
{X('0','n1','o1')}
* U2: integrator (out o2 = -tau0 x')
R2 o1 n2 1.8k
C2 n2 o2 100n
{X('0','n2','o2')}
* U3: integrator (out o3 = x)
R3 o2 n3 1.8k
C3 n3 o3 100n
{X('0','n3','o3')}
* U4: inverting summer with the single nonlinearity (1N4148 half-wave): o4 = -(o2 + 2 max(x - Vd, 0))
R4 o2 n4 1.8k
Rf o4 n4 1.8k
D1 o3 dn D1N4148
Rd dn n4 900
{X('0','n4','o4')}
.ic v(o3)={ic} v(o2)=0 v(o1)=0 v(n1)=0 v(n2)=0 v(n3)=0
.options method=gear reltol=1e-5 abstol=1e-10 vntol=1e-7
.tran 2u {tstop} 0 2u uic
.control
run
wrdata out/{name}.dat v(o3) v(o2) v(o1)
quit
.endc
.end
"""
if __name__=='__main__':
    RA=float(sys.argv[1]); name=sys.argv[2]; ic=float(sys.argv[3]) if len(sys.argv)>3 else -0.5; model=sys.argv[4] if len(sys.argv)>4 else 'ti'
    open(f'netlists/{name}.cir','w').write(cir(RA,ic,name=name,model=model))
