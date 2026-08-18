from pathlib import Path
D = str(Path(__file__).resolve().parents[1] / "data") + "/"
import json, random, ssl, socket, datetime, collections
import urllib.request, urllib.error
from concurrent.futures import ThreadPoolExecutor
import xml.etree.ElementTree as ET

F = json.load(open(D + "feeds.json"))
random.seed(42)
SAMPLE = F if len(F) <= 1000 else random.sample(F, 1000)

CTX = ssl.create_default_context()
CTX.check_hostname = False
CTX.verify_mode = ssl.CERT_NONE
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126 Safari/537.36"


def newest_item_date(body):
    """Return the newest item/entry date found, as a datetime, or None."""
    try:
        root = ET.fromstring(body)
    except Exception:
        return "unparseable"
    dates = []
    for tag in ("pubDate", "{http://purl.org/dc/elements/1.1/}date",
                "{http://www.w3.org/2005/Atom}updated", "{http://www.w3.org/2005/Atom}published"):
        for e in root.iter(tag):
            if e.text:
                dates.append(e.text.strip())
    if not dates:
        return "no-dates"
    import email.utils
    best = None
    for d in dates:
        t = None
        try:
            t = email.utils.parsedate_to_datetime(d)
        except Exception:
            try:
                t = datetime.datetime.fromisoformat(d.replace("Z", "+00:00"))
            except Exception:
                t = None
        if t is not None:
            if t.tzinfo is None:
                t = t.replace(tzinfo=datetime.timezone.utc)
            if best is None or t > best:
                best = t
    return best or "no-dates"


def probe(f):
    url = f["url"]
    rec = {"name": f["name"], "url": url, "cat": f["category"], "subs": f["subscriberCount"]}
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "application/rss+xml, application/xml, text/xml, */*"})
    try:
        with urllib.request.urlopen(req, timeout=20, context=CTX) as r:
            rec["status"] = r.status
            rec["ctype"] = (r.headers.get("Content-Type") or "").split(";")[0].strip().lower()
            body = r.read(30000000)
        rec["bytes"] = len(body)
        d = newest_item_date(body)
        if isinstance(d, str):
            rec["newest"] = d
        else:
            rec["newest"] = d.astimezone(datetime.timezone.utc).isoformat()
    except urllib.error.HTTPError as e:
        rec["status"] = e.code
        rec["err"] = "http"
    except urllib.error.URLError as e:
        rec["status"] = 0
        rec["err"] = type(e.reason).__name__ + ": " + str(e.reason)[:60]
    except socket.timeout:
        rec["status"] = 0
        rec["err"] = "timeout"
    except Exception as e:
        rec["status"] = 0
        rec["err"] = type(e).__name__ + ": " + str(e)[:60]
    return rec


with ThreadPoolExecutor(max_workers=40) as ex:
    res = list(ex.map(probe, SAMPLE))

json.dump(res, open(D + "probe.json", "w"), ensure_ascii=False)
print("probed", len(res))
