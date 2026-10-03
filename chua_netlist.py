"""Single source of truth for the physical FSOT Kennedy-Chua node / 3-node ring (BOM of FSOT-Chua-Circuit).
Used by: falstad/gen_falstad.py, build_visuals/*.py, and checked against spice/models/chua_node.lib.
Op-amp: TL082 (DIP-8): 1 OUT_A, 2 IN-_A, 3 IN+_A, 4 V-, 5 IN+_B, 6 IN-_B, 7 OUT_B, 8 V+.
U1 = half A (outer NIC branch, R1/R2/R3), U2 = half B (inner NIC branch, R4/R5/R6)."""
PHI = (1 + 5 ** 0.5) / 2
R_CHUA, C1, C2, L = 1800.0, 10e-9, 100e-9, 22e-3
ALPHA = C2 / C1
ESAT = 23.0 / 3.0

def rc_for_sigma(s):
    return ALPHA * R_CHUA / s

def node_parts(x, k=1, r0=0.0):
    """Return list of (ref, kind, value, {pin: net}). x = node letter."""
    X = x.upper()
    lnet = f"{X}_L" if r0 > 0 else "GND"
    P = [
        (f"R{X}",  "R", R_CHUA,  {"1": f"{X}_V1", "2": f"{X}_V2"}),
        (f"C1{X}", "C", C1 * k,  {"1": f"{X}_V1", "2": "GND"}),
        (f"C2{X}", "C", C2 * k,  {"1": f"{X}_V2", "2": "GND"}),
        (f"L{X}",  "L", L * k,   {"1": f"{X}_V2", "2": lnet}),
        (f"R1{X}", "R", 220.0,   {"1": f"{X}_V1", "2": f"{X}_O1"}),
        (f"R2{X}", "R", 220.0,   {"1": f"{X}_O1", "2": f"{X}_N1"}),
        (f"R3{X}", "R", 2200.0,  {"1": f"{X}_N1", "2": "GND"}),
        (f"R4{X}", "R", 22000.0, {"1": f"{X}_V1", "2": f"{X}_O2"}),
        (f"R5{X}", "R", 22000.0, {"1": f"{X}_O2", "2": f"{X}_N2"}),
        (f"R6{X}", "R", 3300.0,  {"1": f"{X}_N2", "2": "GND"}),
        (f"U{X}",  "TL082", "TL082", {"1": f"{X}_O1", "2": f"{X}_N1", "3": f"{X}_V1", "4": "VEE",
                                       "5": f"{X}_V1", "6": f"{X}_N2", "7": f"{X}_O2", "8": "VCC"}),
    ]
    if r0 > 0:
        P.append((f"Rr0{X}", "R", r0, {"1": f"{X}_L", "2": "GND"}))
    return P

def ring_parts(rc, nodes="ABC", k=1, r0=0.0):
    P = []
    for x in nodes: P += node_parts(x, k, r0)
    if rc is not None:
        n = len(nodes)
        for i in range(n):
            a, b = nodes[i], nodes[(i + 1) % n]
            P.append((f"Rc{a}{b}", "R", rc, {"1": f"{a}_V1", "2": f"{b}_V1"}))
    return P

def nets(parts):
    d = {}
    for ref, kind, val, pins in parts:
        for p, n in pins.items(): d.setdefault(n, set()).add(f"{ref}.{p}")
    return d
