const E=require('../engine/js/engine.js'), fs=require('fs'); const all=E.parseBars(fs.readFileSync('../data/raw/mnq_rth_5m.txt','utf8')); const MK={pv:2,tick:0.25}; const feat=JSON.parse(fs.readFileSync('dayfeat.json'));
const rt=E.simRT2(all,{risk:400,stop:'opp',tgtR:2},MK);
const v4=f=>{ if(f.pdRel>1.2) return 0; const G=Math.abs(f.gap)>=.6, D=Math.abs(f.orDir)>=.6; if(!(G||D)) return 0; return G?Math.sign(f.gap):Math.sign(f.orDir);};
let tot=0;
for (const d of [20261013,20261014,20261015,20261016,20261019,20261020]) {
  const f=feat[d]; const b=v4(f); const l=(rt.get(d)||[]);
  console.log(`\n${d} gap ${f.gap.toFixed(2)}ADR  first15dir ${f.orDir.toFixed(2)}  pdRange ${f.pdRel.toFixed(2)}ADR -> ${b===0?'NO TRADE (open not committed)':'bias '+(b>0?'LONG':'SHORT')}`);
  if (l.length) console.log('   all retest setups the engine saw:', l.map(t=>JSON.stringify(t)).join('\n   '));
  if (b) { const tk=l.filter(t=>t.side===b); for (const t of tk) { tot+=t.pnl; } console.log('   V4 takes:', tk.length, 'pnl', tk.map(t=>Math.round(t.pnl)).join(', ')); }
}
console.log('\nweek total', Math.round(tot));
