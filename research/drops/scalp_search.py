# 1-minute scalps (hold 1-10 min) on MNQ RTH 1m, 2021-10..2026-10-29. Cost 1 pt per round trip.
# Train <2025, test 2025..2026-10-20, recent 2026-10-21..29 (MNQZ6).
import numpy as np, pandas as pd, itertools
days=[]
for line in open('../../data/raw/mnq_rth_1m.txt'):
    dd,*bars=line.strip().split('|'); a=np.array([[int(x) for x in b.split(',')] for b in bars],float); a[:,1:]/=4; days.append((dd,a[:,1],a[:,2],a[:,3],a[:,4],a[:,0]))
d=pd.read_csv('../../data/live/new/glbx-mdp3-20261016-20261030.ohlcv-1m.csv'); d=d[d.symbol=='MNQZ6']
d['dt']=pd.to_datetime(d.ts_event,utc=True).dt.tz_convert('America/New_York'); d=d.set_index('dt').sort_index()
for day,g in d.groupby(d.index.date):
    k=str(day).replace('-','')
    if k<='20261020': continue
    g=g.between_time('09:30','15:59')
    if len(g)<300: continue
    days.append((k,g.open.values,g.high.values,g.low.values,g.close.values,(g.index.hour*100+g.index.minute).values))
COST=1.0
def per(dd): return 0 if dd<'20250101' else (1 if dd<='20261020' else 2)
def run(strat,stopPts,tgtR,hold,trendTF,win,sides):
    out=[]
    for dd,o,h,l,c,t in days:
        n=len(c)
        if n<120: continue
        e9=pd.Series(c).ewm(span=9,adjust=False).mean().values; e20=pd.Series(c).ewm(span=20,adjust=False).mean().values
        vw=np.cumsum((h+l+c)/3)/np.arange(1,n+1)
        e15=pd.Series(c).ewm(span=21*15,adjust=False).mean().values      # ~15m EMA21 on 1m
        sl20=(e20-np.r_[np.full(5,np.nan),e20[:-5]])
        i=30; 
        while i<n-hold-1:
            tt=t[i]
            if (win=='am' and not(930<=tt<1100)) or (win=='rth' and not(930<=tt<1555)) or (win=='pm' and not(1300<=tt<1555)): i+=1; continue
            took=False
            for side in sides:
                trend=side*(c[i]-vw[i])>0 and side*sl20[i]>0 and (not trendTF or side*(c[i]-e15[i])>0)
                if not trend: continue
                sig=False
                if strat=='ema9_pull':       # pullback touches EMA9 then closes back with the trend
                    sig=((side<0 and h[i]>=e9[i] and c[i]<e9[i] and c[i]<o[i]) or (side>0 and l[i]<=e9[i] and c[i]>e9[i] and c[i]>o[i]))
                elif strat=='ema20_pull':
                    sig=((side<0 and h[i]>=e20[i] and c[i]<e20[i] and c[i]<o[i]) or (side>0 and l[i]<=e20[i] and c[i]>e20[i] and c[i]>o[i]))
                elif strat=='micro_break':   # close beyond last 5-bar extreme with the trend
                    sig=(side<0 and c[i]<l[i-5:i].min()) or (side>0 and c[i]>h[i-5:i].max())
                elif strat=='vwap_reject':   # tag VWAP from the trend side and close back away
                    sig=((side<0 and h[i]>=vw[i] and c[i]<vw[i]-0.25) or (side>0 and l[i]<=vw[i] and c[i]>vw[i]+0.25))
                if not sig: continue
                e=c[i]
                stop=(max(h[i],h[i-1])+0.25 if side<0 else min(l[i],l[i-1])-0.25) if stopPts=='bar' else e-side*stopPts
                r=abs(e-stop)
                if r<2 or r>40: continue
                res=None
                for j in range(i+1,min(i+1+hold,n)):
                    if (side<0 and h[j]>=stop) or (side>0 and l[j]<=stop): res=-r; break
                    if (side<0 and l[j]<=e-tgtR*r) or (side>0 and h[j]>=e+tgtR*r): res=tgtR*r; break
                if res is None: res=side*(c[min(i+hold,n-1)]-e)
                out.append(((res-COST)/r,res-COST,per(dd),dd)); took=True; break
            i+= (hold if took else 1)
    return out
def st(o,p):
    x=np.array([a[1] for a in o if a[2]==p]); R=np.array([a[0] for a in o if a[2]==p])
    if len(x)==0: return (0,None,None)
    return (len(x), round(x[x>0].sum()/max(1e-9,-x[x<0].sum()),2), round(x.mean(),2))
rows=[]
for strat,stopPts,tgtR,hold,tf,win,sides in itertools.product(['ema9_pull','ema20_pull','micro_break','vwap_reject'],['bar',8,15],[1.0,1.5,2.0],[5,10],[True,False],['am','rth'],[(-1,),(-1,1)]):
    o=run(strat,stopPts,tgtR,hold,tf,win,sides)
    ndays=len(set(a[3] for a in o))
    rows.append(dict(strat=strat,stop=stopPts,tgtR=tgtR,hold=hold,trend15=tf,win=win,sides='short' if sides==(-1,) else 'both',
        train=st(o,0),test=st(o,1),recent=st(o,2),per_day=round(len(o)/max(1,len(days)),2)))
    print(rows[-1],flush=True)
pd.DataFrame(rows).to_pickle('scalp_search.pkl')
