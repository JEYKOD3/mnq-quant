const E=require('/home/claude/mnqscalp/lab/engine.js'), fs=require('fs');
const all=E.parseBars(fs.readFileSync('/home/claude/mnqscalp/lab/mnq_rth.txt','utf8'));
const feat={}; const dr=[]; for(let k=0;k<all.length;k++){ const {d,b}=all[k]; if(b.length<20||b[0][0]!==930) continue; const pb=k>0?all[k-1].b:null; if(!pb) continue;
  const pdh=Math.max(...pb.map(x=>x[2])), pdl=Math.min(...pb.map(x=>x[3])), pdc=pb[pb.length-1][4]; const adr=dr.length>=10?dr.slice(-10).reduce((a,b)=>a+b)/10:pdh-pdl; dr.push(pdh-pdl);
  let hi=-1e9,lo=1e9; for(let i=0;i<3;i++){hi=Math.max(hi,b[i][2]);lo=Math.min(lo,b[i][3]);} const open=b[0][1];
  const gap=(open-pdc)/adr, orDir=(b[2][4]-open)/(hi-lo||1), pdRel=(pdh-pdl)/adr;
  feat[d]={gap:+gap.toFixed(2),orDir:+orDir.toFixed(2),pdRel:+pdRel.toFixed(2),committed:((Math.abs(gap)>0.6||Math.abs(orDir)>0.6)&&pdRel<=1.2)?1:0,bias:gap>0.6?1:gap<-0.6?-1:orDir>0.6?1:orDir<-0.6?-1:0}; }
fs.writeFileSync('dayfeat.json',JSON.stringify(feat)); console.log(Object.keys(feat).length,'days; committed 2026:',Object.entries(feat).filter(([d,f])=>+d>=20260101&&f.committed).length,'of',Object.keys(feat).filter(d=>+d>=20260101).length);
