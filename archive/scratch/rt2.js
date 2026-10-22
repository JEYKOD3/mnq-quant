const E=require('/home/claude/mnqscalp/lab/engine.js'), fs=require('fs');
const F={target:1250,mll:1000,dll:600,cap:600,consist:50,evDays:30};
const cache={}; const load=mk=>cache[mk]||(cache[mk]=E.parseBars(fs.readFileSync(`/home/claude/mnqscalp/lab/${mk}_rth.txt`,'utf8')));
function run(lbl,mk,P){ const MK={mnq:{pv:2,tick:0.25},mes:{pv:5,tick:0.25}}[mk]; const days=load(mk), dl=days.map(x=>x.d);
  const dt=E.simRT2(days,P,MK); let net=0,n=0,w=0,hold=0,lm=0,lmn=0; const Y={},ST={}; dt.forEach((l,d)=>l.forEach(t=>{net+=t.pnl;n++;if(t.pnl>0)w++;hold+=t.hold;const y=Math.floor(d/1e4);Y[y]=(Y[y]||0)+t.pnl;ST[t.setup]=ST[t.setup]||[0,0,0];ST[t.setup][0]++;ST[t.setup][1]+=t.pnl>0;ST[t.setup][2]+=t.pnl;if(d>=20260921){lm+=t.pnl;lmn++;}}));
  const S=E.summarize(E.evals(dl,dt,F)); const q=x=>S.pd[Math.floor(x*(S.pd.length-1))];
  console.log(`${mk} ${lbl.padEnd(46)} ${(n/dl.length).toFixed(2)}/d win ${(100*w/n).toFixed(0)}% net ${String(Math.round(net)).padStart(7)} hold ${(hold/n).toFixed(0)}m yrs+ ${Object.values(Y).filter(v=>v>0).length}/6 | P/F ${(S.p*100).toFixed(0)}/${(S.f*100).toFixed(0)} days ${q(.5)} | lastmo ${lmn}t ${Math.round(lm)} | ${Object.entries(ST).map(([k,a])=>`${k}:${a[0]} ${Math.round(100*a[1]/a[0])}% ${(a[2]/1000).toFixed(1)}k`).join(' ')}`); }
module.exports={run};
if(require.main===module){
 const B={risk:400};
 for (const mk of ['mnq','mes']) {
  for (const stop of ['opp','mid','structure','signal']) run(`stop ${stop}, no fade`, mk, {...B,stop,bigPts:0});
  const bigs = mk==='mnq' ? [40,60,80,100] : [10,15,20,25];
  for (const bp of bigs) run(`structure stop, big range >= ${bp} pts fade`, mk, {...B,stop:'structure',bigPts:bp});
  for (const bp of bigs) run(`opp stop, big range >= ${bp} pts fade`, mk, {...B,stop:'opp',bigPts:bp});
  run('structure buf 8 ticks, minStop 24', mk, {...B,stop:'structure',bufT:8,minStop:24});
  run('structure, target 1.5R', mk, {...B,stop:'structure',tgtR:1.5});
  run('structure, target 3R', mk, {...B,stop:'structure',tgtR:3});
 }
}
