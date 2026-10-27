import pickle, numpy as np
days=pickle.load(open('days.pkl','rb')); TICK=0.25; SLIP=0.25; FEE_R=0  # report in R and $ (1 lot, $1 fee)
def run(mode, tp, lock):
    out=[]; split=int(len(days)*0.7)
    for k,(d,ts,o,h,l,c,tr) in enumerate(days):
        n=len(ts); armed=False; tDir=0; rv=0
        for i in range(1,n):
            sig=False
            # manage reversal trade
            if rv!=0:
                hS = l[i]<=rs if rv>0 else h[i]>=rs; hT= h[i]>=rt if rv>0 else l[i]<=rt
                x=None
                if hS: x=rs-SLIP*rv
                elif hT: x=rt
                elif i==n-1: x=c[i]
                else:
                    fav=(h[i]-re if rv>0 else re-l[i])/rr_
                    if lock and not rl and fav>=1: rl=True; rs=re+rv*rr_
                if x is not None:
                    pts=(x-re)*rv; out.append((pts/rr_, pts*2-1, k>=split)); rv=0
            # manage original IB (not traded, just tracked to detect failure)
            if tDir!=0:
                ext = max(ext,h[i]) if tDir>0 else min(ext,l[i])
                failed=False
                if mode=='stop' and (l[i]<=s0 if tDir>0 else h[i]>=s0): failed=True; ent=s0
                if mode=='backin' and mbL<c[i]<mbH: failed=True; ent=c[i]
                if (h[i]>=e+r if tDir>0 else l[i]<=e-r): tDir=0   # original reached 1R -> no reversal
                elif failed:
                    if rv==0 and i<n-2:
                        rv=-tDir; re=ent; rs=(ext+TICK) if rv<0 else (ext-TICK)
                        rr_=abs(re-rs)
                        if 4<=rr_<=80: rt=re+rv*tp*rr_; rl=False
                        else: rv=0
                    tDir=0
            if armed:
                bl=min(o[i],c[i]); bh=max(o[i],c[i]); up=bl>mbH; dn=bh<mbL
                if up or dn:
                    side=1 if up else -1; armed=False; ee=c[i]; ss=mbL-TICK if side>0 else mbH+TICK; r0=abs(ee-ss)
                    if side==tr[i] and tDir==0 and 5<=r0<=80 and i<n-1:
                        tDir=side; e=ee; s0=ss; r=r0; ext=h[i] if side>0 else l[i]; sig=True
                elif i-mbBar>30: armed=False
            if not armed and tDir==0 and h[i]<=h[i-1] and l[i]>=l[i-1] and not sig:
                armed=True; mbH=h[i-1]; mbL=l[i-1]; mbBar=i-1
    a=np.array(out); R=a[:,0]; U=a[:,1]; t=a[:,2]==1
    pf=lambda x: x[x>0].sum()/-x[x<=0].sum()
    return len(R), (R>0).mean(), R.mean(), pf(U), pf(U[~t]), pf(U[t]), U.sum()/len(days)
print("mode   tp  lock | n  win  avgR  PF$ trainPF testPF $/day")
for mode in ('stop','backin'):
    for tp in (1.0,1.5,2.0):
        for lock in (False,True):
            n,w,a,p,p1,p2,pd=run(mode,tp,lock)
            print(f"{mode:6s} {tp} {str(lock):5s} | {n} {w*100:.1f} {a:+.3f} {p:.2f} {p1:.2f} {p2:.2f} {pd:+.1f}")
