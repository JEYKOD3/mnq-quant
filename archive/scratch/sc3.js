const E=require('/home/claude/mnqscalp/lab/engine.js'), fs=require('fs');
const days=E.parseBars(fs.readFileSync('/home/claude/mnqscalp/lab/mnq_rth.txt','utf8')); const dl=days.map(x=>x.d);
const MK={pv:2,tick:0.25};
for (const [acct,F0] of [['Flex25K',{target:1250,mll:1000,dll:600,cap:600,consist:50,maxQty:20}],['Flex50K',{target:3000,mll:2000,dll:1200,cap:1200,consist:50,maxQty:40}]]) {
 for (const room of [0,1,1.5]) for (const risk of (acct==='Flex25K'?[400,600,800]:[600,1000,1500])) for (const evDays of [20,30,60]) {
  const F={...F0,evDays}; const P={risk,stop:'opp',maxQty:F0.maxQty,dayStop:F0.dll,dayTarget:F0.cap}; if(room){P.lvlTgt=true;P.lvlGap=4;P.minRoomR=room;}
  const dt=E.simRT2(days,P,MK); let N=0,NET=0,W=0,Q=0; dt.forEach(l=>l.forEach(t=>{N++;NET+=t.pnl;Q+=t.q;if(t.pnl>0)W++}));
  const S=E.summarize(E.evals(dl,dt,F)); const R=E.randomBaseline(dl,dt,F,2); const med=S.pd.length?S.pd[S.pd.length>>1]:'-';
  const epp=S.p>0?((S.p+S.f)/S.p).toFixed(1):'inf';
  console.log(acct,'room',String(room).padEnd(3),'risk',String(risk).padEnd(4),'days',String(evDays).padEnd(2),'| trades',N,'avg qty',(Q/N).toFixed(1),'net',String(Math.round(NET)).padStart(6),'win',(100*W/N).toFixed(0)+'% | PASS',(S.p*100).toFixed(0),'FAIL',(S.f*100).toFixed(0),'open',(100-S.p*100-S.f*100).toFixed(0),'| median days',med,'| evals/pass',epp,'| random',(R.p*100).toFixed(0)+'/'+(R.f*100).toFixed(0));
 }}
