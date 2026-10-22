<script src="engine.js"></script>
<script>
(() => {
const $ = id => document.getElementById(id);
const E = window.Engine;
const BUILTIN = {
  flex25:{label:'LucidFlex 25K',target:1250,mll:1000,dll:600,cap:600,consist:50,maxQty:20,evDays:20,price:39,reset:45},
  flex50:{label:'LucidFlex 50K',target:3000,mll:2000,dll:1200,cap:1400,consist:50,maxQty:40,evDays:20,price:69,reset:80},
  pro25:{label:'LucidPro 25K',target:1250,mll:1000,dll:600,cap:600,consist:50,maxQty:20,evDays:20,price:64.8,reset:75},
  pro50:{label:'LucidPro 50K',target:3000,mll:2000,dll:1200,cap:1400,consist:50,maxQty:40,evDays:20,price:103.2,reset:120}
};
const FIRM_FIELDS=['target','mll','dll','cap','consist','maxQty','evDays','price','reset'];
const MK = {mnq:{pv:2,tick:0.25,name:'MNQ'}, mes:{pv:5,tick:0.25,name:'MES'}};
const SESS = {all:null,rth:[9,10,11,12,13,14,15],nyo:[9,10,11],ldn:[3,4,5,6,7,8,9,10,11],ovn:[18,19,20,21,22,23,0,1,2],eve:[18,19,20,21,22,23]};
const DATA = {bars:{}, v10:{}};
let state = {mkt:'mnq', strat:'orb'};
let last = null; // last run results for the chart
const fields = ['orMin','stopMode','tgtR','risk','lastEntry','slip','both','pbOr','pbNeed','pbDepth','pbTgt','pbRisk','pbMax','pbLast','pbSlip','pbFlip','tp1','rr','mb','atr','htf','mult','sess','preset','target','mll','dll','cap','consist','maxQty','evDays','price','reset','comm','from','to'];

// ----- custom firm presets (saved in this browser) -----
function loadCustom(){ try{ return JSON.parse(localStorage.getItem('evalLabFirms')||'{}')||{}; }catch(e){ return {}; } }
function saveCustom(o){ try{ localStorage.setItem('evalLabFirms',JSON.stringify(o)); return true; }catch(e){ return false; } }
function allPresets(){ const c=loadCustom(); const o={...BUILTIN}; Object.entries(c).forEach(([k,v])=>o[k]=v); return o; }
function fillPresetSelect(sel){
  const P=allPresets(); const s=$('preset');
  s.innerHTML=Object.entries(P).map(([k,v])=>`<option value="${k}">${esc(v.label)}${k.startsWith('c_')?' (saved)':''}</option>`).join('')+'<option value="custom">Custom (unsaved)</option>';
  s.value = sel && (P[sel]||sel==='custom') ? sel : 'flex25';
}
function esc(t){ return String(t).replace(/[&<>"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c])); }
function applyPreset(k){ const v=allPresets()[k]; if(!v) return; FIRM_FIELDS.forEach(f=>{ if(v[f]!==undefined) $(f).value=v[f]; }); }

function save(){ try{ const o={mkt:state.mkt,strat:state.strat}; fields.forEach(f=>{const e=$(f); o[f]= e.type==='checkbox'?e.checked:e.value}); localStorage.setItem('evalLab',JSON.stringify(o)); }catch(e){} }
function restore(){ try{ const o=JSON.parse(localStorage.getItem('evalLab')||'null'); if(!o) return false;
  fields.forEach(f=>{ if(o[f]===undefined||f==='preset') return; const e=$(f); if(e.type==='checkbox') e.checked=o[f]; else e.value=o[f]; });
  fillPresetSelect(o.preset); state.mkt=o.mkt||'mnq'; state.strat=o.strat||'orb'; return true; }catch(e){ return false; } }
function setSeg(id,v){ document.querySelectorAll('#'+id+' button').forEach(b=>b.setAttribute('aria-pressed', b.dataset.v===v?'true':'false')); }

async function getText(url){ const r=await fetch(url); if(!r.ok) throw new Error('data file missing ('+url+')'); return await r.text(); }
async function loadBars(m){ if (DATA.bars[m]) return DATA.bars[m]; return DATA.bars[m]=E.parseBars(await getText(m+'_rth.txt')); }
async function loadV10(m){ if (DATA.v10[m]!==undefined) return DATA.v10[m]; try{ DATA.v10[m]=JSON.parse(await getText('v10_'+m+'.json')); }catch(e){ DATA.v10[m]=null; } return DATA.v10[m]; }

function simV10(days, J, P){
  const out=new Map(); days.forEach(x=>out.set(x.d,[]));
  const idx=J.cfg.findIndex(c=>c[0]==P.tp1 && c[1]==P.rr && c[2]==P.mb && c[3]==P.atr && c[4]==P.htf);
  if (idx<0) return out;
  const t=J.tr[idx], hs=SESS[P.sess];
  for (let i=0;i<t.length;i+=3){ const d=t[i], h=t[i+1]; if (!out.has(d)) continue; if (hs && !hs.includes(h)) continue; out.get(d).push({pnl:t[i+2]*P.mult, hour:h}); }
  return out;
}

const fmt$ = v => (v<0?'-$':'$')+Math.abs(Math.round(v)).toLocaleString('en-US');
const pct = v => Math.round(v*100)+'%';
const dstr = d => { const s=String(d); return new Date(+s.slice(0,4), +s.slice(4,6)-1, +s.slice(6,8)).toLocaleDateString('en-CA',{weekday:'short',month:'short',day:'numeric',year:'numeric'}); };
const iso = d => { const s=String(d); return s.slice(0,4)+'-'+s.slice(4,6)+'-'+s.slice(6,8); };
const hm = t => { const h=Math.floor(t/100), m=t%100; return h+':'+String(m).padStart(2,'0'); };
const q = (a,x) => a.length? a[Math.min(a.length-1,Math.floor(x*(a.length-1)))] : null;
function readF(){ const o={}; FIRM_FIELDS.forEach(f=>o[f]=+$(f).value); o.evDays=Math.max(1,o.evDays||20); return o; }

let timer=null; function schedule(){ clearTimeout(timer); timer=setTimeout(run,180); }

async function run(){
  save();
  const st=$('status'); st.className='status'; st.textContent='Calculating…';
  try{
    const mk=MK[state.mkt]; const all=await loadBars(state.mkt);
    const from=+($('from').value||'2021-10').replace('-','')*100, to=+($('to').value||'2026-10').replace('-','')*100+31;
    const days=all.filter(x=>x.d>=from && x.d<=to); const dayList=days.map(x=>x.d);
    const F=readF(); const comm=+$('comm').value||0;
    let dt, label;
    if (state.strat==='orb'){
      dt=E.simORB(days,{orMin:+$('orMin').value,stopMode:$('stopMode').value,tgtR:+$('tgtR').value,risk:+$('risk').value,lastEntry:+$('lastEntry').value,slip:+$('slip').value,both:$('both').checked,comm,maxQty:F.maxQty},mk);
      label='Opening range breakout';
    } else if (state.strat==='pb'){
      dt=E.simPB(days,{orMin:+$('pbOr').value,need:+$('pbNeed').value,depth:+$('pbDepth').value,tgtR:+$('pbTgt').value,risk:+$('pbRisk').value,maxTrades:+$('pbMax').value,lastEntry:+$('pbLast').value,slip:+$('pbSlip').value,flip:$('pbFlip').checked,comm,maxQty:F.maxQty,minStop:8,dayStop:F.dll},mk);
      label='ORB + Wade pullback';
    } else {
      const J=await loadV10(state.mkt);
      if (!J){ st.className='status err'; st.textContent='Wade V10 results for '+mk.name+' are missing.'; return; }
      dt=simV10(days,J,{tp1:+$('tp1').value,rr:+$('rr').value,mb:+$('mb').value,atr:+$('atr').value,htf:+$('htf').value,sess:$('sess').value,mult:+$('mult').value});
      label='Wade V10';
    }
    if (dayList.length<=F.evDays){ st.className='status err'; st.textContent='Pick a period longer than the eval length.'; return; }
    const ev=E.evals(dayList,dt,F), S=E.summarize(ev), R=E.randomBaseline(dayList,dt,F);
    last={days,dayList,dt,mk,label,strat:state.strat};
    render(dayList,dt,ev,S,R,F,mk,label);
    const cd=$('chartDay'); cd.min=iso(dayList[0]); cd.max=iso(dayList[dayList.length-1]);
    let cur=+String(cd.value||'').replace(/-/g,''); if(!dayList.includes(cur)){ cur=[...dayList].reverse().find(d=>(dt.get(d)||[]).length)||dayList[dayList.length-1]; }
    showDay(cur);
    st.textContent=mk.name+' · '+dayList.length+' trading days · '+S.n.toLocaleString()+' evals simulated';
  }catch(e){ st.className='status err'; st.textContent='Could not run: '+e.message; console.error(e); }
}

function render(dayList,dt,ev,S,R,F,mk,label){
  const np=Math.round(S.p*100), nf=Math.round(S.f*100); const w=$('waffle'); w.innerHTML='';
  for(let i=0;i<100;i++){ const c=document.createElement('i'); c.className= i<np?'c-pass': i<np+nf?'c-fail':'c-open'; w.appendChild(c); }
  $('bigline').innerHTML=`<b class="p">${np} pass</b>, <b class="f">${nf} fail</b>, <b class="o">${100-np-nf} unfinished</b> within ${F.evDays} trading days.`;
  const edge=S.p-R.p, failGap=S.f-R.f;
  let cls='bad', txt='Worse than luck. Random entries would pass more often.';
  if (edge>=0.08 && failGap<=0.02){ cls='good'; txt='Beats luck clearly.'; } else if (edge>0.02){ cls='mid'; txt='Slightly better than luck. Thin edge.'; }
  $('verdictLine').innerHTML=`<span class="pill ${cls}">${txt}</span> <span class="hint">${label} on ${mk.name}</span>`;
  const barH=s=>`<div class="bar"><span class="c-pass" style="width:${s.p*100}%"></span><span class="c-fail" style="width:${s.f*100}%"></span><span class="c-open" style="width:${s.o*100}%"></span></div>`;
  $('cmp').innerHTML=`<div><div class="lab"><span>This strategy</span><span class="mono">${pct(S.p)} pass · ${pct(S.f)} fail</span></div>${barH(S)}</div>
    <div><div class="lab"><span>Random entries (luck only)</span><span class="mono">${pct(R.p)} pass · ${pct(R.f)} fail</span></div>${barH(R)}</div>`;
  let net=0,n=0,wins=0,gw=0,gl=0,eq=0,pk=0,dd=0; const curve=[];
  dayList.forEach(d=>{ const tl=dt.get(d)||[]; let s=0; tl.forEach(t=>{ const p=E.pnlOf(t); n++; net+=p; s+=p; if(p>0){wins++;gw+=p}else gl-=p; }); eq+=s; pk=Math.max(pk,eq); dd=Math.max(dd,pk-eq); curve.push([d,eq]); });
  const pf= gl? gw/gl : (gw? Infinity:0);
  const tries=S.p>0?(S.p+S.f)/S.p:null; const cost=tries? F.price+Math.max(0,tries-1)*F.reset:null;
  const med=q(S.pd,0.5), p25=q(S.pd,0.25), p75=q(S.pd,0.75);
  const K=[
    ['Typical days to pass', med!==null? med+' days':'none', med!==null? `fastest quarter: ${p25} days or less · slowest quarter: ${p75}+`:'no eval passed'],
    ['Evals per funded account', tries? tries.toFixed(1):'n/a', cost? `about ${fmt$(cost)} in eval + resets`:'never passed'],
    ['Net profit', fmt$(net), `${n.toLocaleString()} trades · ${(n/Math.max(1,dayList.length)).toFixed(1)} per day`],
    ['Win rate', n? pct(wins/n):'n/a', `profit factor ${isFinite(pf)? pf.toFixed(2):'∞'}`],
    ['Worst drawdown', fmt$(-dd), 'largest drop from a high, whole period']
  ];
  $('kpis').innerHTML=K.map(k=>`<div class="kpi"><span class="k">${k[0]}</span><span class="v">${k[1]}</span><span class="d">${k[2]}</span></div>`).join('');
  const Y=new Map(); const yo=y=>{ if(!Y.has(y)) Y.set(y,{n:0,p:0,f:0,net:0,t:0}); return Y.get(y); };
  ev.forEach(e=>{ const o=yo(Math.floor(e.start/10000)); o.n++; if(e.res===1)o.p++; else if(e.res===-1)o.f++; });
  dayList.forEach(d=>{ const o=yo(Math.floor(d/10000)); const tl=dt.get(d)||[]; tl.forEach(t=>o.net+=E.pnlOf(t)); o.t+=tl.length; });
  let beat=0,cnt=0; const rows=[...Y.entries()].sort((a,b)=>a[0]-b[0]).map(([y,o])=>{ const pp=o.n?o.p/o.n:0, ff=o.n?o.f/o.n:0; if(o.n){cnt++; if(pp>R.p) beat++;}
    return `<tr><td>${y}</td><td class="mono">${o.t}</td><td class="mono ${o.net>=0?'pos':'neg'}">${fmt$(o.net)}</td><td class="mono">${o.n?pct(pp):'-'}</td><td class="mono">${o.n?pct(ff):'-'}</td></tr>`; }).join('');
  $('yearTbl').innerHTML=`<thead><tr><th>Year</th><th>Trades</th><th>Net</th><th>Pass</th><th>Fail</th></tr></thead><tbody>${rows}</tbody>`;
  $('yearNote').textContent=`Pass rate beat random entries (${pct(R.p)}) in ${beat} of ${cnt} years.`;
  drawCurve(curve);
  $('eqNote').textContent=`Closed-trade profit from ${dstr(dayList[0])} to ${dstr(dayList[dayList.length-1])}, all trades, no eval resets.`;
  const rec=[]; for(let i=ev.length-1;i>=0 && rec.length<12;i-=3) rec.push(ev[i]);
  $('recentTbl').innerHTML=`<thead><tr><th>Start day</th><th>Result</th><th>Days used</th><th>Balance change</th></tr></thead><tbody>${rec.map(e=>`<tr data-d="${e.start}"><td>${dstr(e.start)}</td><td>${e.res===1?'<span class="tag p">Passed</span>':e.res===-1?'<span class="tag f">Failed</span>':'<span class="tag o">Unfinished</span>'}</td><td class="mono">${e.days}</td><td class="mono ${e.eq>=0?'pos':'neg'}">${fmt$(e.eq)}</td></tr>`).join('')}</tbody>`;
}

function cssv(n){ return getComputedStyle(document.documentElement).getPropertyValue(n).trim(); }
function drawCurve(curve){
  const cv=$('eq'), dpr=window.devicePixelRatio||1, W=cv.clientWidth||800, H=220;
  cv.width=W*dpr; cv.height=H*dpr; const g=cv.getContext('2d'); g.setTransform(dpr,0,0,dpr,0,0); g.clearRect(0,0,W,H);
  if(!curve.length) return;
  const L=62,Rm=10,T=10,B=24; const vals=curve.map(c=>c[1]); let mn=Math.min(0,...vals), mx=Math.max(0,...vals); if(mx===mn) mx=mn+1;
  const x=i=>L+(W-L-Rm)*i/Math.max(1,curve.length-1), y=v=>T+(H-T-B)*(1-(v-mn)/(mx-mn));
  g.font='11px "IBM Plex Mono", monospace'; g.fillStyle=cssv('--muted'); g.strokeStyle=cssv('--grid'); g.lineWidth=1;
  for(let i=0;i<=4;i++){ const v=mn+(mx-mn)*i/4; const yy=y(v); g.beginPath(); g.moveTo(L,yy); g.lineTo(W-Rm,yy); g.stroke(); g.textAlign='right'; g.fillText(fmt$(v),L-6,yy+4); }
  g.strokeStyle=cssv('--muted'); g.setLineDash([3,3]); g.beginPath(); g.moveTo(L,y(0)); g.lineTo(W-Rm,y(0)); g.stroke(); g.setLineDash([]);
  let lastY=null; g.textAlign='center';
  curve.forEach((c,i)=>{ const yr=Math.floor(c[0]/10000); if(yr!==lastY){ lastY=yr; g.fillStyle=cssv('--muted'); g.fillText(yr,Math.min(W-Rm-14,Math.max(L+14,x(i))),H-6); } });
  g.beginPath(); curve.forEach((c,i)=> i? g.lineTo(x(i),y(c[1])) : g.moveTo(x(i),y(c[1])));
  const end=curve[curve.length-1][1]; g.strokeStyle= end>=0? cssv('--pass'):cssv('--fail'); g.lineWidth=1.6; g.stroke();
  g.fillStyle=g.strokeStyle; g.beginPath(); g.arc(x(curve.length-1),y(end),3.5,0,7); g.fill();
}

// ----- candle chart of one day -----
let chartDay=null;
function showDay(d){
  if(!last) return; chartDay=d; $('chartDay').value=iso(d);
  const day=last.days.find(x=>x.d===d); const tl=last.dt.get(d)||[];
  const total=tl.reduce((a,t)=>a+E.pnlOf(t),0);
  $('chartInfo').textContent= day? `${dstr(d)} · ${tl.length} trade${tl.length===1?'':'s'} · ${fmt$(total)}` : 'No data for this day.';
  drawCandles(day, tl);
  const v10 = last.strat==='v10';
  $('dayTbl').innerHTML = tl.length ? `<thead><tr><th>#</th><th>Side</th>${v10?'<th>Entry hour (ET)</th>':'<th>Entry</th><th>Exit</th><th>Contracts</th><th>Exit reason</th>'}<th>P&amp;L</th></tr></thead><tbody>${
    tl.map((t,i)=>{ const p=E.pnlOf(t);
      if (v10) return `<tr><td>${i+1}</td><td>-</td><td class="mono">${t.hour}:00</td><td class="mono ${p>=0?'pos':'neg'}">${fmt$(p)}</td></tr>`;
      const b=day.b; return `<tr><td>${i+1}</td><td>${t.side>0?'<span class="tag p">Long</span>':'<span class="tag f">Short</span>'}</td><td class="mono">${hm(b[t.eI][0])} @ ${t.eP.toFixed(2)}</td><td class="mono">${hm(b[t.xI][0])} @ ${t.xP.toFixed(2)}</td><td class="mono">${t.q}</td><td>${t.why}</td><td class="mono ${p>=0?'pos':'neg'}">${fmt$(p)}</td></tr>`; }).join('')}</tbody>`
    : '<tbody><tr><td>No trades this day.</td></tr></tbody>';
  if (v10) $('chartInfo').textContent += ' · Wade V10 trades show P&L only (pre-computed, many are overnight)';
}
function drawCandles(day, tl){
  const cv=$('candles'), dpr=window.devicePixelRatio||1, W=cv.clientWidth||900, H=360;
  cv.width=W*dpr; cv.height=H*dpr; const g=cv.getContext('2d'); g.setTransform(dpr,0,0,dpr,0,0); g.clearRect(0,0,W,H);
  if(!day) return; const b=day.b;
  const L=8,Rm=72,T=12,B=24; let mn=Infinity,mx=-Infinity; b.forEach(r=>{ mn=Math.min(mn,r[3]); mx=Math.max(mx,r[2]); });
  const tlo = last.strat==='v10'?[]:tl; tlo.forEach(t=>{ mn=Math.min(mn,t.eP,t.xP); mx=Math.max(mx,t.eP,t.xP); });
  const pad=(mx-mn)*0.06||1; mn-=pad; mx+=pad;
  const cw=(W-L-Rm)/b.length; const x=i=>L+cw*(i+0.5); const y=v=>T+(H-T-B)*(1-(v-mn)/(mx-mn));
  g.font='11px "IBM Plex Mono", monospace';
  // grid + price labels
  g.strokeStyle=cssv('--grid'); g.fillStyle=cssv('--muted'); g.lineWidth=1; g.textAlign='left';
  for(let i=0;i<=5;i++){ const v=mn+(mx-mn)*i/5, yy=y(v); g.beginPath(); g.moveTo(L,yy); g.lineTo(W-Rm,yy); g.stroke(); g.fillText(v.toFixed(2),W-Rm+6,yy+4); }
  // time labels each hour
  g.textAlign='center'; b.forEach((r,i)=>{ if(r[0]%100===0) g.fillText(hm(r[0]),x(i),H-6); });
  // opening range box
  if (last.strat!=='v10'){
    const orMin = last.strat==='orb'? +$('orMin').value : +$('pbOr').value; const o=E.orRange(b,orMin);
    g.fillStyle=cssv('--accent-soft'); g.fillRect(L, y(o.hi), W-L-Rm, y(o.lo)-y(o.hi));
    g.strokeStyle=cssv('--accent'); g.setLineDash([4,3]); [o.hi,o.lo].forEach(v=>{ g.beginPath(); g.moveTo(L,y(v)); g.lineTo(W-Rm,y(v)); g.stroke(); }); g.setLineDash([]);
  }
  // candles
  const up=cssv('--pass'), dn=cssv('--fail'); const bw=Math.max(1,cw*0.62);
  b.forEach((r,i)=>{ const [tm,o,h,l,c]=r; const col=c>=o?up:dn; g.strokeStyle=col; g.fillStyle=col;
    g.beginPath(); g.moveTo(x(i),y(h)); g.lineTo(x(i),y(l)); g.stroke();
    const top=y(Math.max(o,c)), hgt=Math.max(1,Math.abs(y(o)-y(c))); g.fillRect(x(i)-bw/2,top,bw,hgt); });
  // trades
  tlo.forEach((t,k)=>{ const col=t.pnl>=0?up:dn, ex=x(t.eI), xx=x(t.xI), ey=y(t.eP), xy=y(t.xP);
    g.strokeStyle=cssv('--ink'); g.setLineDash([2,3]); g.lineWidth=1.2; g.beginPath(); g.moveTo(ex,ey); g.lineTo(xx,xy); g.stroke(); g.setLineDash([]);
    g.fillStyle=t.side>0?up:dn; g.strokeStyle=cssv('--panel'); g.lineWidth=1.5; g.beginPath();
    if(t.side>0){ g.moveTo(ex,ey-1); g.lineTo(ex-7,ey+11); g.lineTo(ex+7,ey+11); } else { g.moveTo(ex,ey+1); g.lineTo(ex-7,ey-11); g.lineTo(ex+7,ey-11); }
    g.closePath(); g.fill(); g.stroke();
    g.fillStyle=col; g.beginPath(); g.arc(xx,xy,5,0,7); g.fill(); g.stroke();
    g.fillStyle=cssv('--ink'); g.textAlign='center'; g.fillText(String(k+1), ex, t.side>0? ey+24 : ey-16); });
}
function stepDay(dir){
  if(!last) return; const L=last.dayList; let i=L.indexOf(chartDay); if(i<0) i=dir>0?-1:L.length;
  for(let j=i+dir;j>=0&&j<L.length;j+=dir){ if((last.dt.get(L[j])||[]).length){ showDay(L[j]); return; } }
}

// ----- wiring -----
document.querySelectorAll('#mkt button').forEach(b=>b.addEventListener('click',()=>{ state.mkt=b.dataset.v; setSeg('mkt',state.mkt); schedule(); }));
document.querySelectorAll('#strat button').forEach(b=>b.addEventListener('click',()=>{ state.strat=b.dataset.v; setSeg('strat',state.strat); showStrat(); schedule(); }));
function showStrat(){ $('orbBox').style.display= state.strat==='orb'?'grid':'none'; $('pbBox').style.display= state.strat==='pb'?'grid':'none'; $('v10Box').style.display= state.strat==='v10'?'grid':'none'; }
$('preset').addEventListener('change',()=>{ const k=$('preset').value; if(k!=='custom'){ applyPreset(k); const v=allPresets()[k]; $('presetName').value = k.startsWith('c_')? v.label : ''; } schedule(); });
FIRM_FIELDS.forEach(f=>$(f).addEventListener('input',()=>{ $('preset').value='custom'; }));
$('savePreset').addEventListener('click',()=>{
  const name=$('presetName').value.trim(); if(!name){ $('presetMsg').textContent='Type a name first, e.g. "Apex 50K".'; return; }
  const c=loadCustom(); const key='c_'+name.toLowerCase().replace(/[^a-z0-9]+/g,'_'); const v={label:name}; FIRM_FIELDS.forEach(f=>v[f]=+$(f).value); c[key]=v;
  if(saveCustom(c)){ fillPresetSelect(key); $('presetMsg').textContent=`Saved "${name}". It stays in this browser's list.`; save(); }
  else $('presetMsg').textContent='This browser blocked saving. Try a normal (not private) window.';
});
$('delPreset').addEventListener('click',()=>{
  const k=$('preset').value; if(!k.startsWith('c_')){ $('presetMsg').textContent='Only your saved presets can be deleted.'; return; }
  const c=loadCustom(); const nm=c[k]&&c[k].label; delete c[k]; saveCustom(c); fillPresetSelect('flex25'); applyPreset('flex25'); $('presetName').value=''; $('presetMsg').textContent=`Deleted "${nm}".`; schedule();
});
fields.forEach(f=>{ if(f==='preset') return; const e=$(f); e.addEventListener('input',schedule); e.addEventListener('change',schedule); });
$('chartDay').addEventListener('change',()=>{ const d=+$('chartDay').value.replace(/-/g,''); if(last && last.dayList.includes(d)) showDay(d); else $('chartInfo').textContent='Market closed or outside the period. Pick another day.'; });
$('chartDay').removeEventListener('input',schedule);
$('prevDay').addEventListener('click',()=>stepDay(-1));
$('nextDay').addEventListener('click',()=>stepDay(1));
$('recentTbl').addEventListener('click',e=>{ const tr=e.target.closest('tr[data-d]'); if(!tr) return; showDay(+tr.dataset.d); $('chartCard').scrollIntoView({behavior:'smooth',block:'start'}); });
let rz=null; window.addEventListener('resize',()=>{ clearTimeout(rz); rz=setTimeout(()=>{ if(last){ showDay(chartDay); } },200); });

fillPresetSelect('flex25');
if (!restore()) applyPreset('flex25');
setSeg('mkt',state.mkt); setSeg('strat',state.strat); showStrat();
run();
})();
</script>
