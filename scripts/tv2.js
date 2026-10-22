const E=require('../engine/js/engine.js'), fs=require('fs'), {report,line}=require('../engine/js/report.js');
const all=E.parseBars(fs.readFileSync('../data/raw/mnq_rth_5m.txt','utf8')); const MK={pv:2,tick:0.25}; const feat=JSON.parse(fs.readFileSync('dayfeat.json'));
const sel=dt=>{ const m=new Map(); dt.forEach((l,d)=>{ if(feat[d]&&feat[d].committed) m.set(d,l); }); return m; };
function tv(dt,a,z,label){ const T=[]; dt.forEach((l,d)=>{ if(d>=a&&d<=z) l.forEach(t=>T.push({d,...t})); }); T.sort((x,y)=>x.d-y.d||x.eI-y.eI);
  let eq=0,pk=0,dd=0,gp=0,gl=0,w=0; const hist={}; for(const t of T){ eq+=t.pnl; pk=Math.max(pk,eq); dd=Math.max(dd,pk-eq); if(t.pnl>0){w++;gp+=t.pnl}else gl-=t.pnl; const b=Math.floor(t.pnl/100)*100; hist[b]=(hist[b]||0)+1; }
  const R=report(dt,a,z); const L=T.filter(t=>t.side>0), S=T.filter(t=>t.side<0); const st=A=>{const n=A.length,ww=A.filter(t=>t.pnl>0).length; return `${n} tr ${n?Math.round(100*ww/n):0}% win ${Math.round(A.reduce((s,t)=>s+t.pnl,0))}$`;};
  console.log(`\n== ${label}`); console.log(`Net P&L ${Math.round(eq)}$ | Max drawdown ${Math.round(dd)}$ | Profitable ${w}/${T.length} (${T.length?Math.round(100*w/T.length):0}%) | PF ${gl?(gp/gl).toFixed(2):'inf'} | avg win ${Math.round(gp/Math.max(1,w))} avg loss ${Math.round(gl/Math.max(1,T.length-w))} | avg hold ${Math.round(T.reduce((s,t)=>s+t.hold,0)/Math.max(1,T.length))} min`);
  console.log(`Long ${st(L)} | Short ${st(S)} | days G/R ${R.g}/${R.r} | weeks+ ${R.wk}/${R.wkn} | months+ ${R.mo}/${R.mon} | worst day ${R.worstDay}`);
  console.log('Months: '+Object.entries(R.months).map(([k,v])=>k.slice(2)+' '+(v>=0?'+':'')+v).join(' | '));
  console.log('Distribution: '+Object.keys(hist).map(Number).sort((a,b)=>a-b).map(b=>`[${b},${b+100}) ${hist[b]}`).join(' '));
}
const orb=sel(E.simORB(all,{orMin:15,stopMode:'opp',tgtR:2,risk:300,lastEntry:1130,slip:1,both:true,comm:2.37,maxQty:20},MK));
const rt=sel(E.simRT2(all,{risk:400,stop:'opp',tgtR:2},MK));
for (const [nm,dt] of [['ORB BREAK adaptive ($300 risk)',orb],['ORB RETEST V2 adaptive ($400 risk)',rt]]) {
  tv(dt,20260101,20261020,nm+' | Jan 1 - Oct 20 2026'); tv(dt,20260421,20261020,nm+' | last 6 months'); tv(dt,20260920,20261021,nm+' | TradingView month Sep 20 - Oct 21'); }
// trade list for TV month
for (const [nm,dt] of [['ORB BREAK',orb],['RETEST V2',rt]]) { console.log('\n'+nm+' trades since Sep 20:'); dt.forEach((l,d)=>{ if(d>=20260920) l.forEach(t=>console.log(d,all.find(x=>x.d===d).b[t.eI][0],t.side>0?'L':'S','q'+t.q,'in',t.eP,'out',t.xP,t.why,Math.round(t.pnl))); }); }
console.log('\ncommitted days since Sep 20:',Object.entries(feat).filter(([d,f])=>+d>=20260920&&f.committed).map(([d,f])=>d+'(gap '+f.gap+' dir '+f.orDir+')').join(' '));
