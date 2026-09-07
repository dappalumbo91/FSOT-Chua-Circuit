# Math map — PDF hardware onto the FSOT pin

Authority: [FSOT-2.1-Lean](https://github.com/dappalumbo91/FSOT-2.1-Lean) `vendor/fsot_compute.py` pin **D1D38A**. Zero free parameters.

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
| Analog RLC / Chua / voltages | Electromagnetism | 9 | currents, fields, ADC rails |
| Passives BOM (C dielectric, L core) | Materials_Science | 10 | catalog emergence panel |
| Acoustic / Chladni / Faraday (PDF p.2) | Acoustics | 10 | nodal fields, later lab |
| ESP32 platform rails | Electromagnetism (panel D=12 in Lean priors) | 9 live / 12 panel | `Esp32PlatformEngineeringPanelPriors` |

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

Identical nodes: \(D_i=D_j=9\). Dimensionless Chua coupling:

\[
\sigma = \alpha R / R_c,\qquad \alpha=C_2/C_1.
\]

The 3% residual was a **wrong object**, not a missing coefficient.

| Wrong (3%) | Right (gates `overall_ok`) |
|------------|----------------------------|
| 1-D chain (ends ≠ middle) | **Ring / triangle** — every node degree 2 |
| Matsumoto \(a,b=-1.143,-0.714\) | **BOM NIC** \(G_a=-1/2.2\mathrm{k}-1/3.3\mathrm{k}\), \(G_b=-1/3.3\mathrm{k}\) |
| `LOCK_ORDER = 0.85` | trit \(\ge \varphi^{-1}\), MAD/amp \(\le \varphi^{-4}\) (hardware working-set law) |
| \(\sigma_c=\alpha/\varphi\) after the sweep | **Operating point \(\sigma=\varphi\)** a priori |

Gates (6 IC seeds):

| \(\sigma\) | \(R_c\) | lock rate |
|-----------:|--------:|----------:|
| 0 | open | 0 |
| 1 | 18.0 kΩ | 0 |
| \(\varphi\) | **11.12461 kΩ** | **1** |
| \(\varphi^2\) | 6.875 kΩ | 1 |

BOM catalog residual at Electromagnetism (\(f=0.0004\)): **0.0208%**.

Build the triangle with three pots DMM-set to 11.12 kΩ. That is the experiment.

## Applied-repo pattern this lab copies

| Repo | What we reuse |
|------|----------------|
| FSOT-2.1-Lean | pin, scalar, EM domain, ESP32 observer, circuit catalog |
| FSOT-GPU | collapse \(\Theta\), trinary pack, no softmax |
| FSOT-Quantum | \(\kappa_{ij}\) coupling, trit = spin |
| FSOT-Genetics | residual \(1+\lvert S\rvert P_{\mathrm{NEW}}\), trit_not |
| fsot-neuron-zig | bare-metal / QEMU doctrine, honest unknown |

## Kill criteria

1. Pin SHA-256 of `fsot_compute.py` does not start with `D1D38A`.
2. Linear \(f_{\mathrm{LC}}\) not in 1–10 kHz (ESP32 ADC envelope).
3. Biased \(V_{C1}\) leaves 0–3.3 V.
4. \(\sigma=0\) trajectory is not chaotic (no double-scroll amplitude).
5. Strong coupling never locks; or lock \(\sigma\) requires a fitted coefficient.
