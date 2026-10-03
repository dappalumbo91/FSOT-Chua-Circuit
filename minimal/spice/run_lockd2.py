"""LOCK D2 scoring runs: ngspice (TI TL082 + 1N4148) edge scans at 27/0/60 C and Vs=12 V, plus derived-knob points."""
import subprocess, json, sys, os
from concurrent.futures import ThreadPoolExecutor
from mkcir import cir
import analyze
os.makedirs('netlists', exist_ok=True); os.makedirs('out', exist_ok=True)
def job(a):
    name, RA, T, Vs = a
    s = cir(RA, name=name).replace('Vcc vcc 0 9', f'Vcc vcc 0 {Vs}').replace('Vee vee 0 -9', f'Vee vee 0 -{Vs}')
    s = s.replace('.options', f'.temp {T}\n.options')
    open(f'netlists/{name}.cir', 'w').write(s)
    subprocess.run(['ngspice', '-b', f'netlists/{name}.cir'], stdout=open(f'out/{name}.log', 'w'), stderr=subprocess.STDOUT)
    r = analyze.stats(name); r.update(RA=RA, T=T, Vs=Vs); return r
jobs = []
for tag, T, Vs in [('T27', 27, 9), ('T0', 0, 9), ('T60', 60, 9), ('V12', 27, 12)]:
    for RA in range(2980, 3221, 10): jobs.append((f'd2_{tag}_{RA}', RA, T, Vs))
for RA in (2744, 4205.2, 4220): jobs.append((f'd2_K_{RA}', RA, 27, 9))
with ThreadPoolExecutor(8) as ex, open('out/lockd2.jsonl', 'w') as f:
    for r in ex.map(job, jobs): f.write(json.dumps(r) + '\n'); f.flush()
print('DONE')
