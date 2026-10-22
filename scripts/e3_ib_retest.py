"""E3: IB (9:30-10:30) break then retest. After 10:30, first 1m close beyond IB high/low (break). Wait for price to reach ext = IBH + k*IB (k=0.1 default) then retest: price returns to within tol*IB of IBH (touch). Enter on first 1m close back above IBH after the touch (long). stop = IBH - s*IB; target = IBH + T*IB (1.3 default) or R mult. cost 3. one trade/day (first retest only)."""
import sys,collections
sys.argv=['x','2022']; src=open('scripts/greenday_lab.py').read(); exec(src.split('# ---------- A) zigzag')[0])
COST=3.0
def run(bars,adr,k=0.1,tol=0.10,s=0.25,T=0.3,tgtR=None,last=870,flat=955,needExt=True,minTgt=0):
    ib=[b for b in bars if b[0]<630]
    if len(ib)<50: return []
    ibh=max(b[2] for b in ib); ibl=min(b[3] for b in ib); W=ibh-ibl
    if W<=0: return []
    trades=[]; pos=0; entry=stp=tgt=0; state=0; side=0; touched=False
    for i,(t,o,h,l,c) in enumerate(bars):
        if t<630: continue
        if pos!=0:
            if pos==1:
                if l<=stp: trades.append(stp-entry-COST); pos=0
                elif h>=tgt: trades.append(tgt-entry-COST); pos=0
            else:
                if h>=stp: trades.append(entry-stp-COST); pos=0
                elif l<=tgt: trades.append(entry-tgt-COST); pos=0
            if pos!=0 and t>=flat: trades.append((c-entry if pos==1 else entry-c)-COST); pos=0
            continue
        if trades or t>last: continue
        if state==0:
            if c>ibh: state=1; side=1; touched=False; ext=False
            elif c<ibl: state=1; side=-1; touched=False; ext=False
        elif state==1:
            if side==1:
                if h>=ibh+k*W: ext=True
                if (ext or not needExt) and l<=ibh+tol*W: touched=True
                if c<ibl: state=0; continue   # failed, reset to other side
                if touched and c>ibh and c>o:
                    e=c; stp=ibh-s*W; R=e-stp
                    if R<8: stp=e-8; R=8
                    g=max(tgtR*R if tgtR else T*W, minTgt)
                    pos=1; entry=e; tgt=e+g
            else:
                if l<=ibl-k*W: ext=True
                if (ext or not needExt) and h>=ibl-tol*W: touched=True
                if c>ibh: state=0; continue
                if touched and c<ibl and c<o:
                    e=c; stp=ibl+s*W; R=stp-e
                    if R<8: stp=e+8; R=8
                    g=max(tgtR*R if tgtR else T*W, minTgt)
                    pos=-1; entry=e; tgt=e-g
    return trades
def rep(name,**kw):
    tot=0;n=0;w=0;gp=gl=0;g=r=0;byY=collections.defaultdict(lambda:[0,0,0]);byT=collections.defaultdict(lambda:[0,0,0])
    for d,bars in days:
        tr=run(bars,feats[d]['adr'],**kw); p=sum(tr); tot+=p; n+=len(tr)
        for x in tr:
            if x>0: w+=1; gp+=x
            else: gl-=x
        if tr:
            y=d[:4]; byY[y][0]+=p; byY[y][1]+=(p>0); byY[y][2]+=(p<0); g+=(p>0); r+=(p<0); ty=feats[d]['type']; byT[ty][0]+=p; byT[ty][1]+=(p>0); byT[ty][2]+=(p<0)
    print(f'{name}: net {tot:+.0f}pts (${tot*2:+.0f}) n={n} win {w/max(n,1):.0%} PF {gp/max(gl,1):.2f} days G/R {g}/{r} ({g/max(g+r,1):.0%}) | '+' '.join(f"{y}:{round(v[0])}({v[1]}/{v[2]})" for y,v in sorted(byY.items()))+' | '+' '.join(f"{y}:{round(v[0])}({v[1]}/{v[2]})" for y,v in sorted(byT.items())))
rep('E3 k.1 tol.1 stop.25W tgt.3W')
rep('E3 tgt .5W',T=.5)
rep('E3 tgt 1R',tgtR=1)
rep('E3 tgt 2R',tgtR=2)
rep('E3 stop .15W tgt .3W',s=.15)
rep('E3 no ext needed, tgt .3W',needExt=False)
rep('E3 tol .05 tgt .3W',tol=.05)
rep('E3 tgt .3W min 25pt',minTgt=25)
rep('E3 2R min25',tgtR=2,minTgt=25)
print('--- with filters known at 10:30 (IB/ADR, move/ADR) ---')
def ibr(d): 
    bars=DD[d]; ib=[b for b in bars if b[0]<630]; return (max(b[2] for b in ib)-min(b[3] for b in ib))/max(feats[d]['adr'],1)
def mv(d):
    bars=DD[d]; ib=[b for b in bars if b[0]<630]; return abs(ib[-1][4]-bars[0][1])/max(feats[d]['adr'],1)
ALL=days; DD=dict(days)
for nm,cond in [('IB<0.5ADR',lambda d:ibr(d)<.5),('IB<0.4ADR',lambda d:ibr(d)<.4),('IB 0.4-0.7',lambda d:.4<=ibr(d)<.7),('IB>=0.7ADR',lambda d:ibr(d)>=.7),('mv>=0.3ADR',lambda d:mv(d)>=.3),('IB<0.5 & mv>=0.25',lambda d:ibr(d)<.5 and mv(d)>=.25)]:
    days=[(d,b) for d,b in ALL if cond(d)]
    rep(f'E3 tgt.3W | {nm} (n days {len(days)})')
    rep(f'E3 tgt.5W | {nm}',T=.5)
days=ALL
