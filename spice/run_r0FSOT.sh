#!/bin/bash
cd "$(dirname "$0")"
r=18.4400497592861384
NP=4 python3 run_ring.py ideal $r 2000 out/ring_ideal_r0_18.44.jsonl 1.46 1.47 1.48 1.49 1.50 1.51 1.52 1.53 1.54 1.618033988749895
NP=4 python3 run_ring.py tl082 $r 2000 out/ring_tl082_r0_18.44.jsonl 1.40 1.425 1.45 1.475 1.50 1.525 1.55 1.618033988749895
echo SPICE_R0FSOT_DONE
