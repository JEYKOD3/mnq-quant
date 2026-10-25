import sys; sys.path.insert(0,'.')
from rules2 import *
import collections
def pf(v):
    g=sum(x for x in v if x>0); l=-sum(x for x in v if x<=0); return g/l if l else 9.9
VAR={"current":(dict(),"current"),"sizing only":(dict(),"updated"),"V4 BE only":(dict(be=True),"current"),"Pin 2h only":(dict(pcap=120),"current"),"H2 0.30 only":(dict(h2th=.3),"current"),"all four":(dict(be=True,pcap=120,h2th=.3),"updated"),"3 rule changes, old sizing":(dict(be=True,pcap=120,h2th=.3),"current"),"BE+sizing":(dict(be=True),"updated")}
TR={k:build("current",**v[0]) for k,v in VAR.items()}
MODE={k:v[1] for k,v in VAR.items()}
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
        dp=size_day(trs,cush,MODE[m],f=f,slipx=8.0)
        bal+=dp; best=max(best,dp)
        if bal<=mll: return 'F',td
        peak=max(peak,bal)
        if bal-50000>=3000 and best<=.5*(bal-50000): return 'P',td
        if td>=horizon: return 'O',td
    return 'O',td
print("=== Lucid Flex 50K eval, attempts every 2 days, +8pt stop slippage ===")
for lab,a,z in (('2022-24',20220301,20241231),('2025-26',20250101,20261023)):
    st=[d for d in DAYS if a<=d<=z][::2]
    for m in TR:
        R=[attempt(m,s) for s in st]; n=len(R); P=sorted(x[1] for x in R if x[0]=='P')
        print(f"{lab} {m:28s} 10d {100*sum(x<=10 for x in P)/n:3.0f}%  20d {100*sum(x<=20 for x in P)/n:3.0f}%  40d {100*sum(x<=40 for x in P)/n:3.0f}%  60d {100*sum(x<=60 for x in P)/n:3.0f}%  failed {100*sum(x[0]=='F' for x in R)/n:3.0f}%")
