const E=require('/home/claude/mnqscalp/lab/engine.js'), fs=require('fs'), {report,line}=require('./rep.js');
const all=E.parseBars(fs.readFileSync('/home/claude/mnqscalp/lab/mnq_rth.txt','utf8')); const MK={pv:2,tick:0.25};
// per-day flag: first OR break followed through (1) or failed (0)
const F=[]; for (const {d,b} of all){ let f=null; if(b.length>=70&&b[0][0]===930){ let hi=-1e9,lo=1e9; for(let i=0;i<3;i++){hi=Math.max(hi,b[i][2]);lo=Math.min(lo,b[i][3]);} const w=hi-lo;
  for(let i=3;i<b.length;i++){ const s=b[i][2]>hi?1:b[i][3]<lo?-1:0; if(!s) continue; let res=0; for(let j=i;j<b.length;j++){ if(s>0?b[j][3]<lo:b[j][2]>hi){res=-1;break;} if(s>0?b[j][2]>=hi+w:b[j][3]<=lo-w){res=1;break;} } f=res>0?1:0; break; } } F.push([d,f]); }
const regime=(k,N)=>{ let s=0,n=0; for(let j=k-1;j>=0&&n<N;j--){ if(F[j][1]===null) continue; s+=F[j][1]; n++; } return n? s/n : 0.5; };
const orb=E.simORB(all,{orMin:15,stopMode:'opp',tgtR:2,risk:300,lastEntry:1130,slip:1,both:true,comm:2.37,maxQty:20},MK);
const fb=E.simFB(all,{pokeMax:30,within:3,stopMode:'poke',tgtR:1,useSw:false,useOR:false,maxStop:60,sessStart:945},MK);
const fbB=E.simFB(all,{pokeMax:30,within:3,stopMode:'bar',tgtR:1.5,useSw:false,useOR:false,maxStop:60,sessStart:945},MK);
for (const N of [10,20,40]) for (const [hiT,loT] of [[0.5,0.4],[0.55,0.45],[0.5,0.5],[0.6,0.35]]) {
  const sw=new Map(), swB=new Map(), onlyOrb=new Map(), onlyFb=new Map();
  all.forEach(({d},k)=>{ const r=regime(k,N); sw.set(d, r>=hiT? (orb.get(d)||[]) : r<=loT? (fb.get(d)||[]) : []); swB.set(d, r>=hiT? (orb.get(d)||[]) : r<=loT? (fbB.get(d)||[]) : []); onlyOrb.set(d, r>=hiT?(orb.get(d)||[]):[]); onlyFb.set(d, r<=loT?(fb.get(d)||[]):[]); });
  console.log(`\nregime: last ${N} days, ORB if follow-through >= ${hiT}, failed-break if <= ${loT}`);
  for (const [nm,dt] of [['switch (ORB / FB-A)',sw],['switch (ORB / FB-B)',swB],['ORB only when trending',onlyOrb],['FB only when choppy',onlyFb]]) {
    console.log(' ',nm); for (const [l,a,z] of [['2022',20220101,20221231],['2023',20230101,20231231],['2024',20240101,20241231],['2025',20250101,20251231],['2026',20260101,20261020]]) console.log('    ',l,line(report(dt,a,z))); }
}
