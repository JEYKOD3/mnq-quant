const E=require('/home/claude/mnqscalp/lab/engine.js'), fs=require('fs');
const days=E.parseBars(fs.readFileSync('/home/claude/mnqscalp/lab/mnq_rth.txt','utf8'));
const MK={pv:2,tick:0.25};
const stats=(dt,from,to)=>{let N=0,NET=0,W=0,GW=0,GL=0,g=0,r=0;dt.forEach((l,d)=>{if(d<from||d>to)return;let dp=0;l.forEach(t=>{N++;NET+=t.pnl;dp+=t.pnl;if(t.pnl>0){W++;GW+=t.pnl}else GL-=t.pnl});if(l.length){if(dp>0)g++;else r++;}});
 return {N,NET,win:N?W/N:0,pf:GL?GW/GL:99,aw:W?GW/W:0,al:(N-W)?GL/(N-W):0,g,r};};
const fmt=s=>`${String(s.N).padStart(3)} tr ${String(Math.round(s.NET)).padStart(6)}$ PF ${s.pf.toFixed(2)} win ${(s.win*100).toFixed(0)}% avgW ${Math.round(s.aw)} avgL ${Math.round(s.al)} G/R days ${s.g}/${s.r}`;
const rows=[];
for (const entry of ['break','retest']) for (const pivN of [6,12]) for (const back of [1,3]) for (const minRoomR of [1,1.5]) for (const maxStop of [25,40,60]) for (const trend of [true,false]) {
  const v={entry,pivN,back,minRoomR,maxStop,trend}; const dt=E.simKL(days,v,MK); const rej={...E.REJ};
  const y=stats(dt,20251001,20261031),o26=stats(dt,20261001,20261031),o25=stats(dt,20251001,20251031);
  let mp=0; for(let ym=202510; ym<=202610; ym=(ym%100===12?ym+89:ym+1)){ if(stats(dt,ym*100,ym*100+31).NET>0) mp++; }
  rows.push({v,y,o26,o25,mp,rej});
}
rows.sort((a,b)=>b.y.NET-a.y.NET);
for (const r of rows.slice(0,8)) { console.log(JSON.stringify(r.v),'rejected:',JSON.stringify(r.rej)); console.log('   13 mo   :',fmt(r.y),'| months+',r.mp+'/13'); console.log('   Oct 2026:',fmt(r.o26)); console.log('   Oct 2025:',fmt(r.o25)); }
console.log('profitable variants (13 mo):',rows.filter(r=>r.y.NET>0).length,'of',rows.length,'| with >=1 trade/day:',rows.filter(r=>r.y.N>=270).length);
fs.writeFileSync('kl2.json',JSON.stringify(rows));
