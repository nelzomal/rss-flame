#!/usr/bin/env bash
# Re-probe ifeed.cc/discover from scratch and regenerate index.html.
# Takes ~3 min, almost all of it waiting on 932 remote feeds.
set -euo pipefail
cd "$(dirname "$0")"
mkdir -p ../data

python3 1_fetch_catalog.py   # -> data/feeds.json    the catalogue, via the unauthenticated API
python3 2_probe.py           # -> data/probe.json    fetch every feed, record status + newest item
python3 3_formats.py         # -> data/formats.json  re-fetch the 200s, parse format/length/caching
python3 4_build.py           # -> data/flame_data.json
python3 5_render.py          # -> index.html

echo
echo "done — open index.html"
