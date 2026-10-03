# Computer-assisted proof (C++20, interval arithmetic)

**System:** the ideal minimal jerk x''' = −A x'' − x' + |x| − 1, with A = 1/φ. A is enclosed rigorously from √5, and this is the LOCK M1 hypothesis value.

The FSOT-derived knob A = γ_rel (LOCK D1) has no bounded attractor: it is unbounded in the ideal model and latches to the rail in the real circuit. A chaos proof at that parameter is therefore impossible, and the proof is done at the M1-locked value.

## Method
- **Section:** Σ = {x = 0}. The return map is P = P₋∘P₊.
- **Flows:** in each half-space the flow is linear, so v(t) = v* + e^{Mt}(v₀ − v*). e^{M[0,h]} (h = 1/32) is enclosed by a 14-term Taylor series with a rigorous remainder.
- **Rounding:** every +, −, × and ÷ is rounded outward by one ulp (iv.hpp). No libm transcendental functions are used.
- **Crossings:** for each step the code proves the sign of x. In the crossing window, x is proven strictly monotone (sign of y) and the crossing is pinned down by sub-interval refinement.
- **Covering relations** (Zgliczyński–Gidea, u = s = 1): an h-set N is a parallelogram c + uU + sS. N ⇒ N under P is verified by two checks over a 1000 × 40 box subdivision:
  - (i) |s(P(N))| < 1;
  - (ii) the two u-edges map to u < −1 and u > +1, one each.

## Verified result (`./proof check hsets.txt`, about 25 s on 8 threads)
- **Na ⇒ Na under P: VERIFIED** (max |s| = 0.48).
- By the covering-relation theorem, P has a fixed point in Na. So there is a **periodic orbit of the flow, proven to exist**, crossing x = 0 at x' ∈ [1.23, 1.40]. It is numerically unstable, with multiplier ≈ −1.616.

## Not reached
A two-symbol topological horseshoe, which would prove chaos with entropy ≥ ln 2 / k, was not reached.
- P has weak expansion (|μ| ≈ 1.6).
- The attractor's section folds near y ≈ 1.66–1.75.
- Covering by P² fails because of interval wrapping at the current box sizes.
- Next steps: h-sets along the folded branch, and Lohner-type QR wrapping control for P².
