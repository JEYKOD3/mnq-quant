const E=require('../engine/js/engine.js'), fs=require('fs'), {report,line}=require('../engine/js/report.js');
const all=E.parseBars(fs.readFileSync('../data/raw/mnq_rth_5m.txt','utf8')); const MK={pv:2,tick:0.25};
const orb=E.simORB(all,{orMin:15,stopMode:'opp',tgtR:2,risk:300,lastEntry:1130,slip:1,both:true,comm:2.37,maxQty:20},MK);
// day features known at 9:45
const feat={}; const dr=[]; for(let k=0;k<all.length;k++){ const {d,b}=all[k]; if(b.length<20||b[0][0]!==930) continue; const pb=k>0?all[k-1].b:null; if(!pb) continue;
  const pdh=Math.max(...pb.map(x=>x[2])), pdl=Math.min(...pb.map(x=>x[3])), pdc=pb[pb.length-1][4], pdo=pb[0][1]; const adr=dr.length>=10?dr.slice(-10).reduce((a,b)=>a+b)/10:pdh-pdl; dr.push(pdh-pdl);
  let hi=-1e9,lo=1e9; for(let i=0;i<3;i++){hi=Math.max(hi,b[i][2]);lo=Math.min(lo,b[i][3]);} const open=b[0][1]; const gap=(open-pdc)/adr; const orW=(hi-lo)/adr;
  const orPos = hi>pdh? 'above PD range' : lo<pdl? 'below PD range' : 'inside PD range'; const pdDir = pdc>pdo?'prior day up':'prior day down'; const pdRangeRel=(pdh-pdl)/adr;
  const dow=new Date(Math.floor(d/10000),Math.floor(d/100)%100-1,d%100).getDay();
  const dayMoveAtOR = Math.abs(b[2][4]-open)/adr;   // how directional the first 15 min were
  feat[d]={gap,orW,orPos,pdDir,pdRangeRel,dow,orDir:(b[2][4]-open)/(hi-lo||1)}; }
const split=(nm,f)=>{ const yes=new Map(), no=new Map(); orb.forEach((l,d)=>{ if(!feat[d]) return; (f(feat[d])?yes:no).set(d,l); });
  console.log(nm); for (const [lab,m] of [['  YES',yes],['  NO ',no]]) { const R5=report(m,20220101,20251231), R6=report(m,20260101,20261020); console.log(lab,'2022-25:',line(R5)); console.log('     2026   :',line(R6)); } };
split('gap > 0.3 ADR (either way)',f=>Math.abs(f.gap)>0.3);
split('gap > 0.6 ADR',f=>Math.abs(f.gap)>0.6);
split('OR width < 0.25 ADR (narrow)',f=>f.orW<0.25);
split('OR width > 0.4 ADR (wide)',f=>f.orW>0.4);
split('OR outside prior day range',f=>f.orPos!=='inside PD range');
split('prior day range > 1.2 ADR (big day before)',f=>f.pdRangeRel>1.2);
split('first 15 min directional (|close-open| > 60% of OR)',f=>Math.abs(f.orDir)>0.6);
split('Mon/Fri',f=>f.dow===1||f.dow===5);
console.log('\n==== COMBOS');
split('A: gap>0.6 OR directional first 15m',f=>Math.abs(f.gap)>0.6||Math.abs(f.orDir)>0.6);
split('B: A and prior day range <= 1.2 ADR',f=>(Math.abs(f.gap)>0.6||Math.abs(f.orDir)>0.6)&&f.pdRangeRel<=1.2);
split('C: B and not Mon/Fri',f=>(Math.abs(f.gap)>0.6||Math.abs(f.orDir)>0.6)&&f.pdRangeRel<=1.2&&f.dow!==1&&f.dow!==5);
split('D: gap>0.6 AND directional',f=>Math.abs(f.gap)>0.6&&Math.abs(f.orDir)>0.6);
split('E: directional and prior day <= 1.2 ADR',f=>Math.abs(f.orDir)>0.6&&f.pdRangeRel<=1.2);
