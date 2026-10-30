# Sell the bounce in a downtrend: after a fresh 5m low (EMA21 falling, price below it), sell when the bounce reaches k ATR above the low.
# Stop s ATR above the low. Target: low - x ATR. Exit at 4h or session end. Same-bar: stop first.
import pandas as pd, numpy as np, itertools
df=pd.read_csv('../../data/raw/MNQ_5m_cont.csv.gz'); df['dt']=pd.to_datetime(df.t,unit='s',utc=True).dt.tz_convert('America/New_York')
h,l,c,v=df.h.values,df.l.values,df.c.values,df.v.values; n=len(c)
hm=(df.dt.dt.hour*100+df.dt.dt.minute).values; yr=df.dt.dt.year.values
ema=pd.Series(c).ewm(span=21,adjust=False).mean().values
atr=pd.Series(np.maximum(h-l,abs(h-np.r_[c[0],c[:-1]]))).rolling(14).mean().values
slope=(ema-np.r_[np.full(6,np.nan),ema[:-6]])/atr
lows=[i for i in range(30,n-60) if slope[i]<-0.5 and c[i]<ema[i] and l[i]==l[i-6:i+1].min() and not(1600<=hm[i]<1800)]
def test(k,s,x,emaCap,hold=48):
    R=[];Y=[]; last=-1
    for i in lows:
        if i<=last: continue
        a=atr[i]; low=l[i]; ent=low+k*a; stop=low+s*a; tgt=low-x*a; r=stop-ent
        filled=None
        for j in range(i+1,min(i+12,n)):                 # must reach the entry within 1h, before a new low
            if l[j]<low: break
            if h[j]>=ent:
                if emaCap and ent>ema[j]+0.25*a: break  # bounce went through the EMA: trend may be over, skip
                filled=j; break
        if filled is None: continue
        j=filled
        if h[j]>=stop: R.append(-1); Y.append(yr[j]); last=j; continue
        res=None
        for q in range(j+1,min(j+hold,n)):
            if 1645<=hm[q]<1800: res=(ent-c[q-1])/r; break
            if h[q]>=stop: res=-1.0; break
            if l[q]<=tgt: res=(ent-tgt)/r; break
        if res is None: res=(ent-c[min(j+hold,n-1)])/r
        R.append(res); Y.append(yr[j]); last=q
    R=np.array(R); Y=np.array(Y)
    pf=lambda m: round(R[m][R[m]>0].sum()/max(1e-9,-R[m][R[m]<0].sum()),3)
    return dict(k=k,s=s,x=x,emaCap=emaCap,n=len(R),win=round((R>0).mean(),3),avgR=round(R.mean(),3),PF=pf(np.ones(len(R),bool)),
                PF_train=pf(Y<2025),PF_test=pf(Y>=2025),yrs=' '.join(str(pf(Y==y)) for y in [2022,2023,2024,2025,2026]))
rows=[]
for k,s,x,cap in itertools.product([0.75,1.0,1.5],[2.5,3.0,4.0],[0.0,0.5,1.0],[True,False]):
    r=test(k,s,x,cap); rows.append(r); print(r,flush=True)
pd.DataFrame(rows).to_csv('sell_bounce_grid.csv',index=False)
