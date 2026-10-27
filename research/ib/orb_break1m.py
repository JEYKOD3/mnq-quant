import pickle, numpy as np
days=pickle.load(open('days.pkl','rb')); TICK=.25; SLIP=.25; FEE=1.0
def sim(orm=5, stop='mid', tp=3.0, lock=1.0, last=13*60, both=False, wfilt=None):
    res=[]; split=int(len(days)*.7); risks=[]
    for k,(dd,ts,o,h,l,c,tr) in enumerate(days):
        if len(o)<orm+5: continue
        ORH=h[:orm].max(); ORL=l[:orm].min(); W=ORH-ORL
        if wfilt and not (wfilt[0]<=W<=wfilt[1]): continue
        pos=0; done=0; usedU=usedD=False
        for i in range(orm,len(o)):
            tmin=570+i
            if pos:
                hS= l[i]<=sL if pos>0 else h[i]>=sL; hT= h[i]>=tT if pos>0 else l[i]<=tT; x=None
                if hS: x=sL-SLIP*pos
                elif hT: x=tT
                elif i==len(o)-1: x=c[i]
                elif lock and not lk and ((h[i]-e) if pos>0 else (e-l[i]))>=lock*r: lk=True; sL=e+pos*lock*r
                if x is not None:
                    pts=(x-e)*pos; res.append((pts/r, pts*2-FEE, k>=split, dd[:4])); pos=0; done+=1
                continue
            if done>=(2 if both else 1) or tmin>=last: continue
            up=h[i]>ORH and not usedU; dn=l[i]<ORL and not usedD
            if up and dn: continue
            if not(up or dn): continue
            side=1 if up else -1
            if side>0: usedU=True
            else: usedD=True
            e=(ORH+TICK if side>0 else ORL-TICK)+SLIP*side
            e=max(e,o[i]) if side>0 else min(e,o[i])   # gap through
            s={'other':(ORL-TICK) if side>0 else (ORH+TICK),'mid':(ORH+ORL)/2}[stop]
            r=abs(e-s)
            if r<4: continue
            risks.append(r)
            tT=e+side*tp*r; sL=s; lk=False; pos=side
            # same-bar stop check (conservative)
            if (l[i]<=sL if side>0 else h[i]>=sL):
                pts=(sL-SLIP*side-e)*side; res.append((pts/r, pts*2-FEE, k>=split, dd[:4])); pos=0; done+=1
    R=np.array([x[0] for x in res]); U=np.array([x[1] for x in res]); t=np.array([x[2] for x in res]); y=np.array([x[3] for x in res])
    pf=lambda x: x[x>0].sum()/-x[x<=0].sum()
    eq=np.cumsum(U); dd=(np.maximum.accumulate(eq)-eq).max()
    return f"n{len(R)} wr{(U>0).mean()*100:.0f}% avgR{R.mean():+.3f} PF{pf(U):.2f} tr{pf(U[~t]):.2f} te{pf(U[t]):.2f} $/day{U.sum()/len(days):+.1f} maxDD${dd:.0f} medRisk{np.median(risks):.1f}pts | "+' '.join(f"{pf(U[y==yy]):.2f}" for yy in ['2022','2023','2024','2025','2026'])
for orm in (5,15):
  for st in ('mid','other'):
    for tp,lk in ((1.5,None),(2.0,None),(1.5,1.0),(2.0,1.0),(3.0,1.0)):
        for both in (False,True):
            print(f"OR{orm} {st:5s} tp{tp} lock{lk} {'2/day' if both else '1/day'}:", sim(orm,st,tp,lk,both=both))
