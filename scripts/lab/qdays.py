import sys; sys.path.insert(0,'.')
exec(open('final_cfg.py').read().split("exec('TR")[0])
from rules2 import *
tr=build("current",be=True,v4t=1.25); byd=collections.defaultdict(list)
for t in tr: byd[t['d']].append(t)
DD=[d for d in D if d>=20220301]
# funded: room assumed $2,000 constant (fresh account), how many trading days to collect 5 days >= $150 with positive cycle
waits=[]
for i0 in range(0,len(DD)-200,2):
    q=0; net=0
    for j,d in enumerate(DD[i0:]):
        dp=size_day([dict(t) for t in byd.get(d,[])],2000+min(net,0),'updated',slipx=8.0); net+=dp
        if dp>=150: q+=1
        if q>=5 and net>0: waits.append(j+1); break
waits.sort(); print('days to 5 qualifying days: median',waits[len(waits)//2],'p25',waits[len(waits)//4],'p75',waits[3*len(waits)//4])
