const E=require('/home/claude/mnq-quant/engine/js/engine.js'), fs=require('fs');
const feat=JSON.parse(fs.readFileSync('/home/claude/mnq-quant/scripts/dayfeat.json')); const MK={pv:2,tick:0.25};
const v4=f=>{ if(!f||f.pdRel>1.2) return 0; const G=Math.abs(f.gap)>=.6, D=Math.abs(f.orDir)>=.6; if(!(G||D)) return 0; return G?Math.sign(f.gap):Math.sign(f.orDir);};
const BIG=1e7;
function trades(tf,tg,mh){ const all=E.parseBars(fs.readFileSync(`/home/claude/mnq-quant/data/tf/rth_${tf}m.txt`,'utf8')); E.setBar(tf); E.setMaxHold(mh);
  const rt=E.simRT2(all,{risk:BIG,stop:'opp',tgtR:tg,maxQty:BIG},MK); E.setMaxHold(0); E.setBar(5);
  const days=all.map(x=>x.d).filter(d=>d>=20220101); const T=new Map();
  for(const d of days){ const s=v4(feat[d]); const t=s?(rt.get(d)||[]).filter(t=>t.side===s)[0]:null; if(t) T.set(d,{pc:t.pnl/t.q, rc:BIG/t.q}); }
  return {days,T}; }
// sizing: mode 'fixed' risk=X ; 'cush' risk=f*(bal-mll) ; cap: win cap for consistency, remaining-target cap
function attempt(S,start,sz,tg){ let bal=50000,peak=50000,best=0,td=0;
  for(const d of S.days){ if(d<start) continue; td++; const mll=Math.min(peak-2000,50000); const t=S.T.get(d);
    if(t){ let budget = sz.mode==='fixed'? sz.x : sz.f*(bal-mll);
      if(sz.cap){ const rem=53000-bal; budget=Math.min(budget, Math.max(rem,300)/tg*1.05, sz.cap/tg); }
      let q=Math.min(40,Math.floor(budget/t.rc)); if(q<1 && t.rc<0.9*(bal-mll)) q=1;
      if(q>=1){ const p=q*t.pc; bal+=p; best=Math.max(best,p); } }
    if(bal<=mll) return {res:'F',td};
    peak=Math.max(peak,bal); const prof=bal-50000; if(prof>=3000 && best<=0.5*prof) return {res:'P',td};
    if(td>=250) return {res:'O',td}; }
  return {res:'O',td}; }
function evalSet(S,sz,tg,a,z){ const starts=S.days.filter((d,i)=>d>=a&&d<=z&&i%5===0); const R=starts.map(s=>attempt(S,s,sz,tg));
  const n=R.length, P=R.filter(r=>r.res==='P'), F=R.filter(r=>r.res==='F');
  const p40=P.filter(r=>r.td<=40).length, p60=P.filter(r=>r.td<=60).length;
  const med=P.length?P.map(r=>r.td).sort((x,y)=>x-y)[Math.floor(P.length/2)]:999;
  return {n,pass:P.length/n,fail:F.length/n,p40:p40/n,p60:p60/n,med}; }
const cfgs=[[1,2,0],[1,2,60],[1,1.5,60],[1,3,0],[5,2,0],[5,1.5,60],[5,1.5,0],[2,1.5,60]];
const sizes=[]; for(const x of [400,600,800,1000,1200,1500]) sizes.push({mode:'fixed',x,lab:`fixed $${x}`});
for(const f of [.25,.35,.5,.7]) { sizes.push({mode:'cush',f,lab:`cushion ${f}`}); sizes.push({mode:'cush',f,cap:1450,lab:`cushion ${f}+caps`}); }
for(const x of [800,1000,1200]) sizes.push({mode:'fixed',x,cap:1450,lab:`fixed $${x}+caps`});
const out=[];
for(const [tf,tg,mh] of cfgs){ const S=trades(tf,tg,mh);
  for(const sz of sizes){ const D=evalSet(S,sz,tg,20220101,20241231), T=evalSet(S,sz,tg,20250101,20260601);
    out.push({cfg:`${tf}m ${tg}R ${mh?mh+'min':'close'}`,sz:sz.lab,D,T}); } }
out.sort((a,b)=>(b.D.p60-b.D.fail)-(a.D.p60-a.D.fail)); const keep=new Set(['1m 2R close','5m 2R close','5m 1.5R close','1m 2R 60min','5m 1.5R 60min']);
const f=x=>String(Math.round(100*x)).padStart(3)+'%';
console.log('Lucid Flex 50K eval, starts every 5 trading days. DEV starts 2022-24, TEST starts 2025-26.06. score=pass within 60 trading days - fail');
console.log('config               sizing              | DEV pass  in40d in60d  fail  medDays | TEST pass in40d in60d fail medDays');
for(const r of out.filter(r=>keep.has(r.cfg)&&!r.sz.includes('caps'))) console.log(r.cfg.padEnd(20), r.sz.padEnd(20), '|', f(r.D.pass),f(r.D.p40),f(r.D.p60),f(r.D.fail),String(r.D.med).padStart(5),' |',f(r.T.pass),f(r.T.p40),f(r.T.p60),f(r.T.fail),String(r.T.med).padStart(5));
fs.writeFileSync('/tmp/claude-0/-home-claude/afdbc088-26a4-5e84-b77d-b387ee40e855/scratchpad/tfopt/evalopt.json',JSON.stringify(out));
