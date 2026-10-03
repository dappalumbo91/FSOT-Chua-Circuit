#!/usr/bin/env python3
"""Render breadboard layouts (PNG/SVG/PDF) + numbered build checklists + test-point lists, from breadboard.py,
after the connectivity check passes."""
import os, sys, json, math
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, FancyBboxPatch, Circle, Polygon
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from breadboard import build, verify, hname, RAIL_ROWS, RAILS
from chua_netlist import rc_for_sigma, PHI
HERE = os.path.dirname(os.path.abspath(__file__))
Y = {**{c: i + 1 for i, c in enumerate("abcde")}, **{c: i + 7 for i, c in enumerate("fghij")}}
RAILY = {"BOT-": -1.7, "BOTG": -0.9, "TOPG": 12.9, "TOP+": 13.7}
BANDS = ["black", "saddlebrown", "red", "darkorange", "gold", "green", "blue", "darkviolet", "gray", "white"]
WCOL = {"red": "#d62728", "blue": "#1f5fd6", "black": "#111111", "yellow": "#e6c700", "green": "#2ca02c",
        "orange": "#ff7f0e", "purple": "#9467bd", "white": "#bbbbbb"}

def xy(h):
    return (h[1], Y[h[3]]) if h[0] == "S" else (h[2], RAILY[h[1]])

def bands(v):
    s = f"{v:.3g}"; m, e = f"{v:.2e}".split("e")
    digits = m.replace(".", "").rstrip("0")
    if len(digits) <= 2:
        d = f"{float(m):.1f}".replace(".", "")[:2]; mult = int(e) - 1
        return [BANDS[int(d[0])], BANDS[int(d[1])], BANDS[mult] if mult >= 0 else "gold", "gold"]
    d = f"{float(m):.2f}".replace(".", "")[:3]; mult = int(e) - 2
    return [BANDS[int(d[0])], BANDS[int(d[1])], BANDS[int(d[2])], BANDS[mult] if mult >= 0 else "gold", "saddlebrown"]

def eng(v, u):
    for f, p in [(1e3, "k"), (1, ""), (1e-3, "m"), (1e-6, "µ"), (1e-9, "n")]:
        if abs(v) >= f * 0.999: return f"{v / f:.4g}{p}{u}"
    return f"{v:g}{u}"

