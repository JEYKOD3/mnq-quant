"""Anatomy of big fast moves: per day, the largest 30-min and 60-min directional run (low->high or high->low within window, end-to-start close based).
Where/when do they start, what preceded them (prior 30m compression, OR state, trend, gap), can they be anticipated?"""
import pickle, sys, collections, datetime
sys.path.insert(0,'.'); from core import *
from hir import TRD, days, F
rows=[]
for d,b in days:
    f=F.get(d)
    if not f or d<20220101 or len(b)<380: continue
    adr=f['adr']; n=len(b); cl=[x[4] for x in b]
    best=(0,0,0)
    for W in (30,):
        for i in range(n-W):
            mv=cl[i+W]-cl[i]
            if abs(mv)>abs(best[0]): best=(mv,i,W)
    mv,i,W=best; s=1 if mv>0 else -1
    pre=b[max(0,i-30):i] or b[:1]
    comp=(max(x[2] for x in pre)-min(x[3] for x in pre))/adr
    t20,t5=TRD[d]
    rows.append(dict(d=d,mv=abs(mv)/adr,start=b[i][0],s=s,comp=comp,with20=(s==t20),with5=(s==t5),gapdir=(1 if f['gap']>0 else -1)==s,
                     ordir=(1 if f['orDir']>0 else -1)==s, v4=v4bias(f), wd=datetime.date(d//10000,d//100%100,d%100).weekday()))
print('days',len(rows))
q=lambda v,p: sorted(v)[int(p*(len(v)-1))]
print('biggest 30-min move per day (ADR units): median %.2f  p75 %.2f  p90 %.2f'%(q([r['mv'] for r in rows],.5),q([r['mv'] for r in rows],.75),q([r['mv'] for r in rows],.9)))
def hist(key,lab,sel=lambda r:True):
    c=collections.Counter(key(r) for r in rows if sel(r)); n=sum(c.values())
    print(lab+': '+'  '.join(f"{k}:{100*v/n:.0f}%" for k,v in sorted(c.items())))
bucket=lambda m: f"{m//60}:{(m%60)//30*30:02d}"
hist(lambda r: bucket(r['start']),'start time of biggest 30m move (all days)')
hist(lambda r: bucket(r['start']),'start time when move >= .4 ADR',lambda r:r['mv']>=.4)
hist(lambda r: 'with' if r['with20'] else 'against','direction vs SMA20 trend (all)')
hist(lambda r: 'with' if r['with20'] else 'against','direction vs SMA20 trend (move>=.4)',lambda r:r['mv']>=.4)
hist(lambda r: 'same' if r['ordir'] else 'opp','direction vs first-15m direction (move>=.4)',lambda r:r['mv']>=.4)
hist(lambda r: 'same' if r['gapdir'] else 'opp','direction vs gap direction (move>=.4)',lambda r:r['mv']>=.4)
hist(lambda r: ('v4 same' if r['v4']==r['s'] else 'v4 opp') if r['v4'] else 'no v4','vs V4 bias (move>=.4)',lambda r:r['mv']>=.4)
hist(lambda r: 'tight<.15' if r['comp']<.15 else ('.15-.3' if r['comp']<.3 else 'wide'),'prior-30m range before the big move (move>=.4)',lambda r:r['mv']>=.4)
hist(lambda r: ['Mon','Tue','Wed','Thu','Fri'][r['wd']],'weekday share of days with a >=.4 move',lambda r:r['mv']>=.4)
pickle.dump(rows,open('/tmp/claude-0/-home-claude/afdbc088-26a4-5e84-b77d-b387ee40e855/scratchpad/anatomy.pkl','wb'))
