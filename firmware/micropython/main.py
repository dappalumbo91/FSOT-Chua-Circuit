"""MicroPython bench observer for the 3-node RLC array.

Flash only if you want a fast ADC bring-up. Authority firmware is the
Rust no_std crate in firmware/esp32_rlc_observer/. Constants match
FSOT-2.1-Lean rust kernel (D1D38A).
"""

from machine import ADC, Pin, UART
import time

# Frozen kernel constants (same as firmware/esp32_rlc_observer/src/scalar.rs).
C_EFF = 0.9577022026205613
P_VAR = 0.9579871226722757
THETA = C_EFF * P_VAR
S_EM = 0.518866  # Electromagnetism; host recomputes live from vendor pin
VDD = 3.3
MID = 1.65
GAIN = 0.5
BP = 1.0

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
while True:
    codes = [a.read() for a in adcs]
    volts = [decode(c) for c in codes]
    trits = [trit(v) for v in volts]
    lock = len(set(trits)) == 1
    if frame % 50 == 0:
        uart.write("FSOT_RLC_FRAME_START frame=%d\n" % frame)
        uart.write("FSOT_RLC_S=%.17f\n" % S_EM)
        uart.write("FSOT_RLC_THETA=%.17f\n" % THETA)
        uart.write("FSOT_RLC_LOCK=%d\n" % (1 if lock else 0))
        for i, (c, v, t) in enumerate(zip(codes, volts, trits)):
            uart.write("FSOT_RLC_NODE|%d|%d|%.6f|%d\n" % (i, c, v, t))
        uart.write("FSOT_RLC_FRAME_END frame=%d\n" % frame)
    led.value(1 if lock and trits[0] == 1 else 0)
    frame += 1
    time.sleep_us(100)
