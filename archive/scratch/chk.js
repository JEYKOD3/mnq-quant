const E=require('/home/claude/mnqscalp/lab/engine.js'), fs=require('fs');
const days=E.parseBars(fs.readFileSync('/home/claude/mnqscalp/lab/mnq_rth.txt','utf8'));
// independent: first break of OR high (9:45-11:30); does price hit entry-S first or entry+2S first (stop-first on same bar)?
for (const S of [10,20,30,60]) { let up=0,dn=0,none=0,ws=[];
 for (const {d,b} of days){ if(b.length<20||b[0][0]!==930) continue; let hi=-1e9,lo=1e9; for(let i=0;i<3;i++){hi=Math.max(hi,b[i][2]);lo=Math.min(lo,b[i][3]);} ws.push(hi-lo);
  for(let i=3;i<b.length;i++){ if(b[i][0]>1130) break; if(b[i][2]>=hi+0.25){ const e=hi+0.25; let r=0;
    for(let j=i;j<b.length;j++){ if(b[j][3]<=e-S){r=-1;break;} if(j>i && b[j][2]>=e+2*S){r=1;break;} }
    if(r>0)up++; else if(r<0)dn++; else none++; break; } } }
 ws.sort((a,b)=>a-b); console.log('stop',S,'pts: target first',up,'stop first',dn,'neither',none,'| win%',(100*up/(up+dn)).toFixed(0),'| median OR width',ws[ws.length>>1]);}
