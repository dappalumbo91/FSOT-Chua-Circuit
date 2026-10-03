"""MicroPython bench observer for the 3-node RLC array.

Flash only if you want a fast ADC bring-up. Authority firmware is the
Rust no_std crate in firmware/esp32_rlc_observer/. Constants match
FSOT-2.1-Lean vendor/fsot_compute.py, pin AEB2AD (re-vendored 2026-10-03).

LOCK (corrected): over a window of 1024 samples, trit agreement >= 1/phi AND every |V_C1| < Bp2 = 230/33 V.
Without the amplitude condition, a ring that escaped to the outer limit cycle (+-7.35 V, all nodes
synchronised there) reads as LOCK; that is what the 20 kOhm setting does with the corrected NIC model.
"""

from machine import ADC, Pin, UART
import time

# Frozen kernel constants (same as firmware/esp32_rlc_observer/src/scalar.rs).
C_EFF = 0.9577480213378242
P_VAR = 0.9579871226722757
THETA = C_EFF * P_VAR  # 0.9175102712064876
S_EM = 0.9557285700955828  # Electromagnetism (D_eff 7, look 1); |S| > THETA -> scalar trit +1
VDD = 3.3
MID = 1.65          # bias: Rs 300k from V_C1, Rp 100k to 3V3, Rg 150k to GND
GAIN = 1.0 / 6.0    # v_adc = 1.65 + V_C1/6 (sim/adc_model.py)
BP = 1.0
BP2 = 230.0 / 33.0  # outer NIC breakpoint (V)
PHI_INV = 0.6180339887498949
LOCK_WINDOW = 1024

PINS = (34, 35, 32)
adcs = [ADC(Pin(p)) for p in PINS]
for a in adcs:
    try:
        a.atten(ADC.ATTN_11DB)
        a.width(ADC.WIDTH_12BIT)
    except Exception:
        pass

led = Pin(2, Pin.OUT)
uart = UART(0, baudrate=115200)


def decode(raw):
    volts = raw / 4095.0 * VDD
    return (volts - MID) / GAIN


def trit(v):
    if v < -BP:
        return -1
    if v > BP:
        return 1
    return 0


frame = 0
win_n = win_agree = 0
win_max = 0.0
lock = amp_ok = False
last_agree = last_max = 0.0
while True:
    codes = [a.read() for a in adcs]
    volts = [decode(c) for c in codes]
    trits = [trit(v) for v in volts]
    win_n += 1
    win_agree += 1 if len(set(trits)) == 1 else 0
    win_max = max(win_max, max(abs(v) for v in volts))
    if win_n == LOCK_WINDOW:
        last_agree, last_max = win_agree / LOCK_WINDOW, win_max
        amp_ok = win_max < BP2
        lock = last_agree >= PHI_INV and amp_ok
        win_n = win_agree = 0
        win_max = 0.0
    if frame % 50 == 0:
        uart.write("FSOT_RLC_FRAME_START frame=%d\n" % frame)
        uart.write("FSOT_RLC_S=%.17f\n" % S_EM)
        uart.write("FSOT_RLC_THETA=%.17f\n" % THETA)
        uart.write("FSOT_RLC_LOCK=%d\n" % (1 if lock else 0))
        uart.write("FSOT_RLC_AMP_OK=%d max_abs_v=%.3f bp2_v=%.3f\n" % (1 if amp_ok else 0, last_max, BP2))
        uart.write("FSOT_RLC_TRIT_AGREE=%.4f\n" % last_agree)
        for i, (c, v, t) in enumerate(zip(codes, volts, trits)):
            uart.write("FSOT_RLC_NODE|%d|%d|%.6f|%d\n" % (i, c, v, t))
        uart.write("FSOT_RLC_FRAME_END frame=%d\n" % frame)
    led.value(1 if lock and trits[0] == 1 else 0)
    frame += 1
    time.sleep_us(100)
