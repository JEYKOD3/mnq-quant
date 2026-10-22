const E=require('/home/claude/mnqscalp/lab/engine.js'), fs=require('fs');
const days=E.parseBars(fs.readFileSync('/home/claude/mnqscalp/lab/mnq_rth_1m.txt','utf8')); const dl=days.map(x=>x.d);
const MK={pv:2,tick:0.25}; const F={target:1250,mll:1000,dll:600,cap:600,consist:50,evDays:20};
const which=process.argv[2];
const run=P=>which==='orb'?E.simORB(days,{orMin:15,stopMode:'opp',tgtR:2,risk:300,lastEntry:1130,slip:1,both:true,comm:2.37,maxQty:20,...P},MK)
                          :E.simRT2(days,{risk:400,stop:'opp',...P},MK);
E.setBar(1); const rows=[]; const t0=Date.now();
for (const hold of [0,20,30,40]) for (const tg of ['2R',8,10,15,20,30]) for (const st of ['range',10,15,20,30]) {
  E.setMaxHold(hold);
  const P={}; if (tg!=='2R') P.tgtPts=tg; if (st!=='range') { if(which==='orb'){P.stopMode='pts';P.stopPts=st;} else {P.stop='pts';P.stopPts=st;} }
  const dt=run(P); let N=0,NET=0,W=0,H=0; dt.forEach(l=>l.forEach(t=>{N++;NET+=t.pnl;if(t.pnl>0)W++;H+=t.hold}));
  const S=E.summarize(E.evals(dl,dt,F)); const R=E.randomBaseline(dl,dt,F,2);
  rows.push({k:`hold ${hold||'none'} tgt ${tg} stop ${st}`,N,NET,W:W/N,H:H/N,p:S.p,f:S.f,rp:R.p,rf:R.f});
}
E.setMaxHold(0);
rows.sort((a,b)=>(b.p-b.f)-(a.p-a.f));
const pr=r=>console.log(r.k.padEnd(32),'trades',r.N,'net',String(Math.round(r.NET)).padStart(7),'win',(r.W*100).toFixed(0)+'%','hold',r.H.toFixed(0)+'m','PASS',(r.p*100).toFixed(0),'FAIL',(r.f*100).toFixed(0),'(random',(r.rp*100).toFixed(0)+'/'+(r.rf*100).toFixed(0)+')');
rows.slice(0,10).forEach(pr); console.log('...'); rows.filter(r=>r.k.startsWith('hold 40')).sort((a,b)=>b.NET-a.NET).slice(0,6).forEach(pr);
console.log('baseline:'); pr(rows.find(r=>r.k==='hold none tgt 2R stop range')); console.log('secs',(Date.now()-t0)/1000);
fs.writeFileSync(`sc1m_${which}.json`,JSON.stringify(rows));
