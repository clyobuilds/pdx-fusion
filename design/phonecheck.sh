#!/bin/sh
# Check the add-event form on phone-sized screens (Chromium + WebKit). usage: design/phonecheck.sh [https://live-site]
cd "$(dirname "$0")/.." && docker run --rm --network pdx-fusion_default -v "$PWD/design/phonecheck.py:/t.py:ro" mcr.microsoft.com/playwright/python:v1.49.1-noble sh -c 'pip install -q playwright==1.49.1 >/dev/null 2>&1 && python /t.py "$0"' "${1:-}"
