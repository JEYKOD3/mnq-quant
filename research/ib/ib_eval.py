import pickle, numpy as np, itertools, collections
days=pickle.load(open('/home/claude/mnq-quant/research/ib/days.pkl','rb'))
TICK=0.25; PV=2; FEE=1.0; SLIP=0.25
def run_day(d, ts,o,h,l,c,tr, exitm, filt, prev):
    pdh,pdl,pdc=prev
    n=len(ts); trades=[]; armed=False; tDir=0; losses=0; consec=0; wins=0; pnl=0; stopped=False
    for i in range(1,n):
        sig=False
        if tDir!=0:
            x=None
            hitS = l[i]<=sL if tDir>0 else h[i]>=sL
            hitT = h[i]>=tT if tDir>0 else l[i]<=tT
            if hitS: x=sL-SLIP*tDir; why='stop' if sL==s0 else 'lock'
            elif hitT: x=tT; why='target'
            elif exitm['backin'] and not reached1 and mbL<c[i]<mbH: x=c[i]-SLIP*tDir; why='backin'
            elif i==n-1: x=c[i]; why='eod'
            if x is None:
                # update lock after bar closes
                fav = h[i]-e if tDir>0 else e-l[i]
                if fav>=r*1.0 and not reached1:
                    reached1=True
                    if exitm['lock'] is not None: sL = e+tDir*exitm['lock']*r
            else:
                pts=(x-e)*tDir; usd=pts*PV-FEE
                trades.append(dict(i=i0,side=tDir,R=pts/r,usd=usd,why=why))
                pnl+=usd; tDir=0
                if usd>0: wins+=1; consec=0
                else: losses+=1; consec+=1
                if filt=='1loss' and losses>=1: stopped=True
                if filt=='2consec' and consec>=2: stopped=True
                if filt=='cap400' and pnl<=-400: stopped=True
                if filt=='1loss_or_2wins' and (losses>=1 or wins>=2): stopped=True
                if filt=='firstwin' and wins>=1: stopped=True
        if armed:
            bl=min(o[i],c[i]); bh=max(o[i],c[i]); up=bl>mbH; dn=bh<mbL
            if up or dn:
                side=1 if up else -1; armed=False
                ee=c[i]; ss=mbL-TICK if side>0 else mbH+TICK; rr_=abs(ee-ss)
                if side==tr[i] and tDir==0 and 5<=rr_<=80 and rr_*PV<=200 and not stopped and i<n-1:
                    tDir=side; e=ee; s0=ss; sL=ss; r=rr_; i0=i; reached1=False; sig=True
                    tT=e+side*exitm['tp']*r
                    if exitm.get('lvl'):
                        lv=[v for v in (pdh,pdl,pdc,o[0]) if v is not None]
                        cand=[v for v in lv if (v-e)*side>=1.0*r and (v-e)*side<=exitm['tp']*r]
                        if cand: tT=min(cand,key=lambda v:(v-e)*side)-side*TICK
            elif i-mbBar>30: armed=False
        if not armed and tDir==0 and h[i]<=h[i-1] and l[i]>=l[i-1] and not sig:
            armed=True; mbH=h[i-1]; mbL=l[i-1]; mbBar=i-1
    return trades
EXITS={
 'A 1R fixed':dict(tp=1.0,lock=None,backin=False),
 'B 1.5R fixed':dict(tp=1.5,lock=None,backin=False),
 'C 1.5R, lock +1R after 1R':dict(tp=1.5,lock=1.0,backin=False),
 'D 1.5R, lock +0.5R after 1R':dict(tp=1.5,lock=0.5,backin=False),
 'E 1R + back-in exit':dict(tp=1.0,lock=None,backin=True),
 'F C + back-in exit':dict(tp=1.5,lock=1.0,backin=True),
 'G C + key-level target':dict(tp=1.5,lock=1.0,backin=False,lvl=True),
}
FILTS=['all','1loss','2consec','cap400','1loss_or_2wins','firstwin']
def stats(sess):
    allt=[t for s in sess for t in s]
    if not allt: return None
    u=np.array([t['usd'] for t in allt]); R=np.array([t['R'] for t in allt])
    ds=np.array([sum(t['usd'] for t in s) for s in sess])
    eq=np.cumsum(ds); dd=(np.maximum.accumulate(eq)-eq).max()
    gw=u[u>0].sum(); gl=-u[u<=0].sum()
    return dict(trades=len(u), wr=round((u>0).mean()*100,1), pf=round(gw/gl,2) if gl else 99, avgR=round(R.mean(),3),
                net=int(u.sum()), perDay=round(ds.mean(),1), green=round((ds>0).mean()*100,1), maxDD=int(dd))
res={}
prevs=[]; 
for k,(d,ts,o,h,l,c,tr) in enumerate(days):
    prevs.append((days[k-1][3].max(),days[k-1][4].min(),days[k-1][5][-1]) if k>0 else (None,None,None))
split=int(len(days)*0.7)
for en,em in EXITS.items():
    for f in FILTS:
        sess=[run_day(d,ts,o,h,l,c,tr,em,f,prevs[k]) for k,(d,ts,o,h,l,c,tr) in enumerate(days)]
        res[(en,f)]=(stats(sess),stats(sess[:split]),stats(sess[split:]),
            {y:stats([s for (dd,*_),s in zip(days,sess) if dd[:4]==y]) for y in ['2022','2023','2024','2025','2026']}, sess)
pickle.dump({k:v[:4] for k,v in res.items()},open('/home/claude/mnq-quant/research/ib/res.pkl','wb'))
print('split date', days[split][0])
print(f"{'exit':30s} {'filter':15s} | trades  WR   PF   avgR   net$  $/day green% maxDD | OOS PF  OOS $/day")
for (en,f),(a,tr_,te,yr,_) in res.items():
    print(f"{en:30s} {f:15s} | {a['trades']:6d} {a['wr']:5.1f} {a['pf']:4.2f} {a['avgR']:+.3f} {a['net']:7d} {a['perDay']:6.1f} {a['green']:5.1f} {a['maxDD']:6d} | {te['pf']:4.2f} {te['perDay']:6.1f}")
