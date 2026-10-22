const E=require('/home/claude/mnqscalp/lab/engine.js'), fs=require('fs'), {report,line,score}=require('./rep.js');
const all=E.parseBars(fs.readFileSync('/home/claude/mnqscalp/lab/mnq_rth.txt','utf8')); const days=all.filter(x=>x.d>=20251101); const MK={pv:2,tick:0.25};
const A=[20260101,20260531], Bh=[20260601,20261020]; const out=[];
for (const pokeMax of [15,30,60]) for (const within of [1,3]) for (const stopMode of ['poke','bar']) for (const tgt of ['1','1.5','2','ema','tp1']) for (const lv of [['pd+or+sw',{}],['pd+or',{useSw:false}],['sw',{usePD:false,useOR:false}],['pd',{useSw:false,useOR:false}]]) for (const maxStop of [30,60]) for (const sessStart of [945,1000]) {
  const P={pokeMax,within,stopMode,maxStop,sessStart,...lv[1]}; if(tgt==='ema'){P.tgtMode='ema';} else if(tgt==='tp1'){P.tp1R=1;P.runR=2;P.beOn=true;P.tgtR=2;} else P.tgtR=+tgt;
  const dt=E.simFB(days,P,MK); const RA=report(dt,...A),RB=report(dt,...Bh); out.push({name:`fail-break poke<=${pokeMax} within ${within} stop ${stopMode} tgt ${tgt} levels ${lv[0]} maxStop ${maxStop} start ${sessStart}`,A:RA,B:RB,sc:Math.min(score(RA),score(RB))}); }
fs.writeFileSync('fb26.json',JSON.stringify(out)); out.sort((a,b)=>b.sc-a.sc);
console.log('variants',out.length,'| both halves profitable',out.filter(o=>o.A.net>0&&o.B.net>0).length,'| green>=55% both',out.filter(o=>o.A.g>=.55*(o.A.g+o.A.r)&&o.B.g>=.55*(o.B.g+o.B.r)).length);
for (const o of out.slice(0,10)) { console.log(o.name); console.log('   Jan-May',line(o.A)); console.log('   Jun-Oct',line(o.B)); }
