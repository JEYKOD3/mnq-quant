const E=require('../engine/js/engine.js'), fs=require('fs'), {report,line}=require('../engine/js/report.js');
const all=E.parseBars(fs.readFileSync('../data/raw/mnq_rth_5m.txt','utf8')); const MK={pv:2,tick:0.25}; const feat=JSON.parse(fs.readFileSync('dayfeat.json'));
const sel=(dt,f)=>{ const m=new Map(); dt.forEach((l,d)=>{ if(feat[d]&&f(feat[d])) m.set(d,l.filter(t=>feat[d].bias===t.side||!feat[d].committed)); }); return m; };
const rt=E.simRT2(all,{risk:400,stop:'opp',tgtR:2},MK), rt3=E.simRT2(all,{risk:400,stop:'opp',tgtR:2,maxTrades:3},MK);
const orb=E.simORB(all,{orMin:15,stopMode:'opp',tgtR:2,risk:300,lastEntry:1130,slip:1,both:true,comm:2.37,maxQty:20},MK);
const fb=E.simFB(all,{pokeMin:2,pokeMax:45,within:5,stopMode:'poke',tgtR:1,bufPts:5,sessStart:1000,lastEntry:1300,useSw:false,useOR:false,maxStop:60},MK);
const S={'Retest V4 adaptive (committed, with bias)':sel(rt,f=>f.committed),'ORB break adaptive (committed, with bias)':sel(orb,f=>f.committed),'Failed break PDH/PDL (all days)':fb,'Failed break on NON-committed days only':sel(fb,f=>!f.committed),'Retest V2 raw (no filter)':rt};
const per=[['Nov 2024',20241101,20241130],['Nov 2025',20251101,20251130],['Oct 2025',20251001,20251031],['Oct 2026',20261001,20261020],['Sep 2026',20260901,20260930],['Aug 2026',20260801,20260831]];
for (const [nm,dt] of Object.entries(S)) { console.log(nm); for (const [l,a,z] of per) console.log('  ',l.padEnd(9),line(report(dt,a,z))); }
// combined: retest adaptive on committed days + failed break on non-committed days (independent, no overlap)
const comb=new Map(); all.forEach(({d})=>{ if(!feat[d]) return; comb.set(d, feat[d].committed ? (S['Retest V4 adaptive (committed, with bias)'].get(d)||[]) : (fb.get(d)||[])); });
console.log('COMBINED: Retest V4 on committed days + Failed break on the other days'); for (const [l,a,z] of [...per,['2026',20260101,20261020],['2022-25',20220101,20251231]]) console.log('  ',l.padEnd(9),line(report(comb,a,z)));
