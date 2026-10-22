"""Reddit r/LucidProp strategy check: 5m, 9 EMA cross entries, exit on opposite cross (or EOD). Variants: all day both ways; after 10:30 only with D2 side; min bar body filter; 15m-direction filter."""
import sys,collections
sys.argv=['x','2022']; src=open('scripts/greenday_lab.py').read(); exec(src.split('# ---------- A) zigzag')[0])
COST=3.0
def agg(bars,n): return [(bars[i][0],bars[i][1],max(b[2] for b in bars[i:i+n]),min(b[3] for b in bars[i:i+n]),bars[i+n-1][4]) for i in range(0,len(bars)-n+1,n)]
def ema(B,n):
    k=2/(n+1); e=None; o=[]
    for b in B: e=b[4] if e is None else e+k*(b[4]-e); o.append(e)
    return o
def run(bars,adr,first=585,useD2=False,X=.4,stopPts=None,body=0.0,flat=955,trend15=False):
    B=agg(bars,5); e9=ema(B,9); n=len(B); trades=[]; pos=0; entry=0
    side=0
    if useD2:
        ib=[b for b in bars if b[0]<630]; mv=(ib[-1][4]-bars[0][1])/adr
        if abs(mv)<X: return []
        side=1 if mv>0 else -1; first=max(first,630)
    B15=agg(bars,15); e15=ema(B15,9)
    for i in range(1,n):
        t,o,h,l,c=B[i]
        if pos!=0:
            crossed = (pos==1 and c<e9[i]) or (pos==-1 and c>e9[i])
            stopped = stopPts and ((pos==1 and l<=entry-stopPts) or (pos==-1 and h>=entry+stopPts))
            if stopped: trades.append(-stopPts-COST); pos=0
            elif crossed or t>=flat: trades.append((c-entry if pos==1 else entry-c)-COST); pos=0
            if pos!=0: continue
        if t<first or t>=flat: continue
        up = c>e9[i] and B[i-1][4]<=e9[i-1]; dn = c<e9[i] and B[i-1][4]>=e9[i-1]
        if body>0 and abs(c-o)<body*(h-l): continue
        if trend15:
            j=(i//3)-1
            if j<0: continue
            
            if up and not (B15[j][4]>e15[j]): up=False
            if dn and not (B15[j][4]<e15[j]): dn=False
        if up and (side>=0): pos=1; entry=c
        elif dn and (side<=0): pos=-1; entry=c
    return trades
def rep(name,**kw):
    tot=0;n=0;w=0;gp=gl=0;g=r=0;byY=collections.defaultdict(lambda:[0,0,0])
    for d,bars in days:
        tr=run(bars,feats[d]['adr'],**kw); p=sum(tr); tot+=p; n+=len(tr)
        for x in tr:
            if x>0: w+=1; gp+=x
            else: gl-=x
        if tr: y=d[:4]; byY[y][0]+=p; byY[y][1]+=(p>0); byY[y][2]+=(p<0); g+=(p>0); r+=(p<0)
    print(f'{name:42s} net {tot:+7.0f}pt n={n:5d} ({n/len(days):.1f}/day) win {w/max(n,1):.0%} PF {gp/max(gl,1):.2f} G/R {g}/{r} ({g/max(g+r,1):.0%}) | '+' '.join(f"{y[2:]}:{round(v[0])}({v[1]}/{v[2]})" for y,v in sorted(byY.items())))
rep('EMA9 cross both ways 9:45-15:55')
rep('EMA9 cross, body>=50%',body=.5)
rep('EMA9 cross + 15m EMA9 direction',trend15=True)
rep('EMA9 cross after 10:30, D2 side only',useD2=True)
rep('EMA9 cross D2 side + 15m dir',useD2=True,trend15=True)
rep('EMA9 cross D2 side, 40pt stop',useD2=True,stopPts=40)
rep('EMA9 cross cost 0 (ceiling)',**{}) if False else None
