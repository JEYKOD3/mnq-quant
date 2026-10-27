import pickle, numpy as np
days=pickle.load(open('days.pkl','rb')); TICK=.25; SLIP=.25
def agg(ts,o,h,l,c,tr,m):
    n=len(ts)//m*m
    if n==0: return None
    g=lambda a,f: f(a[:n].reshape(-1,m),axis=1)
    return (ts[:n:m], o[:n:m], g(h,np.max), g(l,np.min), c[m-1:n:m], tr[:n:m])
def run(m, minR=5, maxR=80, yearly=False):
    out=[]; split=int(len(days)*0.7)
    for k,(d,ts,o,h,l,c,tr) in enumerate(days):
        A=agg(ts,o,h,l,c,tr,m)
        if A is None: continue
        ts,o,h,l,c,tr=A; n=len(ts); armed=False; tDir=0
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
                    pts=(x-e)*tDir; out.append((pts/r, pts*2-1, k>=split, d[:4])); tDir=0
            if armed:
                bl=min(o[i],c[i]); bh=max(o[i],c[i]); up=bl>mbH; dn=bh<mbL
                if up or dn:
                    side=1 if up else -1; armed=False; ee=c[i]; ss=mbL-TICK if side>0 else mbH+TICK; rr=abs(ee-ss)
                    # trend known at the bar's open (tr of first minute) - use the 1m trend of the breakout bar's last minute is lookahead; use bar start
                    if side==tr[i] and tDir==0 and minR<=rr<=maxR and i<n-1:
                        tDir=side; e=ee; sL=ss; r=rr; tT=e+1.5*side*r; lk=False; sig=True
                elif i-mbBar>30: armed=False
            if not armed and tDir==0 and h[i]<=h[i-1] and l[i]>=l[i-1] and not sig:
                armed=True; mbH=h[i-1]; mbL=l[i-1]; mbBar=i-1
    U=np.array([x[1] for x in out]); R=np.array([x[0] for x in out]); t=np.array([x[2] for x in out]); y=np.array([x[3] for x in out])
    pf=lambda x: x[x>0].sum()/-x[x<=0].sum() if len(x) else 0
    yr=' '.join(f"{yy}:{pf(U[y==yy]):.2f}" for yy in ['2022','2023','2024','2025','2026'])
    return len(R), R.mean(), pf(U[~t]), pf(U[t]), U.sum()/len(days), yr
print("RTH, 1.5R + lock | tf trades avgR trainPF testPF $/day | PF by year")
for m in (1,2,3,5,10,15):
    n,a,p1,p2,pd,yr=run(m); print(f"{m:2d}m | {n:5d} {a:+.3f} {p1:.2f} {p2:.2f} {pd:+6.1f} | {yr}")
