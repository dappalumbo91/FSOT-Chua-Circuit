#!/bin/bash
cd "$(dirname "$0")/.."; R=results
./build/rf lyap r0s=16.7:17.5:0.005 nic=3 T=20000 > $R/lyap_fine_w17.tsv
./build/rf lyap r0s=17.9:19.0:0.005 nic=3 T=20000 > $R/lyap_fine_1844.tsv
./build/rf lyap r0s=9.3:10.4:0.01 nic=3 T=20000 > $R/lyap_fine_w10.tsv
./build/rf peaks r0s=0:40:0.02 T=3000 > $R/peaks_wide.tsv
./build/rf peaks r0s=16.5:19.5:0.002 T=4000 > $R/peaks_fine.tsv
echo WIN_DONE
