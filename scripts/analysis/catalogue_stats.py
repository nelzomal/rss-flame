from pathlib import Path
D = str(Path(__file__).resolve().parents[1] / "data") + "/"
import json, re, collections, datetime
from urllib.parse import urlparse

F = json.load(open(D + "feeds.json"))
print("N =", len(F))

# --- host distribution of the FEED url (not the site url) ---
hosts = collections.Counter(urlparse(f["url"]).netloc.lower() for f in F)
print("\n== top 30 feed hosts ==")
for h, n in hosts.most_common(30):
    print(f"{n:5d}  {h}")

# --- classify by mechanism ---
BRIDGE = {
    "rsshub": lambda u: "rsshub" in u or "rss.shab.fun" in u,
    "diffbot": lambda u: "diffbot" in u,
    "rss.app": lambda u: "rss.app" in u,
    "feedburner": lambda u: "feedburner" in u or "feedproxy" in u,
    "rsshub-ish paid saas (rss.beauty/rsser/feed43/politepol/fetchrss)":
        lambda u: any(k in u for k in ["rss.beauty", "rsser", "feed43", "politepol", "fetchrss", "rss-bridge", "rsstt", "wechat2rss", "werss", "feedx", "rss2json", "morss"]),
    "github/gitlab generated": lambda u: "github.com" in u or "githubusercontent" in u,
    "reddit": lambda u: "reddit.com" in u,
    "youtube": lambda u: "youtube.com" in u,
    "medium/substack/wordpress hosted": lambda u: any(k in u for k in ["medium.com", "substack.com", "wordpress.com", "blogspot", "ghost.io", "bearblog", "typlog", "zhubai"]),
}
cls = collections.Counter()
examples = collections.defaultdict(list)
for f in F:
    u = f["url"].lower()
    tag = "native / self-hosted"
    for k, fn in BRIDGE.items():
        if fn(u):
            tag = k
            break
    cls[tag] += 1
    if len(examples[tag]) < 4:
        examples[tag].append(f["url"])
print("\n== mechanism ==")
for k, n in cls.most_common():
    print(f"{n:5d}  {k}")
    for e in examples[k]:
        print("          ", e[:110])

# --- scheme ---
print("\n== scheme ==", collections.Counter(urlparse(f["url"]).scheme for f in F).most_common())

# --- duplicates: same site, multiple feed rows ---
sites = collections.Counter(urlparse(f["siteUrl"] or "").netloc.lower() for f in F)
dups = {k: v for k, v in sites.items() if v > 1 and k}
print("\n== sites with >1 catalog entry ==", len(dups), "covering", sum(dups.values()), "rows")
print(sorted(dups.items(), key=lambda x: -x[1])[:15])

# --- freshness ---
now = datetime.datetime(2026, 8, 18, tzinfo=datetime.timezone.utc)
buckets = collections.Counter()
ages = []
for f in F:
    lu = f.get("lastUpdated")
    if not lu:
        buckets["never"] += 1
        continue
    t = datetime.datetime.fromisoformat(lu.replace("Z", "+00:00"))
    d = (now - t).days
    ages.append(d)
    for label, lim in [("<1d", 1), ("1-7d", 7), ("7-30d", 30), ("30-90d", 90), ("90-365d", 365), (">1y", 10**6)]:
        if d < lim:
            buckets[label] += 1
            break
print("\n== staleness of last article (catalog's own lastUpdated) ==")
for k in ["<1d", "1-7d", "7-30d", "30-90d", "90-365d", ">1y", "never"]:
    n = buckets.get(k, 0)
    print(f"{n:5d}  ({100*n/len(F):5.1f}%)  {k}")

# --- subscribers ---
subs = sorted((f["subscriberCount"] for f in F), reverse=True)
print("\n== subscriberCount ==")
print("sum", sum(subs), "max", subs[0], "median", subs[len(subs)//2], "zero-or-one:", sum(1 for s in subs if s <= 1))
print("top10", subs[:10])
print("\ntop feeds by subscribers:")
for f in sorted(F, key=lambda x: -x["subscriberCount"])[:15]:
    print(f"{f['subscriberCount']:5d}  {f['name'][:40]:42s} {f['url'][:70]}")

# --- articleCount ---
ac = [f["articleCount"] for f in F]
print("\n== articleCount == zero:", sum(1 for a in ac if a == 0), "median", sorted(ac)[len(ac)//2])
