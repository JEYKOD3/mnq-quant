import sys; sys.path.insert(0,'.')
from evalmix import *
def attempt2(S,start,f,dll=1100,slipx=0.0,horizon=250):
    bal=50000.; peak=50000.; best=0.; td=0
    for d in DAYS:
        if d<start: continue
        td+=1; mll=min(peak-2000,50000); cush=bal-mll; dayp=0.; used=0.
        for t in S.get(d,[]):
            rc=(t['r']+SLIP*T)*PV+2*COMM
            pts=t['pts'] - (slipx if t['why']=='stop' else 0)
            pc=pts*PV-2*COMM
            budget=min(f*cush-used, (dll-used) if dll else 1e9)
            q=min(40,int(budget//rc))
            if q<1 and rc<0.9*(cush-used) and (not dll or rc<dll-used): q=1
            if q<1: continue
            used+=q*rc; dayp+=q*pc
        bal+=dayp; best=max(best,dayp)
        if bal<=mll: return ('F',td)
        peak=max(peak,bal); prof=bal-50000
        if prof>=3000 and best<=0.5*prof: return ('P',td)
        if td>=horizon: return ('O',td)
    return ('O',td)
def ev(S,f,a,z,**kw):
    st=[d for d in DAYS if a<=d<=z]; R=[attempt2(S,s,f,**kw) for s in st]; n=len(R)
    P=sorted(r[1] for r in R if r[0]=='P'); Fl=[r[1] for r in R if r[0]=='F']
    return [sum(x<=k for x in P)/n for k in (10,20,40,60,120)]+[len(Fl)/n, (P[len(P)//2] if P else 999), len(P)/n]
pc=lambda x:f"{round(100*x):3d}%"
print('pass within 10/20/40/60/120 trading days | fail | median days | pass by 250d   (DEV starts 2022-24 / TEST 2025-26.06)')
for v,d,m in (('V4_1m_2R',None,'V4'),('V4_1m_2R','D2_1030_4l_close','both'),('V4_1m_2R','D2_1030_o_1500','both'),('V4_1m_2R','D2_1130_l_close','both')):
    S=sched(v,d,m)
    for dll in (1100,None):
        for f in (.5,.65,.8,1.0):
            for sx in (8,):
                D=ev(S,f,20220101,20241231,dll=dll,slipx=sx); Tt=ev(S,f,20250101,20260601,dll=dll,slipx=sx)
                print(f"{m:4s} {v} + {str(d):16s} f{f:4.2f} DLL{'on ' if dll else 'off'} slip+{sx}pt | DEV "+' '.join(pc(x) for x in D[:5])+f" | fail {pc(D[5])} | med {D[6]:3d} | {pc(D[7])}  || TEST "+' '.join(pc(x) for x in Tt[:5])+f" | fail {pc(Tt[5])} | med {Tt[6]:3d} | {pc(Tt[7])}")
