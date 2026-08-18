from pathlib import Path
D = str(Path(__file__).resolve().parents[1] / "data") + "/"
import json, urllib.request

BASE = "https://www.ifeed.cc/api/discovery/feeds?page={}&pageSize=100"
rows = {}
for p in range(1, 120):
    req = urllib.request.Request(BASE.format(p), headers={"accept": "application/json"})
    with urllib.request.urlopen(req, timeout=30) as r:
        d = json.load(r)
    c = d.get("content", [])
    if not c:
        break
    for it in c:
        rows[it["feedId"]] = it
    print("page", p, "got", len(c), "cum", len(rows), flush=True)

out = list(rows.values())
json.dump(out, open(D + "feeds.json", "w"), ensure_ascii=False)
print("TOTAL", len(out))
print("KEYS", list(out[0].keys()))
