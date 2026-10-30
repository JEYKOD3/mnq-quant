# Causal feature table on 5m bars (MNQZ6, Oct 19 -> Oct 30 07:00 ET) + event labels.
import pandas as pd, numpy as np, zstandard, io
def load():
    fr=[]
    for f in ['glbx-mdp3-20261016-20261030.ohlcv-1m.csv.zst','glbx-mdp3-20261029-20261030.ohlcv-1m.csv.zst']:
        raw=zstandard.ZstdDecompressor().decompressobj().decompress(open('../../data/live/new/'+f,'rb').read()); fr.append(pd.read_csv(io.BytesIO(raw)))
    d=pd.concat(fr); d=d[d.symbol=='MNQZ6'].drop_duplicates('ts_event')
    d.index=pd.DatetimeIndex(pd.to_datetime(d.ts_event,utc=True)).tz_convert('America/New_York'); d=d.sort_index()[['open','high','low','close','volume']]
    return d
def build(d):
    m=d.resample('5min').agg({'open':'first','high':'max','low':'min','close':'last','volume':'sum'}).dropna()
    m['sess']=[(t-pd.Timedelta(hours=18)).date() for t in m.index]
    o,h,l,c,v=m.open,m.high,m.low,m.close,m.volume
    m['atr']=np.maximum(h-l,abs(h-c.shift())).rolling(14).mean()
    A=m.atr
    m['ema']=c.ewm(span=21,adjust=False).mean(); m['slope']=(m.ema-m.ema.shift(6))/A
    tp=(h+l+c)/3; m['vwap']=(tp*v).groupby(m.sess).cumsum()/v.groupby(m.sess).cumsum()
    for k in (1,3,6,12,24): m[f'r{k}']=(c-c.shift(k))/A
    m['dvwap']=(c-m.vwap)/A; m['dema']=(c-m.ema)/A
    m['pos12']=(c-l.rolling(12).min())/(h.rolling(12).max()-l.rolling(12).min()+1e-9)
    m['pos48']=(c-l.rolling(48).min())/(h.rolling(48).max()-l.rolling(48).min()+1e-9)
    m['volz']=(v-v.rolling(48).mean())/(v.rolling(48).std()+1e-9)
    m['rangez']=((h-l)-(h-l).rolling(48).mean())/((h-l).rolling(48).std()+1e-9)
    m['upwick']=(h-np.maximum(o,c))/(h-l+1e-9); m['dnwick']=(np.minimum(o,c)-l)/(h-l+1e-9)
    m['body']=(c-o)/(h-l+1e-9)
    dn=(c<o).astype(int); m['dnrun']=dn.groupby((dn!=dn.shift()).cumsum()).cumsum()*dn
    up=(c>o).astype(int); m['uprun']=up.groupby((up!=up.shift()).cumsum()).cumsum()*up
    delta=c.diff(); g=delta.clip(lower=0).ewm(alpha=1/14).mean(); ls=(-delta.clip(upper=0)).ewm(alpha=1/14).mean(); m['rsi']=100-100/(1+g/(ls+1e-9))
    # failed breakout: new 60-min high in last 3 bars and close back below the prior 60-min high
    ph=h.shift(1).rolling(12).max(); pl=l.shift(1).rolling(12).min()
    m['fail_hi']=((h.rolling(3).max()>ph.shift(2))&(c<ph.shift(2))).astype(int)
    m['fail_lo']=((l.rolling(3).min()<pl.shift(2))&(c>pl.shift(2))).astype(int)
    m['brk_lo']=(c<pl).astype(int); m['brk_hi']=(c>ph).astype(int)
    # prior day / overnight levels
    daily=m.groupby('sess').agg(H=('high','max'),L=('low','min'),C=('close','last'))
    prev=daily.shift(1); m['PDH']=m.sess.map(prev.H); m['PDL']=m.sess.map(prev.L); m['PDC']=m.sess.map(prev.C)
    m['dPDL']=(c-m.PDL)/A; m['dPDH']=(c-m.PDH)/A; m['dPDC']=(c-m.PDC)/A
    m['sessH']=h.groupby(m.sess).cummax(); m['sessL']=l.groupby(m.sess).cummin()
    m['dSessH']=(c-m.sessH)/A; m['dSessL']=(c-m.sessL)/A
    m['hr']=m.index.hour+m.index.minute/60
    # swing structure 3/3
    H,L=h.values,l.values; n=len(m); st=np.zeros(n); ph_=[];pl_=[]
    for i in range(n):
        k=i-3
        if k>=3:
            if H[k]==H[k-3:k+4].max(): ph_.append(H[k])
            if L[k]==L[k-3:k+4].min(): pl_.append(L[k])
        if len(ph_)>=2 and len(pl_)>=2: st[i]=1 if (ph_[-1]>ph_[-2] and pl_[-1]>pl_[-2]) else (-1 if (ph_[-1]<ph_[-2] and pl_[-1]<pl_[-2]) else 0)
    m['struct']=st
    # ---- labels (future, for scoring only) ----
    fmin=pd.concat([l.shift(-k) for k in range(1,7)],axis=1).min(1)   # next 30 min
    fmax=pd.concat([h.shift(-k) for k in range(1,7)],axis=1).max(1)
    m['DROP']=((fmin<=c-2.5*A)&(fmax<=c+1.0*A)).astype(int)            # >= 2.5 ATR down within 30 min before +1 ATR up
    m['RIP']=((fmax>=c+2.5*A)&(fmin>=c-1.0*A)).astype(int)
    m['week']=np.where(m.index>=pd.Timestamp('2026-10-25 18:00',tz='America/New_York'),2,1)
    m=m[m.index>=pd.Timestamp('2026-10-19 00:00',tz='America/New_York')]
    return m.dropna(subset=['atr','r24','volz','PDL'])
if __name__=='__main__':
    m=build(load()); m.to_pickle('feat5m.pkl')
    print(len(m),'bars; base rates: DROP',round(m.DROP.mean(),3),'RIP',round(m.RIP.mean(),3), m.groupby('week')[['DROP','RIP']].mean().round(3).to_dict())
