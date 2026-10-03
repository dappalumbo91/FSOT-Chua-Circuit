# Lock A — written 2026-10-03 (ET) BEFORE the fine window scan and BEFORE evaluating any closed form

## Target 3: periodic windows in r0 (single node = synchronous manifold)
Prior knowledge (disclosed): the coarse scans (`error_budget/results/std_r0scan.tsv` at a 2 Ω step, `map_x2_gamma` at a 0.02 γ step) showed periodic cells near r ≈ 10 Ω and r ≈ 17 Ω.
- H3a (FSOT operating-point requirement, genuine): no periodic window (λ1 ≤ 0.01 per τ for the median of 3 ICs) in r0 ∈ [17.94, 18.94] Ω, i.e. 18.44 Ω has a chaos margin of at least ±0.5 Ω.
- H3b (φ-ladder, test hypothesis; partly post-hoc): the centres of the two widest periodic windows in r0 ∈ [0, 40] Ω fall within ±2 % of r0_FSOT·φ^(−n/2), n integer (18.44, 14.50, 11.40, 8.96, 7.04 …).
- H3c (post-hoc; prompted by the coarse 17/10 ≈ 1.7): the ratio of the centres of the two widest windows equals φ within ±3 %.
Window = maximal run of r0 grid points with median λ1 ≤ 0.01. Width = run length. Centre = midpoint.

## Target 5: closed-form leading term for σc (no fitting)
Transverse linear system on each PWL segment with slope m: J_m − s·e1e1ᵀ. Characteristic polynomial λ³ + c2λ² + c1λ + c0 with A = α(1+m) + s:
c2 = 1 + γ + A, c1 = γ + β + A(1+γ) − α, c0 = A(γ+β) − αγ. Let s*(m) = the smallest s ≥ 0 for which Hurwitz holds (c2 > 0, c0 > 0, c2·c1 > c0).
- F5a: σc ≈ s*(b)/λ2, with λ2 = 3 (stabilise the scroll-centre focus, segment slope b).
- F5b: σc ≈ [p_in·s*(a) + (1 − p_in)·s*(b)]/3, where p_in is the attractor's time fraction with |x| < 1 on the isolated node (no ring information used).
- F5c: σc ≈ [s*(b) + λ1/… ]: not used. Only F5a and F5b are locked.
Both are evaluated at BOM α, β, a, b and γ = β·r0/R. They are compared with σ50 = 1.4954 (r0 = 18.44) and with the msfmap grids (γ × α, γ × b/a) from the error budget.
