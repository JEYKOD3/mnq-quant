const E=require('../engine/js/engine.js'), fs=require('fs'), {report,line}=require('../engine/js/report.js');
const all=E.parseBars(fs.readFileSync('../data/raw/mnq_rth_5m.txt','utf8')); const MK={pv:2,tick:0.25}; const feat=JSON.parse(fs.readFileSync('dayfeat.json'));
const v4=f=>{ if(f.pdRel>1.2) return 0; const G=Math.abs(f.gap)>=.6, D=Math.abs(f.orDir)>=.6; if(!(G||D)) return 0; return G?Math.sign(f.gap):Math.sign(f.orDir);};
const show=(nm,m)=>{ console.log(nm); for(const [l,a,z] of [['2022-25',20220101,20251231],['2026   ',20260101,20261020]]) console.log('  ',l,line(report(m,a,z))); };
const rt=E.simRT2(all,{risk:400,stop:'opp',tgtR:2,lastEntry:1530,maxTrades:10},MK);
const ob=E.simORB(all,{orMin:15,stopMode:'opp',tgtR:2,risk:400,lastEntry:1530,slip:1,both:true,comm:2.37,maxQty:20,maxTrades:10},MK);
const ob30=E.simORB(all,{orMin:30,stopMode:'opp',tgtR:2,risk:400,lastEntry:1530,slip:1,both:true,comm:2.37,maxQty:20,maxTrades:10},MK);
const dist=m=>{const c={}; m.forEach(l=>{c[l.length]=(c[l.length]||0)+1}); return JSON.stringify(c);};
for (const cap of [1,3,6,10]) {
  const m=new Map(); rt.forEach((l,d)=>{const f=feat[d]; if(!f) return; const r=v4(f); if(!r) return; const k=l.filter(t=>t.side===r).slice(0,cap); if(k.length) m.set(d,k);});
  show(`V4 retest, entries until 15:30, cap ${cap}/day  trades-per-day dist ${dist(m)}`,m);
}
for (const [nm,src] of [['ORB15 break',ob],['ORB30 break',ob30]]) for (const cap of [3,10]) {
  const m=new Map(); src.forEach((l,d)=>{const f=feat[d]; if(!f) return; const r=v4(f); if(!r) return; const k=l.filter(t=>t.side===r).slice(0,cap); if(k.length) m.set(d,k);});
  show(`${nm} + V4 filter, cap ${cap}/day  dist ${dist(m)}`,m);
}
// union: all break + retest setups with bias, chronological, cap 10
const m=new Map(); rt.forEach((l,d)=>{const f=feat[d]; if(!f) return; const r=v4(f); if(!r) return; const x=[...(ob.get(d)||[]).filter(t=>t.side===r),...l.filter(t=>t.side===r)].sort((p,q)=>p.eI-q.eI).slice(0,10); if(x.length) m.set(d,x);});
show(`UNION break+retest with bias, cap 10  dist ${dist(m)}`,m);
