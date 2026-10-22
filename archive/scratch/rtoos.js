const E=require('/home/claude/mnqscalp/lab/engine.js'), fs=require('fs'), {report,line}=require('./rep.js');
const all=E.parseBars(fs.readFileSync('/home/claude/mnqscalp/lab/mnq_rth.txt','utf8')); const MK={pv:2,tick:0.25};
const W={}; { const hist=[]; for(const {d,b} of all){ if(b.length<3) continue; let hi=-1e9,lo=1e9; for(let i=0;i<3;i++){hi=Math.max(hi,b[i][2]);lo=Math.min(lo,b[i][3]);} const w=hi-lo; const a=hist.length>=20?hist.slice(-20).reduce((x,y)=>x+y)/20:null; W[d]=a?w/a:1; hist.push(w);} }
const filt=(dt,lo,hi)=>{ const o=new Map(); dt.forEach((l,d)=>o.set(d,(W[d]>=lo&&W[d]<=hi)?l:[])); return o; };
const cfgs=[['RT or30 15m structure tgt1 lvl1.5 trend width<=1.5',{orMin:30,brk:'15m',stop:'structure',bufT:4,minStop:16,tgtR:1,lvlTgt:true,lvlGap:4,minRoomR:1.5,trendF:true},1.5],
 ['RT or30 15m structure tgt1 lvl1 width<=1.5',{orMin:30,brk:'15m',stop:'structure',bufT:4,minStop:16,tgtR:1,lvlTgt:true,lvlGap:4,minRoomR:1},1.5],
 ['RT or15 5m opp tgt2 (V2 as is)',{orMin:15,brk:'5m',stop:'opp',tgtR:2},99]];
for (const [nm,P,wf] of cfgs){ const dt=filt(E.simRT2(all,{risk:400,maxQty:20,dayStop:0,dayTarget:0,...P},MK),0,wf); console.log(nm);
  for (const [l,a,z] of [['2022',20220101,20221231],['2023',20230101,20231231],['2024',20240101,20241231],['2025',20250101,20251231],['2026',20260101,20261020],['last 6 mo',20260421,20261020]]) console.log('  ',l.padEnd(9),line(report(dt,a,z))); }
