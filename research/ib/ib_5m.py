import gzip, numpy as np, pickle, datetime as dt
from zoneinfo import ZoneInfo
NY=ZoneInfo("America/New_York")
exec(open('ib_sim.py').read().split('# ---- RTH 1m days')[0])  # loads H (htf trend) + helpers
sess=[]
for line in gzip.open('/home/claude/mnq-quant/data/raw/mnq_eth_5m.txt.gz','rt'):
    p=line.strip().split('|'); d=p[0]
    a=np.array([list(map(int,x.split(','))) for x in p[1:]],float)
    hhmm=a[:,0].astype(int); o,h,l,c=(a[:,1:5]/4).T
    base=dt.datetime(int(d[:4]),int(d[4:6]),int(d[6:]),tzinfo=NY)
    # ETH session labelled by date; times >=1800 belong to previous calendar day
    ts=np.array([int((base+dt.timedelta(days=-1 if x>=1800 else 0, hours=int(x)//100, minutes=int(x)%100)).timestamp()) for x in hhmm])
    s=np.zeros(len(ts))
    for m,(bks,dd) in H.items():
        k=np.searchsorted(bks,(ts-22*3600)//(m*60))-1; s+=np.where(k>=0,dd[np.clip(k,0,None)],0)
    sess.append((d,ts,o,h,l,c,np.where(s>0,1,-1),hhmm))
print(len(sess), sess[0][0], sess[-1][0])
TICK=.25; SLIP=.25
def run(window):
    out=[]; split=int(len(sess)*0.7)
    for k,(d,ts,o,h,l,c,tr,hm) in enumerate(sess):
        n=len(ts); armed=False; tDir=0
        inw=np.array([window(x) for x in hm])
        for i in range(1,n):
            sig=False
            if tDir!=0:
                hS= l[i]<=sL if tDir>0 else h[i]>=sL; hT= h[i]>=tT if tDir>0 else l[i]<=tT; x=None
                if hS: x=sL-SLIP*tDir
                elif hT: x=tT
                elif i==n-1: x=c[i]
                else:
                    fav=(h[i]-e if tDir>0 else e-l[i])/r
                    if not lk and fav>=1: lk=True; sL=e+tDir*r
                if x is not None:
                    pts=(x-e)*tDir; out.append((pts/r, pts*2-1, k>=split, lk or pts>0)); tDir=0
            if armed:
                bl=min(o[i],c[i]); bh=max(o[i],c[i]); up=bl>mbH; dn=bh<mbL
                if up or dn:
                    side=1 if up else -1; armed=False; ee=c[i]; ss=mbL-TICK if side>0 else mbH+TICK; rr=abs(ee-ss)
                    if side==tr[i] and tDir==0 and 5<=rr<=80 and inw[i] and i<n-1:
                        tDir=side; e=ee; sL=ss; r=rr; tT=e+1.5*side*r; lk=False; sig=True
                elif i-mbBar>30: armed=False
            if not armed and tDir==0 and h[i]<=h[i-1] and l[i]>=l[i-1] and not sig:
                armed=True; mbH=h[i-1]; mbL=l[i-1]; mbBar=i-1
    a=np.array(out,float); R=a[:,0]; U=a[:,1]; t=a[:,2]==1
    pf=lambda x: x[x>0].sum()/-x[x<=0].sum()
    return len(R), a[:,3].mean(), R.mean(), pf(U[~t]), pf(U[t]), U.sum()/len(sess)
W={'all 24h':lambda x:True,'overnight 18:00-09:30':lambda x:x>=1800 or x<930,'evening 18:00-20:00':lambda x:1800<=x<2000,
   'Asia 20:00-02:00':lambda x:x>=2000 or x<200,'London 02:00-09:30':lambda x:200<=x<930,'RTH 09:30-16:00':lambda x:930<=x<1600}
print("5m chart, 1.5R target + lock +1R | trades hit1R avgR trainPF testPF $/day")
for k,f in W.items():
    n,h1,a,p1,p2,pd=run(f); print(f"{k:24s} | {n:5d} {h1*100:.1f}% {a:+.3f} {p1:.2f} {p2:.2f} {pd:+.1f}")
