import sys; sys.path.insert(0,'.')
exec(open('rules2_ablate.py').read().split('print("=== Lucid')[0])
for m in ('current','V4 BE only'):
    st=[d for d in DAYS if 20220301<=d<=20241231][::2]
    R=[(s,)+attempt(m,s) for s in st]
    print(m,[ (s,td) for s,o,td in R if o=='F'])
a={(t['d'],t['eT']):t for t in TR['current'] if t['strat']=='V4+'}; b={(t['d'],t['eT']):t for t in TR['V4 BE only'] if t['strat']=='V4+'}
import collections; c=collections.Counter()
for k in a: c[(a[k]['why'],b[k]['why'])]+=1
print(c)
