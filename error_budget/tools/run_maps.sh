#!/bin/bash
set -e
cd "$(dirname "$0")/.."
E=./build/eb; R=results
$E map1 p1=gamma,0,0.5,41 p2=beta,8,22,29 T=1000 > $R/map_gamma_beta.tsv
$E map1 p1=ba,0.2,1.0,33 p2=alpha,6,16,41 T=1000 > $R/map_ba_alpha.tsv
$E map1 p1=x2,2,10,33 p2=gamma,0,0.5,26 T=1000 > $R/map_x2_gamma.tsv
$E msfmap p1=gamma,0,0.4,21 p2=alpha,7,13,25 sig=0:4:0.05 T=1500 > $R/msfmap_gamma_alpha.tsv
$E msfmap p1=gamma,0,0.4,21 p2=ba,0.35,0.75,21 sig=0:4:0.05 T=1500 > $R/msfmap_gamma_ba.tsv
$E mapnet Ns=3,4,5,6 topos=ring,all sig=0:5:0.1 seeds=8 > $R/mapnet_N_topo.tsv
for g in 0.10 0.2132923944; do $E mapnet gamma=$g Ns=3,4,5,6 topos=ring,all sig=0:5:0.1 seeds=8 > $R/mapnet_N_topo_gamma$g.tsv; done
echo MAPS_DONE
