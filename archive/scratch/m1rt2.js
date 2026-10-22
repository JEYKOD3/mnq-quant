const E=require('/home/claude/mnqscalp/lab/engine.js'), fs=require('fs');
const days=E.parseBars(fs.readFileSync('/home/claude/mnqscalp/lab/mnq_rth.txt','utf8'));
const dt=E.simRT2(days,{risk:400,stop:'opp'},{pv:2,tick:0.25});
let net=0,n=0,w=0;
dt.forEach((l,d)=>{ if(d<20260921) return; l.forEach(t=>{net+=t.pnl;n++;if(t.pnl>0)w++;console.log(d,t.hhmm||t.t,t.side,t.qty||t.q,Math.round(t.pnl),t.setup||'')})});
console.log('month',n,'trades net',Math.round(net),'win',w);
let N=0,NET=0; dt.forEach(l=>l.forEach(t=>{N++;NET+=t.pnl})); console.log('5yr',N,Math.round(NET));
