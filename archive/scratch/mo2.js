const E=require('/home/claude/mnqscalp/lab/engine.js'), fs=require('fs');
const days=E.parseBars(fs.readFileSync('/home/claude/mnqscalp/lab/mnq_rth.txt','utf8'));
for (const sm of ['opp']) {
const dt=E.simORB(days,{orMin:15,stopMode:sm,tgtR:2,risk:300,lastEntry:1130,slip:1,both:true,comm:2.37,maxQty:20},{pv:2,tick:0.25}); const M={};let N=0,NET=0;
dt.forEach((l,d)=>l.forEach(t=>{N++;NET+=t.pnl;const k=Math.floor(d/100);M[k]=(M[k]||0)+t.pnl}));
const v=Object.values(M); console.log('ORB',sm,N,'trades net',Math.round(NET),'months',v.length,'pos',v.filter(x=>x>0).length);
console.log(Object.entries(M).slice(-8).map(([k,x])=>k+':'+Math.round(x)).join(' '));}
