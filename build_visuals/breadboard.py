#!/usr/bin/env python3
"""830-point breadboard layout for the FSOT Kennedy-Chua node / 3-node ring, generated from ../chua_netlist.py,
then verified: the layout's hole-level connectivity (strips, rails, jumpers) is rebuilt independently and its net
partition must equal the netlist's (plus the two supply-decoupling caps per chip).

Board model (standard 830-point): rows 1..63; each row has strip a-e (bottom) and strip f-j (top), centre gap between e/f.
Rails: top outer = +V (red), top inner = GND, bottom inner = GND, bottom outer = -V (blue). Rail holes: 10 groups of 5,
at rows 3-7, 9-13, ..., 57-61 (no rail hole at rows 1, 2, 8, 14, ..., 62, 63)."""
import os, sys, json, math
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from chua_netlist import node_parts, ring_parts, rc_for_sigma, nets, PHI
HERE = os.path.dirname(os.path.abspath(__file__))

RAIL_ROWS = [r for g in range(10) for r in range(3 + 6 * g, 8 + 6 * g)]
RAILS = {"TOP+": "VCC", "TOPG": "GND", "BOTG": "GND", "BOT-": "VEE"}
BOT, TOP = "bot", "top"
LET = {BOT: "edcba", TOP: "fghij"}   # fill order: nearest the gap first

class Board:
    def __init__(self):
        self.strip_used = {}      # (row, half) -> list of letters used
        self.rail_used = {k: set() for k in RAILS}
        self.items = []           # dicts: ref, kind, value, leads [(pin, hole)], color, note
    def hole(self, row, half, letter=None):
        used = self.strip_used.setdefault((row, half), [])
        if letter is None:
            letter = next(l for l in LET[half] if l not in used)
        assert letter not in used, f"hole {letter}{row} already used"
        assert len(used) < 5
        used.append(letter)
        return ("S", row, half, letter)
    def rail(self, rail, row):
        cand = sorted(RAIL_ROWS, key=lambda r: (abs(r - row), r))
        r = next(r for r in cand if r not in self.rail_used[rail])
        self.rail_used[rail].add(r)
        return ("R", rail, r)
    def add(self, ref, kind, value, leads, color=None, note=""):
        self.items.append(dict(ref=ref, kind=kind, value=value, leads=leads, color=color, note=note))

def hname(h):
    if h[0] == "S": return f"{h[3]}{h[1]}"
    return {"TOP+": "top +V rail (red)", "TOPG": "top GND rail", "BOTG": "bottom GND rail", "BOT-": "bottom −V rail (blue)"}[h[1]] + f" @ row {h[2]}"

