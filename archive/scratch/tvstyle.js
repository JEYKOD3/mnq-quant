const E=require('/home/claude/mnqscalp/lab/engine.js'), fs=require('fs'), {report,line}=require('./rep.js');
const all=E.parseBars(fs.readFileSync('/home/claude/mnqscalp/lab/mnq_rth.txt','utf8')); const MK={pv:2,tick:0.25};
function tv(dt,a,z,label){ const T=[]; dt.forEach((l,d)=>{ if(d>=a&&d<=z) l.forEach(t=>T.push({d,...t})); }); T.sort((x,y)=>x.d-y.d||x.eI-y.eI);
  let eq=0,pk=0,dd=0,gp=0,gl=0,w=0; const hist={}; for(const t of T){ eq+=t.pnl; pk=Math.max(pk,eq); dd=Math.max(dd,pk-eq); if(t.pnl>0){w++;gp+=t.pnl}else gl-=t.pnl; const b=Math.floor(t.pnl/100)*100; hist[b]=(hist[b]||0)+1; }
  const R=report(dt,a,z); const L=T.filter(t=>t.side>0), S=T.filter(t=>t.side<0); const st=A=>{const n=A.length,ww=A.filter(t=>t.pnl>0).length; return `${n} tr, ${n?Math.round(100*ww/n):0}% win, ${Math.round(A.reduce((s,t)=>s+t.pnl,0))}$`;};
  console.log(`\n== ${label}`); console.log(`Net P&L ${Math.round(eq)}$ | Max drawdown ${Math.round(dd)}$ | Profitable trades ${w}/${T.length} (${T.length?Math.round(100*w/T.length):0}%) | Profit factor ${gl?(gp/gl).toFixed(2):'inf'}`);
  console.log(`Avg win ${Math.round(gp/Math.max(1,w))}$ avg loss ${Math.round(gl/Math.max(1,T.length-w))}$ | largest win ${Math.round(Math.max(0,...T.map(t=>t.pnl)))} largest loss ${Math.round(Math.min(0,...T.map(t=>t.pnl)))} | avg hold ${Math.round(T.reduce((s,t)=>s+t.hold,0)/Math.max(1,T.length))} min`);
  console.log(`Long ${st(L)} | Short ${st(S)} | Days green/red ${R.g}/${R.r} | weeks+ ${R.wk}/${R.wkn} | months+ ${R.mo}/${R.mon}`);
  console.log('Months: '+Object.entries(R.months).map(([k,v])=>k+' '+(v>=0?'+':'')+v).join(' | '));
  console.log('Trade distribution ($100 bins): '+Object.keys(hist).map(Number).sort((a,b)=>a-b).map(b=>`[${b},${b+100}) ${hist[b]}`).join('  '));
  console.log('Exit reasons: '+JSON.stringify(T.reduce((o,t)=>{o[t.why]=(o[t.why]||0)+1;return o},{})));
}
const P={pokeMin:2,pokeMax:45,within:5,stopMode:'poke',tgtR:1,bufPts:5,sessStart:1000,lastEntry:1300,useSw:false,useOR:false,maxStop:60};
const dt=E.simFB(all,P,MK);
tv(dt,20260101,20261020,'Failed Break V1, Jan 1 - Oct 20 2026');
tv(dt,20260421,20261020,'Failed Break V1, last 6 months (Apr 21 - Oct 20 2026)');
tv(dt,20260920,20261021,'Failed Break V1, TradingView month (Sep 20 - Oct 21 2026)');
const T=[]; dt.forEach((l,d)=>{ if(d>=20260920) l.forEach(t=>T.push(`${d} ${all.find(x=>x.d===d).b[t.eI][0]} ${t.side>0?'L':'S'} q${t.q} in ${t.eP} out ${t.xP} ${t.why} ${Math.round(t.pnl)}`)); }); console.log(T.join('\n'));
