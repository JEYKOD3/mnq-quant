import sys, pickle; sys.path.insert(0,'.')
from portfolio import S, attempt, ev, DAYS, TRD, days, F
from core import v4_trades, v4bias
from regime import FOMC
from cont import cont
def norm(t): return dict(d=t['d'],side=t['side'],r=t['r'],pts=t['pts'],why=t['why'])
variants={
 'V4p_.4.4_1.5_2R': dict(g=.4,dd=.4,pd=1.5,tg=2),
 'V4p_.4.4_1.5_3R': dict(g=.4,dd=.4,pd=1.5,tg=3),
 'V4p_.4.5_1.5_2R': dict(g=.4,dd=.5,pd=1.5,tg=2),
 'V4p_.4.4_none_2R': dict(g=.4,dd=.4,pd=0,tg=2),
}
for k,v in variants.items():
    tr=v4_trades(days,F,tf=1,tgtR=v['tg'],bias=lambda f,v=v: v4bias(f,v['g'],v['dd'],v['pd']))
    S[k]={t['d']:norm(t) for t in tr if t['d']>=20220101}
S['D2b']={t['d']:norm(t) for t in cont(630,.5,stop='open',flat=900) if t['d']>=20220101 and t['d'] not in FOMC}
import portfolio
pc=lambda x:f"{round(100*x):3d}%"
for v4k in ['V4']+list(variants):
    for d2w in ((0,0),(1,.5),(1,1)):
        for f in (.5,.65,.8):
            wts={v4k:(1,0),'D2b':d2w}
            order=(v4k,'D2b')
            # patch attempt order via closure
            def att(wts,start,f,order=order): return portfolio.attempt(wts,start,f,order=order)
            def ev2(a,z,step):
                st=[d for d in DAYS if a<=d<=z][::step]; R=[att(wts,s,f) for s in st]; n=len(R)
                P=sorted(r[1] for r in R if r[0]=='P'); Fl=sum(r[0]=='F' for r in R)
                return [sum(x<=k for x in P)/n for k in (10,20,40,60)]+[Fl/n,(P[len(P)//2] if P else 999),len(P)/n]
            Dv=ev2(20220301,20241231,2); Tt=ev2(20250101,20260601,2)
            print(f"{v4k:18s} D2 {d2w} f{f} | DEV p10/20/40/60 "+' '.join(pc(x) for x in Dv[:4])+f" fail {pc(Dv[4])} med {Dv[5]} all {pc(Dv[6])} | TEST "+' '.join(pc(x) for x in Tt[:4])+f" fail {pc(Tt[4])} med {Tt[5]} all {pc(Tt[6])}")
