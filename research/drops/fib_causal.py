# Causal version. At each closed 1m bar t: A = highest high of the last W bars (index a), B = lowest low after a (index b<=t).
# Setup when A-B >= LEG and the bounce off B (max high after b, up to t) >= 0.3*(A-B), and b>a.
# Then a limit sell at B + f*(A-B) is active from t+1 until filled, a new low < B, or 60 bars. Stop A+2, target B. Mirror for longs.
import pandas as pd, numpy as np, sys
def sim(h,l,c,slope,LEG=60,f=0.5,W=120,filt=True,tgt=0.0):
    n=len(c); res=[]; t=W; busy=-1
    while t<n-2:
        if t<=busy: t+=1; continue
        done=False
        for side in (-1,1):
            win_h=h[t-W:t+1]; win_l=l[t-W:t+1]
            if side<0:
                a=t-W+int(np.argmax(win_h)); A=h[a]
                if a>=t: continue
                b=a+1+int(np.argmin(l[a+1:t+1])); B=l[b]; leg=A-B
                if b>=t or leg<LEG: continue
                bounce=h[b+1:t+1].max()-B
            else:
                a=t-W+int(np.argmin(win_l)); A=l[a]
                if a>=t: continue
                b=a+1+int(np.argmax(h[a+1:t+1])); B=h[b]; leg=B-A
                if b>=t or leg<LEG: continue
                bounce=B-l[b+1:t+1].min()
            if bounce<0.3*leg: continue
            if filt and not(side*slope[t]>0): continue
            e=B-side*f*leg; stop=A-side*2; r=abs(stop-e); T=B+side*tgt*leg
            # if price is already beyond the entry at t, skip (we only place the order now)
            if (side<0 and h[t]>=e) or (side>0 and l[t]<=e): continue
            k0=None
            for k in range(t+1,min(t+61,n)):
                if (side<0 and l[k]<B) or (side>0 and h[k]>B): break
                if (side<0 and h[k]>=e+0.25) or (side>0 and l[k]<=e-0.25): k0=k; break
            if k0 is None: continue
            pnl=None; x=k0
            if (side<0 and h[k0]>=stop) or (side>0 and l[k0]<=stop): pnl=-r
            else:
                for k in range(k0+1,min(k0+61,n)):
                    x=k
                    if (side<0 and h[k]>=stop) or (side>0 and l[k]<=stop): pnl=-r; break
                    if (side<0 and l[k]<=T) or (side>0 and h[k]>=T): pnl=abs(e-T); break
            if pnl is None: pnl=side*(c[min(k0+60,n-1)]-e)
            res.append((side,pnl-1,r)); busy=x; done=True; break
        t+=1
    return res
def slope_of(c):
    s=pd.Series(c); c5=s.groupby(np.arange(len(s))//5).transform('last'); e=c5.ewm(span=105,adjust=False).mean()
    return (e-e.shift(30)).fillna(0).values
pf=lambda x: round(x[x>0].sum()/max(1e-9,-x[x<0].sum()),2) if len(x) else None
LEG=float(sys.argv[1]) if len(sys.argv)>1 else 60; F=float(sys.argv[2]) if len(sys.argv)>2 else 0.5
d=pd.read_csv('../../data/live/new/glbx-mdp3-20261016-20261030.ohlcv-1m.csv'); d=d[d.symbol=='MNQZ6']
d.index=pd.DatetimeIndex(pd.to_datetime(d.ts_event,utc=True)).tz_convert('America/New_York'); d=d.sort_index(); d=d[d.index>='2026-10-18 18:00']
wk2=d.index>='2026-10-25 18:00'
for filt in (True,False):
    for part,m in [('wk1',~wk2),('wk2',wk2)]:
        g=d[m]; r=pd.DataFrame(sim(g.high.values,g.low.values,g.close.values,slope_of(g.close.values),LEG,F,filt=filt),columns=['side','pts','risk'])
        print(f'leg>={LEG} f={F} {"trend" if filt else "no filter"} {part}:', {('short' if s<0 else 'long'):(len(x),pf(x.pts),round(x.pts.sum()),round(x.risk.median())) for s,x in r.groupby('side')})
rows=[]
for line in open('../../data/raw/mnq_rth_1m.txt'):
    dd,*bars=line.strip().split('|'); a=np.array([[int(x) for x in b.split(',')] for b in bars],float); a[:,1:]/=4
    for s,p,rk in sim(a[:,2],a[:,3],a[:,4],slope_of(a[:,4]),LEG,F): rows.append((dd[:4],s,p,rk))
R=pd.DataFrame(rows,columns=['yr','side','pts','risk'])
print(f'5y RTH trend: shorts {pf(R[R.side<0].pts)} longs {pf(R[R.side>0].pts)} all {pf(R.pts)} n {len(R)} by year', R.groupby('yr').pts.apply(pf).to_dict())
