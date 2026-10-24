import sys, pickle, itertools; sys.path.insert(0,'.')
from core import *
from hir import TRD, days, F
res=[]
for g,dd,pd in itertools.product((.4,.5,.6,.8),(.4,.5,.6,.7),(1.0,1.2,1.5,9)):
    bias=lambda f,g=g,dd=dd,pd=pd: v4bias(f,g,dd,pd)
    for tf in (1,2):
        base=v4_trades(days,F,tf=tf,tgtR=None,bias=bias)
        for tg in (None,2,3):
            tr=v4_trades(days,F,tf=tf,tgtR=tg,bias=bias) if tg else base
            for trk in ('sma20','r5','none'):
                sel=[t for t in tr if t['d']>=20220101 and (trk=='none' or TRD[t['d']][0 if trk=='sma20' else 1]==t['side'])]
                Dv=summary(sel,20220101,20241231); Tt=summary(sel,20250101,20261231)
                res.append((g,dd,pd,tf,tg,trk,Dv,Tt,yearly(sel)))
pickle.dump(res,open('/tmp/claude-0/-home-claude/afdbc088-26a4-5e84-b77d-b387ee40e855/scratchpad/v4max.pkl','wb'))
# rank by DEV totR (edge x frequency) with min trades
res2=[r for r in res if r[6]['n']>=40]
res2.sort(key=lambda r:-r[6]['totR'])
print('top by DEV total R (2022-24), then TEST (2025-26)')
for g,dd,pd,tf,tg,trk,Dv,Tt,y in res2[:25]:
    print(f"gap{g} dir{dd} pd{pd} {tf}m tgt{tg} trend:{trk:5s} | DEV n{Dv['n']} PF{Dv['pf']} avgR{Dv['avgR']:+.2f} totR{Dv['totR']} dd{Dv['ddR']} | TEST n{Tt['n']} PF{Tt['pf']} avgR{Tt['avgR']:+.2f} totR{Tt['totR']} dd{Tt['ddR']} | {y}")
print('\nplateau check around base (gap.6 dir.6 pd1.2, 1m, tgt2, sma20):')
for r in res:
    g,dd,pd,tf,tg,trk,Dv,Tt,y=r
    if tf==1 and tg==2 and trk=='sma20' and pd==1.2:
        print(f"  gap{g} dir{dd}: DEV PF{Dv['pf']} n{Dv['n']} | TEST PF{Tt['pf']} n{Tt['n']}")
