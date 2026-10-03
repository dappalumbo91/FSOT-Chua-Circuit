#!/bin/bash
cd /workspace/FSOT-Chua-Circuit
for c in "python3 tests/test_algebra.py" "python3 verification/smt_replay.py" "python3 firmware/host_observer.py" "python3 verification/verify_circuit.py" "python3 verification/run_cross_proof.py" "ctest --test-dir cpp/build" "python3 falstad/verify_falstad.py"; do
  echo "=== $c"; $c > /tmp/t.out 2>&1; e=$?; tail -4 /tmp/t.out; echo "EXIT $e"; done
git checkout results/cross_proof_report.json 2>/dev/null; echo TESTS_DONE
