import sys, pickle; sys.path.insert(0,'.')
from regime2 import reg, trend_alt, TR, FOMC
from evalmix import DAYS
from core import SLIP, T, PV, COMM
def tdir(d,kind): 
    try: return trend_alt(d,kind)
    except Exception: return 0
def build(v4k,d2k,kind='sma20',v4against=0.0,d2against=1.0,d2mode='both',skipfomc=True):
    A={};B={}
    for t in TR[v4k]: A.setdefault(t['d'],t)
    if d2k:
        for t in TR[d2k]: B.setdefault(t['d'],t)
    S={}
    for d in DAYS:
        if d not in reg: continue
        L=[]
        if d in A:
            t=A[d]; w=1.0 if tdir(d,kind)==t['side'] else v4against
            if w>0: L.append((t,w))
        if d in B and not (skipfomc and d in FOMC) and (d2mode=='both' or not L):
            t=B[d]; w=1.0 if tdir(d,kind)==t['side'] else d2against
            if w>0: L.append((t,w))
        if L: S[d]=L
    return S
def attempt(S,start,f,dll=1100,slipx=8.0,horizon=250):
    bal=50000.; peak=50000.; best=0.; td=0
    for d in DAYS:
        if d<start: continue
        td+=1; mll=min(peak-2000,50000); cush=bal-mll; dayp=0.; used=0.
        for t,w in S.get(d,[]):
            rc=(t['r']+SLIP*T)*PV+2*COMM; pts=t['pts']-(slipx if t['why']=='stop' else 0); pc=pts*PV-2*COMM
            budget=min(w*f*cush, f*cush-used, (dll-used) if dll else 1e9)
            q=min(40,int(budget//rc))
            if q<1 and rc<0.9*(cush-used) and (not dll or rc<dll-used) and w>=1: q=1
            if q<1: continue
            used+=q*rc; dayp+=q*pc
        bal+=dayp; best=max(best,dayp)
        if bal<=mll: return ('F',td)
        peak=max(peak,bal); prof=bal-50000
        if prof>=3000 and best<=0.5*prof: return ('P',td)
        if td>=horizon: return ('O',td)
    return ('O',td)
def ev(S,f,a,z,**kw):
    st=[d for d in DAYS if a<=d<=z and d in reg]; R=[attempt(S,s,f,**kw) for s in st]; n=len(R)
    P=sorted(r[1] for r in R if r[0]=='P'); Fl=[r for r in R if r[0]=='F']
    return [sum(x<=k for x in P)/n for k in (10,20,40,60)]+[len(Fl)/n,(P[len(P)//2] if P else 999),len(P)/n]
pc=lambda x:f"{round(100*x):3d}%"
if __name__=='__main__':
    print('pass<=10/20/40/60 trading days | fail | median | pass<=250d.  slip +8pt on every stop, DLL $1100 on')
    cfgs=[('V4 all (baseline)','V4_1m_2R',None,dict(v4against=1.0)),
          ('V4 trend-only sma20','V4_1m_2R',None,dict(kind='sma20')),
          ('V4 trend-only r5','V4_1m_2R',None,dict(kind='r5')),
          ('V4T sma20 + D2 1030/15:00 (all)','V4_1m_2R','D2_1030_o_1500',dict(kind='sma20')),
          ('V4T sma20 + D2 1030/15:00 (trend .5 against)','V4_1m_2R','D2_1030_o_1500',dict(kind='sma20',d2against=.5)),
          ('V4T sma20 + D2 1030 lod/close','V4_1m_2R','D2_1030_4l_close',dict(kind='sma20')),
          ('V4T sma20 + D2 1130 lod/close','V4_1m_2R','D2_1130_l_close',dict(kind='sma20')),
          ('V4T sma20 + D2 1130 (trend .5 against)','V4_1m_2R','D2_1130_l_close',dict(kind='sma20',d2against=.5)),
          ('V4T r5 + D2 1030/15:00','V4_1m_2R','D2_1030_o_1500',dict(kind='r5')),
          ('V4T r5 + D2 1130 lod/close','V4_1m_2R','D2_1130_l_close',dict(kind='r5')),
          ('V4 all + D2 1030/15:00 (old)','V4_1m_2R','D2_1030_o_1500',dict(kind='sma20',v4against=1.0)),
          ('V4 .5 against + D2 1130','V4_1m_2R','D2_1130_l_close',dict(kind='sma20',v4against=.5)),]
    for lab,v,d,kw in cfgs:
        S=build(v,d,**kw)
        for f in (.5,.65,.8):
            Dv=ev(S,f,20220301,20241231); Tt=ev(S,f,20250101,20260601)
            print(f"{lab:46s} f{f:.2f} | DEV "+' '.join(pc(x) for x in Dv[:4])+f" | fail {pc(Dv[4])} | med {Dv[5]:3d} | {pc(Dv[6])} || TEST "+' '.join(pc(x) for x in Tt[:4])+f" | fail {pc(Tt[4])} | med {Tt[5]:3d} | {pc(Tt[6])}")
