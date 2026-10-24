import sys, json, datetime as dt, zoneinfo, collections; sys.path.insert(0,'.')
import shortterm as ST
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
tr=ST.run('h2',2,None,trendday=True,dtrend=True,tdth=.4,maxtr=3)
hm=lambda m:f"{m//60}:{m%60:02d}"
for lab,a,z in (('LAST 4 MONTHS (Jun 22 - Oct 23)',20260622,20261023),):
    sel=[t for t in tr if a<=t['d']<=z]; tot=0
    print(lab)
    for t in sel:
        net=t['pts']-2*COMM/PV; tot+=net
        print(f"  {t['d']} {'LONG ' if t['side']>0 else 'SHORT'} {hm(t['eT'])} stop {t['r']:.0f}pt -> {t['why']:5s} after {t['hold']:3d}m  {net:+7.1f}pt  {net*2:+6.0f}$/MNQ  {net/t['r']:+.2f}R")
    W=sum(1 for t in sel if t['pts']-2*COMM/PV>0)
    print(f"  => {len(sel)} trades, {W} winners, {tot:+.1f} pts = {tot*2:+.0f}$ per MNQ, avg hold {sum(t['hold'] for t in sel)/max(1,len(sel)):.0f} min")
    octs=[t for t in sel if t['d']>=20261001]; ot=sum(t['pts']-2*COMM/PV for t in octs)
    print(f"  October only: {len(octs)} trades, {ot:+.1f} pts = {ot*2:+.0f}$ per MNQ")
