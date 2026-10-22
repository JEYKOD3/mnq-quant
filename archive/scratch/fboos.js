const E=require('/home/claude/mnqscalp/lab/engine.js'), fs=require('fs'), {report,line}=require('./rep.js');
const all=E.parseBars(fs.readFileSync('/home/claude/mnqscalp/lab/mnq_rth.txt','utf8')); const MK={pv:2,tick:0.25};
const cfgs=[['A: poke<=30 w3 stop poke tgt1 pd maxStop60 start 945',{pokeMax:30,within:3,stopMode:'poke',tgtR:1,useSw:false,useOR:false,maxStop:60,sessStart:945}],
 ['B: poke<=30 w3 stop bar tgt1.5 pd maxStop60 start 945',{pokeMax:30,within:3,stopMode:'bar',tgtR:1.5,useSw:false,useOR:false,maxStop:60,sessStart:945}],
 ['C: poke<=30 w3 stop poke tgt1.5 pd maxStop60 start 1000',{pokeMax:30,within:3,stopMode:'poke',tgtR:1.5,useSw:false,useOR:false,maxStop:60,sessStart:1000}],
 ['D: poke<=30 w1 stop bar tgt1 pd maxStop60 start 1000',{pokeMax:30,within:1,stopMode:'bar',tgtR:1,useSw:false,useOR:false,maxStop:60,sessStart:1000}]];
for (const [nm,P] of cfgs){ const dt=E.simFB(all,P,MK); console.log(nm);
  for (const [l,a,z] of [['2022',20220101,20221231],['2023',20230101,20231231],['2024',20240101,20241231],['2025',20250101,20251231],['2026',20260101,20261020],['last 6 mo',20260421,20261020]]) console.log('  ',l.padEnd(9),line(report(dt,a,z))); }
