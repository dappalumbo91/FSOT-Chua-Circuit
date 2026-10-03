#!/usr/bin/env python3
"""Generate Falstad CircuitJS import text (File > Import From Text) + ?ctz= URLs for the FSOT Kennedy-Chua
node and 3-node ring, from the shared netlist in ../chua_netlist.py.
Element formats checked against pfalstad/circuitjs1 sources (see README / verify_falstad.py):
  r x1 y1 x2 y2 f R                       ResistorElm
  c x1 y1 x2 y2 f C voltdiff vinit        CapacitorElm (vinit = initial voltage on reset)
  l x1 y1 x2 y2 f L current               InductorElm
  a x1 y1 x2 y2 f maxOut minOut gbw v0 v1 gain   OpAmpElm (f=8: use dumped gain); posts: (-)=(x1,y1-16) (+)=(x1,y1+16) out=(x2,y2)
  g x1 y1 x2 y2 f sym                     GroundElm (post at x1,y1)
  w x1 y1 x2 y2 f                         WireElm
  207 x1 y1 x2 y2 4 NAME                  LabeledNodeElm (same NAME => same node; post at x1,y1)
  o eX speed 0 4290 scaleX scaleY 0 2 eY 0     Scope, new-style (FLAG_PLOTS|plot2d|XY|showV), X-Y of two elements' voltages
"""
import os, sys, json
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from chua_netlist import node_parts, ring_parts, rc_for_sigma, ESAT, PHI
from lzstring_uri import compressToEncodedURIComponent

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = "https://www.falstad.com/circuit/circuitjs.html"

class Doc:
    def __init__(self, dt):
        self.lines, self.idx, self.scopes = [], {}, []
        self.hdr = f"$ 1 {dt:g} 100 50 5 50 5e-11"
    def add(self, line, key=None):
        if key: self.idx[key] = len(self.lines)
        self.lines.append(line)
    def label(self, x, y, dx, dy, net):
        if net == "GND":
            self.add(f"g {x} {y} {x} {y+(16 if dy >= 0 else -16)} 0 0")
        else:
            self.add(f"207 {x} {y} {x+dx} {y+dy} 4 {net}")
    def text(self):
        return "\n".join([self.hdr] + self.lines + self.scopes) + "\n"

def fmt(v): return repr(float(v))

def place_node(D, parts, ox, oy, vinit_c1):
    """parts: node_parts list for one node. Two op-amps on the left, passives in a row to the right."""
    two = [p for p in parts if p[1] in "RCL"]
    u = [p for p in parts if p[1] == "TL082"][0]
    ref, _, _, pins = u
    # U1 = half A: (-)=pin2, (+)=pin3, out=pin1 ; U2 = half B: (-)=6, (+)=5, out=7
    for j, (half, inv, non, out) in enumerate([("A", "2", "3", "1"), ("B", "6", "5", "7")]):
        x, y = ox, oy + 48 + 112 * j
        D.add(f"a {x} {y} {x+64} {y} 8 {fmt(ESAT)} {fmt(-ESAT)} 1000000 0 0 100000", key=f"{ref}{half}")
        D.add(f"w {x} {y-16} {x-32} {y-16} 0"); D.label(x - 32, y - 16, -48, 0, pins[inv])
        D.add(f"w {x} {y+16} {x-32} {y+16} 0"); D.label(x - 32, y + 16, -48, 0, pins[non])
        D.add(f"w {x+64} {y} {x+96} {y} 0"); D.label(x + 96, y, 48, 0, pins[out])
    x0 = ox + 208
    for i, (r, kind, val, pn) in enumerate(two):
        x = x0 + 80 * (i % 6); y = oy + 160 * (i // 6)
        code = {"R": "r", "C": "c", "L": "l"}[kind]
        extra = ""
        if kind == "C":
            vi = vinit_c1 if r.startswith("C1") else 0.0
            extra = f" {fmt(val)} {fmt(vi)} {fmt(vi)}"
        elif kind == "L":
            extra = f" {fmt(val)} 0"
        else:
            extra = f" {fmt(val)}"
        D.add(f"{code} {x} {y+16} {x} {y+80} 0{extra}", key=r)
        D.label(x, y + 16, 0, -32, pn["1"])
        D.label(x, y + 80, 0, 32, pn["2"])

def single(dt=2.5e-7, r0=0.0):
    D = Doc(dt)
    place_node(D, node_parts("a", r0=r0), 96, 64, 0.1)
    D.scopes.append(f"o {D.idx['C1A']} 64 0 4290 1 0.4 0 2 {D.idx['C2A']} 0")
    return D

def ring(sigma, dt=2.5e-7, r0=0.0):
    D = Doc(dt)
    vin = {"a": 0.1, "b": 0.15, "c": 0.2}
    for j, x in enumerate("abc"):
        place_node(D, node_parts(x, r0=r0), 96, 64 + 400 * j, vin[x])
    rc = rc_for_sigma(sigma)
    for j, (a, b) in enumerate([("A", "B"), ("B", "C"), ("C", "A")]):
        x, y = 816, 80 + 160 * j
        D.add(f"r {x} {y} {x} {y+64} 0 {fmt(rc)}", key=f"Rc{a}{b}")
        D.label(x, y, 0, -32, f"{a}_V1"); D.label(x, y + 64, 0, 32, f"{b}_V1")
    D.scopes.append(f"o {D.idx['C1A']} 64 0 4290 1 0.4 0 2 {D.idx['C2A']} 0")   # double scroll of node A
    D.scopes.append(f"o {D.idx['C1A']} 64 0 4290 1 1 1 2 {D.idx['C1B']} 0")      # V_C1A vs V_C1B: diagonal line = lock
    return D

if __name__ == "__main__":
    out = {}
    R0 = 18.4400497592861384  # FSOT 2.1 Branch L inductor series resistance (ohm)
    for name, D in [("chua_single_node", single()), ("chua_ring_sigma_phi2", ring(PHI ** 2)), ("chua_ring_sigma_phi", ring(PHI)),
                    ("chua_single_node_r0_18p44", single(r0=R0)), ("chua_ring_sigma_phi2_r0_18p44", ring(PHI ** 2, r0=R0)),
                    ("chua_ring_sigma_phi_r0_18p44", ring(PHI, r0=R0))]:
        t = D.text()
        open(os.path.join(HERE, name + ".txt"), "w").write(t)
        url = BASE + "?ctz=" + compressToEncodedURIComponent(t)
        open(os.path.join(HERE, name + ".url"), "w").write(url + "\n")
        out[name] = dict(chars=len(t), url_len=len(url), url=url)
        print(name, len(t), len(url))
    json.dump(out, open(os.path.join(HERE, "urls.json"), "w"), indent=1)
