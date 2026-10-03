#!/bin/bash
set -e
cd "$(dirname "$0")/.."
M=./build/mc; R=results
r0=18.4400497592861384
$M mc n=300 seed=11 tolR=0.01 tolC=0.05 tolL=0.10 rlo=$r0 > $R/mc_A_R1C5L10_rFSOT.tsv
$M mc n=300 seed=12 tolR=0.05 tolC=0.10 tolL=0.20 rlo=$r0 > $R/mc_B_R5C10L20_rFSOT.tsv
$M mc n=300 seed=13 tolR=0.01 tolC=0.05 tolL=0.10 tolE=0.05 rlo=$r0 > $R/mc_C_R1C5L10E5_rFSOT.tsv
$M mc n=300 seed=14 tolR=0.01 tolC=0.05 tolL=0.10 rlo=17.3 rhi=22 > $R/mc_D_R1C5L10_TSLcombo.tsv
$M mc n=300 seed=15 tolR=0.05 tolC=0.10 tolL=0.20 rlo=0 rhi=22 > $R/mc_E_R5C10L20_r0to22.tsv
$M mc n=200 seed=16 tolR=0.01 tolC=0.05 tolL=0.10 rlo=43.23 rhi=55 > $R/mc_F_R1C5L10_Wurth.tsv
$M mc n=80 seed=17 tolR=0.01 tolC=0.05 tolL=0.10 rlo=$r0 ring=1 > $R/mc_ringA_hetero.tsv
$M mc n=80 seed=18 tolR=0.05 tolC=0.10 tolL=0.20 rlo=$r0 ring=1 > $R/mc_ringB_hetero.tsv
$M mc n=40 seed=19 tolR=0 tolC=0 tolL=0 rlo=$r0 ring=1 hetero=0 > $R/mc_ring_nominal.tsv
echo MC_DONE
