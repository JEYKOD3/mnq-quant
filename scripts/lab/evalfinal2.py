import sys; sys.path.insert(0,'.')
from evalfinal import *
from cont import cont
import pickle
TR['D2_1100_o_1500']=[t for t in cont(660,.5,stop='open',flat=900) if t['d']>=20220101]
# union: 10:30 signal else 11:30 signal (same rules), both exit 15:00 stop open
u={}
for t in TR['D2_1030_o_1500']: u[t['d']]=t
for t in [t for t in cont(690,.5,stop='open',flat=900) if t['d']>=20220101]:
    u.setdefault(t['d'],t)
TR['D2_1030or1130_o_1500']=sorted(u.values(),key=lambda t:t['d'])
from core import summary, yearly
for k in ('D2_1100_o_1500','D2_1030or1130_o_1500'): print(k,summary(TR[k]),yearly(TR[k]))
cfgs=[('V4T r5 + D2 1030|1130 /15:00','V4_1m_2R','D2_1030or1130_o_1500',dict(kind='r5')),
      ('V4T sma20 + D2 1030|1130 /15:00','V4_1m_2R','D2_1030or1130_o_1500',dict(kind='sma20')),
      ('V4T sma20 + D2 1030|1130 (.5 against)','V4_1m_2R','D2_1030or1130_o_1500',dict(kind='sma20',d2against=.5)),
      ('V4T r5 + D2 1100/15:00','V4_1m_2R','D2_1100_o_1500',dict(kind='r5'))]
for lab,v,d,kw in cfgs:
    S=build(v,d,**kw)
    for f in (.5,.65,.8):
        Dv=ev(S,f,20220301,20241231); Tt=ev(S,f,20250101,20260601)
        print(f"{lab:46s} f{f:.2f} | DEV "+' '.join(pc(x) for x in Dv[:4])+f" | fail {pc(Dv[4])} | med {Dv[5]:3d} | {pc(Dv[6])} || TEST "+' '.join(pc(x) for x in Tt[:4])+f" | fail {pc(Tt[4])} | med {Tt[5]:3d} | {pc(Tt[6])}")
