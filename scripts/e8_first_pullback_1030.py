"""E8: after 10:30, side = sign(c1030 - open) if |move|>=X ADR. Enter on the first pullback: price retraces >= P pts (or P2 ADR) from the extreme since open,
then a 1m bar closes back in the direction (close > prior high for longs). stop = beyond pullback extreme + 1tk (min 8, max M). target = T*ADR or R mult. One trade/day (and variant: up to 3). cost 3 pts."""
import sys,collections
sys.argv=['x','2022']; src=open('scripts/greenday_lab.py').read(); exec(src.split('# ---------- A) zigzag')[0])
COST=3.0
def run(bars,adr,X=0.4,pbFrac=0.25,tgtADR=0.10,tgtR=None,maxStop=60,maxTr=1,last=840,flat=955,useTrail=False):
    o=bars[0][1]; ib=[b for b in bars if b[0]<630]
    if len(ib)<50: return []
    c1030=ib[-1][4]; mv=(c1030-o)/adr
    if abs(mv)<X: return []
    side=1 if mv>0 else -1
    ext = max(b[2] for b in ib) if side==1 else min(b[3] for b in ib)
    trades=[]; pos=0; entry=stp=tgt=0; pbExt=None; inPB=False; n=0; tick=.25
    for i,(t,oo,h,l,c) in enumerate(bars):
        if t<630: continue
        if pos!=0:
            if pos==1:
                if l<=stp: trades.append(stp-entry-COST); pos=0
                elif h>=tgt: trades.append(tgt-entry-COST); pos=0
            else:
                if h>=stp: trades.append(entry-stp-COST); pos=0
                elif l<=tgt: trades.append(entry-tgt-COST); pos=0
            if pos!=0 and t>=flat: trades.append((c-entry if pos==1 else entry-c)-COST); pos=0
            if pos!=0: continue
        if n>=maxTr or t>last: continue
        # track extreme and pullback
        if side==1:
            if h>ext: ext=h; inPB=False; pbExt=None
            depth=ext-l
            if depth>=pbFrac*adr*0.5: inPB=True   # pullback >= pbFrac*(0.5 ADR) pts
            if inPB: pbExt=l if pbExt is None else min(pbExt,l)
            if inPB and i>0 and c>bars[i-1][2] and c>oo:
                e=c; s=pbExt-tick; R=e-s
                if R<8: s=e-8; R=8
                if R<=maxStop:
                    g=tgtR*R if tgtR else tgtADR*adr
                    pos=1; entry=e; stp=s; tgt=e+g; n+=1; inPB=False; pbExt=None
        else:
            if l<ext: ext=l; inPB=False; pbExt=None
            depth=h-ext
            if depth>=pbFrac*adr*0.5: inPB=True
            if inPB: pbExt=h if pbExt is None else max(pbExt,h)
            if inPB and i>0 and c<bars[i-1][3] and c<oo:
                e=c; s=pbExt+tick; R=s-e
                if R<8: s=e+8; R=8
                if R<=maxStop:
                    g=tgtR*R if tgtR else tgtADR*adr
                    pos=-1; entry=e; stp=s; tgt=e-g; n+=1; inPB=False; pbExt=None
    return trades
def rep(name,**kw):
    tot=0;n=0;w=0;gp=gl=0;g=r=0;byY=collections.defaultdict(lambda:[0,0,0])
    for d,bars in days:
        tr=run(bars,feats[d]['adr'],**kw); p=sum(tr); tot+=p; n+=len(tr)
        for x in tr:
            if x>0: w+=1; gp+=x
            else: gl-=x
        if tr:
            y=d[:4]; byY[y][0]+=p; byY[y][1]+=(p>0); byY[y][2]+=(p<0); g+=(p>0); r+=(p<0)
    print(f'{name}: net {tot:+.0f}pts (${tot*2:+.0f}) n={n} win {w/max(n,1):.0%} PF {gp/max(gl,1):.2f} days G/R {g}/{r} ({g/max(g+r,1):.0%}) | '+' '.join(f"{y}:{round(v[0])}({v[1]}/{v[2]})" for y,v in sorted(byY.items())))
rep('E8 X.4 pb.25 tgt.10ADR 1tr')
rep('E8 X.4 pb.25 tgt.15ADR 1tr',tgtADR=.15)
rep('E8 X.4 pb.25 tgt 2R 1tr',tgtR=2)
rep('E8 X.4 pb.25 tgt 1R 1tr',tgtR=1)
rep('E8 X.4 pb.4 tgt.10ADR 1tr',pbFrac=.4)
rep('E8 X.6 pb.25 tgt.10ADR 1tr',X=.6)
rep('E8 X.3 pb.25 tgt.10ADR 1tr',X=.3)
rep('E8 X.4 pb.25 tgt.10ADR 3tr',maxTr=3)
rep('E8 X.4 pb.25 tgt.10ADR 1tr last 12:00',last=720)
