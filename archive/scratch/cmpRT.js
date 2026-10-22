const E=require('/home/claude/mnqscalp/lab/engine.js'), fs=require('fs');
function go(mk){
const MK={mnq:{pv:2,tick:0.25},mes:{pv:5,tick:0.25}}[mk];
const days=E.parseBars(fs.readFileSync(`/home/claude/mnqscalp/lab/${mk}_rth.txt`,'utf8')); const dl=days.map(x=>x.d);
const F={target:1250,mll:1000,dll:600,cap:600,consist:50,evDays:30,price:39,reset:45};
const V={
 'Break entry (old ORB)':r=>E.simORB(days,{orMin:15,stopMode:'opp',tgtR:2,risk:r,lastEntry:1130,slip:1,both:true,comm:2.37,maxQty:20},MK),
 'Retest limit, opp stop':r=>E.simRT(days,{orMin:15,brk:'5m',entry:'limit',stop:'opp',cancel:true,maxW:0,tgtR:2,lastEntry:1300,tol:0,risk:r,maxQty:20,comm:2.37,slip:1},MK),
 'Retest bounce, opp stop':r=>E.simRT(days,{orMin:15,brk:'5m',entry:'bounce',stop:'opp',cancel:true,maxW:0,tgtR:2,lastEntry:1300,tol:0,risk:r,maxQty:20,comm:2.37,slip:1},MK),
 'Retest bounce 15m, opp':r=>E.simRT(days,{orMin:15,brk:'15m',entry:'bounce',stop:'opp',cancel:true,maxW:0,tgtR:2,lastEntry:1300,tol:0,risk:r,maxQty:20,comm:2.37,slip:1},MK),
};
console.log('=== '+mk.toUpperCase()+' Flex 25K, 30-day window ===');
for(const [nm,f] of Object.entries(V)) for(const r of [300,400,500]){
 const dt=f(r); const S=E.summarize(E.evals(dl,dt,F)); const R=E.randomBaseline(dl,dt,F,3);
 let net=0,n=0,w=0; const Y={}; dt.forEach((l,d)=>{const y=Math.floor(d/1e4);l.forEach(t=>{net+=t.pnl;n++;if(t.pnl>0)w++;Y[y]=(Y[y]||0)+t.pnl})});
 const tries=(S.p+S.f)/S.p; const q=x=>S.pd[Math.floor(x*(S.pd.length-1))];
 console.log(`${nm.padEnd(25)} $${r} | PASS ${(S.p*100).toFixed(0)} FAIL ${(S.f*100).toFixed(0)} (random ${(R.p*100).toFixed(0)}/${(R.f*100).toFixed(0)}) | days ${q(.5)} (fast ${q(.25)}) | cost $${Math.round(F.price+(tries-1)*F.reset)} | net ${Math.round(net)} trades ${n} win ${(100*w/n).toFixed(0)}% | yrs ${Object.entries(Y).map(([y,v])=>y.slice(2)+':'+(v/1000).toFixed(1)+'k').join(' ')}`);
}}
go('mnq'); go('mes');
