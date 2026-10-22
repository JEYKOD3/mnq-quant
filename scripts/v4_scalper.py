#!/usr/bin/env python3
"""V4 Scalper lab. ORB/open = direction only (V4 committed-open filter). Entries = with-bias pullbacks to a level on 1m
(OR edge, VWAP, EMA21, prior-day H/L/C, intraday swing), signal bar, stop order 1 tick beyond.
Exits = TP1 on half (pts), stop to BE, runner to next S/R level (or R multiple), optional trail, max hold.
2 contracts (1 scalp + 1 runner). Costs: $2.37/side/contract + 1 tick slip per side.
Develop window: 2026-06-01..2026-10-20. Holdout: 2026-01..05 and 2022-25 reported for every config.
"""
import sys, collections, itertools, json
RAW='/home/claude/mnq-quant/data/raw/mnq_rth_1m.txt'
FEAT='/home/claude/mnq-quant/data/features/day_features.json'
feat=json.load(open(FEAT))
days=[]
for line in open(RAW):
    p=line.strip().split('|')
    if len(p)<300: continue
    d=p[0]
    if d<'20220101': continue
    bars=[]
    for x in p[1:]:
        t,o,h,l,c=x.split(','); t=int(t); bars.append((t//100*60+t%100,int(o)/4,int(h)/4,int(l)/4,int(c)/4))
    days.append((d,bars))
DD=dict(days)
COMM=2.37; TICK=.25; PV=2.0

def v4bias(d):
    f=feat.get(d)
    if not f or f['pdRel']>1.2: return 0
    G=abs(f['gap'])>=.6; D=abs(f['orDir'])>=.6
    if not (G or D): return 0
    return (1 if f['gap']>0 else -1) if G else (1 if f['orDir']>0 else -1)

def prevday(i):
    if i==0: return None
    b=days[i-1][1]; return (max(x[2] for x in b),min(x[3] for x in b),b[-1][4])

def run(di,P):
    d,bars=days[di]; side=v4bias(d)
    if side==0: return []
    pd=prevday(di); n=len(bars)
    orb=[b for b in bars if b[0]<585]; orh=max(b[2] for b in orb); orl=min(b[3] for b in orb)
    # running vwap, ema21, atr20 (1m), swings
    pv=0; vol=0; vw=[None]*n; ema=[None]*n; e=None; k=2/22; rng=[0]*n
    for i,(t,o,h,l,c) in enumerate(bars):
        tp=(h+l+c)/3; pv+=tp; vol+=1; vw[i]=pv/vol   # no volume in file -> TWAP of typical price (proxy)
        e=c if e is None else e+k*(c-e); ema[i]=e
        rng[i]=sum(b[2]-b[3] for b in bars[max(0,i-19):i+1])/min(20,i+1)
    trades=[]; pos=None; pend=None; ntr=0; losses=0; consec=0; dayPnl=0
    swH=[]; swL=[]
    for i in range(1,n):
        t,o,h,l,c=bars[i]
        # swings (confirmed 3 bars later)
        if i>=6:
            j=i-3
            if bars[j][2]==max(b[2] for b in bars[j-3:j+4]): swH.append(bars[j][2])
            if bars[j][3]==min(b[3] for b in bars[j-3:j+4]): swL.append(bars[j][3])
        if pos:
            s=pos['side']; q=pos['q']; stp=pos['stp']
            # stop first
            if (s==1 and l<=stp) or (s==-1 and h>=stp):
                x=stp-s*TICK; pnl=(x-pos['e'])*s*q*PV-2*COMM*q-TICK*PV*q; pos['pnl']+=pnl; pos['why']='be' if pos['tp1'] else 'stop'; pos['xi']=i; trades.append(pos); dayPnl+=pos['pnl'];
                if pos['pnl']<0: losses+=1; consec+=1
                else: consec=0
                pos=None; continue
            if not pos['tp1'] and ((s==1 and h>=pos['tp1p']) or (s==-1 and l<=pos['tp1p'])):
                q1=pos['q1']; x=pos['tp1p']; pos['pnl']+=(x-pos['e'])*s*q1*PV-2*COMM*q1; pos['q']=q-q1; pos['tp1']=True
                if P['be']: pos['stp']=pos['e'] + s*P['beOff']
                if pos['q']==0: pos['why']='tp1only'; pos['xi']=i; trades.append(pos); dayPnl+=pos['pnl']; consec=0; pos=None; continue
                q=pos['q']; stp=pos['stp']
            if pos['tp1'] or P['tp1pts']==0:
                if pos['tgt'] is not None and ((s==1 and h>=pos['tgt']) or (s==-1 and l<=pos['tgt'])):
                    x=pos['tgt']; pos['pnl']+=(x-pos['e'])*s*q*PV-2*COMM*q; pos['why']='target'; pos['xi']=i; trades.append(pos); dayPnl+=pos['pnl']; consec=0; pos=None; continue
                if P['trail']>0 and pos['tp1']:
                    ex=min(b[3] for b in bars[max(pos['i'],i-P['trail']+1):i+1]) if s==1 else max(b[2] for b in bars[max(pos['i'],i-P['trail']+1):i+1])
                    pos['stp']=max(pos['stp'],ex-TICK) if s==1 else min(pos['stp'],ex+TICK)
            if (i-pos['i'])>=P['maxHold'] or t>=955:
                x=c; pos['pnl']+=(x-pos['e'])*s*q*PV-2*COMM*q; pos['why']='time' if t<955 else 'close'; pos['xi']=i; trades.append(pos); dayPnl+=pos['pnl']
                if pos['pnl']<0: losses+=1; consec+=1
                else: consec=0
                pos=None
            continue
        # pending stop order (valid 1 bar)
        if pend:
            pp=pend; pend=None
            if (pp['side']==1 and h>=pp['lvl']) or (pp['side']==-1 and l<=pp['lvl']):
                e0=(max(o,pp['lvl']) if pp['side']==1 else min(o,pp['lvl']))+pp['side']*TICK
                r=abs(e0-pp['stp'])
                if r<P['minStop']: pp['stp']=e0-pp['side']*P['minStop']; r=P['minStop']
                if r<=P['maxStop']:
                    tgt=None
                    if P['runner']=='level':
                        lv=[x for x in ([pd[0],pd[1],pd[2]] if pd else [])+[orh,orl]+swH+swL if (x-e0)*pp['side']>=P['minRoom']]
                        if lv: tgt=min(lv) if pp['side']==1 else max(lv)
                        if tgt is None or abs(tgt-e0)>P['runR']*r: tgt=e0+pp['side']*P['runR']*r
                    else: tgt=e0+pp['side']*P['runR']*r
                    pos=dict(side=pp['side'],e=e0,stp=pp['stp'],q=2,q1=1 if P['tp1pts']>0 else 0,tp1=False,tp1p=e0+pp['side']*(P['tp1pts'] if P['tp1mode']=='pts' else P['tp1pts']*r),tgt=tgt,i=i,pnl=0,r=r,lvl=pp['name'])
                    ntr+=1
                    # same-bar stop
                    if (pos['side']==1 and l<=pos['stp']) or (pos['side']==-1 and h>=pos['stp']):
                        x=pos['stp']-pos['side']*TICK; pos['pnl']=(x-e0)*pos['side']*2*PV-2*COMM*2-TICK*PV*2; pos['why']='stop'; pos['xi']=i; trades.append(pos); dayPnl+=pos['pnl']; losses+=1; consec+=1; pos=None
                    continue
        if t<P['first'] or t>P['last'] or ntr>=P['maxTr'] or losses>=P['maxLoss'] or consec>=P['maxConsec'] or dayPnl<=-P['dayStop'] or dayPnl>=P['dayTgt']: continue
        # signal bar with bias at a level
        s=side; bb=bars[i]; r=h-l; body=abs(c-o)
        if r<=0: continue
        sig = (c>o and (c-l)>=P['sigFrac']*r and body>=P['sigBody']*r) if s==1 else (c<o and (h-c)>=P['sigFrac']*r and body>=P['sigBody']*r)
        if not sig: continue
        # key level test: pullback low (last 3 bars) within D of a level, level must be below (long) i.e. support
        D=P['lvlD']*rng[i]; pbExt=min(b[3] for b in bars[i-2:i+1]) if s==1 else max(b[2] for b in bars[i-2:i+1])
        levels=[]
        if 'OR' in P['levels']: levels+= [('ORH',orh),('ORL',orl)]
        if 'VWAP' in P['levels']: levels.append(('VWAP',vw[i]))
        if 'EMA' in P['levels']: levels.append(('EMA',ema[i]))
        if 'PD' in P['levels'] and pd: levels+=[('PDH',pd[0]),('PDL',pd[1]),('PDC',pd[2])]
        if 'SW' in P['levels']: levels+=[('SWH',x) for x in swH[-5:]]+[('SWL',x) for x in swL[-5:]]
        hit=None
        for nm,lv in levels:
            if lv is None: continue
            if abs(pbExt-lv)<=D and ((s==1 and c>lv) or (s==-1 and c<lv)): hit=nm; break
        if not hit: continue
        # pullback requirement: price must have pulled back >= pbMin pts from the recent extreme (last 20 bars) in bias dir
        ext=max(b[2] for b in bars[max(0,i-20):i]) if s==1 else min(b[3] for b in bars[max(0,i-20):i])
        if (ext-pbExt if s==1 else pbExt-ext)<P['pbMin']: continue
        stp=(pbExt-P['bufT']*TICK) if s==1 else (pbExt+P['bufT']*TICK)
        pend=dict(side=s,lvl=(h+TICK) if s==1 else (l-TICK),stp=stp,name=hit)
    return trades

def evaluate(P,a,z):
    tot=0;n=0;w=0;gp=gl=0;g=r=0;worst=0;eq=0;peak=0;dd=0;tpd=[]
    for di,(d,bars) in enumerate(days):
        if d<a or d>z: continue
        tr=run(di,P); p=sum(t['pnl'] for t in tr); tot+=p; n+=len(tr); tpd.append(len(tr))
        for t in tr:
            if t['pnl']>0: w+=1; gp+=t['pnl']
            else: gl-=t['pnl']
        if tr:
            if p>0: g+=1
            elif p<0: r+=1
        worst=min(worst,p); eq+=p; peak=max(peak,eq); dd=max(dd,peak-eq)
    return dict(net=round(tot),n=n,win=round(100*w/max(n,1)),pf=round(gp/max(gl,1),2),g=g,r=r,worst=round(worst),dd=round(dd),tpd=round(sum(tpd)/max(len(tpd),1),2))

BASE=dict(first=585,last=840,maxTr=4,maxLoss=3,maxConsec=2,dayStop=600,dayTgt=1e9,sigFrac=.5,sigBody=.3,lvlD=1.0,levels=('OR','VWAP','EMA','PD','SW'),pbMin=10,bufT=4,minStop=8,maxStop=30,tp1pts=10,tp1mode='pts',be=True,beOff=0,runner='level',runR=2,minRoom=15,trail=0,maxHold=60)
if __name__=='__main__':
    DEV=('20260601','20261020'); HO1=('20260101','20260531'); HO2=('20220101','20251231')
    grid=[]
    for tp1,maxStop,runR,trail,mh,lvlD,levels in itertools.product([10,15,0],[20,30,45],[2,3],[0,3],[30,60],[0.75,1.5],[('OR','VWAP','EMA','PD','SW'),('OR','PD','SW'),('EMA','VWAP')]):
        P=dict(BASE); P.update(tp1pts=tp1,maxStop=maxStop,runR=runR,trail=trail,maxHold=mh,lvlD=lvlD,levels=levels); grid.append(P)
    print('grid',len(grid)); res=[]
    for P in grid:
        e=evaluate(P,*DEV); res.append((e,P))
    res.sort(key=lambda x:(x[0]['pf'] if x[0]['n']>=25 else 0, x[0]['net']),reverse=True)
    print('\nTOP 12 on DEV (Jun-Oct 2026), with holdouts:')
    for e,P in res[:12]:
        h1=evaluate(P,*HO1); h2=evaluate(P,*HO2)
        print(f"DEV net {e['net']:+6d} n{e['n']:3d} win{e['win']}% PF{e['pf']} G/R {e['g']}/{e['r']} worst{e['worst']} DD{e['dd']} | JanMay26 PF{h1['pf']} net{h1['net']:+d} G/R{h1['g']}/{h1['r']} | 22-25 PF{h2['pf']} net{h2['net']:+d} G/R{h2['g']}/{h2['r']} || tp1 {P['tp1pts']} stop<={P['maxStop']} run {P['runR']}R trail{P['trail']} hold{P['maxHold']} lvlD{P['lvlD']} {'/'.join(P['levels'])}")
    print('\nmedian config on DEV:', res[len(res)//2][0])
    json.dump([(e,{k:(list(v) if isinstance(v,tuple) else v) for k,v in P.items()}) for e,P in res[:12]],open('/home/claude/mnq-quant/scripts/v4_scalper_top.json','w'))
