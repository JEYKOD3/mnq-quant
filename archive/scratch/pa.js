const E=require('/home/claude/mnqscalp/lab/engine.js'), fs=require('fs');
const F={target:1250,mll:1000,dll:600,cap:600,consist:50,evDays:30};
const cache={}; const load=f=>cache[f]||(cache[f]=E.parseBars(fs.readFileSync('/home/claude/mnqscalp/lab/'+f,'utf8')));
const rows=[];
function run(P,mk='mnq',file){ const MK={mnq:{pv:2,tick:0.25},mes:{pv:5,tick:0.25}}[mk]; const days=load(file||mk+'_rth.txt'), dl=days.map(x=>x.d);
  const dt=E.simW2E(days,P,MK); let net=0,n=0,w=0,hold=0; const Y={}; dt.forEach((l,d)=>l.forEach(t=>{net+=t.pnl;n++;if(t.pnl>0)w++;hold+=t.hold;const y=Math.floor(d/1e4);Y[y]=(Y[y]||0)+t.pnl}));
  const S=E.summarize(E.evals(dl,dt,F)); return {n,perDay:n/dl.length,win:w/n,net,hold:hold/n,yrs:Object.values(Y).filter(v=>v>0).length,p:S.p,f:S.f}; }
module.exports={run};
if(require.main===module){
 const base={sessStart:1000,sessEnd:1530,maxTrades:6,maxConsec:3,risk:200,maxHold:90,keyMode:'either',swingN:20};
 for (const stopMode of ['signal','pullback','swing']) for (const tgtMode of ['r','levels']) for (const volMin of [0,1.0,1.3]) for (const trendMode of ['ema','swing']) for (const extra of [{},{useLH:true},{congMult:2}]) {
   const P={...base,stopMode,tgtMode,volMin,trendMode,...extra,exhaust:tgtMode==='levels'}; const r=run(P); rows.push({P:{stopMode,tgtMode,volMin,trendMode,...extra},...r});
 }
 const f=r=>`${JSON.stringify(r.P).padEnd(90)} ${r.perDay.toFixed(2)}/d win ${(r.win*100).toFixed(0)}% net ${Math.round(r.net)} hold ${r.hold.toFixed(0)}m yrs+ ${r.yrs}/6 P/F ${(r.p*100).toFixed(0)}/${(r.f*100).toFixed(0)}`;
 rows.sort((a,b)=>b.net-a.net); const act=rows.filter(r=>r.perDay>=0.15); console.log("ACTIVE (>=0.15 trades/day):",act.length,"positive:",act.filter(r=>r.net>0).length); act.slice(0,6).forEach(r=>console.log(f(r)));
 `${JSON.stringify(r.P).padEnd(90)} ${r.perDay.toFixed(2)}/d win ${(r.win*100).toFixed(0)}% net ${Math.round(r.net)} hold ${r.hold.toFixed(0)}m yrs+ ${r.yrs}/6 P/F ${(r.p*100).toFixed(0)}/${(r.f*100).toFixed(0)}`;
 console.log('TOP 8'); rows.slice(0,8).forEach(r=>console.log(f(r)));
 console.log('share positive', rows.filter(r=>r.net>0).length,'/',rows.length);
}
