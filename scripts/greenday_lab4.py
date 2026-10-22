import sys,collections; sys.argv=['x','2022']
src=open('scripts/greenday_lab.py').read()
exec(src.split('# ---------- A) zigzag')[0])
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

# honest labels: TREND2 = close in top/bottom 20% AND range>=1.0 ADR AND open-to-close move >= 0.6 range; RANGE2 = range<=0.7 ADR or close mid (0.35-0.65)
for d,bars in days:
    f=feats[d]; oc=abs(f['c']-f['o'])/max(f['rng'],1)
    f['t2']='TREND2' if ((f['cl']>=.8 or f['cl']<=.2) and f['rng']>=1.0*f['adr'] and oc>=.6) else ('RANGE2' if (f['rng']<=.7*f['adr'] or .35<=f['cl']<=.65) else 'MID2')
tc=collections.Counter(f['t2'] for f in feats.values()); print('labels2',dict(tc))
def P(cond):
    sel=[d for d,_ in days if cond(early[d])]
    tr=sum(1 for d in sel if feats[d]['t2']=='TREND2'); rg=sum(1 for d in sel if feats[d]['t2']=='RANGE2')
    return f'n={len(sel)} P(trend2)={tr/max(len(sel),1):.0%} P(range2)={rg/max(len(sel),1):.0%}'
print('base', P(lambda e:True))
for nm,c in [('ib<0.35adr',lambda e:e['ibr']<.35),('ib<0.5adr',lambda e:e['ibr']<.5),('ib>0.7adr',lambda e:e['ibr']>.7),('ib>1.0adr',lambda e:e['ibr']>1.0),
 ('|dir15|>.6',lambda e:abs(e['dir15'])>.6),('pb<0.4',lambda e:e['pb']<.4),('pb>0.8',lambda e:e['pb']>.8),('outside',lambda e:e['outside']==1),
 ('mv@1030>0.5adr',lambda e:e['mvADR']>.5),('mv>.5 & pb<.4',lambda e:e['mvADR']>.5 and e['pb']<.4),('mv>.5&pb<.4&outside',lambda e:e['mvADR']>.5 and e['pb']<.4 and e['outside']),
 ('mv<.2adr',lambda e:e['mvADR']<.2)]:
    print(f'{nm:24s}',P(c))
# direction persistence: P(close > open) given side at 10:30, by mv bucket
for lo,hi in [(0,.2),(.2,.4),(.4,.6),(.6,1),(1,9)]:
    sel=[d for d,_ in days if lo<=early[d]['mvADR']<hi]
    agree=sum(1 for d in sel if (feats[d]['c']-feats[d]['o'])*early[d]['side']>0)
    # move from 10:30 close to day close in direction of side, in ADR
    cont=[ (feats[d]['c']-[b for b in dict(days)[d] if b[0]<630][-1][4])*early[d]['side']/max(feats[d]['adr'],1) for d in sel]
    cont.sort()
    print(f'mv@1030 in [{lo},{hi}) ADR: n={len(sel)} P(day close same side as 10:30)={agree/max(len(sel),1):.0%} median further move same dir {cont[len(cont)//2]:+.2f} ADR, mean {sum(cont)/max(len(cont),1):+.2f}')
