import subprocess, json
from concurrent.futures import ThreadPoolExecutor
from mkcir_bpr import cir
import analyze
U = 9 * 1800 / 40200
J = [('b5_attr', dict(o3=-1.04 * U, o2=0.2 * U, o1=0.2 * U)), ('b6_default', dict(o3=-0.3)), ('b5_attr_long', dict(o3=-1.04 * U, o2=0.2 * U, o1=0.2 * U, tstop=1.5))]
def job(a):
    n, kw = a; open(f'netlists/{n}.cir', 'w').write(cir(n, **kw)); subprocess.run(['ngspice', '-b', f'netlists/{n}.cir'], stdout=open(f'out/{n}.log', 'w'), stderr=subprocess.STDOUT)
    return n, analyze.stats(n)
with ThreadPoolExecutor(3) as ex: R = dict(ex.map(job, J))
print(json.dumps(R, indent=1)); json.dump(R, open('out/lockb.json', 'w'), indent=1)
