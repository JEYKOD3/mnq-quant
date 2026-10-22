const E=require('/home/claude/mnqscalp/lab/engine.js'), fs=require('fs');
const days=E.parseBars(fs.readFileSync('/home/claude/mnqscalp/lab/mnq_rth.txt','utf8'));
const T=0.25,PV=2,C=2.37;
function sim(P){ const out=new Map();
 for(const {d,b} of days){ const res=[]; out.set(d,res); if(b.length<70||b[0][0]!==930) continue;
  let hi=-1e9,lo=1e9; for(let i=0;i<3;i++){hi=Math.max(hi,b[i][2]);lo=Math.min(lo,b[i][3]);}
  let brk=0, bi=-1, ext=null, done=false;
  for(let i=3;i<b.length && !done;i++){ const [tm,o,h,l,c]=b[i]; if(tm>P.last) break;
   if(!brk){ if(h>hi){brk=1;bi=i;ext=h;} else if(l<lo){brk=-1;bi=i;ext=l;} if(!brk) continue; }
   ext = brk>0?Math.max(ext,h):Math.min(ext,l);
   if(i-bi>P.win){ done=true; break; }
   // failed: candle closes back inside the range
   if(brk>0? c<hi : c>lo){ const side=-brk; if(i+1>=b.length) break; const eP=b[i+1][1]-side*0*T + side*T; // next open + slippage
     const stp= side<0 ? ext+P.buf : ext-P.buf; const r=Math.abs(eP-stp); if(r<4||r>P.maxStop){done=true;break;}
     let tgt = side<0 ? lo+T : hi-T; if(P.tgt==='mid') tgt=(hi+lo)/2; if((tgt-eP)*side < P.minRoomR*r){done=true;break;}
     const q=Math.min(20,Math.floor(P.risk/(r*PV+2*C))); if(q<1){done=true;break;}
     let x=null,why=''; for(let j=i+1;j<b.length;j++){ const [t2,o2,h2,l2,c2]=b[j]; if(side<0?h2>=stp:l2<=stp){x=stp+(side<0?T:-T);why='stop';break;} if(side<0?l2<=tgt:h2>=tgt){x=tgt;why='target';break;} if(P.hold && (j-i)*5>=P.hold){x=c2;why='time';break;} if(t2>=1555){x=c2;why='close';break;} }
     if(x===null){x=b[b.length-1][4];why='close';}
     res.push({side,pnl:(x-eP)*side*q*PV-2*C*q,why,q,tm:b[i+1][0]}); done=true; }
  } }
 return out; }
const st=(dt,a,z)=>{let N=0,NET=0,W=0,GW=0,GL=0;dt.forEach((l,d)=>{if(d<a||d>z)return;l.forEach(t=>{N++;NET+=t.pnl;if(t.pnl>0){W++;GW+=t.pnl}else GL-=t.pnl})});return {N,NET,win:N?W/N:0,pf:GL?GW/GL:9};};
const f=s=>`${String(s.N).padStart(3)} tr ${String(Math.round(s.NET)).padStart(6)}$ PF ${s.pf.toFixed(2)} win ${(s.win*100).toFixed(0)}%`;
for (const P of [{win:6,buf:2,maxStop:80,tgt:'other',minRoomR:1,risk:300,last:1200,hold:0},{win:6,buf:2,maxStop:80,tgt:'mid',minRoomR:0.5,risk:300,last:1200,hold:0},{win:12,buf:2,maxStop:80,tgt:'other',minRoomR:1,risk:300,last:1200,hold:0},{win:6,buf:2,maxStop:60,tgt:'other',minRoomR:1.5,risk:300,last:1200,hold:0}]) {
 const dt=sim(P); console.log(JSON.stringify({window_bars:P.win,target:P.tgt,minRoomR:P.minRoomR,maxStop:P.maxStop}));
 const row=[]; for(let ym=202508; ym<=202610; ym=(ym%100===12?ym+89:ym+1)){ const s=st(dt,ym*100,ym*100+31); row.push(`${String(ym).slice(2)}:${s.NET>=0?'+':''}${Math.round(s.NET)}(${s.N})`); }
 console.log('   by month:',row.join(' '));
 console.log('   Oct 2026',f(st(dt,20261001,20261031)),'| Oct 2025',f(st(dt,20251001,20251031)),'| Aug-Oct 2026',f(st(dt,20260801,20261031)),'| Oct25-Oct26',f(st(dt,20251001,20261031)),'| 2021-Sep25',f(st(dt,20211001,20250930)));
}
