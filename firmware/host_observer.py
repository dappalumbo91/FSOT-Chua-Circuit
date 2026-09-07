"""Host twin of the ESP32 RLC observer.

Same collapse law as firmware/esp32_rlc_observer (Θ = C_eff·P_var) and
the same serial frame names. Used by the simulator and by a live UART
decoder when the board is on the bench.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from sim.adc_model import decode  # noqa: E402
from sim.fsot_engine import (  # noqa: E402
    COLLAPSE_THRESHOLD,
    domain_scalar,
    snapshot,
    trinary_from_scalar,
    trinary_from_voltage,
)


def collapse_frame(codes: list[int], frame: int) -> dict:
    volts = [float(v) for v in decode(__import__("numpy").array(codes))]
    trits = [trinary_from_voltage(v).trit for v in volts]
    S = domain_scalar("Electromagnetism")
    scalar_trit = trinary_from_scalar(S)
    locked = len(set(trits)) == 1
    return {
        "frame": frame,
        "codes": codes,
        "volts": volts,
        "trits": trits,
        "lock": locked,
        "S": S,
        "scalar_trit": scalar_trit.trit,
        "theta": COLLAPSE_THRESHOLD,
    }


def emit_serial(doc: dict) -> str:
    lines = [
        f"FSOT_RLC_FRAME_START frame={doc['frame']}",
        f"FSOT_RLC_S={doc['S']:.17f}",
        f"FSOT_RLC_THETA={doc['theta']:.17f}",
        f"FSOT_RLC_SCALAR_TRIT={doc['scalar_trit']}",
        f"FSOT_RLC_LOCK={1 if doc['lock'] else 0}",
    ]
    for i, (c, v, t) in enumerate(zip(doc["codes"], doc["volts"], doc["trits"])):
        lines.append(f"FSOT_RLC_NODE|{i}|{c}|{v:.6f}|{t}")
    lines.append(f"FSOT_RLC_FRAME_END frame={doc['frame']}")
    return "\n".join(lines)


def main() -> None:
    snap = snapshot()
    print("FSOT RLC host observer")
    print(f"FSOT_RLC_PIN={snap['pin']}")
    print(f"FSOT_RLC_D_EFF={snap['D_eff']}")
    print(f"FSOT_RLC_S={snap['S_electromagnetism']:.17f}")
    print(f"FSOT_RLC_THETA={snap['collapse_threshold']:.17f}")
    demo = collapse_frame([2048, 2800, 1200], frame=0)
    print(emit_serial(demo))
    print(json.dumps({"demo": demo, "snapshot_ok": True}, indent=2))


if __name__ == "__main__":
    main()
