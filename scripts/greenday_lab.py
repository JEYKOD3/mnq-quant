#!/usr/bin/env python3
"""Green-day lab on MNQ RTH 1m (Databento).
A) swing ceiling per day: how many 'good movements' (zigzag swings >= T pts) exist, by day type, by hour.
B) executable Wade-lite second-entry (H2/L2 at EMA21) with 1-tick triggers, cost 3 pts/trade, variants of target & trade caps.
Prints compact tables. Usage: python3 greenday_lab.py [year_from]
"""
import sys, math, collections
RAW='/home/claude/mnq-quant/data/raw/mnq_rth_1m.txt'
YFROM=int(sys.argv[1]) if len(sys.argv)>1 else 2022
COST=3.0   # pts round trip (commission 2.37 + slip)

days=[]
for line in open(RAW):
    line=line.strip()
    if not line: continue
    parts=line.split('|'); d=parts[0]
    if int(d[:4])<YFROM: continue
    bars=[]
    for p in parts[1:]:
        t,o,h,l,c=p.split(','); t=int(t)
        bars.append((t//100*60+t%100,int(o)/4,int(h)/4,int(l)/4,int(c)/4))
    if len(bars)>300: days.append((d,bars))
print('days',len(days),days[0][0],days[-1][0])

# ---------- day features ----------
def dayfeat(bars):
    ib=[b for b in bars if b[0]<630]           # 9:30-10:29
    ibh=max(b[2] for b in ib); ibl=min(b[3] for b in ib)
    hi=max(b[2] for b in bars); lo=min(b[3] for b in bars)
    o=bars[0][1]; c=bars[-1][4]; rng=hi-lo
    cl=(c-lo)/rng if rng>0 else .5
    return dict(ib=ibh-ibl,rng=rng,cl=cl,o=o,c=c,ratio=rng/max(ibh-ibl,1))
feats={}
prev=None; adr=collections.deque(maxlen=10)
for d,bars in days:
    f=dayfeat(bars); f['adr']=sum(adr)/len(adr) if adr else f['rng']
    f['type']='TREND' if (f['ratio']>=2.0 and (f['cl']>=.8 or f['cl']<=.2)) else ('RANGE' if f['ratio']<=1.3 else 'MID')
    feats[d]=f; adr.append(f['rng'])
tc=collections.Counter(f['type'] for f in feats.values())
print('day types',dict(tc), 'share', {k:round(v/len(feats),2) for k,v in tc.items()})

# ---------- A) zigzag swings ----------
def zigzag(bars,T):
    # returns list of (start_min,end_min,size_pts,dir)
    sw=[]; dirn=0; ext=bars[0][2]; extT=bars[0][0]; piv=bars[0][3]; pivT=bars[0][0]
    # start: find first move >= T
    hi=bars[0][2]; lo=bars[0][3]; hiT=loT=bars[0][0]
    for t,o,h,l,c in bars:
        if dirn==0:
            if h>hi: hi,hiT=h,t
            if l<lo: lo,loT=l,t
            if h-lo>=T and loT<=hiT: dirn=1; piv,pivT=lo,loT; ext,extT=h,t
            elif hi-l>=T and hiT<=loT: dirn=-1; piv,pivT=hi,hiT; ext,extT=l,t
        elif dirn==1:
            if h>ext: ext,extT=h,t
            elif ext-l>=T:
                sw.append((pivT,extT,ext-piv,1)); dirn=-1; piv,pivT=ext,extT; ext,extT=l,t
        else:
            if l<ext: ext,extT=l,t
            elif h-ext>=T:
                sw.append((pivT,extT,piv-ext,-1)); dirn=1; piv,pivT=ext,extT; ext,extT=h,t
    if dirn!=0: sw.append((pivT,extT,abs(ext-piv),dirn))
    return sw

for T in (15,25,40):
    per=collections.defaultdict(list); hour=collections.Counter(); cnt=[]
    for d,bars in days:
        sw=zigzag(bars,T); cnt.append(len(sw)); per[feats[d]['type']].append(len(sw))
        for s in sw: hour[s[0]//60]+=1
    cnt.sort()
    print(f'\nZZ T={T}pts: swings/day median {cnt[len(cnt)//2]} p25 {cnt[len(cnt)//4]} p75 {cnt[3*len(cnt)//4]} | by type:',
          {k:round(sum(v)/len(v),1) for k,v in per.items()}, '| swing starts by hour ET:', {h:hour[h] for h in sorted(hour)})

# ---------- B) Wade-lite H2/L2 at EMA21, 1m ----------
def ema_series(bars,n=21):
    k=2/(n+1); e=None; out=[]
    for b in bars:
        e=b[4] if e is None else e+k*(b[4]-e); out.append(e)
    return out

def run(bars,tgtR=2.0,minTgt=0.0,maxTr=99,first=585,last=930,flat=955,emaD=None,minStop=8,maxStop=40,sigBody=.3,useFirst=False,dayStop=None):
    """H2/L2: bias = ema slope sign over 10 bars & close side. Count legs against bias with 1-tick break rule.
    entry stop order 1 tick beyond signal bar (with-bias bar, body>=sigBody*range, close in with-bias half), bar within emaD pts of EMA."""
    ema=ema_series(bars); n=len(bars); tick=.25
    rng20=[0]*n
    for i in range(n): rng20[i]=sum(b[2]-b[3] for b in bars[max(0,i-19):i+1])/min(20,i+1)
    trades=[]; pos=0; entry=stp=tgt=0; q=0
    # leg state
    bias=0; cnt=0; legExt=None; inLeg=False; lastExt=None; pendE=None
    pnl=0.0
    for i in range(1,n):
        t,o,h,l,c=bars[i]
        # manage open position (stop first)
        if pos!=0:
            if pos==1:
                if l<=stp: pnl+=stp-entry-COST; trades.append((stp-entry-COST,t)); pos=0
                elif h>=tgt: pnl+=tgt-entry-COST; trades.append((tgt-entry-COST,t)); pos=0
            else:
                if h>=stp: pnl+=entry-stp-COST; trades.append((entry-stp-COST,t)); pos=0
                elif l<=tgt: pnl+=entry-tgt-COST; trades.append((entry-tgt-COST,t)); pos=0
            if pos!=0 and t>=flat:
                x=c; pnl+=(x-entry if pos==1 else entry-x)-COST; trades.append(((x-entry if pos==1 else entry-x)-COST,t)); pos=0
        # pending entry fills on this bar
        if pos==0 and pendE is not None and t<flat:
            side,e,s,g=pendE
            if side==1 and h>=e:
                pos=1; entry=e+tick; stp=s; tgt=entry+g; pendE=None
                if l<=stp: pnl+=stp-entry-COST; trades.append((stp-entry-COST,t)); pos=0
            elif side==-1 and l<=e:
                pos=-1; entry=e-tick; stp=s; tgt=entry-g; pendE=None
                if h>=stp: pnl+=entry-stp-COST; trades.append((entry-stp-COST,t)); pos=0
            else: pendE=None   # one-bar validity
        # bias
        nb = 1 if (i>=10 and ema[i]>ema[i-10] and c>ema[i]) else (-1 if (i>=10 and ema[i]<ema[i-10] and c<ema[i]) else 0)
        if nb!=bias:
            bias=nb; cnt=0; inLeg=False; legExt=None
            lastExt = h if bias==1 else l
        if bias==0: continue
        # new extreme resets count
        if bias==1 and h>lastExt: lastExt=h; cnt=0; inLeg=False; legExt=None; continue
        if bias==-1 and l<lastExt: lastExt=l; cnt=0; inLeg=False; legExt=None; continue
        # leg tracking against bias: a pullback leg is alive until price breaks 1 tick beyond prior bar's with-bias side
        ph,pl=bars[i-1][2],bars[i-1][3]
        if bias==1:
            if l<pl: inLeg=True          # pullback continues (lower low)
            if inLeg and h>ph+0*tick:    # break above prior bar high = trigger
                cnt+=1; inLeg=False
                if (cnt==2 or (useFirst and cnt==1)) and pos==0 and first<=t<=last and len([x for x in trades if x[1]>=0])<maxTr:
                    sb=bars[i-1]; body=abs(sb[4]-sb[1]); r=sb[2]-sb[3]
                    d=(emaD if emaD is not None else .5*rng20[i])
                    ok = sb[4]>sb[1] and r>0 and body>=sigBody*r and (sb[4]-sb[3])>=.5*r and (sb[3]-ema[i-1])<=d
                    if ok:
                        e=sb[2]+tick; s=sb[3]-tick; R=e+tick-s
                        if R<minStop: s=e+tick-minStop; R=minStop
                        if R<=maxStop:
                            g=max(tgtR*R,minTgt)
                            # fill on this same bar since it already broke the high
                            pos=1; entry=e+tick; stp=s; tgt=entry+g
                            if l<=stp and False: pass
        else:
            if h>ph: inLeg=True
            if inLeg and l<pl:
                cnt+=1; inLeg=False
                if (cnt==2 or (useFirst and cnt==1)) and pos==0 and first<=t<=last and len([x for x in trades if x[1]>=0])<maxTr:
                    sb=bars[i-1]; body=abs(sb[4]-sb[1]); r=sb[2]-sb[3]
                    d=(emaD if emaD is not None else .5*rng20[i])
                    ok = sb[4]<sb[1] and r>0 and body>=sigBody*r and (sb[2]-sb[4])>=.5*r and (ema[i-1]-sb[2])<=d
                    if ok:
                        e=sb[3]-tick; s=sb[2]+tick; R=s-(e-tick)
                        if R<minStop: s=e-tick+minStop; R=minStop
                        if R<=maxStop:
                            g=max(tgtR*R,minTgt)
                            pos=-1; entry=e-tick; stp=s; tgt=entry-g
        if dayStop is not None and pnl<=-dayStop:
            if pos!=0: x=c; pnl+=(x-entry if pos==1 else entry-x)-COST; trades.append(((x-entry if pos==1 else entry-x)-COST,t)); pos=0
            break
    return trades

def report(name,fn):
    tot=0; n=0; g=r=0; wins=0; gp=gl=0; byY=collections.defaultdict(lambda:[0,0,0]); byT=collections.defaultdict(lambda:[0,0,0]); tpd=[]
    for d,bars in days:
        tr=fn(bars); p=sum(x[0] for x in tr); tot+=p; n+=len(tr); tpd.append(len(tr))
        for x in tr:
            if x[0]>0: wins+=1; gp+=x[0]
            else: gl-=x[0]
        y=d[:4]; byY[y][0]+=p; byY[y][1]+= (1 if p>0 else 0); byY[y][2]+=(1 if p<0 else 0)
        ty=feats[d]['type']; byT[ty][0]+=p; byT[ty][1]+=(1 if p>0 else 0); byT[ty][2]+=(1 if p<0 else 0)
        if p>0: g+=1
        elif p<0: r+=1
    tpd.sort()
    print(f'\n== {name}: net {tot:+.0f} pts (${tot*2:+.0f}) trades {n} ({n/len(days):.1f}/day, median {tpd[len(tpd)//2]}) win {wins/max(n,1):.0%} PF {gp/max(gl,1):.2f} green/red days {g}/{r} ({g/max(g+r,1):.0%})')
    print('   by year:',{y:(round(v[0]),f'{v[1]}/{v[2]}') for y,v in sorted(byY.items())})
    print('   by type:',{y:(round(v[0]),f'{v[1]}/{v[2]}') for y,v in sorted(byT.items())})

report('H2 EMA21 1m, tgt 2R, cost3',            lambda b: run(b,tgtR=2.0))
report('H2 EMA21 1m, tgt 1R, cost3',            lambda b: run(b,tgtR=1.0))
report('H2 EMA21 1m, tgt 1R min25pts',          lambda b: run(b,tgtR=1.0,minTgt=25))
report('H2 EMA21 1m, tgt 2R min25pts',          lambda b: run(b,tgtR=2.0,minTgt=25))
report('H2 EMA21 1m, tgt 2R, max 5 tr/day',     lambda b: run(b,tgtR=2.0,maxTr=5))
report('H2 EMA21 1m, tgt 2R, day stop -40pts',  lambda b: run(b,tgtR=2.0,dayStop=40))
report('H1+H2 (first entries too), tgt 2R',     lambda b: run(b,tgtR=2.0,useFirst=True))
report('H2 EMA21 1m, tgt 2R, 9:45-11:30 only',  lambda b: run(b,tgtR=2.0,last=690))
report('H2 EMA21 1m, tgt 2R, cost 0 (ceiling)', lambda b: [(x[0]+COST,x[1]) for x in run(b,tgtR=2.0)])
