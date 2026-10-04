#!/bin/sh
# Take screenshots of the running site (home + add-event, phone/desktop, light/dark) into design/screenshots/
# usage: design/shoot.sh <name-prefix> [https://live-site]   (without a URL: the local site, which must be running)
cd "$(dirname "$0")/.." && docker run --rm --network pdx-fusion_default -v "$PWD/design/shoot.py:/shoot.py:ro" -v "$PWD/design/screenshots:/out" mcr.microsoft.com/playwright/python:v1.49.1-noble sh -c 'pip install -q playwright==1.49.1 >/dev/null 2>&1 && python /shoot.py "$0" "$1"' "${1:-shot}" "${2:-}"
