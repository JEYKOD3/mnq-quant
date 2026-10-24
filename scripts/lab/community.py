"""Community NQ strategies, mechanical versions. All on RTH 1m (+ overnight levels from ETH 5m). Results in R after costs, dev/test split.
Each returns trades dict(d,side,r,pts,why). Uses hir.mk/run_trade for exits."""
import sys, collections; sys.path.insert(0,'.')
from core import *
from hir import days, F, TRD, mk, rstats, run_trade
from eth import S as ETH, seq
ON={}
for d,b in ETH:
    pre=[x for x in b if seq(x[0])<seq(570)]
    if pre: ON[d]=(max(x[2] for x in pre),min(x[3] for x in pre))
def bars5(b): return agg(b,5)
def sweep(level='pd', win=(575,720), minpen=2, back_within=3, stopbuf=1, tgt='2R', flt='none', offv4=False):
    """turtle soup: price trades beyond level (high above PDH by >=minpen pts), then a 1m close back below the level within back_within bars -> short.
    stop = sweep extreme + buf; target 2R / opposite level / EOD"""
    out=[]
    for d,b in days:
        f=F.get(d)
        if not f or d<20220101: continue
        if offv4 and v4bias(f): continue
        if level=='pd': H,L=f['pdh'],f['pdl']
        elif level=='on':
            if d not in ON: continue
            H,L=ON[d]
        else: H,L=f['orh'],f['orl']
        if not (L< b[0][1] <H): continue   # open inside the levels
        state=None; done=False
        for i,(m,o,h,l,c) in enumerate(b):
            if done or m>win[1]: break
            if m<win[0]: continue
            for s,lvl in ((-1,H),(1,L)):
                pen=(h-lvl) if s<0 else (lvl-l)
                if pen>=minpen and (state is None or state[0]!=s): state=(s,i,(h if s<0 else l))
            if state:
                s,i0,ext=state
                ext=max(ext,h) if s<0 else min(ext,l); state=(s,i0,ext)
                lvl=H if s<0 else L
                if i-i0>back_within: state=None; continue
                if (s<0 and c<lvl) or (s>0 and c>lvl):
                    if flt=='trend' and TRD[d][0]!=s: state=None; continue
                    eP=c+s*SLIP*T; stp=ext-s*stopbuf
                    r=abs(eP-stp)
                    if r<4: state=None; continue
                    tg = eP+s*2*r if tgt=='2R' else (eP+s*3*r if tgt=='3R' else None)
                    if tgt=='opp': tg=(L if s<0 else H)
                    t=mk(d,b,i+1,s,eP,stp,tgtR=None)
                    if tg is not None:
                        rr=abs(tg-eP)/r; t=mk(d,b,i+1,s,eP,stp,tgtR=rr)
                    if t: out.append(t)
                    done=True
    return out
def ib_break(ibend=630, last=840, stop='mid', tgt=None, flt='trend', offv4=False):
    """initial balance (9:30-ibend) breakout: 5m close beyond IB -> enter next bar; stop IB mid or other side; exit EOD or tgt"""
    out=[]
    for d,b in days:
        f=F.get(d)
        if not f or d<20220101: continue
        if offv4 and v4bias(f): continue
        IB=[x for x in b if x[0]<ibend]; hi=max(x[2] for x in IB); lo=min(x[3] for x in IB)
        for i,(m,o,h,l,c) in enumerate(b):
            if m<ibend or m>last: continue
            if (m+1)%5: continue
            s=1 if c>hi else (-1 if c<lo else 0)
            if not s: continue
            if flt=='trend' and TRD[d][0]!=s: break
            eP=c+s*SLIP*T; stp=((hi+lo)/2) if stop=='mid' else (lo-T if s>0 else hi+T)
            t=mk(d,b,i+1,s,eP,stp,tgtR=tgt)
            if t: out.append(t)
            break
    return out
def silver_bullet(win=(600,660), tf=1, tgt='2R', flt='trend', stopbuf=1):
    """ICT silver bullet: first FVG formed in 10:00-11:00 (3-candle gap) in bias direction; enter limit at FVG edge on retrace;
    stop beyond candle-1 extreme; target 2R or PDH/PDL. bias = daily trend (flt) or direction of displacement."""
    out=[]
    for d,b1 in days:
        f=F.get(d)
        if not f or d<20220101: continue
        b=agg(b1,tf); fvg=None
        for i in range(2,len(b)):
            m=b[i][0]
            if m>win[1]+60: break
            if fvg is None and win[0]<=m<win[1]:
                c1,c2,c3=b[i-2],b[i-1],b[i]
                if c1[2]<c3[3]: s=1; top=c3[3]; bot=c1[2]; stp=c1[3]-stopbuf
                elif c1[3]>c3[2]: s=-1; top=c1[3]; bot=c3[2]; stp=c1[2]+stopbuf
                else: continue
                if flt=='trend' and TRD[d][0]!=s: continue
                fvg=(s,top,bot,stp,i); continue
            if fvg:
                s,top,bot,stp,i0=fvg
                if m>win[1]+30: break
                entry = top if s>0 else bot
                if (s>0 and b[i][3]<=entry) or (s<0 and b[i][2]>=entry):
                    eP=entry+s*SLIP*T; r=abs(eP-stp)
                    if r<4: break
                    if tgt=='pd':
                        tg=f['pdh'] if s>0 else f['pdl']; rr=(tg-eP)*s/r
                        if rr<1: break
                        t=mk(d,b,i+1,s,eP,stp,tgtR=rr)
                    else: t=mk(d,b,i+1,s,eP,stp,tgtR=(2 if tgt=='2R' else None))
                    if t: out.append(t)
                    break
    return out
def gapfill(minG=.2, maxG=.8, stopk=.5):
    """fade the gap toward prior close: enter at 9:30 open (next bar), target pdc, stop = open +/- stopk*gap"""
    out=[]
    for d,b in days:
        f=F.get(d)
        if not f or d<20220101: continue
        g=f['gap']
        if not (minG<=abs(g)<=maxG): continue
        s=-1 if g>0 else 1; eP=b[1][1]+s*SLIP*T; gappts=abs(f['open']-f['pdc'])
        stp=eP-s*stopk*gappts; r=abs(eP-stp); tg=abs(f['pdc']-eP)/r
        if r<4 or tg<=0: continue
        t=mk(d,b,1,s,eP,stp,tgtR=tg)
        if t: out.append(t)
    return out
if __name__=='__main__':
    for lv in ('pd','on'):
        for win in ((575,720),(575,660),(660,900)):
            for tg in ('2R','opp',None):
                for flt in ('none','trend'):
                    rstats(sweep(lv,win,2,3,1,tg,flt),f"SWEEP {lv} {win[0]//60}:{win[0]%60:02d}-{win[1]//60}:{win[1]%60:02d} tgt {tg} {flt}")
    for ibe in (600,630):
        for st in ('mid','opp'):
            for tg in (None,2):
                for flt in ('none','trend'):
                    rstats(ib_break(ibe,840,st,tg,flt),f"IB{ibe-570}m break stop {st} tgt {tg} {flt}")
    for tf in (1,5):
        for tg in ('2R','pd',None):
            for flt in ('none','trend'):
                rstats(silver_bullet((600,660),tf,tg,flt),f"SILVER BULLET {tf}m tgt {tg} {flt}")
    for mg,xg in ((.1,.3),(.2,.5),(.3,.8)):
        for sk in (.5,1.0):
            rstats(gapfill(mg,xg,sk),f"GAP FILL {mg}-{xg} ADR stop {sk}x gap")
