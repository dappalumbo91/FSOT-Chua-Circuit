# minimal/ STATUS (checkpoint)
- [x] Design: PWL jerk x'''=-A x''-x'+|x|-1, TL074 + 1N4148; Branch J A=1/phi (hypothesis). LOCK M1 078343de14f49cf8116b9fb9c53ad7642bd6712e7d767903fb8733bd31df40d4
- [x] C++ engine src/mj.cpp (build: g++ -std=c++20 -O3 -pthread -o mj src/mj.cpp). LE at 1/phi: l1 0.048 (8 ICs), sum -0.61803, f 0.1555/tau=864 Hz, x in [-2.445,1.186]
- [x] Bifurcation vs A: results/bif_A.tsv (0.40-0.80), bif_A_fine.tsv (0.60-0.64). Chaos [0.547,0.640] with windows; hair-thin window at 0.6182 near 1/phi.
- [x] Shilnikov: E- satisfies ratio (0.133) but NO homoclinic for A in [0.3,1.2] (stable manifold escapes; results/homo_Eminus.tsv). E+ fails ratio (1.027). -> need CAP horseshoe.
- [x] LOCK M2 (bench knob R_A,c=2.812k [2.64,2.98], TL074 |dA_c|<=0.005, SPICE chaos) — hash in predictions/LOCK_M2.sha256
- [x] Full op-amp model src/oa.cpp (build g++ -std=c++20 -O3 -pthread -o oa src/oa.cpp). At 1/phi TL074: l1 0.0530 (8 ICs) vs ideal 0.048 (+10%), f 0.15535/tau (-0.1%), x [-2.448,1.195] -> B3 parts hold. Edge: ideal last chaotic A 0.6405 (R_A,c 2810 ohm), TL074 0.6425 (2802 ohm): dA_c +0.002 <= 0.005 -> B3 HOLDS; B1 ideal value inside band (results/edge_summary.txt)
- [ ] NEXT: CAP proof (interval covering relations, small, CI-replayable) in src/cap.cpp
- [ ] ngspice netlist + TI TL074 model by link+sha256 (spice/), score B4; Falstad ctz link; schematic+breadboard PNG; BENCH guide; comparison vs Chua table
- [ ] branch feat/fsot-minimal-chaos, CI job, draft PR (no merge)

## Notes for resume
- LOCK M2 window list is approximate (periodic gaps actually 0.549-0.563, 0.571-0.572, 0.586-0.598 per bif_A.tsv); these are reported facts, not predictions.
- Hair-thin periodic window at A=0.6182, 0.0002 above 1/phi: flag in report (bench resistor tolerance makes it irrelevant but it is close).
- Remaining order: (1) CAP proof src/cap.cpp, (2) spice/ netlist + TL074 model link+sha256 + score B4, (3) Falstad ctz, (4) PNGs schematic/breadboard/attractor/bif, (5) BENCH guide, (6) comparison table vs Chua, (7) copy to repo minimal/, CI job, branch feat/fsot-minimal-chaos, push, draft PR.
- [x] Side task Branch J: LOCK J 3683004b8c9d3a53325bc340d6d5eff0f37293ba245dcba0d4a960395617117f. J1 A=k=0.0393 and J2 A=gamma=0.1509 both ESCAPE (unbounded) -> FALSIFIED. Distances to the 0.6182 hairline: -0.579 / -0.467. No 1/phi-independent derivation found.
- [ ] CAP proof: deferred (intractable in budget); strongest rigorous = exact analytic eigen/divergence results. Do ngspice next.
- [x] ngspice (spice/mkcir.py, analyze.py; TI TL082 SLOJ070 as TL07x proxy, sha256-checked fetch; 1N4148 Shockley): nominal R_A=2912.5 is PERIOD-2 (2 distinct maxima, lam~0) -> B4 FAILS. Scan 2700-3400/20: period doubling 2960->2980(4)->3060(8)->chaos >=3080 with windows (3120, 3240, 3320). SPICE upper chaos edge ~3070 ohm (A~0.586) vs locked 2812 [2640,2980] -> B1 FAILS. Cause: soft diode knee (ideal-opamp E-source run identical: eid_nominal periodic, eid_3150 chaotic) -> TL082 effect negligible, B3 consistent. R_A=3150: chaotic, lam ~310/s (two-run divergence). Post-hoc bench value: R_A = 3.16k (E96) middle of 3160-3220 chaotic run.
- [ ] NEXT: Falstad, PNGs, guide, comparison, repo/PR
- [x] Falstad: falstad/gen_falstad_minimal.py, verify_minimal.py ALL OK (roundtrip with Falstad lz-string, values); urls.json (nominal 2912.5 and bench 3160). Not live-run in a browser.
- [x] PNGs: png/{lambda1_vs_A_cpp,spice_RA_scan,attractors_cpp_vs_spice,schematic_minimal,breadboard_minimal}.png; build_checklist_minimal.md (tools/layout.py). NEXT: BENCH guide, comparison, REPORT, repo+CI+PR
- [x] BENCH_BUILD_GUIDE_MINIMAL.md
- [x] REPORT.md (scorecard + comparison). NEXT: repo minimal/, CI job, branch, PR

## Task 3 (directive: NO post-hoc values), started 08:27 ET
- [x] REPO_SURVEY.md. Finds: γ_rel is FSOT's damping rate; τ0 and U are engineering scales (fsot-law-circuit precedent); no FSOT junction physics; FSOT chaos results are Feigenbaum and Hénon only
- [x] LOCK D1 9a9bd4cb… (knob A = γ_rel, giving R_A = 4205 Ω; scales; Branch D = Shockley model)
- [x] src/bd.cpp (Branch D engine). LOCK D2 3fe1b39a… (edge shifts at T0/T60/V12, K-1 rail latch, K′ at 2744 periodic)
- [ ] ngspice scoring running (spice/run_lockd2.py, writing out/lockd2.jsonl)
- [ ] interval proof (src/proof.cpp)
- [x] ngspice scoring: D-T0/T60/V12 confirmed; K-1 rail latch confirmed (FSOT knob not chaotic); K′ periodic confirmed (results/LOCK_D_score.md, png/lockD2_edge_shifts.png)
- [x] proof/: Na ⇒ Na VERIFIED at A = 1/φ (periodic orbit exists); horseshoe not reached
- [x] guide, REPORT and Falstad (added the derived 4.22k link) updated. NEXT: CI step, tests, commit, push
- [x] tests green (algebra, falstad x2, ctest 2/2, check_minimal + Branch D replay, proof check); committed 0d04b38 and pushed (verified with ls-remote)

## Task 4 (DJ + FSOT topology + chaos proof), started 08:57 ET
- [ ] P1 DJ derivation + datasheet + lock  - [ ] P2 candidates + lock  - [ ] sims  - [ ] proof
- [x] LOCK DJ f80d7d0d… LOCK T 61f259b2… LOCK T2 724228ea… (sha files in predictions/)
- [x] DJ scored (datasheets/fig1_digitized.json): DJ1, DJ3, DJ4, DJ5 pass; DJ2 fails (Rs); DJ6 fails narrowly (max spec); DJ-K confirmed (rail latch; DJ edge 3100 Ω)
- [x] T: S-a FALSIFIED (C++ unbounded in all ICs; ngspice rail-to-rail periodic). 16 candidates; only A-c (≡ canonical at γ_rel) bounded, in 1 of 4 ICs
- [x] T2 (post-hoc small-basin attractor at γ_rel): T2-1 falsified (basin < 0.005), T2-4/T2-5 falsified (real diode → rail latch)
- [ ] NEXT: proof at A = γ_rel, ideal canonical (mean-value form + Thm-16 covering graph)
- [x] PROOF: horseshoe.cpp verifies 4/4 covering relations under P^4 at A = γ_rel (ideal), entropy ≥ ln2/4. CI job horseshoe-proof
- [x] docs, REPORT, check_minimal (new locks, datasheet checksums, S-a replay). NEXT: tests, commit, push
- [x] PROOF: horseshoe.cpp verifies 4/4 covering relations under P^4 at A = γ_rel (ideal), entropy ≥ ln2/4. CI job horseshoe-proof
- [x] docs, REPORT, check_minimal (new locks, datasheet checksums, S-a replay). NEXT: tests, commit, push
