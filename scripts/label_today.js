// Morning read for one day: node scripts/label_today.js YYYYMMDD  (uses data/raw/mnq_rth_5m.txt; for live use, append today's 9:30-9:45 bars first)
const E=require('../engine/js/engine.js'), fs=require('fs');
const all=E.parseBars(fs.readFileSync('../data/raw/mnq_rth_5m.txt','utf8')); const d=+process.argv[2]||all[all.length-1].d;
const k=all.findIndex(x=>x.d===d); if(k<1){console.log('no data for',d);process.exit(1);} const b=all[k].b, pb=all[k-1].b;
const dr=[]; for(let m=Math.max(0,k-10);m<k;m++){const bb=all[m].b; dr.push(Math.max(...bb.map(x=>x[2]))-Math.min(...bb.map(x=>x[3])));} const adr=dr.reduce((a,b)=>a+b)/dr.length;
const pdh=Math.max(...pb.map(x=>x[2])), pdl=Math.min(...pb.map(x=>x[3])), pdc=pb[pb.length-1][4];
let hi=-1e9,lo=1e9; for(let i=0;i<3;i++){hi=Math.max(hi,b[i][2]);lo=Math.min(lo,b[i][3]);} const open=b[0][1];
const gap=(open-pdc)/adr, dir=(b[2][4]-open)/(hi-lo||1), pdRel=(pdh-pdl)/adr;
const gapOK=Math.abs(gap)>=0.6, dirOK=Math.abs(dir)>=0.6, pdOK=pdRel<=1.2; const committed=(gapOK||dirOK)&&pdOK; const bias=gapOK?(gap>0?'LONG':'SHORT'):dirOK?(dir>0?'LONG':'SHORT'):'none';
console.log(`${d} | ADR ${Math.round(adr)} | prior day ${pdl}-${pdh} close ${pdc} (range ${(pdRel).toFixed(2)} ADR) | open ${open} gap ${gap.toFixed(2)} ADR | OR 9:30-9:45 ${lo}-${hi} first15 dir ${dir.toFixed(2)}`);
console.log(committed ? `COMMITTED OPEN -> Playbook A (ORB Retest V4), ${bias} only. Stop = ${bias==='LONG'?lo-0.25:hi+0.25}, target 2R, last entry 13:00.` : (!pdOK ? 'DAY AFTER A HUGE DAY -> no trade.' : `QUIET OPEN -> Playbook B only (failed break at ${pdh} / ${pdl}, 10:00-13:00, 1R).`));
