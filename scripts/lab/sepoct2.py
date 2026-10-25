import sys,json; sys.path.insert(0,'.')
from rules2 import *
hm=lambda m:f"{m//60}:{m%60:02d}"
res={}
for m in ('current','updated'):
    tr=build(m,20260901,20261023); byd=collections.defaultdict(list)
    for t in tr: byd[t['d']].append(t)
    bal=50000.; peak=50000.; rows=[]
    for d in [x for x in D if 20260901<=x<=20261023]:
        mll=min(peak-2000,50000); cush=bal-mll; trs=byd.get(d,[])
        dp=size_day(trs,cush,m); bal+=dp; peak=max(peak,bal)
        rows.append((d,cush,dp,bal,trs))
    res[m]=rows
    n1=sum(t['net1'] for r in rows for t in r[4]); print(m,'1MNQ',round(n1),'eval',round(rows[-1][3]-50000),'trades',sum(len(r[4]) for r in rows),'sized',sum(t['q']>0 for r in rows for t in r[4]))
    for s in ('V4+','D2','Pinball','H2'):
        t=[x for r in rows for x in r[4] if x['strat']==s]; print('  ',s,len(t),sum(x['net1']>0 for x in t),round(sum(x['net1'] for x in t)),round(sum(x['netq'] for x in t)))
for (d,c0,p0,b0,t0),(_,c1,p1,b1,t1) in zip(res['current'],res['updated']):
    if t0 or t1: print(d,f"cur {p0:+6.0f} room {c0:5.0f} | upd {p1:+6.0f} room {c1:5.0f} |",' ; '.join(f"{t['strat']} {hm(t['eT'])}-{hm(t['xT'])} {t['why']} {t['pts']:+.0f} q{t['q']}" for t in t1))
json.dump({m:[dict(d=d,room=c,day=p,bal=b,trades=[{k:v for k,v in t.items()} for t in trs]) for d,c,p,b,trs in rows] for m,rows in res.items()},open('/tmp/claude-0/-home-claude/afdbc088-26a4-5e84-b77d-b387ee40e855/scratchpad/sepoct2.json','w'))
