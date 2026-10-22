const E=require('/home/claude/mnqscalp/lab/engine.js'), fs=require('fs');
const F={target:1250,mll:1000,dll:600,cap:600,consist:50,evDays:30};
const base={emaLen:21,slopeBars:3,keyTol:8,sigFrac:0.5,minBody:0.3,allowFirst:false,swingN:20,stopMode:'signal',minStop:12,maxStop:100,risk:200,maxQty:20,tp1R:1,tp1Pct:50,runR:2,beOn:true,maxHold:30,maxTrades:3,dayTarget:600,dayLoss:550,maxConsec:2,sessStart:930,sessEnd:1530,comm:2.37,slip:1};
for (const mk of ['mnq','mes']) {
 const MK={mnq:{pv:2,tick:0.25},mes:{pv:5,tick:0.25}}[mk];
 const days=E.parseBars(fs.readFileSync(`/home/claude/mnqscalp/lab/${mk}_rth.txt`,'utf8')); const dl=days.map(x=>x.d);
 for (const v of [{},{maxHold:0},{allowFirst:true},{stopMode:'pullback'},{tp1R:0.5,runR:1.5},{keyTol:20},{maxTrades:5}]) {
  const P={...base,...v}; const dt=E.simW2E(days,P,MK); const S=E.summarize(E.evals(dl,dt,F)); const R=E.randomBaseline(dl,dt,F,2);
  let net=0,n=0,w=0,hold=0; const Y={}; dt.forEach((l,d)=>l.forEach(t=>{net+=t.pnl;n++;if(t.pnl>0)w++;hold+=t.hold;const y=Math.floor(d/1e4);Y[y]=(Y[y]||0)+t.pnl}));
  console.log(`${mk} ${JSON.stringify(v).padEnd(28)} trades ${n} (${(n/dl.length).toFixed(2)}/day) net ${Math.round(net)} win ${(100*w/n).toFixed(0)}% hold ${(hold/n).toFixed(0)}m | yrs ${Object.entries(Y).map(([y,x])=>y.slice(2)+':'+(x/1000).toFixed(1)+'k').join(' ')} | PASS ${(S.p*100).toFixed(0)} FAIL ${(S.f*100).toFixed(0)} (rand ${(R.p*100).toFixed(0)}/${(R.f*100).toFixed(0)})`);
 }}
