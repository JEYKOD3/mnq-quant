const E=require('../engine/js/engine.js'), fs=require('fs'), {report,line}=require('../engine/js/report.js');
const all=E.parseBars(fs.readFileSync('../data/raw/mnq_rth_5m.txt','utf8')); const MK={pv:2,tick:0.25};
const feat={}; const dr=[]; for(let k=0;k<all.length;k++){ const {d,b}=all[k]; if(b.length<20||b[0][0]!==930) continue; const pb=k>0?all[k-1].b:null; if(!pb) continue;
  const pdh=Math.max(...pb.map(x=>x[2])), pdl=Math.min(...pb.map(x=>x[3])), pdc=pb[pb.length-1][4]; const adr=dr.length>=10?dr.slice(-10).reduce((a,b)=>a+b)/10:pdh-pdl; dr.push(pdh-pdl);
  let hi=-1e9,lo=1e9; for(let i=0;i<3;i++){hi=Math.max(hi,b[i][2]);lo=Math.min(lo,b[i][3]);} const open=b[0][1];
  feat[d]={gap:(open-pdc)/adr,pdRangeRel:(pdh-pdl)/adr,orDir:(b[2][4]-open)/(hi-lo||1),dow:new Date(Math.floor(d/10000),Math.floor(d/100)%100-1,d%100).getDay()}; }
const committed=f=>(Math.abs(f.gap)>0.6||Math.abs(f.orDir)>0.6)&&f.pdRangeRel<=1.2;
const rt2=E.simRT2(all,{risk:400,stop:'opp',tgtR:2},MK);
const fb=E.simFB(all,{pokeMin:2,pokeMax:45,within:5,stopMode:'poke',tgtR:1,bufPts:5,sessStart:1000,lastEntry:1300,useSw:false,useOR:false,maxStop:60},MK);
const fbA=E.simFB(all,{pokeMax:30,within:3,stopMode:'poke',tgtR:1,useSw:false,useOR:false,maxStop:60,sessStart:945},MK);
const show=(nm,m)=>{ console.log(nm); for(const [l,a,z] of [['2022-25',20220101,20251231],['2026   ',20260101,20261020],['last 6m',20260421,20261020]]) console.log('  ',l,line(report(m,a,z))); };
const sel=(dt,f)=>{ const m=new Map(); dt.forEach((l,d)=>{ if(feat[d]&&f(feat[d])) m.set(d,l); }); return m; };
show('Retest V2 on committed days only',sel(rt2,committed));
show('Retest V2 on NOT committed days',sel(rt2,f=>!committed(f)));
show('Failed-break (robust) on NOT committed days',sel(fb,f=>!committed(f)));
show('Failed-break (robust) on committed days',sel(fb,committed));
show('Failed-break (2026-tuned) on NOT committed days',sel(fbA,f=>!committed(f)));
