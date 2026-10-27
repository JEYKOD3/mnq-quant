import pickle, numpy as np
days=pickle.load(open('days.pkl','rb'))
TICK=0.25; SLIP=0.25
def run(f, lockR):
    out=[]; split=int(len(days)*0.7)
    for k,(d,ts,o,h,l,c,tr) in enumerate(days):
        n=len(ts); armed=False; tDir=0
        for i in range(1,n):
            sig=False
            if tDir!=0:
                hitS = l[i]<=sL if tDir>0 else h[i]>=sL
                hit1 = h[i]>=e+tDir*r if tDir>0 else l[i]<=e-r
                hitT = h[i]>=e+1.5*r if tDir>0 else l[i]<=e-1.5*r
                res=None
                if hitS:
                    xR=(sL-SLIP*tDir-e)*tDir/r
                    res = (f*1.0 + (1-f)*xR) if took1 else xR
                elif hitT:
                    res = (f*1.0 + (1-f)*1.5)
                elif i==n-1:
                    xR=(c[i]-e)*tDir/r; res=(f+(1-f)*xR) if took1 else xR
                elif hit1 and not took1:
                    took1=True
                if res is None and took1 and not moved:
                    moved=True; sL=e+tDir*lockR*r   # applies from next bar
                if res is not None:
                    out.append((res, k>=split)); tDir=0
            if armed:
                bl=min(o[i],c[i]); bh=max(o[i],c[i]); up=bl>mbH; dn=bh<mbL
                if up or dn:
                    side=1 if up else -1; armed=False; ee=c[i]; ss=mbL-TICK if side>0 else mbH+TICK; rr=abs(ee-ss)
                    if side==tr[i] and tDir==0 and 5<=rr<=80 and i<n-1:
                        tDir=side; e=ee; sL=ss; r=rr; took1=False; moved=False; sig=True
                elif i-mbBar>30: armed=False
            if not armed and tDir==0 and h[i]<=h[i-1] and l[i]>=l[i-1] and not sig:
                armed=True; mbH=h[i-1]; mbL=l[i-1]; mbBar=i-1
    R=np.array([x[0] for x in out]); oos=np.array([x[1] for x in out])
    pf=lambda a: a[a>0].sum()/-a[a<=0].sum()
    return len(R), R.mean(), pf(R), pf(R[oos]), (R>0).mean()
print("partial@1R  rest-stop-after-1R | trades avgR  PF  OOS-PF  win%")
for f in (0, 1/3, 0.5, 2/3, 1.0):
    for lk in (0.0, 0.5, 1.0):
        if f==1.0 and lk>0: continue
        n,a,p,po,w=run(f,lk)
        print(f"{f:5.2f}  stop->{lk:+.1f}R | {n} {a:+.3f} {p:.3f} {po:.3f} {w*100:.1f}")
