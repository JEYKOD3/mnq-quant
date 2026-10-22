const E=require('../engine/js/engine.js'), fs=require('fs'); const all=E.parseBars(fs.readFileSync('../data/raw/mnq_rth_5m.txt','utf8')); const MK={pv:2,tick:0.25}; const feat=JSON.parse(fs.readFileSync('dayfeat.json'));
const rt=E.simRT2(all,{risk:400,stop:'opp',tgtR:2,lastEntry:1300,maxTrades:6},MK);
const v4=f=>{ if(f.pdRel>1.2) return 0; const G=Math.abs(f.gap)>=.6, D=Math.abs(f.orDir)>=.6; if(!(G||D)) return 0; return G?Math.sign(f.gap):Math.sign(f.orDir);};
const tm=i=>{const m=570+i*5; return `${Math.floor(m/60)}:${String(m%60).padStart(2,'0')}`;};
let month=null, mt=0, mg=0, mr=0;
for (const d of [...rt.keys()].filter(d=>d>=20260821&&d<=20261020)) {
  const ds=String(d); const mo=ds.slice(0,6); if(mo!==month){ if(month) console.log(`== ${month} total ${Math.round(mt)}  green/red ${mg}/${mr}`); month=mo; mt=0; mg=0; mr=0; console.log(`\n##### ${mo}`); }
  const f=feat[d]; const b=v4(f); const seen=rt.get(d)||[];
  const why = f.pdRel>1.2 ? `prior day range ${f.pdRel.toFixed(2)}ADR > 1.2: skip` : (b===0?`gap ${f.gap.toFixed(2)} / first15 ${f.orDir.toFixed(2)}: not committed, skip`:`gap ${f.gap.toFixed(2)}ADR first15 ${f.orDir.toFixed(2)} -> ${b>0?'LONG':'SHORT'} only`);
  const take=b?seen.filter(t=>t.side===b):[]; const p=take.reduce((s,t)=>s+t.pnl,0); mt+=p; if(take.length){ if(p>0) mg++; else mr++; }
  let line=`${ds.slice(4,6)}/${ds.slice(6)}  ${why}`;
  if (b && !take.length) line+=`  | no retest setup -> no trade` + (seen.length?` (engine saw ${seen.length} against-bias setup(s), ignored)`:'');
  console.log(line);
  for (const t of take) console.log(`      ${t.side>0?'LONG ':'SHORT'} ${tm(t.eI)} @${t.eP}  x${t.q}  exit ${tm(t.xI)} @${t.xP} (${t.why})  hold ${t.hold}m  MFE ${t.mfeR.toFixed(1)}R  P&L ${Math.round(t.pnl)>0?'+':''}${Math.round(t.pnl)}`);
}
console.log(`== ${month} total ${Math.round(mt)}  green/red ${mg}/${mr}`);
