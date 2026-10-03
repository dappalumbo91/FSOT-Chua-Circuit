# Firmware status

| Path | In gauntlet? | Status |
|------|----------------|--------|
| `host_observer.py` | Yes | PC twin of serial frames + trit collapse |
| `micropython/main.py` | No | Fast bench if MicroPython is already on the DevKit |
| `esp32_rlc_observer/` (Rust `no_std`) | **No** | Source for ESP32-WROOM-32. Needs the Xtensa/espup toolchain. **Not compiled in CI.** |

The math gate does not wait on a successful `espflash`. Flash is a hardware bring-up step (`docs/NEXT.md`).

Do not treat a firmware compile failure as a pin failure. Do not treat a successful flash as a lock proof — UART `FSOT_RLC_LOCK=1` with `FSOT_RLC_AMP_OK=1` at 6.88 kΩ, `LOCK=0` at 20 kΩ, and the threshold near 12.08 kΩ are that proof.
