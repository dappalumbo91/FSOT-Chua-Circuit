#!/bin/bash
# (a)/(b) numerics of the sigma_c gap at r0_FSOT (default model). Outputs in results/.
set -e
cd "$(dirname "$0")/.."
E=./build/eb; R=results
$E msf sig=1.40:1.60:0.001 T=20000 nic=16 dt=0.005 > $R/msf_fine_T20000_dt005.tsv
$E msf sig=1.40:1.60:0.001 T=20000 nic=8 dt=0.0025 > $R/msf_fine_T20000_dt0025.tsv
$E msf sig=1.40:1.60:0.001 T=20000 nic=8 dt=0.005 trans=2000 > $R/msf_fine_T20000_trans2000.tsv
$E ringeig sig=1.40:1.60:0.02 T=3000 > $R/ringeig.tsv
$E ring sig=1.45:1.60:0.001 seeds=48 > $R/ring_fine_base.tsv
$E ring sig=1.45:1.60:0.0025 seeds=48 dt=0.0025 > $R/ring_dt0025.tsv
$E ring sig=1.45:1.60:0.0025 seeds=48 T=8000 tail=2000 > $R/ring_T8000.tsv
$E ring sig=1.45:1.60:0.0025 seeds=48 tail=200 > $R/ring_tail200.tsv
$E ring sig=1.45:1.60:0.0025 seeds=48 madcut=0.2360679774997897 > $R/ring_madcut_phi-3.tsv
$E ring sig=1.45:1.60:0.0025 seeds=48 madcut=0.0901699437494742 > $R/ring_madcut_phi-5.tsv
$E ring sig=1.45:1.60:0.0025 seeds=48 tritcut=0.9 > $R/ring_tritcut_0.9.tsv
$E ring sig=1.45:1.60:0.0025 seeds=48 ampcheck=0 > $R/ring_noampcheck.tsv
$E basin sig=1.40:1.60:0.005 eps=1e-6,1e-4,1e-2,0.1,0.3,1,3 seeds=24 > $R/basin.tsv
$E sens params=gamma,a,b,c,x2,alpha,beta rel=0.02 nic=8 T=10000 sig=1.38:1.62:0.004 > $R/sens_msf.tsv
echo NUMERICS_DONE
