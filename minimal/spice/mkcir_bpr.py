"""LOCK B design B-PR netlist: canonical jerk at A = gamma_rel with a precision half-wave rectifier (TI TL082 macro-models, 1N4148)."""
import sys
def cir(name, o3=-0.3, o2=0.0, o1=0.0, RA='4.22k', tstop=0.6, temp=27):
    return f"""* FSOT B-PR: x''' = -gamma_rel x'' - x' - x + 2 max(x,0) - 1 ; R = 1.8k, C = 100n (tau0 = 180 us), RA = R/gamma_rel
.include models/vendor/ti_sloj070/TL082.301
.model D1N4148 D(Is=2.52n Rs=0.568 N=1.752 Cjo=4p M=0.4 tt=20n BV=100)
.temp {temp}
Vcc vcc 0 9
Vee vee 0 -9
* start: operating point solved with outputs held at .ic (no uic), so op-amp internal nodes are consistent and the state starts at (o3,o2,o1)
* U1 summing integrator: -A o1 - o3 - o4 + 2 max - U
RA o1 n1 {RA}
Rx o3 n1 1.8k
Rw o4 n1 1.8k
Rr r n1 900
Rc vcc n1 40.2k
C1 n1 o1 100n
XU1 0 n1 vcc vee o1 TL082
R2 o1 n2 1.8k
C2 n2 o2 100n
XU2 0 n2 vcc vee o2 TL082
R3 o2 n3 1.8k
C3 n3 o3 100n
XU3 0 n3 vcc vee o3 TL082
* U4 unity inverter: o4 = -o2
R4 o2 n4 1.8k
Rf4 o4 n4 1.8k
XU4 0 n4 vcc vee o4 TL082
* U5 precision half-wave rectifier: r = -max(o3, 0)
R5 o3 n5 1.8k
Rf5 r n5 1.8k
Da u5 n5 D1N4148
Db r u5 D1N4148
XU5 0 n5 vcc vee u5 TL082
.ic v(o3)={o3} v(o2)={o2} v(o1)={o1} v(o4)={-o2} v(r)={-max(o3,0)} v(n1)=0 v(n2)=0 v(n3)=0 v(n4)=0 v(n5)=0
.options method=gear reltol=1e-6 abstol=1e-11 vntol=1e-8
.tran 2u {tstop} 0 2u
.control
run
wrdata out/{name}.dat v(o3) v(o2) v(o1)
quit
.endc
.end
"""
