const E=require('/home/claude/mnqscalp/lab/engine.js'), fs=require('fs');
const mk=process.argv[2]||'mnq'; const MK={mnq:{pv:2,tick:0.25},mes:{pv:5,tick:0.25}}[mk];
const days=E.parseBars(fs.readFileSync(`/home/claude/mnqscalp/lab/${mk}_rth.txt`,'utf8')); const dl=days.map(x=>x.d);
const F={target:1250,mll:1000,dll:600,cap:600,consist:50,evDays:20};
const rows=[];
for(const brk of ['5m','15m'])for(const entry of ['limit','bounce'])for(const stop of ['retest','mid','opp'])for(const cancel of [true,false])for(const maxW of [0,1.5])for(const tgtR of [1,1.5,2,3])for(const lastEntry of [1130,1300])for(const tol of [0,8]){
  const P={orMin:15,brk,entry,stop,cancel,maxW,minW:0,tgtR,lastEntry,tol,risk:300,maxQty:20,comm:2.37,slip:1};
  const dt=E.simRT(days,P,MK); const S=E.summarize(E.evals(dl,dt,F)); const R=E.randomBaseline(dl,dt,F,2);
  let net=0,n=0,w=0; const Y={}; dt.forEach((l,d)=>{const y=Math.floor(d/1e4);l.forEach(t=>{net+=t.pnl;n++;if(t.pnl>0)w++;Y[y]=(Y[y]||0)+t.pnl})});
  rows.push({P,p:S.p,f:S.f,rp:R.p,rf:R.f,net,n,w:w/n,yrsPos:Object.values(Y).filter(v=>v>0).length,Y,med:S.pd[S.pd.length>>1]});
}
fs.writeFileSync('/tmp/claude-0/-home-claude/afdbc088-26a4-5e84-b77d-b387ee40e855/scratchpad/rt_'+mk+'.json',JSON.stringify(rows));
const pos=rows.filter(r=>r.net>0); console.log(mk,'variants',rows.length,'net positive',pos.length,'| median net',Math.round(rows.map(r=>r.net).sort((a,b)=>a-b)[rows.length>>1]));
// group effects
for(const k of ['brk','entry','stop','cancel','maxW','tgtR','lastEntry','tol']){const g={};rows.forEach(r=>{const v=String(r.P[k]);g[v]=g[v]||[];g[v].push(r.net)});console.log(k.padEnd(9),Object.entries(g).map(([v,a])=>`${v}: median ${Math.round(a.sort((x,y)=>x-y)[a.length>>1])} pos ${a.filter(x=>x>0).length}/${a.length}`).join(' | '));}
rows.sort((a,b)=>(b.p-b.rp)-(a.p-a.rp)+0.5*((a.f-a.rf)-(b.f-b.rf)));
console.log('--- top 10 by pass edge over random');
for(const r of rows.slice(0,10)) console.log(`${r.P.brk} ${r.P.entry} stop:${r.P.stop} cancel:${+r.P.cancel} maxW:${r.P.maxW} tgt:${r.P.tgtR} last:${r.P.lastEntry} tol:${r.P.tol} | PASS ${(r.p*100).toFixed(0)} FAIL ${(r.f*100).toFixed(0)} (rand ${(r.rp*100).toFixed(0)}/${(r.rf*100).toFixed(0)}) net ${Math.round(r.net)} n${r.n} win ${(r.w*100).toFixed(0)}% yrs+ ${r.yrsPos}/6 med ${r.med}d`);
