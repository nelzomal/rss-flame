from pathlib import Path
D = str(Path(__file__).resolve().parents[1] / "data") + "/"
import json, ssl, collections, statistics, re
import urllib.request, urllib.error
import xml.etree.ElementTree as ET
from concurrent.futures import ThreadPoolExecutor

F = json.load(open(D + "feeds.json"))
P = json.load(open(D + "probe.json"))
GOOD = [p["url"] for p in P if p["status"] == 200 and p.get("newest") not in ("unparseable",)]
print("re-fetching", len(GOOD), "feeds that returned 200 and parsed")

CTX = ssl.create_default_context(); CTX.check_hostname = False; CTX.verify_mode = ssl.CERT_NONE
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/126 Safari/537.36"

ATOM = "{http://www.w3.org/2005/Atom}"
CONTENT = "{http://purl.org/rss/1.0/modules/content/}encoded"
RDF = "{http://www.w3.org/1999/02/22-rdf-syntax-ns#}RDF"
RSS10 = "{http://purl.org/rss/1.0/}"


def one(url):
    rec = {"url": url}
    try:
        with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": UA}), timeout=20, context=CTX) as r:
            rec["etag"] = bool(r.headers.get("ETag"))
            rec["lastmod"] = bool(r.headers.get("Last-Modified"))
            rec["cachectl"] = r.headers.get("Cache-Control") or ""
            body = r.read(30000000)
    except Exception as e:
        rec["fmt"] = "fetch-fail"
        return rec
    rec["bytes"] = len(body)
    s = body.lstrip()[:200]
    if s.startswith(b"{"):
        try:
            j = json.loads(body)
            rec["fmt"] = "JSON Feed" if "items" in j else "JSON (other)"
            rec["items"] = len(j.get("items", []))
        except Exception:
            rec["fmt"] = "broken-json"
        return rec
    try:
        root = ET.fromstring(body)
    except Exception:
        rec["fmt"] = "unparseable"
        return rec
    tag = root.tag
    if tag == RDF:
        rec["fmt"] = "RSS 1.0 (RDF)"
        items = root.findall(RSS10 + "item")
    elif tag == ATOM + "feed":
        rec["fmt"] = "Atom 1.0"
        items = root.findall(ATOM + "entry")
    elif tag == "rss":
        rec["fmt"] = "RSS " + (root.get("version") or "?")
        items = root.findall(".//item")
    else:
        rec["fmt"] = "other:" + tag[:40]
        items = []
    rec["items"] = len(items)
    # full text?
    fulls, summaries = 0, 0
    lens = []
    for it in items:
        ce = it.find(CONTENT)
        body_text = None
        if ce is not None and ce.text:
            body_text = ce.text
            fulls += 1
        else:
            for t in ("description", ATOM + "content", ATOM + "summary"):
                e = it.find(t)
                if e is not None and (e.text or len(list(e))):
                    body_text = e.text or ET.tostring(e, encoding="unicode")
                    break
            summaries += 1
        if body_text:
            lens.append(len(re.sub(r"<[^>]+>", "", body_text)))
    rec["content_encoded_items"] = fulls
    rec["median_item_chars"] = int(statistics.median(lens)) if lens else 0
    rec["has_enclosure"] = any(it.find("enclosure") is not None for it in items)
    rec["has_itunes"] = b"itunes" in body[:3000]
    return rec


with ThreadPoolExecutor(max_workers=30) as ex:
    R = list(ex.map(one, GOOD))
json.dump(R, open(D + "formats.json", "w"), ensure_ascii=False)

ok = [r for r in R if r.get("fmt") not in (None, "fetch-fail", "unparseable", "broken-json")]
print("\n== feed format (of %d successfully re-fetched & parsed) ==" % len(ok))
for k, v in collections.Counter(r["fmt"] for r in R).most_common():
    print(f"{v:5d} ({100*v/len(R):5.1f}%)  {k}")

print("\n== full text vs summary ==")
full = [r for r in ok if r.get("content_encoded_items", 0) > 0]
print(f"  feeds shipping <content:encoded> full bodies: {len(full)} / {len(ok)}  ({100*len(full)/len(ok):.1f}%)")
med = sorted(r.get("median_item_chars", 0) for r in ok)
print(f"  median-of-medians item body length: {med[len(med)//2]} chars")
buck = collections.Counter()
for r in ok:
    c = r.get("median_item_chars", 0)
    for label, lim in [("empty (0)", 1), ("headline only (<120)", 120), ("teaser (120-600)", 600), ("partial (600-2000)", 2000), ("full text (>2000)", 10**9)]:
        if c < lim:
            buck[label] += 1
            break
for k in ["empty (0)", "headline only (<120)", "teaser (120-600)", "partial (600-2000)", "full text (>2000)"]:
    v = buck.get(k, 0)
    print(f"  {v:5d} ({100*v/len(ok):5.1f}%)  {k}")

print("\n== items per feed ==")
its = sorted(r.get("items", 0) for r in ok)
print("  median", its[len(its)//2], " p10", its[len(its)//10], " p90", its[9*len(its)//10], " max", its[-1])
print("  feeds with <=10 items (i.e. tiny sliding window):", sum(1 for i in its if i <= 10), f"({100*sum(1 for i in its if i<=10)/len(its):.1f}%)")

print("\n== HTTP conditional-GET support (bandwidth of polling) ==")
e = sum(1 for r in R if r.get("etag")); l = sum(1 for r in R if r.get("lastmod"))
n = sum(1 for r in R if not r.get("etag") and not r.get("lastmod") and "fmt" in r and r["fmt"] != "fetch-fail")
tot = sum(1 for r in R if r.get("fmt") != "fetch-fail")
print(f"  ETag: {e}/{tot} ({100*e/tot:.1f}%)   Last-Modified: {l}/{tot} ({100*l/tot:.1f}%)   neither: {n}/{tot} ({100*n/tot:.1f}%)")
sizes = sorted(r.get("bytes", 0) for r in R if r.get("bytes"))
print(f"  payload bytes: median {sizes[len(sizes)//2]:,}  p90 {sizes[9*len(sizes)//10]:,}  max {sizes[-1]:,}  total {sum(sizes):,}")
