"""Schematic, breadboard PNG and hole-by-hole checklist for the LOCK PJ circuit:
x''' = -gamma_rel x'' - Theta x' + (kappa/gamma_rel)|x| - 1, precision-rectifier |x| (TL074 + TL072 + 2 x 1N4148), E96 values."""
# step, part, value, hole1, hole2, note   (holes: col letter + row; rails: '+T' top red +9 V, 'GT' top GND, 'GB' bottom GND, '-B' bottom blue -9 V)
S = [
 (1, "U1", "TL074 (14-pin)", "e10..e16 / f10..f16", "", "notch LEFT; pin 1 = e10, pin 7 = e16, pin 8 = f16, pin 14 = f10"),
 (2, "U5", "TL072 (8-pin)", "e22..e25 / f22..f25", "", "notch LEFT; pin 1 = e22, pin 4 = e25, pin 5 = f25, pin 8 = f22"),
 (3, "J+", "red wire", "a13", "+T@13", "TL074 pin 4 V+ -> +9 V"), (4, "J-", "blue wire", "j13", "-B@13", "TL074 pin 11 V- -> -9 V"),
 (5, "J2+", "red wire", "j22", "+T@22", "TL072 pin 8 V+ -> +9 V"), (6, "J2-", "blue wire", "a25", "-B@25", "TL072 pin 4 V- -> -9 V"),
 (7, "Jg", "black wire", "GT@30", "GB@30", "tie the two GND rails at the right end"),
 (8, "Cd1+", "100 nF", "+T@12", "GT@12", "decoupling TL074"), (9, "Cd1-", "100 nF", "-B@14", "GB@14", "decoupling TL074"),
 (10, "Cd2+", "100 nF", "+T@21", "GT@21", "decoupling TL072"), (11, "Cd2-", "100 nF", "-B@26", "GB@26", "decoupling TL072"),
 (12, "Jg3", "black wire", "d12", "GB@12", "TL074 pin 3 IN1+ -> GND"), (13, "Jg5", "black wire", "d14", "GB@15", "TL074 pin 5 IN2+ -> GND"),
 (14, "Jg12", "black wire", "g12", "GT@11", "TL074 pin 12 IN4+ -> GND"), (15, "Jg10", "black wire", "g14", "GT@15", "TL074 pin 10 IN3+ -> GND"),
 (16, "Jg24", "black wire", "b24", "GB@24", "TL072 pin 3 IN1+ -> GND"), (17, "Jg25", "black wire", "j25", "GT@25", "TL072 pin 5 IN2+ -> GND (unused half)"),
 (18, "J67", "short wire", "g24", "g23", "TL072 pin 6 -> pin 7 (unused half as grounded follower)"),
 (19, "C1", "100 nF film", "a10", "a11", "U1 integrator cap (o1-n1)"), (20, "RA", "4.22 k (R/gamma_rel)", "b10", "b11", "x'' gain gamma_rel"),
 (21, "Jn1", "yellow wire", "c11", "a5", "extends node n1 to row 5"),
 (22, "Rc", "40.2 k", "b5", "+T@5", "constant: 9 V x 1.8k/40.2k = 0.403 V (= U)"),
 (23, "Rx", "2.43 k (R/G, G = kappa/gamma_rel)", "c5", "j18", "x term (o3 -> n1)"),
 (24, "Rw", "1.96 k (R/B, B = Theta)", "d5", "j10", "x' term (o4 -> n1)"),
 (25, "Rr", "1.21 k (R/2G)", "e5", "e6", "rectifier term (r -> n1); row 6 = node r"),
 (26, "Jr", "white wire", "a6", "a27", "node r: row 6 <-> row 27"),
 (27, "R2", "1.8 k", "c10", "b15", "o1 -> n2"), (28, "C2", "100 nF film", "a15", "a16", "U2 integrator cap"),
 (29, "R3", "1.8 k", "b16", "g15", "o2 -> n3 (crosses the gap)"), (30, "C3", "100 nF film", "h15", "h16", "U3 integrator cap"),
 (31, "R4", "1.8 k", "c16", "g11", "o2 -> n4 (crosses the gap)"), (32, "Rf", "1.8 k", "h10", "h11", "U4 feedback: o4 = -o2"),
 (33, "Jx", "green wire", "i16", "f18", "o3 = x -> row 18 (x test point)"),
 (34, "R5", "1.8 k", "g18", "b23", "o3 -> n5 (rectifier input)"),
 (35, "Rf5", "1.8 k", "c23", "c27", "n5 -> r (rectifier feedback)"),
 (36, "Da", "1N4148", "d22", "d23", "anode u5 (row 22), cathode/band n5 (row 23)"),
 (37, "Db", "1N4148", "b27", "b22", "anode r (row 27), cathode/band u5 (row 22)"),
]
TP = [("TP_x (V_o3, CH1)", "h18"), ("TP_x' (V_o2 = -U x', CH2)", "d16"), ("TP_x'' (V_o1)", "d10"), ("TP_w (V_o4)", "i10"), ("TP_r", "d27")]
def xy(h):
    if '@' in h:
        r, n = h.split('@'); n = int(n); return (n, {'+T': 12.6, 'GT': 12.0, 'GB': -1.0, '-B': -1.6}[r])
    c, n = h[0], int(h[1:]); return (n, {'a': 0, 'b': 1, 'c': 2, 'd': 3, 'e': 4, 'f': 6.5, 'g': 7.5, 'h': 8.5, 'i': 9.5, 'j': 10.5}[c])