def place_node(B, x, b, parts):
    """Chip pin 1 at row b (bottom strip, hole e). Returns dict of named strips for later use."""
    P = {p[0]: p for p in parts}; X = x.upper()
    # TL082: pins 1-4 at e[b..b+3], pins 8-5 at f[b..b+3] (notch toward row b-1 / left)
    chip = [("1", b, BOT), ("2", b + 1, BOT), ("3", b + 2, BOT), ("4", b + 3, BOT),
            ("8", b, TOP), ("7", b + 1, TOP), ("6", b + 2, TOP), ("5", b + 3, TOP)]
    B.add(f"U{X}", "TL082", "TL082", [(p, B.hole(r, h, "e" if h == BOT else "f")) for p, r, h in chip],
          note="notch/dot toward the left (lower row numbers); pin 1 bottom-left")
    S = dict(O1=(b, BOT), N1=(b + 1, BOT), V1a=(b + 2, BOT), VEE=(b + 3, BOT),
             VCC=(b, TOP), O2=(b + 1, TOP), N2=(b + 2, TOP), V1b=(b + 3, TOP),
             HUB=(b + 5, BOT), V2=(b + 8, BOT), LEND=(b + 10, BOT))
    h = lambda k: B.hole(*S[k])
    # power
    B.add(f"Jvcc{X}", "wire", None, [("1", h("VCC")), ("2", B.rail("TOP+", b))], color="red")
    B.add(f"Jvee{X}", "wire", None, [("1", h("VEE")), ("2", B.rail("BOT-", b + 3))], color="blue")
    B.add(f"Cd+{X}", "Cdec", 100e-9, [("1", h("VCC")), ("2", B.rail("TOPG", b + 1))], note="decoupling, pin 8 to GND")
    B.add(f"Cd-{X}", "Cdec", 100e-9, [("1", h("VEE")), ("2", B.rail("BOTG", b + 4))], note="decoupling, pin 4 to GND")
    # outer NIC branch (bottom)
    B.add(f"R2{X}", "R", P[f"R2{X}"][2], [("1", h("O1")), ("2", h("N1"))], note="upright (hairpin) mount")
    B.add(f"R1{X}", "R", P[f"R1{X}"][2], [("1", h("V1a")), ("2", h("O1"))], note="upright (hairpin) mount")
    B.add(f"R3{X}", "R", P[f"R3{X}"][2], [("1", h("N1")), ("2", B.rail("BOTG", b + 1))])
    # inner NIC branch (top)
    B.add(f"R5{X}", "R", P[f"R5{X}"][2], [("1", h("O2")), ("2", h("N2"))], note="upright (hairpin) mount")
    B.add(f"R4{X}", "R", P[f"R4{X}"][2], [("1", h("V1b")), ("2", h("O2"))], note="upright (hairpin) mount")
    B.add(f"R6{X}", "R", P[f"R6{X}"][2], [("1", h("N2")), ("2", B.rail("TOPG", b + 2))])
    # V1 interconnect: pin-5 strip -> pin-3 strip (across the gap), pin-3 strip -> hub
    B.add(f"Jv1x{X}", "wire", None, [("1", h("V1b")), ("2", h("V1a"))], color="yellow")
    B.add(f"Jv1h{X}", "wire", None, [("1", h("V1a")), ("2", h("HUB"))], color="yellow")
    # Chua core
    B.add(f"C1{X}", "C", P[f"C1{X}"][2], [("1", h("HUB")), ("2", B.rail("BOTG", b + 5))])
    B.add(f"R{X}", "R", P[f"R{X}"][2], [("1", h("HUB")), ("2", h("V2"))])
    B.add(f"C2{X}", "C", P[f"C2{X}"][2], [("1", h("V2")), ("2", B.rail("BOTG", b + 8))])
    B.add(f"L{X}", "L", P[f"L{X}"][2], [("1", h("V2")), ("2", h("LEND"))], note="22 mH; measure its DCR (= r0)")
    B.add(f"Jl{X}", "wire", None, [("1", h("LEND")), ("2", B.rail("BOTG", b + 10))], color="black",
          note="replace with r0 resistor to set γ = β·r0/R (FSOT preregistration)")
    return S

def build(nodes="A", rc_pair=None):
    B = Board(); strips = {}
    bases = {"A": 3, "B": 17, "C": 31}
    parts = ring_parts(None, nodes) if len(nodes) > 1 else node_parts("a")
    for x in nodes:
        strips[x] = place_node(B, x, bases[x], [p for p in parts if p[0].endswith(x)])
    # test points (reserve one free hole per test strip so the probe always has a home)
    tps = []
    for x in nodes:
        S = strips[x]
        tps += [(f"TP1{x}", f"{x}_V1 = V_C1 (scope X / CH1)", B.hole(*S["V1a"])),
                (f"TP2{x}", f"{x}_V2 = V_C2 (scope Y / CH2)", B.hole(*S["V2"])),
                (f"TP3{x}", f"U{x} pin 7 = inner op-amp out (should rail at ±7.67 V)", B.hole(*S["O2"]))]
    if len(nodes) == 3:
        # coupling area: top strips A=45, AB-mid=49, B=53, BC-mid=57, C=61; bottom A'=45, CA-mid=53, C'=61
        CP = {"A": (45, TOP), "ABm": (49, TOP), "B": (53, TOP), "BCm": (57, TOP), "C": (61, TOP),
              "A'": (45, BOT), "CAm": (53, BOT), "C'": (61, BOT)}
        col = {"A": "green", "B": "orange", "C": "purple"}
        for x in "ABC":
            B.add(f"Jc{x}", "wire", None, [("1", B.hole(*strips[x]["HUB"])), ("2", B.hole(*CP[x]))], color=col[x], note=f"{x}_V1 to coupling area")
        B.add("JcA'", "wire", None, [("1", B.hole(*CP["A"])), ("2", B.hole(*CP["A'"]))], color="green")
        B.add("JcC'", "wire", None, [("1", B.hole(*CP["C"])), ("2", B.hole(*CP["C'"]))], color="purple")
        (r1, r2) = rc_pair
        for name, a, m, bb in [("RcAB", "A", "ABm", "B"), ("RcBC", "B", "BCm", "C"), ("RcCA", "C'", "CAm", "A'")]:
            B.add(f"{name}_1", "R", r1, [("1", B.hole(*CP[a])), ("2", B.hole(*CP[m]))], note=f"{name} part 1")
            if r2 > 0:
                B.add(f"{name}_2", "R", r2, [("1", B.hole(*CP[m])), ("2", B.hole(*CP[bb]))], note=f"{name} part 2")
            else:
                B.add(f"{name}_2", "wire", None, [("1", B.hole(*CP[m])), ("2", B.hole(*CP[bb]))], color="white", note=f"{name}: single resistor, jumper")
    # GND rails tied together; +V/-V/GND supply entry at the left end
    B.add("Jgnd", "wire", None, [("1", B.rail("TOPG", 61)), ("2", B.rail("BOTG", 61))], color="black", note="ties top and bottom GND rails")
    return B, parts, tps

