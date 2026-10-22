const E=require('../engine/js/engine.js'), fs=require('fs'), {report,line}=require('../engine/js/report.js');
const all=E.parseBars(fs.readFileSync('../data/raw/mnq_rth_5m.txt','utf8')); const MK={pv:2,tick:0.25}; const feat=JSON.parse(fs.readFileSync('dayfeat.json'));
const sel=dt=>{ const m=new Map(); dt.forEach((l,d)=>{ if(feat[d]&&feat[d].committed) m.set(d,l.filter(t=>feat[d].bias===t.side)); }); return m; };
const rows=[];
for (const [nm,P,hold] of [['2R target, no limit',{tgtR:2},0],['2R, max 60 min',{tgtR:2},60],['2R, max 90 min',{tgtR:2},90],['2R, max 120 min',{tgtR:2},120],['1.5R',{tgtR:1.5},0],['3R',{tgtR:3},0],['TP1 1R 50% + BE + 2R',{tp1R:1,tp1Pct:50,beOn:true,runR:2,tgtR:2},0],['TP1 1R 50% + 3R (no BE)',{tp1R:1,tp1Pct:50,beOn:false,runR:3,tgtR:3},0],['2R + trail 6 bars after 1R',{tgtR:2,trailN:6,trailTrig:1},0],['next level target, room 1R',{tgtR:2,lvlTgt:true,lvlGap:4,minRoomR:1},0],['2R, structure stop',{tgtR:2,stop:'structure',bufT:4,minStop:16},0],['2R, risk $600 (2 contracts)',{tgtR:2,risk:600},0]]) {
  E.setMaxHold(hold); const dt=sel(E.simRT2(all,{risk:400,stop:'opp',...P},MK)); E.setMaxHold(0);
  const R=[['2022-25',20220101,20251231],['2026',20260101,20261020],['last 6m',20260421,20261020]].map(([l,a,z])=>[l,report(dt,a,z)]);
  console.log(nm); for (const [l,r] of R) console.log('   ',l.padEnd(8),line(r)); }
