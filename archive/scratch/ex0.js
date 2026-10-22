const E=require('/home/claude/mnqscalp/lab/engine.js'), fs=require('fs');
const days=E.parseBars(fs.readFileSync('/home/claude/mnqscalp/lab/mnq_rth.txt','utf8'));
const MK={pv:2,tick:0.25};
const RT=P=>E.simRT2(days,{risk:400,stop:'opp',...P},MK), ORB=P=>E.simORB(days,{orMin:15,stopMode:'opp',tgtR:2,risk:300,lastEntry:1130,slip:1,both:true,comm:2.37,maxQty:20,...P},MK);
for (const [nm,f] of [['RT2',RT],['ORB',ORB]]) {
 const dt=f({}); let N=0,NET=0; const mf=[]; const why={};
 dt.forEach(l=>l.forEach(t=>{N++;NET+=t.pnl;mf.push(t.mfeR);why[t.why]=(why[t.why]||0)+1}));
 mf.sort((a,b)=>a-b); const pct=x=>mf.filter(v=>v>=x).length/N*100;
 console.log(nm,N,Math.round(NET),JSON.stringify(why),'| reached +1R',pct(1).toFixed(0)+'%','+2R',pct(2).toFixed(0)+'%','+3R',pct(3).toFixed(0)+'%','+4R',pct(4).toFixed(0)+'%');
 // of stopped-out trades, how many had been +1R first
 let s1=0,ss=0; dt.forEach(l=>l.forEach(t=>{if(t.why==='stop'){ss++; if(t.mfeR>=1)s1++;}})); console.log('  stopped trades',ss,'that were +1R first',s1,(100*s1/ss).toFixed(0)+'%');
}
