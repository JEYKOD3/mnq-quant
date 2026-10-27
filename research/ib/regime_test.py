import pickle, gzip, numpy as np, pandas as pd
days=pickle.load(open('days.pkl','rb'))
c5=pd.read_csv(gzip.open('/home/claude/mnq-quant/data/raw/MNQ_5m_cont.csv.gz','rt')); v5=dict(zip(c5.t.values//300, c5.v.values))
TICK=.25; SLIP=.25; FEE=1.0
def regimes(ts,o,h,l,c,tr):
    n=len(c); e21=pd.Series(c).ewm(span=21,adjust=False).mean().values
    trng=np.maximum(h,np.r_[c[0],c[:-1]])-np.minimum(l,np.r_[c[0],c[:-1]]); atr=pd.Series(trng).ewm(alpha=1/14,adjust=False).mean().values
    slope=np.r_[np.zeros(10),(e21[10:]-e21[:-10])]/np.maximum(atr,TICK)
    vol=np.array([v5.get(t//300,1)/5 for t in ts]); hlc=(h+l+c)/3; vw=np.cumsum(hlc*vol)/np.cumsum(vol)
    above=(c>e21).astype(int); cr=np.r_[0,np.abs(np.diff(above))]; xN=pd.Series(cr).rolling(30,min_periods=1).sum().values
    now=np.where((xN>=5)&(np.abs(slope)<1),0,np.where(slope>1,1,np.where(slope<-1,-1,2)))
    reg=np.zeros(n,int)
    for i in range(n):
        if now[i]==0: reg[i]=0
        elif tr[i]>0: reg[i]= 1 if now[i]==1 else 2 if now[i]==2 else (3 if c[i]>vw[i] else 4)
        else: reg[i]= -1 if now[i]==-1 else -2 if now[i]==2 else (-3 if c[i]<vw[i] else -4)
    return reg
NAME={1:'STRONG',2:'WEAK',3:'PULLBACK',4:'BREAKING',0:'SIDEWAYS'}
rows=[]; split=int(len(days)*.7)
for k,(d,ts,o,h,l,c,tr) in enumerate(days):
    reg=regimes(ts,o,h,l,c,tr); n=len(c)
    # ---- IB (variant C) on 1m
    armed=False; tDir=0
    for i in range(1,n):
        sig=False
        if tDir!=0:
            hS= l[i]<=sL if tDir>0 else h[i]>=sL; hT= h[i]>=tT if tDir>0 else l[i]<=tT; x=None
            if hS: x=sL-SLIP*tDir
            elif hT: x=tT
            elif i==n-1: x=c[i]
            elif not lk and ((h[i]-e) if tDir>0 else (e-l[i]))>=r: lk=True; sL=e+tDir*r
            if x is not None:
                pts=(x-e)*tDir; rows.append(('IB',k>=split,rg,pts/r,pts*2-FEE)); tDir=0
        if armed:
            bl=min(o[i],c[i]); bh=max(o[i],c[i]); up=bl>mbH; dn=bh<mbL
            if up or dn:
                side=1 if up else -1; armed=False; ee=c[i]; ss=mbL-TICK if side>0 else mbH+TICK; rr=abs(ee-ss)
                if side==tr[i] and tDir==0 and 5<=rr<=80 and i<n-1:
                    tDir=side; e=ee; sL=ss; r=rr; tT=e+1.5*side*r; lk=False; sig=True; rg=abs(reg[i]) if reg[i]!=0 else 0
            elif i-mbBar>30: armed=False
        if not armed and tDir==0 and h[i]<=h[i-1] and l[i]>=l[i-1] and not sig:
            armed=True; mbH=h[i-1]; mbL=l[i-1]; mbBar=i-1
    # ---- ORB retest (15m OR, body>=0.5, other-side stop, 2R, lock) signals on 5m closes, managed on 1m
    n5=n//5; O5=o[:n5*5:5]; H5=h[:n5*5].reshape(-1,5).max(1); L5=l[:n5*5].reshape(-1,5).min(1); C5=c[4:n5*5:5]
    ORH=H5[:3].max(); ORL=L5[:3].min(); W=ORH-ORL; arm=0; tch=False
    for j in range(3,n5):
        if 570+5*j>=780: break
        if arm==0:
            if C5[j]>ORH: arm=1; tch=False
            elif C5[j]<ORL: arm=-1; tch=False
            continue
        if (arm>0 and C5[j]<ORH) or (arm<0 and C5[j]>ORL): arm=0; continue
        if (arm>0 and L5[j]<=ORH+.1*W) or (arm<0 and H5[j]>=ORL-.1*W): tch=True
        rgx=H5[j]-L5[j]; strong=rgx>0 and abs(C5[j]-O5[j])>=.5*rgx and ((C5[j]>O5[j]) if arm>0 else (C5[j]<O5[j]))
        if tch and strong:
            side=arm; e=C5[j]; s=ORL-TICK if side>0 else ORH+TICK; r=abs(e-s); sL=s; tT=e+2*side*r; lk=False; x=None
            ie=j*5+4; rgv=reg[ie]; rg = 0 if rgv==0 else (abs(rgv) if np.sign(rgv)==side else -abs(rgv))  # negative = regime against the trade
            for i in range(ie+1,n):
                if (l[i]<=sL if side>0 else h[i]>=sL): x=sL-SLIP*side; break
                if (h[i]>=tT if side>0 else l[i]<=tT): x=tT; break
                if not lk and ((h[i]-e) if side>0 else (e-l[i]))>=r: lk=True; sL=e+side*r
            if x is None: x=c[-1]
            pts=(x-e)*side; rows.append(('ORB',k>=split,rg,pts/r,pts*2-FEE)); break
df=pd.DataFrame(rows,columns=['s','test','rg','R','usd'])
pf=lambda u: u[u>0].sum()/-u[u<=0].sum()
for s in ['IB','ORB']:
    d=df[df.s==s]; print(f"\n== {s}: all n={len(d)} PF {pf(d.usd):.2f} train {pf(d[~d.test].usd):.2f} test {pf(d[d.test].usd):.2f}")
    for g,x in d.groupby('rg'):
        nm=NAME.get(abs(g),'?')+(' (against trade)' if g<0 else '')
        print(f"  {nm:28s} n={len(x):5d} share {len(x)/len(d)*100:4.1f}% avgR {x.R.mean():+.3f} PF {pf(x.usd):.2f} train {pf(x[~x.test].usd):.2f} test {pf(x[x.test].usd):.2f}")
df.to_pickle('regime_trades.pkl')
