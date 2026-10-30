# Walk-forward contest, MNQZ6. Decisions every 5 min from Sun Oct 25 18:00 to Fri Oct 30 07:00 ET, using only closed bars.
# Each model says LONG / SHORT / NONE (+ a probability for the ML model). Two scores:
#  (1) call accuracy: was price higher/lower 60 min later?
#  (2) trading: one position at a time, stop 1.5 x ATR(5m), target 1.5 x ATR (1:1) or 3 x ATR (2:1), time stop 60 min, cost 1 pt.
import pandas as pd, numpy as np, zstandard, io
from sklearn.linear_model import LogisticRegression
fr=[]
for f in ['glbx-mdp3-20261016-20261030.ohlcv-1m.csv.zst','glbx-mdp3-20261029-20261030.ohlcv-1m.csv.zst']:
    raw=zstandard.ZstdDecompressor().decompressobj().decompress(open('../../data/live/new/'+f,'rb').read()); fr.append(pd.read_csv(io.BytesIO(raw)))
d=pd.concat(fr); d=d[d.symbol=='MNQZ6'].drop_duplicates('ts_event')
d.index=pd.DatetimeIndex(pd.to_datetime(d.ts_event,utc=True)).tz_convert('America/New_York'); d=d.sort_index()[['open','high','low','close','volume']]
m=d.resample('5min').agg({'open':'first','high':'max','low':'min','close':'last','volume':'sum'}).dropna()
m['sess']=[(t-pd.Timedelta(hours=18)).date() for t in m.index]
c,h,l,v=m.close,m.high,m.low,m.volume
m['atr']=(np.maximum(h-l,abs(h-c.shift()))).rolling(14).mean()
m['ema']=c.ewm(span=21,adjust=False).mean(); m['slope']=(m.ema-m.ema.shift(6))/m.atr
tp=(h+l+c)/3; m['vwap']=(tp*v).groupby(m.sess).cumsum()/v.groupby(m.sess).cumsum()
for k in (1,3,12): m[f'r{k}']=(c-c.shift(k))/m.atr
m['dv']=(c-m.vwap)/m.atr; m['de']=(c-m.ema)/m.atr
m['pos60']=(c-l.rolling(12).min())/(h.rolling(12).max()-l.rolling(12).min()+1e-9)
m['hr']=m.index.hour+m.index.minute/60; m['hs']=np.sin(2*np.pi*m.hr/24); m['hc']=np.cos(2*np.pi*m.hr/24)
m['volz']=(v-v.rolling(48).mean())/(v.rolling(48).std()+1e-9)
# swings (3/3 pivots, known 15 min later)
H,L=h.values,l.values; n=len(m); s_struct=np.zeros(n); lastLH=np.full(n,np.nan); lastHL=np.full(n,np.nan); ph=[];pl=[]
for i in range(n):
    k=i-3
    if k>=3:
        if H[k]==H[k-3:k+4].max(): ph.append(H[k])
        if L[k]==L[k-3:k+4].min(): pl.append(L[k])
    if len(ph)>=2 and len(pl)>=2:
        s_struct[i]=1 if (ph[-1]>ph[-2] and pl[-1]>pl[-2]) else (-1 if (ph[-1]<ph[-2] and pl[-1]<pl[-2]) else 0)
    lastLH[i]=ph[-1] if ph else np.nan; lastHL[i]=pl[-1] if pl else np.nan
m['struct']=s_struct; m['fwd']=c.shift(-12)-c           # 60-min forward change (only for scoring)
m['y']=(m.fwd>0).astype(int)
FEATS=['r1','r3','r12','dv','de','slope','pos60','hs','hc','volz','struct']
test=(m.index>=pd.Timestamp('2026-10-25 18:00',tz='America/New_York'))&m.fwd.notna()&m.atr.notna()
# ---- models: each returns +1/-1/0 using row i only (past data already baked into features)
def M_trend(r): return 1 if r.slope>0.5 else (-1 if r.slope<-0.5 else 0)
def M_meanrev(r): return -1 if r.r12>2 else (1 if r.r12<-2 else 0)
def M_vwap(r): return 1 if r.dv>0.5 else (-1 if r.dv<-0.5 else 0)
def M_struct(r): return int(r.struct)
def M_always_short(r): return -1
def M_breakdown(r,i): 
    lo=m.low.iloc[i-12:i].min(); hi=m.high.iloc[i-12:i].max()
    return -1 if r.close<lo else (1 if r.close>hi else 0)
