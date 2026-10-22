const E=require('/home/claude/mnqscalp/lab/engine.js'), fs=require('fs');
const days=E.parseBars(fs.readFileSync('/home/claude/mnqscalp/lab/mnq_rth.txt','utf8')); const dl=days.map(x=>x.d);
const MK={pv:2,tick:0.25}; const F={target:1250,mll:1000,dll:600,cap:600,consist:50,evDays:30};
// OR width ratio vs prior 20 days
const W={}; const hist=[]; for(const {d,b} of days){ if(b.length<3) continue; let hi=-1e9,lo=1e9; for(let i=0;i<3;i++){hi=Math.max(hi,b[i][2]);lo=Math.min(lo,b[i][3]);} const w=hi-lo; const a=hist.length>=20?hist.slice(-20).reduce((x,y)=>x+y)/20:null; W[d]=a?w/a:1; hist.push(w);}
const RT=P=>E.simRT2(days,{stop:'opp',...P},MK), ORB=P=>E.simORB(days,{orMin:15,stopMode:'opp',tgtR:2,lastEntry:1130,slip:1,both:true,comm:2.37,maxQty:20,...P},MK);
const which=process.argv[2]; const f=which==='orb'?ORB:RT; const rows=[];
for (const risk of [300,400,500,600]) { const dt0=f({risk});
 for (const [lo,hi] of [[0,99],[0.6,99],[0.8,99],[0,1.5],[0.6,1.5],[0.8,1.5],[0.6,2],[1,99]]) {
  const dt=new Map(); dt0.forEach((l,d)=>dt.set(d,(W[d]>=lo&&W[d]<=hi)?l:[]));
  let N=0,NET=0; const Y={}; dt.forEach((l,d)=>l.forEach(t=>{N++;NET+=t.pnl;const y=Math.floor(d/1e4);Y[y]=(Y[y]||0)+t.pnl}));
  const S=E.summarize(E.evals(dl,dt,F)); rows.push({k:`risk ${risk} width ${lo}-${hi}x`,N,NET,p:S.p,f:S.f,pd:S.pd,yp:Object.values(Y).filter(x=>x>0).length,tpd:N/dl.length});
 }}
rows.sort((a,b)=>(b.p-b.f)-(a.p-a.f));
for (const r of rows.slice(0,10)) console.log(r.k.padEnd(26),'trades/day',r.tpd.toFixed(2),'net',String(Math.round(r.NET)).padStart(6),'PASS',(r.p*100).toFixed(0),'FAIL',(r.f*100).toFixed(0),'days',r.pd,'yrs+',r.yp);
