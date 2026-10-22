const E=require('/home/claude/mnqscalp/lab/engine.js'), fs=require('fs');
for (const [f,lab] of [['mnq_rth.txt','5m'],['mnq_rth_1m.txt','1m']]) {
 const days=E.parseBars(fs.readFileSync('/home/claude/mnqscalp/lab/'+f,'utf8'));
 const M={}; for (const {d,b} of days){ const k=Math.floor(d/100); if(k<202410) continue; M[k]=M[k]||{s:0,n:0,dr:0,dn:0,px:0}; for(const x of b){ if(x[0]<1000) continue; M[k].s+=x[2]-x[3]; M[k].n++; } M[k].dr+=Math.max(...b.map(x=>x[2]))-Math.min(...b.map(x=>x[3])); M[k].dn++; M[k].px=b[0][1]; }
 console.log(lab+' avg candle range (pts, after 10:00) | avg daily range | price');
 console.log(Object.entries(M).map(([k,v])=>`${k}: ${(v.s/v.n).toFixed(1)} | ${(v.dr/v.dn).toFixed(0)} | ${Math.round(v.px)}`).join('\n'));
}
