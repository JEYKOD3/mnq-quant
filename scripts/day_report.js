// Journal step: node scripts/day_report.js YYYYMMDD  (from scripts/). Runs both playbooks on the base data + live file for that day,
// writes journal/daily/YYYYMMDD.md and appends journal/trades.csv.
const E=require('../engine/js/engine.js'), fs=require('fs'), path=require('path');
const base=fs.readFileSync('../data/raw/mnq_rth_5m.txt','utf8'); const livep='../data/live/mnq_rth_5m_live.txt'; const live=fs.existsSync(livep)?fs.readFileSync(livep,'utf8'):'';
const seen=new Set(); const lines=[]; for (const l of (base+'\n'+live).split('\n')) { if(!l.trim()) continue; const d=l.slice(0,8); if(live.includes(l)) { lines.push(l); seen.add(d);} }
for (const l of base.split('\n')) { if(l.trim() && !seen.has(l.slice(0,8))) lines.push(l); }
lines.sort(); const all=E.parseBars(lines.join('\n')); const MK={pv:2,tick:0.25};
const d=+process.argv[2]||all[all.length-1].d; const k=all.findIndex(x=>x.d===d); if(k<11){console.log('no data for',d);process.exit(1);}
const b=all[k].b, pb=all[k-1].b; const dr=[]; for(let m=k-10;m<k;m++){const bb=all[m].b; dr.push(Math.max(...bb.map(x=>x[2]))-Math.min(...bb.map(x=>x[3])));} const adr=dr.reduce((a,b)=>a+b)/10;
const pdh=Math.max(...pb.map(x=>x[2])), pdl=Math.min(...pb.map(x=>x[3])), pdc=pb[pb.length-1][4]; let hi=-1e9,lo=1e9; for(let i=0;i<3;i++){hi=Math.max(hi,b[i][2]);lo=Math.min(lo,b[i][3]);} const open=b[0][1];
const gap=(open-pdc)/adr, dir=(b[2][4]-open)/(hi-lo||1), pdRel=(pdh-pdl)/adr; const gapOK=Math.abs(gap)>=0.6, dirOK=Math.abs(dir)>=0.6, pdOK=pdRel<=1.2; const committed=(gapOK||dirOK)&&pdOK; const bias=gapOK?(gap>0?1:-1):dirOK?(dir>0?1:-1):0;
const hm=t=>String(Math.floor(t/100)).padStart(2,'0')+':'+String(t%100).padStart(2,'0'); const rows=[];
const days=all.slice(Math.max(0,k-15),k+1);
if (committed) { const rt=E.simRT2(days,{risk:400,stop:'opp',tgtR:2},MK); (rt.get(d)||[]).forEach(t=>{ if(t.side===bias) rows.push(['ORB Retest V4 Adaptive','committed',t.side>0?'long':'short',hm(b[t.eI][0]),t.eP,t.stp,t.tgt,hm(b[t.xI][0]),t.xP,t.q,Math.round(t.pnl),t.why]); }); }
else if (pdOK) { const fb=E.simFB(days,{pokeMin:2,pokeMax:45,within:5,stopMode:'poke',tgtR:1,bufPts:5,sessStart:1000,lastEntry:1300,useSw:false,useOR:false,maxStop:60},MK); (fb.get(d)||[]).forEach(t=>rows.push(['Failed Break V1','quiet',t.side>0?'long':'short',hm(b[t.eI][0]),t.eP,t.stp,t.tgt,hm(b[t.xI][0]),t.xP,t.q,Math.round(t.pnl),t.why])); }
const dayType = committed?`committed ${bias>0?'LONG':'SHORT'}` : !pdOK?'after a huge day (no trade)':'quiet open';
const pnl=rows.reduce((s,r)=>s+r[10],0); const last=b[b.length-1];
let md=`# ${d}\n\n9:45 read: ADR ${Math.round(adr)} | prior day ${pdl}-${pdh} close ${pdc} (${pdRel.toFixed(2)} ADR) | open ${open} gap ${gap.toFixed(2)} ADR | OR ${lo}-${hi} first15 ${dir.toFixed(2)} | **${dayType}**\n\n`;
md+=`Bars through ${hm(last[0])}, close ${last[4]}. Day P&L (system): **${pnl>=0?'+':''}${pnl}$** on ${rows.length} trade(s), ${pnl>0?'GREEN':rows.length?'RED':'FLAT'}.\n\n`;
if(rows.length){ md+='| Playbook | Side | Entry | Price | Stop | Target | Exit | Price | Qty | P&L | Reason |\n|---|---|---|---|---|---|---|---|---|---|---|\n'; rows.forEach(r=>md+=`| ${r[0]} | ${r[2]} | ${r[3]} | ${r[4]} | ${r[5]} | ${r[6]??'-'} | ${r[7]} | ${r[8]} | ${r[9]} | ${r[10]} | ${r[11]} |\n`); }
fs.mkdirSync('../journal/daily',{recursive:true}); fs.writeFileSync(`../journal/daily/${d}.md`,md);
const csv='../journal/trades.csv'; if(!fs.existsSync(csv)) fs.writeFileSync(csv,'day,playbook,day_type,side,entry_time,entry,stop,target,exit_time,exit,qty,pnl,reason,source\n');
const old=fs.readFileSync(csv,'utf8').split('\n').filter(l=>l&&!l.startsWith(d+',')); rows.forEach(r=>old.push([d,...r,'backtest-engine'].join(','))); fs.writeFileSync(csv,old.join('\n')+'\n');
console.log(md);
