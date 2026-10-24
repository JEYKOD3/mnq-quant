import sys, json, datetime as dt, zoneinfo, collections; sys.path.insert(0,'.')
import shortterm as ST
from core import features, COMM, PV, SLIP, T
NY=zoneinfo.ZoneInfo('America/New_York')
r=json.load(open('/tmp/claude-0/-home-claude/afdbc088-26a4-5e84-b77d-b387ee40e855/scratchpad/mnq1_tv.json'))
tv=collections.OrderedDict()
for t,o,h,l,c in r['bars']:
    x=dt.datetime.fromtimestamp(t,NY); m=x.hour*60+x.minute
    if 570<=m<960: tv.setdefault(int(x.strftime('%Y%m%d')),[]).append((m,o,h,l,c))
have={d for d,_ in ST.days}
for d,b in tv.items():
    if d not in have: ST.days.append((d,b))
ST.F=features(ST.days); ST.D=[d for d,_ in ST.days]; ST.C={d:b[-1][4] for d,b in ST.days}
for i,d in enumerate(ST.D):
    if i>=21: ST.TRD[d]=1 if ST.C[ST.D[i-1]]>sum(ST.C[x] for x in ST.D[i-20:i])/20 else -1
import evalh2 as E
S=E.sched(['V4','D2','PIN','H2'])
def run(a,z,mode):
    bal=50000.; peak=50000.; rows=[]; per=collections.defaultdict(float); n=collections.Counter()
    for d in sorted(x for x in S if a<=x<=z):
        mll=min(peak-2000,50000); cush=bal-mll; used=0; dayp=0
        for t in S[d]:
            nm='H2' if 'setup' in t else ('D2' if t['eT']==630 and 'w' in t else ('V4+' if t in E.V4 else 'PIN'))
            pc=(t['pts']-2*COMM/PV)*PV
            if mode=='1mnq': q=1
            else:
                w=t.get('w',1.0)*(0.5 if nm=='H2' else 1.0); rc=(t['r']+SLIP*T)*PV+2*COMM
                budget=min(w*.65*cush,.65*cush-used,1100-used); q=min(40,int(budget//rc))
                if q<1 and w>=1 and rc<.9*(cush-used) and rc<1100-used: q=1
                q=max(q,0); used+=q*rc
            dayp+=q*pc; per[nm]+=q*pc; n[nm]+=1
        bal+=dayp; peak=max(peak,bal); rows.append((d,dayp,bal))
    return bal-50000, per, n, rows
for lab,a,z in (('OCTOBER 1-23',20261001,20261023),('LAST 30 DAYS (Sep 24 - Oct 23)',20260924,20261023)):
    for mode in ('1mnq','eval'):
        net,per,n,rows=run(a,z,mode)
        g=sum(1 for _,p,_ in rows if p>0); rd=sum(1 for _,p,_ in rows if p<0)
        print(f"{lab} [{ '1 MNQ per signal' if mode=='1mnq' else 'eval sizing 50K (65% of room, H2 half)'}]: net {net:+.0f}$ | "+', '.join(f"{k} {per[k]:+.0f}$ ({n[k]} tr)" for k in ('V4+','D2','PIN','H2'))+f" | trading days {len(rows)}: {g} green / {rd} red")
# long-run monthly expectation, 1 MNQ per signal, 2022-01..2026-10
mo=collections.defaultdict(float)
for d,L in S.items():
    for t in L: mo[d//100]+=(t['pts']-2*COMM/PV)*PV
v=sorted(mo.values()); import statistics
print(f"2022-2026 monthly P&L at 1 MNQ per signal: mean {statistics.mean(v):+.0f}$, median {statistics.median(v):+.0f}$, worst {v[0]:+.0f}$, best {v[-1]:+.0f}$, green months {sum(x>0 for x in v)}/{len(v)}")
