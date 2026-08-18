from pathlib import Path
D = str(Path(__file__).resolve().parents[1] / "data") + "/"
PAGE = str(Path(__file__).resolve().parents[1] / "index.html")
import json

DATA = open(D + "flame_data.json").read().replace("</", "<\\/")

HTML = r"""<!doctype html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>所谓「RSS 订阅源」到底是什么 —— ifeed.cc/discover 火焰图</title>
<style>
  :root {
    --bg:#0e1116; --panel:#161b22; --line:#272e38; --ink:#e6edf3; --dim:#8b949e;
    --live:#2ea043; --stale:#d29922; --zombie:#bb6b1e; --broken:#cf3c33;
  }
  * { box-sizing:border-box; }
  body {
    margin:0; background:var(--bg); color:var(--ink);
    font:14px/1.7 -apple-system,BlinkMacSystemFont,"PingFang SC","Hiragino Sans GB","Microsoft YaHei","Segoe UI",Helvetica,sans-serif;
  }
  .wrap { max-width:1240px; margin:0 auto; padding:28px 22px 80px; }
  h1 { font-size:23px; margin:0 0 6px; letter-spacing:-.01em; }
  .sub { color:var(--dim); margin:0 0 22px; max-width:80ch; }
  .sub b { color:var(--ink); font-weight:600; }
  code { font-family:ui-monospace,SFMono-Regular,Menlo,monospace; font-size:.92em;
         background:#1c222b; padding:1px 5px; border-radius:4px; }

  /* ---- controls ---- */
  .bar { display:flex; gap:10px; align-items:center; flex-wrap:wrap; margin-bottom:14px; }
  .seg { display:flex; border:1px solid var(--line); border-radius:7px; overflow:hidden; }
  .seg button {
    background:transparent; border:0; color:var(--dim); padding:7px 13px; cursor:pointer;
    font:inherit; font-size:13px; border-right:1px solid var(--line);
  }
  .seg button:last-child { border-right:0; }
  .seg button.on { background:#22303f; color:var(--ink); }
  .seg button:hover:not(.on) { background:#1b222c; color:var(--ink); }
  input[type=search] {
    background:var(--panel); border:1px solid var(--line); border-radius:7px; color:var(--ink);
    padding:7px 11px; font:inherit; font-size:13px; width:230px;
  }
  input[type=search]::placeholder { color:#5b6572; }
  .ghost { background:transparent; border:1px solid var(--line); border-radius:7px; color:var(--dim);
           padding:7px 13px; font:inherit; font-size:13px; cursor:pointer; }
  .ghost:hover { color:var(--ink); border-color:#3d4757; }

  /* ---- legend ---- */
  .legend { display:flex; gap:16px; flex-wrap:wrap; margin:0 0 10px; font-size:12.5px; color:var(--dim); }
  .legend span { display:flex; align-items:center; gap:6px; }
  .sw { width:11px; height:11px; border-radius:2px; display:inline-block; }

  /* ---- crumbs ---- */
  .crumbs { font-size:12.5px; color:var(--dim); margin-bottom:8px; min-height:19px;
            font-family:ui-monospace,SFMono-Regular,Menlo,monospace; }
  .crumbs a { color:#6cb6ff; cursor:pointer; text-decoration:none; }
  .crumbs a:hover { text-decoration:underline; }

  /* ---- flame ---- */
  #flame { position:relative; border:1px solid var(--line); border-radius:9px;
           background:var(--panel); padding:8px; overflow:hidden; }
  .row { position:relative; height:27px; margin-bottom:3px; }
  .rowlabel { position:absolute; left:-1px; top:-17px; font-size:11px; color:#5b6572; }
  .cell {
    position:absolute; top:0; height:27px; border-radius:3px; cursor:pointer;
    overflow:hidden; white-space:nowrap; font-size:12px; line-height:27px;
    padding:0 7px; color:#fff; text-shadow:0 1px 2px rgba(0,0,0,.55);
    border:1px solid rgba(0,0,0,.35); transition:filter .08s, opacity .08s;
  }
  .cell:hover { filter:brightness(1.28); }
  .cell.anc { background:#2b3441 !important; color:var(--dim); text-shadow:none; }
  .cell.dim { opacity:.17; }
  .cell.hit { outline:2px solid #6cb6ff; outline-offset:-2px; }
  .cell .pct { color:rgba(255,255,255,.62); font-size:11px; margin-left:7px;
               font-family:ui-monospace,SFMono-Regular,Menlo,monospace; }

  /* ---- detail ---- */
  .detail { margin-top:18px; border:1px solid var(--line); border-radius:9px;
            background:var(--panel); padding:16px 18px; min-height:150px; }
  .detail h3 { margin:0 0 3px; font-size:15px; word-break:break-all; }
  .detail .kind { font-size:11.5px; color:var(--dim); }
  .detail .note { color:var(--dim); margin:9px 0 12px; max-width:82ch; }
  .kv { display:grid; grid-template-columns:max-content 1fr; gap:3px 16px; font-size:13px; }
  .kv dt { color:var(--dim); }
  .kv dd { margin:0; font-family:ui-monospace,SFMono-Regular,Menlo,monospace; word-break:break-all; }
  .mixbar { height:9px; border-radius:5px; overflow:hidden; display:flex; margin:11px 0 5px; }
  .mixbar i { display:block; height:100%; }
  .tag { display:inline-block; padding:1px 7px; border-radius:4px; font-size:11.5px;
         font-weight:600; letter-spacing:.02em; }

  /* ---- footnote table ---- */
  table { border-collapse:collapse; width:100%; margin:0 0 10px; font-size:13px; }
  th,td { text-align:left; padding:7px 10px; border-bottom:1px solid var(--line); }
  th { color:var(--dim); font-weight:500; font-size:12px; }
  td.num { text-align:right; font-family:ui-monospace,SFMono-Regular,Menlo,monospace; }
  th.num { text-align:right; }
  td.mech { line-height:1.35; }
  td.mech small { display:block; color:var(--dim); font-size:11.5px; margin-top:2px; max-width:52ch; }
  tr:hover td { background:#1b222c; }
  .caption { color:var(--dim); font-size:12.5px; margin-top:9px; }
  .callout { margin-top:18px; border:1px solid #4a2320; border-left:3px solid var(--broken);
             border-radius:9px; background:#1a1315; padding:15px 18px; }
  .callout h4 { margin:0 0 7px; font-size:14.5px; color:#ff8b80; }
  .callout p { margin:0 0 9px; color:#c3ccd6; max-width:84ch; }
  .callout pre { margin:0; padding:11px 13px; background:#0e1116; border:1px solid var(--line);
                 border-radius:6px; overflow-x:auto; font-size:12px; line-height:1.6;
                 font-family:ui-monospace,SFMono-Regular,Menlo,monospace; color:#9fb0c0; }
  .callout pre b { color:#ff8b80; font-weight:600; }
</style>
</head>
<body>
<div class="wrap">

<h1>「RSS」有一半不是 RSS，是套了 XML 外壳的抓取</h1>
<p class="sub">
  <code>ifeed.cc/discover</code> 目录里的 <b>932</b> 个订阅源，全部真实抓取并解析了一遍。
  这里按<b>「这段 XML 究竟是怎么生产出来的」</b>分组 —— 不是按格式分。
  条形宽度是<b>订阅数之和</b>，颜色是<b>实际抓取的结果</b>。
  点任意一条可以逐层下钻，一直钻到单个订阅源。
</p>

<table id="tbl">
  <thead><tr>
    <th>生产方式</th>
    <th class="num">订阅源数</th><th class="num">占源数</th>
    <th class="num">订阅数</th><th class="num">占订阅数</th>
    <th class="num">30 天内存活</th>
  </tr></thead>
  <tbody></tbody>
</table>
<p class="caption" id="cap" style="margin:0 0 26px"></p>

<div class="bar">
  <div class="seg" id="metric">
    <button data-m="subs" class="on">宽度 = 订阅数</button>
    <button data-m="cnt">宽度 = 订阅源个数</button>
  </div>
  <input type="search" id="q" placeholder="高亮订阅源 / 主机…">
  <button class="ghost" id="reset">重置缩放</button>
  <span style="color:var(--dim);font-size:12.5px" id="hint"></span>
</div>

<div class="legend">
  <span><i class="sw" style="background:var(--live)"></i> 存活 —— 30 天内更新过</span>
  <span><i class="sw" style="background:var(--stale)"></i> 陈旧 —— 30 天到 1 年</span>
  <span><i class="sw" style="background:var(--zombie)"></i> 僵尸 —— 照常返回 200，但一年多没动静</span>
  <span><i class="sw" style="background:var(--broken)"></i> 损坏 —— 非 200，或返回 200 但根本不是 feed</span>
</div>
<p class="caption" style="margin:0 0 10px">
  每一行都按<b>健康度从好到坏</b>排序；上层条形的色带就是它整个子树的健康度直方图 ——
  所以一条的红色尾巴，宽度正好等于下一行里那些坏掉的订阅源。
</p>

<div class="crumbs" id="crumbs"></div>
<div id="flame"></div>

<div class="detail" id="detail"></div>

<div class="callout">
  <h4>最坏的失效方式不是 404，是「格式完全正确的垃圾」</h4>
  <p>
    上图那一整块红色 —— <code>rss.xcancel.com</code>，194 个源、占目录 20.8% —— 并不是打不开。
    它稳稳地返回一份格式完全合法的 RSS 2.0，里面只有一条：
  </p>
  <pre>&lt;title&gt;<b>RSS reader not yet whitelisted!</b>&lt;/title&gt;
&lt;description&gt;Please send an email rss [AT] xcancel [DOT] com with this ID
              to get your RSS feed reader whitelisted: 9db973f9…&lt;/description&gt;
&lt;pubDate&gt;Mon, 01 January <b>1971</b> 00:00:00 GMT&lt;/pubDate&gt;</pre>
  <p style="margin-top:11px">
    后果在 ifeed 自己的数据库里已经能看到：这 194 条记录的<b>标题字段全部变成了
    「RSS reader not yet whitelisted!」</b> —— 阅读器照常解析、照常入库，把哨兵报文当成正文，
    把原来的账号名覆盖掉了。协议层面一切正常，200、合法 XML、有 <code>pubDate</code>；
    只是内容没了。一个中转方改了一次策略，目录里五分之一的源就这样被静默污染，
    而没有任何一层会报错。
  </p>
</div>


</div>

<script>
const DATA = __DATA__;
const ROOT = DATA.root, T = DATA.totals;
const C = { live:'#2ea043', stale:'#d29922', zombie:'#bb6b1e', broken:'#cf3c33' };
const ORDER = ['live','stale','zombie','broken'];
const HN = { live:'存活', stale:'陈旧', zombie:'僵尸', broken:'损坏' };
const ROWNAMES = ['目录','生产方式','提供 XML 的主机','单个订阅源'];

let metric = 'subs';       // 'subs' | 'cnt'
let focus  = ROOT;         // zoomed-to node
let path   = [ROOT];       // ancestor chain incl. focus
let query  = '';

const val  = n => metric === 'subs' ? n.subs : n.cnt;
const mix  = n => n.leaf ? { [n.h]: val(n) } : (metric === 'subs' ? n.mix : n.mixc);
const fmt  = x => x.toLocaleString();

/* An internal bar is painted as its children's health mix, in hard stops.
   So a mechanism's bar already shows you what you'd find by clicking it. */
function paint(n) {
  if (n.leaf) return C[n.h];
  const m = mix(n), tot = ORDER.reduce((s,k) => s + (m[k]||0), 0);
  if (!tot) return '#39424f';
  let at = 0, stops = [];
  for (const k of ORDER) {
    const w = (m[k]||0) / tot * 100;
    if (w <= 0) continue;
    stops.push(`${C[k]} ${at.toFixed(3)}%`, `${C[k]} ${(at+w).toFixed(3)}%`);
    at += w;
  }
  return `linear-gradient(90deg, ${stops.join(',')})`;
}

function layout() {
  const rows = [];
  // ancestors above the zoom root, rendered full width
  path.slice(0, -1).forEach((a, d) => rows.push([{ node:a, x:0, w:100, anc:true, depth:d }]));
  const base = path.length - 1;
  (function walk(n, x, w, d) {
    (rows[d] ||= []).push({ node:n, x, w, anc:false, depth:d });
    if (!n.c) return;
    const tot = val(n);
    if (!tot) return;
    let at = x;
    for (const ch of n.c) {
      const cw = val(ch) / tot * w;
      if (cw > 0) walk(ch, at, cw, d + 1);
      at += cw;
    }
  })(focus, 0, 100, base);
  return rows;
}

function render() {
  const rows = layout();
  const el = document.getElementById('flame');
  el.innerHTML = '';
  const q = query.trim().toLowerCase();
  let hits = 0;

  rows.forEach((cells, d) => {
    const row = document.createElement('div');
    row.className = 'row';
    if (ROWNAMES[d]) row.innerHTML = `<span class="rowlabel">${ROWNAMES[d]}</span>`;
    row.style.marginTop = ROWNAMES[d] ? '20px' : '';
    for (const c of cells) {
      const n = c.node, div = document.createElement('div');
      div.className = 'cell' + (c.anc ? ' anc' : '');
      div.style.left = c.x + '%';
      div.style.width = 'calc(' + c.w + '% - 2px)';
      if (!c.anc) div.style.background = paint(n);
      const fv = val(focus) || 1;
      const share = val(n) / fv * 100;
      const label = n.k === 'feed' ? n.n : n.n;
      div.innerHTML = c.w > 4
        ? `${esc(label)}<span class="pct">${share >= 99.95 ? '100' : share.toFixed(1)}%</span>`
        : (c.w > 1.2 ? esc(label) : '');
      if (q) {
        const hay = (n.n + ' ' + (n.leaf ? n.leaf.url + ' ' + n.leaf.cat : '')).toLowerCase();
        if (hay.includes(q)) { div.classList.add('hit'); hits++; }
        else div.classList.add('dim');
      }
      div.onmouseenter = () => detail(n);
      div.onclick = () => zoom(n, c.depth);
      row.appendChild(div);
    }
    el.appendChild(row);
  });

  document.getElementById('hint').textContent =
    q ? `匹配 ${hits} 项` :
    `当前视图内共 ${fmt(val(focus))} ${metric === 'subs' ? '个订阅' : '个订阅源'}`;

  document.getElementById('crumbs').innerHTML = path.map((n, i) =>
    i === path.length - 1 ? `<span>${esc(n.n)}</span>`
                          : `<a data-i="${i}">${esc(n.n)}</a>`).join(' <span style="color:#3d4757">▸</span> ');
  document.querySelectorAll('.crumbs a').forEach(a => a.onclick = () => {
    path = path.slice(0, +a.dataset.i + 1); focus = path[path.length-1]; render(); detail(focus);
  });
}

function zoom(n, depth) {
  if (n === focus) {                       // clicking the focus pops out one level
    if (path.length > 1) { path.pop(); focus = path[path.length-1]; }
  } else if (depth < path.length - 1) {    // clicked an ancestor
    path = path.slice(0, depth + 1); focus = path[path.length-1];
  } else {                                 // clicked a descendant — rebuild the chain
    const chain = [];
    (function find(cur, acc) {
      acc = acc.concat([cur]);
      if (cur === n) { chain.push(...acc); return true; }
      return (cur.c || []).some(ch => find(ch, acc));
    })(ROOT, []);
    if (chain.length) { path = chain; focus = n; }
  }
  render(); detail(focus);
}

function esc(s) { return String(s).replace(/[&<>"]/g, m => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[m])); }

function detail(n) {
  const d = document.getElementById('detail');
  const m = mix(n), tot = ORDER.reduce((s,k)=>s+(m[k]||0),0) || 1;
  const bar = ORDER.map(k => `<i style="width:${(m[k]||0)/tot*100}%;background:${C[k]}"></i>`).join('');
  const mixTxt = ORDER.filter(k => m[k]).map(k =>
    `<span style="color:${C[k]}">${HN[k]} ${fmt(m[k])}</span>`).join(' · ');

  let kv = '';
  if (n.leaf) {
    const L = n.leaf;
    kv = `
      <dl class="kv">
        <dt>feed 地址</dt><dd>${esc(L.url)}</dd>
        <dt>抓取结果</dt><dd><span class="tag" style="background:${C[L.health]}22;color:${C[L.health]}">${HN[L.health]}</span> — ${esc(L.why)}</dd>
        <dt>订阅数</dt><dd>${L.subs}</dd>
        <dt>分类</dt><dd>${esc(L.cat)}</dd>
        <dt>传输格式</dt><dd>${esc(L.fmt)}</dd>
        <dt>条目数</dt><dd>${L.items ?? '—'}</dd>
        <dt>单条正文中位长度</dt><dd>${L.chars != null ? L.chars + ' 字符' + (L.chars > 2000 ? '（全文）' : L.chars < 120 ? '（只有标题）' : '（摘要）') : '—'}</dd>
        <dt>条件请求</dt><dd>${esc(L.cond === 'none' ? '不支持' : L.cond)}</dd>
        <dt>单次抓取体积</dt><dd>${L.bytes != null ? fmt(L.bytes) + ' 字节' : '—'}</dd>
      </dl>`;
  } else {
    const live = (m.live||0)/tot*100;
    kv = `
      <dl class="kv">
        <dt>订阅源数</dt><dd>${fmt(n.cnt)}  （占目录 ${(n.cnt/T.feeds*100).toFixed(1)}%）</dd>
        <dt>订阅数</dt><dd>${fmt(n.subs)}  （占全部订阅 ${(n.subs/T.subs*100).toFixed(1)}%）</dd>
        <dt>下级节点</dt><dd>${n.c ? n.c.length : 0}</dd>
        <dt>存活占比</dt><dd>${live.toFixed(1)}%（按${metric === 'subs' ? '订阅数' : '订阅源个数'}加权）</dd>
      </dl>`;
  }
  d.innerHTML = `
    <div class="kind">${n.k === 'feed' ? 'RSS 订阅源' : n.k === 'host' ? '提供 XML 的主机' : n.k === 'mech' ? '生产方式' : '目录'}</div>
    <h3>${esc(n.n)}</h3>
    ${n.note ? `<p class="note">${esc(n.note)}</p>` : ''}
    <div class="mixbar">${bar}</div>
    <div style="font-size:12.5px;color:var(--dim);margin-bottom:12px">${mixTxt || '—'}</div>
    ${kv}`;
}

/* ---- summary table: the count-vs-subscriber inversion ---- */
(function table() {
  const tb = document.querySelector('#tbl tbody');
  ROOT.c.forEach(m => {
    const liveSubs = m.mix.live || 0;
    tb.insertAdjacentHTML('beforeend', `<tr>
      <td class="mech">${esc(m.n)}<small>${esc(m.note || '')}</small></td>
      <td class="num">${m.cnt}</td>
      <td class="num">${(m.cnt/T.feeds*100).toFixed(1)}%</td>
      <td class="num">${m.subs}</td>
      <td class="num">${(m.subs/T.subs*100).toFixed(1)}%</td>
      <td class="num" style="color:${liveSubs/m.subs > .8 ? C.live : liveSubs/m.subs < .2 ? C.broken : C.stale}">
        ${(liveSubs/m.subs*100).toFixed(1)}%</td>
    </tr>`);
  });
  document.getElementById('cap').innerHTML =
    `探测于 ${T.probed}。${T.feeds} 个订阅源中：` +
    ORDER.map(k => `<span style="color:${C[k]}">${HN[k]} ${T[k]}</span>`).join('、') + `。` +
    `注意「占源数」和「占订阅数」两列是倒挂的 —— Nitter/xcancel 中转占了 ` +
    `<b>20.8% 的订阅源，却只占 9.2% 的订阅</b>：批量导入的中转源在目录里堆积的速度，` +
    `远快于真有人去订阅它们的速度。只有 13 个源订阅数为 0，所以按订阅数加权几乎没有藏住任何东西。`;
})();

document.querySelectorAll('#metric button').forEach(b => b.onclick = () => {
  document.querySelectorAll('#metric button').forEach(x => x.classList.remove('on'));
  b.classList.add('on'); metric = b.dataset.m; render(); detail(focus);
});
document.getElementById('q').oninput = e => { query = e.target.value; render(); };
document.getElementById('reset').onclick = () => { path = [ROOT]; focus = ROOT; render(); detail(ROOT); };

render(); detail(ROOT);
</script>
</body>
</html>
"""

open(PAGE, "w").write(HTML.replace("__DATA__", DATA))
print("wrote", PAGE, len(HTML) + len(DATA), "bytes")
