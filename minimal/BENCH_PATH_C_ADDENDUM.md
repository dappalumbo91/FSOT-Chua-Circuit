# Path C (LOCK PC): Kennedy–Chua single node at Branch L. Bench pointers

This is the existing, validated FSOT-Chua build. Use the full staged guide with meter checkpoints:
- guide: `build_visuals/BENCH_BUILD_GUIDE.md` (stages 0–4 and troubleshooting);
- breadboard: `build_visuals/breadboard_single_node.png`;
- schematic: `build_visuals/schematic_single_node.png`;
- Falstad: `falstad/chua_single_node_r0_18p44.url`.

New results from LOCK PC (`67274bb1…`) that matter on the bench:
- **ngspice, TI TL082, default start:** double scroll with no rail latch. V_C1 runs −4.27 … +4.28 V at the calibrated ±9.19 V rails, and −4.16 … +4.17 V at ±9.00 V. There are 149–154 distinct maxima in 0.1 s.
- **Local frequency:** ≈ 2.55 kHz (C++ 2547 Hz, ngspice 2564 Hz). Lobe switching gives a broad low-frequency peak (≈ 210–280 Hz).
- **Coexisting outer limit cycle:** 30 of 64 random starts in C++ go to a large periodic orbit with max|x| = 7.35 Bp (≈ ±7.3 V, beyond the outer breakpoint). Power-on from discharged capacitors reaches the double scroll in C++ and ngspice.
  - **Troubleshooting entry:** if the scope shows a large clean ±7 V loop, switch off, short C1 and C2 for a second to discharge them, and power up again.
- **Tolerance:** 61 of 64 C++ draws stay on the double scroll within the acceptance spec (L ±1.2 %, C1 ±1 %, R ±1 %, C2 ±4.5 %, r0 ±0.33 Ω, NIC resistors ±1 %).
