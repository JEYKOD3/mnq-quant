"""Short-term intraday setups after 9:45 on MNQ: signals on 5m bars, management on 1m bars. Costs: comm 2.37/side, 1 tick slip entry + stop.
Setups: EMA pullback (Holy-Grail style), EMA9/21 cross, compression breakout, second-entry pullback (H2/L2 style).
Filters: intraday trend (price vs session TWAP + EMA20 slope), daily trend (prior close vs SMA20), D2 trend-day flag."""
import pickle, sys, collections
sys.path.insert(0,'.'); from core import *
days,F=pickle.load(open('/tmp/claude-0/-home-claude/afdbc088-26a4-5e84-b77d-b387ee40e855/scratchpad/lab.pkl','rb')) if False else (None,None)
days=load(); F=features(days)
D=[d for d,_ in days]; C={d:b[-1][4] for d,b in days}
TRD={}
for i,d in enumerate(D):
    if i>=21: TRD[d]=1 if C[D[i-1]]>sum(C[x] for x in D[i-20:i])/20 else -1
def ema(v,n):
    k=2/(n+1); out=[]; e=None
    for x in v: e=x if e is None else e+k*(x-e); out.append(e)
    return out
def mgmt(b1,i,s,eP,stp,tgt,tcap,flat=955):
    """walk 1m bars from index i; returns (xP,why,minutes)"""
    t0=b1[i][0] if i<len(b1) else 955
    for j in range(i,len(b1)):
        m,o,h,l,c=b1[j]
        if (s>0 and l<=stp) or (s<0 and h>=stp): return stp-s*SLIP*T,'stop',m-t0
        if tgt is not None and ((s>0 and h>=tgt) or (s<0 and l<=tgt)): return tgt,'tgt',m-t0
        if m>=flat or (tcap and m-t0>=tcap): return c,'time',m-t0
    return b1[-1][4],'close',b1[-1][0]-t0
