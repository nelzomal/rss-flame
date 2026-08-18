"""Build a self-contained flame-graph page for the mechanism taxonomy (answer 1c).

Hierarchy: root -> mechanism -> host -> feed.
Width = sum of subscriberCount (toggleable to feed count).
Colour = measured health of the live probe.
"""
from pathlib import Path
D = str(Path(__file__).resolve().parents[1] / "data") + "/"
import json, datetime, collections
from urllib.parse import urlparse

FEEDS = json.load(open(D + "feeds.json"))
PROBE = {p["url"]: p for p in json.load(open(D + "probe.json"))}
FMT = {f["url"]: f for f in json.load(open(D + "formats.json"))}
NOW = datetime.datetime.now(datetime.timezone.utc)

# Same rules as mechanism.py — order matters, first match wins.
RULES = [
    ("Nitter / xcancel 中转（X）", ["xcancel", "nitter"],
     "第三方抓取 X 再吐出 XML。X 自己的 feed 在 2013 年就关掉了，这是唯一的替代路径。"),
    ("公共 RSSHub 实例", ["rsshub", "rss.shab.fun", "anyfeeder", "aishort", "buzzing.cc"],
     "志愿者运维的开源抓取农场。免费、共享，因此被限流——你的 feed 能不能用，取决于别人在用多少。"),
    ("商业抓取 SaaS", ["diffbot", "rss.app", "politepol", "feed43", "fetchrss",
                  "rsseverything", "feedx.net", "xgo.ing", "jintiankansha",
                  "wechat2rss", "werss", "morss"],
     "付费的 HTML→RSS 转换。有人掏钱，所以大部分时候是好的。"),
    ("FeedBurner 中转（Google）", ["feedburner", "feedproxy", "feedpress"],
     "2004 年那一代的跳转层，至今还挡在一批真 feed 前面。"),
    ("平台原生接口", ["youtube.com/feeds", "reddit.com", "/.rss", "github.com"],
     "封闭平台自己发布了真 feed。稀有，而且还在减少。"),
    ("托管博客 / newsletter", ["blogspot", "wordpress.com", "medium.com", "substack",
                          "ghost.io", "typlog", "zhubai", "bearblog", "blogger.com"],
     "博客托管方默认就吐 RSS，作者根本没做过这个决定。"),
    ("播客托管", ["fireside.fm", "acast", "anchor.fm", "spreaker", "libsyn",
              "buzzsprout", "xiaoyuzhou"],
     "RSS 是播客的事实标准传输层。广告塞在 enclosure 里，所以发布方能靠它赚钱。"),
]
SELF = ("站点自建 feed", "网站在自己域名上提供 /feed，中间没有任何人。")

MECH_ORDER = [SELF[0]] + [r[0] for r in RULES]
MECH_NOTE = {SELF[0]: SELF[1]}
MECH_NOTE.update({r[0]: r[2] for r in RULES})


def mechanism(url):
    u = url.lower()
    for name, keys, _ in RULES:
        if any(k in u for k in keys):
            return name
    return SELF[0]


def health(f):
    """Measured outcome of actually fetching this feed."""
    p = PROBE.get(f["url"])
    if not p:
        return "broken", "未探测"
    if p["status"] != 200:
        return "broken", f"HTTP {p['status']}" + (f"（{p['err'][:40]}）" if p.get("err") else "")
    n = p.get("newest")
    if n == "unparseable":
        return "broken", f"返回 200，但不是 XML（{p.get('ctype', '?')}）"
    if n == "no-dates":
        return "stale", "能解析，但没有任何一条带日期"
    t = datetime.datetime.fromisoformat(n)
    days = (NOW - t).days
    if days < 30:
        return "live", f"最新一条距今 {max(days, 0)} 天"
    if days < 365:
        return "stale", f"最新一条距今 {days} 天"
    return "zombie", f"最新一条距今 {days} 天（约 {days // 365} 年）"


