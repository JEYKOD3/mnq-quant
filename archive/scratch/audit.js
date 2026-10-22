const E=require('/home/claude/mnqscalp/lab/engine.js'), fs=require('fs');
const days=E.parseBars(fs.readFileSync('/home/claude/mnqscalp/lab/mnq_rth.txt','utf8'));
for (const [lbl,P] of [['2nd entry only',{maxTrades:5}],['All rules',{maxTrades:5,keyMode:'either',corrTL:true,useLH:true,useF2:true,congMult:2}]]) {
  const dt=E.simW2E(days,P,{pv:2,tick:0.25}); const A=[]; dt.forEach((l,d)=>{const b=days.find(x=>x.d===d).b; l.forEach(t=>A.push({...t,d,hm:b[t.eI][0]}))});
  const n=A.length; const by=(f)=>{const g={}; A.forEach(t=>{const k=f(t); g[k]=g[k]||[0,0,0]; g[k][0]++; g[k][1]+=t.pnl; g[k][2]+=t.pnl>0;}); return Object.entries(g).map(([k,a])=>`${k}: ${a[0]} (${Math.round(100*a[0]/n)}%) avg $${Math.round(a[1]/a[0])} win ${Math.round(100*a[2]/a[0])}%`).join(' | ');};
  console.log(`== ${lbl}: ${n} trades, net $${Math.round(A.reduce((s,t)=>s+t.pnl,0))}`);
  console.log(' exit reason ->', by(t=>t.why));
  console.log(' hold        ->', by(t=>t.hold<=10?'<=10m':t.hold<=20?'10-20m':'20-30m'));
  console.log(' hour        ->', by(t=>Math.floor(t.hm/100)));
  console.log(' setup       ->', by(t=>t.setup));
  const stops=A.filter(t=>t.why==='stop'); console.log(` stopped before TP1: ${stops.length} trades, total $${Math.round(stops.reduce((s,t)=>s+t.pnl,0))}; TP1 hit: ${A.filter(t=>t.tp1).length} (${Math.round(100*A.filter(t=>t.tp1).length/n)}%)`);
  const avgR=A.reduce((s,t)=>s+t.q,0)/n; console.log(` avg contracts ${avgR.toFixed(1)}, commission per trade ~$${(avgR*4.74).toFixed(0)}`);
}
