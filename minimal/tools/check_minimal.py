"""CI check: build-free replay of the key locked facts with the C++ engine (expects ./mj built from src/mj.cpp)."""
import subprocess, sys, os, hashlib, re
H = os.path.dirname(os.path.abspath(__file__)); R = os.path.join(H, '..')
locks = {'LOCK_M1_2026-10-03_minimal_jerk.md': '078343de14f49cf8116b9fb9c53ad7642bd6712e7d767903fb8733bd31df40d4',
         'LOCK_M2_2026-10-03_bench_knob_and_opamp.md': '5a794149f2af44a1ee3ee16b110cb72f26a5bd9c535b684d175b2b1366113481',
         'LOCK_J_2026-10-03_branchJ_derived_A.md': '3683004b8c9d3a53325bc340d6d5eff0f37293ba245dcba0d4a960395617117f',
         'LOCK_D1_2026-10-03_derived_knob_scales_branchD.md': '9a9bd4cb83db98e088ba7898ea3272cb5cf4886f5c4d2c709a652c1df0f02ad1',
         'LOCK_D2_2026-10-03_branchD_numbers.md': '3fe1b39aa51f12a9695e51f8d3299c1d11acc582ac2e86e47d8f1a34efd3d55c',
         'LOCK_DJ_2026-10-03_fsot_junction.md': 'f80d7d0d26b14cd584b19c12ead3de7d51a20bdf4e292f2c0673a05420db4467',
         'LOCK_T_2026-10-03_fsot_topology.md': '61f259b203a56124d58b9df72323b6804f6ee7c9f332d8e12e1adfcf52ffccf7',
         'LOCK_T2_2026-10-03_gammarel_small_basin.md': '724228ea9cc29937f176c4150ba974667cd0a12098ae86a36a9090571526de61'}
for f, h in locks.items():
    assert hashlib.sha256(open(os.path.join(R, 'predictions', f), 'rb').read()).hexdigest() == h, f
out = subprocess.run([os.path.join(R, 'mj'), 'le', 'nic=4', 'T=3000'], capture_output=True, text=True, check=True).stdout.splitlines()[1:]
for l in out:
    c = l.split('\t'); l1, l2, s = float(c[2]), float(c[3]), float(c[5])
    assert l1 > 0.02 and abs(l2) < 0.01 and abs(s + 0.6180339887) < 1e-4, l
esc = subprocess.run([os.path.join(R, 'mj'), 'le', 'A=0.0393143', 'nic=1', 'T=500'], capture_output=True, text=True, check=True).stdout.splitlines()[1]
assert 'nan' in esc  # LOCK J1 falsified: unbounded
print('MINIMAL_CHECK_OK', len(out), 'ICs')

# LOCK D2: bd.cpp unchanged since lock, and the Branch D replay (3150 chaotic, 4205 = R/gamma_rel rail latch)
import subprocess
bds = re.search(r"bd.cpp sha256: ([0-9a-f]{64})", open(os.path.join(R, 'predictions', 'LOCK_D2_2026-10-03_branchD_numbers.md')).read()).group(1)
assert hashlib.sha256(open(os.path.join(R, 'src', 'bd.cpp'), 'rb').read()).hexdigest() == bds, 'bd.cpp changed after LOCK D2'
if os.path.exists(os.path.join(R, 'bd')):
    o = subprocess.run([os.path.join(R, 'bd'), 'RA=3150:3150:1', 'nic=1'], capture_output=True, text=True).stdout.splitlines()[-1].split('\t')
    assert float(o[3]) > 0.005 and o[7].strip() == '0', o
    o = subprocess.run([os.path.join(R, 'bd'), 'RA=4205.2:4205.2:1', 'nic=1'], capture_output=True, text=True).stdout.splitlines()[-1].split('\t')
    assert o[7].strip() == '1', o
    print('Branch D replay OK')

# datasheets referenced by LOCK DJ (checksums)
for f, h in (('1n4148.pdf', 'aefe85400a427ed886a4e1c88205ceabb9f9b38044b29c6acee4bb00146a44b7'), ('ds30086.pdf', '39c16a6888bdab22418e93e17182174aad763a66957a4632e70c944194e3fc08')):
    q = os.path.join(R, 'datasheets', f)
    if os.path.exists(q): assert hashlib.sha256(open(q, 'rb').read()).hexdigest() == h, f
# LOCK T: the winner S-a is unbounded (falsified) in the C++ engine
if os.path.exists(os.path.join(R, 'topo', 'tj')):
    o = subprocess.run([os.path.join(R, 'topo', 'tj'), '0.42804344605980688', '0', '1', '1', 'sgn', '0', '4', '1000'], capture_output=True, text=True).stdout.split('\n')
    assert all(l.split('\t')[6] == '0' for l in o if l.strip()), o
    print('LOCK T replay OK (S-a unbounded)')
