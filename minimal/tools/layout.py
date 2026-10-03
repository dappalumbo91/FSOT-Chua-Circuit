"""Schematic (net-labelled) and Tinkercad-style breadboard PNGs + checklist for the FSOT minimal jerk circuit (TL074 + 1N4148)."""
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
RA = 3160  # post-hoc bench value (see REPORT); phi*R = 2912.5 is the locked design and is periodic with a real diode
# step, part, value, hole1, hole2, note   (holes: col letter + row; rails: '+T' top red, 'GT' top GND, 'GB' bottom GND, '-B' bottom blue)
S = [
 (1, "U1", "TL074 (14-pin)", "e10..e16 / f10..f16", "", "notch LEFT; pin 1 = e10 (bottom-left), pin 14 = f10"),
 (2, "J+", "red wire", "a13", "+T@13", "pin 4 V+ -> +9 V rail"),
 (3, "J-", "blue wire", "j13", "-B@13", "pin 11 V- -> -9 V rail"),
 (4, "Jg", "black wire", "GT@60", "GB@60", "tie the two GND rails"),
 (5, "Cd+", "100 nF", "+T@12", "GT@12", "decoupling"), (6, "Cd-", "100 nF", "-B@14", "GB@14", "decoupling"),
 (7, "Jg3", "black wire", "d12", "GB@12", "pin 3 IN1+ -> GND"), (8, "Jg5", "black wire", "d14", "GB@15", "pin 5 IN2+ -> GND"),
 (9, "Jg12", "black wire", "g12", "GT@11", "pin 12 IN4+ -> GND"), (10, "Jg10", "black wire", "g14", "GT@15", "pin 10 IN3+ -> GND"),
 (11, "C1", "100 nF", "a10", "a11", "U1 integrator cap (o1-n1)"), (12, "RA", f"{RA} ohm", "b10", "b11", "THE KNOB: 2.7k + 1k trimmer"),
 (13, "Jn1", "yellow wire", "c11", "a5", "extends node n1 to row 5"),
 (14, "Rc", "40.2 k", "b5", "+T@5", "constant: 9 V * 1.8k/40.2k = 0.403 V"),
 (15, "Rx", "1.8 k", "c5", "j18", "x feedback (o3 -> n1), via o3 extension row 18"),
 (16, "Rw", "1.8 k", "d5", "j10", "o4 -> n1"),
 (17, "R2", "1.8 k", "c10", "b15", "o1 -> n2"), (18, "C2", "100 nF", "a15", "a16", "U2 integrator cap"),
 (19, "R3", "1.8 k", "b16", "g15", "o2 -> n3 (crosses the gap)"), (20, "C3", "100 nF", "h15", "h16", "U3 integrator cap"),
 (21, "R4", "1.8 k", "c16", "g11", "o2 -> n4 (crosses the gap)"), (22, "Rf", "1.8 k", "h10", "h11", "U4 feedback"),
 (23, "Jx", "green wire", "i16", "f18", "o3 = x -> row 18 (x test point)"),
 (24, "D1", "1N4148", "g18", "g22", "anode (no band) row 18, cathode (black band) row 22"),
 (25, "Rd", "900 ohm (2 x 1.8k in parallel, or 909 E96)", "h22", "i11", "dn -> n4"),
]
TP = [("TP_x (V_o3, scope CH1)", "j16"), ("TP_x' (V_o2 = -tau0 x', CH2)", "d16"), ("TP_x'' (V_o1)", "d10"), ("TP_w (V_o4)", "i10")]
def xy(h):
    if '@' in h:
        r, n = h.split('@'); n = int(n); return (n, {'+T': 12.6, 'GT': 12.0, 'GB': -1.0, '-B': -1.6}[r])
    c, n = h[0], int(h[1:]); y = {'a': 0, 'b': 1, 'c': 2, 'd': 3, 'e': 4, 'f': 6.5, 'g': 7.5, 'h': 8.5, 'i': 9.5, 'j': 10.5}[c]; return (n, y)
fig, ax = plt.subplots(figsize=(15, 6)); ax.set_facecolor('#f4f1e8')
for n in range(1, 31):
    for c in 'abcdefghij': x, y = xy(f"{c}{n}"); ax.plot(x, y, 's', color='#bbb', ms=4)
for (rail, col) in [('+T', 'r'), ('GT', 'k'), ('GB', 'k'), ('-B', 'b')]:
    y = xy(f"{rail}@1")[1]; ax.plot([0.5, 30.5], [y, y], color=col, lw=2)
