const E=require('/home/claude/mnqscalp/lab/engine.js'), fs=require('fs');
const days=E.parseBars(fs.readFileSync('/home/claude/mnqscalp/lab/mnq_rth.txt','utf8'));
const MK={pv:2,tick:0.25};
const stats=(dt,from,to)=>{let N=0,NET=0,W=0,GW=0,GL=0,g=0,r=0,dd=0;dt.forEach((l,d)=>{if(d<from||d>to)return;let dp=0;l.forEach(t=>{N++;NET+=t.pnl;dp+=t.pnl;if(t.pnl>0){W++;GW+=t.pnl}else GL-=t.pnl});if(l.length){dd++;if(dp>0)g++;else r++;}});
 return {N,NET,win:N?W/N:0,pf:GL?GW/GL:99,aw:W?GW/W:0,al:(N-W)?GL/(N-W):0,g,r,dd};};
const fmt=s=>`${String(s.N).padStart(3)} tr ${String(Math.round(s.NET)).padStart(6)} $ PF ${s.pf.toFixed(2)} win ${(s.win*100).toFixed(0)}% avgW ${Math.round(s.aw)} avgL ${Math.round(s.al)} days G/R ${s.g}/${s.r}`;
const variants=[];
for (const entry of ['break','retest']) for (const trend of [true,false]) for (const minRoomR of [1,1.5,2]) for (const stopMode of ['level','bar']) for (const maxHold of [0,40])
  variants.push({entry,trend,minRoomR,stopMode,maxHold});
const rows=[];
for (const v of variants){ E.setMaxHold(v.maxHold); const dt=E.simKL(days,{...v},MK);
  const o26=stats(dt,20261001,20261031), o25=stats(dt,20251001,20251031), y12=stats(dt,20251001,20261031);
  // months positive in last 13
  let mp=0; for(let ym=202510; ym<=202610; ym=(ym%100===12?ym+89:ym+1)){ if(stats(dt,ym*100,ym*100+31).NET>0) mp++; }
  rows.push({v,o26,o25,y12,mp}); }
E.setMaxHold(0);
rows.sort((a,b)=>b.y12.NET-a.y12.NET);
for (const r of rows.slice(0,10)) { console.log(JSON.stringify(r.v)); console.log('   last 13 mo:',fmt(r.y12),'| months+',r.mp+'/13'); console.log('   Oct 2026  :',fmt(r.o26)); console.log('   Oct 2025  :',fmt(r.o25)); }
fs.writeFileSync('kl1.json',JSON.stringify(rows));
