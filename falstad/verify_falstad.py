#!/usr/bin/env python3
"""Validate generated CircuitJS text: (1) every line uses an element code/format from pfalstad/circuitjs1
(r,c,l,a,g,w,207,o,$), with the token counts the constructors read; (2) rebuild connectivity exactly like
CircuitJS (posts at identical coordinates join; wires join their two posts; LabeledNodes with equal text join;
ground posts are node 0); (3) compare with the shared netlist (chua_netlist.py); (4) check scopes reference
C1A (X) / C2A (Y); (5) round-trip the ?ctz= string through Falstad's own war/lz-string.min.js (node)."""
import os, sys, subprocess, json
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from chua_netlist import node_parts, ring_parts, rc_for_sigma, nets, PHI
HERE = os.path.dirname(os.path.abspath(__file__))
LZJS = "/workspace/circuitjs1_src/war/lz-string.min.js"
NTOK = {"r": 7, "c": 9, "l": 8, "a": 12, "g": 7, "w": 6, "207": 7}

class UF:
    def __init__(s): s.p = {}
    def f(s, a):
        s.p.setdefault(a, a)
        while s.p[a] != a: s.p[a] = s.p[s.p[a]]; a = s.p[a]
        return a
    def u(s, a, b): s.p[s.f(a)] = s.f(b)

def parse(text):
    L = text.strip().split("\n"); assert L[0].startswith("$ ") and len(L[0].split()) == 8, L[0]
    elms, scopes = [], []
    for ln in L[1:]:
        t = ln.split()
        if t[0] == "o": scopes.append(t); continue
        assert t[0] in NTOK, f"unknown code {t[0]}"
        assert len(t) == NTOK[t[0]], f"token count {len(t)} for {ln}"
        elms.append(t)
    return elms, scopes

def connectivity(elms):
    uf = UF(); posts = []
    for i, t in enumerate(elms):
        x1, y1, x2, y2 = map(int, t[1:5])
        if t[0] == "a":
            assert y1 == y2 and x2 > x1 and int(t[5]) & 1 == 0
            P = {"inv": (x1, y1 - 16), "non": (x1, y1 + 16), "out": (x2, y2)}
        elif t[0] in ("g", "207"): P = {"p": (x1, y1)}
        else: P = {"1": (x1, y1), "2": (x2, y2)}
        for k, xy in P.items(): uf.f(("pt",) + xy)
        if t[0] == "w": uf.u(("pt", x1, y1), ("pt", x2, y2))
        if t[0] == "g": uf.u(("pt", x1, y1), ("NET", "GND"))
        if t[0] == "207": uf.u(("pt", x1, y1), ("NET", t[6]))
        posts.append(P)
    return uf, posts

def check(name, text, parts, opamp_keys):
    elms, scopes = parse(text)
    uf, posts = connectivity(elms)
    # map Falstad elements to parts in generation order (passives keyed by order; op-amps by order)
    want = nets(parts)
    got = {}
    pas = [p for p in parts if p[1] in "RCL"]
    ops = [p for p in parts if p[1] == "TL082"]
    ei = [i for i, t in enumerate(elms) if t[0] in "rcl"]
    ai = [i for i, t in enumerate(elms) if t[0] == "a"]
    assert len(ai) == 2 * len(ops)
    # passives: generator emits node passives first per node, then ring Rc after all nodes
    order = []
    for x in sorted({p[0][-1] for p in ops}):
        order += [p for p in pas if p[0][-1] == x and not p[0].startswith("Rc")]
    order += [p for p in pas if p[0].startswith("Rc")]
    vals_ok = True
    for (ref, kind, val, pins), i in zip(order, ei):
        t = elms[i]
        assert {"R": "r", "C": "c", "L": "l"}[kind] == t[0], (ref, t)
        vals_ok &= abs(float(t[6]) - val) <= 1e-9 * abs(val)
        for pn, xy in posts[i].items(): got.setdefault(("pin", ref, pn), uf.f(("pt",) + xy))
    for j, (ref, kind, val, pins) in enumerate(ops):
        for half, (inv, non, out) in zip((0, 1), (("2", "3", "1"), ("6", "5", "7"))):
            P = posts[ai[2 * j + half]]
            got[("pin", ref, inv)] = uf.f(("pt",) + P["inv"]); got[("pin", ref, non)] = uf.f(("pt",) + P["non"]); got[("pin", ref, out)] = uf.f(("pt",) + P["out"])
            assert abs(float(elms[ai[2 * j + half]][6]) - 23 / 3) < 1e-12 and abs(float(elms[ai[2 * j + half]][7]) + 23 / 3) < 1e-12
    # build falstad partition restricted to modeled pins (power pins 4/8 are implicit in Falstad's ideal op-amp)
    fal = {}
    for (_, ref, pn), root in got.items(): fal.setdefault(root, set()).add(f"{ref}.{pn}")
    W = [frozenset(v - {p for p in v if p.endswith(('.4', '.8')) and p.split('.')[0].startswith('U')}) for v in want.values()]
    W = {w for w in W if w}
    F = {frozenset(v) for v in fal.values()}
    ok = W == F
    # scope check: X = C1A, Y = C2A (first scope)
    sc = scopes[0]; ex, ey = int(sc[1]), int(sc[9])
    sc_ok = elms[ex][0] == "c" and float(elms[ex][6]) == 1e-08 and elms[ey][0] == "c" and float(elms[ey][6]) == 1e-07
    sc_ok &= uf.f(("pt",) + posts[ex]["2"]) == uf.f(("NET", "GND")) and uf.f(("pt",) + posts[ey]["2"]) == uf.f(("NET", "GND"))
    return dict(nets_match=ok, values_match=bool(vals_ok), scope_xy_C1A_vs_C2A=bool(sc_ok), n_elements=len(elms), n_nets=len(F),
                diff=None if ok else [sorted(x) for x in (W ^ F)])

def roundtrip(text, url):
    js = ("const fs=require('fs');eval(fs.readFileSync('%s','utf8')+';global.LZString=LZString;');"
          "process.stdout.write(LZString.decompressFromEncodedURIComponent(process.argv[1]));" % LZJS)
    ctz = url.split("?ctz=")[1].strip()
    return subprocess.run(["node", "-e", js, ctz], capture_output=True, text=True).stdout == text

if __name__ == "__main__":
    res = {}
    for name, parts in [("chua_single_node", node_parts("a")),
                        ("chua_ring_sigma_phi2", ring_parts(rc_for_sigma(PHI ** 2))),
                        ("chua_ring_sigma_phi", ring_parts(rc_for_sigma(PHI))),
                        ("chua_single_node_r0_18p44", node_parts("a", r0=18.4400497592861384)),
                        ("chua_ring_sigma_phi2_r0_18p44", ring_parts(rc_for_sigma(PHI ** 2), r0=18.4400497592861384)),
                        ("chua_ring_sigma_phi_r0_18p44", ring_parts(rc_for_sigma(PHI), r0=18.4400497592861384))]:
        text = open(os.path.join(HERE, name + ".txt")).read(); url = open(os.path.join(HERE, name + ".url")).read()
        r = check(name, text, parts, None); r["ctz_roundtrip_with_falstad_lzstring"] = roundtrip(text, url)
        res[name] = r; print(name, json.dumps(r))
    json.dump(res, open(os.path.join(HERE, "verify_report.json"), "w"), indent=1)
    assert all(r["nets_match"] and r["values_match"] and r["scope_xy_C1A_vs_C2A"] and r["ctz_roundtrip_with_falstad_lzstring"] for r in res.values())
    print("ALL OK")
