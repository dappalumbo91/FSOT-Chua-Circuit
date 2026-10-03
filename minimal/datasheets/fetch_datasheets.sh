#!/bin/sh
# Fetch the datasheets referenced by LOCK DJ, verify their checksums, and render the Vishay page used by digitize_fig1.py (needs poppler-utils + python3-pil).
set -e
cd "$(dirname "$0")"
curl -sL -A "Mozilla/5.0" -o 1n4148.pdf https://www.vishay.com/docs/81857/1n4148.pdf
curl -sL -A "Mozilla/5.0" -o ds30086.pdf https://www.diodes.com/assets/Datasheets/ds30086.pdf
sha256sum -c <<SUMS
aefe85400a427ed886a4e1c88205ceabb9f9b38044b29c6acee4bb00146a44b7  1n4148.pdf
39c16a6888bdab22418e93e17182174aad763a66957a4632e70c944194e3fc08  ds30086.pdf
SUMS
pdftoppm -f 2 -l 2 -r 400 -png 1n4148.pdf hi
python3 -c "from PIL import Image; im=Image.open('hi-2.png'); W,H=im.size; im.crop((int(W*0.08),int(H*0.37),int(W*0.42),int(H*0.58))).save('fig1.png')"
python3 digitize_fig1.py
