import sys, json, datetime as dt, zoneinfo, collections; sys.path.insert(0,'.')
import st2 as ST
from core import features, COMM, PV
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
f=ST.F[20261022]; px=[x for x in tv[20261022] if x[0]==629][0][4]
print(f"Oct 22: ADR {f['adr']:.0f}, open {f['open']}, 10:29 close {px}, move {(px-f['open'])/f['adr']:+.2f} ADR (H2 needs 0.40)")
hm=lambda m:f"{m//60}:{m%60:02d}"
for st in ('h2','vwapx','vwap','ema_pb'):
    for th in (.25,.3,.4):
        for tg,tc in ((2,None),(2,60),(1.5,60)):
            tr=ST.run(st,tg,tc,trendday=True,dtrend=True,tdth=th,maxtr=3)
            ST.rep(f"{st} trendday>={th} tgt{tg}R cap{tc}",tr)
        o=[t for t in ST.run(st,2,None,trendday=True,dtrend=True,tdth=th,maxtr=3) if t['d']==20261022]
        print('     Oct22:',' | '.join(f"{'S' if t['side']<0 else 'L'} {hm(t['eT'])} risk{t['r']:.0f} {t['why']} {t['pts']:+.0f}pt" for t in o) or 'none')
