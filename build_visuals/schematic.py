#!/usr/bin/env python3
"""Printable schematics (PNG/SVG/PDF) of one FSOT Kennedy-Chua node and the 3-node ring.
All values come from ../chua_netlist.py (single source of truth shared with SPICE/Falstad/breadboard)."""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import matplotlib; matplotlib.use("Agg")
import schemdraw, schemdraw.elements as elm
from chua_netlist import node_parts, rc_for_sigma, PHI
HERE = os.path.dirname(os.path.abspath(__file__))

def eng(v, unit):
    for f, p in [(1e3, "k"), (1, ""), (1e-3, "m"), (1e-6, "µ"), (1e-9, "n")]:
        if abs(v) >= f * 0.999: return f"{v / f:.6g} {p}{unit}"
    return f"{v:g} {unit}"

def draw_node(d, x, ox=0.0, oy=0.0, notes=True):
    """Draw node x with its V1 bus at x = ox+9. Returns (V1 point, V2 point)."""
    P = {p[0]: p for p in node_parts(x)}; X = x.upper()
    bus_x = ox + 9.0
    v1 = (bus_x, oy + 8.0)
    pins = [("U1", "A", "2", "3", "1", "R1", "R2", "R3"), ("U2", "B", "6", "5", "7", "R4", "R5", "R6")]
    for j, (u, half, inv, non, out, ra, rb, rc) in enumerate(pins):
        y0 = oy + 6.0 - 4.6 * j
        op = elm.Opamp(leads=True).right().at((ox + 3.0, y0)).anchor("in1"); d += op
        A = op.absanchors
        d += elm.Label().at((A["center"][0] - 0.35, A["center"][1])).label(f"{u}{X}\nTL082\n½{half}", fontsize=8)
        d += elm.Label().at(A["in1"]).label(f"{inv}", loc="left", fontsize=9, ofst=(0.05, 0.18), halign="right")
        d += elm.Label().at(A["in2"]).label(f"{non}", loc="left", fontsize=9, ofst=(0.05, -0.18), halign="right")
        d += elm.Label().at(A["out"]).label(f"{out}", fontsize=9, ofst=(0.25, 0.25))
        # Ra: out -> V1 bus (positive feedback)
        d += elm.Resistor().at((A["out"][0] + 0.6, A["out"][1])).to((bus_x, A["out"][1])).label(f"{ra}{X} {eng(P[ra + X][2], 'Ω')}", loc="bottom")
        d += elm.Line().at(A["out"]).to((A["out"][0] + 0.6, A["out"][1]))
        d += elm.Dot().at((bus_x, A["out"][1]))
        # + input: in2 -> left -> down -> right to bus
        low = A["in2"][1] - 0.9
        d += elm.Line().at(A["in2"]).to((A["in2"][0] - 0.6, A["in2"][1]))
        d += elm.Line().to((A["in2"][0] - 0.6, low))
        d += elm.Line().to((bus_x, low))
        d += elm.Dot().at((bus_x, low))
        # Rb: out -> up -> left (resistor) -> node N -> (-) input
        top = A["in1"][1] + 1.3
        N = (A["in1"][0] - 1.4, A["in1"][1])
        d += elm.Dot().at((A["out"][0] + 0.6, A["out"][1]))
        d += elm.Line().at((A["out"][0] + 0.6, A["out"][1])).to((A["out"][0] + 0.6, top))
        d += elm.Resistor().to((N[0], top)).label(f"{rb}{X} {eng(P[rb + X][2], 'Ω')}")
        d += elm.Line().to(N)
        d += elm.Line().at(N).to(A["in1"])
        d += elm.Dot().at(N)
        # Rc: N -> left -> GND
        d += elm.Resistor().at(N).left(2.2).label(f"{rc}{X}\n{eng(P[rc + X][2], 'Ω')}", loc="bottom")
        d += elm.Ground()
    # V1 bus
    ybot = oy + 6.0 - 4.6 - 1.25 - 0.9
    d += elm.Line().at((bus_x, ybot)).to(v1)
    d += elm.Dot().at(v1).label(f"{X}_V1 = V_C1", loc="top", fontsize=10)
    d += elm.Line().at(v1).right(1.6)
    c1p = (bus_x + 1.6, v1[1])
    d += elm.Capacitor().at(c1p).down(2.5).label(f"C1{X}\n{eng(P['C1' + X][2], 'F')}", loc="bottom"); d += elm.Ground()
    d += elm.Dot().at(c1p)
    d += elm.Resistor().at(c1p).right(3).label(f"R{X} {eng(P['R' + X][2], 'Ω')}", loc="bottom")
    v2 = (c1p[0] + 3, v1[1])
    d += elm.Dot().at(v2).label(f"{X}_V2 = V_C2", loc="top", fontsize=10)
    d += elm.Capacitor().at(v2).down(2.5).label(f"C2{X}\n{eng(P['C2' + X][2], 'F')}", loc="bottom"); d += elm.Ground()
    d += elm.Line().at(v2).right(2.2)
    d += elm.Inductor2(loops=4).down(2.5).label(f"L{X}\n{eng(P['L' + X][2], 'H')}\n(DCR = r0)", loc="bottom"); d += elm.Ground()
    if notes:
        d += elm.Label().at((ox + 11.3, oy + 3.6)).label("Test points (scope):\n TP1 = V_C1 (X / CH1)\n TP2 = V_C2 (Y / CH2)\n TP3 = U2 out pin 7 (rails ≈ ±7.67 V)", fontsize=9, halign="left", valign="top")
    return v1, v2

