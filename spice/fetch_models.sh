#!/usr/bin/env bash
# Fetch third-party op-amp macromodels (NOT committed: vendor licence terms are not an explicit
# redistribution grant). Verifies SHA-256 so every run uses byte-identical models.
set -euo pipefail
mkdir -p "$(dirname "$0")/models/vendor"
cd "$(dirname "$0")/models/vendor"
# 1) TI TL082 PSpice macromodel, SLOJ070.ZIP (product page https://www.ti.com/product/TL082 -> Design & development -> PSpice model)
curl -fsSL -o sloj070.zip https://www.ti.com/lit/zip/sloj070
echo "4f27e17a7ceabebf61edddca7b7e187830c1924af417c40811255a8f3a879937  sloj070.zip" | sha256sum -c -
mkdir -p ti_sloj070 && unzip -o -q sloj070.zip -d ti_sloj070
echo "adad2e131f728610963e0797670ea34d2857c0b26b3f49c6ce356a3213d89011  ti_sloj070/TL082.301" | sha256sum -c -
# 2) uA741 macromodel (TI "Parts release 4.01, 07/05/89" Boyle model) as mirrored by KiCad-Spice-Library
#    https://github.com/kicad-spice-library/KiCad-Spice-Library/blob/master/Models/Manufacturer/Texas%20Instruments/ua741.mod
curl -fsSL -o ua741.mod "https://raw.githubusercontent.com/kicad-spice-library/KiCad-Spice-Library/master/Models/Manufacturer/Texas%20Instruments/ua741.mod"
echo "75693f527a364af59a5b5ebf72e8bff1a2efee98ce2de83c541fa4a3604e9505  ua741.mod" | sha256sum -c -
echo "models OK"
