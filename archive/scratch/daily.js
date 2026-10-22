const E=require('/home/claude/mnqscalp/lab/engine.js'), fs=require('fs');
const days=E.parseBars(fs.readFileSync('/home/claude/mnqscalp/lab/mnq_rth.txt','utf8')); const MK={pv:2,tick:0.25};
const byD=new Map(days.map((x,i)=>[x.d,i]));
// EMA21 over RTH bars, avg range
const emaOf=new Map(); { let e=null; const k=2/22; for(const {d,b} of days){ const a=[]; for(const x of b){ e=e===null?x[4]:e+k*(x[4]-e); a.push(e);} emaOf.set(d,a);} }
const strat={ 'ORB break':E.simORB(days,{orMin:15,stopMode:'opp',tgtR:2,risk:300,lastEntry:1130,slip:1,both:true,comm:2.37,maxQty:20},MK),
  'Retest V3':E.simRT2(days,{risk:400,stop:'opp',lvlTgt:true,lvlGap:4,minRoomR:1},MK),
  'Retest V2':E.simRT2(days,{risk:400,stop:'opp'},MK)};
function feat(d,t){ const i=byD.get(d), b=days[i].b, em=emaOf.get(d); const j=t.eI, s=t.side;
  const pv=days[i-1].b; const pdC=pv[pv.length-1][4], pdO=pv[0][1];
  const ar=b.slice(Math.max(0,j-12),j).reduce((a,x)=>a+x[2]-x[3],0)/Math.max(1,Math.min(12,j)) || (b[j][2]-b[j][3]);
  const slope=j>=3?(em[j-1]-em[j-4])*s:0; const withTrend = slope>0 && (b[j-1][4]-em[j-1])*s>0;
  const ext=(b[j-1][4]-em[j-1])*s/ar;   // how stretched from EMA, in candles
  const lv=[...new Set([].concat(...[1,2,3].map(k=>i-k>=0?[Math.max(...days[i-k].b.map(x=>x[2])),Math.min(...days[i-k].b.map(x=>x[3]))]:[])))];
  const ahead=lv.filter(x=>(x-t.eP)*s>4).sort((a,z)=>(a-z)*s); const r=Math.abs(t.eP-(t.stp??t.eP));
  const stopPts=t.r||null;
  const dayOpenMove=(b[j-1][4]-b[0][1])*s; // has the day already moved our way
  return {tm:b[j][0], withTrend, ext:+ext.toFixed(2), gapWith:((b[0][1]-pdC)*s>0), pdWith:((pdC-pdO)*s>0), roomPts: ahead.length?Math.abs(ahead[0]-t.eP):null, movedPts:Math.round(dayOpenMove), ar:+ar.toFixed(1)};
}
const out={};
for (const [nm,dt] of Object.entries(strat)) {
  for (const [lab,from,to] of [['Oct 2026',20261001,20261031],['Oct 2025',20251001,20251031]]) {
    const rows=[]; dt.forEach((l,d)=>{ if(d<from||d>to||!l.length) return; rows.push({d,pnl:l.reduce((a,t)=>a+t.pnl,0),trades:l.map(t=>({...feat(d,t),side:t.side>0?'L':'S',pnl:Math.round(t.pnl),why:t.why,hold:t.hold,q:t.q}))}); });
    out[nm+'|'+lab]=rows;
    const g=rows.filter(r=>r.pnl>0), rd=rows.filter(r=>r.pnl<=0);
    console.log(`\n${nm} ${lab}: ${rows.length} trading days, green ${g.length} (+$${Math.round(g.reduce((a,r)=>a+r.pnl,0))}), red ${rd.length} (-$${Math.round(-rd.reduce((a,r)=>a+r.pnl,0))}), net $${Math.round(rows.reduce((a,r)=>a+r.pnl,0))}`);
    console.log('   '+rows.map(r=>`${String(r.d).slice(6)}:${r.pnl>0?'+':''}${Math.round(r.pnl)}`).join(' '));
  }
}
// winners vs losers over Sep 2025 - Oct 2026 (enough trades to see patterns)
console.log('\nWINNERS vs LOSERS, Oct 2025 - Oct 2026');
for (const [nm,dt] of Object.entries(strat)) {
  const T=[]; dt.forEach((l,d)=>{ if(d<20251001||d>20261031) return; l.forEach(t=>T.push({...feat(d,t),pnl:t.pnl,hold:t.hold,why:t.why})); });
  const grp=(f)=>{const w=T.filter(t=>t.pnl>0&&f(t)).length, n=T.filter(f).length; const pnl=T.filter(f).reduce((a,t)=>a+t.pnl,0); return `${n} tr, win ${n?Math.round(100*w/n):0}%, $${Math.round(pnl)}`;};
  console.log(`\n${nm} (${T.length} trades)`);
  console.log('  with trend      :',grp(t=>t.withTrend),' | against/no trend:',grp(t=>!t.withTrend));
  console.log('  entry < 10:00   :',grp(t=>t.tm<1000),' | 10:00-11:00:',grp(t=>t.tm>=1000&&t.tm<1100),' | 11:00+:',grp(t=>t.tm>=1100));
  console.log('  stretched >2 candles from EMA:',grp(t=>t.ext>2),' | 0-2:',grp(t=>t.ext>=0&&t.ext<=2),' | wrong side of EMA:',grp(t=>t.ext<0));
  console.log('  day already moved >150pt our way:',grp(t=>t.movedPts>150),' | less:',grp(t=>t.movedPts<=150));
  console.log('  prior day same direction:',grp(t=>t.pdWith),' | opposite:',grp(t=>!t.pdWith));
  console.log('  gap with us:',grp(t=>t.gapWith),' | gap against:',grp(t=>!t.gapWith));
  console.log('  room to prior-day H/L < 50pt:',grp(t=>t.roomPts!==null&&t.roomPts<50),' | >=50 or none:',grp(t=>t.roomPts===null||t.roomPts>=50));
  console.log('  exit reason:',['target','stop','close'].map(w=>w+' '+grp(t=>t.why===w)).join(' | '));
}
fs.writeFileSync('daily.json',JSON.stringify(out));
