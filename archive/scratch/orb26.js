const E=require('/home/claude/mnqscalp/lab/engine.js'), fs=require('fs'), {report,line,score}=require('./rep.js');
const all=E.parseBars(fs.readFileSync('/home/claude/mnqscalp/lab/mnq_rth.txt','utf8')); const days=all.filter(x=>x.d>=20251101); const MK={pv:2,tick:0.25};
const A=[20260101,20260531], Bh=[20260601,20261020];
// OR width filter helper: ratio to 20-day avg
const W={}; { const hist=[]; for(const {d,b} of all){ if(b.length<3) continue; let hi=-1e9,lo=1e9; for(let i=0;i<3;i++){hi=Math.max(hi,b[i][2]);lo=Math.min(lo,b[i][3]);} const w=hi-lo; const a=hist.length>=20?hist.slice(-20).reduce((x,y)=>x+y)/20:null; W[d]=a?w/a:1; hist.push(w);} }
const filt=(dt,lo,hi)=>{ const o=new Map(); dt.forEach((l,d)=>o.set(d,(W[d]>=lo&&W[d]<=hi)?l:[])); return o; };
const out=[];
const push=(name,dt)=>{ const RA=report(dt,...A), RB=report(dt,...Bh), RT=report(dt,A[0],Bh[1]); out.push({name,A:RA,B:RB,T:RT,sc:Math.min(score(RA),score(RB))}); };
const base={orMin:15,stopMode:'opp',tgtR:2,risk:300,lastEntry:1130,slip:1,both:true,comm:2.37,maxQty:20};
for (const orMin of [15,30]) for (const stopMode of ['opp','mid']) for (const tgtR of [1,1.5,2,3,0]) for (const lastEntry of [1030,1130,1300]) for (const trendF of [false,'skip']) for (const wf of [[0,99],[0,1.5],[0.6,1.5],[0.7,99]]) {
  const dt=E.simORB(days,{...base,orMin,stopMode,tgtR,lastEntry,trendF},MK); push(`ORB break or${orMin} stop ${stopMode} tgt ${tgtR||'EOD'} last ${lastEntry} trend ${trendF||'off'} width ${wf[0]}-${wf[1]}`, filt(dt,...wf)); }
const b2={risk:400,stop:'opp',maxQty:20,dayStop:0,dayTarget:0};
for (const orMin of [15,30]) for (const brk of ['5m','15m']) for (const stop of ['opp','structure','mid']) for (const tgtR of [1,1.5,2,3]) for (const lv of [0,1,1.5]) for (const maxExt of [0,2]) for (const trendF of [false,true]) for (const wf of [[0,99],[0,1.5]]) {
  const P={...b2,orMin,brk,stop,tgtR,maxExt,trendF}; if(stop==='structure'){P.bufT=4;P.minStop=16;} if(lv){P.lvlTgt=true;P.lvlGap=4;P.minRoomR=lv;}
  const dt=E.simRT2(days,P,MK); push(`ORB retest or${orMin} brk ${brk} stop ${stop} tgt ${tgtR} levels ${lv||'off'} stretch<=${maxExt||'any'} trend ${trendF?'on':'off'} width ${wf[0]}-${wf[1]}`, filt(dt,...wf)); }
fs.writeFileSync('orb26.json',JSON.stringify(out));
out.sort((a,b)=>b.sc-a.sc);
console.log('variants',out.length,'| both halves profitable',out.filter(o=>o.A.net>0&&o.B.net>0).length,'| green>=55% both',out.filter(o=>o.A.g>=.55*(o.A.g+o.A.r)&&o.B.g>=.55*(o.B.g+o.B.r)).length);
for (const o of out.slice(0,12)) { console.log(o.name); console.log('   Jan-May',line(o.A)); console.log('   Jun-Oct',line(o.B)); }
