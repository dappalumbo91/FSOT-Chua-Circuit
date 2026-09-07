# Firmware status

| Path | In gauntlet? | Status |
|------|----------------|--------|
| `host_observer.py` | Yes | PC twin of serial frames + trit collapse |
| `micropython/main.py` | No | Fast bench if MicroPython is already on the DevKit |
| `esp32_rlc_observer/` (Rust `no_std`) | **No** | Source for ESP32-WROOM-32. Needs the Xtensa/espup toolchain. **Not compiled in CI.** |

The math gate does not wait on a successful `espflash`. Flash is a hardware bring-up step (`docs/NEXT.md`).

Do not treat a firmware compile failure as a pin failure. Do not treat a successful flash as a lock proof — UART `FSOT_RLC_LOCK` on the triangle at 11.12 kΩ is that proof.
