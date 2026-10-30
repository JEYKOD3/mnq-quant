# Edge search on MNQ 5m, all hours, 2021-10 .. 2026-10-30 (5y Databento cont + Oct 16-30 MNQZ6).
# Costs: 1 pt per round trip (commission + slippage). Train < 2025, test 2025-01 .. 2026-10-15, recent = 2026-10-16 .. 30.
import pandas as pd, numpy as np, itertools, sys
a=pd.read_csv('../../data/raw/MNQ_5m_cont.csv.gz'); a['dt']=pd.to_datetime(a.t,unit='s',utc=True).dt.tz_convert('America/New_York')
a=a.rename(columns={'o':'open','h':'high','l':'low','c':'close','v':'volume'}).set_index('dt')[['open','high','low','close','volume']]
b=pd.read_csv('mnq_5m_oct16_30.csv',index_col=0); b.index=pd.to_datetime(b.index,utc=True).tz_convert('America/New_York')
df=pd.concat([a[a.index<b.index.min()],b]).sort_index()
o,h,l,c,v=[df[k].values for k in ['open','high','low','close','volume']]; n=len(c)
t=df.index; hm=(t.hour*100+t.minute).values; dnum=(t.year*10000+t.month*100+t.day).values
period=np.where(t<pd.Timestamp('2025-01-01',tz='America/New_York'),0,np.where(t<pd.Timestamp('2026-10-16',tz='America/New_York'),1,2))
ema=pd.Series(c).ewm(span=21,adjust=False).mean().values
atr=pd.Series(np.maximum(h-l,np.abs(h-np.r_[c[0],c[:-1]]))).rolling(14).mean().values
slope=(ema-np.r_[np.full(6,np.nan),ema[:-6]])/atr
vavg=pd.Series(v).rolling(20).mean().values
# 1h EMA trend (12 x 5m bars ~ EMA21 on 1h approximated by EMA 252 on 5m)
ema1h=pd.Series(c).ewm(span=252,adjust=False).mean().values
COST=1.0
def win_ok(x,w):
    if w=='all': return True
    if w=='am': return 700<=x<1045
    if w=='rth': return 930<=x<1600
    if w=='am+pm': return (700<=x<1045) or (1500<=x<1600)
def manage(i,side,e,stop,tgtR,trail,maxbars=36):
    r=abs(e-stop); best=0
    for j in range(i+1,min(i+maxbars,n)):
        if 1645<=hm[j]<1800: return side*(c[j-1]-e)-COST, r
        if (side<0 and h[j]>=stop) or (side>0 and l[j]<=stop): return side*(stop-e)-COST, r
        fav=side*((l[j] if side<0 else h[j])-e)
        if tgtR and fav>=tgtR*r: return tgtR*r-COST, r
        best=max(best,fav)
        if trail and best>=1*r:                       # after +1R trail stop at entry then 1R behind best
            ns=e-side*(best-1*r)*(-1) if False else (e+side*(best-1*r))
            if side<0: stop=min(stop,e-(best-1*r))
            else: stop=max(stop,e+(best-1*r))
    j=min(i+maxbars,n-1); return side*(c[j]-e)-COST, r
def stats(res,per):
    out={}
    for p,name in [(0,'train'),(1,'test'),(2,'recent')]:
        R=np.array([x for x,q in zip(res,per) if q==p])
        if len(R)==0: out[name]=(0,np.nan,np.nan); continue
        pf=R[R>0].sum()/max(1e-9,-R[R<0].sum()); out[name]=(len(R),round(pf,2),round(R.mean(),3))
    return out
rows=[]
# ---------- A: breakdown / breakout momentum ----------
def stratA(N,volx,win,stopA,tgtR,trail,trend,sides):
    res=[];per=[];last=-1
    for i in range(300,n-2):
        if i<=last or np.isnan(atr[i]) or not win_ok(hm[i],win): continue
        lo=l[i-N:i].min(); hi=h[i-N:i].max()
        for side in sides:
            brk=(c[i]<lo) if side<0 else (c[i]>hi)
            if not brk or v[i]<volx*vavg[i]: continue
            if trend and side*(c[i]-ema1h[i])<=0: continue
            e=c[i]; stop=e-side*stopA*atr[i]
            pnl,r=manage(i,side,e,stop,tgtR,trail); res.append(pnl/r); per.append(period[i]); last=i+3; break
    return res,per
for N,volx,win,stopA,tgtR,trail,trend,sides in itertools.product([12,24],[0,1.5],['all','am'],[1.0,2.0],[2.0,None],[True],[True,False],[(-1,),(-1,1)]):
    if tgtR is None and not trail: continue
    res,per=stratA(N,volx,win,stopA,tgtR,trail,trend,sides)
    s=stats(res,per); rows.append(dict(strat='A_break',N=N,volx=volx,win=win,stopATR=stopA,tgtR=tgtR,trend1h=trend,sides='short' if sides==(-1,) else 'both',**{k:v for k,v in s.items()}))
    print(rows[-1],flush=True)
# ---------- B: wait for the bounce, enter on roll-over ----------
def stratB(kmin,win,tgt,trend1h,sides):
    res=[];per=[];last=-1
    i=300
    while i<n-50:
        done=False
        for side in sides:
            # trend: 5m EMA falling and price below (shorts) / mirror
            if not(side*slope[i]>0.5 and side*(c[i]-ema[i])>0): continue
            if trend1h and side*(c[i]-ema1h[i])<=0: continue
            ext=l[i] if side<0 else h[i]
            if not((side<0 and l[i]==l[i-6:i+1].min()) or (side>0 and h[i]==h[i-6:i+1].max())): continue
            a0=atr[i]; bx=ext
            for j in range(i+1,min(i+24,n-2)):
                if (side<0 and l[j]<ext) or (side>0 and h[j]>ext): break      # new extreme before setup: no trade
                bx=max(bx,h[j]) if side<0 else min(bx,l[j])
                k=abs(bx-ext)/a0
                if k>3.0: break
                # roll-over: bounce reached kmin ATR, then a 5m bar closes back in trend direction below prior bar low
                if k>=kmin and win_ok(hm[j],win) and ((side<0 and c[j]<l[j-1] and c[j]<o[j]) or (side>0 and c[j]>h[j-1] and c[j]>o[j])):
                    e=c[j]; stop=bx+side*-0.25*a0*(-1) if False else (bx+0.25*a0 if side<0 else bx-0.25*a0)
                    if tgt=='2R': pnl,r=manage(j,side,e,stop,2.0,False)
                    elif tgt=='3R': pnl,r=manage(j,side,e,stop,3.0,False)
                    else: pnl,r=manage(j,side,e,stop,None,True)
                    res.append(pnl/r); per.append(period[j]); last=j; done=True; break
            if done: break
        i=(last+3) if done else i+1
    return res,per
for kmin,win,tgt,tr,sides in itertools.product([0.5,1.0,1.5],['all','am','rth'],['2R','3R','trail'],[True,False],[(-1,),(-1,1)]):
    res,per=stratB(kmin,win,tgt,tr,sides)
    s=stats(res,per); rows.append(dict(strat='B_rollover',kmin=kmin,win=win,tgt=tgt,trend1h=tr,sides='short' if sides==(-1,) else 'both',**s))
    print(rows[-1],flush=True)
pd.DataFrame(rows).to_pickle('edge_search.pkl')
