"""E11: 5m H2/L2 at EMA21, after 10:30, only on days with D2 move>=X ADR by 10:30 and in that direction; spike prereq (2 consecutive trend bars body>=.5r in bias dir within last 8 bars); exits: 2R / 25pt min / runner trail."""
import sys,collections
sys.argv=['x','2022']; src=open('scripts/greenday_lab.py').read(); exec(src.split('# ---------- A) zigzag')[0])
COST=3.0
def agg(bars,n): return [(bars[i][0],bars[i][1],max(b[2] for b in bars[i:i+n]),min(b[3] for b in bars[i:i+n]),bars[i+n-1][4]) for i in range(0,len(bars)-n+1,n)]
def ema_series(bars,n=21):
    k=2/(n+1); e=None; out=[]
    for b in bars: e=b[4] if e is None else e+k*(b[4]-e); out.append(e)
    return out
def run(bars,adr,X=0.4,spike=True,tgtR=2.0,minTgt=25,trail=False,emaD=0.5,minStop=10,maxStop=60,maxTr=2,first=630,last=870,flat=955,sigFrac=.5,sigBody=.3,forceSide=True):
    b1=[b for b in bars if b[0]<630]
    if len(b1)<50: return []
    o=bars[0][1]; mv=(b1[-1][4]-o)/adr
    if abs(mv)<X: return []
    side=1 if mv>0 else -1
    B=agg(bars,5); ema=ema_series(B); n=len(B); tick=.25
    rng20=[sum(b[2]-b[3] for b in B[max(0,i-19):i+1])/min(20,i+1) for i in range(n)]
    trades=[]; pos=0; entry=stp=tgt=0; cnt=0; inLeg=False; lastExt=None; bias=0; ntr=0; hiSince=loSince=None
    for i in range(1,n):
        t,oo,h,l,c=B[i]
        if pos!=0:
            if pos==1:
                if l<=stp: trades.append(stp-entry-COST); pos=0
                elif (not trail) and h>=tgt: trades.append(tgt-entry-COST); pos=0
                else:
                    if trail:
                        hiSince=max(hiSince,h)
                        if hiSince-entry>=R0: stp=max(stp, min(B[i-1][3],l)-tick)   # trail under last 2-bar low once +1R
            else:
                if h>=stp: trades.append(entry-stp-COST); pos=0
                elif (not trail) and l<=tgt: trades.append(entry-tgt-COST); pos=0
                else:
                    if trail:
                        loSince=min(loSince,l)
                        if entry-loSince>=R0: stp=min(stp, max(B[i-1][2],h)+tick)
            if pos!=0 and t>=flat: trades.append((c-entry if pos==1 else entry-c)-COST); pos=0
            if pos!=0: continue
        nb = 1 if (i>=10 and ema[i]>ema[i-10] and c>ema[i]) else (-1 if (i>=10 and ema[i]<ema[i-10] and c<ema[i]) else 0)
        if forceSide and nb!=side: nb=0
        if nb!=bias: bias=nb; cnt=0; inLeg=False; lastExt = h if bias==1 else l
        if bias==0: continue
        if bias==1 and h>lastExt: lastExt=h; cnt=0; inLeg=False; continue
        if bias==-1 and l<lastExt: lastExt=l; cnt=0; inLeg=False; continue
        ph,pl=B[i-1][2],B[i-1][3]
        def spikeOK():
            if not spike: return True
            w=B[max(0,i-9):i-1]
            for j in range(1,len(w)):
                a,b=w[j-1],w[j]
                if bias==1 and a[4]>a[1] and b[4]>b[1] and (a[4]-a[1])>=.5*(a[2]-a[3]) and (b[4]-b[1])>=.5*(b[2]-b[3]): return True
                if bias==-1 and a[4]<a[1] and b[4]<b[1] and (a[1]-a[4])>=.5*(a[2]-a[3]) and (b[1]-b[4])>=.5*(b[2]-b[3]): return True
            return False
        if bias==1:
            if l<pl: inLeg=True
            if inLeg and h>ph:
                cnt+=1; inLeg=False
                if cnt==2 and ntr<maxTr and first<=t<=last and spikeOK():
                    sb=B[i-1]; body=abs(sb[4]-sb[1]); r=sb[2]-sb[3]
                    ok = sb[4]>sb[1] and r>0 and body>=sigBody*r and (sb[4]-sb[3])>=sigFrac*r and (sb[3]-ema[i-1])<=emaD*rng20[i]
                    if ok:
                        e=sb[2]+tick; s=sb[3]-tick; R=e+tick-s
                        if R<minStop: s=e+tick-minStop; R=minStop
                        if R<=maxStop:
                            pos=1; entry=e+tick; stp=s; R0=R; tgt=entry+max(tgtR*R,minTgt); ntr+=1; hiSince=h
        else:
            if h>ph: inLeg=True
            if inLeg and l<pl:
                cnt+=1; inLeg=False
                if cnt==2 and ntr<maxTr and first<=t<=last and spikeOK():
                    sb=B[i-1]; body=abs(sb[4]-sb[1]); r=sb[2]-sb[3]
                    ok = sb[4]<sb[1] and r>0 and body>=sigBody*r and (sb[2]-sb[4])>=sigFrac*r and (ema[i-1]-sb[2])<=emaD*rng20[i]
                    if ok:
                        e=sb[3]-tick; s=sb[2]+tick; R=s-(e-tick)
                        if R<minStop: s=e-tick+minStop; R=minStop
                        if R<=maxStop:
                            pos=-1; entry=e-tick; stp=s; R0=R; tgt=entry-max(tgtR*R,minTgt); ntr+=1; loSince=l
    return trades
def rep(name,**kw):
    tot=0;n=0;w=0;gp=gl=0;g=r=0;byY=collections.defaultdict(lambda:[0,0,0])
    for d,bars in days:
        tr=run(bars,feats[d]['adr'],**kw); p=sum(tr); tot+=p; n+=len(tr)
        for x in tr:
            if x>0: w+=1; gp+=x
            else: gl-=x
        if tr: y=d[:4]; byY[y][0]+=p; byY[y][1]+=(p>0); byY[y][2]+=(p<0); g+=(p>0); r+=(p<0)
    print(f'{name:38s} net {tot:+6.0f}pt n={n:3d} win {w/max(n,1):.0%} PF {gp/max(gl,1):.2f} G/R {g}/{r} ({g/max(g+r,1):.0%}) | '+' '.join(f"{y[2:]}:{round(v[0])}({v[1]}/{v[2]})" for y,v in sorted(byY.items())))
rep('E11 X.4 spike 2R min25')
rep('E11 X.4 nospike 2R min25',spike=False)
rep('E11 X.4 spike 2R min25 trail',trail=True)
rep('E11 X.4 spike 1.5R min25',tgtR=1.5)
rep('E11 X.4 spike 3R min25',tgtR=3)
rep('E11 X.3 spike 2R min25',X=.3)
rep('E11 X.5 spike 2R min25',X=.5)
rep('E11 X.4 spike 2R min25 emaD1.0',emaD=1.0)
rep('E11 X.4 spike 2R min25 1tr/day',maxTr=1)
rep('E11 X.4 spike 2R min25 no side force',forceSide=False)
rep('E11 X.0 spike 2R min25 (all days, ema bias)',X=0.0,forceSide=False)
