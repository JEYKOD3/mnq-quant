# LuxAlgo Fair Value Gap (threshold 0) on the 1m chart + Jey's Playbook trend banner, MNQ.
# 5y RTH 1m (2021-10..2026-10-20, VWAP = equal-weight session average: no volume in that file) + Oct 21-29 MNQZ6 all-hours 1m (true VWAP).
# Questions: after price pulls back into an FVG, when does it reject (continue) vs fill (close beyond the far edge = LuxAlgo mitigation)?
#            and is there a tradable entry (edge / middle / confirmation) with the banner as filter?
import numpy as np, pandas as pd, pickle
COST=1.0
# ---- higher-timeframe bias (15m, 1h, 4h close vs EMA21, previous closed bar) from 5m all-hours data ----
a=pd.read_csv('../../data/raw/MNQ_5m_cont.csv.gz'); a.index=pd.DatetimeIndex(pd.to_datetime(a.t,unit='s',utc=True)).tz_convert('America/New_York')
b=pd.read_csv('mnq_5m_oct16_30.csv',index_col=0); b.index=pd.to_datetime(b.index,utc=True).tz_convert('America/New_York')
cl=pd.concat([a.c[a.index<b.index.min()],b.close]).sort_index()
bias=pd.DataFrame(index=cl.index)
for tf,name in [('15min','d1'),('60min','d2'),('240min','d3')]:
    r=cl.resample(tf,label='right',closed='left').last().dropna()
    d=np.where(r>r.ewm(span=21,adjust=False).mean(),1,-1)
    s=pd.Series(d,index=r.index)          # value known at bar close (label right) = previous closed bar for later times
    bias[name]=s.reindex(bias.index,method='ffill')
bias['trend']=np.where(bias.d1+bias.d2+bias.d3>0,1,-1)
def htf_at(ts): 
    k=bias.index.searchsorted(ts,side='right')-1
    return int(bias.trend.iat[k]) if k>=0 else 0
