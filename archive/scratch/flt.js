const E=require('/home/claude/mnqscalp/lab/engine.js'), fs=require('fs');
const days=E.parseBars(fs.readFileSync('/home/claude/mnqscalp/lab/mnq_rth.txt','utf8')); const MK={pv:2,tick:0.25};
const dl=days.map(x=>x.d); const F={target:1250,mll:1000,dll:600,cap:600,consist:50,evDays:20};
const st=(dt,a,z)=>{let N=0,NET=0,W=0,GW=0,GL=0,g=0,r=0;dt.forEach((l,d)=>{if(d<a||d>z)return;let dp=0;l.forEach(t=>{N++;NET+=t.pnl;dp+=t.pnl;if(t.pnl>0){W++;GW+=t.pnl}else GL-=t.pnl});if(l.length){if(dp>0)g++;else r++;}});return {N,NET,win:N?W/N:0,pf:GL?GW/GL:9,g,r};};
const f=s=>`${String(s.N).padStart(3)} tr ${String(Math.round(s.NET)).padStart(6)}$ PF ${s.pf.toFixed(2)} win ${(s.win*100).toFixed(0)}% green/red days ${s.g}/${s.r}`;
const months=(dt,a,z)=>{let p=0,n=0;for(let ym=a;ym<=z;ym=(ym%100===12?ym+89:ym+1)){const s=st(dt,ym*100,ym*100+31);if(s.N){n++;if(s.NET>0)p++;}}return p+'/'+n;};
const runs={
 'ORB break (as is)':E.simORB(days,{orMin:15,stopMode:'opp',tgtR:2,risk:300,lastEntry:1130,slip:1,both:true,comm:2.37,maxQty:20},MK),
 'ORB + start 10:00':E.simORB(days,{orMin:15,stopMode:'opp',tgtR:2,risk:300,lastEntry:1130,slip:1,both:true,comm:2.37,maxQty:20,firstEntry:1000},MK),
 'ORB + trend':E.simORB(days,{orMin:15,stopMode:'opp',tgtR:2,risk:300,lastEntry:1130,slip:1,both:true,comm:2.37,maxQty:20,trendF:true},MK),
 'ORB + 10:00 + trend':E.simORB(days,{orMin:15,stopMode:'opp',tgtR:2,risk:300,lastEntry:1130,slip:1,both:true,comm:2.37,maxQty:20,firstEntry:1000,trendF:true},MK),
 'ORB + 10:00 + trend, last 12:00':E.simORB(days,{orMin:15,stopMode:'opp',tgtR:2,risk:300,lastEntry:1200,slip:1,both:true,comm:2.37,maxQty:20,firstEntry:1000,trendF:true},MK),
 'RT V2 (as is)':E.simRT2(days,{risk:400,stop:'opp'},MK),
 'RT V2 + not stretched (<=2)':E.simRT2(days,{risk:400,stop:'opp',maxExt:2},MK),
 'RT V2 + room 50pt':E.simRT2(days,{risk:400,stop:'opp',minRoomPts:50},MK),
 'RT V2 + not stretched + room':E.simRT2(days,{risk:400,stop:'opp',maxExt:2,minRoomPts:50},MK),
 'RT V2 + not stretched + room + trend':E.simRT2(days,{risk:400,stop:'opp',maxExt:2,minRoomPts:50,trendF:true},MK),
};
for (const [nm,dt] of Object.entries(runs)) {
 const S=E.summarize(E.evals(dl.filter(d=>d>=20251001),new Map([...dt].filter(([d])=>d>=20251001)),F));
 console.log(nm);
 console.log('   Oct 2026            ',f(st(dt,20261001,20261031)));
 console.log('   Oct 2025            ',f(st(dt,20251001,20251031)));
 console.log('   Oct 25-Oct 26 (found)',f(st(dt,20251001,20261031)),'| months+',months(dt,202510,202610),'| evals pass/fail',(S.p*100).toFixed(0)+'/'+(S.f*100).toFixed(0));
 console.log('   Oct 24-Sep 25 (check)',f(st(dt,20241001,20250930)),'| months+',months(dt,202410,202509));
}
