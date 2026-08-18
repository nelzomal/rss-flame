import ssl, urllib.request, urllib.error
CTX = ssl.create_default_context(); CTX.check_hostname = False; CTX.verify_mode = ssl.CERT_NONE
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/126 Safari/537.36"

URLS = [
    ("xiaohongshu native rss?", "https://www.xiaohongshu.com/rss"),
    ("xiaohongshu feed?", "https://www.xiaohongshu.com/feed"),
    ("xhs user page (bot)", "https://www.xiaohongshu.com/user/profile/5b1b6b2b6b2b6b2b6b2b6b2b"),
    ("douyin rss?", "https://www.douyin.com/rss"),
    ("douyin user page (bot)", "https://www.douyin.com/user/MS4wLjABAAAA"),
    ("tiktok rss?", "https://www.tiktok.com/rss"),
    ("tiktok @user (bot)", "https://www.tiktok.com/@tiktok"),
    ("instagram rss?", "https://www.instagram.com/instagram/feed/"),
    ("--- open comparison ---", None),
    ("youtube channel feed", "https://www.youtube.com/feeds/videos.xml?channel_id=UCBR8-60-B28hp2BmDPdntcQ"),
    ("wordpress.com blog", "https://en.blog.wordpress.com/feed/"),
    ("substack", "https://astralcodexten.substack.com/feed"),
    ("bilibili native rss?", "https://www.bilibili.com/rss"),
    ("weibo native rss?", "https://weibo.com/rss"),
    ("zhihu native rss?", "https://www.zhihu.com/rss"),
    ("mp.weixin native rss?", "https://mp.weixin.qq.com/rss"),
]
for name, u in URLS:
    if u is None:
        print(name); continue
    try:
        with urllib.request.urlopen(urllib.request.Request(u, headers={"User-Agent": UA}), timeout=15, context=CTX) as r:
            b = r.read(600)
        ct = (r.headers.get("Content-Type") or "")[:30]
        isfeed = b.lstrip()[:200].find(b"<rss") >= 0 or b.lstrip()[:200].find(b"<feed") >= 0
        print(f"{name:26s} {r.status}  feed={isfeed!s:5s}  {ct:30s} {b[:60]!r}")
    except urllib.error.HTTPError as e:
        print(f"{name:26s} {e.code}  -")
    except Exception as e:
        print(f"{name:26s} ERR {type(e).__name__} {str(e)[:50]}")
