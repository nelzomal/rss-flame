from pathlib import Path
D = str(Path(__file__).resolve().parents[1] / "data") + "/"
import json, re, collections
F = json.load(open(D + "feeds.json"))
P = json.load(open(D + "probe.json"))
by_url = {p["url"]: p for p in P}

PLAT = {
    "X / Twitter": ["xcancel", "nitter", "twitter.com", "/x.com", "twitter"],
    "小红书 xiaohongshu": ["xiaohongshu", "xhslink", "小红书"],
    "抖音 / TikTok": ["douyin", "tiktok", "抖音"],
    "微信公众号 WeChat": ["weixin", "wechat", "mp.weixin", "公众号", "werss", "jintiankansha"],
    "知乎 Zhihu": ["zhihu", "知乎"],
    "Bilibili": ["bilibili", "b23.tv"],
    "Instagram": ["instagram"],
    "YouTube": ["youtube.com/feeds", "youtube"],
    "Reddit": ["reddit"],
    "Podcast (fireside/acast/anchor/spreaker/xiaoyuzhou)": ["fireside", "acast", "anchor.fm", "spreaker", "xiaoyuzhou", "podcast", "libsyn", "buzzsprout"],
}
for name, keys in PLAT.items():
    hits = [f for f in F if any(k in (f["url"] + " " + f["siteUrl"] + " " + f["name"]).lower() for k in keys)]
    live = 0
    for f in hits:
        p = by_url.get(f["url"])
        if p and p["status"] == 200 and p.get("newest") not in ("unparseable", "no-dates"):
            live += 1
    print(f"{name:52s} {len(hits):4d} entries   {live:4d} returned a parseable feed")
    for f in hits[:3]:
        p = by_url.get(f["url"], {})
        print(f"      [{p.get('status','?')}] {f['name'][:24]:26s} {f['url'][:82]}")
