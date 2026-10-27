import pickle, numpy as np
days=pickle.load(open('/home/claude/mnq-quant/research/ib/days.pkl','rb'))
TICK=0.25
rows=[]
for k,(d,ts,o,h,l,c,tr) in enumerate(days):
    if k==0: continue
    P=days[k-1]; pdh,pdl,pdc=P[3].max(),P[4].min(),P[5][-1]
    n=len(ts); armed=False; tDir=0
    for i in range(1,n):
        sig=False
        if tDir!=0:
            fav=(h[i]-e)/r if tDir>0 else (e-l[i])/r
            hitS= l[i]<=s if tDir>0 else h[i]>=s
            if hitS or i==n-1:
                rows.append((mfe, blk, blkR, d[:4], hitS)); tDir=0
            else:
                mfe=max(mfe,fav)
                if mfe>=3: rows.append((mfe,blk,blkR,d[:4],False)); tDir=0
        if armed:
            bl=min(o[i],c[i]); bh=max(o[i],c[i]); up=bl>mbH; dn=bh<mbL
            if up or dn:
                side=1 if up else -1; armed=False; ee=c[i]; ss=mbL-TICK if side>0 else mbH+TICK; rr=abs(ee-ss)
                if side==tr[i] and tDir==0 and 5<=rr<=80 and i<n-1:
                    tDir=side; e=ee; s=ss; r=rr; mfe=0; sig=True
                    lv=[pdh,pdl,pdc,o[0],h[:i].max(),l[:i].min()]
                    ahead=[(v-e)*side/r for v in lv if (v-e)*side>0]
                    blkR=min(ahead) if ahead else 9; blk=blkR<1.0
            elif i-mbBar>30: armed=False
        if not armed and tDir==0 and h[i]<=h[i-1] and l[i]>=l[i-1] and not sig:
            armed=True; mbH=h[i-1]; mbL=l[i-1]; mbBar=i-1
m=np.array([x[0] for x in rows]); b=np.array([x[1] for x in rows]); bR=np.array([x[2] for x in rows])
print('trades',len(m))
for lab,mask in [('all',np.ones(len(m),bool)),('key level BEFORE 1R',b),('clear path to 1R',~b)]:
    mm=m[mask]
    print(f"{lab:22s} n={mask.sum():5d} reach0.5R {np.mean(mm>=.5)*100:4.1f}%  reach1R {np.mean(mm>=1)*100:4.1f}%  reach1.5R {np.mean(mm>=1.5)*100:4.1f}%  reach2R {np.mean(mm>=2)*100:4.1f}%")
nr=m[m<1]
print('trades that never reached 1R:',len(nr), f'({len(nr)/len(m)*100:.0f}%)')
for a,bb in [(0,.25),(.25,.5),(.5,.75),(.75,1)]:
    print(f"  best excursion {a:.2f}-{bb:.2f}R: {np.mean((nr>=a)&(nr<bb))*100:4.1f}% of them")
# level distance buckets
for a,bb in [(0,.5),(.5,1),(1,1.5),(1.5,9)]:
    mk=(bR>=a)&(bR<bb); mm=m[mk]
    print(f"nearest level {a}-{bb}R ahead: n={mk.sum():5d} reach1R {np.mean(mm>=1)*100:4.1f}% reach1.5R {np.mean(mm>=1.5)*100:4.1f}%")
