const E=require('/home/claude/mnqscalp/lab/engine.js'), fs=require('fs');
const days=E.parseBars(fs.readFileSync('/home/claude/mnqscalp/lab/mnq_rth.txt','utf8')); const dl=days.map(x=>x.d);
const MK={pv:2,tick:0.25}; const F={target:1250,mll:1000,dll:600,cap:600,consist:50,evDays:60};
const base={emaLen:21,slopeBars:3,keyTol:8,sigFrac:0.5,minBody:0.3,swingN:20,minStop:12,maxStop:100,risk:300,maxQty:20,tp1R:1,tp1Pct:50,runR:2,beOn:true,maxTrades:3,dayTarget:600,dayLoss:550,maxConsec:2,sessStart:1000,sessEnd:1530,comm:2.37,slip:1};
const rows=[];
for (const keyMode of ['ema','either']) for (const stopMode of ['signal','pullback','swing']) for (const tgtMode of ['r','levels']) for (const room of [0,1,1.5]) for (const maxHold of [40,0]) for (const trendMode of ['ema','swing']) for (const useLH of [false,true]) {
  if (tgtMode==='r' && room) continue;
  const P={...base,keyMode,stopMode,tgtMode,minRoomR:room,maxHold,trendMode,useLH}; const dt=E.simW2E(days,P,MK);
  let N=0,NET=0,W=0; const Y={}; dt.forEach((l,d)=>l.forEach(t=>{N++;NET+=t.pnl;if(t.pnl>0)W++;const y=Math.floor(d/1e4);Y[y]=(Y[y]||0)+t.pnl}));
  if(!N) continue; const S=E.summarize(E.evals(dl,dt,F));
  rows.push({k:`key ${keyMode} stop ${stopMode} tgt ${tgtMode} room ${room} hold ${maxHold||'none'} trend ${trendMode} HL/LH ${useLH?'on':'off'}`,N,NET,W:W/N,p:S.p,f:S.f,yp:Object.values(Y).filter(x=>x>0).length});
}
rows.sort((a,b)=>b.NET-a.NET); console.log('combos',rows.length,'profitable',rows.filter(r=>r.NET>0).length);
rows.slice(0,8).forEach(r=>console.log(r.k.padEnd(84),'trades',r.N,'('+(r.N/dl.length).toFixed(2)+'/day) net',Math.round(r.NET),'win',(r.W*100).toFixed(0)+'%','PASS',(r.p*100).toFixed(0),'FAIL',(r.f*100).toFixed(0),'yrs+',r.yp));
