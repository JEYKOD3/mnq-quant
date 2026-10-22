const E=require('/home/claude/mnqscalp/lab/engine.js'), fs=require('fs');
const days=E.parseBars(fs.readFileSync('/home/claude/mnqscalp/lab/mnq_rth.txt','utf8'));
const dt=E.simRT2(days,{risk:400,stop:'opp',lvlTgt:true,lvlGap:4,minRoomR:1},{pv:2,tick:0.25});
let n=0,net=0; dt.forEach((l,d)=>{ if(d<20260921) return; const b=days.find(x=>x.d===d).b; l.forEach(t=>{n++;net+=t.pnl;console.log(d,b[t.eI][0],t.side>0?'long':'short','qty',t.q,'entry',t.eP,'exit',t.xP,t.why,Math.round(t.pnl))})});
console.log('month',n,'trades net',Math.round(net));
