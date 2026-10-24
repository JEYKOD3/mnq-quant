import json, datetime as dt, zoneinfo, sys, collections, pickle
sys.path.insert(0,'.')
import core
from core import *
NY=zoneinfo.ZoneInfo('America/New_York')
days=load()
# append TV 1m days not in data, verify overlap
r=json.load(open('/tmp/claude-0/-home-claude/afdbc088-26a4-5e84-b77d-b387ee40e855/scratchpad/mnq1_tv.json'))
tv=collections.OrderedDict()
for t,o,h,l,c in r['bars']:
    x=dt.datetime.fromtimestamp(t,NY); m=x.hour*60+x.minute
    if 570<=m<960: tv.setdefault(int(x.strftime('%Y%m%d')),[]).append((m,o,h,l,c))
have={d:b for d,b in days}; mx=0; n=0
for d,b in tv.items():
    if d in have:
        hb={x[0]:x for x in have[d]}
        for x in b:
            if x[0] in hb: n+=1; mx=max(mx,abs(hb[x[0]][4]-x[4]),abs(hb[x[0]][2]-x[2]))
    else: days.append((d,b))
print('TV 1m overlap check: bars',n,'max diff',mx,'| added days',[d for d in tv if d not in have])
F=features(days)
D=[d for d,_ in days]; C={d:b[-1][4] for d,b in days}
def trend(d):
    i=D.index(d); s=sum(C[x] for x in D[i-20:i])/20; return 1 if C[D[i-1]]>s else -1
# V4+
tr=v4_trades(days,F,tf=1,tgtR=2,bias=lambda f: v4bias(f,.4,.4,0))
V4=[t for t in tr if trend(t['d'])==t['side']]
# D2
import csv
EV=collections.defaultdict(set)
for x in csv.DictReader(open('/home/claude/mnq-quant/data/macro_dates.csv')): EV[int(x['date'])].add(x['event'])
D2=[]
for d,b in days:
    f=F.get(d)
    if not f or d<20220101 or {'FOMC','CPI'}&EV.get(d,set()): continue
    idx=[i for i,x in enumerate(b) if x[0]==629]
    if not idx: continue
    i=idx[0]; px=b[i][4]; mv=(px-f['open'])/f['adr']
    if abs(mv)<.5: continue
    s=1 if mv>0 else -1; eP=px+s*SLIP*T; stp=f['open']-s*T
    xi,xP,why,mae,mfe=manage(b,i+1,s,eP,stp,None,0,900)
    D2.append(dict(d=d,side=s,eT=630,eP=eP,stp=stp,r=abs(eP-stp),xT=b[xi][0],xP=xP,why=why,pts=(xP-eP)*s,w=1.0 if trend(d)==s else .5))
# PINBALL
DAILY={d:b[-1][4] for d,b in days}
PIN=[]
for k,d in enumerate(D):
    if d<20220101: continue
    ch=[C[D[j]]-C[D[j-1]] for j in range(k-3,k)]; up=sum(x for x in ch if x>0); dn=-sum(x for x in ch if x<0)
    rsi=100 if dn==0 else 100-100/(1+up/dn); s=1 if rsi<30 else (-1 if rsi>70 else 0)
    if not s or trend(d)!=s: continue
    b=dict(days)[d]; IB=[x for x in b if x[0]<630]; hi=max(x[2] for x in IB); lo=min(x[3] for x in IB)
    lvl=hi+T if s>0 else lo-T
    for i,(m,o,h,l,c) in enumerate(b):
        if m<630 or m>900: continue
        if (s>0 and h>=lvl) or (s<0 and l<=lvl):
            eP=(max(o,lvl) if s>0 else min(o,lvl))+s*SLIP*T; stp=(lo-T) if s>0 else (hi+T)
            if (s>0 and l<=stp) or (s<0 and h>=stp): xi,xP,why=i,stp-s*SLIP*T,'stop'
            else: xi,xP,why,_,_=manage(b,i+1,s,eP,stp,None,0,955)
            PIN.append(dict(d=d,side=s,eT=m,eP=eP,stp=stp,r=abs(eP-stp),xT=b[xi][0],xP=xP,why=why,pts=(xP-eP)*s)); break
A,Z=20260622,20261023
rows=[]
for name,L in (('V4+',V4),('D2',D2),('PIN',PIN)):
    for t in L:
        if A<=t['d']<=Z: rows.append((t['d'],name,t))
rows.sort(key=lambda x:(x[0],x[2]['eT']))
hm=lambda m:f"{m//60}:{m%60:02d}"
tot=collections.defaultdict(float); totR=collections.defaultdict(float); cnt=collections.Counter(); wins=collections.Counter()
# eval-style sizing: risk 65% of room (start 2000), cap 1100/day, cushion trailing
bal=50000.; peak=50000.; lines=[]; curd=None; used=0; dayp=0; daybal={}
def close_day():
    global bal,peak,dayp,used
    bal+=dayp; peak=max(peak,bal); dayp=0; used=0
for d,name,t in rows:
    if d!=curd:
        if curd is not None: close_day(); daybal[curd]=bal
        curd=d
    mll=min(peak-2000,50000); cush=bal-mll
    rc=(t['r']+SLIP*T)*PV+2*COMM; pc=t['pts']*PV-2*COMM
    w=t.get('w',1.0); budget=min(w*.65*cush,.65*cush-used,1100-used); q=min(40,int(budget//rc))
    if q<1 and w>=1 and rc<.9*(cush-used) and rc<1100-used: q=1
    used+=max(q,0)*rc; dayp+=max(q,0)*pc
    tot[name]+=pc; totR[name]+=(t['pts']-2*COMM/PV)/t['r']; cnt[name]+=1; wins[name]+=pc>0
    lines.append(f"{d} {name:4s} {'LONG ' if t['side']>0 else 'SHORT'} {hm(t['eT'])} @{t['eP']:.2f} stop {t['stp']:.2f} ({t['r']:.0f}pt) -> {t['why']:6s} {hm(t['xT'])} @{t['xP']:.2f}  {t['pts']-2*COMM/PV:+7.1f}pt  1 MNQ {pc:+7.0f}$  {(t['pts']-2*COMM/PV)/t['r']:+5.2f}R | eval size {q} MNQ {q*pc:+7.0f}$")
if curd: close_day(); daybal[curd]=bal
print('\n'.join(lines))
print()
for k in ('V4+','D2','PIN'): print(f"{k:4s}: {cnt[k]} trades, {wins[k]} winners, 1 MNQ total {tot[k]:+.0f}$ ({tot[k]/2:+.0f} pts), {totR[k]:+.1f}R")
print(f"ALL : {sum(cnt.values())} trades, 1 MNQ total {sum(tot.values()):+.0f}$ , {sum(totR.values()):+.1f}R")
print(f"Eval-sized account (65% of room, $1100/day cap): 50000 -> {bal:.0f} ({bal-50000:+.0f}$)")
# when would eval pass (target 3000, consistency 50%)
b2=50000; best=0; pk=50000
for d in sorted(daybal):
    pass
