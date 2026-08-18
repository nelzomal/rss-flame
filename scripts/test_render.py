"""Drive zoom/search/metric programmatically so headless Chrome (which cannot click)
can verify the interaction logic and the Chinese strings."""
from pathlib import Path
D = str(Path(__file__).resolve().parents[1] / "data") + "/"
PAGE = str(Path(__file__).resolve().parents[1] / "index.html")
h = open(PAGE).read()

harness = r"""
<script>
const crumbs = () => document.getElementById('crumbs').innerText.replace(/\s+/g,' ').trim();
const cells  = () => document.querySelectorAll('#flame .cell').length;
const hint   = () => document.getElementById('hint').innerText;
const log = [];
log.push(['初始', crumbs(), cells(), hint()]);

const mech = ROOT.c.find(m => m.n.indexOf('xcancel') >= 0);
zoom(mech, 1);
log.push(['下钻 -> 生产方式', crumbs(), cells(), hint()]);
log.push(['该层详情', document.getElementById('detail').innerText.replace(/\s+/g,' ').slice(0,200), '', '']);

const host = mech.c[0];  zoom(host, 2);
log.push(['下钻 -> 主机', crumbs(), cells(), hint()]);

const leaf = host.c[0];  zoom(leaf, 3);
log.push(['下钻 -> 单个订阅源', crumbs(), cells(), hint()]);
log.push(['订阅源详情', document.getElementById('detail').innerText.replace(/\s+/g,' ').slice(0,330), '', '']);

zoom(ROOT, 0);                       log.push(['点面包屑回到顶层', crumbs(), cells(), '']);
metric = 'cnt'; render();            log.push(['切换为订阅源个数', crumbs(), cells(), hint()]);
metric = 'subs'; query='少数派'; render(); log.push(['搜索「少数派」', crumbs(), cells(), hint()]);
query = ''; render();

document.body.innerHTML = '<pre id="out">' +
  log.map(r => r.filter(x => x !== '').join('  |  ')).join('\n') + '</pre>';
</script>
"""
open("/tmp/flame_test.html", "w").write(h.replace("</body>", harness + "</body>"))
print("wrote /tmp/flame_test.html")
