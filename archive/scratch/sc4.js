const E=require('/home/claude/mnqscalp/lab/engine.js'), fs=require('fs');
const days=E.parseBars(fs.readFileSync('/home/claude/mnqscalp/lab/mnq_rth.txt','utf8')); const dl=days.map(x=>x.d);
const MK={pv:2,tick:0.25}; const F={target:1250,mll:1000,dll:600,cap:600,consist:50,maxQty:20};
const cfg={orb:P=>E.simORB(days,{orMin:15,stopMode:'opp',tgtR:2,risk:300,lastEntry:1130,slip:1,both:true,comm:2.37,maxQty:20,...P},MK),
 rt:P=>E.simRT2(days,{risk:400,stop:'opp',maxQty:20,dayStop:600,dayTarget:600,...P},MK),
 rtRoom:P=>E.simRT2(days,{risk:400,stop:'opp',maxQty:20,dayStop:600,dayTarget:600,lvlTgt:true,lvlGap:4,minRoomR:1,...P},MK)};
for (const [nm,f] of Object.entries(cfg)) for (const add of [0,0.5,1]) for (const pct of [50,100,200]) { if(!add&&pct!==100) continue;
 const P={addR:add,addPct:pct}; if(add&&nm!=='rtRoom'){P.tgtR=3;} const dt=f(P);
 let N=0,NET=0,A=0; dt.forEach(l=>l.forEach(t=>{N++;NET+=t.pnl}));
 for (const ev of [20,60]) { const S=E.summarize(E.evals(dl,dt,{...F,evDays:ev})); const med=S.pd.length?S.pd[S.pd.length>>1]:'-';
 console.log(nm.padEnd(6),'add at',add?add+'R':'off','size +'+(add?pct:0)+'%'.padEnd(2),'days',ev,'| net',String(Math.round(NET)).padStart(6),'| PASS',(S.p*100).toFixed(0),'FAIL',(S.f*100).toFixed(0),'| median days',med,'| evals/pass',S.p?((S.p+S.f)/S.p).toFixed(1):'-');}}
