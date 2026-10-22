const E=require('/home/claude/mnqscalp/lab/engine.js'), fs=require('fs');
const days=E.parseBars(fs.readFileSync('/home/claude/mnqscalp/lab/mnq_rth.txt','utf8')); const dl=days.map(x=>x.d);
const F={target:1250,mll:1000,dll:600,cap:600,consist:50,evDays:20};
for (const comm of [2.37,1.0,0.5,0]) for (const minStop of [8,24,40]) {
 const P={orMin:15,need:1,depth:1,tgtR:1.5,maxTrades:4,lastEntry:1300,flip:true,risk:300,maxQty:20,comm,slip:1,minStop,dayStop:600};
 const dt=E.simPB(days,P,{pv:2,tick:0.25}); let n=0,net=0,w=0,R=[],qs=0,stp=0;
 dt.forEach(l=>l.forEach(t=>{n++;net+=t.pnl;if(t.pnl>0)w++;qs+=t.q;stp+=Math.abs(t.eP-(t.side>0?1:1)*0)}));
 const S=E.summarize(E.evals(dl,dt,F));
 console.log(`comm ${comm} minStop ${minStop}t: trades ${n} net ${Math.round(net)} win ${(100*w/n).toFixed(0)}% avgQty ${(qs/n).toFixed(1)} | PASS ${(S.p*100).toFixed(0)} FAIL ${(S.f*100).toFixed(0)}`);
}
