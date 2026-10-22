const E=require('/home/claude/mnqscalp/lab/engine.js'), fs=require('fs');
const bar=+process.argv[2]; E.setBar(bar);
const days=E.parseBars(fs.readFileSync('/home/claude/mnqscalp/lab/'+(bar===1?'mnq_rth_1m.txt':'mnq_rth.txt'),'utf8')).filter(x=>x.d>=20250901);
const MK={pv:2,tick:0.25};
const stats=(dt,from,to)=>{let N=0,NET=0,W=0,GW=0,GL=0,g=0,r=0,H=0;dt.forEach((l,d)=>{if(d<from||d>to)return;let dp=0;l.forEach(t=>{N++;NET+=t.pnl;dp+=t.pnl;H+=t.hold;if(t.pnl>0){W++;GW+=t.pnl}else GL-=t.pnl});if(l.length){if(dp>0)g++;else r++;}});
 return {N,NET,win:N?W/N:0,pf:GL?GW/GL:99,aw:W?GW/W:0,al:(N-W)?GL/(N-W):0,g,r,H:N?H/N:0};};
const fmt=s=>`${String(s.N).padStart(3)} tr ${String(Math.round(s.NET)).padStart(6)}$ PF ${s.pf.toFixed(2)} win ${(s.win*100).toFixed(0)}% avgW ${Math.round(s.aw)} avgL ${Math.round(s.al)} hold ${Math.round(s.H)}m G/R ${s.g}/${s.r}`;
const rows=[];
const pivs = bar===1?[15,30]:[3,6];
for (const entry of ['break','retest']) for (const pivN of pivs) for (const minRoomR of [1,1.5]) for (const maxStopATR of [1,1.5,2.5]) for (const bufATR of [0.1,0.3]) for (const trend of [true,false]) {
  const v={entry,pivN,back:3,minRoomR,maxStopATR,bufATR,trend,minStop:3,emaLen:bar===1?105:21,slopeBars:bar===1?15:3,armBars:bar===1?60:12,momRange:1.2,lastEntry:1500}; const dt=E.simKL(days,v,MK);
  const y=stats(dt,20251001,20261031),o26=stats(dt,20261001,20261031),o25=stats(dt,20251001,20251031);
  let mp=0; for(let ym=202510; ym<=202610; ym=(ym%100===12?ym+89:ym+1)){ if(stats(dt,ym*100,ym*100+31).NET>0) mp++; }
  rows.push({v,y,o26,o25,mp});
}
rows.sort((a,b)=>b.y.NET-a.y.NET);
for (const r of rows.slice(0,6)) { const {entry,pivN,minRoomR,maxStopATR,bufATR,trend}=r.v; console.log({entry,pivN,minRoomR,maxStopATR,bufATR,trend}); console.log('   13 mo   :',fmt(r.y),'| months+',r.mp+'/13'); console.log('   Oct 2026:',fmt(r.o26)); console.log('   Oct 2025:',fmt(r.o25)); }
console.log('profitable (13 mo):',rows.filter(r=>r.y.NET>0).length,'of',rows.length,'| >= 0.5 trade/day:',rows.filter(r=>r.y.N>=140).length, '| profitable AND >=0.5/day:',rows.filter(r=>r.y.N>=140&&r.y.NET>0).length);
fs.writeFileSync('kl3_'+bar+'.json',JSON.stringify(rows));
