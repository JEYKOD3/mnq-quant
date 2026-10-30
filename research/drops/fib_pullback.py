# Sell the pullback inside a leg (Oct 19-30, MNQZ6 1m). Leg A->B of >= LEG pts (confirmed once price bounces 30% of it off B).
# Entry: limit at B + f*leg (f = 0.5 or 0.618) if reached before a new low. Stop: 2 pts beyond A (the lower high).
# Target: back to B (prior low) or B - 0.27*leg. Time stop 60 min. Cost 1 pt. Same for long legs (mirror).
import pandas as pd, numpy as np, itertools
d=pd.read_csv('../../data/live/new/glbx-mdp3-20261016-20261030.ohlcv-1m.csv'); d=d[d.symbol=='MNQZ6']
d.index=pd.DatetimeIndex(pd.to_datetime(d.ts_event,utc=True)).tz_convert('America/New_York'); d=d.sort_index()
d=d[d.index>=pd.Timestamp('2026-10-18 18:00',tz='America/New_York')]
h,l,c=d.high.values,d.low.values,d.close.values; n=len(c); ts=d.index
c5=d.close.resample('5min').last().ffill(); e5=c5.ewm(span=21,adjust=False).mean()
slope5=((e5-e5.shift(6))).reindex(ts,method='ffill').values; above5=(c5>e5).reindex(ts,method='ffill').values
def legs(LEG):
    # swing detection: track running extreme; a leg A->B (down) is confirmed when price rises 0.3*leg off B
    out=[]; i=0
    while i<n-1:
        # down legs: A = highest high of last 60 bars at i, B = running low after A
        A_i=i; A=h[i]; B=l[i]; B_i=i; j=i+1
        while j<n and j-A_i<120:
            if h[j]>A and B_i==A_i: A=h[j]; A_i=j; B=l[j]; B_i=j
            if l[j]<B: B=l[j]; B_i=j
            leg=A-B
            if leg>=LEG and h[j]-B>=0.3*leg: out.append((-1,A_i,A,B_i,B,j)); break
            j+=1
        i=j if j>i+1 else i+1
    return out
def run(LEG,f,tgt,filt,side_ok):
    res=[]
    for side,A_i,A,B_i,B,conf in legs(LEG):
        leg=A-B; e=B+f*leg; stop=A+2; r=stop-e
        if side_ok=='long': continue
        if filt and not(slope5[conf]<0): continue
        k0=None
        for k in range(conf,min(conf+60,n)):
            if l[k]<B: break
            if h[k]>=e+0.25: k0=k; break
        if k0 is None: continue
        T=B if tgt=='prior low' else B-0.27*leg
        pnl=None
        if h[k0]>=stop: pnl=-r
        else:
            for k in range(k0+1,min(k0+61,n)):
                if h[k]>=stop: pnl=-r; break
                if l[k]<=T: pnl=e-T; break
        if pnl is None: pnl=e-c[min(k0+60,n-1)]
        res.append((ts[k0],pnl-1,r))
    return pd.DataFrame(res,columns=['t','pts','risk'])
rows=[]
for LEG,f,tgt,filt in itertools.product([60,80,120],[0.5,0.618],['prior low','-0.27 ext'],[True,False]):
    t=run(LEG,f,tgt,filt,'short')
    if len(t)==0: continue
    wk=t.t>=pd.Timestamp('2026-10-25 18:00',tz='America/New_York')
    pf=lambda x: round(x[x>0].sum()/max(1e-9,-x[x<0].sum()),2)
    rows.append(dict(leg_min=LEG,entry=f,target=tgt,trend5m=filt,trades=len(t),win=round((t.pts>0).mean(),2),pts=round(t.pts.sum()),PF=pf(t.pts),PF_lastwk=pf(t[~wk].pts),PF_thiswk=pf(t[wk].pts),med_risk=round(t.risk.median())))
R=pd.DataFrame(rows); pd.set_option('display.width',200); print(R.sort_values('PF',ascending=False).to_string(index=False))
