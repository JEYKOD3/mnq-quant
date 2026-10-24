import sys; sys.path.insert(0,'.')
from evalh2 import *
import evalh2 as E
def attempt(S,start,f,dll=1100,slipx=8.0,horizon=250,h2w=1.0):
    bal=50000.; peak=50000.; best=0.; td=0
    for d in DAYS:
        if d<start: continue
        td+=1; mll=min(peak-2000,50000); cush=bal-mll; dayp=0.; used=0.
        for t in S.get(d,[]):
            w=t.get('w',1.0)*(h2w if 'setup' in t else 1.0)
            rc=(t['r']+SLIP*T)*PV+2*COMM; pts=t['pts']-(slipx if t['why']=='stop' else 0); pc=pts*PV-2*COMM
            budget=min(w*f*cush, f*cush-used, dll-used); q=min(40,int(budget//rc))
            if q<1 and w>=1 and rc<.9*(cush-used) and rc<dll-used: q=1
            if q<1: continue
            used+=q*rc; dayp+=q*pc
        bal+=dayp; best=max(best,dayp)
        if bal<=mll: return ('F',td)
        peak=max(peak,bal); prof=bal-50000
        if prof>=3000 and best<=.5*prof: return ('P',td)
        if td>=horizon: return ('O',td)
    return ('O',td)
def ev2(S,f,a,z,**kw):
    st=[d for d in DAYS if a<=d<=z][::2]; R=[attempt(S,s,f,**kw) for s in st]; n=len(R)
    P=sorted(r[1] for r in R if r[0]=='P'); Fl=sum(r[0]=='F' for r in R)
    return [sum(x<=k for x in P)/n for k in (10,20,40,60)]+[Fl/n,(P[len(P)//2] if P else 999)]
for names in (['V4','D2','PIN'],['V4','D2','PIN','H2']):
    S=sched(names)
    for sx in (2,4,8):
        for h2w in ((1.0,.5,.33) if 'H2' in names else (1.0,)):
            f=.65
            Dv=ev2(S,f,20220301,20241231,slipx=sx,h2w=h2w); Tt=ev2(S,f,20250101,20260601,slipx=sx,h2w=h2w)
            print(f"{'+'.join(names):14s} stop-slip+{sx}pt H2 size x{h2w} f{f} | DEV 10/20/40/60d "+' '.join(pc(x) for x in Dv[:4])+f" fail {pc(Dv[4])} med {Dv[5]} | TEST "+' '.join(pc(x) for x in Tt[:4])+f" fail {pc(Tt[4])} med {Tt[5]}")
