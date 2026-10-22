const E=require('../engine/js/engine.js'), fs=require('fs'), {report,line}=require('../engine/js/report.js'); const all=E.parseBars(fs.readFileSync('../data/raw/mnq_rth_5m.txt','utf8')); const MK={pv:2,tick:0.25}; const feat=JSON.parse(fs.readFileSync('dayfeat.json'));
const v4=f=>{ if(f.pdRel>1.2) return 0; const G=Math.abs(f.gap)>=.6, D=Math.abs(f.orDir)>=.6; if(!(G||D)) return 0; return G?Math.sign(f.gap):Math.sign(f.orDir);};
const tm=i=>{const m=570+i*5; return `${Math.floor(m/60)}:${String(m%60).padStart(2,'0')}`;};
function runCfg(name,q,P,detail){
  const rt=E.simRT2(all,Object.assign({risk:1e9,maxQty:q,lastEntry:1530,maxTrades:6,dayStop:0,dayTarget:0},P),MK);
  const m=new Map(); rt.forEach((l,d)=>{const f=feat[d]; if(!f) return; const r=v4(f); if(!r) return; const k=l.filter(t=>t.side===r||P.fadeBoth&&t.setup!=='retest'); if(k.length) m.set(d,k);});
  console.log(`\n### ${name}  (${q} contracts)`);
  for(const [l,a,z] of [['2022-25',20220101,20251231],['2026',20260101,20261020]]) console.log('  ',l,line(report(m,a,z)));
  if(detail){ let tot=0,g=0,r=0; for(const d of [...m.keys()].filter(d=>d>=20260821)){ const L=m.get(d); const p=L.reduce((s,t)=>s+t.pnl,0); tot+=p; p>0?g++:r++; const ds=String(d); console.log(`  ${ds.slice(4,6)}/${ds.slice(6)} day ${Math.round(p)>0?'+':''}${Math.round(p)} :: `+L.map(t=>`${t.side>0?'L':'S'} ${tm(t.eI)}@${t.eP} risk/ct ${Math.round(Math.abs(t.eP-(t.stp||0))||0)}pt -> ${tm(t.xI)} ${t.why}${t.tp1?'(tp1 hit)':''} ${Math.round(t.pnl)>0?'+':''}${Math.round(t.pnl)}`).join(' | ')); } console.log(`  2-month total ${Math.round(tot)}  green/red days ${g}/${r}`); }
  return m;
}
const base={stop:'opp',tgtR:2};
const mgd={stop:'structure',bufT:4,minStop:16,maxStopPts:60,tp1R:1,tp1Pct:50,beOn:true,runR:3,trailN:3,trailTrig:1};
runCfg('A. current rules (stop other side, 2R, no TP1)',10,base,false);
runCfg('B. structure stop (max 60pt), TP1 1R 50% -> BE, runner 3R w/ 3-bar trail',10,mgd,true);
runCfg('B. same',20,mgd,false);
runCfg('C. B + fade range edges when range >= 60pt (more trades)',10,Object.assign({},mgd,{bigPts:60,fade:true,fadeBoth:true}),true);
runCfg('C. same',20,Object.assign({},mgd,{bigPts:60,fade:true,fadeBoth:true}),false);
