import sys; sys.path.insert(0,'.')
from rules2 import *
def pf(v):
    g=sum(x for x in v if x>0); l=-sum(x for x in v if x<=0); return g/l if l else 9.9
VAR={
 "A current (2R, no tgt D2/Pin)":(dict(),"current"),
 "B V4+ & H2 at 1.25R":(dict(v4t=1.25,h2t=1.25),"current"),
 "C all four at 1.25R":(dict(v4t=1.25,h2t=1.25,d2t=1.25,pint=1.25),"current"),
 "D V4+ 1.25R only":(dict(v4t=1.25),"current"),
 "E H2 1.25R only":(dict(h2t=1.25),"current"),
 "F 1.5R V4+ & H2":(dict(v4t=1.5,h2t=1.5),"current"),
 "G updated rules":(dict(be=True,pcap=120,h2th=.3),"updated"),
 "H updated + 1.25R all":(dict(be=True,pcap=120,h2th=.3,v4t=1.25,h2t=1.25,d2t=1.25,pint=1.25),"updated"),
}
TR={k:build("current",**v[0]) for k,v in VAR.items()}; MODE={k:v[1] for k,v in VAR.items()}
print("=== 1 MNQ per signal, 2022 - Oct 2026 ===")
for k,t in TR.items():
    for s in ('V4+','D2','Pinball','H2','ALL'):
        x=[u for u in t if s=='ALL' or u['strat']==s]
        R=[(u['pts']-2*COMM/PV)/u['r'] for u in x]; a=[r for u,r in zip(x,R) if u['d']<=20241231]; z=[r for u,r in zip(x,R) if u['d']>20241231]
        if s=='ALL' or k.startswith(('A','C')):
            print(f"{k:32s} {s:8s} n{len(x):4d} win {100*sum(r>0 for r in R)/len(R):3.0f}% PF {pf(R):.2f} ({pf(a):.2f}|{pf(z):.2f}) totR {sum(R):+6.1f} $1MNQ {sum(u['pts']*PV-2*COMM for u in x):+7.0f} hold {sum(u['xT']-u['eT'] for u in x)/len(x):4.0f}m")
DAYS=[d for d in D if 20220301<=d]
byd={k:collections.defaultdict(list) for k in TR}
for k in TR:
    for t in TR[k]: byd[k][t['d']].append(t)
def attempt(m,start,f=.65,horizon=250):
    bal=50000.; peak=50000.; best=0.; td=0
    for d in DAYS:
        if d<start: continue
        td+=1; mll=min(peak-2000,50000); cush=bal-mll
        dp=size_day([dict(t) for t in byd[m].get(d,[])],cush,MODE[m],f=f,slipx=8.0)
        bal+=dp; best=max(best,dp)
        if bal<=mll: return 'F',td
        peak=max(peak,bal)
        if bal-50000>=3000 and best<=.5*(bal-50000): return 'P',td
        if td>=horizon: return 'O',td
    return 'O',td
print("\n=== eval sim, +8pt stop slip ===")
for lab,a,z in (('2022-24',20220301,20241231),('2025-26',20250101,20261023)):
    st=[d for d in DAYS if a<=d<=z][::2]
    for m in TR:
        R=[attempt(m,s) for s in st]; n=len(R); P=sorted(x[1] for x in R if x[0]=='P')
        print(f"{lab} {m:32s} 10d {100*sum(x<=10 for x in P)/n:3.0f}% 20d {100*sum(x<=20 for x in P)/n:3.0f}% 40d {100*sum(x<=40 for x in P)/n:3.0f}% 60d {100*sum(x<=60 for x in P)/n:3.0f}% fail {100*sum(x[0]=='F' for x in R)/n:3.0f}%")
# Sep-Oct
print("\n=== Sep 1 - Oct 23 eval sizing ===")
for m in TR:
    bal=50000.; peak=50000.; best=0
    for d in [x for x in D if 20260901<=x<=20261023]:
        mll=min(peak-2000,50000); dp=size_day([dict(t) for t in byd[m].get(d,[])],bal-mll,MODE[m]); bal+=dp; peak=max(peak,bal); best=max(best,dp)
    n1=sum(t['pts']*PV-2*COMM for t in TR[m] if 20260901<=t['d']<=20261023)
    print(f"{m:32s} 1MNQ {n1:+6.0f}  eval {bal-50000:+6.0f}  best day {best:+5.0f}")
