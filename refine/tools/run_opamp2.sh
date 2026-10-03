#!/bin/bash
# fast op-amp sweep: 21-26 tangents around the expected root, T=3000, 4 ICs; 2 jobs in parallel
cd "$(dirname "$0")/.."; R=results/opamp; mkdir -p $R
EADD=0.01024447208849228
jobs() {
for r0 in 18.4400497592861384 0 20 35; do
  case $r0 in 0) S=2.00:2.30:0.0125;; 35) S=0.90:1.30:0.0125;; 20) S=1.22:1.52:0.0125;; *) S=1.25:1.55:0.0125;; esac
  t=${r0%%.*}
  echo "ideal_r$t r0=$r0 sig=$S"
  echo "tl082_r$t r0=$r0 sig=$S gbw=3e6 sr=8"
  echo "tl082h_r$t r0=$r0 sig=$S gbw=5.25e6 sr=20"
  echo "ua741_k1_r$t r0=$r0 sig=0.9:1.7:0.02 gbw=1e6 sr=0.5"
  echo "ua741_k10_r$t r0=$r0 sig=$S gbw=1e6 sr=0.5 k=10"
  echo "branchN_ideal_r$t r0=$r0 sig=$S e_add=$EADD"
  echo "branchN_tl082_r$t r0=$r0 sig=$S gbw=3e6 sr=8 e_add=$EADD"
done; }
jobs | xargs -P 2 -L 1 bash -c 'n=$0; ./build2/rf msf "$@" nic=4 T=3000 > results/opamp/$n.txt'
echo OPAMP_DONE
