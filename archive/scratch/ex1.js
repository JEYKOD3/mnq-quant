const E=require('/home/claude/mnqscalp/lab/engine.js'), fs=require('fs');
const days=E.parseBars(fs.readFileSync('/home/claude/mnqscalp/lab/mnq_rth.txt','utf8')); const dl=days.map(x=>x.d);
const MK={pv:2,tick:0.25}; const F={target:1250,mll:1000,dll:600,cap:600,consist:50,evDays:30};
const RT=P=>E.simRT2(days,{risk:400,stop:'opp',...P},MK), ORB=P=>E.simORB(days,{orMin:15,stopMode:'opp',tgtR:2,risk:300,lastEntry:1130,slip:1,both:true,comm:2.37,maxQty:20,...P},MK);
const which=process.argv[2]; const f=which==='orb'?ORB:RT; const rows=[];
const S0=E.summarize(E.evals(dl,f({}),F)); console.log('summary keys',Object.keys(S0).join(','));
for (const tgtR of [1,1.5,2,3,0]) for (const tp1R of [0,0.5,1]) for (const be of [false,true]) for (const trailN of [0,3,6]) {
  if (tp1R===0 && be) continue; if (tp1R>0 && tgtR>0 && tgtR<=tp1R) continue;
  const P= tp1R>0 ? {tp1R,tp1Pct:50,beOn:be,runR:tgtR,trailN,trailTrig:1} : {tgtR,trailN,trailTrig:1};
  const dt=f(P); let N=0,NET=0,W=0; const Y={}; dt.forEach((l,d)=>l.forEach(t=>{N++;NET+=t.pnl;if(t.pnl>0)W++;const y=Math.floor(d/1e4);Y[y]=(Y[y]||0)+t.pnl}));
  const S=E.summarize(E.evals(dl,dt,F));
  rows.push({k:`tgt ${tgtR||'none'} tp1 ${tp1R||'-'} be ${be?'Y':'n'} trail ${trailN||'-'}`,N,NET,W:W/N,p:S.p,f:S.f,dp:S.medDays||S.days||S.avgDays,yp:Object.values(Y).filter(x=>x>0).length});
}
rows.sort((a,b)=>(b.p-b.f)-(a.p-a.f));
for (const r of rows.slice(0,12)) console.log(r.k.padEnd(34),'net',String(Math.round(r.NET)).padStart(6),'win',(r.W*100).toFixed(0)+'%','PASS',(r.p*100).toFixed(0),'FAIL',(r.f*100).toFixed(0),'days',r.dp,'yrs+',r.yp);
console.log('--- baseline'); const b=rows.find(r=>r.k==='tgt 2 tp1 - be n trail -'); console.log(b.k,'net',Math.round(b.NET),'PASS',(b.p*100).toFixed(0),'FAIL',(b.f*100).toFixed(0),'days',b.dp);
