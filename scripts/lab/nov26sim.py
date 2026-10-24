import sys, random, statistics, collections; sys.path.insert(0,'.')
exec(open('month_all.py').read().split("for lab,a,z in")[0])
# monthly market character from RTH data
MO=collections.defaultdict(list)
for d,b in ST.days:
    if d>=20220101: MO[d//100].append((d,b[0][1],max(x[2] for x in b),min(x[3] for x in b),b[-1][4]))
info={}
for m,L in MO.items():
    if len(L)<15: continue
    ret=L[-1][4]/L[0][1]-1; rng=statistics.mean((x[2]-x[3])/x[1] for x in L)
    info[m]=(ret,rng)
vols=sorted(v[1] for v in info.values()); vmed=vols[len(vols)//2]
def bucket(ret,rng):
    if ret>.03: return 'BULL'
    if ret<-.03: return 'BEAR'
    return 'RANGE'
B=collections.defaultdict(list)
for m,(ret,rng) in info.items(): B[bucket(ret,rng)].append(m)
res={}
for m in info:
    a=m*100+1; z=m*100+31
    n1,per1,_,rows1=run(a,z,'1mnq'); ne,_,_,rowse=run(a,z,'eval')
    # eval month outcome
    bal=50000; pk=50000; best=0; out='open'
    for d,p,_ in rowse:
        bal+=p; best=max(best,p); mll=min(pk-2000,50000)
        if bal<=mll: out='FAIL'; break
        pk=max(pk,bal)
        if bal-50000>=3000 and best<=.5*(bal-50000): out='PASS'; break
    res[m]=(n1,ne,out)
print('historical months by type (2022-2026):')
for k in ('BULL','RANGE','BEAR'):
    L=B[k]; v=[res[m][0] for m in L]; ve=[res[m][1] for m in L]
    print(f"  {k:5s}: {len(L)} months | 1 MNQ/signal: avg {statistics.mean(v):+.0f}$, median {statistics.median(v):+.0f}$, green {sum(x>0 for x in v)}/{len(v)} | eval-sized: avg {statistics.mean(ve):+.0f}$ | eval passed in-month {sum(res[m][2]=='PASS' for m in L)}/{len(L)}, failed {sum(res[m][2]=='FAIL' for m in L)}")
# scenarios for Nov 2026 (weights = my synthesis of strategist views; see notes)
SC={'Post-midterm relief rally (BULL)':('BULL',.40),'Choppy / two-way (RANGE)':('RANGE',.40),'Risk-off continues (BEAR)':('BEAR',.20)}
random.seed(7); N=20000; sims=[]; sime=[]; outs=collections.Counter()
for _ in range(N):
    r=random.random(); acc=0
    for nm,(bk,w) in SC.items():
        acc+=w
        if r<=acc: break
    m=random.choice(B[bk]); sims.append(res[m][0]); sime.append(res[m][1]); outs[res[m][2]]+=1
q=lambda v,p: sorted(v)[int(p*(len(v)-1))]
print('\nNOVEMBER 2026 simulation (scenario-weighted resampling of real historical months):')
for nm,(bk,w) in SC.items(): print(f"  {nm:34s} weight {int(w*100)}%")
print(f"  1 MNQ per signal: expected {statistics.mean(sims):+.0f}$, median {q(sims,.5):+.0f}$, 10th pct {q(sims,.1):+.0f}$, 90th pct {q(sims,.9):+.0f}$, P(green month) {sum(x>0 for x in sims)/N:.0%}")
print(f"  eval sizing:      expected {statistics.mean(sime):+.0f}$, median {q(sime,.5):+.0f}$, 10th {q(sime,.1):+.0f}$, 90th {q(sime,.9):+.0f}$ | eval passed within November {outs['PASS']/N:.0%}, failed {outs['FAIL']/N:.0%}, still open {outs['open']/N:.0%}")
