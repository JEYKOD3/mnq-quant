const E=require('../engine/js/engine.js'), fs=require('fs'), {report,line,score}=require('../engine/js/report.js');
const all=E.parseBars(fs.readFileSync('../data/raw/mnq_rth_5m.txt','utf8')); const MK={pv:2,tick:0.25};
const yrs=[['2022',20220101,20221231],['2023',20230101,20231231],['2024',20240101,20241231],['2025',20250101,20251231],['2026',20260101,20261020]];
const rows=[];
for (const pokeMin of [0,2,5]) for (const pokeMax of [20,30,45]) for (const within of [2,3,5]) for (const stopMode of ['poke','bar']) for (const tgtR of [0.75,1,1.25]) for (const bufPts of [2,5]) for (const sessStart of [945,1000,1030]) for (const lastEntry of [1300,1500]) {
  const P={pokeMin,pokeMax,within,stopMode,tgtR,bufPts,sessStart,lastEntry,useSw:false,useOR:false,maxStop:60};
  const dt=E.simFB(all,P,MK); const R=yrs.map(([l,a,z])=>report(dt,a,z));
  const pos=R.filter(x=>x.net>0).length; const g=R.reduce((s,x)=>s+x.g,0), r=R.reduce((s,x)=>s+x.r,0);
  rows.push({P,pos,net:R.reduce((s,x)=>s+x.net,0),net26:R[4].net,g26:R[4].g,r26:R[4].r,gr:g/(g+r),R}); }
rows.sort((a,b)=>(b.pos*10000+b.net)-(a.pos*10000+a.net));
console.log('variants',rows.length,'| profitable in all 5 years:',rows.filter(x=>x.pos===5).length,'| 4 of 5:',rows.filter(x=>x.pos===4).length);
for (const x of rows.slice(0,8)) { console.log(JSON.stringify(x.P),'| years+',x.pos,'| 5y net',x.net,'| green days all years',(100*x.gr).toFixed(0)+'%'); console.log('    '+x.R.map((y,i)=>yrs[i][0]+': '+y.net+' ('+y.g+'/'+y.r+' PF '+y.pf+')').join(' | ')); }
fs.writeFileSync('fb2.json',JSON.stringify(rows.map(x=>({P:x.P,pos:x.pos,net:x.net,net26:x.net26,gr:x.gr}))));
