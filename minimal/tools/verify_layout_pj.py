"""Check the Path J breadboard: no hole used twice, and every part connects the nets of spice/mkcir_pj.py."""
import sys, os, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from layout_pj import S
def strip(h):
    if '@' in h: return {'+T': 'VCC', '-B': 'VEE', 'GT': '0', 'GB': '0'}[h.split('@')[0]]
    c, n = h[0], int(h[1:]); return f"{'L' if c in 'abcde' else 'R'}{n}"
# chip pins -> strips (TL074 pins 1-7 on L10..L16, 8-14 on R16..R10; TL072 pins 1-4 on L22..L25, 5-8 on R25..R22)
pin = {}
for k in range(1, 8): pin[('U1', k)] = f"L{9+k}"; pin[('U1', 15 - k)] = f"R{9+k}"
for k in range(1, 5): pin[('U5', k)] = f"L{21+k}"; pin[('U5', 9 - k)] = f"R{21+k}"
net = {}  # union-find on strips
par = {}
def f(a): par.setdefault(a, a); return a if par[a] == a else f(par[a])
def u(a, b): par[f(a)] = f(b)
used = collections.Counter()
parts = {}
for st, p, v, h1, h2, note in S:
    if not h2: continue
    used[h1] += '@' not in h1; used[h2] += '@' not in h2
    if 'wire' in v: u(strip(h1), strip(h2))
    else: parts[p] = (strip(h1), strip(h2))
dup = [h for h, c in used.items() if c > 1]
name = {'o1': pin[('U1', 1)], 'n1': pin[('U1', 2)], 'o2': pin[('U1', 7)], 'n2': pin[('U1', 6)], 'o3': pin[('U1', 8)], 'n3': pin[('U1', 9)],
        'n4': pin[('U1', 13)], 'o4': pin[('U1', 14)], 'u5': pin[('U5', 1)], 'n5': pin[('U5', 2)], 'VCC': 'VCC', 'VEE': 'VEE', '0': '0'}
gnd_pins = [('U1', 3), ('U1', 5), ('U1', 10), ('U1', 12), ('U5', 3), ('U5', 5)]
ok = not dup
for g in gnd_pins: ok &= f(pin[g]) == f('0') or print('GND pin not grounded', g)
ok &= f(pin[('U1', 4)]) == f('VCC') and f(pin[('U1', 11)]) == f('VEE') and f(pin[('U5', 8)]) == f('VCC') and f(pin[('U5', 4)]) == f('VEE')
ok &= f(pin[('U5', 6)]) == f(pin[('U5', 7)])
def N(s):
    for k, v in name.items():
        if f(v) == f(s): return k
    return 'r' if f(s) == f(parts['Rr'][1]) else f(s)
exp = {'C1': {'o1', 'n1'}, 'RA': {'o1', 'n1'}, 'Rc': {'n1', 'VCC'}, 'Rx': {'n1', 'o3'}, 'Rw': {'n1', 'o4'}, 'Rr': {'n1', 'r'}, 'R2': {'o1', 'n2'}, 'C2': {'n2', 'o2'},
       'R3': {'o2', 'n3'}, 'C3': {'n3', 'o3'}, 'R4': {'o2', 'n4'}, 'Rf': {'o4', 'n4'}, 'R5': {'o3', 'n5'}, 'Rf5': {'n5', 'r'}, 'Da': {'u5', 'n5'}, 'Db': {'r', 'u5'},
       'Cd1+': {'VCC', '0'}, 'Cd1-': {'VEE', '0'}, 'Cd2+': {'VCC', '0'}, 'Cd2-': {'VEE', '0'}}
for p, (a, b) in parts.items():
    got = {N(a), N(b)}
    if got != exp[p]: ok = False; print('MISMATCH', p, got, exp[p])
# diode polarity: Da anode u5 (hole1), Db anode r (hole1)
ok &= N(parts['Da'][0]) == 'u5' and N(parts['Db'][0]) == 'r'
print('duplicate holes:', dup); print('LAYOUT_PJ_OK' if ok else 'LAYOUT_PJ_FAIL'); sys.exit(0 if ok else 1)
