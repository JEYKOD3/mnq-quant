import sys, json, datetime as dt, zoneinfo, collections; sys.path.insert(0,'.')
import shortterm as ST
from core import features, agg, T
NY=zoneinfo.ZoneInfo('America/New_York')
r=json.load(open('/tmp/claude-0/-home-claude/afdbc088-26a4-5e84-b77d-b387ee40e855/scratchpad/mnq1_tv.json'))
tv=collections.OrderedDict()
for t,o,h,l,c in r['bars']:
    x=dt.datetime.fromtimestamp(t,NY); m=x.hour*60+x.minute
    if 570<=m<960: tv.setdefault(int(x.strftime('%Y%m%d')),[]).append((m,o,h,l,c))
b1=tv[20261022]; f=None
hm=lambda m:f"{m//60}:{m%60:02d}"
b=agg(b1,5); cl=[x[4] for x in b]; e20=ST.ema(cl,20)
tw=[];s=0
for k,x in enumerate(b): s+=(x[2]+x[3]+x[4])/3; tw.append(s/(k+1))
print('open',b1[0][1],'10:29 close',[x for x in b1 if x[0]==629][0][4])
for k,x in enumerate(b):
    m,o,h,l,c=x
    if m<600: continue
    note=''
    if k>=8:
        dn=c<tw[k] and e20[k]<e20[k-3]
        ll=min(y[3] for y in b[:k-2]); rl=min(y[3] for y in b[k-8:k-2])
        pb=b[k-1][4]>b[k-2][4]; brk=c<b[k-1][3] and c<o
        note=f"dn={int(dn)} newlow={int(rl<=ll)} pb={int(pb)} brk={int(brk)}"
        if dn and rl<=ll and pb and brk:
            stp=max(y[2] for y in b[k-3:k+1])+T; note+=f"  SIGNAL risk {stp-c:.1f}"
    print(hm(m),o,h,l,c,f"tw {tw[k]:.1f} e20 {e20[k]:.1f}",note)
