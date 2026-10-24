import sys, collections, csv; sys.path.insert(0,'.')
exec(open('final_stats.py').read().split("for k,w in")[0])
from core import summary, SLIP, T, COMM, PV
from hir import days, F
EV=collections.defaultdict(set)
for r in csv.DictReader(open('/home/claude/mnq-quant/data/macro_dates.csv')): EV[int(r['date'])].add(r['event'])
def tag(d):
    e=EV.get(d,set())
    if 'FOMC' in e: return 'FOMC'
    if 'CPI' in e: return 'CPI'
    if 'NFP' in e: return 'NFP'
    if 'PPI' in e: return 'PPI'
    return 'none'
for k,w in (('V4p_.4.4_none_2R',(1,0)),('D2b',(1,1))):
    tr=stream(k,w); g=collections.defaultdict(list)
    for t in tr: g[tag(t['d'])].append(t)
    print(k,' | '.join(f"{a}: n{len(v)} PF{summary(v)['pf']} avgR{summary(v)['avgR']:+.2f}" for a,v in sorted(g.items())))
# share of days V4 fires on event days
n_ev=collections.Counter(tag(d) for d,_ in days if d>=20220101); print('event-day counts',dict(n_ev))
# FOMC 14:00 breakout: range 14:00-14:09 (10 min), break after 14:10 until 15:00, stop other side, exit 15:55 / tgt
def fomc(rng_end=840+10, tgtR=None, stopk='range', flat=955):
    out=[]
    for d,b in days:
        if tag(d)!='FOMC' or d<20220101: continue
        A=[x for x in b if 840<=x[0]<rng_end]
        if not A: continue
        hi=max(x[2] for x in A); lo=min(x[3] for x in A)
        for i,x in enumerate(b):
            m,o,h,l,c=x
            if m<rng_end or m>900: continue
            s=1 if c>hi else (-1 if c<lo else 0)
            if not s: continue
            eP=c+s*SLIP*T; stp=(lo-T) if s>0 else (hi+T); r=abs(eP-stp); tg=eP+s*tgtR*r if tgtR else None; xP=None
            for y in b[i+1:]:
                if (s>0 and y[3]<=stp) or (s<0 and y[2]>=stp): xP=stp-s*SLIP*T; break
                if tg and ((s>0 and y[2]>=tg) or (s<0 and y[3]<=tg)): xP=tg; break
                if y[0]>=flat: xP=y[4]; break
            if xP is None: xP=b[-1][4]
            out.append(dict(d=d,R=((xP-eP)*s-2*COMM/PV)/r,r=r)); break
    return out
for re in (845,850,855,860):
    for tg in (None,2,3):
        o=fomc(re,tg); R=[t['R'] for t in o]
        g=sum(x for x in R if x>0); l=-sum(x for x in R if x<=0)
        print(f"FOMC BO range 14:00-{re//60}:{re%60:02d} tgt {tg}: n{len(o)} wr{100*sum(x>0 for x in R)/len(R):.0f}% PF{g/l if l else 9.9:.2f} avgR{sum(R)/len(R):+.2f} avg stop {sum(t['r'] for t in o)/len(o):.0f}pt")
