// daily/weekly/monthly report for Map(day->trades)
function report(dt, a, z){ const day=[]; dt.forEach((l,d)=>{ if(d<a||d>z||!l.length) return; day.push([d,l]); }); day.sort((x,y)=>x[0]-y[0]);
  let n=0,w=0,gp=0,gl=0; const dv=[]; const wk={}, mo={};
  for (const [d,l] of day){ let s=0; for(const t of l){ n++; s+=t.pnl; if(t.pnl>0){w++;gp+=t.pnl} else gl-=t.pnl; } dv.push(s);
    const ds=String(d); const dtm=new Date(+ds.slice(0,4),+ds.slice(4,6)-1,+ds.slice(6,8)); const th=new Date(dtm); th.setDate(th.getDate()+3-((th.getDay()+6)%7)); const wkk=th.getFullYear()+'-'+Math.ceil(((th-new Date(th.getFullYear(),0,1))/864e5+1)/7);
    wk[wkk]=(wk[wkk]||0)+s; const mk=ds.slice(0,6); mo[mk]=(mo[mk]||0)+s; }
  const g=dv.filter(v=>v>0).length, r=dv.length-g; let eq=0,pk=0,dd=0; for(const v of dv){eq+=v;pk=Math.max(pk,eq);dd=Math.max(dd,pk-eq);}
  const wv=Object.values(wk), mv=Object.values(mo);
  return {n,net:Math.round(dv.reduce((a,b)=>a+b,0)),win:n?Math.round(100*w/n):0,pf:gl?+(gp/gl).toFixed(2):99,avgW:Math.round(gp/Math.max(1,w)),avgL:Math.round(gl/Math.max(1,n-w)),g,r,wk:wv.filter(v=>v>0).length,wkn:wv.length,mo:mv.filter(v=>v>0).length,mon:mv.length,worstDay:dv.length?Math.round(Math.min(...dv)):0,dd:Math.round(dd),months:Object.fromEntries(Object.entries(mo).map(([k,v])=>[k,Math.round(v)]))};
}
const line=R=>`net ${String(R.net).padStart(6)} | ${String(R.n).padStart(3)} tr win ${R.win}% PF ${R.pf.toFixed(2)} avgW ${R.avgW} avgL ${R.avgL} | days G/R ${R.g}/${R.r} | weeks+ ${R.wk}/${R.wkn} | months+ ${R.mo}/${R.mon} | worst day ${R.worstDay} DD ${R.dd}`;
const score=R=> R.n<10? -9 : (R.g/Math.max(1,R.g+R.r))*2 + R.mo/Math.max(1,R.mon) + Math.min(R.pf,3)/3;
module.exports={report,line,score};
