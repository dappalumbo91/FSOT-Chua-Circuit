"""Verify the minimal-circuit Falstad exports: ctz round-trip with Falstad's own lz-string JS, and component values vs spice/mkcir.py."""
import os, sys, json, subprocess, re
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(HERE, "..", "..", "falstad")); sys.path.insert(1, "/workspace/FSOT-Chua-Circuit/falstad")
from verify_falstad import roundtrip
ok = True
for name, RA in [("fsot_minimal_RA_phiR_2912", 2912.5), ("fsot_minimal_RA_3160_bench", 3160.0), ("fsot_minimal_RA_gammarel_4220_derived", 4220.0)]:
    t = open(os.path.join(HERE, name + ".txt")).read(); u = open(os.path.join(HERE, name + ".url")).read()
    rt = roundtrip(t, u); vals = sorted(float(l.split()[6]) for l in t.splitlines() if l.startswith("r "))
    exp = sorted([RA, 1800, 1800, 40200, 1800, 1800, 1800, 1800, 900]); vm = vals == exp
    nd = sum(l.startswith("d ") for l in t.splitlines()); na = sum(l.startswith("a ") for l in t.splitlines())
    r = dict(roundtrip=rt, resistor_values_match=vm, diodes=nd, opamps=na); ok &= rt and vm and nd == 1 and na == 4; print(name, json.dumps(r))
print("ALL OK" if ok else "FAIL"); sys.exit(0 if ok else 1)