FOOT = ("TL082 (DIP-8, notch left, pin 1 bottom-left when viewed from top): 1 OUT A · 2 IN− A · 3 IN+ A · 4 V− · 5 IN+ B · 6 IN− B · 7 OUT B · 8 V+\n"
        "Supply: ±9.19 V (SPICE-calibrated with the TI TL082 macromodel so U2 saturates at Esat = 23/3 V → Bp1 = 1 V); 100 nF from pin 8 and pin 4 to GND.\n"
        "741 alternative: two 741s per node (U1, U2): pin 3 = +, pin 2 = −, pin 6 = out, pin 7 = V+, pin 4 = V−; rails ±9.66 V (SPICE-calibrated). Measure Esat and trim rails.")

def single():
    d = schemdraw.Drawing(fontsize=10, unit=2.0)
    d += elm.Label().at((-1, 10.2)).label("FSOT Kennedy–Chua node (BOM of FSOT-Chua-Circuit) — one TL082 per node", fontsize=13, halign="left")
    draw_node(d, "A")
    d += elm.Label().at((-1, -2.6)).label(FOOT, fontsize=8, halign="left", valign="top")
    return d

def ring(sigma=PHI ** 2):
    rc = rc_for_sigma(sigma)
    d = schemdraw.Drawing(fontsize=10, unit=2.0)
    d += elm.Label().at((-1, 10.6)).label(f"FSOT Kennedy–Chua 3-node ring: coupling Rc between V_C1 nets (A–B, B–C, C–A).  σ = αR/Rc;  σ = φ² → Rc = {rc:.2f} Ω (6.8 kΩ + 75 Ω)", fontsize=13, halign="left")
    pts = {}
    for j, x in enumerate("ABC"):
        pts[x] = draw_node(d, x, oy=-12.5 * j, notes=False)
        d += elm.Label().at((-1, 9.3 - 12.5 * j)).label(f"Node {x}", fontsize=12, halign="left")
    # coupling: taps from each V1 to its own vertical line; no unmarked crossings
    X = {"A": 33.0, "B": 29.0, "C": 25.0}
    ys = {x: pts[x][0][1] + 1.0 for x in "ABC"}
    yAB, yBC, yCA = ys["B"] - 3.5, ys["C"] - 3.5, ys["C"] - 7.0
    ends = {"A": yCA, "B": yBC, "C": yCA}
    for x in "ABC":
        v1 = pts[x][0]
        d += elm.Line().at(v1).to((v1[0], ys[x])); d += elm.Line().to((X[x], ys[x]))
        d += elm.Label().at(((v1[0] + X[x]) / 2, ys[x])).label(f"{x}_V1", fontsize=9, loc="top")
        d += elm.Line().at((X[x], ys[x])).to((X[x], ends[x]))
    for (a, b), y in [(("A", "B"), yAB), (("B", "C"), yBC), (("C", "A"), yCA)]:
        lo, hi = sorted([X[a], X[b]])
        d += elm.Dot().at((lo, y)); d += elm.Dot().at((hi, y))
        d += elm.Resistor().at((lo, y)).to((hi, y)).label(f"Rc{a}{b} = {rc:.2f} Ω", loc="top")
    cx = 22
    d += elm.Label().at((cx, -28.5)).label("Gate values:  open (σ=0) · 20 kΩ (σ=0.9) · 18 kΩ (σ=1) · 11 124.61 Ω (σ=φ; 10 k + 1.13 k E96) · 6 875.39 Ω (σ=φ²; 6.8 k + 75 Ω)\n"
                                             "Build each node exactly as the single-node schematic; one TL082 per node; common GND and ±9.19 V rails.", fontsize=9, halign="left")
    d += elm.Label().at((-1, -28.5)).label(FOOT, fontsize=8, halign="left", valign="top")
    return d

def save(d, base):
    for ext in ("png", "svg", "pdf"):
        if ext == "png": d.save(os.path.join(HERE, f"{base}.png"), dpi=180)
        else: d.save(os.path.join(HERE, f"{base}.{ext}"))

if __name__ == "__main__":
    save(single(), "schematic_single_node")
    save(ring(), "schematic_ring_sigma_phi2")
