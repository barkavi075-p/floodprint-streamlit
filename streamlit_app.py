import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="FloodPrint", layout="wide")

HTML_PAGE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>FloodPrint — Live Watchlist</title>
<link href="https://fonts.googleapis.com/css2?family=Manrope:wght@500;700;800&family=IBM+Plex+Mono:wght@400;600&display=swap" rel="stylesheet">
<style>
  :root{
    --bg:#0D1B24; --panel:#142B38; --panel-alt:#1B394A; --line:#24475A;
    --text:#EAF2F4; --muted:#8FA9B5; --water:#4FB8D6;
    --low:#4FAE7C; --med:#E3A83B; --high:#D9534F;
    --flood:rgba(79,184,214,0.14);
    box-sizing:border-box;
    padding-top:env(safe-area-inset-top,0px); padding-bottom:env(safe-area-inset-bottom,0px);
  }
  @media (prefers-color-scheme: light){
    :root:not([data-theme="dark"]){
      --bg:#F3F7F8; --panel:#FFFFFF; --panel-alt:#EAF1F3; --line:#D6E2E6;
      --text:#12262E; --muted:#5A727B; --flood:rgba(79,184,214,0.18);
    }
  }
  html{scroll-padding-top:env(safe-area-inset-top,0px); height:100%;}
  *{box-sizing:border-box;}
  body{
    margin:0; background:var(--bg); color:var(--text);
    font-family:"Manrope",system-ui,-apple-system,Segoe UI,sans-serif;
    height:100%; -webkit-font-smoothing:antialiased;
  }
  .mono{font-family:"IBM Plex Mono",ui-monospace,Menlo,monospace;}

  header{
    padding:18px 24px calc(14px + env(safe-area-inset-top,0px));
    padding-top:calc(18px + env(safe-area-inset-top,0px));
    border-bottom:1px solid var(--line);
    display:flex; align-items:center; justify-content:space-between; gap:16px; flex-wrap:wrap;
  }
  .brand{display:flex; align-items:baseline; gap:10px;}
  .brand h1{margin:0; font-size:1.15rem; font-weight:800; letter-spacing:.01em;}
  .brand span{color:var(--muted); font-size:.82rem;}
  .stats{display:flex; gap:22px; flex-wrap:wrap;}
  .stat{text-align:right;}
  .stat b{display:block; font-size:1.15rem; font-weight:700;}
  .stat small{color:var(--muted); font-size:.72rem;}

  main{
    display:grid; grid-template-columns:1.55fr 1fr; gap:1px; background:var(--line);
    min-height:calc(100vh - 78px);
  }
  @media (max-width:880px){ main{grid-template-columns:1fr;} }

  .map-pane{background:var(--bg); padding:18px; display:flex; flex-direction:column; gap:12px;}
  .map-head{display:flex; justify-content:space-between; align-items:baseline; gap:12px; flex-wrap:wrap;}
  .map-head h2{margin:0; font-size:.95rem; font-weight:700;}
  .map-head p{margin:2px 0 0; color:var(--muted); font-size:.78rem;}
  .legend{display:flex; gap:14px; flex-wrap:wrap; font-size:.72rem; color:var(--muted);}
  .legend i{display:inline-block; width:8px; height:8px; border-radius:50%; margin-right:5px; vertical-align:middle;}

  svg.mapsvg{width:100%; height:auto; background:var(--panel); border-radius:10px; border:1px solid var(--line);}
  .river{fill:none; stroke:var(--water); stroke-width:7; stroke-linecap:round;}
  .floodband{fill:none; stroke:var(--flood); stroke-width:70; stroke-linecap:round;}
  .wetland{fill:var(--flood); stroke:var(--water); stroke-width:1.5; opacity:.9;}
  .site{cursor:pointer; transition:transform .18s ease;}
  .site circle.core{stroke:var(--bg); stroke-width:2;}
  .site.dim{opacity:.28;}
  .site.active circle.core{transform-origin:center; }
  .ring{fill:none; stroke-width:2; opacity:0;}
  .site.active .ring{opacity:.9; animation:pulse 1.4s ease-out infinite;}
  @keyframes pulse{
    0%{ r:12; opacity:.8; }
    100%{ r:26; opacity:0; }
  }
  .sitelabel{font-size:9px; fill:var(--muted); font-family:"IBM Plex Mono",monospace;}

  .side{background:var(--panel); display:flex; flex-direction:column; min-height:0;}
  .side-head{padding:16px 18px 10px; border-bottom:1px solid var(--line);}
  .side-head h2{margin:0 0 4px; font-size:.95rem; font-weight:700;}
  .side-head p{margin:0; color:var(--muted); font-size:.78rem;}
  .filters{display:flex; gap:6px; padding:12px 18px 0; flex-wrap:wrap;}
  .filters button{
    background:var(--panel-alt); border:1px solid var(--line); color:var(--text);
    font-family:inherit; font-size:.74rem; padding:6px 11px; border-radius:20px; cursor:pointer;
  }
  .filters button.on{background:var(--water); border-color:var(--water); color:#04222c; font-weight:700;}

  .list{list-style:none; margin:0; padding:10px 10px 16px; overflow-y:auto; flex:1;}
  .row{
    padding:12px 12px; border-radius:9px; cursor:pointer; margin-bottom:6px;
    border:1px solid transparent; transition:background .15s, border-color .15s;
  }
  .row:hover{background:var(--panel-alt);}
  .row.sel{background:var(--panel-alt); border-color:var(--water);}
  .row-top{display:flex; justify-content:space-between; gap:10px; align-items:baseline;}
  .row-top strong{font-size:.88rem;}
  .risk{font-size:.78rem; font-weight:700; padding:1px 8px; border-radius:12px;}
  .row-meta{display:flex; justify-content:space-between; color:var(--muted); font-size:.72rem; margin-top:5px;}
  .row.hide{display:none;}

  .detail{border-top:1px solid var(--line); padding:16px 18px calc(18px + env(safe-area-inset-bottom,0px)); font-size:.82rem;}
  .detail h3{margin:0 0 6px; font-size:.92rem;}
  .detail .status{display:inline-block; font-size:.72rem; padding:2px 9px; border-radius:10px; margin-bottom:8px;}
  .detail dl{display:grid; grid-template-columns:auto 1fr; gap:4px 12px; margin:0; color:var(--muted);}
  .detail dt{font-size:.72rem;}
  .detail dd{margin:0; color:var(--text); text-align:right; font-family:"IBM Plex Mono",monospace; font-size:.78rem;}

  footer{padding:10px 24px calc(12px + env(safe-area-inset-bottom,0px)); color:var(--muted); font-size:.72rem; border-top:1px solid var(--line);}
</style>
</head>
<body>

<header>
  <div class="brand">
    <h1>FloodPrint</h1>
    <span>Live watchlist — prototype demo</span>
  </div>
  <div class="stats">
    <div class="stat"><b class="mono" id="statTotal">–</b><small>sites flagged</small></div>
    <div class="stat"><b class="mono" id="statHigh">–</b><small>high risk</small></div>
    <div class="stat"><b class="mono" id="statPop">–</b><small>people downstream</small></div>
  </div>
</header>

<main>
  <section class="map-pane">
    <div class="map-head">
      <div>
        <h2>Test Basin — Sector 4</h2>
        <p>Change-detection pass · imagery refreshed 6 days ago</p>
      </div>
      <div class="legend">
        <span><i style="background:var(--high)"></i>High risk</span>
        <span><i style="background:var(--med)"></i>Medium</span>
        <span><i style="background:var(--low)"></i>Low</span>
        <span><i style="background:var(--water)"></i>River / drainage</span>
      </div>
    </div>
    <svg class="mapsvg" viewBox="0 0 1000 650" id="mapsvg">
      <path class="floodband" d="M 60,40 C 200,100 150,220 280,280 C 420,350 380,450 520,500 C 620,540 700,560 940,610"/>
      <ellipse class="wetland" cx="700" cy="410" rx="95" ry="55"/>
      <path class="river" d="M 60,40 C 200,100 150,220 280,280 C 420,350 380,450 520,500 C 620,540 700,560 940,610"/>
      <text x="705" y="345" class="sitelabel">tank bed</text>
      <g id="sites"></g>
    </svg>
  </section>

  <section class="side">
    <div class="side-head">
      <h2>Ranked watchlist</h2>
      <p>Sorted by risk score · tap a site to inspect</p>
    </div>
    <div class="filters" id="filters">
      <button class="on" data-f="all">All</button>
      <button data-f="high">High</button>
      <button data-f="med">Medium</button>
      <button data-f="low">Low</button>
    </div>
    <ul class="list" id="list"></ul>
    <div class="detail" id="detail"></div>
  </section>
</main>

<footer>Synthetic demo data over an illustrative test basin — for prototype walkthrough only, not live imagery.</footer>

<script>
const sites = [
  {id:"A", name:"Riverside Residency", x:300, y:300, risk:92, pop:18400, type:"Residential complex (240 units)", status:"Illegal — floodplain", detected:"14 Aug 2026", dist:"2.1 km downstream"},
  {id:"E", name:"Metro Logistics Hub", x:150, y:150, risk:88, pop:2300, type:"Logistics warehouse", status:"Illegal — dry tank bed", detected:"02 Sep 2026", dist:"6.8 km downstream"},
  {id:"B", name:"Greenfield Warehouse", x:500, y:480, risk:78, pop:6200, type:"Warehouse cluster", status:"Unpermitted", detected:"22 Jul 2026", dist:"4.4 km downstream"},
  {id:"G", name:"Northside Extension", x:240, y:220, risk:70, pop:7500, type:"Housing layout (extension)", status:"Unpermitted", detected:"30 Aug 2026", dist:"5.9 km downstream"},
  {id:"C", name:"Lakeview Homes Ph2", x:680, y:420, risk:65, pop:9800, type:"Housing project, phase 2", status:"Under review", detected:"10 Sep 2026", dist:"3.5 km downstream"},
  {id:"D", name:"Sunrise Apartments", x:420, y:350, risk:54, pop:4100, type:"Apartment block", status:"Permit pending", detected:"18 Jun 2026", dist:"3.9 km downstream"},
  {id:"F", name:"Palm Grove Layout", x:780, y:540, risk:41, pop:3000, type:"Plotted layout", status:"Under review", detected:"05 Sep 2026", dist:"7.6 km downstream"}
];
sites.sort((a,b)=>b.risk-a.risk);

function tier(r){ return r>=75?"high":(r>=50?"med":"low"); }
const col = {high:"var(--high)", med:"var(--med)", low:"var(--low)"};

document.getElementById("statTotal").textContent = sites.length;
document.getElementById("statHigh").textContent = sites.filter(s=>tier(s.risk)==="high").length;
document.getElementById("statPop").textContent = sites.reduce((a,s)=>a+s.pop,0).toLocaleString();

const sitesG = document.getElementById("sites");
sites.forEach(s=>{
  const g = document.createElementNS("http://www.w3.org/2000/svg","g");
  g.setAttribute("class","site"); g.setAttribute("data-id",s.id); g.setAttribute("data-tier",tier(s.risk));
  const r = 6 + Math.min(s.pop,20000)/20000*6;
  g.innerHTML = `<circle class="ring" cx="${s.x}" cy="${s.y}" r="12" stroke="${col[tier(s.risk)]}"/>
    <circle class="core" cx="${s.x}" cy="${s.y}" r="${r.toFixed(1)}" fill="${col[tier(s.risk)]}"/>`;
  g.addEventListener("click", ()=>select(s.id));
  sitesG.appendChild(g);
});

const list = document.getElementById("list");
sites.forEach(s=>{
  const li = document.createElement("li");
  li.className="row"; li.dataset.id=s.id; li.dataset.tier=tier(s.risk);
  li.innerHTML = `<div class="row-top"><strong>${s.name}</strong>
      <span class="risk mono" style="background:${col[tier(s.risk)]}22; color:${col[tier(s.risk)]}">${s.risk}</span></div>
    <div class="row-meta"><span>${s.type}</span><span class="mono">${s.pop.toLocaleString()} downstream</span></div>`;
  li.addEventListener("click", ()=>select(s.id));
  list.appendChild(li);
});

const detail = document.getElementById("detail");
function select(id){
  const s = sites.find(x=>x.id===id);
  document.querySelectorAll(".site").forEach(g=>g.classList.toggle("active", g.dataset.id===id));
  document.querySelectorAll(".row").forEach(r=>r.classList.toggle("sel", r.dataset.id===id));
  detail.innerHTML = `<h3>${s.name}</h3>
    <span class="status" style="background:${col[tier(s.risk)]}22; color:${col[tier(s.risk)]}">${s.status}</span>
    <dl>
      <dt>Risk score</dt><dd>${s.risk} / 100</dd>
      <dt>Downstream population</dt><dd>${s.pop.toLocaleString()}</dd>
      <dt>Distance</dt><dd>${s.dist}</dd>
      <dt>Detected</dt><dd>${s.detected}</dd>
      <dt>Construction type</dt><dd>${s.type}</dd>
    </dl>`;
}
select(sites[0].id);

document.getElementById("filters").addEventListener("click", e=>{
  const btn = e.target.closest("button"); if(!btn) return;
  document.querySelectorAll("#filters button").forEach(b=>b.classList.remove("on"));
  btn.classList.add("on");
  const f = btn.dataset.f;
  document.querySelectorAll(".row").forEach(r=> r.classList.toggle("hide", f!=="all" && r.dataset.tier!==f));
  document.querySelectorAll(".site").forEach(g=> g.classList.toggle("dim", f!=="all" && g.dataset.tier!==f));
});
</script>
</body>
</html>
"""

components.html(HTML_PAGE, height=900, scrolling=True)
