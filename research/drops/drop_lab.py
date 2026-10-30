# What comes before a big MNQ drop? Downtrend pullback-break study on 5m bars (all hours), 2021-10..2026-10.
import pandas as pd, numpy as np, sys
df=pd.read_csv('../../data/raw/MNQ_5m_cont.csv.gz')
extra=sys.argv[1] if len(sys.argv)>1 else None
df['dt']=pd.to_datetime(df.t,unit='s',utc=True).dt.tz_convert('America/New_York')
if extra:
    x=pd.read_csv(extra,index_col=0,parse_dates=True)
    x.index=pd.to_datetime(x.index,utc=True).tz_convert('America/New_York')
    x5=x.resample('5min',label='left',closed='left').agg({'open':'first','high':'max','low':'min','close':'last','volume':'sum'}).dropna()
    x5=x5[x5.index>df.dt.max()]
    add=pd.DataFrame({'dt':x5.index,'o':x5.open.values,'h':x5.high.values,'l':x5.low.values,'c':x5.close.values,'v':x5.volume.values})
    df=pd.concat([df[['dt','o','h','l','c','v']],add],ignore_index=True)
df=df.reset_index(drop=True)
o,h,l,c,v=[df[k].values for k in 'ohlcv']; n=len(df)
hm=(df.dt.dt.hour*100+df.dt.dt.minute).values
# session id: new session at 18:00 ET
sess=np.cumsum(np.r_[1,(np.diff(df.dt.values).astype('timedelta64[m]').astype(int)>60)|((hm[1:]>=1800)&(hm[:-1]<1800))])
tp=(h+l+c)/3; vw=np.zeros(n); pv=0; vv=0
for i in range(n):
    if i==0 or sess[i]!=sess[i-1]: pv=0; vv=0
    pv+=tp[i]*v[i]; vv+=v[i]; vw[i]=pv/vv if vv>0 else c[i]
ema=pd.Series(c).ewm(span=21,adjust=False).mean().values
tr=np.maximum(h-l,np.maximum(abs(h-np.r_[c[0],c[:-1]]),abs(l-np.r_[c[0],c[:-1]])))
atr=pd.Series(tr).rolling(14).mean().values
vavg=pd.Series(v).rolling(20).mean().values
slope=(ema-np.r_[np.full(6,np.nan),ema[:-6]])/atr
rows=[]
i=40
while i<n-30:
    # downtrend context
    if not(c[i]<vw[i] and slope[i]<-0.5): i+=1; continue
    # pullback: last 2..8 bars rallied off a leg low and tagged EMA21 or VWAP, and this bar breaks the prior bar's low
    win=range(i-8,i)
    lowk=min(win,key=lambda k:l[k])                 # leg low before pullback
    if lowk>=i-1: i+=1; continue
    pbh_k=max(range(lowk+1,i),key=lambda k:h[k])     # pullback high
    pbh=h[pbh_k]
    legstart=max(range(lowk-12,lowk),key=lambda k:h[k]); legH=h[legstart]
    leg=legH-l[lowk]
    if leg<1.5*atr[i]: i+=1; continue
    depth=(pbh-l[lowk])/leg
    tagged=pbh>=min(ema[i],vw[i])-0.15*atr[i]
    trig=c[i]<l[i-1] and c[i]<o[i]
    if not trig or depth<0.2: i+=1; continue
    e=c[i]; stop=pbh+0.25; r=stop-e
    if r<=0 or r>3*atr[i]: i+=1; continue
    pbvol=np.mean(v[lowk+1:i]); legvol=np.mean(v[legstart:lowk+1])
    ext=(ema[i]-c[i])/atr[i]
    # outcome on 5m bars, stop first if same bar
    res=None; mfe=0
    for j in range(i+1,min(i+25,n)):
        if sess[j]!=sess[i]: res=(e-c[j-1])/r; break
        if h[j]>=stop: res=-1.0; break
        mfe=max(mfe,(e-l[j])/r)
        if l[j]<=e-2*r: res=2.0; break
    if res is None: res=(e-c[min(i+24,n-1)])/r
    rows.append(dict(dt=df.dt[i],hm=hm[i],R=res,mfe=mfe,depth=depth,tagged=tagged,volr=pbvol/legvol,pbbars=i-lowk-1,ext=ext,risk_pts=r,legatr=leg/atr[i],year=df.dt[i].year))
    i+=3
t=pd.DataFrame(rows)
t.to_pickle('drop_trades.pkl')
def st(g):
    w=g.R[g.R>0].sum(); L=-g.R[g.R<0].sum()
    return pd.Series(dict(n=len(g),win=(g.R>0).mean(),hit2R=(g.R>=2).mean(),avgR=g.R.mean(),PF=w/L if L else np.nan))
print('ALL',st(t).round(3).to_dict())
for name,col,bins in [('pullback depth',t.depth,[0.2,0.38,0.5,0.62,0.8,10]),('pullback vol / leg vol',t.volr,[0,0.5,0.7,0.9,1.2,10]),('pullback bars',t.pbbars,[0,2,3,5,9]),('tagged EMA/VWAP',t.tagged,None),('dist below EMA at entry (ATR)',t.ext,[-5,0,0.5,1,1.5,10]),('risk pts',t.risk_pts,[0,10,20,30,50,500])]:
    g=t.groupby(pd.cut(col,bins) if bins else col,observed=True).apply(st)
    print('\n==',name); print(g.round(3).to_string())
t['sess']=np.where((t.hm>=930)&(t.hm<1600),'RTH',np.where((t.hm>=300)&(t.hm<930),'London/pre','Asia/eve'))
print('\n== session'); print(t.groupby('sess').apply(st).round(3).to_string())
print('\n== year'); print(t.groupby('year').apply(st).round(3).to_string())
