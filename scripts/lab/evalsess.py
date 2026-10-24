import sys; sys.path.insert(0,'.')
exec(open('sessions.py').read().split("for k,w in (('V4p")[0])
exec(open('news.py').read().split("for k,w in")[0].split("exec(")[0])
import csv, collections
EV=collections.defaultdict(set)
for r in csv.DictReader(open('/home/claude/mnq-quant/data/macro_dates.csv')): EV[int(r['date'])].add(r['event'])
from core import SLIP, T, PV, COMM
DAYS=[d for d,_ in days if d>=20220301]
def sched(cfg):
    out={}
    for d in DAYS:
        L=[]
        t=S['V4p_.4.4_none_2R'].get(d)
        if t and d in TRD and TRD[d][0]==t['side']:
            w=1.0
            if cfg.get('v4lon') and d in info and sg(info[d]['london'])!=t['side']: w=cfg['v4lon']
            L.append((t,w))
        t=S['D2b'].get(d)
        if t and d in TRD and not ({'FOMC','CPI'} & EV.get(d,set()) if cfg.get('skipnews') else False):
            al=TRD[d][0]==t['side']; w=1.0 if al else cfg.get('d2against',1.0)
            if cfg.get('d2lon') is not None and d in info and sg(info[d]['london'])!=t['side']: w*=cfg['d2lon']
            if w>0: L.append((t,w))
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
cfgs={'base (V4+ trend, D2 all)':{}, 'D2 half against trend':{'d2against':.5}, '+skip CPI/FOMC D2':{'skipnews':1},
      'D2 London-filter 0':{'d2lon':0,'skipnews':1}, 'D2 London-filter .5':{'d2lon':.5,'skipnews':1},
      'D2 London .5 + V4 London .5':{'d2lon':.5,'v4lon':.5,'skipnews':1},'D2 London 0 + against .5':{'d2lon':0,'d2against':.5,'skipnews':1}}
for lab,cfg in cfgs.items():
    Sx=sched(cfg)
    for f in (.5,.65,.8):
        Dv=ev2(Sx,f,20220301,20241231); Tt=ev2(Sx,f,20250101,20260601)
        print(f"{lab:32s} f{f} | DEV p10/20/40/60 "+' '.join(pc(x) for x in Dv[:4])+f" fail {pc(Dv[4])} med {Dv[5]} all {pc(Dv[6])} | TEST "+' '.join(pc(x) for x in Tt[:4])+f" fail {pc(Tt[4])} med {Tt[5]} all {pc(Tt[6])}")
