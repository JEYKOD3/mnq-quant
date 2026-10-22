const E=require('../engine/js/engine.js'), fs=require('fs'), {report,line}=require('../engine/js/report.js');
const all=E.parseBars(fs.readFileSync('../data/raw/mnq_rth_5m.txt','utf8')); const feat=JSON.parse(fs.readFileSync('dayfeat.json'));
const D=all.filter(x=>x.b.length>30).map(x=>({d:x.d,o:x.b[0][1],c:x.b[x.b.length-1][4]}));
// states from trailing 20-day return (close to close), Lewis Jackson's method
const N=20, TH=0.05; const st=D.map((x,i)=> i<N? null : (x.c/D[i-N].c-1>=TH?1 : x.c/D[i-N].c-1<=-TH?-1 : 0));
// walk-forward transition matrix: counts from all prior transitions (min 250 days of history)
const idx=s=>s+1; const sig=[]; const cnt=[[0,0,0],[0,0,0],[0,0,0]];
for (let i=N+1;i<D.length;i++){ const a=st[i-1], b=st[i]; // we know state at close of day i (uses closes up to i)
  // signal for day i+1 computed with counts up to transition (i-1 -> i)
  cnt[idx(a)][idx(b)]++;
  const row=cnt[idx(b)]; const tot=row[0]+row[1]+row[2]; sig[i]= (i>N+250 && tot>=20) ? (row[2]-row[0])/tot : null; }
// strategy A: next-day close-to-close in signal direction (|sig|>thr), 1 micro ($2/pt), $4.74 commissions
function dayPnl(thr,mode){ const m=new Map(); for(let i=N+252;i<D.length-1;i++){ const s=sig[i]; if(s===null) continue; let side=0;
  if(mode==='markov') side= s>thr?1 : s<-thr?-1 : 0; else side= st[i]===1?1 : st[i]===-1?-1 : 0;   // mode 'momentum' = trade the state itself
  if(!side) continue; const nx=D[i+1]; const pnl=(nx.c-nx.o)*side*2-4.74;   // open-to-close of next day (we can't trade the overnight close-to-close inside RTH)
  m.set(nx.d,[{pnl,side,hold:390,why:'close',q:1}]); } return m; }
const per=[['2022-25',20220101,20251231],['2026',20260101,20261020],['last 6m',20260421,20261020]];
for (const [nm,thr,mode] of [['Markov signal > 0.10',0.10,'markov'],['Markov signal > 0.25',0.25,'markov'],['Markov signal > 0.40',0.40,'markov'],['Momentum: trade the current state',0,'momentum']]) {
  const m=dayPnl(thr,mode); console.log(nm); for(const [l,a,z] of per) console.log('  ',l.padEnd(8),line(report(m,a,z))); }
// regime stats
const cnt2={}; st.forEach(s=>{ if(s!==null) cnt2[s]=(cnt2[s]||0)+1;}); console.log('state counts (bull/side/bear):',cnt2[1],cnt2[0],cnt2[-1]);
const M=cnt.map(r=>{const t=r[0]+r[1]+r[2]; return r.map(v=>(v/t).toFixed(2));}); console.log('final transition matrix rows bear/side/bull -> [bear,side,bull]:',JSON.stringify(M));
// next-day direction accuracy by state
for (const s of [1,0,-1]){ let up=0,n=0; for(let i=N;i<D.length-1;i++){ if(st[i]!==s) continue; n++; if(D[i+1].c>D[i+1].o) up++; } console.log('state',s,'next day RTH up',n?Math.round(100*up/n):0,'% of',n,'days'); }
// as a filter on Retest V4 adaptive: skip trades against the regime
const rt=E.simRT2(all,{risk:400,stop:'opp',tgtR:2},{pv:2,tick:0.25}); const stByD=new Map(D.map((x,i)=>[x.d,st[i]])); const prevSt=new Map(); for(let i=1;i<D.length;i++) prevSt.set(D[i].d,st[i-1]);
const base=new Map(), filt=new Map(); rt.forEach((l,d)=>{ if(!feat[d]||!feat[d].committed) return; const L=l.filter(t=>feat[d].bias===t.side); base.set(d,L); const s=prevSt.get(d); filt.set(d, L.filter(t=> s===null||s===0|| s===t.side)); });
console.log('Retest V4 adaptive, no regime filter'); for(const [l,a,z] of per) console.log('  ',l.padEnd(8),line(report(base,a,z)));
console.log('Retest V4 adaptive + skip trades against the 20-day regime'); for(const [l,a,z] of per) console.log('  ',l.padEnd(8),line(report(filt,a,z)));
