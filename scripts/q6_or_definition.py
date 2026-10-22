"""Q6/D11: OR15 vs OR30 vs IB60 size (/ADR) -> P(trend2)/P(range2), first-break continuation (day closes beyond OR in break dir), double-break rate."""
import sys,collections
sys.argv=['x','2022']; src=open('scripts/greenday_lab.py').read(); exec(src.split('# ---------- A) zigzag')[0])
for d,bars in days:
    f=feats[d]; oc=abs(f['c']-f['o'])/max(f['rng'],1)
    f['t2']='TREND2' if ((f['cl']>=.8 or f['cl']<=.2) and f['rng']>=1.0*f['adr'] and oc>=.6) else ('RANGE2' if (f['rng']<=.7*f['adr'] or .35<=f['cl']<=.65) else 'MID2')
def stats(win):
    rows=[]
    for d,bars in days:
        adr=feats[d]['adr']; w=[b for b in bars if b[0]<570+win]; rest=[b for b in bars if b[0]>=570+win]
        oh=max(b[2] for b in w); ol=min(b[3] for b in w); W=(oh-ol)/adr
        fb=0; dbl=False; cont=None
        for b in rest:
            if fb==0:
                if b[4]>oh: fb=1
                elif b[4]<ol: fb=-1
            else:
                if (fb==1 and b[4]<ol) or (fb==-1 and b[4]>oh): dbl=True; break
        c=feats[d]['c']
        if fb: cont = (c>oh) if fb==1 else (c<ol)
        rows.append((W,feats[d]['t2'],fb,dbl,cont))
    print(f'--- OR window {win}m ---')
    for lo,hi in [(0,.15),(.15,.25),(.25,.35),(.35,.5),(.5,.7),(.7,9)]:
        sel=[r for r in rows if lo<=r[0]<hi]; n=len(sel)
        if n<10: continue
        tr=sum(1 for r in sel if r[1]=='TREND2')/n; rg=sum(1 for r in sel if r[1]=='RANGE2')/n
        brk=[r for r in sel if r[2]]; db=sum(1 for r in brk if r[3])/max(len(brk),1); co=sum(1 for r in brk if r[4])/max(len(brk),1)
        print(f'OR/ADR [{lo},{hi}) n={n:4d} P(trend)={tr:.0%} P(range)={rg:.0%} | broke {len(brk)/n:.0%} double-break {db:.0%} close-beyond-OR-in-first-break-dir {co:.0%}')
for w in (15,30,60): stats(w)
