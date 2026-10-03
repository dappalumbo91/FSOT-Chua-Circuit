#!/usr/bin/env python3
"""Write hand-runnable, parameterised netlists to netlists/ (run: cd netlists && ngspice <file>)."""
import os, json
HERE = os.path.dirname(os.path.abspath(__file__))
RAIL = json.load(open(os.path.join(HERE, "out", "rail_calibration.json")))
OPA = {"ideal": ("../models/opamp_beh.lib", "OPAMP_GBW GBW=1e9", 9.0),
       "gbw100M": ("../models/opamp_beh.lib", "OPAMP_GBW GBW=100e6", 9.0),
       "tl082": ("../models/vendor/ti_sloj070/TL082.301", "TL082", RAIL["tl082"]["rail_V"]),
       "ua741": ("../models/vendor/ua741.mod", "UA741", RAIL["ua741"]["rail_V"])}
def write(name, lvl, k, ring):
    inc, sub, vr = OPA[lvl]
    tau = 180e-6 * k
    L = [f"* FSOT Kennedy-Chua {'3-node ring' if ring else 'single node'}; op-amp={lvl}; time scale k={k} (tau = {tau*1e6:g} us)",
         "* Parameters: k (C1,C2,L x k), r0 = inductor series resistance [ohm], Rc = coupling [ohm] (ring only).",
         "* sigma = alpha*R/Rc = 18000/Rc:  20k->0.9, 18k->1, 11124.61->phi, 6875.39->phi^2.",
         f".param k={k} r0=0" + (" Rc=6875.390" if ring else ""),
         ".include ../models/chua_node.lib", f".include {inc}",
         ".subckt OPA inp inn vcc vee out", f"X inp inn vcc vee out {sub}", ".ends OPA",
         f"Vcc vcc 0 {vr}", f"Vee vee 0 {-vr}",
         "Xa a1 a2 vcc vee CHUA_NODE k={k} r0={r0}"]
    if ring:
        L += ["Xb b1 b2 vcc vee CHUA_NODE k={k} r0={r0}", "Xc c1 c2 vcc vee CHUA_NODE k={k} r0={r0}",
              "Rcab a1 b1 {Rc}", "Rcbc b1 c1 {Rc}", "Rcca c1 a1 {Rc}",
              ".ic v(a1)=0.1 v(a2)=0 v(b1)=0.15 v(b2)=0 v(c1)=0.2 v(c2)=0"]
    else:
        L += [".ic v(a1)=0.1 v(a2)=0"]
    T = (2000 if ring else 500) * tau
    L += [".options method=gear reltol=1e-4 abstol=1e-10 vntol=1e-7 itl4=100",
          f".tran {tau/100:g} {T:g} 0 {tau*0.002:g} uic", ".control", "run",
          "plot v(a1) vs v(a2) title 'double scroll: V(C1) vs V(C2)'" if not ring else "plot v(a1) v(b1) v(c1) xlimit " + f"{0.9*T:g} {T:g}",
          "meas tran vmax MAX v(a1) from=" + f"{0.6*T:g}", "meas tran vmin MIN v(a1) from=" + f"{0.6*T:g}",
          ".endc", ".end"]
    open(os.path.join(HERE, "netlists", name), "w").write("\n".join(L) + "\n")
for lvl in OPA:
    for k in (1, 10):
        write(f"chua_single_{lvl}_x{k}.cir", lvl, k, False)
        write(f"chua_ring_{lvl}_x{k}.cir", lvl, k, True)
print(sorted(os.listdir(os.path.join(HERE, "netlists")))[:20])
