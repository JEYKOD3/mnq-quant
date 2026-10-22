const E=require('/home/claude/mnqscalp/lab/engine.js'), fs=require('fs');
const days=E.parseBars(fs.readFileSync('/home/claude/mnqscalp/lab/mnq_rth.txt','utf8'));
for (const [nm,P] of [['retestV2',{risk:400,stop:'opp'}]]) {
const dt=E.simRT2(days,P,{pv:2,tick:0.25}); const M={};
dt.forEach((l,d)=>l.forEach(t=>{const k=Math.floor(d/100);M[k]=(M[k]||0)+t.pnl}));
const v=Object.values(M); console.log(nm,'months',v.length,'positive',v.filter(x=>x>0).length,'worst',Math.round(Math.min(...v)),'best',Math.round(Math.max(...v)));
console.log(Object.entries(M).slice(-8).map(([k,x])=>k+':'+Math.round(x)).join(' '));}
const d2=E.simORB?E.simORB(days,{},{pv:2,tick:0.25}):null; if(d2){const M={};d2.forEach((l,d)=>l.forEach(t=>{const k=Math.floor(d/100);M[k]=(M[k]||0)+t.pnl}));const v=Object.values(M);console.log('ORBbreak months',v.length,'positive',v.filter(x=>x>0).length);console.log(Object.entries(M).slice(-8).map(([k,x])=>k+':'+Math.round(x)).join(' '));}
