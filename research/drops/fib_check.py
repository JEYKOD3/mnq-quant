# Same pullback rule, both directions, on (a) Oct 19-30 all hours and (b) 5y RTH 1m (per day). Trend filter = 5m EMA21 slope (built from 1m).
import pandas as pd, numpy as np
def sim(h,l,c,slope,LEG=60,f=0.5,filt=True):
    n=len(c); res=[]; i=0
    while i<n-1:
        found=False
        for side in (-1,1):
            A_i=i; A=h[i] if side<0 else l[i]; B=l[i] if side<0 else h[i]; B_i=i; j=i+1
            while j<n and j-A_i<120:
                if side<0:
                    if h[j]>A and B_i==A_i: A=h[j];A_i=j;B=l[j];B_i=j
                    if l[j]<B: B=l[j];B_i=j
                    leg=A-B; bounce=h[j]-B
                else:
                    if l[j]<A and B_i==A_i: A=l[j];A_i=j;B=h[j];B_i=j
                    if h[j]>B: B=h[j];B_i=j
                    leg=B-A; bounce=B-l[j]
                if leg>=LEG and bounce>=0.3*leg: break
                j+=1
            else: continue
            if j>=n or j-A_i>=120: continue
            conf=j
            if filt and not(side*slope[conf]>0): i=conf; found=True; break
            e=B-side*f*leg; stop=A-side*2; r=abs(stop-e); k0=None
            for k in range(conf,min(conf+60,n)):
                if (side<0 and l[k]<B) or (side>0 and h[k]>B): break
                if (side<0 and h[k]>=e+0.25) or (side>0 and l[k]<=e-0.25): k0=k; break
            if k0 is None: i=conf; found=True; break
            pnl=None
            if (side<0 and h[k0]>=stop) or (side>0 and l[k0]<=stop): pnl=-r
            else:
                for k in range(k0+1,min(k0+61,n)):
                    if (side<0 and h[k]>=stop) or (side>0 and l[k]<=stop): pnl=-r; break
                    if (side<0 and l[k]<=B) or (side>0 and h[k]>=B): pnl=abs(e-B); break
            if pnl is None: pnl=side*(c[min(k0+60,n-1)]-e)
            res.append((side,pnl-1,r)); i=k0+1; found=True; break
        if not found: i+=1
    return res
def slope_of(c):
    s=pd.Series(c); c5=s.groupby(np.arange(len(s))//5).transform('last'); e=c5.ewm(span=105,adjust=False).mean()   # ~EMA21 on 5m
    return (e-e.shift(30)).fillna(0).values
pf=lambda x: round(x[x>0].sum()/max(1e-9,-x[x<0].sum()),2) if len(x) else None
# (a) recent
d=pd.read_csv('../../data/live/new/glbx-mdp3-20261016-20261030.ohlcv-1m.csv'); d=d[d.symbol=='MNQZ6']
d.index=pd.DatetimeIndex(pd.to_datetime(d.ts_event,utc=True)).tz_convert('America/New_York'); d=d.sort_index(); d=d[d.index>='2026-10-18 18:00']
for filt in (True,False):
    r=pd.DataFrame(sim(d.high.values,d.low.values,d.close.values,slope_of(d.close.values),filt=filt),columns=['side','pts','risk'])
    print('2 weeks, trend filter' if filt else '2 weeks, no filter', {s:(len(g),pf(g.pts),round(g.pts.sum())) for s,g in r.groupby('side')})
# (b) 5 years RTH
rows=[]
for line in open('../../data/raw/mnq_rth_1m.txt'):
    dd,*bars=line.strip().split('|'); a=np.array([[int(x) for x in b.split(',')] for b in bars],float); a[:,1:]/=4
    for s,p,rk in sim(a[:,2],a[:,3],a[:,4],slope_of(a[:,4])): rows.append((dd[:4],s,p,rk))
R=pd.DataFrame(rows,columns=['yr','side','pts','risk'])
print('5y RTH, trend filter: shorts',pf(R[R.side<0].pts),'longs',pf(R[R.side>0].pts),'all',pf(R.pts),'n',len(R),' by year',R.groupby('yr').pts.apply(pf).to_dict())
