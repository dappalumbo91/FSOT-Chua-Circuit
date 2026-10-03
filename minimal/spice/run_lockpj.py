"""LOCK PJ ngspice: winner B = Theta, G = kappa/gamma_rel, precision-rectifier topology, TI TL082 models."""
import subprocess, json, sys
from concurrent.futures import ThreadPoolExecutor
from mkcir_pj import cir
import analyze
U = 9 * 1800 / 40200; R = 1800.0; g = 0.42804344605980688; B = 0.91751027120648765; G = 0.73504813634763333
ex = dict(RA=f'{R/g:.2f}', RB=f'{R/B:.2f}', RG=f'{R/G:.2f}', RR=f'{R/(2*G):.2f}')
e96 = dict(RA='4.22k', RB='1.96k', RG='2.43k', RR='1.21k')
ic = dict(o3=-2.542110 * U, o2=-0.838748 * U, o1=1.708328 * U)
J = [('pj6_attr', dict(**ic, **ex)), ('pj7_default', dict(o3=-0.3, **ex)), ('pjx_attr_e96', dict(**ic, **e96)), ('pjx_default_e96', dict(o3=-0.3, **e96))]
def job(a):
    n, kw = a; open(f'netlists/{n}.cir', 'w').write(cir(n, **kw)); subprocess.run(['ngspice', '-b', f'netlists/{n}.cir'], stdout=open(f'out/{n}.log', 'w'), stderr=subprocess.STDOUT)
    return n, analyze.stats(n)
with ThreadPoolExecutor(4) as e: Rr = dict(e.map(job, J))
json.dump(Rr, open('out/lockpj.json', 'w'), indent=1)
for k, v in Rr.items(): print(k, v)
