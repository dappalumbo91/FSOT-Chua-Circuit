#!/usr/bin/env python3
"""Python cross-check for Branch L: evaluates the same formulas with the authority
vendor/fsot_compute.py (pin AEB2AD, mpmath dps 50) and writes golden/branch_l_AEB2AD.tsv."""
import hashlib, importlib.util, sys
from pathlib import Path
AUTH = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parents[2] / "vendor" / "fsot_compute.py"
OUT = Path(sys.argv[2] if len(sys.argv) > 2 else Path(__file__).resolve().parents[1] / "golden" / "branch_l_AEB2AD.tsv")
sha = hashlib.sha256(AUTH.read_bytes()).hexdigest().upper()
assert sha.startswith("AEB2AD"), sha
spec = importlib.util.spec_from_file_location("fc", AUTH); fc = importlib.util.module_from_spec(spec); sys.modules["fc"] = fc; spec.loader.exec_module(fc)
from mpmath import mp, mpf, sqrt, fabs
mp.dps = 50
def S(name):
    return fc.domain_scalar(name)  # same path as FSOT-2.1-Cpp tools/dump_golden.py (mp, 169 bit)
R, L, C2 = mpf(1800), mpf("0.022"), mpf("1e-7")
rows = []
for dom in ("Electromagnetism", "Materials_Science"):
    eps = fabs(S(dom)) * fc.ALPHA
    k = sqrt((1 + eps) ** 2 - 1)
    beta = R * R * C2 / L
    rows += [(dom, "S", S(dom)), (dom, "eps", eps), (dom, "k", k), (dom, "Q_L", 1 / k),
             (dom, "r0_ohm", k * sqrt(L / C2)), (dom, "gamma", k * sqrt(beta))]
R1 = R2 = mpf(220); R3 = mpf(2200); R4 = R5 = mpf(22000); R6 = mpf(3300)
rows += [("NIC", "Ga", -R2 / (R1 * R3) - R5 / (R4 * R6)), ("NIC", "Gb", -R2 / (R1 * R3) + 1 / R4), ("NIC", "Gc", 1 / R1 + 1 / R4)]
with OUT.open("w") as f:
    f.write(f"# Branch L golden, authority sha256 {sha}, mpmath dps 50\n")
    for d, n, v in rows:
        f.write(f"{d}\t{n}\t{mp.nstr(v, 45)}\n")
print(OUT.read_text())
