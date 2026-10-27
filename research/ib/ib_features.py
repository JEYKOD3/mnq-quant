# One row per IB trade (variant C rules: 1.5R target, lock +1R after 1R), with features known AT ENTRY.
import pickle, gzip, numpy as np, pandas as pd
days=pickle.load(open('/home/claude/mnq-quant/research/ib/days.pkl','rb'))
c5=pd.read_csv(gzip.open('/home/claude/mnq-quant/data/raw/MNQ_5m_cont.csv.gz','rt'))
v5=dict(zip(c5.t.values//300, c5.v.values)); vavg=c5.v.rolling(20).mean().shift(1); va=dict(zip(c5.t.values//300, vavg.values))
TICK=0.25; SLIP=0.25
rows=[]
adr=[]
for k,(d,ts,o,h,l,c,tr) in enumerate(days):
    rng=h.max()-l.min(); adr.append(rng)
for k,(d,ts,o,h,l,c,tr) in enumerate(days):
    if k<21: continue
    ADR=np.mean(adr[k-20:k]); P=days[k-1]; pdh,pdl,pdc=P[3].max(),P[4].min(),P[5][-1]
    n=len(ts)
    trng=np.maximum(h[1:],c[:-1])-np.minimum(l[1:],c[:-1]); trng=np.r_[h[0]-l[0],trng]
    atr=pd.Series(trng).ewm(alpha=1/14).mean().values
    ema=pd.Series(c).ewm(span=20).mean().values
    armed=False; tDir=0; nIn=0; todayRes=[]
    for i in range(1,n):
        sig=False
        if tDir!=0:
            hitS = l[i]<=sL if tDir>0 else h[i]>=sL
            hitT = h[i]>=tT if tDir>0 else l[i]<=tT
            res=None
            if hitS: res=(sL-SLIP*tDir-e)*tDir/r
            elif hitT: res=1.5
            elif i==n-1: res=(c[i]-e)*tDir/r
            else:
                fav=(h[i]-e if tDir>0 else e-l[i])/r; mfe=max(mfe,fav)
                if not locked and fav>=1: locked=True; sL=e+tDir*r
            if res is not None:
                row['res']=res; row['mfe']=max(mfe,(h[i]-e if tDir>0 else e-l[i])/r if hitT else mfe); row['hit1']=locked or res>=1
                rows.append(row); todayRes.append(res); tDir=0
        if armed:
            bl=min(o[i],c[i]); bh=max(o[i],c[i]); up=bl>mbH; dn=bh<mbL
            if up or dn:
                side=1 if up else -1; armed=False; ee=c[i]; ss=mbL-TICK if side>0 else mbH+TICK; rr=abs(ee-ss)
                if side==tr[i] and tDir==0 and 5<=rr<=80 and i<n-1:
                    tDir=side; e=ee; sL=ss; r=rr; tT=e+1.5*side*r; locked=False; mfe=0; sig=True
                    hi_so=h[:i+1].max(); lo_so=l[:i+1].min()
                    lv={'pdh':pdh,'pdl':pdl,'pdc':pdc,'open':o[0],'hod':h[:i].max(),'lod':l[:i].min()}
                    ahead=[(v-e)*side/r for v in lv.values() if (v-e)*side>0]
                    behind=[(e-v)*side/r for v in lv.values() if (e-v)*side>=0]
                    b5=ts[i]//300
                    rows_feat=dict(
                        day=d, k=k, side=side, mins=i, r_pts=rr, r_atr=rr/atr[i], mother_atr=(mbH-mbL)/atr[i],
                        n_inside=i-mbBar-1, bo_body=abs(c[i]-o[i])/max(h[i]-l[i],TICK), bo_range_atr=(h[i]-l[i])/atr[i],
                        bo_ext=(c[i]-(mbH if side>0 else mbL))*side/r, ema_dist=(c[i]-ema[i])*side/atr[i],
                        lvl_ahead=min(ahead) if ahead else 9, lvl_behind=min(behind) if behind else 9,
                        day_rng_adr=(hi_so-lo_so)/ADR, pos_in_day=((c[i]-lo_so)/max(hi_so-lo_so,TICK)) if side>0 else ((hi_so-c[i])/max(hi_so-lo_so,TICK)),
                        open_move=(c[i]-o[0])*side/ADR, gap=(o[0]-pdc)*side/ADR,
                        vol_rel=(v5.get(b5,np.nan)/va.get(b5,np.nan)) if va.get(b5) else np.nan,
                        prev_res=todayRes[-1] if todayRes else np.nan, n_prev=len(todayRes),
                        dow=pd.Timestamp(d).dayofweek, atr_pts=atr[i], adr=ADR,
                        trend3=0)
                    row=rows_feat
            elif i-mbBar>30: armed=False
        if not armed and tDir==0 and h[i]<=h[i-1] and l[i]>=l[i-1] and not sig:
            armed=True; mbH=h[i-1]; mbL=l[i-1]; mbBar=i-1
df=pd.DataFrame(rows); df.to_pickle('/home/claude/mnq-quant/research/ib/trades.pkl')
print(len(df), df.res.mean(), df.hit1.mean())
