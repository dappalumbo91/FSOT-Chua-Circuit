"""CI check: build-free replay of the key locked facts with the C++ engine (expects ./mj built from src/mj.cpp)."""
import subprocess, sys, os, hashlib
H = os.path.dirname(os.path.abspath(__file__)); R = os.path.join(H, '..')
locks = {'LOCK_M1_2026-10-03_minimal_jerk.md': '078343de14f49cf8116b9fb9c53ad7642bd6712e7d767903fb8733bd31df40d4',
         'LOCK_M2_2026-10-03_bench_knob_and_opamp.md': '5a794149f2af44a1ee3ee16b110cb72f26a5bd9c535b684d175b2b1366113481',
         'LOCK_J_2026-10-03_branchJ_derived_A.md': '3683004b8c9d3a53325bc340d6d5eff0f37293ba245dcba0d4a960395617117f'}
for f, h in locks.items():
    assert hashlib.sha256(open(os.path.join(R, 'predictions', f), 'rb').read()).hexdigest() == h, f
out = subprocess.run([os.path.join(R, 'mj'), 'le', 'nic=4', 'T=3000'], capture_output=True, text=True, check=True).stdout.splitlines()[1:]
for l in out:
    c = l.split('\t'); l1, l2, s = float(c[2]), float(c[3]), float(c[5])
    assert l1 > 0.02 and abs(l2) < 0.01 and abs(s + 0.6180339887) < 1e-4, l
esc = subprocess.run([os.path.join(R, 'mj'), 'le', 'A=0.0393143', 'nic=1', 'T=500'], capture_output=True, text=True, check=True).stdout.splitlines()[1]
assert 'nan' in esc  # LOCK J1 falsified: unbounded
print('MINIMAL_CHECK_OK', len(out), 'ICs')
