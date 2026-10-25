import sys; sys.path.insert(0,'.')
from rules2 import *
import collections
def pf(v):
    g=sum(x for x in v if x>0); l=-sum(x for x in v if x<=0); return g/l if l else 9.9
TR={m:build(m) for m in ('current','updated')}
print("=== 2022 - Oct 2026, 1 MNQ per signal (net R after costs) ===")
for m in TR:
    for s in ('V4+','D2','Pinball','H2','ALL'):
        t=[x for x in TR[m] if s=='ALL' or x['strat']==s]
        R=[(x['pts']-2*COMM/PV)/x['r'] for x in t]; a=[(x['pts']-2*COMM/PV)/x['r'] for x in t if x['d']<=20241231]; z=[(x['pts']-2*COMM/PV)/x['r'] for x in t if x['d']>20241231]
        dl=sum((x['pts']*PV-2*COMM) for x in t); hold=sum(x['xT']-x['eT'] for x in t)/len(t)
        print(f"{m:8s} {s:8s} n{len(t):4d} win {100*sum(x>0 for x in R)/len(R):3.0f}% PF {pf(R):.2f} (22-24 {pf(a):.2f} | 25-26 {pf(z):.2f}) totR {sum(R):+6.1f}  $1MNQ {dl:+8.0f}  hold {hold:4.0f}m")
# eval attempts with stress (+8 pts on stops), start every 2 days
DAYS=[d for d in D if 20220301<=d]
byd={m:collections.defaultdict(list) for m in TR}
for m in TR:
    for t in TR[m]: byd[m][t['d']].append(t)
def attempt(m,start,f=.65,horizon=250):
    bal=50000.; peak=50000.; best=0.; td=0
    for d in DAYS:
        if d<start: continue
        td+=1; mll=min(peak-2000,50000); cush=bal-mll
        trs=[dict(t) for t in byd[m].get(d,[])]
        dp=size_day(trs,cush,m,f=f,slipx=8.0)
        bal+=dp; best=max(best,dp)
        if bal<=mll: return 'F',td
        peak=max(peak,bal)
        if bal-50000>=3000 and best<=.5*(bal-50000): return 'P',td
        if td>=horizon: return 'O',td
    return 'O',td
print("\n=== Lucid Flex 50K eval, attempts every 2 days, +8pt stop slippage ===")
for lab,a,z in (('2022-24',20220301,20241231),('2025-26',20250101,20261023)):
    st=[d for d in DAYS if a<=d<=z][::2]
    for m in TR:
        R=[attempt(m,s) for s in st]; n=len(R); P=sorted(x[1] for x in R if x[0]=='P')
        print(f"{lab} {m:8s} passed within 10d {100*sum(x<=10 for x in P)/n:3.0f}%  20d {100*sum(x<=20 for x in P)/n:3.0f}%  40d {100*sum(x<=40 for x in P)/n:3.0f}%  60d {100*sum(x<=60 for x in P)/n:3.0f}%  failed {100*sum(x[0]=='F' for x in R)/n:3.0f}%  median days {P[len(P)//2] if P else '-'}")
