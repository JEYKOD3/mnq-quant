"""Version de l'ami: box = mother bar (haut/bas). Apres un inside bar, entree a la cloture de la premiere bougie dont le CORPS entier (open et close) sort de la box dans le sens de la tendance; stop = autre cote de la box; cible 2:1. 5m MNQ. cout 3pt."""
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
def run(d,bars,tf=5,tgtR=2.0,trend='ema',first=585,last=870,flat=955,maxStop=80,maxTr=3,maxWait=6,both=True):
    B=agg(bars,tf); n=len(B); k=2/22; e=None; ema=[]
    for b in B: e=b[4] if e is None else e+k*(b[4]-e); ema.append(e)
    bias=v4(d) if trend=='v4' else 0
    if trend=='v4' and bias==0: return []
    trades=[]; pos=0; box=None; ntr=0
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
        if t<first or t>last or ntr>=maxTr: continue
        # new box when an inside bar appears
        m=B[i-1]; ib=B[i]
        if ib[2]<=m[2] and ib[3]>=m[3] and (m[2]-m[3])>0:
            if trend=='ema': dirn = 1 if (ema[i]>ema[i-6] and c>ema[i]) else (-1 if (ema[i]<ema[i-6] and c<ema[i]) else 0)
            else: dirn=bias
            if dirn!=0: box=(m[2],m[3],dirn,i)
            continue
        if box:
            hi,lo,dirn,bi=box
            if i-bi>maxWait: box=None; continue
            # body fully outside in trend direction
            if dirn==1 and min(o,c)>hi:
                entry=c; stp=lo-tick; R=entry-stp
                if R<=maxStop: pos=1; tgt=entry+tgtR*R; ntr+=1
                box=None
            elif dirn==-1 and max(o,c)<lo:
                entry=c; stp=hi+tick; R=stp-entry
                if R<=maxStop: pos=-1; tgt=entry-tgtR*R; ntr+=1
                box=None
            elif (dirn==1 and max(o,c)<lo) or (dirn==-1 and min(o,c)>hi): box=None   # broke the wrong way: cancel
    return trades
def rep(name,**kw):
    tot=0;n=0;w=0;gp=gl=0;g=r=0;byY=collections.defaultdict(lambda:[0,0,0])
    for d,bars in days:
        tr=run(d,bars,**kw); p=sum(tr); tot+=p; n+=len(tr)
        for x in tr:
            if x>0: w+=1; gp+=x
            else: gl-=x
        if tr: y=d[:4]; byY[y][0]+=p; byY[y][1]+=(p>0); byY[y][2]+=(p<0); g+=(p>0); r+=(p<0)
    print(f'{name:44s} net {tot:+7.0f}pt n={n:5d} win {w/max(n,1):.0%} PF {gp/max(gl,1):.2f} G/R {g}/{r} ({g/max(g+r,1):.0%}) | '+' '.join(f"{y[2:]}:{round(v[0])}({v[1]}/{v[2]})" for y,v in sorted(byY.items())))
rep('5m, tendance EMA, corps hors box, 2:1')
rep('5m, tendance EMA, 1.5:1',tgtR=1.5)
rep('5m, tendance EMA, 3:1',tgtR=3)
rep('5m, direction V4 seulement, 2:1',trend='v4')
rep('15m, tendance EMA, 2:1',tf=15,maxStop=120)
rep('15m, direction V4, 2:1',tf=15,trend='v4',maxStop=120)
rep('5m, EMA, 1 trade/jour',maxTr=1)
