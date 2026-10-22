const E=require('/home/claude/mnqscalp/lab/engine.js'), fs=require('fs');
const days=E.parseBars(fs.readFileSync('/home/claude/mnqscalp/lab/mnq_rth.txt','utf8'));
const TK=0.25,PV=2,CM=2.37;
// Mai retest rules, manual execution: signal bar -> stop order next bar only; manage stop/target; day limits -550/+600, max 6
let N=0,NET=0,W=0; const M={};
for (const {d,b} of days){ if(b.length<20||b[0][0]!==930) continue;
 let hi=-1e9,lo=1e9; for(let i=0;i<3;i++){hi=Math.max(hi,b[i][2]);lo=Math.min(lo,b[i][3]);}
 let pos=null,pend=null,tr=0,dp=0,ku=0,kd=0,tu=false,td=false;
 for(let i=3;i<b.length;i++){const [tm,o,h,l,c]=b[i];
  if(pend&&!pos){ if(pend.s>0?h>=pend.e:l<=pend.e){ const eP=pend.e+pend.s*TK; pos={...pend,eP}; if(pend.s>0?l<=pos.stp:h>=pos.stp){const p=(pos.stp-pos.s*TK-eP)*pos.s*pos.q*PV-2*CM*pos.q;NET+=p;dp+=p;N++;tr++;M[Math.floor(d/100)]=(M[Math.floor(d/100)]||0)+p;pos=null;} } pend=null; }
  else if(pos){ let x=null; if(pos.s>0?l<=pos.stp:h>=pos.stp) x=pos.stp-pos.s*TK; else if(pos.s>0?h>=pos.tp:l<=pos.tp) x=pos.tp; else if(tm>=1555) x=c;
    if(x!==null){const p=(x-pos.eP)*pos.s*pos.q*PV-2*CM*pos.q;NET+=p;dp+=p;N++;if(p>0)W++;tr++;M[Math.floor(d/100)]=(M[Math.floor(d/100)]||0)+p;pos=null;} }
  // run state (Mai: BARSLAST/COUNT)
  if(c>hi){ tu = (ku>0?tu:false) || l<=hi; ku++; } else {ku=0;tu=false;}
  if(c<lo){ td = (kd>0?td:false) || h>=lo; kd++; } else {kd=0;td=false;}
  if(pos||tm>1255||tr>=6||dp<=-550||dp>=600) continue;
  const r=h-l, bull=r>0&&c>o&&(c-l)>=.5*r&&Math.abs(c-o)>=.3*r, bear=r>0&&c<o&&(h-c)>=.5*r&&Math.abs(c-o)>=.3*r;
  if(tu&&bull){const e=h+TK,R=Math.max(e+TK-(lo-TK),4),q=Math.min(20,Math.floor(400/(R*2+4.74))); if(q>=1) pend={s:1,e,stp:e+TK-R,tp:e+TK+2*R,q};}
  if(td&&bear){const e=l-TK,R=Math.max(hi+TK-(e-TK),4),q=Math.min(20,Math.floor(400/(R*2+4.74))); if(q>=1) pend={s:-1,e,stp:e-TK+R,tp:e-TK-2*R,q};}
 }}
const v=Object.values(M); console.log('Mai retest replay:',N,'trades net',Math.round(NET),'win',(100*W/N).toFixed(0)+'%','months pos',v.filter(x=>x>0).length+'/'+v.length);
