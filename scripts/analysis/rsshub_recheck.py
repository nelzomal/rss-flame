from pathlib import Path
D = str(Path(__file__).resolve().parents[1] / "data") + "/"
import json, ssl, time, urllib.request, urllib.error
from urllib.parse import urlparse

F = json.load(open(D + "feeds.json"))
HOSTS = {"rsshub.ktachibana.party", "rsshub.rssforever.com", "rsshub.bestblogs.dev", "rss.xcancel.com"}
CTX = ssl.create_default_context(); CTX.check_hostname = False; CTX.verify_mode = ssl.CERT_NONE
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/126 Safari/537.36"

targets = [f for f in F if urlparse(f["url"]).netloc.lower() in HOSTS]
by = {}
for f in targets:
    by.setdefault(urlparse(f["url"]).netloc.lower(), []).append(f["url"])

for rnd in range(3):
    print(f"--- round {rnd} (serial, 3s apart) ---")
    for h, us in by.items():
        u = us[0]
        req = urllib.request.Request(u, headers={"User-Agent": UA})
        try:
            with urllib.request.urlopen(req, timeout=20, context=CTX) as r:
                body = r.read(400)
            print(f"  {h:32s} {r.status}  {body[:90]!r}")
        except urllib.error.HTTPError as e:
            print(f"  {h:32s} {e.code}  {e.read(200)[:120]!r}")
        except Exception as e:
            print(f"  {h:32s} ERR {type(e).__name__} {e}")
        time.sleep(3)
