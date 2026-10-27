import pickle, numpy as np
days=pickle.load(open('days.pkl','rb')); TICK=.25; SLIP=.25; FEE=1.0
def manage(o,h,l,c,j0,side,e,s,tp,lock):
    r=abs(e-s); sL=s; tT=e+side*tp*r if tp else None; lk=False
    for i in range(j0,len(o)):
        if (l[i]<=sL if side>0 else h[i]>=sL): return (sL-SLIP*side-e)*side, r, i
        if tT is not None and (h[i]>=tT if side>0 else l[i]<=tT): return (tT-e)*side, r, i
        if lock and not lk and ((h[i]-e) if side>0 else (e-l[i]))>=lock*r: lk=True; sL=e+side*lock*r
    return (c[-1]-e)*side, r, len(o)-1
def sim(setup, orm=15, stop='other', tp=2.0, lock=1.0, last=13*60, maxtr=1, bodymin=0.0, tol=0.1, tgt_other=False):
    res=[]; split=int(len(days)*.7)
    for k,(dd,ts,O,Hh,Ll,C,tr) in enumerate(days):
        n5=len(O)//5; o=O[:n5*5:5]; h=Hh[:n5*5].reshape(-1,5).max(1); l=Ll[:n5*5].reshape(-1,5).min(1); c=C[4:n5*5:5]
        nor=orm//5
        if n5<nor+3: continue
        ORH=h[:nor].max(); ORL=l[:nor].min(); W=ORH-ORL
        armed=0; touched=False; ntr=0; broke=False; i=nor; busy_until=-1
        while i<n5:
            tmin=570+5*i
            if i<=busy_until or ntr>=maxtr or tmin>=last: i+=1; continue
            body=abs(c[i]-o[i])/max(h[i]-l[i],TICK); side=0
            if setup=='retest':
                if armed==0:
                    if c[i]>ORH: armed=1; touched=False
                    elif c[i]<ORL: armed=-1; touched=False
                    i+=1; continue
                if (armed>0 and c[i]<ORH) or (armed<0 and c[i]>ORL): armed=0; i+=1; continue
                if armed>0 and l[i]<=ORH+tol*W: touched=True
                if armed<0 and h[i]>=ORL-tol*W: touched=True
                if touched and ((c[i]>o[i]) if armed>0 else (c[i]<o[i])) and body>=bodymin:
                    side=armed; e=c[i]
                    s={'other':(ORL-TICK) if side>0 else (ORH+TICK),'mid':(ORH+ORL)/2,
                       'bar':(min(l[i],l[i-1])-TICK) if side>0 else (max(h[i],h[i-1])+TICK)}[stop]
                    armed=0
            elif setup=='bounce':
                if c[i]>ORH or c[i]<ORL: broke=True
                if not broke:
                    if l[i]<=ORL+tol*W and c[i]>o[i] and c[i]>ORL and body>=bodymin: side=1
                    elif h[i]>=ORH-tol*W and c[i]<o[i] and c[i]<ORH and body>=bodymin: side=-1
                    if side: e=c[i]; s=(min(l[i],ORL)-0.1*W) if side>0 else (max(h[i],ORH)+0.1*W)
            if side:
                r=abs(e-s)
                if r>=4 and (side>0 and s<e or side<0 and s>e):
                    tpx=tp
                    if tgt_other: tpx=abs(((ORH if side>0 else ORL)-e))/r
                    pts,r,xi=manage(Hh*0+O, Hh, Ll, C, (i+1)*5, side, e, s, tpx, lock)
                    res.append((pts/r, pts*2-FEE, k>=split, dd[:4], W)); ntr+=1; busy_until=xi//5
            i+=1
    R=np.array([x[0] for x in res]); U=np.array([x[1] for x in res]); t=np.array([x[2] for x in res]); y=np.array([x[3] for x in res])
    if len(R)==0: return 'none'
    pf=lambda x: x[x>0].sum()/max(-x[x<=0].sum(),1e-9)
    eq=np.cumsum(U); dd=(np.maximum.accumulate(eq)-eq).max()
    return f"n{len(R)} wr{(U>0).mean()*100:.0f}% avgR{R.mean():+.3f} PF{pf(U):.2f} tr{pf(U[~t]):.2f} te{pf(U[t]):.2f} $/day{U.sum()/len(days):+.1f} maxDD${dd:.0f} | "+' '.join(f"{pf(U[y==yy]):.2f}" for yy in ['2022','2023','2024','2025','2026'])
print('RETEST (15m OR unless noted)')
for orm in (15,30):
  for st in ('other','mid','bar'):
    for tp,lk in ((1.5,1.0),(2.0,1.0),(2.0,None),(3.0,1.0)):
      for bm in (0.0,0.5):
        print(f" OR{orm} stop={st:5s} tp{tp} lock{lk} body>={bm}:", sim('retest',orm,st,tp,lk,bodymin=bm))
print('BOUNCE inside range (fade the edge until a 5m close outside)')
for orm in (15,30):
  for tp,lk,to in ((1.0,None,False),(1.5,1.0,False),(0,None,True)):
    for bm in (0.0,0.5):
      print(f" OR{orm} tp{'other edge' if to else tp} lock{lk} body>={bm}:", sim('bounce',orm,'edge',tp,lk,bodymin=bm,tgt_other=to,maxtr=2))
