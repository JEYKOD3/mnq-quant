"""Verified-source strategies (Crabel, Williams, Raschke, Fisher) mechanized on MNQ RTH 1m."""
import sys, collections; sys.path.insert(0,'.')
from core import *
from hir import days, F, TRD, mk, rstats
D=[d for d,_ in days]; DB={d:b for d,b in days}
DAILY={d:(b[0][1],max(x[2] for x in b),min(x[3] for x in b),b[-1][4]) for d,b in days}
def prev(d,k=1):
    i=D.index(d); return D[i-k] if i-k>=0 else None
def stop_order_day(d,b,buy,sell,stopfn,tgtR=None,start=570,end=955,first_only=True,flt=None):
    for i,(m,o,h,l,c) in enumerate(b):
        if m<start or m>end: continue
        for s,lvl in ((1,buy),(-1,sell)):
            if lvl is None: continue
            if (s>0 and h>=lvl) or (s<0 and l<=lvl):
                if flt and flt!=s: return None
                eP=(max(o,lvl) if s>0 else min(o,lvl))+s*SLIP*T
                stp=stopfn(s,eP,i)
                if (s>0 and stp>=eP) or (s<0 and stp<=eP): return None
                # same bar stop check
                if (s>0 and l<=stp) or (s<0 and h>=stp):
                    r=abs(eP-stp); return dict(d=d,s=s,r=r,pts=(stp-s*SLIP*T-eP)*s,R=0,Rn=((stp-s*SLIP*T-eP)*s-2*COMM/PV)/r,why='stop',hold=1,eT=m)
                return mk(d,b,i+1,s,eP,stp,tgtR=tgtR)
    return None
def crabel_stretch(mult=2, nr=None, tgtR=None, trendf=False, minR=4):
    out=[]
    for k,d in enumerate(D):
        if d<20220101 or k<12: continue
        b=DB[d]; o=b[0][1]
        noise=[min(DAILY[x][1]-DAILY[x][0],DAILY[x][0]-DAILY[x][2]) for x in D[k-10:k]]
        st=mult*sum(noise)/10
        if nr:
            rng=[DAILY[x][1]-DAILY[x][2] for x in D[k-nr:k]]
            if rng[-1]!=min(rng): continue
        buy=o+st; sell=o-st
        t=stop_order_day(d,b,buy,sell,lambda s,eP,i: sell if s>0 else buy,tgtR,flt=(TRD[d][0] if trendf else None))
        if t and t['r']>=minR: out.append(t)
    return out
def williams(kf=.4, tgtR=None, trendf=False, stopk=None):
    out=[]
    for k,d in enumerate(D):
        if d<20220101 or k<2: continue
        b=DB[d]; o=b[0][1]; pd=DAILY[D[k-1]]; R=pd[1]-pd[2]
        buy=o+kf*R; sell=o-kf*R
        sf=(lambda s,eP,i: sell if s>0 else buy) if stopk is None else (lambda s,eP,i: eP-s*stopk*R)
        t=stop_order_day(d,b,buy,sell,sf,tgtR,flt=(TRD[d][0] if trendf else None))
        if t: out.append(t)
    return out
def oops(minGap=0, end=720, tgt='close', trendf=False):
    out=[]
    for k,d in enumerate(D):
        if d<20220101 or k<2: continue
        f=F.get(d); b=DB[d]; o=b[0][1]; pdh,pdl,pdc=f['pdh'],f['pdl'],f['pdc']
        if o<pdl-minGap*f['adr']: buy,sell=pdl,None
        elif o>pdh+minGap*f['adr']: buy,sell=None,pdh
        else: continue
        def sf(s,eP,i):
            seg=b[:i+1]; return (min(x[3] for x in seg)-T) if s>0 else (max(x[2] for x in seg)+T)
        tg=None
        t=stop_order_day(d,b,buy,sell,sf,None,end=end,flt=(TRD[d][0] if trendf else None))
        if t and tgt=='pdc' and t['r']>0:
            # recompute with pdc target
            pass
        if t: out.append(t)
    return out
def r8020(pen=5, end=720, trendf=False):
    out=[]
    for k,d in enumerate(D):
        if d<20220101 or k<2: continue
        f=F.get(d); b=DB[d]; po,ph,pl,pc=DAILY[D[k-1]]; rg=ph-pl
        if rg<=0: continue
        if (po-pl)/rg>=.8 and (pc-pl)/rg<=.2: side=1
        elif (po-pl)/rg<=.2 and (pc-pl)/rg>=.8: side=-1
        else: continue
        if trendf and TRD[d][0]!=side: continue
        armed=False
        for i,(m,o,h,l,c) in enumerate(b):
            if m>end: break
            if side>0 and l<=pl-pen: armed=True
            if side<0 and h>=ph+pen: armed=True
            if armed and ((side>0 and h>=pl) or (side<0 and l<=ph)) and (i>0):
                lvl=pl if side>0 else ph
                eP=(max(o,lvl) if side>0 else min(o,lvl))+side*SLIP*T
                seg=b[:i+1]; stp=(min(x[3] for x in seg)-T) if side>0 else (max(x[2] for x in seg)+T)
                if abs(eP-stp)<4: break
                t=mk(d,b,i+1,side,eP,stp); 
                if t: out.append(t)
                break
    return out
