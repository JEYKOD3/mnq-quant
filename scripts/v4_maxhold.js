const E=require('../engine/js/engine.js'), fs=require('fs'), {report}=require('../engine/js/report.js');
const all=E.parseBars(fs.readFileSync('../data/raw/mnq_rth_5m.txt','utf8')); const MK={pv:2,tick:0.25}; const feat=JSON.parse(fs.readFileSync('dayfeat.json'));
const v4=f=>{ if(!f||f.pdRel>1.2) return 0; const G=Math.abs(f.gap)>=.6, D=Math.abs(f.orDir)>=.6; if(!(G||D)) return 0; return G?Math.sign(f.gap):Math.sign(f.orDir);};
const sel=rt=>{const m=new Map(); rt.forEach((l,d)=>{const s=v4(feat[d]); if(!s) return; const k=l.filter(t=>t.side===s); if(k.length) m.set(d,k);}); return m;};
const yrPF=m=>[2022,2023,2024,2025,2026].map(y=>report(m,y*10000+101,y*10000+1231).pf.toFixed(2)).join('/');
const avgHold=m=>{let s=0,n=0; m.forEach(l=>l.forEach(t=>{s+=t.hold;n++})); return Math.round(s/n);};
const why=m=>{const c={}; m.forEach(l=>l.forEach(t=>{c[t.why]=(c[t.why]||0)+1})); return JSON.stringify(c);};
console.log('risk $1000/trade. ALL = 2022-01..2026-10-23 | SEP-OCT = 2026-09-01..10-23');
for (const tg of [1,1.5,2]) for (const mh of [0,30,60,90,120,180]) {
  E.setMaxHold(mh); const m=sel(E.simRT2(all,{risk:1000,stop:'opp',tgtR:tg,maxQty:40},MK));
  const A=report(m,20220101,20261031), B=report(m,20260901,20261031);
  console.log(`tgt ${tg}R maxHold ${mh?mh+'m':'none'}`.padEnd(22), `ALL PF ${A.pf.toFixed(2)} net ${A.net} n${A.n} win ${A.win}% DD ${A.dd} yrs ${yrPF(m)} avgHold ${avgHold(m)}m | SEP-OCT net ${B.net} PF ${B.pf.toFixed(2)} DD ${B.dd} | exits ${why(m)}`);
}
E.setMaxHold(0);