ax.add_patch(plt.Rectangle((9.6, 4.3), 6.8, 1.9, color='#222')); ax.text(13, 5.25, 'TL074', color='w', ha='center', va='center', fontsize=10)
ax.plot(9.8, 5.25, 'wo', ms=5)
cols = {'wire': None}
for st, p, v, h1, h2, note in S:
    if not h2: continue
    (x1, y1), (x2, y2) = xy(h1), xy(h2)
    c = 'r' if 'red' in v else 'b' if 'blue' in v else 'k' if 'black' in v else 'y' if 'yellow' in v else 'g' if 'green' in v else ('#c47' if p.startswith('R') else '#2a6' if p.startswith('C') else '#555')
    ax.plot([x1, x2], [y1, y2], '-', color=c, lw=3 if 'wire' in v else 5, solid_capstyle='round', alpha=.85)
    ax.text((x1 + x2) / 2, (y1 + y2) / 2 + 0.25, p, fontsize=7, ha='center', bbox=dict(fc='w', ec='none', alpha=.7, pad=.5))
for t, h in TP: x, y = xy(h); ax.plot(x, y, 'm*', ms=12); ax.text(x + .2, y - .45, t.split(' ')[0], color='m', fontsize=7)
ax.set_xlim(0, 31); ax.set_ylim(-2.3, 13.3); ax.set_xticks(range(1, 31)); ax.set_yticks([xy(c + '1')[1] for c in 'abcdefghij']); ax.set_yticklabels(list('abcdefghij'))
ax.set_title(f'FSOT minimal chaotic circuit, breadboard (top rail red +9 V, bottom blue -9 V, inner rails GND). R_A = {RA} ohm'); plt.tight_layout(); plt.savefig('png/breadboard_minimal.png', dpi=130); plt.close()
# schematic (net-labelled blocks)
fig, ax = plt.subplots(figsize=(13, 6)); ax.axis('off')
def opamp(x, y, name, inp, out):
    ax.add_patch(plt.Polygon([[x, y - .6], [x, y + .6], [x + 1.1, y]], fill=False, lw=2)); ax.text(x + .35, y, name, fontsize=8, va='center')
    ax.text(x - .1, y + .3, '-', ha='right'); ax.text(x - .1, y - .3, '+ (GND)', ha='right', fontsize=7); ax.plot([x - .6, x], [y + .3, y + .3], 'k'); ax.text(x - .65, y + .3, inp, ha='right', va='center', fontsize=9, color='b')
    ax.plot([x + 1.1, x + 1.6], [y, y], 'k'); ax.text(x + 1.65, y, out, va='center', fontsize=9, color='b')
blocks = [(1, 4.5, 'U1 (1/4 TL074)', 'n1', 'o1 = tau0^2 x\'\''), (5.5, 4.5, 'U2', 'n2', 'o2 = -tau0 x\''), (9.5, 4.5, 'U3', 'n3', 'o3 = x'), (5.5, 1.2, 'U4', 'n4', 'o4 = -(o2 + 2 max(x - Vd, 0))')]
for b in blocks: opamp(*b)
txt = [f"n1: R_A = {RA} (to o1) || C1 100 nF (to o1); Rw 1.8k from o4; Rx 1.8k from o3; Rc 40.2k from +9 V",
       "n2: R2 1.8k from o1; C2 100 nF to o2", "n3: R3 1.8k from o2; C3 100 nF to o3",
       "n4: R4 1.8k from o2; Rf 1.8k to o4; 1N4148 (anode o3) + Rd 900 ohm",
       "All non-inverting inputs to GND. Supplies +-9 V, 100 nF decoupling each rail.",
       "Dynamics: x''' = -A x'' - x' + |x - Vd| - U_eff,  A = R/R_A, tau0 = 1.8k*100n = 180 us, U_eff = 0.403 V + Vd"]
for i, t in enumerate(txt): ax.text(0.2, -0.6 - 0.45 * i, t, fontsize=9, family='monospace')
ax.set_xlim(0, 14); ax.set_ylim(-3.6, 5.6); ax.set_title('FSOT minimal chaotic circuit: schematic (net-labelled), 1 x TL074 + 1 x 1N4148 + 3 C + 9 R'); plt.tight_layout(); plt.savefig('png/schematic_minimal.png', dpi=130); plt.close()
with open('build_checklist_minimal.md', 'w') as f:
    f.write("# Build checklist: FSOT minimal chaotic circuit (TL074, 830-point breadboard)\n\nRails: top outer **+9 V (red)**, top inner GND, bottom inner GND, bottom outer **-9 V (blue)**. '+T@13' = top red rail hole at row 13.\n\n| Step | Part | Value | Lead 1 | Lead 2 | Notes |\n|---|---|---|---|---|---|\n")
    for st, p, v, h1, h2, note in S: f.write(f"| {st} | {p} | {v} | {h1} | {h2} | {note} |\n")
    f.write("\n| Test point | hole |\n|---|---|\n" + "".join(f"| {t} | {h} |\n" for t, h in TP))
print('ok')
