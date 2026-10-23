"""Friend's strategy: inside bar after a trend, buy stop 1 tick above inside-bar high (sell below low). 5m MNQ RTH.
Trend = EMA21 slope over 6 bars & close on EMA side (or V4 bias). Stop = inside bar low - 1tk (or mother bar low). Target R mult. cost 3pt."""
import sys,collections,json
sys.argv=['x','2022']; src=open('scripts/greenday_lab.py').read(); exec(src.split('# ---------- A) zigzag')[0])
feat=json.load(open('data/features/day_features.json')); COST=3.0; tick=.25
def v4(d):
    f=feat.get(d)
    if not f or f['pdRel']>1.2: return 0
    G=abs(f['gap'])>=.6; D=abs(f['orDir'])>=.6
    if not(G or D): return 0
    return (1 if f['gap']>0 else -1) if G else (1 if f['orDir']>0 else -1)
def agg(bars,n): return [(bars[i][0],bars[i][1],max(b[2] for b in bars[i:i+n]),min(b[3] for b in bars[i:i+n]),bars[i+n-1][4]) for i in range(0,len(bars)-n+1,n)]
def run(d,bars,tf=5,tgtR=2.0,stopMode='ib',trend='ema',first=585,last=870,flat=955,minStop=8,maxStop=60,maxTr=3,both=True):
    B=agg(bars,tf); n=len(B); k=2/22; e=None; ema=[]
    for b in B: e=b[4] if e is None else e+k*(b[4]-e); ema.append(e)
    bias=v4(d) if trend=='v4' else 0
    if trend=='v4' and bias==0: return []
    trades=[]; pos=0; pend=None; ntr=0
    for i in range(2,n):
        t,o,h,l,c=B[i]
        if pos!=0:
            if pos==1:
                if l<=stp: trades.append(stp-entry-COST); pos=0
                elif h>=tgt: trades.append(tgt-entry-COST); pos=0
            else:
                if h>=stp: trades.append(entry-stp-COST); pos=0
                elif l<=tgt: trades.append(entry-tgt-COST); pos=0
            if pos!=0 and t>=flat: trades.append((c-entry if pos==1 else entry-c)-COST); pos=0
            if pos!=0: continue
        if pend:
            s,lvl,st=pend; pend=None
            if (s==1 and h>=lvl) or (s==-1 and l<=lvl):
                entry=lvl+s*tick; R=abs(entry-st)
                if R<minStop: st=entry-s*minStop; R=minStop
                if R<=maxStop:
                    pos=s; stp=st; tgt=entry+s*tgtR*R; ntr+=1
                    if (s==1 and l<=stp) or (s==-1 and h>=stp): trades.append(-R-COST); pos=0
                continue
        if t<first or t>last or ntr>=maxTr: continue
        m=B[i-1]; ib=B[i]
        if not (ib[2]<=m[2] and ib[3]>=m[3] and (m[2]-m[3])>0): continue   # inside bar (wicks included)
        if trend=='ema':
            up = ema[i]>ema[i-6] and c>ema[i]; dn = ema[i]<ema[i-6] and c<ema[i]
        else:
            up = bias==1; dn = bias==-1
        if up: pend=(1, ib[2], (ib[3] if stopMode=='ib' else m[3])-tick)
        elif dn and both: pend=(-1, ib[3], (ib[2] if stopMode=='ib' else m[2])+tick)
    return trades
def rep(name,**kw):
    tot=0;n=0;w=0;gp=gl=0;g=r=0;byY=collections.defaultdict(lambda:[0,0,0])
    for d,bars in days:
        tr=run(d,bars,**kw); p=sum(tr); tot+=p; n+=len(tr)
        for x in tr:
            if x>0: w+=1; gp+=x
            else: gl-=x
        if tr: y=d[:4]; byY[y][0]+=p; byY[y][1]+=(p>0); byY[y][2]+=(p<0); g+=(p>0); r+=(p<0)
    print(f'{name:46s} net {tot:+7.0f}pt n={n:5d} win {w/max(n,1):.0%} PF {gp/max(gl,1):.2f} G/R {g}/{r} ({g/max(g+r,1):.0%}) | '+' '.join(f"{y[2:]}:{round(v[0])}({v[1]}/{v[2]})" for y,v in sorted(byY.items())))
rep('5m, EMA trend, stop IB low, 2R')
rep('5m, EMA trend, stop IB low, 1R',tgtR=1)
rep('5m, EMA trend, stop mother bar, 2R',stopMode='mother')
rep('5m, EMA trend, stop mother bar, 3R',stopMode='mother',tgtR=3)
rep('5m, V4 bias only, stop IB, 2R',trend='v4')
rep('5m, V4 bias only, stop mother, 2R',trend='v4',stopMode='mother')
rep('15m, EMA trend, stop IB, 2R',tf=15,maxStop=90)
rep('15m, V4 bias, stop mother, 2R',tf=15,trend='v4',stopMode='mother',maxStop=90)
rep('1m, EMA trend, stop IB, 2R',tf=1,maxStop=30)
