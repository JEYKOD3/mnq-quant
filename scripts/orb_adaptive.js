const E=require('../engine/js/engine.js'), fs=require('fs'), {report,line}=require('../engine/js/report.js');
const all=E.parseBars(fs.readFileSync('../data/raw/mnq_rth_5m.txt','utf8')); const MK={pv:2,tick:0.25}; const feat=JSON.parse(fs.readFileSync('dayfeat.json'));
const v4=f=>{ if(f.pdRel>1.2) return 0; const G=Math.abs(f.gap)>=.6, D=Math.abs(f.orDir)>=.6; if(!(G||D)) return 0; return G?Math.sign(f.gap):Math.sign(f.orDir);};
const sel=(dt,first)=>{const m=new Map(); dt.forEach((l,d)=>{const f=feat[d]; if(!f) return; const r=v4(f); if(r){ const k=l.filter(t=>t.side===r); m.set(d, first?k.slice(0,1):k);} }); return m;};
const show=(nm,m)=>{ console.log(nm); for(const [l,a,z] of [['2022-25',20220101,20251231],['2026   ',20260101,20261020],['last 6m',20260421,20261020]]) console.log('  ',l,line(report(m,a,z))); };
const rt=E.simRT2(all,{risk:400,stop:'opp',tgtR:2},MK);
show('V4 retest (current)',sel(rt));
for (const [nm,o] of [['ORB break 15m, stop opp, 2R',{orMin:15,stopMode:'opp',tgtR:2,risk:400,lastEntry:1130,slip:1,both:true,comm:2.37,maxQty:20}],['ORB break 15m, 2R, first trade only',null],['ORB break 30m, stop opp, 2R',{orMin:30,stopMode:'opp',tgtR:2,risk:400,lastEntry:1130,slip:1,both:true,comm:2.37,maxQty:20}],['ORB break 15m, stop mid, 2R',{orMin:15,stopMode:'mid',tgtR:2,risk:400,lastEntry:1130,slip:1,both:true,comm:2.37,maxQty:20}],['ORB break 15m, 1.5R',{orMin:15,stopMode:'opp',tgtR:1.5,risk:400,lastEntry:1130,slip:1,both:true,comm:2.37,maxQty:20}]]) {
  if(!o){ const ob=E.simORB(all,{orMin:15,stopMode:'opp',tgtR:2,risk:400,lastEntry:1130,slip:1,both:true,comm:2.37,maxQty:20},MK); show(nm+' + V4 filter',sel(ob,true)); continue; }
  const ob=E.simORB(all,o,MK); show(nm+' + V4 filter',sel(ob));
}
// combined: break OR retest, whichever first, with bias
const ob=E.simORB(all,{orMin:15,stopMode:'opp',tgtR:2,risk:400,lastEntry:1130,slip:1,both:true,comm:2.37,maxQty:20},MK);
const comb=new Map(); rt.forEach((l,d)=>{const f=feat[d]; if(!f) return; const r=v4(f); if(!r) return; const a=(ob.get(d)||[]).filter(t=>t.side===r).map(t=>({...t,src:'brk'})); const b=l.filter(t=>t.side===r).map(t=>({...t,src:'rt'})); const x=[...a,...b].sort((p,q)=>(p.eI-q.eI)); if(x.length) comb.set(d,x.slice(0,1));});
show('COMBINED: first of (ORB break, retest) with bias',comb);