if __name__ == '__main__':
    import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(15, 6)); ax.set_facecolor('#f4f1e8')
    for n in range(1, 31):
        for c in 'abcdefghij': x, y = xy(f"{c}{n}"); ax.plot(x, y, 's', color='#bbb', ms=4)
    for rail, col in [('+T', 'r'), ('GT', 'k'), ('GB', 'k'), ('-B', 'b')]:
        y = xy(f"{rail}@1")[1]; ax.plot([0.5, 30.5], [y, y], color=col, lw=2)
    for x0, w, nm in ((9.6, 6.8, 'TL074'), (21.6, 3.8, 'TL072')):
        ax.add_patch(plt.Rectangle((x0, 4.3), w, 1.9, color='#222')); ax.text(x0 + w / 2, 5.25, nm, color='w', ha='center', va='center', fontsize=10); ax.plot(x0 + .2, 5.25, 'wo', ms=5)
    for st, p, v, h1, h2, note in S:
        if not h2: continue
        (x1, y1), (x2, y2) = xy(h1), xy(h2)
        c = 'r' if 'red' in v else 'b' if 'blue' in v else 'k' if 'black' in v else 'y' if 'yellow' in v else 'g' if 'green' in v else '#999' if 'white' in v or 'short' in v else ('#c47' if p.startswith('R') else '#2a6' if p.startswith('C') else '#d60' if p.startswith('D') else '#555')
        ax.plot([x1, x2], [y1, y2], '-', color=c, lw=3 if 'wire' in v else 5, solid_capstyle='round', alpha=.85)
        ax.text((x1 + x2) / 2, (y1 + y2) / 2 + 0.25, p, fontsize=7, ha='center', bbox=dict(fc='w', ec='none', alpha=.7, pad=.5))
    for t, h in TP: x, y = xy(h); ax.plot(x, y, 'm*', ms=12); ax.text(x + .2, y - .45, t.split(' ')[0], color='m', fontsize=7)
    ax.set_xlim(0, 31); ax.set_ylim(-2.3, 13.3); ax.set_xticks(range(1, 31)); ax.set_yticks([xy(c + '1')[1] for c in 'abcdefghij']); ax.set_yticklabels(list('abcdefghij'))
    ax.set_title('FSOT Path J circuit (LOCK PJ): breadboard. Top rail red +9 V, bottom blue -9 V, inner rails GND'); plt.tight_layout(); plt.savefig('png/breadboard_pj.png', dpi=130); plt.close()
    fig, ax = plt.subplots(figsize=(13, 6.6)); ax.axis('off')
    def opamp(x, y, name, inp, out):
        ax.add_patch(plt.Polygon([[x, y - .6], [x, y + .6], [x + 1.1, y]], fill=False, lw=2)); ax.text(x + .3, y, name, fontsize=8, va='center')
        ax.text(x - .1, y - .3, '+ (GND)', ha='right', fontsize=7); ax.plot([x - .6, x], [y + .3, y + .3], 'k'); ax.text(x - .65, y + .3, inp, ha='right', va='center', fontsize=9, color='b')
        ax.plot([x + 1.1, x + 1.6], [y, y], 'k'); ax.text(x + 1.65, y, out, va='center', fontsize=9, color='b')
    for b in [(1, 5, 'U1 TL074a', 'n1', "o1 = U x''"), (5.5, 5, 'U2 TL074b', 'n2', "o2 = -U x'"), (10, 5, 'U3 TL074c', 'n3', 'o3 = U x'),
              (1, 2, 'U4 TL074d', 'n4', "o4 = -o2 = U x'"), (5.5, 2, 'U5 TL072a', 'n5', 'u5 (diode node)')]: opamp(*b)
    txt = ["n1: RA 4.22k to o1 || C1 100n to o1; Rw 1.96k from o4; Rx 2.43k from o3; Rr 1.21k from r; Rc 40.2k from +9 V",
           "n2: R2 1.8k from o1; C2 100n to o2        n3: R3 1.8k from o2; C3 100n to o3        n4: R4 1.8k from o2; Rf 1.8k to o4",
           "n5: R5 1.8k from o3; Rf5 1.8k to r; Da 1N4148 u5 -> n5; Db 1N4148 r -> u5   =>  r = -max(o3, 0)  (precision half-wave)",
           "Unused TL072b: IN+ to GND, IN- to OUT. Supplies +-9 V, 100 nF decoupling per rail per chip.",
           "Dynamics (tau0 = 1.8k x 100n = 180 us, U = 0.403 V):  x''' = -gamma_rel x'' - Theta x' + (kappa/gamma_rel)|x| - 1",
           "gamma_rel = 0.42804, Theta = 0.91751, kappa/gamma_rel = 0.73505 (FSOT; LOCK PJ 7524bad0). Exact R/B = 1961.8, R/G = 2448.8, R/2G = 1224.4 ohm",
           "Expected: o3 in [-1.39, +0.85] V, chaotic, f ~ 800-820 Hz (ngspice TL082: 798 Hz E96)"]
    for i, t in enumerate(txt): ax.text(0.1, 0.6 - 0.45 * i, t, fontsize=8.5, family='monospace')
    ax.set_xlim(0, 14); ax.set_ylim(-2.7, 6); ax.set_title('FSOT Path J chaotic circuit: schematic (net-labelled). 1 x TL074 + 1 x TL072 + 2 x 1N4148 + 3 C + 12 R'); plt.tight_layout(); plt.savefig('png/schematic_pj.png', dpi=130); plt.close()
    with open('build_checklist_pj.md', 'w') as f:
        f.write("# Build checklist: FSOT Path J circuit (TL074 + TL072, 830-point breadboard)\n\nRails: top outer **+9 V (red)**, top inner GND, bottom inner GND, bottom outer **-9 V (blue)**. '+T@13' = top red rail hole at row 13.\n\n| Step | Part | Value | Hole 1 | Hole 2 | Note |\n|---|---|---|---|---|---|\n")
        for st, p, v, h1, h2, note in S: f.write(f"| {st} | {p} | {v} | {h1} | {h2} | {note} |\n")
        f.write("\n| Test point | hole |\n|---|---|\n" + "".join(f"| {t} | {h} |\n" for t, h in TP))
    print('ok')
