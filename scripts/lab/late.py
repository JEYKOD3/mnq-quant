import sys; sys.path.insert(0,'.')
from cont import *
def fade(ET=930, th=.4, sfrac=.15, flat=959, ref='open', a=None):
    out=[]
    for d,b in days:
        f=F.get(d)
        if not f or d<20220101: continue
        idx=[i for i,x in enumerate(b) if x[0]==ET-1]
        if not idx: continue
        i=idx[0]; px=b[i][4]; base=f['open'] if ref=='open' else f['pdc']
        mv=(px-base)/f['adr']
        if abs(mv)<th: continue
        s=-1 if mv>0 else 1; eP=px+s*SLIP*T; stp=eP-s*sfrac*f['adr']; r=abs(eP-stp)
        xi,xP,why,mae,mfe=manage(b,i+1,s,eP,stp,None,0,flat)
        pts=(xP-eP)*s; out.append(dict(d=d,side=s,r=r,pts=pts,R=pts/r,why=why,f=f))
    return out
for ET_ in (900,930,945):
    for th in (0,.3,.5,.8):
        for sf in (.1,.2):
            rep(f"FADE at {ET_//60}:{ET_%60:02d} th{th} stop{sf}ADR exit 15:59",fade(ET_,th,sf))
