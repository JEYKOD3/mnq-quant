function simORB(days, P, mk){
  const out=new Map(), T=mk.tick, PV=mk.pv, C=P.comm, S=P.slip;
  for (const {d,b} of days){
    const n=P.orMin/5; if (b.length<20 || b[0][0]!==930) { out.set(d,[]); continue; }
    let hi=-Infinity, lo=Infinity; for(let i=0;i<n;i++){ hi=Math.max(hi,b[i][2]); lo=Math.min(lo,b[i][3]); }
    const res=[]; const used=new Set(); let pos=null;
    for (let i=n;i<b.length;i++){
      const [tm,o,h,l,c]=b[i];
      if (pos){
        const {side,ent,stp,tgt,q}=pos; let ex=null;
        if (side>0 ? l<=stp : h>=stp) ex=stp-side*S*T;
        else if (tgt!==null && (side>0 ? h>=tgt : l<=tgt)) ex=tgt;
        else if (tm>=1555) ex=c;
        if (ex!==null){ res.push((ex-ent)*side*q*PV-C*q*2); pos=null; if(!P.both) break; }
        continue;
      }
      if (tm>P.lastEntry || tm>=1555) continue;
      for (const [side,lvl] of [[1,hi+T],[-1,lo-T]]){
        if (used.has(side)) continue;
        if ((side>0 && h>=lvl) || (side<0 && l<=lvl)){
          const ent=lvl+side*S*T;
          const stp = P.stopMode==='opp' ? (side>0? lo-T : hi+T) : Math.round(((hi+lo)/2)/T)*T;
          const r=Math.abs(ent-stp); const q=Math.floor(Math.min(P.maxQty, P.risk/(r*PV+2*C)));
          used.add(side); if (q<1) continue;
          if ((side>0 && l<=stp) || (side<0 && h>=stp)){ res.push((stp-side*S*T-ent)*side*q*PV-C*q*2); continue; }
          pos={side,ent,stp,tgt:P.tgtR>0? ent+side*P.tgtR*r : null,q}; break;
        }
      }
      if (!P.both && res.length) break;
    }
    out.set(d,res);
  }
  return out;
}
function evals(dayList, dt, F){
  const out=[]; const N=F.evDays;
  for (let k=0;k+N<=dayList.length;k++){
    let eq=0, peak=0, thr=-F.mll, best=0, res=0, used=0;
    for (let j=0;j<N;j++){
      const tl=dt.get(dayList[k+j])||[]; let dp=0;
      for (const p of tl){
        if (F.dll && dp<=-F.dll) break;
        if (F.cap && dp>=F.cap) break;
        eq+=p; dp+=p;
        if (eq<=thr){ res=-1; break; }
        if (eq>=F.target && (!F.consist || Math.max(best,dp) <= F.consist/100*eq)){ res=1; break; }
      }
      used=j+1; if (res) break;
      best=Math.max(best,dp); peak=Math.max(peak,eq); thr=Math.min(peak-F.mll,100);
    }
    out.push({start:dayList[k],res,days:used,eq});
  }
  return out;
}

const zlib=require('zlib'),fs=require('fs');
const t=zlib.gunzipSync(fs.readFileSync('mnq_rth.txt.gz')).toString();
const days=[];for(const line of t.split('\n')){if(!line)continue;const p=line.split('|');const b=[];for(let i=1;i<p.length;i++){const a=p[i].split(',');b.push([+a[0],a[1]/4,a[2]/4,a[3]/4,a[4]/4]);}days.push({d:+p[0],b});}
const dt=simORB(days,{orMin:15,stopMode:'opp',tgtR:2,risk:300,lastEntry:1130,slip:1,both:true,comm:2.37,maxQty:20},{pv:2,tick:0.25});
let net=0,n=0;dt.forEach(l=>l.forEach(p=>{net+=p;n++}));
const ev=evals(days.map(x=>x.d),dt,{target:1250,mll:1000,dll:0,cap:600,consist:50,evDays:20});
const P=ev.filter(e=>e.res===1).length/ev.length,F=ev.filter(e=>e.res===-1).length/ev.length;
console.log('trades',n,'net',Math.round(net),'pass',(P*100).toFixed(1),'fail',(F*100).toFixed(1),'evals',ev.length);
const ev2=evals(days.map(x=>x.d),dt,{target:1250,mll:1000,dll:600,cap:600,consist:50,evDays:20});
console.log('with DLL 600: pass',(ev2.filter(e=>e.res===1).length/ev2.length*100).toFixed(1),'fail',(ev2.filter(e=>e.res===-1).length/ev2.length*100).toFixed(1));
