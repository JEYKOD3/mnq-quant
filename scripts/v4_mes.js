const E=require('../engine/js/engine.js'), fs=require('fs'), {report,line}=require('../engine/js/report.js');
const sym=process.argv[2]||'mes'; const all=E.parseBars(fs.readFileSync(`../data/raw/${sym}_rth_5m.txt`,'utf8')); const MK=sym==='mes'?{pv:5,tick:0.25}:{pv:2,tick:0.25}; const feat=JSON.parse(fs.readFileSync(sym==='mes'?'dayfeat_mes.json':'dayfeat.json'));
const v4=f=>{ if(f.pdRel>1.2) return 0; const G=Math.abs(f.gap)>=.6, D=Math.abs(f.orDir)>=.6; if(!(G||D)) return 0; return G?Math.sign(f.gap):Math.sign(f.orDir);};
const sel=(dt)=>{const m=new Map(); dt.forEach((l,d)=>{const f=feat[d]; if(!f) return; const r=v4(f); if(r){const k=l.filter(t=>t.side===r); if(k.length) m.set(d,k);}}); return m;};
for (const [nm,P] of [['V4 retest 2R, $400 risk',{risk:400,stop:'opp',tgtR:2,comm:2.37}],['V4 retest 2R, comm $0.50',{risk:400,stop:'opp',tgtR:2,comm:0.5}]]) {
  const m=sel(E.simRT2(all,P,MK)); console.log(`\n${sym.toUpperCase()} ${nm}`);
  for(const [l,a,z] of [['2022-25',20220101,20251231],['2026',20260101,20261020],['Jun-Oct26',20260601,20261020]]) console.log('  ',l,line(report(m,a,z)));
}