def run(setup, tgtR=2.0, tcap=60, start=585, end=900, maxtr=3, dtrend=True, itrend=True, trendday=False, minR=6, maxRadr=.25, tdth=.4):
    out=[]
    for d,b1 in days:
        f=F.get(d)
        if not f or d<20220101 or d not in TRD or len(b1)<300: continue
        tdir=0
        if trendday:
            px=[x for x in b1 if x[0]==629]
            if not px or abs(px[0][4]-f['open'])<tdth*f['adr']: continue
            tdir=1 if px[0][4]>f['open'] else -1
            start=max(start,630)
        b=agg(b1,5); cl=[x[4] for x in b]; e20=ema(cl,20); e9=ema(cl,9); e21=ema(cl,21)
        tw=[]; s_=0
        for k,x in enumerate(b): s_+=(x[2]+x[3]+x[4])/3; tw.append(s_/(k+1))
        idx1={x[0]:j for j,x in enumerate(b1)}
        ntr=0; busy_until=0
        for k in range(8,len(b)):
            m,o,h,l,c=b[k]; mclose=m+5
            if mclose<start or mclose>end or ntr>=maxtr or mclose<busy_until: continue
            up = c>tw[k] and e20[k]>e20[k-3]; dn = c<tw[k] and e20[k]<e20[k-3]
            s=0; stp=None
            if setup=='ema_pb':
                if (not itrend or up) and l<=e20[k] and c>e20[k] and c>o: s=1; stp=min(x[3] for x in b[k-2:k+1])-T
                elif (not itrend or dn) and h>=e20[k] and c<e20[k] and c<o: s=-1; stp=max(x[2] for x in b[k-2:k+1])+T
            elif setup=='cross':
                if e9[k]>e21[k] and e9[k-1]<=e21[k-1] and (not itrend or c>tw[k]): s=1; stp=min(x[3] for x in b[k-5:k+1])-T
                elif e9[k]<e21[k] and e9[k-1]>=e21[k-1] and (not itrend or c<tw[k]): s=-1; stp=max(x[2] for x in b[k-5:k+1])+T
            elif setup=='squeeze':
                win=b[k-6:k]; hi=max(x[2] for x in win); lo=min(x[3] for x in win)
                if hi-lo<.15*f['adr']:
                    if c>hi and (not itrend or up): s=1; stp=lo-T
                    elif c<lo and (not itrend or dn): s=-1; stp=hi+T
            elif setup=='h2':
                # trend leg: new session-extreme within last 8 bars, then pullback of >=2 bars, then bar closing back in trend dir above prior bar high
                hh=max(x[2] for x in b[:k-2]); ll=min(x[3] for x in b[:k-2])
                recent_hi=max(x[2] for x in b[k-8:k-2]); recent_lo=min(x[3] for x in b[k-8:k-2])
                if (not itrend or up) and recent_hi>=hh-1e-9 and b[k-1][4]<b[k-2][4] and c>b[k-1][2] and c>o: s=1; stp=min(x[3] for x in b[k-3:k+1])-T
                elif (not itrend or dn) and recent_lo<=ll+1e-9 and b[k-1][4]>b[k-2][4] and c<b[k-1][3] and c<o: s=-1; stp=max(x[2] for x in b[k-3:k+1])+T
            elif setup=='vwap':
                if (not itrend or c>tw[k]) and l<=tw[k] and c>tw[k] and c>o and tw[k]>e20[k]*0+0 and b[k-1][4]<b[k-2][4]+1e9: s=1; stp=min(x[3] for x in b[k-2:k+1])-T
                elif (not itrend or c<tw[k]) and h>=tw[k] and c<tw[k] and c<o: s=-1; stp=max(x[2] for x in b[k-2:k+1])+T
            elif setup=='vwapx':   # rejection from above TWAP: bar closes back below TWAP after trading above it, in a down day
                if c>tw[k] and b[k-1][4]<tw[k-1] and c>o: s=1; stp=min(x[3] for x in b[k-3:k+1])-T
                elif c<tw[k] and b[k-1][4]>tw[k-1] and c<o: s=-1; stp=max(x[2] for x in b[k-3:k+1])+T
            if not s: continue
            if dtrend and TRD[d]!=s: continue
            if tdir and s!=tdir: continue
            j=idx1.get(mclose)
            if j is None: continue
            eP=b1[j][1]+s*SLIP*T; r=abs(eP-stp)
            if (s>0 and stp>=eP) or (s<0 and stp<=eP) or r<minR or r>maxRadr*f['adr']: continue
            tgt=eP+s*tgtR*r if tgtR else None
            xP,why,mins=mgmt(b1,j,s,eP,stp,tgt,tcap)
            pts=(xP-eP)*s
            out.append(dict(d=d,side=s,eT=mclose,r=r,pts=pts,R=(pts-2*COMM/PV)/r,why=why,hold=mins,setup=setup))
            ntr+=1; busy_until=mclose+mins+5
    return out
def rep(lab,tr):
    if not tr: print(lab,'n0'); return
    def pf(v):
        g=sum(x for x in v if x>0); l=-sum(x for x in v if x<=0); return g/l if l else 9.9
    R=[t['R'] for t in tr]; dv=[t['R'] for t in tr if t['d']<=20241231]; tv=[t['R'] for t in tr if t['d']>20241231]
    eq=pk=dd=0
    for x in R: eq+=x; pk=max(pk,eq); dd=max(dd,pk-eq)
    yrs=' '.join(f"{y%100}:{pf([t['R'] for t in tr if t['d']//10000==y]):.2f}" for y in range(2022,2027))
    print(f"{lab:58s} n{len(tr):5d} ({len(tr)/4.8:4.0f}/yr) wr{100*sum(x>0 for x in R)/len(R):3.0f}% PF{pf(R):5.2f} DEV{pf(dv):5.2f} TEST{pf(tv):5.2f} avgR{sum(R)/len(R):+.2f} DD{dd:5.1f}R hold{sum(t['hold'] for t in tr)/len(tr):4.0f}m risk{sum(t['r'] for t in tr)/len(tr):4.0f}pt | {yrs}")
if False and __name__=='__main__':
    for st in ('ema_pb','cross','squeeze','h2'):
        for tg in (1.5,2,3):
            for tc in (30,60,90):
                for td in (False,True):
                    rep(f"{st} tgt{tg}R cap{tc}m dailytrend+intraday trendday{int(td)}",run(st,tg,tc,trendday=td))
