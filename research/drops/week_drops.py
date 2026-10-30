# This week's MNQ drops (MNQZ6 1m, Oct 19-30 2026): what came before each big drop, and how big were the bounces.
import pandas as pd, numpy as np
d=pd.read_csv('../../data/live/new/glbx-mdp3-20261016-20261030.ohlcv-1m.csv')
d=d[d.symbol=='MNQZ6'].copy(); d['dt']=pd.to_datetime(d.ts_event,utc=True).dt.tz_convert('America/New_York'); d=d.set_index('dt').sort_index()
m1=d[['open','high','low','close','volume']]
m5=m1.resample('5min',label='left',closed='left').agg({'open':'first','high':'max','low':'min','close':'last','volume':'sum'}).dropna()
m5.to_csv('mnq_5m_oct16_30.csv')
c,h,l,v=m5.close.values,m5.high.values,m5.low.values,m5.volume.values; n=len(c)
ema=pd.Series(c).ewm(span=21,adjust=False).mean().values
atr=pd.Series(np.maximum(h-l,abs(h-np.r_[c[0],c[:-1]]))).rolling(14).mean().values
slope=(ema-np.r_[np.full(6,np.nan),ema[:-6]])/atr
idx=m5.index
# 1) big drops: 5m close-to-low fall of >= 4 ATR within 12 bars (1h), non-overlapping
print('5m ATR this period, median pts:',round(np.nanmedian(atr),1))
drops=[];i=30
while i<n-12:
    lo=l[i+1:i+13].min(); k=i+1+int(np.argmin(l[i+1:i+13]))
    if c[i]-lo>=4*atr[i]:
        # context before the drop
        pre=slice(max(0,i-12),i+1)
        drops.append(dict(start=idx[i],end=idx[k],pts=round(c[i]-lo,1),atr=round(atr[i],1),
            below_ema=bool(c[i]<ema[i]),slope=round(slope[i],2),
            pre_range_atr=round((h[pre].max()-l[pre].min())/atr[i],1),
            pre_vol_vs_20=round(v[pre].mean()/np.mean(v[max(0,i-60):i+1]),2),
            drop_vol_vs_20=round(v[i+1:k+1].mean()/np.mean(v[max(0,i-60):i+1]),2)))
        i=k+1
    else: i+=1
D=pd.DataFrame(drops); pd.set_option('display.width',220)
print('\nBIG DROPS (>= 4 x 5m ATR within 1h):'); print(D.to_string(index=False))
# 2) bounce sizes in falling market this period vs 5y stats
rows=[];i=30
while i<n-48:
    if slope[i]<-0.5 and c[i]<ema[i] and l[i]==l[i-6:i+1].min():
        low=l[i]; mx=low; res=0
        for j in range(i+1,min(i+48,n)):
            mx=max(mx,h[j])
            if l[j]<low-0.25: res=1; break
        rows.append(((mx-low)/atr[i],mx-low,res)); i=j if res else i+1
    else: i+=1
B=pd.DataFrame(rows,columns=['k','pts','newlow'])
print('\nfresh lows in falling market:',len(B),' new low within 4h:',round(B.newlow.mean(),2),'(5y: 0.89)')
nb=B[B.newlow==1]
print('bounce before next low, ATR quantiles:',nb.k.quantile([.5,.8,.9]).round(2).to_dict(),'(5y: 0.98 / 1.93 / 2.84)')
print('bounce before next low, POINTS quantiles:',nb.pts.quantile([.5,.8,.9]).round(0).to_dict())
for k in [1,1.5,2,2.5,3]: s=B[B.k>=k]; print(f'  bounce >= {k} ATR -> new low {s.newlow.mean():.2f} (n={len(s)})')
