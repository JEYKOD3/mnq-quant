const E=require('/home/claude/mnqscalp/lab/engine.js'), fs=require('fs');
const bar=+process.argv[3]||5; const days=E.parseBars(fs.readFileSync('/home/claude/mnqscalp/lab/'+(bar===1?'mnq_rth_1m.txt':'mnq_rth.txt'),'utf8')); const dl=days.map(x=>x.d);
E.setBar(bar); const MK={pv:2,tick:0.25}; const F={target:1250,mll:1000,dll:600,cap:600,consist:50,evDays:20};
const which=process.argv[2];
const run=P=>which==='orb'?E.simORB(days,{orMin:15,stopMode:'opp',tgtR:2,risk:300,lastEntry:1130,slip:1,both:true,comm:2.37,maxQty:20,...P},MK):E.simRT2(days,{risk:400,stop:'opp',...P},MK);
const rows=[];
for (const hold of [0,40]) for (const pb of [0,1,2]) for (const ex of [false,true]) for (const lv of ['off','tgt','tgt+room1','tgt+room2']) {
  E.setMaxHold(hold); const P={exitPB:pb,exhaust:ex}; if(lv!=='off'){P.lvlTgt=true;P.lvlGap=4; if(lv.includes('room')) P.minRoomR=+lv.slice(-1);}
  const dt=run(P); let N=0,NET=0,W=0,H=0; const Y={}; dt.forEach((l,d)=>l.forEach(t=>{N++;NET+=t.pnl;if(t.pnl>0)W++;H+=t.hold;const y=Math.floor(d/1e4);Y[y]=(Y[y]||0)+t.pnl}));
  const S=E.summarize(E.evals(dl,dt,F)); const R=E.randomBaseline(dl,dt,F,2);
  rows.push({k:`hold ${hold||'none'} pullbackExit ${['off','any','profit'][pb]} exhaust ${ex?'on':'off'} levels ${lv}`,N,NET,W:W/N,H:H/N,p:S.p,f:S.f,rp:R.p,rf:R.f,yp:Object.values(Y).filter(x=>x>0).length});
}
rows.sort((a,b)=>(b.p-b.f)-(a.p-a.f));
rows.slice(0,8).forEach(r=>console.log(r.k.padEnd(70),'tr',r.N,'net',String(Math.round(r.NET)).padStart(7),'win',(r.W*100).toFixed(0)+'%','hold',r.H.toFixed(0)+'m','PASS',(r.p*100).toFixed(0),'FAIL',(r.f*100).toFixed(0),'rand',(r.rp*100).toFixed(0)+'/'+(r.rf*100).toFixed(0),'yrs+',r.yp));
