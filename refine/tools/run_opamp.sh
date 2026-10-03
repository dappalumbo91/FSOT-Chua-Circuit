#!/bin/bash
cd "$(dirname "$0")/.."; F=./build/rf; R=results/opamp; mkdir -p $R
for r0 in 0 18.4400497592861384 20 35; do
  case $r0 in 0) S=1.95:2.45:0.005;; 35) S=0.85:1.35:0.005;; *) S=1.25:1.75:0.005;; esac
  t=${r0%%.*}
  $F msf r0=$r0 sig=$S nic=4 > $R/ideal_r$t.txt
  $F msf r0=$r0 sig=$S nic=4 gbw=3e6 sr=8 > $R/tl082_r$t.txt
  $F msf r0=$r0 sig=$S nic=4 gbw=5.25e6 sr=20 > $R/tl082h_r$t.txt
  $F msf r0=$r0 sig=$S nic=4 gbw=1e6 sr=0.5 > $R/ua741_k1_r$t.txt
  $F msf r0=$r0 sig=$S nic=4 gbw=1e6 sr=0.5 k=10 > $R/ua741_k10_r$t.txt
  $F msf r0=$r0 sig=$S nic=4 e_add=0.01024447208849228 > $R/branchN_ideal_r$t.txt
  $F msf r0=$r0 sig=$S nic=4 gbw=3e6 sr=8 e_add=0.01024447208849228 > $R/branchN_tl082_r$t.txt
  $F msf r0=$r0 sig=$S nic=4 gbw=3e6 sr=8 e_add=7.86e-7 > $R/ledgerB_gbw_tl082_r$t.txt
done
echo OPAMP_DONE
