"""Fair Pricing Theory, step 0: does price come back to the 'fair price' more often than chance?
For each NY morning (9:30-11:00, 1m bars): the first time price gets D points away from fair price F,
does it touch F before going S=25 pts further away?  Random-walk chance = S/(D+S).
Fair price versions: OPEN = 9:30 1m open; C929 = 9:29 close (= close of the 9:25 5m ETH bar).
Placebo: F = price at 10:00, events 10:00-11:30 (no session open) -> if the 'edge' shows here too, it's generic mean reversion, not the open."""
import sys, collections
sys.path.insert(0,'/home/claude/mnq-quant/scripts/lab')
from core import load
days=load()
eth={}
for ln in open('/home/claude/mnq-quant/data/raw/mnq_eth_5m.txt'):
    p=ln.strip().split('|')
    if len(p)<50: continue
    for x in p[1:]:
        t,o,h,l,c=x.split(',')
        if t=='925': eth[int(p[0])]=int(c)/4
S=25
def first_event(b, F, D, t0, t1):
    """returns (outcome, minutes) for the first touch of F+-D between t0..t1; outcome 'back','away','none','both'"""
    for i,(m,o,h,l,c) in enumerate(b):
        if m<t0 or m>=t1: continue
        up = h>=F+D; dn = l<=F-D
        if not (up or dn): continue
        s = 1 if up and not dn else (-1 if dn and not up else (1 if c>o else -1))
        lvl=F+s*D; away=F+s*(D+S)
        # same bar: did it also reach 'away'?
        if (s>0 and h>=away) or (s<0 and l<=away): return 'away',0
        for j in range(i+1,len(b)):
            m2,o2,h2,l2,c2=b[j]
            back = (l2<=F) if s>0 else (h2>=F)
            aw = (h2>=away) if s>0 else (l2<=away)
            if back and aw: return 'both',m2-m
            if back: return 'back',m2-m
            if aw: return 'away',m2-m
        return 'none',0
    return None,0
def study(name, getF, t0, t1, a=20220101, z=20261231):
    rows=[]
    for D in (25,38,50,75):
        res=collections.Counter(); yrs=collections.defaultdict(collections.Counter); mins=[]
        for d,b in days:
            if d<a or d>z: continue
            F=getF(d,b)
            if F is None: continue
            out,mm=first_event(b,F,D,t0,t1)
            if out is None: continue
            res[out]+=1; yrs[d//10000][out]+=1
            if out=='back': mins.append(mm)
        n=res['back']+res['away']+res['both']
        p=res['back']/n if n else 0; base=S/(D+S)
        py=' '.join(f"{y%100}:{yrs[y]['back']/max(1,yrs[y]['back']+yrs[y]['away']+yrs[y]['both']):.0%}" for y in sorted(yrs))
        mins.sort()
        rows.append(f"  D={D:3d}  events {n:4d}  back first {p:5.1%}  chance {base:5.1%}  edge {100*(p-base):+5.1f} pts  ambiguous {res['both']:3d}  median time back {mins[len(mins)//2] if mins else 0:3d}m  | {py}")
    print(name); print('\n'.join(rows))
def F_open(d,b): return b[0][1] if b[0][0]==570 else None
def F_c929(d,b): return eth.get(d)
def F_1000(d,b):
    x=[c for m,o,h,l,c in b if m==599]; return x[0] if x else None
print(f"Stop distance S = {S} pts beyond the touch. Window 9:30-11:00 unless noted. Days 2022 - Oct 2026.\n")
study("FAIR = 9:30 OPEN", F_open, 570, 660)
study("FAIR = 9:29 CLOSE", F_c929, 570, 660)
study("PLACEBO: FAIR = 10:00 price, window 10:00-11:30", F_1000, 600, 690)
