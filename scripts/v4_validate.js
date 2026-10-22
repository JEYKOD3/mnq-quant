// V4 validation: cost sweep, by-year walk, parameter plateau around gap .6 / dir .6 / pd 1.2
const E=require('../engine/js/engine.js'), fs=require('fs'), {report,line}=require('../engine/js/report.js');
const all=E.parseBars(fs.readFileSync('../data/raw/mnq_rth_5m.txt','utf8')); const MK={pv:2,tick:0.25}; const feat=JSON.parse(fs.readFileSync('dayfeat.json'));
const sel=(dt,ok)=>{const m=new Map(); dt.forEach((l,d)=>{const f=feat[d]; if(!f) return; const r=ok(f); if(r) m.set(d,l.filter(t=>t.side===r));}); return m;};
const v4=(g,dd,pd)=>f=>{ if(pd>0&&f.pdRel>pd) return 0; const G=Math.abs(f.gap)>=g, D=Math.abs(f.orDir)>=dd; if(!(G||D)) return 0; return G?Math.sign(f.gap):Math.sign(f.orDir);};
const sum=(m,a,z)=>{const r=report(m,a,z); return r;};
console.log('--- cost sweep (slip ticks per side; comm 2.37 fixed) ---');
for (const slip of [0,1,2,3,4]) {
  const rt=E.simRT2(all,{risk:400,stop:'opp',tgtR:2,slip},MK); const m=sel(rt,v4(.6,.6,1.2));
  console.log(`slip ${slip}tk: 2022-25 ${line(report(m,20220101,20251231))}`); console.log(`         2026    ${line(report(m,20260101,20261020))}`);
}
const rt=E.simRT2(all,{risk:400,stop:'opp',tgtR:2},MK);
console.log('--- by year ---');
for (const y of [2022,2023,2024,2025,2026]) console.log(y, line(report(sel(rt,v4(.6,.6,1.2)),y*10000+101,y*10000+1231)));
console.log('--- plateau (2022-26 all): gap x dir, pd 1.2 ---');
for (const g of [.4,.5,.6,.7,.8]) { let row=`gap ${g}: `; for (const d of [.4,.5,.6,.7,.8]) { const r=report(sel(rt,v4(g,d,1.2)),20220101,20261020); row+=`d${d} PF${r.pf.toFixed(2)} n${r.n} G/R${r.green}/${r.red} | `; } console.log(row); }
console.log('--- pd filter ---'); for (const pd of [0,1.0,1.2,1.5,2.0]) { const r=report(sel(rt,v4(.6,.6,pd)),20220101,20261020); console.log(`pd ${pd}: PF${r.pf.toFixed(2)} n${r.n} net${Math.round(r.net)} G/R${r.green}/${r.red}`); }
console.log('--- target R ---'); for (const t of [1,1.5,2,2.5,3]) { const m=sel(E.simRT2(all,{risk:400,stop:'opp',tgtR:t},MK),v4(.6,.6,1.2)); const r=report(m,20220101,20261020); const r6=report(m,20260101,20261020); console.log(`tgt ${t}R: all PF${r.pf.toFixed(2)} n${r.n} net${Math.round(r.net)} G/R${r.green}/${r.red} | 2026 PF${r6.pf.toFixed(2)} net${Math.round(r6.net)}`); }
