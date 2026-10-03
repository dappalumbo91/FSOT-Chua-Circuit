#!/bin/bash
# diagnostic (post-lock): sigma_c vs GBW at r0=18.44, lag only (no slew), nic=4 T=3000
cd "$(dirname "$0")/.."; while pgrep -x run_opamp2.sh >/dev/null || [ -n "$(ps -eo args | grep '^/bin/bash tools/run_opamp2.sh')" ]; do sleep 20; done
for g in 2e6 3e6 4e6 5.25e6 8e6 12e6; do echo "gbw_$g r0=18.4400497592861384 sig=1.25:1.60:0.0125 gbw=$g"; done | xargs -P 2 -L 1 bash -c 'n=$0; ./build2/rf msf "$@" nic=4 T=3000 > results/opamp/$n.txt'
echo GBW_DONE
