const E=require('/home/claude/mnqscalp/lab/engine.js'), fs=require('fs');
const all=E.parseBars(fs.readFileSync('/home/claude/mnqscalp/lab/mnq_rth.txt','utf8')); const MK={pv:2,tick:0.25}; const feat=JSON.parse(fs.readFileSync('dayfeat.json'));
const rt=E.simRT2(all,{risk:400,stop:'opp',tgtR:2},MK); const em=E.emaArr(all,21); const byD=new Map(all.map((x,i)=>[x.d,i]));
const T=[]; rt.forEach((l,d)=>{ if(!feat[d]||!feat[d].committed) return; const b=all[byD.get(d)].b, e=em.get(d); l.forEach((t,idx)=>{ if(feat[d].bias!==t.side) return; const j=t.eI;
  let hi=-1e9,lo=1e9; for(let i=0;i<3;i++){hi=Math.max(hi,b[i][2]);lo=Math.min(lo,b[i][3]);}
  T.push({d,pnl:t.pnl,tm:b[j][0],side:t.side,nth:idx+1,ext:E.stretch(e,b,j,t.side),orW:(hi-lo),r:t.r,gap:Math.abs(feat[d].gap),dir:Math.abs(feat[d].orDir),why:t.why,hold:t.hold}); }); });
const grp=(nm,f)=>{ for(const [l,a,z] of [['2022-25',20220101,20251231],['2026',20260101,20261020]]){ const S=T.filter(t=>t.d>=a&&t.d<=z&&f(t)); const n=S.length,w=S.filter(t=>t.pnl>0).length,net=S.reduce((s,t)=>s+t.pnl,0); process.stdout.write(`${l}: ${n} tr win ${n?Math.round(100*w/n):0}% net ${Math.round(net)} ($${n?Math.round(net/n):0}/tr)   `);} console.log(' <-',nm); };
grp('entry 9:45-10:00',t=>t.tm<1000); grp('entry 10:00-11:00',t=>t.tm>=1000&&t.tm<1100); grp('entry 11:00-13:00',t=>t.tm>=1100);
grp('1st trade of day',t=>t.nth===1); grp('2nd+ trade of day',t=>t.nth>1);
grp('stretch <= 2 candles',t=>t.ext<=2); grp('stretch > 2',t=>t.ext>2);
grp('OR width < 60 pts',t=>t.orW<60); grp('OR width 60-120',t=>t.orW>=60&&t.orW<120); grp('OR width >= 120',t=>t.orW>=120);
grp('gap-based day',t=>t.gap>0.6); grp('direction-based day (no gap)',t=>t.gap<=0.6);
grp('long',t=>t.side>0); grp('short',t=>t.side<0);
