"""Falstad CircuitJS export of the FSOT minimal jerk circuit (same netlist as spice/mkcir.py). Prints ?ctz= URLs."""
import json, os
from lzstring_uri import compressToEncodedURIComponent
BASE = "https://www.falstad.com/circuit/circuitjs.html"
def build(RA):
    L = ["$ 1 1e-6 10 50 5 50 5e-11"]; idx = {}
    def add(s, k=None):
        if k: idx[k] = len(L) - 1
        L.append(s)
    def lab(x, y, dx, dy, n):
        add(f"g {x} {y} {x} {y+16} 0 0" if n == "GND" else f"207 {x} {y} {x+dx} {y+dy} 4 {n}")
    # op-amps: (-) input top, (+) bottom; rails +-9 V supply, output clamp ~ +-7.5 V
    for j, (m, o) in enumerate([("n1", "o1"), ("n2", "o2"), ("n3", "o3"), ("n4", "o4")]):
        x, y = 96, 64 + 96 * j
        add(f"a {x} {y} {x+64} {y} 8 7.5 -7.5 1000000 0 0 3000000", "U" + o)
        add(f"w {x} {y-16} {x-32} {y-16} 0"); lab(x - 32, y - 16, -48, 0, m)
        add(f"w {x} {y+16} {x-32} {y+16} 0"); lab(x - 32, y + 16, 0, 16, "GND")
        add(f"w {x+64} {y} {x+96} {y} 0"); lab(x + 96, y, 48, 0, o)
    parts = [("r", "RA", RA, "o1", "n1"), ("r", "Rw", 1800, "o4", "n1"), ("r", "Rx", 1800, "o3", "n1"), ("r", "Rc", 40200, "VCC", "n1"),
             ("c", "C1", 100e-9, "n1", "o1"), ("r", "R2", 1800, "o1", "n2"), ("c", "C2", 100e-9, "n2", "o2"), ("r", "R3", 1800, "o2", "n3"),
             ("c", "C3", 100e-9, "n3", "o3"), ("r", "R4", 1800, "o2", "n4"), ("r", "Rf", 1800, "o4", "n4"), ("d", "D1", None, "o3", "dn"), ("r", "Rd", 900, "dn", "n4")]
    for i, (k, ref, v, a, b) in enumerate(parts):
        x = 336 + 80 * (i % 7); y = 64 + 160 * (i // 7)
        if k == "r": add(f"r {x} {y+16} {x} {y+80} 0 {float(v)!r}", ref)
        elif k == "c": add(f"c {x} {y+16} {x} {y+80} 0 {float(v)!r} {(-0.5 if ref=='C3' else 0.0)!r} 0.001", ref)
        else: add(f"d {x} {y+16} {x} {y+80} 2 default", ref)
        lab(x, y + 16, 0, -32, a); lab(x, y + 80, 0, 32, b)
    add("R 720 400 720 352 0 0 40 9 0 0 0.5"); lab(720, 400, 0, 32, "VCC")  # +9 V rail feeding Rc
    L.append(f"o {idx['C3']} 64 0 4291 5 0.4 0 2 {idx['C2']} 0")  # X-Y: v(C3) ~ -x  vs  v(C2) ~ x'
    return "\n".join(L) + "\n"
if __name__ == "__main__":
    out = {}
    for name, RA in [("fsot_minimal_RA_phiR_2912", 2912.5), ("fsot_minimal_RA_3160_bench", 3160.0), ("fsot_minimal_RA_gammarel_4220_derived", 4220.0)]:
        t = build(RA); open(name + ".txt", "w").write(t); z = compressToEncodedURIComponent(t)
        out[name] = BASE + "?ctz=" + z; open(name + ".url", "w").write(out[name] + "\n")
    json.dump(out, open("urls.json", "w"), indent=1); print(json.dumps({k: len(v) for k, v in out.items()}))
