import sys,collections; sys.argv=['x','2022']
src=open('scripts/greenday_lab.py').read()
exec(src.split('# ---------- A) zigzag')[0])
exec('def ema_series'+src.split('def ema_series')[1].split("report('H2 EMA21 1m, tgt 2R, cost3'")[0])
def agg(bars,n):
    return [(bars[i][0],bars[i][1],max(b[2] for b in bars[i:i+n]),min(b[3] for b in bars[i:i+n]),bars[i+n-1][4]) for i in range(0,len(bars)-n+1,n)]
# early features at 10:30 (known then): ib/adr, first15 dir strength, open vs prior day range, pullback depth at 10:30 vs move since open, close10:30 side of open
prevf=None; early={}
pd=None
for d,bars in days:
    f=feats[d]; ib=[b for b in bars if b[0]<630]; o=bars[0][1]
    ibh=max(b[2] for b in ib); ibl=min(b[3] for b in ib); c1030=ib[-1][4]
    f15=[b for b in ib if b[0]<585]; c15=f15[-1][4]; r15=max(b[2] for b in f15)-min(b[3] for b in f15)
    dir15=(c15-o)/max(r15,1)
    mv=c1030-o; ext=ibh-o if mv>0 else o-ibl
    pb = (ibh-c1030)/ext if mv>0 and ext>0 else ((c1030-ibl)/ext if mv<0 and ext>0 else 1)
    outside = 1 if (pd and (o>pd[0] or o<pd[1])) else 0
    early[d]=dict(ibr=(ibh-ibl)/max(f['adr'],1),dir15=dir15,pb=pb,outside=outside,side=1 if c1030>o else -1,mvADR=abs(mv)/max(f['adr'],1))
    pd=(max(b[2] for b in bars),min(b[3] for b in bars))
def P(cond):
    sel=[d for d,_ in days if cond(early[d])]; 
    tr=sum(1 for d in sel if feats[d]['type']=='TREND'); rg=sum(1 for d in sel if feats[d]['type']=='RANGE')
    return f'n={len(sel)} P(trend)={tr/max(len(sel),1):.0%} P(range)={rg/max(len(sel),1):.0%}'
print('base', P(lambda e:True))
print('ib<0.35adr', P(lambda e:e['ibr']<.35)); print('ib>0.7adr', P(lambda e:e['ibr']>.7))
print('|dir15|>.6', P(lambda e:abs(e['dir15'])>.6)); print('pb<0.4', P(lambda e:e['pb']<.4)); print('pb>0.8', P(lambda e:e['pb']>.8))
print('outside', P(lambda e:e['outside']==1)); print('mv@1030>0.5adr', P(lambda e:e['mvADR']>.5))
print('combo pb<.4 & mv>.4adr', P(lambda e:e['pb']<.4 and e['mvADR']>.4))
print('combo pb<.4 & mv>.4adr & |dir15|>.5', P(lambda e:e['pb']<.4 and e['mvADR']>.4 and abs(e['dir15'])>.5))
# run 5m H2 only after 10:30 on combo days, with bias forced? use run as-is but first=630
days5=[(d,agg(b,5)) for d,b in days]
D=days
def sel_run(cond,**kw):
    out=[]
    def fn(bars):
        return run(bars,**kw)
    return fn
for name,cond in [('all',lambda e:True),('combo pb<.4&mv>.4',lambda e:e['pb']<.4 and e['mvADR']>.4),('combo3',lambda e:e['pb']<.4 and e['mvADR']>.4 and abs(e['dir15'])>.5),('range-like ib>.7 or pb>.8',lambda e:e['ibr']>.7 or e['pb']>.8)]:
    days=[(d,b) for d,b in days5 if cond(early[d])]
    report(f'5m H2 after 10:30 | {name}',lambda b: run(b,tgtR=2.0,minStop=10,maxStop=60,first=630))
    report(f'5m H2 after 10:30 1R | {name}',lambda b: run(b,tgtR=1.0,minStop=10,maxStop=60,first=630))
