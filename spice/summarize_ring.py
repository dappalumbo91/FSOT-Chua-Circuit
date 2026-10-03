#!/usr/bin/env python3
"""Summarize ring sweep JSONL files -> table + sigma_c (smallest grid sigma above which every sigma/seed locks)."""
import json, sys, collections, os
from chua_spice import PHI
def load(p):
    rows = list({(r["sigma"], r["seed"]): r for r in (json.loads(l) for l in open(p))}.values())
    by = collections.defaultdict(list)
    for r in rows: by[r["sigma"]].append(r)
    return dict(sorted(by.items()))
def sigma_c(by):
    sig = [s for s in by if s > 0]
    ok = {s: all(r["lock"] for r in by[s]) for s in sig}
    sc = None
    for s in sorted(sig, reverse=True):
        if ok[s]: sc = s
        else: break
    below = max([s for s in sig if sc is not None and s < sc], default=None)
    return sc, below
out = {}
for p in sys.argv[1:]:
    by = load(p); sc, below = sigma_c(by)
    print(f"\n== {os.path.basename(p)}   sigma_c in ({below}, {sc}]")
    print("sigma     Rc[ohm]    locks  mean_mad/amp  max|V1|tail  trit_agree  escape_tau(min)")
    tab = []
    for s, rs in by.items():
        n = len(rs); nl = sum(r["lock"] for r in rs)
        esc = [r["t_escape_tau"] for r in rs if r["t_escape_tau"] is not None]
        line = dict(sigma=s, Rc=rs[0]["Rc"], locks=f"{nl}/{n}", mad=sum(r["mad_over_amp"] for r in rs) / n,
                    maxv=max(r["maxabs_tail"] for r in rs), trit=sum(r["trit_agree"] for r in rs) / n, esc=min(esc) if esc else None)
        tab.append(line)
        print(f"{s:<9.5f} {('open' if line['Rc'] is None else f'{line[chr(82)+chr(99)]:.2f}'):>9}  {line['locks']:>5}  {line['mad']:>12.3g}  {line['maxv']:>10.3f}  {line['trit']:>10.3f}  {line['esc'] if line['esc'] is None else round(line['esc'],1)}")
    out[os.path.basename(p)] = dict(sigma_c_upper=sc, sigma_c_lower=below, table=tab)
json.dump(out, open("out/ring_summary.json" if len(sys.argv) > 2 else "out/ring_summary_single.json", "w"), indent=1)
