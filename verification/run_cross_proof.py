#!/usr/bin/env python3
"""Independent multi-prover gauntlet for FSOT-Circuit.

This application does not inherit FSOT-2.1-Lean hub overall_ok.
Every layer here is re-run on THIS tree.

  python verification/run_cross_proof.py
  python verification/run_cross_proof.py --fast   # skip ODE sweep
"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

REPORT = ROOT / "results" / "cross_proof_report.json"


def run(cmd: list[str], cwd: Path | None = None, timeout: int = 120) -> tuple[int, str]:
    try:
        p = subprocess.run(
            cmd,
            cwd=str(cwd or ROOT),
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        out = (p.stdout or "") + (p.stderr or "")
        return p.returncode, out[-4000:]
    except FileNotFoundError as e:
        return 127, str(e)
    except subprocess.TimeoutExpired:
        return 124, "timeout"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--fast", action="store_true", help="skip Chua ODE sweep")
    args = ap.parse_args()

    layers = []

    def record(name: str, required: bool, rc: int, detail: str) -> None:
        ok = rc == 0
        status = "PASS" if ok else ("SKIP" if rc == 127 and not required else "FAIL")
        if rc == 127 and required:
            status = "FAIL"
        layers.append(
            {
                "name": name,
                "required": required,
                "ok": ok or (status == "SKIP"),
                "status": status,
                "returncode": rc,
                "detail": detail[-1500:],
            }
        )
        print(f"[{status}] {name}")
        if detail and status != "PASS":
            print(detail[-800:])

    # A — pin + algebra
    rc, out = run([sys.executable, str(ROOT / "tests" / "test_algebra.py")])
    record("python_algebra_pin", True, rc, out)

    rc, out = run([sys.executable, str(ROOT / "firmware" / "host_observer.py")])
    host_ok = rc == 0 and "FSOT_RLC_PIN=D1D38A" in out
    record("python_host_observer", True, 0 if host_ok else rc or 1, out)

    # B — ODE application gates
    if args.fast:
        record("python_chua_sweep", True, 0, "skipped --fast")
        layers[-1]["status"] = "SKIP"
        layers[-1]["ok"] = True
    else:
        rc, out = run([sys.executable, "-m", "sim.run_sim"], timeout=180)
        record("python_chua_sweep", True, rc, out)

    rc, out = run([sys.executable, str(ROOT / "verification" / "verify_circuit.py")])
    record("python_obligations", True, rc, out)

    # SMT-class bounds (always; no hub path)
    rc, out = run([sys.executable, str(ROOT / "verification" / "smt_replay.py")])
    record("smt_python_bounds", True, rc, out)

    z3 = shutil.which("z3")
    if not z3:
        for cand in (
            ROOT / "tools" / "z3" / "z3.exe",
            ROOT / "tools" / "z3" / "z3",
        ):
            if cand.is_file():
                z3 = str(cand)
                break
    if z3:
        rc, out = run([z3, str(ROOT / "verification" / "circuit_bounds.smt2")])
        smt_ok = rc == 0 and "sat" in out and "unsat" not in out.split()[:3]
        record("smt_z3", True, 0 if smt_ok else 1, out)
    else:
        record("smt_z3", False, 127, "z3 not on PATH (CI installs it; python bounds still required)")

    # Lean
    lake = shutil.which("lake")
    lean = shutil.which("lean")
    if lake:
        rc, out = run([lake, "build"], timeout=180)
        record("lean_lake_build", True, rc, out)
    elif lean:
        rc, out = run([lean, str(ROOT / "FSOTCircuit" / "ArrayPriors.lean")], timeout=120)
        record("lean_file", True, rc, out)
    else:
        record("lean", True, 127, "lake/lean not on PATH")

    # Coq / Rocq
    coqc = shutil.which("coqc")
    if coqc:
        rc, out = run([coqc, "-Q", ".", "FSOTCircuit", "CircuitArray.v"], cwd=ROOT / "formal" / "coq", timeout=120)
        record("coq_circuit_array", True, rc, out)
    else:
        record("coq_circuit_array", True, 127, "coqc not on PATH")

    # Rust host kernel
    cargo = shutil.which("cargo")
    if cargo:
        rc, out = run(
            [cargo, "run", "--quiet", "--release"],
            cwd=ROOT / "verification" / "rust_circuit_kernel",
            timeout=180,
        )
        rust_ok = rc == 0 and "FSOT_CIRCUIT_RUST_OK" in out
        record("rust_host_kernel", True, 0 if rust_ok else rc or 1, out)
    else:
        record("rust_host_kernel", True, 127, "cargo not on PATH")

    # TLA+ TLC
    jar = ROOT / "tools" / "tla" / "tla2tools.jar"
    java = shutil.which("java")
    if java and jar.is_file():
        rc, out = run(
            [java, "-cp", str(jar), "tlc2.TLC", "-config", "CircuitArray.cfg", "CircuitArray.tla"],
            cwd=ROOT / "formal" / "tla",
            timeout=120,
        )
        tlc_ok = rc == 0 and "No error has been found" in out
        record("tla_tlc", True, 0 if tlc_ok else 1, out)
    else:
        record("tla_tlc", False, 127, "java or tla2tools.jar missing")

    # Isabelle — optional until present
    isabelle = shutil.which("isabelle")
    if isabelle:
        rc, out = run([isabelle, "process", "-T", "CircuitArray"], cwd=ROOT / "formal" / "isabelle", timeout=180)
        record("isabelle", False, rc, out)
    else:
        record("isabelle", False, 127, "isabelle not on PATH (optional until installed)")

    required_fail = [L for L in layers if L["required"] and L["status"] == "FAIL"]
    doc = {
        "application": "FSOT-Circuit",
        "inherits_hub_overall_ok": False,
        "fast": bool(args.fast),
        "layers": layers,
        "required_fail_count": len(required_fail),
        "overall_ok": len(required_fail) == 0,
    }
    REPORT.parent.mkdir(exist_ok=True)
    REPORT.write_text(json.dumps(doc, indent=2), encoding="utf-8")
    print("=" * 60)
    print(f"overall_ok={doc['overall_ok']}  required_fail={len(required_fail)}  layers={len(layers)}")
    print("wrote", REPORT)
    return 0 if doc["overall_ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
