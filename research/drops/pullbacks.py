# Pullback anatomy, MNQZ6 1m, sessions Oct 27-30 (+ Oct 19-26 for comparison). Zigzag swings >= Z pts.
import pandas as pd, numpy as np, sys
Z=float(sys.argv[1]) if len(sys.argv)>1 else 20
d=pd.read_csv('../../data/live/new/glbx-mdp3-20261016-20261030.ohlcv-1m.csv'); d=d[d.symbol=='MNQZ6']
d.index=pd.DatetimeIndex(pd.to_datetime(d.ts_event,utc=True)).tz_convert('America/New_York'); d=d.sort_index()
d['sess']=[(t-pd.Timedelta(hours=18)).date()+pd.Timedelta(days=1) for t in d.index]
d=d[d.sess>=pd.Timestamp('2026-10-19').date()]
out=[]
for s,g in d.groupby('sess'):
    h,l,c,v=g.high.values,g.low.values,g.close.values,g.volume.values; n=len(c); ts=g.index
    e21=pd.Series(c).ewm(span=21,adjust=False).mean().values
    vw=np.cumsum((h+l+c)/3*v)/np.cumsum(v)
    # zigzag
    piv=[(0,c[0],0)]; dirn=0; ext=c[0]; ei=0
    for i in range(1,n):
        if dirn>=0:
            if h[i]>ext: ext=h[i]; ei=i
            if dirn==1 and ext-l[i]>=Z: piv.append((ei,ext,1)); dirn=-1; ext=l[i]; ei=i
            elif dirn==0 and ext-l[i]>=Z: piv.append((ei,ext,1)); dirn=-1; ext=l[i]; ei=i
        if dirn<=0:
            if l[i]<ext or dirn==0: 
                if l[i]<ext: ext=l[i]; ei=i
            if dirn==-1 and h[i]-ext>=Z: piv.append((ei,ext,-1)); dirn=1; ext=h[i]; ei=i
            elif dirn==0 and h[i]-ext>=Z: piv.append((ei,ext,-1)); dirn=1; ext=h[i]; ei=i
    piv=piv[1:]
    for k in range(2,len(piv)):
        a,b,cc=piv[k-2],piv[k-1],piv[k]       # leg a->b, pullback b->cc
        leg=abs(b[1]-a[1]); pb=abs(cc[1]-b[1]); legdir=np.sign(b[1]-a[1])
        j=cc[0]
        out.append(dict(sess=str(s),time=ts[b[0]].strftime('%m-%d %H:%M'),legdir='down' if legdir<0 else 'up',leg=round(leg,1),pullback=round(pb,1),retr=round(pb/leg,2),
            mins=cc[0]-b[0],end_vs_ema=round((cc[1]-e21[j])*(-legdir),1),end_vs_vwap=round((cc[1]-vw[j])*(-legdir),1),
            continued=(k+1<len(piv) and ((legdir<0 and piv[k+1][1]<b[1]) or (legdir>0 and piv[k+1][1]>b[1])))))
P=pd.DataFrame(out); P['wk']=np.where(P.sess>='2026-10-26','this week','last week')
pd.set_option('display.width',200)
print(f'zigzag {Z} pts. pullbacks after DOWN legs:')
dn=P[P.legdir=='down']
for w,g in dn.groupby('wk'):
    print(f' {w}: n={len(g)} pullback pts median {g.pullback.median():.0f}, 75% {g.pullback.quantile(.75):.0f}, 90% {g.pullback.quantile(.9):.0f} | retrace of leg median {g.retr.median():.2f}, 75% {g.retr.quantile(.75):.2f} | minutes median {g.mins.median():.0f} | then new low {g.continued.mean():.2f}')
g=dn[dn.wk=='this week']
print('\n this week, pullback size vs whether the down move continued after it:')
print(g.groupby(pd.cut(g.retr,[0,0.382,0.5,0.618,0.786,1.0,10]),observed=True).continued.agg(['mean','size']).round(2))
print('\n where the pullback HIGH ended vs the 1m EMA21 (+ = above EMA) and VWAP, this week (pts):')
print(g[['end_vs_ema','end_vs_vwap']].describe(percentiles=[.25,.5,.75]).round(1).T)
print('\n share of pullback highs within 5 pts of EMA21:', round((g.end_vs_ema.abs()<=5).mean(),2), ' above EMA21 by >5:',round((g.end_vs_ema>5).mean(),2))
P.to_csv('pullbacks.csv',index=False)
print('\nlast 3 sessions, every down leg and its pullback:'); print(P[(P.sess>='2026-10-28')&(P.legdir=='down')&(P.leg>=40)][['time','leg','pullback','retr','mins','end_vs_ema','continued']].to_string(index=False))
