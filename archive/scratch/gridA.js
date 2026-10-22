const E=require('/home/claude/mnqscalp/lab/engine.js'), fs=require('fs');
const mk=process.argv[2]||'mnq'; const MK={mnq:{pv:2,tick:0.25},mes:{pv:5,tick:0.25}}[mk];
const days=E.parseBars(fs.readFileSync(`/home/claude/mnqscalp/lab/${mk}_rth.txt`,'utf8')); const dl=days.map(x=>x.d);
const F={target:1250,mll:1000,dll:600,cap:600,consist:50,evDays:20};
function yearly(ev,dt){const Y={};ev.forEach(e=>{const y=Math.floor(e.start/1e4);Y[y]=Y[y]||[0,0,0,0];Y[y][0]++;if(e.res===1)Y[y][1]++;if(e.res===-1)Y[y][2]++;});dl.forEach(d=>{const y=Math.floor(d/1e4);(dt.get(d)||[]).forEach(t=>{Y[y]&&(Y[y][3]+=t.pnl)})});return Y;}
const out=[];
for(const need of [1,2])for(const depth of [0,0.5,1])for(const tgtR of [1,1.5,2])for(const maxTrades of [2,4])for(const lastEntry of [1130,1300])for(const flip of [false,true]){
  const P={orMin:15,need,depth,tgtR,maxTrades,lastEntry,flip,risk:300,maxQty:20,comm:2.37,slip:1,minStop:8,dayStop:600};
  const dt=E.simPB(days,P,MK); const ev=E.evals(dl,dt,F); const S=E.summarize(ev);
  let net=0,n=0; dt.forEach(l=>l.forEach(t=>{net+=t.pnl;n++}));
  const Y=yearly(ev,dt); const beat=Object.values(Y).filter(a=>a[1]/a[0]>0.25).length;
  out.push({P,p:S.p,f:S.f,net,n,beat,Y,med:S.pd[Math.floor(S.pd.length/2)]});
}
out.sort((a,b)=>(b.p-0.5*b.f)-(a.p-0.5*a.f));
for(const r of out.slice(0,12)) console.log(`need${r.P.need} depth${r.P.depth} tgt${r.P.tgtR} max${r.P.maxTrades} last${r.P.lastEntry} flip${+r.P.flip} | PASS ${(r.p*100).toFixed(0)} FAIL ${(r.f*100).toFixed(0)} net ${Math.round(r.net)} n${r.n} med${r.med}d | `+Object.entries(r.Y).map(([y,a])=>`${y}:${Math.round(100*a[1]/a[0])}/${Math.round(100*a[2]/a[0])} ${Math.round(a[3]/1000)}k`).join(' '));
const nets=out.map(r=>r.net).sort((a,b)=>a-b); console.log('grid net median',Math.round(nets[nets.length>>1]),'share positive',(out.filter(r=>r.net>0).length/out.length).toFixed(2));
