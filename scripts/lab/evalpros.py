import sys, collections, csv; sys.path.insert(0,'.')
from pros import pinball, williams, oops, acd
from core import summary, yearly, SLIP, T, PV, COMM, v4bias
from hir import TRD, days, F
import pickle
exec(open('evalv4plus.py').read().split("import portfolio")[0])
EV=collections.defaultdict(set)
for r in csv.DictReader(open('/home/claude/mnq-quant/data/macro_dates.csv')): EV[int(r['date'])].add(r['event'])
def nm(tr): return {t['d']:dict(d=t['d'],side=t['s'],r=t['r'],pts=t['pts'],why=t['why'],R=t['Rn']) for t in tr}
S['PIN']=nm(pinball(True)); S['WVB']=nm(williams(.4,None,True,None)); S['OOPS']=nm(oops(.15,720,'close',True)); S['ACD']=nm(acd(.1,15,8,True))
v4days={d for d,t in S['V4p_.4.4_none_2R'].items() if d in TRD and TRD[d][0]==t['side']}
for k in ('PIN','WVB','OOPS','ACD'):
    allt=list(S[k].values()); off=[t for t in allt if t['d'] not in v4days]
    for lab,tr in (('all',allt),('V4-off days',off)):
        R=[t['R'] for t in tr]; g=sum(x for x in R if x>0); l=-sum(x for x in R if x<=0)
        dv=[t['R'] for t in tr if t['d']<=20241231]; tv=[t['R'] for t in tr if t['d']>20241231]
        pf=lambda v:(sum(x for x in v if x>0)/-sum(x for x in v if x<=0)) if any(x<=0 for x in v) else 9.9
        print(f"{k:5s} {lab:12s} n{len(tr):4d} PF{g/l:5.2f} DEV{pf(dv):5.2f} TEST{pf(tv):5.2f} avgR{sum(R)/len(R):+.2f}")
DAYS=[d for d,_ in days if d>=20220301]
def sched(streams):
    out={}
    for d in DAYS:
        L=[]
        t=S['V4p_.4.4_none_2R'].get(d)
        if t and d in TRD and TRD[d][0]==t['side']: L.append((t,1.0))
        for k,w,offonly in streams:
            t=S[k].get(d)
            if not t: continue
            if k=='D2b':
                if {'FOMC','CPI'} & EV.get(d,set()): continue
                ww=1.0 if TRD.get(d,(0,))[0]==t['side'] else .5
            else: ww=w
            if offonly and L: continue
            L.append((t,ww))
        if L: out[d]=L
    return out
def attempt(Sx,start,f,dll=1100,slipx=8.0,horizon=250):
    bal=50000.; peak=50000.; best=0.; td=0
    for d in DAYS:
        if d<start: continue
        td+=1; mll=min(peak-2000,50000); cush=bal-mll; dayp=0.; used=0.
        for t,w in Sx.get(d,[]):
            rc=(t['r']+SLIP*T)*PV+2*COMM; pts=t['pts']-(slipx if t['why']=='stop' else 0); pc=pts*PV-2*COMM
            budget=min(w*f*cush, f*cush-used, dll-used); q=min(40,int(budget//rc))
            if q<1 and w>=1 and rc<0.9*(cush-used) and rc<dll-used: q=1
            if q<1: continue
            used+=q*rc; dayp+=q*pc
        bal+=dayp; best=max(best,dayp)
        if bal<=mll: return ('F',td)
        peak=max(peak,bal); prof=bal-50000
        if prof>=3000 and best<=0.5*prof: return ('P',td)
        if td>=horizon: return ('O',td)
    return ('O',td)
def ev2(Sx,f,a,z,step=2):
    st=[d for d in DAYS if a<=d<=z][::step]; R=[attempt(Sx,s,f) for s in st]; n=len(R)
    P=sorted(r[1] for r in R if r[0]=='P'); Fl=sum(r[0]=='F' for r in R)
    return [sum(x<=k for x in P)/n for k in (10,20,40,60)]+[Fl/n,(P[len(P)//2] if P else 999),len(P)/n]
pc=lambda x:f"{round(100*x):3d}%"
cfgs={'V4+ & D2 (current)':[('D2b',1,False)],
      '+PIN':[('D2b',1,False),('PIN',1,False)],
      '+PIN +OOPS':[('D2b',1,False),('PIN',1,False),('OOPS',1,False)],
      '+PIN +WVB(off-days)':[('D2b',1,False),('PIN',1,False),('WVB',1,True)],
      '+PIN +WVB(.5,off)':[('D2b',1,False),('PIN',1,False),('WVB',.5,True)],
      '+PIN +ACD(off)':[('D2b',1,False),('PIN',1,False),('ACD',1,True)],
      '+PIN +WVB(off) +OOPS':[('D2b',1,False),('PIN',1,False),('WVB',1,True),('OOPS',1,False)],
      'V4+ +PIN +WVB(off) (no D2)':[('PIN',1,False),('WVB',1,True)]}
for lab,st in cfgs.items():
    Sx=sched(st)
    for f in (.5,.65,.8):
        Dv=ev2(Sx,f,20220301,20241231); Tt=ev2(Sx,f,20250101,20260601)
        print(f"{lab:30s} f{f} | DEV p10/20/40/60 "+' '.join(pc(x) for x in Dv[:4])+f" fail {pc(Dv[4])} med {Dv[5]} all {pc(Dv[6])} | TEST "+' '.join(pc(x) for x in Tt[:4])+f" fail {pc(Tt[4])} med {Tt[5]} all {pc(Tt[6])}")
