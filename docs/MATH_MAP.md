# Math map — PDF hardware onto the FSOT pin

Authority: [FSOT-2.1-Lean](https://github.com/dappalumbo91/FSOT-2.1-Lean) `vendor/fsot_compute.py` pin **AEB2AD**. Zero free parameters.

## Engine

\[
S = K(T_1 + T_2 + T_3)
\]

Seeds: \(\pi, e, \varphi, \gamma, G\). Collapse threshold \(\Theta = C_{\mathrm{eff}}\cdot P_{\mathrm{var}}\).

Prediction law (every domain):

```
computed = measured × (1 + |S(domain)| × P_NEW)
```

Mismatch rule: change \(D_{\mathrm{eff}}\) / domain, not a new coefficient.

## Domain routing for this board

| Piece | Domain | \(D_{\mathrm{eff}}\) | Why |
|-------|--------|---------------------:|-----|
| Analog RLC / Chua / voltages | Electromagnetism | 7 (nest, AEB2AD) | currents, fields, ADC rails; Branch L inductor loss |
| Passives BOM (C dielectric, L core) | Materials_Science | 8 | catalog emergence panel (Branch L sensitivity: r0 18.42 Ω) |
| Acoustic / Chladni / Faraday (PDF p.2) | Acoustics | 8 | nodal fields, later lab |
| ESP32 platform rails | Electromagnetism (panel D=12 in Lean priors) | 7 live / 12 panel | `Esp32PlatformEngineeringPanelPriors` |

S(Electromagnetism) is computed live from the pin. Do not hard-code it in new math; firmware may freeze the kernel constants.

## Trinary

Same \(\{-1,0,+1\}\) as GPU consensus, Quantum spins, Genetics codons, neuron-zig ORFs.

| Trit | Scalar collapse | Voltage (Chua) | PDF word |
|------|-----------------|----------------|----------|
| \(+1\) | \(S > \Theta\) | \(V_{C1} > +B_p\) | excitation / emergence |
| \(0\) | \(\lvert S\rvert < \Theta\) | \(\lvert V_{C1}\rvert \le B_p\) | quiescent / superposed inner |
| \(-1\) | \(S < -\Theta\) | \(V_{C1} < -B_p\) | inhibition / damping |

\(B_p = 1\,\mathrm{V}\) is the Chua breakpoint, not a fit.

## Coupling (T³ / Quantum κ)

FSOT-Quantum:

\[
\kappa_{ij} = A_{\mathrm{bleed}}\cdot\mathrm{POOF}\cdot\lvert S_i\rvert\lvert S_j\rvert\big/\bigl(1+\lvert D_i-D_j\rvert/25\bigr)
\]

Identical nodes: \(D_i=D_j=7\). Dimensionless Chua coupling:

\[
\sigma = \alpha R / R_c,\qquad \alpha=C_2/C_1.
\]

The 3% residual was a **wrong object**, not a missing coefficient.

| Wrong (3%) | Right (gates `overall_ok`) |
|------------|----------------------------|
| 1-D chain (ends ≠ middle) | **Ring / triangle** — every node degree 2 |
| Matsumoto \(a,b=-1.143,-0.714\) | **BOM NIC** \(G_a=-1/1320\), \(G_b=1/R_4-R_2/(R_1R_3)=-9/22000\) (2026-10-03 fix; was \(-1/3.3\mathrm{k}\)), outer \(G_c=101/22000\) |
| `LOCK_ORDER = 0.85` | trit \(\ge \varphi^{-1}\), MAD/amp \(\le \varphi^{-4}\) (hardware working-set law) |
| \(\sigma_c=\alpha/\varphi\) after the sweep | **\(\sigma_c=1.4897\)** from Branch L \(\gamma\) + master stability, locked before the sweep; \(\sigma=\varphi^2\) robust gate |
| 80 τ window + `np.clip(±8)` | 2000 τ, no clip, lock requires no escape beyond \(B_{p2}\) |
| ideal inductor (\(r_0=0\)) | Branch L \(r_0=\sqrt{(1+|S_{EM}|\alpha)^2-1}\sqrt{L/C_2}=18.44\,\Omega\), \(\gamma=0.15087\) |

Gates (6 IC seeds, 2000 τ, amplitude-checked):

| \(\sigma\) | \(R_c\) | lock rate |
|-----------:|--------:|----------:|
| 0 | open | 0 |
| 0.9 | 20.0 kΩ | 0 (escaped) |
| 1 | 18.0 kΩ | 0 (escaped) |
| 1.525 | 11.80 kΩ | 1 (sweep threshold; predicted 1.4897) |
| \(\varphi\) | 11.12461 kΩ | 1 (demoted) |
| \(\varphi^2\) | **6.875 kΩ** | **1** (robust gate) |

BOM catalog residual at Electromagnetism (\(f=0.0004\)): **0.0382%** (AEB2AD).

Build the triangle; test 20 kΩ (no lock), 6.88 kΩ (lock), and sweep for the 12.08 kΩ threshold. That is the experiment.

## Applied-repo pattern this lab copies

| Repo | What we reuse |
|------|----------------|
| FSOT-2.1-Lean | pin, scalar, EM domain, ESP32 observer, circuit catalog |
| FSOT-GPU | collapse \(\Theta\), trinary pack, no softmax |
| FSOT-Quantum | \(\kappa_{ij}\) coupling, trit = spin |
| FSOT-Genetics | residual \(1+\lvert S\rvert P_{\mathrm{NEW}}\), trit_not |
| fsot-neuron-zig | bare-metal / QEMU doctrine, honest unknown |

## Kill criteria

1. Pin SHA-256 of `fsot_compute.py` does not start with `AEB2AD`.
2. Linear \(f_{\mathrm{LC}}\) not in 1–10 kHz (ESP32 ADC envelope).
3. Biased \(V_{C1}\) leaves 0–3.3 V.
4. \(\sigma=0\) trajectory is not chaotic (no double-scroll amplitude).
5. Strong coupling never locks; or lock \(\sigma\) requires a fitted coefficient.
