#!/bin/bash
# reduced queue (time budget): SPICE-comparable r0 for TL082 variants + 741, then post-lock GBW diagnostic (lag only, no slew)
cd "$(dirname "$0")/.."
:
{
echo "tl082_r20 r0=20 sig=1.22:1.52:0.0125 gbw=3e6 sr=8"
echo "tl082_r35 r0=35 sig=0.90:1.30:0.0125 gbw=3e6 sr=8"
echo "ideal_r20 r0=20 sig=1.22:1.52:0.0125"
echo "ideal_r35 r0=35 sig=0.90:1.30:0.0125"
echo "gbw_2e6 r0=18.4400497592861384 sig=1.25:1.60:0.0125 gbw=2e6"
echo "gbw_3e6 r0=18.4400497592861384 sig=1.25:1.60:0.0125 gbw=3e6"
echo "gbw_5.25e6 r0=18.4400497592861384 sig=1.25:1.60:0.0125 gbw=5.25e6"
echo "ua741_k1_r0 r0=0 sig=1.6:2.3:0.02 gbw=1e6 sr=0.5"
echo "tl082h_r20 r0=20 sig=1.22:1.52:0.0125 gbw=5.25e6 sr=20"
echo "tl082h_r35 r0=35 sig=0.90:1.30:0.0125 gbw=5.25e6 sr=20"
} | xargs -P 2 -L 1 bash -c 'n=$0; ./build2/rf msf "$@" nic=4 T=3000 > results/opamp/$n.txt'
echo OPAMP3_DONE