# ML: logistic regression retrained before each session on all PRIOR sessions only
probs=pd.Series(np.nan,index=m.index)
sessions=sorted(m.sess[test].unique())
for s in sessions:
    tr=(m.sess<s)&m[FEATS].notna().all(1)&m.fwd.notna()
    # forward label must be fully known before session start: drop the last 12 bars before s
    idx=m.index[tr]; idx=idx[:-12] if len(idx)>12 else idx
    X=m.loc[idx,FEATS]; y=m.loc[idx,'y']
    mdl=LogisticRegression(C=0.5,max_iter=1000).fit(X,y)
    te=(m.sess==s)&test&m[FEATS].notna().all(1)
    probs[te]=mdl.predict_proba(m.loc[te,FEATS])[:,1]
m['p_up']=probs
def M_ml(r): 
    if np.isnan(r.p_up): return 0
    return 1 if r.p_up>0.58 else (-1 if r.p_up<0.42 else 0)
# pullback 61.8 (causal leg on 5m: A = high of last 24 bars, B = low after it), trend filter
def M_pullback(r,i):
    if i<30: return 0
    for side in (-1,1):
        if side*r.slope<=0: continue
        w=slice(i-24,i+1)
        if side<0:
            a=i-24+int(np.argmax(H[w])); A=H[a]
            if a>=i: continue
            b=a+1+int(np.argmin(L[a+1:i+1])); B=L[b]; leg=A-B
            if b>=i or leg<60: continue
            lvl=B+0.618*leg
            if H[i]>=lvl and r.close<lvl and r.close>B: return -1
        else:
            a=i-24+int(np.argmin(L[w])); A=L[a]
            if a>=i: continue
            b=a+1+int(np.argmax(H[a+1:i+1])); B=H[b]; leg=B-A
            if b>=i or leg<60: continue
            lvl=B-0.618*leg
            if L[i]<=lvl and r.close>lvl and r.close<B: return 1
    return 0
models={'1 Trend (EMA slope)':M_trend,'2 Fade the last hour':M_meanrev,'3 VWAP side':M_vwap,'4 Swing structure (HH/HL vs LH/LL)':M_struct,
        '5 Breakout of last hour high/low':M_breakdown,'6 Pullback 61.8 + trend':M_pullback,'7 ML probability (walk-forward)':M_ml,'0 Always short (benchmark)':M_always_short}
ti=np.where(test)[0]
rows=[]; trades_all={}
for name,fn in models.items():
    sig=np.array([fn(m.iloc[i],i) if fn.__code__.co_argcount==2 else fn(m.iloc[i]) for i in ti])
    fwd=m.fwd.values[ti]; called=sig!=0
    acc=(np.sign(fwd[called])==sig[called]).mean() if called.any() else np.nan
    for rr in (1.0,2.0):
        busy=-1; tr=[]
        for k,i in enumerate(ti):
            if i<=busy or sig[k]==0: continue
            side=sig[k]; e=m.close.iat[i]; a=m.atr.iat[i]; stop=e-side*1.5*a; tgt=e+side*1.5*rr*a; pnl=None
            for j in range(i+1,min(i+13,n)):
                if (side>0 and L[j]<=stop) or (side<0 and H[j]>=stop): pnl=-1.5*a; break
                if (side>0 and H[j]>=tgt) or (side<0 and L[j]<=tgt): pnl=1.5*rr*a; break
            if pnl is None: j=min(i+12,n-1); pnl=side*(m.close.iat[j]-e)
            tr.append((m.index[i],side,pnl-1)); busy=j
        T=pd.DataFrame(tr,columns=['t','side','pts']); trades_all[(name,rr)]=T
        pf=T.pts[T.pts>0].sum()/max(1e-9,-T.pts[T.pts<0].sum()) if len(T) else np.nan
        eq=T.pts.cumsum(); dd=(eq.cummax()-eq).max() if len(T) else 0
        rows.append(dict(model=name,calls_pct=round(called.mean()*100),call_accuracy=round(acc*100,1),RR=f'1:{rr:g}',trades=len(T),win=round((T.pts>0).mean()*100) if len(T) else 0,pts=round(T.pts.sum()),PF=round(pf,2),maxDD_pts=round(dd)))
R=pd.DataFrame(rows); pd.set_option('display.width',220)
print(R.sort_values(['RR','pts'],ascending=[True,False]).to_string(index=False))
# ML calibration
te=m[test&m.p_up.notna()]
print('\nML calibration (this week): predicted P(up) bucket -> actual share up 60 min later')
print(te.groupby(pd.cut(te.p_up,[0,.35,.42,.5,.58,.65,1])).y.agg(['mean','size']).round(2))
# per day for the top models
for key in [('6 Pullback 61.8 + trend',1.0),('7 ML probability (walk-forward)',1.0),('0 Always short (benchmark)',1.0)]:
    T=trades_all[key]; T['day']=T.t.dt.strftime('%a %m-%d'); print('\n',key[0],'1:1 by day:',T.groupby('day').pts.sum().round().to_dict())
R.to_csv('wf_results.csv',index=False)
