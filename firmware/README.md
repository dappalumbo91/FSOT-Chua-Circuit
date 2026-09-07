# Firmware

Authority firmware is **Rust no_std** on ESP32 classic (same embassy/esp-hal family as the hub observer, **this crate is independent**). See [`STATUS.md`](STATUS.md).

| Path | Role |
|------|------|
| `esp32_rlc_observer/` | Bare-metal ADC + FSOT scalar + trinary lock |
| `host_observer.py` | PC twin; same serial frames; used by the sim |
| `micropython/main.py` | Optional fast bench if MicroPython is already on the DevKit |

## Pins

| Node | GPIO | ADC |
|------|------|-----|
| A | 34 | ADC1_CH6, input only |
| B | 35 | ADC1_CH7, input only |
| C | 32 | ADC1_CH4 |
| LED | 2 | onboard (do not jumper) |

Input must already be biased to 0–3.3 V (`hardware/schematic.md`).

## Flash (Rust)

Requires the same Xtensa toolchain you used for the RF observer.

```powershell
cd firmware\esp32_rlc_observer
cargo build --release
espflash flash --monitor --chip esp32
```

## Host twin (no board)

```powershell
python firmware\host_observer.py
```

Serial grammar (both twins):

```
FSOT_RLC_FRAME_START frame=N
FSOT_RLC_S=...
FSOT_RLC_THETA=...
FSOT_RLC_SCALAR_TRIT=+1|0|-1
FSOT_RLC_LOCK=0|1
FSOT_RLC_NODE|i|code|volts|trit
FSOT_RLC_FRAME_END frame=N
```
