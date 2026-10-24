"""Continuation family: at time T, if move from open (or prior close) >= th*ADR, enter with the move; stop variants; exit at flat time.
Also last-half-hour intraday momentum (Gao-Han-Li-Zhou): sign of first-30m return (incl. overnight) -> trade 15:30-15:59."""
import pickle, sys, collections
sys.path.insert(0,'.'); from core import *
days,F=pickle.load(open('/tmp/claude-0/-home-claude/afdbc088-26a4-5e84-b77d-b387ee40e855/scratchpad/lab.pkl','rb'))
def cont(ET=630, th=.4, ref='open', stop='open', sfrac=.25, flat=955, tgtR=None, offV4=False, maxR=None, minth=None):
    out=[]
    for d,b in days:
        f=F.get(d)
        if not f or d<20220101: continue
        if offV4 and v4bias(f): continue
        idx=[i for i,x in enumerate(b) if x[0]==ET-1]
        if not idx: continue
        i=idx[0]; px=b[i][4]; base=f['open'] if ref=='open' else f['pdc']
        mv=(px-base)/f['adr']
        if abs(mv)<th or (minth and abs(mv)>minth): continue
        s=1 if mv>0 else -1; eP=px+s*SLIP*T
        if stop=='open': stp=f['open']-s*T
        elif stop=='adr': stp=eP-s*sfrac*f['adr']
        elif stop=='half': stp=eP-s*abs(px-f['open'])/2
        elif stop=='lod':  # low/high of day so far
            stp=(min(x[3] for x in b[:i+1])-T) if s>0 else (max(x[2] for x in b[:i+1])+T)
        if stop=='pdc': stp=f['pdc']-s*T
        if (s>0 and stp>=eP) or (s<0 and stp<=eP): continue   # stop on wrong side -> no trade
        r=abs(eP-stp)
        if r<4: stp=eP-s*4; r=4
        if maxR and r>maxR*f['adr']: continue
        tgt=eP+s*tgtR*r if tgtR else None
        xi,xP,why,mae,mfe=manage(b,i+1,s,eP,stp,tgt,0,flat)
        pts=(xP-eP)*s
        out.append(dict(d=d,side=s,eT=ET,eP=eP,stp=stp,r=r,xT=b[xi][0],xP=xP,why=why,pts=pts,pnl=pts*PV-2*COMM,R=pts/r,maeR=mae/r,mfeR=mfe/r,f=f))
    return out
def rep(lab,tr):
    D=summary(tr,20220101,20241231); Tt=summary(tr,20250101,20261231); A=summary(tr,20220101)
    print(f"{lab:52s} DEV n{D['n']:3d} PF{D['pf']:5.2f} avgR{D['avgR']:+.2f} | TEST n{Tt['n']:3d} PF{Tt['pf']:5.2f} avgR{Tt['avgR']:+.2f} | ALL ddR{A['ddR']:4.1f} wr{A['wr']} | {yearly(tr)}")
if __name__=='__main__':
    print('### entry time x threshold, stop=open, hold to close')
    for ET_ in (600,615,630,660,690,720,780,840):
        for th in (.3,.4,.5,.6):
            rep(f"T={ET_//60}:{ET_%60:02d} th{th}",cont(ET_,th))
    print('### stops at 10:30 th .4')
    for st,sf in (('open',0),('half',0),('lod',0),('adr',.15),('adr',.2),('adr',.25),('adr',.3),('adr',.4)):
        rep(f'stop {st}{sf or ""}',cont(630,.4,stop=st,sfrac=sf))
    print('### exits at 10:30 th .4 stop open')
    for fl in (720,780,840,900,930): rep(f'flat {fl//60}:{fl%60:02d}',cont(630,.4,flat=fl))
    for tg in (1,1.5,2): rep(f'target {tg}R',cont(630,.4,tgtR=tg))
    print('### V4-off days only')
    for ET_ in (630,660,720):
        for th in (.4,.5): rep(f"offV4 T={ET_//60}:{ET_%60:02d} th{th}",cont(ET_,th,offV4=True))
    print('### ref = prior close (includes gap)')
    for ET_ in (630,720):
        for th in (.4,.6,.8): rep(f"refPDC T={ET_//60}:{ET_%60:02d} th{th}",cont(ET_,th,ref="pdc"))
    print('### last half hour momentum: signal at 15:30 (move since open), enter 15:30 exit 15:59, stop 0.15ADR')
    for th in (0,.2,.4,.6): rep(f'15:30 th{th}',cont(930,th,stop='adr',sfrac=.15,flat=959))
    for th in (0,.2,.4): rep(f'15:00 th{th} exit close',cont(900,th,stop='adr',sfrac=.2,flat=959))