def draw(B, tps, title, fname, rows=(0, 64)):
    r0, r1 = rows
    W = (r1 - r0) * 0.42 + 1.5
    fig, ax = plt.subplots(figsize=(W, 7.6))
    ax.add_patch(FancyBboxPatch((r0 + 0.3, -2.4), r1 - r0 - 0.6, 16.8, boxstyle="round,pad=0.1", fc="#f3f1ea", ec="#999"))
    ax.add_patch(Rectangle((r0 + 0.5, 5.6), r1 - r0 - 1, 0.8, fc="#e2dfd5", ec="none"))
    for rail, y in RAILY.items():
        c = "#d62728" if rail == "TOP+" else ("#1f5fd6" if rail == "BOT-" else "#111")
        ax.plot([r0 + 0.8, r1 - 0.8], [y + 0.38] * 2 if rail in ("TOP+", "BOTG") else [y - 0.38] * 2, color=c, lw=1.2)
        ax.text(r0 + 0.6, y, {"TOP+": "+9.19 V", "TOPG": "GND", "BOTG": "GND", "BOT-": "−9.19 V"}[rail], fontsize=7, color=c, ha="right", va="center")
        for r in RAIL_ROWS:
            if r0 < r < r1: ax.add_patch(Rectangle((r - 0.14, y - 0.14), 0.28, 0.28, fc="#555", ec="none"))
    for r in range(max(1, r0 + 1), min(64, r1)):
        for c, y in Y.items(): ax.add_patch(Rectangle((r - 0.13, y - 0.13), 0.26, 0.26, fc="#777", ec="none"))
        if r % 5 == 0 or r == 1: 
            ax.text(r, 0.2, str(r), fontsize=6.5, ha="center"); ax.text(r, 11.65, str(r), fontsize=6.5, ha="center")
    for c, y in Y.items():
        ax.text(r0 + 0.55, y, c, fontsize=7, ha="center", va="center"); ax.text(r1 - 0.55, y, c, fontsize=7, ha="center", va="center")
    lab_alt = 0
    for it in B.items:
        pts = [xy(h) for _, h in it["leads"]]
        if not all(r0 < p[0] < r1 for p in pts): continue
        k = it["kind"]
        if k == "TL082":
            rows_ = [p[0] for p in pts]; xa, xb = min(rows_) - 0.4, max(rows_) + 0.4
            ax.add_patch(Rectangle((xa, 4.75), xb - xa, 2.5, fc="#222", ec="k", zorder=5))
            ax.add_patch(Circle((xa + 0.12, 6.0), 0.18, fc="#666", zorder=6))
            ax.text((xa + xb) / 2, 6.0, it["ref"] + "\nTL082", color="w", fontsize=6.5, ha="center", va="center", zorder=6)
            for pin, h in it["leads"]:
                x, y = xy(h); ax.text(x, 5.05 if y < 6 else 6.95, pin, color="yellow", fontsize=6, ha="center", va="center", zorder=7)
            continue
        (x1, y1), (x2, y2) = pts
        if k == "wire":
            col = WCOL[it["color"]]
            if abs(x1 - x2) < 1e-9: xs, ys = [x1, x1], [y1, y2]
            else:
                mx = (x1 + x2) / 2; my = (y1 + y2) / 2 + (0.6 if y1 > 6 and y2 > 6 else -0.6 if y1 < 6 and y2 < 6 else 0)
                import numpy as np
                t = np.linspace(0, 1, 30); xs = (1 - t) ** 2 * x1 + 2 * (1 - t) * t * mx + t ** 2 * x2; ys = (1 - t) ** 2 * y1 + 2 * (1 - t) * t * my + t ** 2 * y2
            ax.plot(xs, ys, color=col, lw=2.6, solid_capstyle="round", zorder=8)
            ax.plot([x1, x2], [y1, y2], "o", color=col, ms=3.5, zorder=9)
            continue
        # two-lead parts
        hair = abs(x1 - x2) <= 1.01 and abs(y1 - y2) < 1e-9 or (abs(x1 - x2) <= 2.01 and abs(y1 - y2) < 1e-9 and it["note"].startswith("upright"))
        mx, my = (x1 + x2) / 2, (y1 + y2) / 2
        if hair: my += 0.55 if y1 > 6 else -0.55
        ax.plot([x1, mx, x2], [y1, my, y2], color="#888", lw=1.0, zorder=10)
        ang = math.degrees(math.atan2(y2 - y1, x2 - x1))
        if k == "R":
            L, H = 0.9, 0.32
            body = Rectangle((mx - L / 2, my - H / 2), L, H, fc="#e8c99a", ec="#7a5a2f", lw=0.6, zorder=11,
                             transform=matplotlib.transforms.Affine2D().rotate_deg_around(mx, my, ang) + ax.transData)
            ax.add_patch(body)
            bb = bands(it["value"])
            for i, bc in enumerate(bb):
                off = -0.32 + i * (0.64 / (len(bb) - 1))
                bx, by = mx + off * math.cos(math.radians(ang)), my + off * math.sin(math.radians(ang))
                ax.add_patch(Rectangle((bx - 0.04, by - H / 2), 0.08, H, fc=bc, ec="none", zorder=12,
                                       transform=matplotlib.transforms.Affine2D().rotate_deg_around(bx, by, ang) + ax.transData))
            lab = f"{it['ref']}\n{eng(it['value'], 'Ω')}"
        elif k in ("C", "Cdec"):
            ax.add_patch(Circle((mx, my), 0.22, fc="#f2b21b" if k == "C" else "#4a90d9", ec="k", lw=0.5, zorder=11))
            lab = f"{it['ref']}\n{eng(it['value'], 'F')}"
        elif k == "L":
            ax.add_patch(Circle((mx, my), 0.36, fc="#3d8f3d", ec="k", lw=0.6, zorder=11))
            lab = f"{it['ref']}\n{eng(it['value'], 'H')}"
        lab_alt ^= 1
        dy = 0.45 if my >= 6 else -0.45
        if k == "Cdec": lab = it["ref"]
        ax.text(mx, my + dy + (0.25 if lab_alt and dy > 0 else -0.25 if lab_alt else 0), lab, fontsize=5.6, ha="center", va="bottom" if dy > 0 else "top", zorder=13,
                bbox=dict(boxstyle="round,pad=0.08", fc="white", ec="none", alpha=0.75))
    for name, desc, h in tps:
        x, y = xy(h)
        if r0 < x < r1:
            ax.add_patch(Circle((x, y), 0.24, fc="none", ec="magenta", lw=1.4, zorder=14))
            ax.text(x + 0.25, y + (0.3 if y > 6 else -0.3), name, color="magenta", fontsize=6, zorder=14, va="center")
    ax.set_xlim(r0 - 0.6, r1 + 0.2); ax.set_ylim(-3.2, 15.4); ax.set_aspect("equal"); ax.axis("off")
    ax.set_title(title, fontsize=10, loc="left")
    fig.tight_layout()
    for ext in ("png", "svg", "pdf"):
        fig.savefig(os.path.join(HERE, f"{fname}.{ext}"), dpi=170 if ext == "png" else None)
    plt.close(fig)

