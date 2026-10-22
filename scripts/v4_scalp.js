const E=require('../engine/js/engine.js'), fs=require('fs'), {report,line}=require('../engine/js/report.js'); const all=E.parseBars(fs.readFileSync('../data/raw/mnq_rth_5m.txt','utf8')); const MK={pv:2,tick:0.25}; const feat=JSON.parse(fs.readFileSync('dayfeat.json'));
const v4=f=>{ if(f.pdRel>1.2) return 0; const G=Math.abs(f.gap)>=.6, D=Math.abs(f.orDir)>=.6; if(!(G||D)) return 0; return G?Math.sign(f.gap):Math.sign(f.orDir);};
const tm=i=>{const m=570+i*5; return `${Math.floor(m/60)}:${String(m%60).padStart(2,'0')}`;};
function runCfg(name,q,P,hold,detail){
  E.setMaxHold(hold);
  const rt=E.simRT2(all,Object.assign({risk:1e9,maxQty:q,lastEntry:1530,maxTrades:6,dayStop:0,dayTarget:0},P),MK);
  E.setMaxHold(0);
  const m=new Map(); rt.forEach((l,d)=>{const f=feat[d]; if(!f) return; const r=v4(f); if(!r) return; const k=l.filter(t=>t.side===r); if(k.length) m.set(d,k);});
  console.log(`\n### ${name} | ${q} ct | max hold ${hold}m`);
  for(const [l,a,z] of [['2022-25',20220101,20251231],['2026',20260101,20261020]]) console.log('  ',l,line(report(m,a,z)));
  if(detail){ let tot=0,g=0,r=0; for(const d of [...m.keys()].filter(d=>d>=20260921)){ const L=m.get(d); const p=L.reduce((s,t)=>s+t.pnl,0); tot+=p; p>0?g++:r++; const ds=String(d); console.log(`  ${ds.slice(4,6)}/${ds.slice(6)} ${Math.round(p)>0?'+':''}${Math.round(p)} :: `+L.map(t=>`${t.side>0?'L':'S'} ${tm(t.eI)}@${t.eP} r=${Math.round(t.r||0)}pt -> ${tm(t.xI)} ${t.why}${t.tp1?'(tp1)':''} ${Math.round(t.pnl)>0?'+':''}${Math.round(t.pnl)}`).join(' | ')); } console.log(`  last-month total ${Math.round(tot)}  green/red ${g}/${r}`); }
}
const A={stop:'opp',tgtR:2};
const S1={stop:'structure',bufT:4,minStop:16,maxStopPts:40,tp1R:1,tp1Pct:50,beOn:true,runR:2};
const S2={stop:'structure',bufT:4,minStop:16,maxStopPts:40,tp1R:1,tp1Pct:50,beOn:true,runR:2,trailN:2,trailTrig:1};
const S3={stop:'structure',bufT:4,minStop:16,maxStopPts:40,tgtR:1.5};
for (const [nm,P] of [['A opp-stop 2R',A],['S1 struct<=40pt TP1 1R 50% BE runner 2R',S1],['S2 S1 + 2-bar trail',S2],['S3 struct<=40pt plain 1.5R',S3]]) for (const h of [30,60]) runCfg(nm,10,P,h,nm.startsWith('S1')&&h===30);
runCfg('S1',20,S1,30,false);
