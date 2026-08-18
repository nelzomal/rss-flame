from pathlib import Path
D = str(Path(__file__).resolve().parents[1] / "data") + "/"
import json, collections, datetime
from urllib.parse import urlparse

R = json.load(open(D + "probe.json"))
N = len(R)
now = datetime.datetime.now(datetime.timezone.utc)
print("N =", N)

st = collections.Counter(r["status"] for r in R)
print("\n== HTTP status ==")
for k, v in st.most_common():
    print(f"{v:5d} ({100*v/N:5.1f}%)  {k}")

print("\n== transport errors (status 0) ==")
errs = collections.Counter(r.get("err", "").split(":")[0] for r in R if r["status"] == 0)
for k, v in errs.most_common(12):
    print(f"{v:5d}  {k}")

ok = [r for r in R if r["status"] == 200]
print(f"\n== of the {len(ok)} that returned 200 ==")
ct = collections.Counter(r.get("ctype") for r in ok)
print("content-types:", ct.most_common(8))
bad = [r for r in ok if r.get("newest") == "unparseable"]
nod = [r for r in ok if r.get("newest") == "no-dates"]
print("unparseable XML (200 but not a feed):", len(bad))
for r in bad[:12]:
    print("    ", r["ctype"], r["bytes"], r["url"][:95])
print("parsed but no item dates:", len(nod))

dated = [r for r in ok if r.get("newest") not in ("unparseable", "no-dates")]
print("parsed with dates:", len(dated))
buck = collections.Counter()
for r in dated:
    t = datetime.datetime.fromisoformat(r["newest"])
    d = (now - t).days
    for label, lim in [("<1d", 1), ("1-7d", 7), ("7-30d", 30), ("30-90d", 90), ("90-365d", 365), ("1-3y", 1095), (">3y", 10**6)]:
        if d < lim:
            buck[label] += 1
            break
print("\n== freshness of newest item, LIVE fetch ==")
for k in ["<1d", "1-7d", "7-30d", "30-90d", "90-365d", "1-3y", ">3y"]:
    v = buck.get(k, 0)
    print(f"{v:5d} ({100*v/N:5.1f}% of all, {100*v/len(dated):5.1f}% of parsed)  {k}")

# funnel
alive30 = sum(buck.get(k, 0) for k in ["<1d", "1-7d", "7-30d"])
print("\n== FUNNEL (of all %d catalog entries) ==" % N)
print(f"  fetched 200 OK ............ {len(ok):4d}  {100*len(ok)/N:5.1f}%")
print(f"  ... and parsed as XML ..... {len(ok)-len(bad):4d}  {100*(len(ok)-len(bad))/N:5.1f}%")
print(f"  ... and had item dates .... {len(dated):4d}  {100*len(dated)/N:5.1f}%")
print(f"  ... and updated <30d ...... {alive30:4d}  {100*alive30/N:5.1f}%")

# per-host reliability for the big bridges
print("\n== reliability by feed host (hosts with >=5 entries) ==")
byhost = collections.defaultdict(list)
for r in R:
    byhost[urlparse(r["url"]).netloc.lower()].append(r)
rows = []
for h, rs in byhost.items():
    if len(rs) < 5:
        continue
    o = sum(1 for r in rs if r["status"] == 200)
    fresh = 0
    for r in rs:
        n = r.get("newest")
        if isinstance(n, str) and n not in ("unparseable", "no-dates"):
            if (now - datetime.datetime.fromisoformat(n)).days < 30:
                fresh += 1
    rows.append((len(rs), h, o, fresh))
for n, h, o, fresh in sorted(rows, reverse=True):
    print(f"  {n:4d} entries  {100*o/n:5.1f}% 200  {100*fresh/n:5.1f}% fresh<30d   {h}")

# how do the highest-subscriber feeds hold up?
print("\n== top-25 catalog feeds by subscriberCount ==")
for r in sorted(R, key=lambda x: -x["subs"])[:25]:
    n = r.get("newest", "-")
    if isinstance(n, str) and n not in ("unparseable", "no-dates", "-"):
        n = str((now - datetime.datetime.fromisoformat(n)).days) + "d old"
    print(f"  subs={r['subs']:3d} status={r['status']:<4} newest={str(n)[:14]:14s} {r['name'][:28]:30s} {r['url'][:60]}")