def acd(Afrac=.1, orm=15, hold=8, trendf=False):
    out=[]
    for d,b in days:
        f=F.get(d)
        if not f or d<20220101: continue
        A=Afrac*f['adr']; ORb=[x for x in b if x[0]<570+orm]; hi=max(x[2] for x in ORb); lo=min(x[3] for x in ORb)
        up=hi+A; dn=lo-A; cnt={1:0,-1:0}
        for i,(m,o,h,l,c) in enumerate(b):
            if m<570+orm or m>900: continue
            cnt[1]=cnt[1]+1 if c>up else 0; cnt[-1]=cnt[-1]+1 if c<dn else 0
            s=1 if cnt[1]>=hold else (-1 if cnt[-1]>=hold else 0)
            if s:
                if trendf and TRD[d][0]!=s: break
                eP=c+s*SLIP*T; stp=(lo-T) if s>0 else (hi+T)
                t=mk(d,b,i+1,s,eP,stp)
                if t: out.append(t)
                break
    return out
def pinball(trendf=False):
    out=[]; rs=[]
    closes=[DAILY[x][3] for x in D]
    def rsi3(k):
        ch=[closes[j]-closes[j-1] for j in range(k-3,k)]
        up=sum(x for x in ch if x>0); dn=-sum(x for x in ch if x<0)
        return 100 if dn==0 else 100-100/(1+up/dn)
    for k,d in enumerate(D):
        if d<20220101 or k<5: continue
        r=rsi3(k)   # uses closes up to D[k-1]
        side=1 if r<30 else (-1 if r>70 else 0)
        if not side: continue
        if trendf and TRD[d][0]!=side: continue
        b=DB[d]; IB=[x for x in b if x[0]<630]; hi=max(x[2] for x in IB); lo=min(x[3] for x in IB)
        t=stop_order_day(d,b,hi+T if side>0 else None,lo-T if side<0 else None,lambda s,eP,i: (lo-T) if s>0 else (hi+T),start=630,end=900)
        if t: out.append(t)
    return out
def early_entry(trendf=False):
    out=[]; r1=[]
    for d,b in days:
        b5=agg(b,5)
        if len(b5)<10: continue
        x1=b5[0]; rng=x1[2]-x1[3]; avg=sum(r1[-10:])/10 if len(r1)>=10 else None; r1.append(rng)
        if d<20220101 or not avg or rng<=avg or rng==0: continue
        o,h,l,c=x1[1],x1[2],x1[3],x1[4]
        if (o-l)<=.1*rng and (h-c)<=.1*rng: s=1
        elif (h-o)<=.1*rng and (c-l)<=.1*rng: s=-1
        else: continue
        x2=b5[1]
        if (x2[4]-x1[4])*s<=0: continue
        if trendf and TRD[d][0]!=s: continue
        eP=x2[4]+s*SLIP*T; stp=(l-T) if s>0 else (h+T)
        idx=[i for i,x in enumerate(b) if x[0]==580][0]
        t=mk(d,b,idx,s,eP,stp)
        if t: out.append(t)
    return out
if __name__=='__main__':
    for mult in (1,1.5,2):
        for nr in (None,4,7):
            for tg in (None,2):
                for tf in (False,True):
                    rstats(crabel_stretch(mult,nr,tg,tf),f"CRABEL stretch x{mult} NR{nr} tgt{tg} trend{int(tf)}")
    for kf in (.2,.3,.4,.6):
        for tf in (False,True):
            for stk in (None,.25):
                rstats(williams(kf,None,tf,stk),f"WILLIAMS volBO k{kf} stop {'opp' if stk is None else stk} trend{int(tf)}")
    for mg in (0,.15):
        for tf in (False,True): rstats(oops(mg,720,'close',tf),f"WILLIAMS OOPS gap>{mg}ADR trend{int(tf)}")
    for pen in (5,10,15):
        for tf in (False,True): rstats(r8020(pen,720,tf),f"RASCHKE 80-20 pen{pen} trend{int(tf)}")
    for af in (.1,.15):
        for orm in (15,30):
            for tf in (False,True): rstats(acd(af,orm,8 if orm==15 else 15,tf),f"FISHER ACD A{af} OR{orm} trend{int(tf)}")
    for tf in (False,True): rstats(pinball(tf),f"RASCHKE pinball trend{int(tf)}")
    for tf in (False,True): rstats(early_entry(tf),f"CRABEL early entry trend{int(tf)}")
