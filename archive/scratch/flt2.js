const E=require('/home/claude/mnqscalp/lab/engine.js'), fs=require('fs');
const days=E.parseBars(fs.readFileSync('/home/claude/mnqscalp/lab/mnq_rth.txt','utf8')); const MK={pv:2,tick:0.25};
const dl=days.map(x=>x.d);
const st=(dt,a,z)=>{let N=0,NET=0,W=0,GW=0,GL=0,g=0,r=0;dt.forEach((l,d)=>{if(d<a||d>z)return;let dp=0;l.forEach(t=>{N++;NET+=t.pnl;dp+=t.pnl;if(t.pnl>0){W++;GW+=t.pnl}else GL-=t.pnl});if(l.length){if(dp>0)g++;else r++;}});return {N,NET,win:N?W/N:0,pf:GL?GW/GL:9,g,r,aw:W?GW/W:0,al:N-W?GL/(N-W):0};};
const f=s=>`${String(s.N).padStart(3)} tr ${String(Math.round(s.NET)).padStart(6)}$ PF ${s.pf.toFixed(2)} win ${(s.win*100).toFixed(0)}% avg win $${Math.round(s.aw)} / loss $${Math.round(s.al)} | green/red days ${s.g}/${s.r}`;
const months=(dt,a,z)=>{let p=0,n=0;for(let ym=a;ym<=z;ym=(ym%100===12?ym+89:ym+1)){const s=st(dt,ym*100,ym*100+31);if(s.N){n++;if(s.NET>0)p++;}}return p+'/'+n;};
const base={orMin:15,stopMode:'opp',tgtR:2,risk:300,lastEntry:1130,slip:1,both:true,comm:2.37,maxQty:20};
const F={target:1250,mll:1000,dll:600,cap:600,consist:50,evDays:20};
for (const [nm,P] of [['ORB as is',{}],['ORB + trend (wait for trend)',{trendF:true}],['ORB + trend (skip side if not)',{trendF:'skip'}]]) {
 const dt=E.simORB(days,{...base,...P},MK); console.log(nm);
 for (const [lab,a,z] of [['Oct 2026',20261001,20261031],['Oct 2025',20251001,20251031],['Oct 2024',20241001,20241031],['Sep 2026',20260901,20260930],['Sep 2025',20250901,20250930]]) console.log('  ',lab.padEnd(9),f(st(dt,a,z)));
 for (const [lab,a,z,ma,mz] of [['Oct25-Oct26',20251001,20261031,202510,202610],['Oct24-Sep25',20241001,20250930,202410,202509],['Oct21-Sep24',20211001,20240930,202110,202409]]) {
   const S=E.summarize(E.evals(dl.filter(d=>d>=a&&d<=z),new Map([...dt].filter(([d])=>d>=a&&d<=z)),F));
   console.log('  ',lab.padEnd(11),f(st(dt,a,z)),'| months+',months(dt,ma,mz),'| 20-day evals pass/fail',(S.p*100).toFixed(0)+'/'+(S.f*100).toFixed(0)); }
}
