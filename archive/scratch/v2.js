const E=require('/home/claude/mnqscalp/lab/engine.js'), fs=require('fs');
const F={target:1250,mll:1000,dll:600,cap:600,consist:50,evDays:30};
const cache={}; const load=f=>cache[f]||(cache[f]=E.parseBars(fs.readFileSync('/home/claude/mnqscalp/lab/'+f,'utf8')));
function run(lbl,file,bar,P,mk='mnq'){
  E.setBar(bar); const MK={mnq:{pv:2,tick:0.25},mes:{pv:5,tick:0.25}}[mk];
  const days=load(file), dl=days.map(x=>x.d); const dt=E.simW2E(days,P,MK);
  let net=0,n=0,w=0,hold=0,lm=0,lmn=0,lmw=0; const Y={}, ST={};
  dt.forEach((l,d)=>l.forEach(t=>{net+=t.pnl;n++;if(t.pnl>0)w++;hold+=t.hold;const y=Math.floor(d/1e4);Y[y]=(Y[y]||0)+t.pnl;ST[t.setup]=ST[t.setup]||[0,0,0];ST[t.setup][0]++;ST[t.setup][1]+=t.pnl>0;ST[t.setup][2]+=t.pnl; if(d>=20260921){lm+=t.pnl;lmn++;if(t.pnl>0)lmw++;}}));
  const S=E.summarize(E.evals(dl,dt,F));
  console.log(`${lbl.padEnd(40)} ${(n/dl.length).toFixed(2)}/day win ${(100*w/n).toFixed(0)}% net ${String(Math.round(net)).padStart(7)} hold ${(hold/n).toFixed(0)}m yrs+ ${Object.values(Y).filter(v=>v>0).length}/6 | last month ${lmn}t ${lmn?Math.round(100*lmw/lmn):0}% ${Math.round(lm)} | P/F ${(S.p*100).toFixed(0)}/${(S.f*100).toFixed(0)} | ${Object.entries(ST).map(([k,a])=>`${k}:${a[0]} ${Math.round(100*a[1]/a[0])}% ${Math.round(a[2]/1000)}k`).join(' ')}`);
  E.setBar(5);
}
module.exports={run};
if (require.main===module){
 const B={maxTrades:5};
 run('V1 rules (RTH 5m)','mnq_rth.txt',5,{...B});
 run('+ trendline key point (either)','mnq_rth.txt',5,{...B,keyMode:'either'});
 run('+ both EMA and TL','mnq_rth.txt',5,{...B,keyMode:'both'});
 run('+ correction TL rule','mnq_rth.txt',5,{...B,corrTL:true});
 run('+ LH/HL','mnq_rth.txt',5,{...B,useLH:true});
 run('+ F2','mnq_rth.txt',5,{...B,useF2:true});
 run('+ congestion 1.5','mnq_rth.txt',5,{...B,congMult:1.5});
 run('+ congestion 2.5','mnq_rth.txt',5,{...B,congMult:2.5});
 const ALL={...B,keyMode:'either',corrTL:true,useLH:true,useF2:true,congMult:2};
 run('ALL rules RTH 5m','mnq_rth.txt',5,ALL);
 run('ALL rules London+NY 5m (3:00-15:30)','mnq_eth.txt',5,{...ALL,sessStart:300});
 run('ALL rules 24h 5m','mnq_eth.txt',5,{...ALL,sessStart:1800,sessEnd:1530,maxTrades:8});
 run('ALL rules RTH 1m','mnq_rth_1m.txt',1,{...ALL,swingN:60,fSwing:15,fBars:8,congBars:20,slopeBars:5,minStop:8});
}