def checklist(B, tps, title, fname, extra=""):
    L = [f"# {title}", "", "Board: standard 830-point (rows 1–63, holes a–e bottom / f–j top, centre gap between e and f).",
         "Rails: top outer = **+9.19 V (red)**, top inner = **GND**, bottom inner = **GND**, bottom outer = **−9.19 V (blue)**.",
         "If your board's rails are split in the middle (gap near row 30), bridge each rail across the gap with a short wire of the rail's colour.",
         "Supply: two bench supplies in series (or ±9 V then trim): (+) of PS1 → top +V rail, PS1 (−)/PS2 (+) → GND rails, PS2 (−) → bottom −V rail.",
         "**Before power-on**: set the rails so U2's saturated output reads 7.67 V (SPICE: ±9.19 V for TL082, ±9.66 V for 741 models). Bp1 = Esat·3.3/25.3 = 1.00 V.",
         "Rail positions written '@ row N' mean the rail hole nearest row N — electrically any hole on that same rail is equivalent.",
         "741 alternative (no TL082): use two 741s per node (U1 for R1/R2/R3, U2 for R4/R5/R6): 741 pin 3 = + (to V_C1), pin 2 = −, pin 6 = out, pin 7 = +V, pin 4 = −V; this layout is for the TL082 (one chip per node, matching the repo BOM).",
         "Hairpin = resistor stood upright with one lead bent back down (the two holes are only 1–2 rows apart).", ""]
    if extra: L += [extra, ""]
    L += ["| Step | Part | Value | Lead 1 | Lead 2 | Notes |", "|---|---|---|---|---|---|"]
    order = {"wire": 1, "TL082": 0, "Cdec": 2, "R": 3, "C": 4, "L": 5}
    items = sorted(B.items, key=lambda it: (0 if it["kind"] == "TL082" else 1, 0 if it["kind"] == "wire" and it["color"] in ("red", "blue", "black") and it["ref"].startswith(("Jv", "Jg")) else 1))
    n = 0
    for it in items:
        k = it["kind"]
        if k == "TL082":
            n += 1
            pins = ", ".join(f"pin {p} → {hname(h)}" for p, h in it["leads"])
            L.append(f"| {n} | {it['ref']} | TL082 | {pins} | | {it['note']} |"); continue
        n += 1
        val = (f"{it['color']} wire" if k == "wire" else eng(it["value"], {"R": "Ω", "C": "F", "Cdec": "F", "L": "H"}[k]))
        L.append(f"| {n} | {it['ref']} | {val} | {hname(it['leads'][0][1])} | {hname(it['leads'][1][1])} | {it['note']} |")
    L += ["", "## Test points (scope probe tip; ground clip on any GND rail hole)", "", "| TP | Signal | Hole |", "|---|---|---|"]
    for name, desc, h in tps: L.append(f"| {name} | {desc} | {hname(h)} |")
    L += ["", "Scope: X–Y mode with CH1 = TP1 (V_C1), CH2 = TP2 (V_C2) shows the double scroll; Y-T mode at 2 ms/div (×1 values) shows lobe switching ≈ ±4.3 V on V_C1."]
    open(os.path.join(HERE, f"{fname}.md"), "w").write("\n".join(L) + "\n")
    return n

