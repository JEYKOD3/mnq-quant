# Inside-bar simulator on 5y MNQ RTH 1m with HTF trend (15/60/240 EMA21) from 5m full-session data.
import gzip, numpy as np, datetime as dt
from zoneinfo import ZoneInfo
NY=ZoneInfo("America/New_York")
R='/home/claude/mnq-quant/data/raw/'
# ---- HTF trend from 5m continuous
c5=np.loadtxt(gzip.open(R+'MNQ_5m_cont.csv.gz','rt'),delimiter=',',skiprows=1,usecols=(0,4))
t5=c5[:,0].astype(np.int64); cl5=c5[:,1]
def htf(minutes):
    anchor=22*3600  # 18:00 EDT; DST drift of 1h ignored for 15/60, small for 240
    bk=(t5-anchor)//(minutes*60)
    ends=np.r_[np.nonzero(np.diff(bk))[0], len(bk)-1]
    bc=cl5[ends]; a=2/22; e=np.empty_like(bc); e[0]=bc[0]
    for i in range(1,len(bc)): e[i]=a*bc[i]+(1-a)*e[i-1]
    d=np.where(bc>e,1,-1)
    # bucket start times; dir of a completed bucket applies from the next bucket start
    return bk[ends], d
H={m:htf(m) for m in (15,60,240)}
def trend_at(ts):
    s=0
    for m,(bks,d) in H.items():
        b=(ts-22*3600)//(m*60)
        k=np.searchsorted(bks,b)-1   # last completed bucket strictly before current
        s+= d[k] if k>=0 else 0
    return 1 if s>0 else -1
# ---- RTH 1m days
days=[]
for line in gzip.open(R+'mnq_rth_1m.txt.gz','rt'):
    p=line.strip().split('|'); d=p[0]
    rows=[list(map(int,x.split(','))) for x in p[1:]]
    a=np.array(rows,dtype=float); hhmm=a[:,0].astype(int); o,h,l,c=(a[:,1:5]/4).T
    base=dt.datetime(int(d[:4]),int(d[4:6]),int(d[6:]),tzinfo=NY)
    ts=np.array([int((base+dt.timedelta(hours=int(x)//100,minutes=int(x)%100)).timestamp()) for x in hhmm])
    days.append((d,ts,o,h,l,c))
print('days',len(days),days[0][0],days[-1][0])
# precompute trend per bar (vectorised per tf)
for i,(d,ts,o,h,l,c) in enumerate(days):
    s=np.zeros(len(ts))
    for m,(bks,dd) in H.items():
        k=np.searchsorted(bks,(ts-22*3600)//(m*60))-1
        s+=np.where(k>=0,dd[np.clip(k,0,None)],0)
    days[i]=(d,ts,o,h,l,c,np.where(s>0,1,-1))
import pickle; pickle.dump(days,open('/home/claude/mnq-quant/research/ib/days.pkl','wb'))
