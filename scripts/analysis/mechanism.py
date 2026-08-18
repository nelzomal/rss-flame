from pathlib import Path
D = str(Path(__file__).resolve().parents[1] / "data") + "/"
import json, collections
from urllib.parse import urlparse
F = json.load(open(D + "feeds.json"))
P = {p["url"]: p for p in json.load(open(D + "probe.json"))}

RULES = [
    ("scrape-bridge: nitter/xcancel (X)", ["xcancel", "nitter"]),
    ("scrape-bridge: RSSHub instance", ["rsshub", "rss.shab.fun", "anyfeeder", "aishort", "buzzing.cc"]),
    ("scrape-bridge: commercial SaaS", ["diffbot", "rss.app", "politepol", "feed43", "fetchrss", "rsseverything", "feedx.net", "xgo.ing", "jintiankansha", "wechat2rss", "werss", "morss"]),
    ("relay: FeedBurner (Google)", ["feedburner", "feedproxy", "feedpress"]),
    ("platform-native feed endpoint", ["youtube.com/feeds", "reddit.com", "/.rss", "github.com"]),
    ("hosted blog/newsletter platform", ["blogspot", "wordpress.com", "medium.com", "substack", "ghost.io", "typlog", "zhubai", "bearblog", "blogger.com"]),
    ("podcast host", ["fireside.fm", "acast", "anchor.fm", "spreaker", "libsyn", "buzzsprout", "xiaoyuzhou"]),
]
cnt = collections.Counter(); live = collections.Counter()
for f in F:
    u = f["url"].lower()
    tag = "self-published (site's own /feed)"
    for name, keys in RULES:
        if any(k in u for k in keys):
            tag = name; break
    cnt[tag] += 1
    p = P.get(f["url"], {})
    if p.get("status") == 200 and p.get("newest") not in ("unparseable", "no-dates", None):
        live[tag] += 1
print(f"{'mechanism':38s} {'n':>5s} {'%':>6s} {'parseable':>10s}  {'%live':>6s}")
for k, n in cnt.most_common():
    print(f"{k:38s} {n:5d} {100*n/len(F):5.1f}% {live[k]:10d}  {100*live[k]/n:5.1f}%")
print(f"{'TOTAL':38s} {len(F):5d}")