if __name__ == "__main__":
    report = {}
    B, parts, tps = build("A")
    v = verify(B, parts, "A"); report["single_node"] = v; assert v["nets_match"], v
    draw(B, tps, "FSOT Kennedy–Chua node A on an 830-point breadboard (TL082)\ngenerated from chua_netlist.py; hole-level connectivity verified against the netlist", "breadboard_single_node", rows=(0, 16))
    report["single_node"]["steps"] = checklist(B, tps, "Build checklist — single FSOT Kennedy–Chua node (TL082)", "build_checklist_single_node")
    rc = rc_for_sigma(PHI ** 2)
    B, parts, tps = build("ABC", (6800.0, 75.0))
    v = verify(B, parts, "ABC"); report["ring_phi2"] = v; assert v["nets_match"], v
    draw(B, tps, f"FSOT Kennedy–Chua 3-node ring on one 830-point breadboard (3 × TL082), σ = φ²: each Rc = 6.8 kΩ + 75 Ω = 6875 Ω (target {rc:.2f} Ω)\ngenerated from chua_netlist.py; hole-level connectivity verified against the netlist", "breadboard_ring_sigma_phi2")
    report["ring_phi2"]["steps"] = checklist(B, tps, "Build checklist — 3-node ring, σ = φ² (Rc = 6.8 kΩ + 75 Ω)", "build_checklist_ring_sigma_phi2",
        extra="Other gates: swap the three Rc pairs → σ = φ: 10 kΩ + 1.13 kΩ (E96) = 11 130 Ω (target 11 124.61 Ω); σ = 1: 18 kΩ + jumper; σ = 0.9: 20 kΩ + jumper; open: remove the three coupling wires JcA/JcB/JcC.")
    # mutation test: the checker must catch a single mis-wired lead
    B2, parts2, _ = build("ABC", (6800.0, 75.0))
    it = next(i for i in B2.items if i["ref"] == "R4B"); p, h = it["leads"][0]; it["leads"][0] = (p, ("S", h[1] - 1, h[2], h[3]))
    try: report["mutation_test_detected"] = not verify(B2, parts2, "ABC")["nets_match"]
    except AssertionError as e: report["mutation_test_detected"] = f"yes ({e})"
    B3, parts3, _ = build("ABC", (6800.0, 75.0))   # second mutation: move C1B's lead to an empty strip
    it = next(i for i in B3.items if i["ref"] == "C1B"); p, h = it["leads"][0]; it["leads"][0] = (p, ("S", 63, "bot", "a"))
    report["mutation2_detected"] = not verify(B3, parts3, "ABC")["nets_match"]
    json.dump(report, open(os.path.join(HERE, "connectivity_report.json"), "w"), indent=1)
    print(json.dumps(report, indent=1))
