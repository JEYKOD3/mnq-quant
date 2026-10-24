const E=require('../engine/js/engine.js'), fs=require('fs');
const all=E.parseBars(fs.readFileSync('../data/raw/mnq_rth_5m.txt','utf8')); const MK={pv:2,tick:0.25}; const feat=JSON.parse(fs.readFileSync('dayfeat.json'));
const v4=f=>{ if(!f||f.pdRel>1.2) return 0; const G=Math.abs(f.gap)>=.6, D=Math.abs(f.orDir)>=.6; if(!(G||D)) return 0; return G?Math.sign(f.gap):Math.sign(f.orDir);};
const DAYS=all.map(x=>x.d).filter(d=>d>=20220101);
function daily(ver,risk){ E.setMaxHold(ver==='B'?60:0); const rt=E.simRT2(all,{risk,stop:'opp',tgtR:ver==='B'?1.5:2,maxQty:40},MK); E.setMaxHold(0);
  const m=new Map(); for(const d of DAYS){ const s=v4(feat[d]); let p=0; if(s){ for(const t of (rt.get(d)||[]).filter(t=>t.side===s)){ if(p<=-1200) break; p+=t.pnl; } } m.set(d,p);} return m; }
function attempt(dp,start){ let bal=50000,peak=50000,best=0,td=0,trades=0; for(const d of DAYS){ if(d<start) continue; td++; const p=dp.get(d); if(p!==0){trades++;} bal+=p; best=Math.max(best,p);
    const mll=Math.min(peak-2000,50000); if(bal<=mll) return {res:'FAIL',d,td,trades};
    peak=Math.max(peak,bal); const prof=bal-50000; if(prof>=3000 && best<=0.5*prof) return {res:'PASS',d,td,trades}; }
  return {res:'OPEN',td,trades,bal}; }
const starts=[]; let last=''; for(const d of DAYS){ const mo=String(d).slice(0,6); if(mo!==last){ starts.push(d); last=mo; } }
for (const ver of ['B','A']) for (const risk of (process.argv[2]||'300,400,500,1000').split(',').map(Number)) {
  const dp=daily(ver,risk); const R=starts.filter(s=>s<=20260601).map(s=>attempt(dp,s));
  const p=R.filter(r=>r.res==='PASS'), f=R.filter(r=>r.res==='FAIL'), o=R.filter(r=>r.res==='OPEN');
  const med=a=>{const v=a.map(r=>r.td).sort((x,y)=>x-y); return v.length?v[Math.floor(v.length/2)]:'-';};
  const so=attempt(dp,20260901);
  console.log(`ver ${ver} ${ver==='B'?'(1.5R, 60min)':'(2R, hold) '} risk $${risk}: ${R.length} monthly starts 2022-01..2026-06 -> PASS ${p.length} (${Math.round(100*p.length/R.length)}%) median ${med(p)} trading days | FAIL ${f.length} (${Math.round(100*f.length/R.length)}%) median ${med(f)} days | unresolved ${o.length}  || start Sep 1 2026: ${so.res}${so.d?' on '+so.d:''} after ${so.td} days ${so.bal?'bal '+Math.round(so.bal):''}`);
}
// detail for B $400 starting Sep 1
const dp=daily('B',400); let bal=50000; console.log('\nDetail ver B risk $400 from Sep 1 2026:'); for(const d of DAYS){ if(d<20260901) continue; const p=dp.get(d); if(p){ bal+=p; console.log(d, (p>0?'+':'')+Math.round(p), Math.round(bal)); } }
