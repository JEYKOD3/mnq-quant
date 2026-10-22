const E=require('/home/claude/mnqscalp/lab/engine.js'), fs=require('fs');
for (const mk of ['mnq','mes']){
const MK={mnq:{pv:2,tick:0.25},mes:{pv:5,tick:0.25}}[mk];
const days=E.parseBars(fs.readFileSync(`/home/claude/mnqscalp/lab/${mk}_rth.txt`,'utf8')); const dl=days.map(x=>x.d);
for (const evDays of [30,60]) for (const r of [500,600,800]) for (const tg of [2,3]) {
 const F={target:1250,mll:1000,dll:600,cap:600,consist:50,evDays,price:39,reset:45};
 const dt=E.simRT(days,{orMin:15,brk:'5m',entry:'bounce',stop:'opp',cancel:true,maxW:0,tgtR:tg,lastEntry:1300,tol:0,risk:r,maxQty:20,comm:2.37,slip:1},MK);
 const S=E.summarize(E.evals(dl,dt,F)); const tries=(S.p+S.f)/S.p; const q=x=>S.pd[Math.floor(x*(S.pd.length-1))];
 let net=0; dt.forEach(l=>l.forEach(t=>net+=t.pnl));
 console.log(`${mk} ${evDays}d risk$${r} tgt${tg}R | PASS ${(S.p*100).toFixed(0)} FAIL ${(S.f*100).toFixed(0)} open ${(S.o*100).toFixed(0)} | days ${q(.5)} (fast ${q(.25)}) | evals/pass ${tries.toFixed(1)} cost $${Math.round(39+(tries-1)*45)} | net ${Math.round(net)}`);
}}
