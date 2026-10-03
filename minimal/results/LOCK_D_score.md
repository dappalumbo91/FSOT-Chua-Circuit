# LOCK D1/D2 scorecard (scored after both locks; ngspice uses the TI TL082 macro-model (SLOJ070) and the 1N4148 model, with the classifier "chaotic if V(o3) has more than 40 distinct maxima")

| ID | blind? | locked prediction | ngspice result | verdict |
|---|---|---|---|---|
| D-0 edge at 27 °C | NO (already known) | 3100 Ω | 3080 Ω | consistent (within ±40 Ω) |
| D-T0 edge shift at 0 °C | YES | −50 Ω | −40 Ω (edge 3040) | **CONFIRMED** (band [−90, −10]) |
| D-T60 edge shift at 60 °C | YES | +40 Ω | +50 Ω (edge 3130) | **CONFIRMED** (band [0, +80]) |
| D-V12 edge shift at ±12 V | YES | −40 Ω | −20 Ω (edge 3060) | **CONFIRMED** (band [−80, 0]) |
| K-1 FSOT knob R_A = R/γ_rel = 4205 Ω (and 4.22 kΩ) | YES | not chaotic; rail latch | x pinned to 3.97–7.48 V, 1 distinct maximum, 360 Hz ripple: rail latch | **CONFIRMED**. The FSOT-derived knob does **not** give chaos |
| K′-1 R_A = 2744 Ω (A = \|S_med\|) | YES | periodic; f = 876 Hz ±3 %; x in [−1.62, 1.35] V | periodic (2 distinct maxima); f = 872 Hz; x in [−1.62, 1.37] V | **CONFIRMED** (periodic, not chaotic) |

Bottom line:
- Branch D, standard Shockley junction physics with zero free parameters, correctly predicted the sign and size of three blind edge shifts.
- Both FSOT-derived knob candidates (γ_rel and |S_med|) were correctly predicted to be **non-chaotic**.
- So no FSOT-derived R_A puts this circuit in chaos. The chaotic band (ngspice 3080 to about 3400 Ω with windows; Branch D 3100–3490 Ω) is a circuit-physics result, not an FSOT result.
