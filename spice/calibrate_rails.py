#!/usr/bin/env python3
"""Find the symmetric supply rail that makes the inner NIC op-amp (U2, loaded by R4/R5/R6) saturate at
|Esat| = 23/3 V, i.e. Bp1 = Esat*R6/(R5+R6) = 1 V, for each vendor macromodel (plan step 1)."""
import subprocess, re, sys, json, os
from chua_spice import opa_block, ESAT, HERE
def esat(level, vrail, vin):
    net = "\n".join(["* cal"] + opa_block(level) + [f"Vcc vcc 0 {vrail}", f"Vee vee 0 {-vrail}", f"Vin v1 0 {vin}",
        "XU2 v1 n2m vcc vee o2 OPA", "R4 v1 o2 22k", "R5 o2 n2m 22k", "R6 n2m 0 3.3k",
        "XU1 v1 n1m vcc vee o1 OPA", "R1 v1 o1 220", "R2 o1 n1m 220", "R3 n1m 0 2.2k",
        ".control", "op", "print v(o2) v(o1)", "quit", ".endc", ".end"]) + "\n"
    p = os.path.join(HERE, "out", "cal.cir"); open(p, "w").write(net)
    o = subprocess.run(["ngspice", "-b", p], cwd=HERE, capture_output=True, text=True).stdout
    return float(re.search(r"v\(o2\) = ([-\d.e+]+)", o).group(1)), float(re.search(r"v\(o1\) = ([-\d.e+]+)", o).group(1))
res = {}
for lvl in ["tl082", "ua741"]:
    lo, hi = 8.0, 12.0
    for _ in range(40):
        m = (lo + hi) / 2
        vp = esat(lvl, m, 3.0)[0]; vn = esat(lvl, m, -3.0)[0]
        if (vp - vn) / 2 < ESAT: lo = m
        else: hi = m
    vr = (lo + hi) / 2
    vp, vn = esat(lvl, vr, 3.0)[0], esat(lvl, vr, -3.0)[0]
    o1p = esat(lvl, vr, 7.5)[1]; o1n = esat(lvl, vr, -7.5)[1]
    at9 = esat(lvl, 9.0, 3.0)[0], esat(lvl, 9.0, -3.0)[0]
    res[lvl] = dict(rail_V=round(vr, 4), U2_Esat_plus=vp, U2_Esat_minus=vn, Bp1_plus=vp * 3.3 / 25.3, Bp1_minus=vn * 3.3 / 25.3,
                    U1_out_at_v1_pm7p5=[o1p, o1n], U2_Esat_at_pm9V_rails=list(at9), Bp1_at_pm9V=[at9[0] * 3.3 / 25.3, at9[1] * 3.3 / 25.3])
print(json.dumps(res, indent=1)); json.dump(res, open(os.path.join(HERE, "out", "rail_calibration.json"), "w"), indent=1)
