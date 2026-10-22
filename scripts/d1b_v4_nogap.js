// D1b: V4 Adaptive with gap term removed (direction only) vs original
const E=require('../engine/js/engine.js'), fs=require('fs'), {report,line}=require('../engine/js/report.js');
const all=E.parseBars(fs.readFileSync('../data/raw/mnq_rth_5m.txt','utf8')); const MK={pv:2,tick:0.25}; const feat=JSON.parse(fs.readFileSync('dayfeat.json'));
const rt=E.simRT2(all,{risk:400,stop:'opp',tgtR:2},MK);
const sel=(dt,ok)=>{const m=new Map(); dt.forEach((l,d)=>{const f=feat[d]; if(!f) return; const r=ok(f); if(r) m.set(d,l.filter(t=>t.side===r));}); return m;};
const show=(nm,m)=>{ console.log(nm); for(const [l,a,z] of [['2022-25',20220101,20251231],['2026   ',20260101,20261020],['last 6m',20260421,20261020]]) console.log('  ',l,line(report(m,a,z))); };
const pdok=f=>f.pdRel<=1.2;
show('V4 original (gap>=.6 OR dir>=.6), pd<=1.2, with bias', sel(rt,f=>{ if(!pdok(f)) return 0; const g=Math.abs(f.gap)>=.6, d=Math.abs(f.orDir)>=.6; if(!(g||d)) return 0; return g?Math.sign(f.gap):Math.sign(f.orDir);}));
show('D1b dir only >=.6, pd<=1.2', sel(rt,f=>pdok(f)&&Math.abs(f.orDir)>=.6?Math.sign(f.orDir):0));
show('D1b dir only >=.5, pd<=1.2', sel(rt,f=>pdok(f)&&Math.abs(f.orDir)>=.5?Math.sign(f.orDir):0));
show('D1b dir only >=.7, pd<=1.2', sel(rt,f=>pdok(f)&&Math.abs(f.orDir)>=.7?Math.sign(f.orDir):0));
show('D1b dir only >=.6, no pd filter', sel(rt,f=>Math.abs(f.orDir)>=.6?Math.sign(f.orDir):0));
show('gap only >=.6, pd<=1.2', sel(rt,f=>pdok(f)&&Math.abs(f.gap)>=.6?Math.sign(f.gap):0));
show('dir>=.6 AND gap agrees (or gap small)', sel(rt,f=>{ if(!pdok(f)||Math.abs(f.orDir)<.6) return 0; const s=Math.sign(f.orDir); if(Math.abs(f.gap)>=.6&&Math.sign(f.gap)!==s) return 0; return s;}));
