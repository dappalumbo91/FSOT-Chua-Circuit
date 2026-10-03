"""Falstad CircuitJS export of the LOCK PJ circuit (same netlist as spice/mkcir_pj.py, E96 values). Prints a ?ctz= URL."""
import json
from lzstring_uri import compressToEncodedURIComponent
BASE = "https://www.falstad.com/circuit/circuitjs.html"
E96 = dict(RA=4220.0, RB=1960.0, RG=2430.0, RR=1210.0)
def build(v=E96):
    L = ["$ 1 1e-6 10 50 5 50 5e-11"]; idx = {}
    def add(s, k=None):
        if k: idx[k] = len(L) - 1
        L.append(s)
    def lab(x, y, dx, dy, n): add(f"g {x} {y} {x} {y+16} 0 0" if n == "GND" else f"207 {x} {y} {x+dx} {y+dy} 4 {n}")
    for j, (m, o) in enumerate([("n1", "o1"), ("n2", "o2"), ("n3", "o3"), ("n4", "o4"), ("n5", "u5")]):
        x, y = 96, 64 + 96 * j
        add(f"a {x} {y} {x+64} {y} 8 7.5 -7.5 1000000 0 0 3000000", "U" + o)
        add(f"w {x} {y-16} {x-32} {y-16} 0"); lab(x - 32, y - 16, -48, 0, m)
        add(f"w {x} {y+16} {x-32} {y+16} 0"); lab(x - 32, y + 16, 0, 16, "GND")
        add(f"w {x+64} {y} {x+96} {y} 0"); lab(x + 96, y, 48, 0, o)
    parts = [("r", "RA", v['RA'], "o1", "n1"), ("r", "Rw", v['RB'], "o4", "n1"), ("r", "Rx", v['RG'], "o3", "n1"), ("r", "Rr", v['RR'], "r", "n1"), ("r", "Rc", 40200, "VCC", "n1"),
             ("c", "C1", 100e-9, "n1", "o1"), ("r", "R2", 1800, "o1", "n2"), ("c", "C2", 100e-9, "n2", "o2"), ("r", "R3", 1800, "o2", "n3"),
             ("c", "C3", 100e-9, "n3", "o3"), ("r", "R4", 1800, "o2", "n4"), ("r", "Rf", 1800, "o4", "n4"),
             ("r", "R5", 1800, "o3", "n5"), ("r", "Rf5", 1800, "n5", "r"), ("d", "Da", None, "u5", "n5"), ("d", "Db", None, "r", "u5")]
    for i, (k, ref, val, a, b) in enumerate(parts):
        x = 336 + 80 * (i % 8); y = 64 + 160 * (i // 8)
        if k == "r": add(f"r {x} {y+16} {x} {y+80} 0 {float(val)!r}", ref)
        elif k == "c": add(f"c {x} {y+16} {x} {y+80} 0 {float(val)!r} {(-0.3 if ref=='C3' else 0.0)!r} 0.001", ref)
        else: add(f"d {x} {y+16} {x} {y+80} 2 default", ref)
        lab(x, y + 16, 0, -32, a); lab(x, y + 80, 0, 32, b)
    add("R 720 400 720 352 0 0 40 9 0 0 0.5"); lab(720, 400, 0, 32, "VCC")
    L.append(f"o {idx['C3']} 64 0 4291 5 0.4 0 2 {idx['C2']} 0")  # X-Y: v(C3) ~ -x vs v(C2) ~ x'
    return "\n".join(L) + "\n"
if __name__ == "__main__":
    t = build(); open("fsot_pj_theta_kg.txt", "w").write(t); u = BASE + "?ctz=" + compressToEncodedURIComponent(t)
    open("fsot_pj_theta_kg.url", "w").write(u + "\n"); d = json.load(open("urls.json")); d["fsot_pj_theta_kg"] = u; json.dump(d, open("urls.json", "w"), indent=1); print(len(u))
