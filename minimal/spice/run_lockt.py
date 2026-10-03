"""LOCK T T4 (winner S-a: x''' = -g x'' - x + sgn(x), comparator) and LOCK T2 T2-5 (canonical board at 4205 ohm from the mapped attractor IC) in ngspice (TI TL082 + 1N4148)."""
import subprocess, json
from mkcir import cir
import analyze
def run(name, s):
    open(f'netlists/{name}.cir', 'w').write(s); subprocess.run(['ngspice', '-b', f'netlists/{name}.cir'], stdout=open(f'out/{name}.log', 'w'), stderr=subprocess.STDOUT)
    return analyze.stats(name)
sa = """* LOCK T winner S-a: x''' = -gamma_rel x'' - x + sgn(x); R = 1.8k, C = 100n, RA = R/gamma_rel = 4.22k (E96), comparator swing sets the volt scale only
.include models/vendor/ti_sloj070/TL082.301
Vcc vcc 0 9
Vee vee 0 -9
RA o1 n1 4.22k
Rx o3 n1 1.8k
Rs o4 n1 15k
C1 n1 o1 100n
XU1 0 n1 vcc vee o1 TL082
R2 o1 n2 1.8k
C2 n2 o2 100n
XU2 0 n2 vcc vee o2 TL082
R3 o2 n3 1.8k
C3 n3 o3 100n
XU3 0 n3 vcc vee o3 TL082
XU4 0 o3 vcc vee o4 TL082
.ic v(o3)=-0.3 v(o2)=0 v(o1)=0 v(n1)=0 v(n2)=0 v(n3)=0
.options method=gear reltol=1e-5 abstol=1e-10 vntol=1e-7
.tran 2u 0.6 0 2u uic
.control
run
wrdata out/t4_Sa.dat v(o3) v(o2) v(o1)
quit
.endc
.end
"""
r = {'T4_Sa': run('t4_Sa', sa)}
s = cir(4205.2, ic=-0.44, name='t25_4205').replace('.ic v(o3)=-0.44 v(o2)=0 v(o1)=0', '.ic v(o3)=-0.44 v(o2)=0.2 v(o1)=0.2')
r['T2-5'] = run('t25_4205', s)
print(json.dumps(r, indent=1)); json.dump(r, open('out/lockt.json', 'w'), indent=1)
