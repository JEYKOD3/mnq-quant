const E=require('/home/claude/mnqscalp/lab/engine.js'), fs=require('fs');
const MK={pv:2,tick:0.25};
const d5=E.parseBars(fs.readFileSync('/home/claude/mnqscalp/lab/mnq_rth.txt','utf8'));
const d1=E.parseBars(fs.readFileSync('/home/claude/mnqscalp/lab/mnq_rth_1m.txt','utf8'));
const F={target:1250,mll:1000,dll:600,cap:600,consist:50,evDays:30};
function rep(lbl,days,P,bar,mh){ E.setBar(bar); E.setMaxHold(mh); const dt=E.simRT(days,P,MK); const dl=days.map(x=>x.d);
  const S=E.summarize(E.evals(dl,dt,F)); let net=0,n=0,w=0,hold=0; const Y={}; dt.forEach((l,d)=>l.forEach(t=>{net+=t.pnl;n++;if(t.pnl>0)w++;hold+=t.hold;const y=Math.floor(d/1e4);Y[y]=(Y[y]||0)+t.pnl}));
  console.log(`${lbl.padEnd(44)} net ${String(Math.round(net)).padStart(7)} n${n} win ${(100*w/n).toFixed(0)}% hold ${(hold/n).toFixed(0)}m yrs+ ${Object.values(Y).filter(v=>v>0).length}/6 | PASS ${(S.p*100).toFixed(0)} FAIL ${(S.f*100).toFixed(0)}`); }
const base={orMin:15,brk:'5m',entry:'bounce',stop:'opp',cancel:true,maxW:0,tgtR:2,lastEntry:1300,tol:0,risk:500,maxQty:20,comm:2.37,slip:1};
rep('5m bars, best retest (check)',d5,base,5,0);
rep('1m bars, same rules (5m close breakout)',d1,base,1,0);
console.log('--- 1m scalping variants (tight stops, fast exits)');
for (const stop of ['retest','mid']) for (const tg of [1,1.5,2]) for (const mh of [0,5,10,15]) for (const brk of ['5m','bar']){
  rep(`stop ${stop} tgt ${tg} maxHold ${mh||'off'} brk ${brk}`,d1,{...base,stop,tgtR:tg,brk,risk:300},1,mh); }
E.setBar(5); E.setMaxHold(0);
