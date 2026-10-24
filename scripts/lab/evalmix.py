import pickle, sys, collections, itertools
sys.path.insert(0,'.'); from core import *
TR=pickle.load(open('/tmp/claude-0/-home-claude/afdbc088-26a4-5e84-b77d-b387ee40e855/scratchpad/trades.pkl','rb'))
days,F=pickle.load(open('/tmp/claude-0/-home-claude/afdbc088-26a4-5e84-b77d-b387ee40e855/scratchpad/lab.pkl','rb'))
DAYS=[d for d,_ in days if d>=20220101]
def per_day(k): 
    m={}
    for t in TR[k]: m.setdefault(t['d'],t)
    return m
def sched(v4k,d2k,mode):
    A=per_day(v4k) if v4k else {}; B=per_day(d2k) if d2k else {}
    S={}
    for d in DAYS:
        L=[]
        if mode in ('V4','both','V4+D2off') and d in A: L.append(A[d])
        if mode=='D2' and d in B: L.append(B[d])
        if mode=='both' and d in B: L.append(B[d])
        if mode=='V4+D2off' and d not in A and d in B: L.append(B[d])
        if L: S[d]=L
    return S
def attempt(S,start,f,dll=1100,horizon=250,minq=True):
    bal=50000.; peak=50000.; best=0.; td=0
    for d in DAYS:
        if d<start: continue
        td+=1; mll=min(peak-2000,50000); cush=bal-mll; dayp=0.; used=0.
        for t in S.get(d,[]):
            rc=(t['r']+SLIP*T)*PV+2*COMM; pc=t['pts']*PV-2*COMM
            budget=min(f*cush-used, dll-used)
            q=min(40,int(budget//rc))
            if q<1 and minq and rc<0.9*(cush-used) and rc<dll-used: q=1
            if q<1: continue
            used+=q*rc; dayp+=q*pc
        bal+=dayp; best=max(best,dayp)
        if bal<=mll: return ('F',td)
        peak=max(peak,bal); prof=bal-50000
        if prof>=3000 and best<=0.5*prof: return ('P',td)
        if td>=horizon: return ('O',td)
    return ('O',td)
def evalset(S,f,a,z):
    st=[d for d in DAYS if a<=d<=z]; R=[attempt(S,s,f) for s in st]; n=len(R)
    P=[r[1] for r in R if r[0]=='P']; Fl=[r for r in R if r[0]=='F']
    med=sorted(P)[len(P)//2] if P else 999
    return dict(p20=sum(x<=20 for x in P)/n,p40=sum(x<=40 for x in P)/n,p60=sum(x<=60 for x in P)/n,pass_=len(P)/n,fail=len(Fl)/n,med=med)
if __name__=='__main__':
    rows=[]
    V4s=['V4_1m_2R','V4_1m_close','V4_1m_1500']; D2s=['D2_1030_o_1500','D2_1130_l_close','D2_1030_4l_close','D2_1100_l_close']
    combos=[(v,None,'V4') for v in V4s]+[(None,d,'D2') for d in D2s]+[(v,d,m) for v in V4s for d in D2s for m in ('V4+D2off','both')]
    for v,d,m in combos:
        S=sched(v,d,m)
        for f in (.35,.5,.65,.8,1.0):
            D=evalset(S,f,20220101,20241231); Tt=evalset(S,f,20250101,20260601)
            rows.append((v,d,m,f,D,Tt))
    pickle.dump(rows,open('/tmp/claude-0/-home-claude/afdbc088-26a4-5e84-b77d-b387ee40e855/scratchpad/evalmix.pkl','wb'))
    rows.sort(key=lambda r:-(r[4]['p40']-r[4]['fail']))
    pc=lambda x:f"{round(100*x):3d}%"
    print('mode        V4             D2                 f    | DEV p20 p40 p60 fail med | TEST p20 p40 p60 fail med')
    for v,d,m,f,D,Tt in rows[:45]:
        print(f"{m:10s} {str(v):14s} {str(d):18s} {f:4.2f} |",pc(D['p20']),pc(D['p40']),pc(D['p60']),pc(D['fail']),f"{D['med']:4d}",'|',pc(Tt['p20']),pc(Tt['p40']),pc(Tt['p60']),pc(Tt['fail']),f"{Tt['med']:4d}")