leaves = []
for f in FEEDS:
    h, why = health(f)
    p = PROBE.get(f["url"], {})
    fm = FMT.get(f["url"], {})
    leaves.append({
        "name": f["name"],
        "url": f["url"],
        "site": f["siteUrl"],
        "cat": f["categoryName"],
        "subs": f["subscriberCount"],
        "mech": mechanism(f["url"]),
        "host": urlparse(f["url"]).netloc.lower() or "(no host)",
        "health": h,
        "why": why,
        "status": p.get("status"),
        "fmt": fm.get("fmt", "—"),
        "items": fm.get("items"),
        "chars": fm.get("median_item_chars"),
        "cond": ("ETag" if fm.get("etag") else "") + ("+Last-Modified" if fm.get("lastmod") else "")
                or ("none" if fm else "—"),
        "bytes": p.get("bytes"),
    })

# ---- assemble tree ----
by_mech = collections.defaultdict(lambda: collections.defaultdict(list))
for lf in leaves:
    by_mech[lf["mech"]][lf["host"]].append(lf)


def node(name, kind, children=None, leaf=None, note=""):
    n = {"n": name, "k": kind, "note": note}
    if leaf:
        n["leaf"] = leaf
        n["subs"] = leaf["subs"]
        n["cnt"] = 1
        n["h"] = leaf["health"]
    else:
        n["c"] = children
        n["subs"] = sum(c["subs"] for c in children)
        n["cnt"] = sum(c["cnt"] for c in children)
        mix = collections.Counter()
        mixc = collections.Counter()
        for c in children:
            for k in ("live", "stale", "zombie", "broken"):
                mix[k] += c.get("mix", {}).get(k, c["subs"] if c.get("h") == k else 0)
                mixc[k] += c.get("mixc", {}).get(k, c["cnt"] if c.get("h") == k else 0)
        n["mix"] = dict(mix)
        n["mixc"] = dict(mixc)
    return n


# Children are ordered healthiest-first at EVERY level, so that a parent's colour
# band (which is its subtree's health histogram) lines up with the children drawn
# beneath it. Ordering by subscribers instead would make that band a lie.
RANK = {"live": 0, "stale": 1, "zombie": 2, "broken": 3}


def score(n):
    """Subscriber-weighted mean health, 0 (all live) .. 3 (all broken)."""
    m = n.get("mix") or {n["h"]: n["subs"]}
    tot = sum(m.values())
    if not tot:  # zero-subscriber subtree — fall back to feed counts
        m = n.get("mixc") or {n["h"]: 1}
        tot = sum(m.values()) or 1
    return sum(RANK[k] * v for k, v in m.items()) / tot


def order(nodes):
    return sorted(nodes, key=lambda x: (score(x), -x["subs"], -x["cnt"], x["n"]))


mech_nodes = []
for m in MECH_ORDER:
    hosts = by_mech.get(m)
    if not hosts:
        continue
    host_nodes = [node(h, "host", order([node(lf["name"], "feed", leaf=lf) for lf in lfs]))
                  for h, lfs in hosts.items()]
    mech_nodes.append(node(m, "mech", order(host_nodes), note=MECH_NOTE[m]))

mech_nodes = order(mech_nodes)
ROOT = node("ifeed.cc /discover 全部 932 个订阅源", "root", mech_nodes,
            note="目录里的每一个订阅源，都真实抓取并解析过。")

TOTALS = {
    "feeds": len(leaves),
    "subs": sum(l["subs"] for l in leaves),
    "zero_sub": sum(1 for l in leaves if l["subs"] == 0),
    "one_or_less": sum(1 for l in leaves if l["subs"] <= 1),
    "probed": NOW.strftime("%Y-%m-%d %H:%M UTC"),
}
for k in ("live", "stale", "zombie", "broken"):
    TOTALS[k] = sum(1 for l in leaves if l["health"] == k)
    TOTALS[k + "_subs"] = sum(l["subs"] for l in leaves if l["health"] == k)

open(D + "flame_data.json", "w").write(json.dumps({"root": ROOT, "totals": TOTALS},
                                                  ensure_ascii=False, separators=(",", ":")))
print("mechanisms:", len(mech_nodes), " leaves:", len(leaves), " subs:", TOTALS["subs"])
for m in mech_nodes:
    print(f"  {m['n']:32s} subs={m['subs']:5d}  feeds={m['cnt']:4d}  hosts={len(m['c']):3d}  mix={m['mix']}")
print("zero-subscriber feeds:", TOTALS["zero_sub"])
