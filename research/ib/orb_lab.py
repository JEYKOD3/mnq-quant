import pickle, numpy as np, itertools
days=pickle.load(open('/home/claude/mnq-quant/research/ib/days.pkl','rb'))
TICK=.25; SLIP=.25; FEE=1.0
def bars5(d):
    _,ts,o,h,l,c,tr=d; n=len(ts)//5*5
    return o[:n:5], h[:n].reshape(-1,5).max(1), l[:n].reshape(-1,5).min(1), c[4:n:5]
def sim(setup, orm=15, stop='other', tp=2.0, lock=None, last=13*60, maxtr=1, bodymin=0.0):
    res=[]; split=int(len(days)*.7)
    for k,d in enumerate(days):
        o,h,l,c=bars5(d); n=len(o); nor=orm//5
        if n<nor+3: continue
        ORH=h[:nor].max(); ORL=l[:nor].min(); W=ORH-ORL
        armed=0; touched=False; pos=0; ntr=0; brokeU=brokeD=False
        for i in range(nor,n):
            tmin=9*60+30+5*i  # bar start minute
            # manage
            if pos:
                hS= l[i]<=sL if pos>0 else h[i]>=sL; hT= h[i]>=tT if pos>0 else l[i]<=tT; x=None
                if hS: x=sL-SLIP*pos
                elif hT: x=tT
                elif i==n-1: x=c[i]
                elif lock and not lk and ((h[i]-e) if pos>0 else (e-l[i]))>=lock*r: lk=True; sL=e+pos*lock*r
                if x is not None:
                    pts=(x-e)*pos; res.append(((pts/r), pts*2-FEE, k>=split, d[0][:4], k)); pos=0
                continue
            if ntr>=maxtr or tmin>=last: 
                continue
            body=abs(c[i]-o[i])/max(h[i]-l[i],TICK)
            if setup=='break':   # stop order 1 tick beyond OR edge
                up=h[i]>ORH and not brokeU; dn=l[i]<ORL and not brokeD
                if up and dn: continue
                if up: brokeU=True; side=1; e=ORH+TICK+SLIP
                elif dn: brokeD=True; side=-1; e=ORL-TICK-SLIP
                else: continue
                s= (ORL-TICK) if side>0 else (ORH+TICK)
                if stop=='mid': s=(ORH+ORL)/2
            elif setup=='closebreak':
                if c[i]>ORH and not brokeU: side=1; brokeU=True
                elif c[i]<ORL and not brokeD: side=-1; brokeD=True
                else: continue
                if body<bodymin: continue
                e=c[i]; s=(ORL-TICK) if side>0 else (ORH+TICK)
                if stop=='mid': s=(ORH+ORL)/2
                if stop=='bar': s=(l[i]-TICK) if side>0 else (h[i]+TICK)
            elif setup=='retest':  # 5m close outside arms; close back inside disarms; touch edge; bullish close away = entry
                if armed==0:
                    if c[i]>ORH: armed=1; touched=False
                    elif c[i]<ORL: armed=-1; touched=False
                    continue
                if armed>0 and c[i]<ORH: armed=0; continue
                if armed<0 and c[i]>ORL: armed=0; continue
                if armed>0 and l[i]<=ORH+0.1*W: touched=True
                if armed<0 and h[i]>=ORL-0.1*W: touched=True
                if not touched: continue
                ok = (c[i]>o[i] and body>=bodymin) if armed>0 else (c[i]<o[i] and body>=bodymin)
                if not ok: continue
                side=armed; e=c[i]
                s=(ORL-TICK) if side>0 else (ORH+TICK)
                if stop=='mid': s=(ORH+ORL)/2
                if stop=='bar': s=(min(l[i],l[i-1])-TICK) if side>0 else (max(h[i],h[i-1])+TICK)
                armed=0
            elif setup=='bounce':  # inside range: touch edge then close back away, target other edge
                if c[i]>ORH or c[i]<ORL: brokeU=True  # once range broken by a close, stop fading
                if brokeU: continue
                if l[i]<=ORL+0.1*W and c[i]>o[i] and c[i]>ORL and body>=bodymin: side=1
                elif h[i]>=ORH-0.1*W and c[i]<o[i] and c[i]<ORH and body>=bodymin: side=-1
                else: continue
                e=c[i]; s=(min(l[i],ORL)-0.1*W) if side>0 else (max(h[i],ORH)+0.1*W)
            r=abs(e-s)
            if r<4: continue
            tT = e+side*tp*r if setup!='bounce' or tp>0 else None
            if setup=='bounce' and tp==0: tT=(ORH-TICK) if side>0 else (ORL+TICK)
            pos=side; sL=s; lk=False; ntr+=1
    a=np.array([x[:2] for x in res]); t=np.array([x[2] for x in res]); y=np.array([x[3] for x in res])
    if len(a)==0: return None
    R,U=a[:,0],a[:,1]; pf=lambda x: x[x>0].sum()/max(-x[x<=0].sum(),1e-9)
    yrs=' '.join(f"{pf(U[y==yy]):.2f}" for yy in ['2022','2023','2024','2025','2026'])
    return dict(n=len(R), wr=(U>0).mean()*100, avgR=R.mean(), pf=pf(U), tr=pf(U[~t]), te=pf(U[t]), pday=U.sum()/len(days), yrs=yrs, avgrisk=None)
rows=[]
for setup in ['break','closebreak','retest','bounce']:
    for orm in [5,15,30]:
        stops=['other','mid'] + (['bar'] if setup in('closebreak','retest') else [])
        if setup=='bounce': stops=['edge']
        tps=[1.0,1.5,2.0,3.0] if setup!='bounce' else [0,1.0,1.5]
        for st in stops:
            for tp in tps:
                for lock in [None,1.0]:
                    if lock and tp<=1: continue
                    for bm in ([0.0,0.5] if setup in('retest','bounce','closebreak') else [0.0]):
                        r=sim(setup,orm,st,tp,lock,bodymin=bm)
                        if r: rows.append((setup,orm,st,tp,lock,bm,r))
import json
pickle.dump(rows,open('/home/claude/mnq-quant/research/ib/orb_rows.pkl','wb'))
rows.sort(key=lambda x:-min(x[6]['tr'],x[6]['te']))
print("setup OR stop tp lock body | n wr avgR PF trainPF testPF $/day | PF by yr 22..26")
for s in rows[:30]:
    r=s[6]; print(f"{s[0]:10s} {s[1]:2d} {s[2]:5s} {s[3]} {s[4]} {s[5]} | {r['n']} {r['wr']:.0f}% {r['avgR']:+.3f} {r['pf']:.2f} {r['tr']:.2f} {r['te']:.2f} {r['pday']:+.1f} | {r['yrs']}")
