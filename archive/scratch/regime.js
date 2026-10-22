const E=require('/home/claude/mnqscalp/lab/engine.js'), fs=require('fs');
const days=E.parseBars(fs.readFileSync('/home/claude/mnqscalp/lab/mnq_rth.txt','utf8'));
function reg(a,z){ const D=days.filter(x=>x.d>=a&&x.d<=z&&x.b.length>70); let trend=0,chop=0,orFollow=0,orFake=0,rng=0,move=0,up=0,rev=0;
 for(const {b} of D){ const H=Math.max(...b.map(x=>x[2])),L=Math.min(...b.map(x=>x[3])),O=b[0][1],C=b[b.length-1][4]; const pos=(C-L)/(H-L); rng+=H-L; move+=Math.abs(C-O); if(C>O)up++;
  if(pos>0.75||pos<0.25) trend++; else chop++;
  let hi=-1e9,lo=1e9; for(let i=0;i<3;i++){hi=Math.max(hi,b[i][2]);lo=Math.min(lo,b[i][3]);} const w=hi-lo;
  // first break after 9:45: did it reach 1x OR width beyond before coming back to the other side?
  for(let i=3;i<b.length;i++){ const s=b[i][2]>hi?1:b[i][3]<lo?-1:0; if(!s) continue; let res=0; for(let j=i;j<b.length;j++){ if(s>0?b[j][3]<lo:b[j][2]>hi){res=-1;break;} if(s>0?b[j][2]>=hi+w:b[j][3]<=lo-w){res=1;break;} } if(res>0)orFollow++; else orFake++; break; }
  // reversal day: morning trend (open->12:00) opposite to afternoon (12:00->close)
  const mid=b.find(x=>x[0]>=1200); if(mid && (mid[4]-O)*(C-mid[4])<0 && Math.abs(C-mid[4])>0.3*(H-L)) rev++; }
 const n=D.length; return `${n} days | up days ${up} | avg range ${Math.round(rng/n)} pt | open->close ${Math.round(move/n)} pt (${Math.round(100*move/rng)}% of range) | trend days ${trend} / chop ${chop} | ORB follow-through ${orFollow} vs fail ${orFake} | afternoon reversals ${rev}`; }
for (const [l,a,z] of [['Oct 2026',20261001,20261031],['Oct 2025',20251001,20251031],['Oct 2024',20241001,20241031],['Sep 2026',20260901,20260930],['Sep 2025',20250901,20250930],['Aug 2026',20260801,20260831],['Aug 2025',20250801,20250831]]) console.log(l.padEnd(9),reg(a,z));
