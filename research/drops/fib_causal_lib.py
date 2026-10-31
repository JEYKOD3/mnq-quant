# Causal version. At each closed 1m bar t: A = highest high of the last W bars (index a), B = lowest low after a (index b<=t).
# Setup when A-B >= LEG and the bounce off B (max high after b, up to t) >= 0.3*(A-B), and b>a.
# Then a limit sell at B + f*(A-B) is active from t+1 until filled, a new low < B, or 60 bars. Stop A+2, target B. Mirror for longs.
import pandas as pd, numpy as np, sys
def sim(h,l,c,slope,LEG=60,f=0.5,W=120,filt=True,tgt=0.0,tfrac=1.0):
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
            e=B-side*f*leg; stop=A-side*2; r=abs(stop-e); T=e+(B+side*tgt*leg-e)*tfrac
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
