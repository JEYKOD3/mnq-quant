# Does a simple trend engine call direction and reversals? MNQZ6, Oct 19 -> Oct 30 07:00 ET, 1m bars.
# E1 trend: 5m EMA21 change over 30 min (> +0.5 x 5m ATR up, < -0.5 down, else flat).
# E2 warning: price closes beyond the last confirmed 5m swing against the trend (above the last lower high in a downtrend) = trend over.
import pandas as pd, numpy as np, zstandard, io
fr=[]
for f in ['glbx-mdp3-20261016-20261030.ohlcv-1m.csv.zst','glbx-mdp3-20261029-20261030.ohlcv-1m.csv.zst']:
    raw=zstandard.ZstdDecompressor().decompressobj().decompress(open('../../data/live/new/'+f,'rb').read()); fr.append(pd.read_csv(io.BytesIO(raw)))
d=pd.concat(fr); d=d[d.symbol=='MNQZ6'].drop_duplicates('ts_event')
d.index=pd.DatetimeIndex(pd.to_datetime(d.ts_event,utc=True)).tz_convert('America/New_York'); d=d.sort_index(); d=d[d.index>='2026-10-18 18:00']
m5=d.resample('5min').agg({'open':'first','high':'max','low':'min','close':'last'}).dropna()
e=m5.close.ewm(span=21,adjust=False).mean(); atr=(m5.high-m5.low).rolling(14).mean()
sl=(e-e.shift(6))/atr
# 5m swings, pivots 3/3 (known 3 bars = 15 min after the pivot)
H,L=m5.high.values,m5.low.values; n5=len(m5); lastLH=np.full(n5,np.nan); lastHL=np.full(n5,np.nan)
ph=[];pl=[]
for i in range(n5):
    k=i-3
    if k>=3:
        if H[k]==H[k-3:k+4].max(): ph.append(H[k])
        if L[k]==L[k-3:k+4].min(): pl.append(L[k])
    lastLH[i]=ph[-1] if ph else np.nan; lastHL[i]=pl[-1] if pl else np.nan
st=[]; state='FLAT'
for i in range(n5):
    s=sl.iat[i]; c=m5.close.iat[i]
    trend='DOWN' if s<-0.5 else ('UP' if s>0.5 else 'FLAT')
    if trend=='DOWN' and c>lastLH[i]: trend='WARN: down trend breaking (closed above last lower high)'
    if trend=='UP' and c<lastHL[i]: trend='WARN: up trend breaking (closed below last higher low)'
    st.append(trend)
m5['state']=st
# forward returns by state (from the 5m close where the state is known)
for k,name in [(6,'next 30 min'),(12,'next 60 min')]:
    m5[name]=m5.close.shift(-k)-m5.close
g=m5.groupby(m5.state.str[:22])
print('== what price did next, by state (pts) ==')
print(pd.DataFrame({'share of time':g.size()/len(m5),'avg next 60 min':g['next 60 min'].mean(),'down next 60 min %':g['next 60 min'].apply(lambda x:(x<0).mean()),'avg next 30 min':g['next 30 min'].mean()}).round(2))
flips=(m5.state.str[:4]!=m5.state.str[:4].shift()).sum(); days=m5.index.normalize().nunique()
print('\nstate changes per day:',round(flips/days,1))
# major turns: zigzag 150 pts on 5m closes of highs/lows
piv=[];dirn=0;ext=m5.close.iat[0];ei=0
for i in range(n5):
    if dirn>=0 and H[i]>ext: ext,ei=H[i],i
    if dirn<=0 and L[i]<ext: ext,ei=L[i],i
    if dirn>=0 and ext-L[i]>=150 and (dirn==1 or ext==H[ei]): piv.append(('TOP',ei,ext)); dirn=-1; ext,ei=L[i],i
    elif dirn<=0 and H[i]-ext>=150 and (dirn==-1 or ext==L[ei]): piv.append(('BOTTOM',ei,ext)); dirn=1; ext,ei=H[i],i
print('\n== major turns (150+ pt swings): how long until the engine said so ==')
for kind,i,p in piv:
    want='DOWN' if kind=='TOP' else 'UP'; warn='WARN: up' if kind=='TOP' else 'WARN: down'
    j_w=next((j for j in range(i,n5) if m5.state.iat[j].startswith(warn)),None)
    j_t=next((j for j in range(i,n5) if m5.state.iat[j]==want),None)
    fmt=lambda j: f"{(m5.index[j]-m5.index[i]).total_seconds()/60:.0f} min, {abs(m5.close.iat[j]-p):.0f} pts from the turn" if j is not None else 'never'
    print(f"{kind:6s} {m5.index[i].strftime('%a %m-%d %H:%M')} at {p:.0f}: warning after {fmt(j_w)} | new trend after {fmt(j_t)}")
m5.to_csv('trend_states.csv')
