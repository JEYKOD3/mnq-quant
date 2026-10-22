const E=require('/home/claude/mnqscalp/lab/engine.js'), fs=require('fs');
const all=E.parseBars(fs.readFileSync('/home/claude/mnqscalp/lab/mnq_rth.txt','utf8')); const MK={pv:2,tick:0.25}; const feat=JSON.parse(fs.readFileSync('dayfeat.json'));
const rt=E.simRT2(all,{risk:400,stop:'opp',tgtR:2},MK); const fb=E.simFB(all,{pokeMin:2,pokeMax:45,within:5,stopMode:'poke',tgtR:1,bufPts:5,sessStart:1000,lastEntry:1300,useSw:false,useOR:false,maxStop:60},MK);
const hm=t=>String(Math.floor(t/100)).padStart(2,'0')+':'+String(t%100).padStart(2,'0');
for (const {d,b} of all){ if(d<20260921||d>20261021) continue; const f=feat[d]; if(!f) continue;
  let hi=-1e9,lo=1e9; for(let i=0;i<3;i++){hi=Math.max(hi,b[i][2]);lo=Math.min(lo,b[i][3]);}
  // biggest move after 9:45: max run from any bar's close to a later extreme
  let best=0,bs='',bt=''; for(let i=3;i<b.length;i++){ let mx=-1e9,mn=1e9,imx=i,imn=i; for(let j=i;j<b.length;j++){ if(b[j][2]>mx){mx=b[j][2];imx=j;} if(b[j][3]<mn){mn=b[j][3];imn=j;} } const up=mx-b[i][4], dn=b[i][4]-mn; if(up>best){best=up;bs='up';bt=hm(b[i][0])+'-'+hm(b[imx][0]);} if(dn>best){best=dn;bs='down';bt=hm(b[i][0])+'-'+hm(b[imn][0]);} }
  const dayRange=Math.max(...b.map(x=>x[2]))-Math.min(...b.map(x=>x[3])); const oc=b[b.length-1][4]-b[0][1];
  const tr=[]; if(f.committed) (rt.get(d)||[]).forEach(t=>{ if(f.bias===t.side) tr.push(`V4 ${t.side>0?'LONG':'SHORT'} ${hm(b[t.eI][0])} @${t.eP} stop ${t.stp} tgt ${t.tgt?t.tgt:'-'} -> ${hm(b[t.xI][0])} @${t.xP} ${t.why} ${t.pnl>0?'+':''}${Math.round(t.pnl)}`); });
  (fb.get(d)||[]).forEach(t=>tr.push(`FB ${t.side>0?'LONG':'SHORT'} ${hm(b[t.eI][0])} @${t.eP} -> ${hm(b[t.xI][0])} @${t.xP} ${t.why} ${t.pnl>0?'+':''}${Math.round(t.pnl)}`));
  console.log(`${d} | OR ${lo}-${hi} (${hi-lo}pt) gap ${f.gap} first15 ${f.orDir} | ${f.committed?('COMMITTED '+(f.bias>0?'LONG':'SHORT')):'no trade (quiet open)'} | day range ${dayRange}pt open->close ${oc>0?'+':''}${oc} | biggest move after 9:45: ${Math.round(best)}pt ${bs} ${bt}`);
  tr.forEach(x=>console.log('    '+x)); }