# ---- 1m days ----
days=[]
for line in open('../../data/raw/mnq_rth_1m.txt'):
    dd,*bars=line.strip().split('|'); x=np.array([[int(v) for v in bb.split(',')] for bb in bars],float); x[:,1:]/=4
    tm=x[:,0].astype(int); ts=pd.to_datetime(dd)+pd.to_timedelta(tm//100,'h')+pd.to_timedelta(tm%100,'min')
    days.append((dd,ts.tz_localize('America/New_York'),x[:,1],x[:,2],x[:,3],x[:,4],None))
d=pd.read_csv('../../data/live/new/glbx-mdp3-20261016-20261030.ohlcv-1m.csv'); d=d[d.symbol=='MNQZ6']
d.index=pd.DatetimeIndex(pd.to_datetime(d.ts_event,utc=True)).tz_convert('America/New_York'); d=d.sort_index()
sess=(d.index-pd.Timedelta(hours=18)).date      # globex session id (18:00 start)
for s_,g in d.groupby(sess):
    if str(s_)<'2026-10-20': continue
    days.append((str(s_).replace('-','')+'g',g.index,g.open.values,g.high.values,g.low.values,g.close.values,g.volume.values))
def per(dd): return 0 if dd<'20250101' else (1 if dd[:8]<='20261020' and not dd.endswith('g') else 2)
rows=[]
for dd,ts,o,h,l,c,v in days:
    n=len(c)
    if n<120: continue
    tp=(h+l+c)/3; vw=np.cumsum(tp*(v if v is not None else 1))/np.cumsum(v if v is not None else np.ones(n))
    e21=pd.Series(c).ewm(span=21,adjust=False).mean().values
    tr=np.maximum(h-l,np.abs(h-np.r_[c[0],c[:-1]])); atr=pd.Series(tr).ewm(alpha=1/14,adjust=False).mean().values
    slope=(e21-np.r_[np.full(10,np.nan),e21[:-10]])/np.maximum(atr,.25)
    cross=np.r_[0,np.sign(c[1:]-e21[1:])!=np.sign(c[:-1]-e21[:-1])].astype(int); xN=pd.Series(cross).rolling(30,min_periods=1).sum().values
    # swings: pivots 5/5 (confirmed 5 bars later)
    H0=H1=L0=L1=np.nan; struct=np.zeros(n)
    for i in range(n):
        k=i-5
        if k>=5:
            if h[k]==h[k-5:k+6].max(): H0,H1=H1,h[k]
            if l[k]==l[k-5:k+6].min(): L0,L1=L1,l[k]
        if not np.isnan(H0) and not np.isnan(L0):
            hh=H1>H0; hl=L1>L0; struct[i]=1 if hh and hl else (-1 if (not hh and not hl) else 0)
    nowS=np.where((xN>=5)&(np.abs(slope)<1),0,np.where(slope>1,1,np.where(slope<-1,-1,2)))
    now=np.where((struct<0)&((c<vw)|(slope<=0)),-1,np.where((struct>0)&((c>vw)|(slope>=0)),1,nowS))
    trend=np.array([htf_at(t) for t in ts])
    reg=np.where(now==0,0,np.where(trend>0,np.where(now==1,1,np.where(now==2,2,np.where(c>vw,3,4))),np.where(now==-1,-1,np.where(now==2,-2,np.where(c<vw,-3,-4)))))
    hm=(ts.hour*100+ts.minute).values
    for i in range(2,n-3):
        for side in (-1,1):   # side = trade direction (bearish FVG -> short)
            if side<0 and not(h[i]<l[i-2] and c[i-1]<l[i-2]): continue
            if side>0 and not(l[i]>h[i-2] and c[i-1]>h[i-2]): continue
            top,bot=(l[i-2],h[i]) if side<0 else (l[i],h[i-2])     # zone [bot,top]
            size=top-bot; a_=atr[i]
            if size<=0: continue
            near=bot if side<0 else top; far=top if side<0 else bot; ext=l[i-2:i+1].min() if side<0 else h[i-2:i+1].max()
            # find first touch
            j=None
            for k in range(i+1,min(i+120,n)):
                if side<0 and c[k]>top: break                 # mitigated without a clean touch first (gap up through)
                if side>0 and c[k]<bot: break
                if (side<0 and h[k]>=near) or (side>0 and l[k]<=near): j=k; break
                if (side<0 and l[k]<ext) or (side>0 and h[k]>ext): ext=l[k] if side<0 else h[k]
            if j is None: continue
            # descriptive outcome after touch: new extreme beyond ext first (continuation) vs close beyond far edge (fill)
            out='none'
            for k in range(j,min(j+120,n)):
                if (side<0 and c[k]>far) or (side>0 and c[k]<far): out='fill'; break
                if k>j and ((side<0 and l[k]<ext) or (side>0 and h[k]>ext)): out='cont'; break
            # trades
            res={}
            for entry in ('edge','mid','confirm'):
                if entry=='edge': e=near; k0=j
                elif entry=='mid':
                    e=(top+bot)/2; k0=None
                    for k in range(j,min(j+30,n)):
                        if (side<0 and c[k]>top) or (side>0 and c[k]<bot): break
                        if (side<0 and h[k]>=e) or (side>0 and l[k]<=e): k0=k; break
                    if k0 is None: continue
                else:
                    k0=None
                    for k in range(j,min(j+5,n)):
                        if (side<0 and c[k]>top) or (side>0 and c[k]<bot): break
                        if (side<0 and c[k]<near and c[k]<o[k]) or (side>0 and c[k]>near and c[k]>o[k]): k0=k; break
                    if k0 is None: continue
                    e=c[k0]
                for stopm in ('far','far+0.5atr'):
                    stop=far-side*(0.25 if stopm=='far' else 0.5*a_)
                    r=abs(e-stop)
                    if r<1: continue
                    tgts={'1R':e+side*r,'1.5R':e+side*1.5*r,'2R':e+side*2*r,'ext':ext}
                    for tn,tg in tgts.items():
                        if side*(tg-e)<=0.5: continue
                        pnl=None; start=k0 if entry=='confirm' else k0
                        for k in range(start+(1 if entry=='confirm' else 0),min(k0+30,n)):
                            if entry!='confirm' and k==k0:
                                # same bar as fill: only the stop can be judged conservatively
                                if (side<0 and h[k]>=stop) or (side>0 and l[k]<=stop): pnl=-r; break
                                continue
                            if (side<0 and h[k]>=stop) or (side>0 and l[k]<=stop): pnl=-r; break
                            if (side<0 and l[k]<=tg) or (side>0 and h[k]>=tg): pnl=abs(tg-e); break
                        if pnl is None: pnl=side*(c[min(k0+30,n-1)]-e)
                        res[f'{entry}|{stopm}|{tn}']=(pnl-COST)/r
            rows.append(dict(day=dd,per=per(dd),side=side,hm=hm[j],reg=reg[j],trend=trend[j],now=now[j],struct=struct[j],vwside=int(np.sign(c[j]-vw[j])),
                             size_atr=size/max(a_,.25),age=j-i,out=out,**res))
df=pd.DataFrame(rows); df.to_pickle('fvg_rows.pkl'); print('FVG touches',len(df))
