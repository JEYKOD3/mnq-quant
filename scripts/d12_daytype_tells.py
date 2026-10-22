"""D12: Brooks early tells vs honest day labels (TREND2/RANGE2/MID2), MNQ RTH 1m->5m. Everything computed by 10:00 or 10:30 ET."""
import sys,collections
sys.argv=['x','2022']; src=open('scripts/greenday_lab.py').read(); exec(src.split('# ---------- A) zigzag')[0])
# honest labels
for d,bars in days:
    f=feats[d]; oc=abs(f['c']-f['o'])/max(f['rng'],1)
    f['t2']='TREND2' if ((f['cl']>=.8 or f['cl']<=.2) and f['rng']>=1.0*f['adr'] and oc>=.6) else ('RANGE2' if (f['rng']<=.7*f['adr'] or .35<=f['cl']<=.65) else 'MID2')
def agg(bars,n): return [(bars[i][0],bars[i][1],max(b[2] for b in bars[i:i+n]),min(b[3] for b in bars[i:i+n]),bars[i+n-1][4]) for i in range(0,len(bars)-n+1,n)]
DD=dict(days); prev=None; tells={}
pdLast=None
for d,bars in days:
    b5=agg(bars,5); adr=feats[d]['adr']
    first6=b5[:6]; first12=b5[:12]   # 9:30-10:00, 9:30-10:30
    def body(b): return abs(b[4]-b[1])
    def rng(b): return b[2]-b[3]
    def tb(b): return rng(b)>0 and body(b)>=.6*rng(b)
    def overlap(a,b): return max(0,min(a[2],b[2])-max(a[3],b[3]))/max(rng(a),1e-9)
    # tells
    b1=b5[0]; doji1 = rng(b1)>0 and body(b1)<.3*rng(b1)
    inPdLast = pdLast is not None and pdLast[1]<=b1[4]<=pdLast[0]
    gap=abs(feats[d]['o']-prev['c'])/adr if prev else 0
    # consecutive trend bars same dir in first 6 bars
    maxrun=0; run=0; dirn=0
    for b in first6:
        s=1 if b[4]>b[1] else -1
        if tb(b) and s==dirn: run+=1
        elif tb(b): run=1; dirn=s
        else: run=0; dirn=0
        maxrun=max(maxrun,run)
    # direction reversals (close-to-close sign changes) in first 12 bars
    sg=[1 if b[4]>b[1] else -1 for b in first12]; rev=sum(1 for i in range(1,len(sg)) if sg[i]!=sg[i-1])
    # overlapping tailed bars in first 12
    ovl=sum(1 for i in range(1,len(first12)) if overlap(first12[i],first12[i-1])>.7 and body(first12[i])<.5*rng(first12[i]))
    ema=None; k=2/22
    for b in b5[:12]: ema=b[4] if ema is None else ema+k*(b[4]-ema)
    tells[d]=dict(doji1=doji1,inPd=inPdLast,gap=gap,maxrun=maxrun,rev=rev,ovl=ovl,r1=rng(b1)/adr,
                  bar1strong=(tb(b1) and (rng(b1)-body(b1))<.3*rng(b1)))
    hi=max(b[2] for b in bars); lo=min(b[3] for b in bars)
    last=[b for b in bars if b[0]>=900]; pdLast=(max(b[2] for b in last),min(b[3] for b in last)); prev=feats[d]
base=collections.Counter(feats[d]['t2'] for d,_ in days); N=len(days)
def P(nm,cond):
    sel=[d for d,_ in days if cond(tells[d])]; n=len(sel)
    c=collections.Counter(feats[d]['t2'] for d in sel)
    print(f'{nm:40s} n={n:4d}  P(trend)={c["TREND2"]/max(n,1):.0%}  P(range)={c["RANGE2"]/max(n,1):.0%}')
print(f'base n={N} P(trend)={base["TREND2"]/N:.0%} P(range)={base["RANGE2"]/N:.0%}')
P('bar1 doji & inside pd last hour',lambda t:t['doji1'] and t['inPd'])
P('bar1 doji',lambda t:t['doji1'])
P('bar1 strong trend bar',lambda t:t['bar1strong'])
P('bar1 strong & gap>=.5ADR',lambda t:t['bar1strong'] and t['gap']>=.5)
P('>=3 consec trend bars by 10:00',lambda t:t['maxrun']>=3)
P('>=4 consec trend bars by 10:00',lambda t:t['maxrun']>=4)
P('gap>=.5ADR & >=3 trend bars',lambda t:t['gap']>=.5 and t['maxrun']>=3)
P('gap>=.5ADR',lambda t:t['gap']>=.5)
P('>=5 reversals in first 12 bars',lambda t:t['rev']>=5)
P('>=7 reversals in first 12 bars',lambda t:t['rev']>=7)
P('>=4 overlapping tailed bars',lambda t:t['ovl']>=4)
P('>=3 overlapping tailed bars',lambda t:t['ovl']>=3)
P('bar1 range >= .25ADR',lambda t:t['r1']>=.25)
P('bar1 range < .08ADR',lambda t:t['r1']<.08)
P('RANGE combo: rev>=6 or ovl>=4 or (doji1&inPd)',lambda t:t['rev']>=6 or t['ovl']>=4 or (t['doji1'] and t['inPd']))
P('TREND combo: maxrun>=3 & rev<=4',lambda t:t['maxrun']>=3 and t['rev']<=4)
P('TREND combo: (maxrun>=3 or bar1strong) & rev<=4 & ovl<=1',lambda t:(t['maxrun']>=3 or t['bar1strong']) and t['rev']<=4 and t['ovl']<=1)
