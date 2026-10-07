#!/bin/sh
# Builds the app you open on your computer (Takewise.html) from the page source (src/takewise.html).
set -e
cd "$(dirname "$0")"
{ printf '<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover"><style>[hidden]{display:none!important}</style></head><body>\n'; cat src/takewise.html; printf '\n</body></html>\n'; } > Takewise.html
echo "Built Takewise.html"
