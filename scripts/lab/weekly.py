import sys, random, statistics, collections, datetime as dt; sys.path.insert(0,'.')
exec(open('month_all.py').read().split("for lab,a,z in")[0])
WK=collections.defaultdict(list)
for d,b in ST.days:
    if d>=20220101:
        k=dt.date(d//10000,d//100%100,d%100).isocalendar()[:2]; WK[k].append((d,b[0][1],b[-1][4]))
res={}
for k,L in WK.items():
    if len(L)<3: continue
    ret=L[-1][2]/L[0][1]-1
    n1,_,_,_=run(L[0][0],L[-1][0],'1mnq'); ne,_,_,_=run(L[0][0],L[-1][0],'eval')
    res[k]=(ret,n1,ne)
B=collections.defaultdict(list)
for k,(ret,a,b) in res.items(): B['BULL' if ret>.015 else ('BEAR' if ret<-.015 else 'RANGE')].append(k)
q=lambda v,p: sorted(v)[int(p*(len(v)-1))]
for nm in ('BULL','RANGE','BEAR'):
    v=[res[k][1] for k in B[nm]]; ve=[res[k][2] for k in B[nm]]
    print(f"{nm:5s} weeks {len(v):3d}: 1 MNQ avg {statistics.mean(v):+.0f}$ median {statistics.median(v):+.0f}$ green {sum(x>0 for x in v)} flat {sum(x==0 for x in v)} red {sum(x<0 for x in v)} | eval avg {statistics.mean(ve):+.0f}$")
random.seed(3); N=20000; s1=[]; se=[]
W={'BULL':.4,'RANGE':.4,'BEAR':.2}
for _ in range(N):
    r=random.random(); nm='BULL' if r<.4 else ('RANGE' if r<.8 else 'BEAR'); k=random.choice(B[nm]); s1.append(res[k][1]); se.append(res[k][2])
print(f"WEEKLY (scenario-weighted): 1 MNQ expected {statistics.mean(s1):+.0f}$ median {q(s1,.5):+.0f}$ 10th {q(s1,.1):+.0f}$ 90th {q(s1,.9):+.0f}$ | green {sum(x>0 for x in s1)/N:.0%} flat {sum(x==0 for x in s1)/N:.0%} red {sum(x<0 for x in s1)/N:.0%}")
print(f"   eval sizing expected {statistics.mean(se):+.0f}$ median {q(se,.5):+.0f}$ 10th {q(se,.1):+.0f}$ 90th {q(se,.9):+.0f}$")
