const E=require('/home/claude/mnqscalp/lab/engine.js'), fs=require('fs');
for (const mk of ['mnq','mes']){
const MK={mnq:{pv:2,tick:0.25},mes:{pv:5,tick:0.25}}[mk];
const days=E.parseBars(fs.readFileSync(`/home/claude/mnqscalp/lab/${mk}_rth.txt`,'utf8')); const dl=days.map(x=>x.d);
const F={target:1250,mll:1000,dll:600,cap:600,consist:50,evDays:30,price:39,reset:45};
console.log('=== '+mk);
for (const stop of ['opp','mid','retest']) for (const tg of [0.5,1,2]) for (const mh of [0,60,30,15,10,5]) {
  E.setMaxHold(mh);
  const dt=E.simRT(days,{orMin:15,brk:'5m',entry:'bounce',stop,cancel:true,maxW:0,tgtR:tg,lastEntry:1300,tol:0,risk:500,maxQty:20,comm:2.37,slip:1},MK);
  const S=E.summarize(E.evals(dl,dt,F)); let net=0,n=0,w=0,hold=0; const Y={};
  dt.forEach((l,d)=>l.forEach(t=>{net+=t.pnl;n++;if(t.pnl>0)w++;hold+=t.hold;const y=Math.floor(d/1e4);Y[y]=(Y[y]||0)+t.pnl}));
  const yp=Object.values(Y).filter(v=>v>0).length;
  console.log(`stop ${stop.padEnd(6)} tgt ${String(tg).padEnd(3)} maxHold ${String(mh||'off').padEnd(3)} | net ${String(Math.round(net)).padStart(7)} n${n} win ${(100*w/n).toFixed(0)}% avgHold ${(hold/n).toFixed(0)}m yrs+ ${yp}/6 | PASS ${(S.p*100).toFixed(0)} FAIL ${(S.f*100).toFixed(0)}`);
}}
E.setMaxHold(0);