def verify(B, parts, nodes):
    """Independent connectivity rebuild -> compare to netlist nets (+ decoupling caps)."""
    par = {}
    def f(a):
        par.setdefault(a, a)
        while par[a] != a: par[a] = par[par[a]]; a = par[a]
        return a
    def u(a, b): par[f(a)] = f(b)
    def node_of(h):
        return ("strip", h[1], h[2]) if h[0] == "S" else ("rail", h[1])
    for k, v in RAILS.items(): u(("rail", k), ("NET", v))
    holes = set()
    for it in B.items:
        for _, h in it["leads"]:
            assert h not in holes, f"hole reused: {h}"; holes.add(h)
            if h[0] == "R": assert h[2] in RAIL_ROWS
            else: assert 1 <= h[1] <= 63 and h[3] in "abcdefghij"
        if it["kind"] == "wire":
            u(node_of(it["leads"][0][1]), node_of(it["leads"][1][1]))
    for (row, half), used in B.strip_used.items(): assert len(used) <= 5
    got = {}
    for it in B.items:
        if it["kind"] == "wire": continue
        ref = it["ref"]
        for pin, h in it["leads"]:
            got.setdefault(f(node_of(h)), set()).add(f"{ref}.{pin}")
    # expected: netlist + decoupling caps; series Rc halves map onto one netlist Rc
    exp = nets(parts if len(nodes) == 1 else [p for p in parts if not p[0].startswith("Rc")])
    for x in nodes:
        exp.setdefault("VCC", set()).add(f"Cd+{x.upper()}.1"); exp.setdefault("GND", set()).update({f"Cd+{x}.2", f"Cd-{x}.2"})
        exp.setdefault("VEE", set()).add(f"Cd-{x}.1")
    if len(nodes) == 3:
        for name, a, b in [("RcAB", "A", "B"), ("RcBC", "B", "C"), ("RcCA", "C", "A")]:
            exp[f"{a}_V1"].add(f"{name}_1.1"); exp.setdefault(f"{name}_mid", set()).update({f"{name}_1.2", f"{name}_2.1"} if any(i["ref"] == f"{name}_2" and i["kind"] == "R" for i in B.items) else {f"{name}_1.2"})
            if any(i["ref"] == f"{name}_2" and i["kind"] == "R" for i in B.items): exp[f"{b}_V1"].add(f"{name}_2.2")
    # RcCA is placed C'->A' (reverse orientation), fix expected pins accordingly
    if len(nodes) == 3:
        exp["C_V1"].discard("RcCA_2.2"); exp["A_V1"].discard("RcCA_1.1")
        exp["C_V1"].add("RcCA_1.1"); exp["A_V1"].add("RcCA_2.2")
    E = {frozenset(v) for v in exp.values() if v}
    G = {frozenset(v) for v in got.values()}
    return dict(nets_match=E == G, n_nets=len(G), n_items=len(B.items), holes_used=len(holes),
                diff=None if E == G else [sorted(s) for s in (E ^ G)])
