# In MNQ downtrends: how big do bounces get before price makes a new low? (5m bars, all hours, 2021-10..2026-10)
import pandas as pd, numpy as np
df=pd.read_csv('../../data/raw/MNQ_5m_cont.csv.gz'); df['dt']=pd.to_datetime(df.t,unit='s',utc=True).dt.tz_convert('America/New_York')
h,l,c=df.h.values,df.l.values,df.c.values; n=len(c)
ema=pd.Series(c).ewm(span=21,adjust=False).mean().values
atr=pd.Series(np.maximum(h-l,abs(h-np.r_[c[0],c[:-1]]))).rolling(14).mean().values
slope=(ema-np.r_[np.full(6,np.nan),ema[:-6]])/atr
rows=[]
i=30
while i<n-48:
    if slope[i]<-0.5 and c[i]<ema[i] and l[i]==l[i-6:i+1].min():      # fresh low in a falling market
        low=l[i]; mx=low; res='none'
        for j in range(i+1,min(i+48,n)):
            mx=max(mx,h[j])
            if l[j]<low-0.25: res='newlow'; break
        rows.append(dict(dt=df.dt[i],bounce_pts=mx-low,bounce_atr=(mx-low)/atr[i],atr=atr[i],res=res,year=df.dt[i].year,bars=j-i))
        i=j if res=='newlow' else i+1
    else: i+=1
t=pd.DataFrame(rows); nl=t[t.res=='newlow']
print('fresh lows',len(t),' followed by a NEW low within 4h:',round((t.res=="newlow").mean(),3))
q=[.5,.7,.8,.9,.95]
print('bounce before the new low, in ATR(5m) quantiles', nl.bounce_atr.quantile(q).round(2).to_dict())
r=nl[nl.year==2026]; print('2026 bounce pts quantiles', r.bounce_pts.quantile(q).round(1).to_dict(),' median 5m ATR 2026',round(t[t.year==2026].atr.median(),1))
# probability of a new low given the bounce already reached k ATR
for k in [0.5,1,1.5,2,2.5,3]:
    reached=t[t.bounce_atr>=k]; print(f'bounce reached {k} ATR -> still makes new low: {(reached.res=="newlow").mean():.2f} (n={len(reached)})')
