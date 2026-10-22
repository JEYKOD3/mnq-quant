const E=require('../engine/js/engine.js'), fs=require('fs'), {report,line}=require('../engine/js/report.js');
const all=E.parseBars(fs.readFileSync('../data/raw/mnq_rth_5m.txt','utf8')); const MK={pv:2,tick:0.25}; const feat=JSON.parse(fs.readFileSync('dayfeat.json'));
const sel=(dt,f)=>{ const m=new Map(); dt.forEach((l,d)=>{ if(feat[d]&&feat[d].committed) m.set(d,l.filter(t=>f(t,feat[d]))); }); return m; };
const orb=E.simORB(all,{orMin:15,stopMode:'opp',tgtR:2,risk:300,lastEntry:1130,slip:1,both:true,comm:2.37,maxQty:20},MK);
const rt=E.simRT2(all,{risk:400,stop:'opp',tgtR:2},MK);
const show=(nm,m)=>{ console.log(nm); for(const [l,a,z] of [['2022-25',20220101,20251231],['2026   ',20260101,20261020],['last 6m',20260421,20261020]]) console.log('  ',l,line(report(m,a,z))); };
for (const [nm,dt] of [['ORB break',orb],['Retest V2',rt]]) {
  show(nm+' committed, all trades',sel(dt,()=>true));
  show(nm+' committed, WITH the open bias only',sel(dt,(t,f)=>f.bias===t.side));
  show(nm+' committed, AGAINST the open bias',sel(dt,(t,f)=>f.bias!==t.side));
  show(nm+' committed, with bias, first trade of the day only',(()=>{const m=sel(dt,(t,f)=>f.bias===t.side); const o=new Map(); m.forEach((l,d)=>o.set(d,l.slice(0,1))); return o;})());
}
