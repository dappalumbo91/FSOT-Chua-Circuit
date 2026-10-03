"""ESP32 12-bit ADC behind a 3-resistor bias network (corrected 2026-10-03).

Network per node: V_C1 --Rs 300k--+--> GPIO;  +--Rp 100k--> 3V3;  +--Rg 150k--> GND.
Superposition: v = V_C1 * (Rp||Rg)/(Rs + Rp||Rg) + 3.3 * (Rs||Rg)/(Rp + Rs||Rg)
             = V_C1/6 + 1.65   (exact for 300k/100k/150k).

Why 1/6 and not the old 100k/100k map (which claimed 1.65 + V/2 but actually gives 1.1 + V/3):
the LOCK amplitude check must SEE an escape to the outer limit cycle (|V_C1| ~ 7.35 V > Bp2 = 6.97 V).
That needs 1.65 + 7.35 G <= 3.3, so G <= 0.2245. G = 1/6 maps the double scroll (|V| <= 4.33 V) to
0.93-2.37 V (the ESP32 11 dB linear zone) and the outer cycle to 0.43-2.88 V (inside the rails).
Load on the node: Thevenin 360 kOhm to 1.98 V (simulated in cpp/, no effect on the gates).
"""

from __future__ import annotations

import numpy as np

VDD = 3.3
RS, RP, RG = 300e3, 100e3, 150e3


def _par(a: float, b: float) -> float:
    return a * b / (a + b)


GAIN = _par(RP, RG) / (RS + _par(RP, RG))          # 1/6
MID = VDD * _par(RS, RG) / (RP + _par(RS, RG))      # 1.65 V
R_THEVENIN = RS + _par(RP, RG)                      # 360 kOhm seen by V_C1
V_THEVENIN = VDD * RG / (RP + RG)                   # 1.98 V
ADC_BITS = 12
ADC_MAX = (1 << ADC_BITS) - 1


def vc1_to_adc_volts(vc1: np.ndarray) -> np.ndarray:
    return np.clip(MID + GAIN * vc1, 0.0, VDD)


def encode(vc1: np.ndarray) -> np.ndarray:
    volts = vc1_to_adc_volts(vc1)
    return np.clip(np.rint(volts / VDD * ADC_MAX), 0, ADC_MAX).astype(np.int32)


def decode(code: np.ndarray) -> np.ndarray:
    volts = code.astype(float) * VDD / ADC_MAX
    return (volts - MID) / GAIN


def quantize(vc1: np.ndarray) -> np.ndarray:
    return decode(encode(vc1))
