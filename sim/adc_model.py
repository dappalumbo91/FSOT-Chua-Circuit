"""ESP32 12-bit ADC + 100 kΩ/100 kΩ bias network (Circuit PDF).

v_adc = clamp(1.65 + 0.5 · V_C1, 0, 3.3)
code  = round(v_adc / 3.3 · 4095)
"""

from __future__ import annotations

import numpy as np

VDD = 3.3
MID = 1.65
GAIN = 0.5  # ±2 V → 0.65 … 2.65 V
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
