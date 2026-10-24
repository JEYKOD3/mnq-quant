const E=require('/home/claude/mnq-quant/engine/js/engine.js'), fs=require('fs'), {report}=require('/home/claude/mnq-quant/engine/js/report.js');
const feat=JSON.parse(fs.readFileSync('/home/claude/mnq-quant/scripts/dayfeat.json')); const MK={pv:2,tick:0.25};
const v4=f=>{ if(!f||f.pdRel>1.2) return 0; const G=Math.abs(f.gap)>=.6, D=Math.abs(f.orDir)>=.6; if(!(G||D)) return 0; return G?Math.sign(f.gap):Math.sign(f.orDir);};
const sel=rt=>{const m=new Map(); rt.forEach((l,d)=>{const s=v4(feat[d]); if(!s) return; const k=l.filter(t=>t.side===s).slice(0,1); if(k.length) m.set(d,k);}); return m;};
const rows=[];
for (const tf of [1,2,3,5,10,15]) { const all=E.parseBars(fs.readFileSync(`/home/claude/mnq-quant/data/tf/rth_${tf}m.txt`,'utf8')); E.setBar(tf);
  for (const tg of [1,1.5,2,3]) for (const mh of [0,60,120,180]) { E.setMaxHold(mh);
    const m=sel(E.simRT2(all,{risk:1000,stop:'opp',tgtR:tg,maxQty:40},MK));
    const D=report(m,20220101,20241231), T=report(m,20250101,20261031);
    const yrs=[2022,2023,2024,2025,2026].map(y=>report(m,y*1e4+101,y*1e4+1231).pf);
    let hs=0,hn=0; m.forEach(l=>l.forEach(t=>{hs+=t.hold;hn++}));
    rows.push({tf,tg,mh,devPF:D.pf,devN:D.n,devDD:D.dd,testPF:T.pf,testN:T.n,testDD:T.dd,yrs,hold:Math.round(hs/hn),minY:Math.min(...yrs.slice(0,3))});
  } }
E.setMaxHold(0); E.setBar(5);
rows.sort((a,b)=>b.devPF-a.devPF);
console.log('ranked by DEV (2022-24) PF; TEST = 2025-26 (unseen). 1 trade/day, $1000 risk');
for (const r of rows) console.log(`${String(r.tf).padStart(2)}m tgt ${r.tg}R hold ${r.mh||'close'}`.padEnd(26), `DEV PF ${r.devPF.toFixed(2)} n${r.devN} DD${r.devDD} | TEST PF ${r.testPF.toFixed(2)} n${r.testN} DD${r.testDD} | yrs ${r.yrs.map(x=>x.toFixed(2)).join('/')} | hold ${r.hold}m`);
fs.writeFileSync('/tmp/claude-0/-home-claude/afdbc088-26a4-5e84-b77d-b387ee40e855/scratchpad/tfopt/grid.json',JSON.stringify(rows));
