import sys, collections; sys.path.insert(0,'.')
exec(open('final_stats.py').read().split("for k,w in")[0])
from core import summary
from eth import S as ETH, seq
info={}
for d,b in ETH:
    A=[x for x in b if seq(1080)<=seq(x[0])<seq(180)]; L=[x for x in b if seq(180)<=seq(x[0])<seq(570)]; R=[x for x in b if 570<=x[0]<960]
    if len(A)<50 or len(L)<40 or len(R)<70: continue
    rng=max(x[2] for x in b if seq(x[0])<seq(570))-min(x[3] for x in b if seq(x[0])<seq(570))
    info[d]=dict(asia=A[-1][4]-A[0][1], london=L[-1][4]-L[0][1], on=L[-1][4]-A[0][1], rth=R[-1][4]-R[0][1], onrng=rng,
                 lon_hi_brk = max(x[2] for x in L)>max(x[2] for x in A), lon_lo_brk=min(x[3] for x in L)<min(x[3] for x in A))
sg=lambda x: 1 if x>0 else -1
ds=[d for d in info if d>=20220101]
def agree(a,b): return sum(sg(info[d][a])==sg(info[d][b]) for d in ds)/len(ds)
print(f'days {len(ds)}: P(RTH dir = London dir) {agree("london","rth"):.2f} | = Asia dir {agree("asia","rth"):.2f} | = overnight dir {agree("on","rth"):.2f} | Asia=London {agree("asia","london"):.2f}')
# conditional: when Asia and London agree
both=[d for d in ds if sg(info[d]['asia'])==sg(info[d]['london'])]
print(f'when Asia and London agree ({len(both)} days): P(RTH same) {sum(sg(info[d]["rth"])==sg(info[d]["london"]) for d in both)/len(both):.2f}')
# London broke Asia high only (one side)
up=[d for d in ds if info[d]['lon_hi_brk'] and not info[d]['lon_lo_brk']]; dn=[d for d in ds if info[d]['lon_lo_brk'] and not info[d]['lon_hi_brk']]
print(f'London broke only Asia high ({len(up)}d): RTH up {sum(info[d]["rth"]>0 for d in up)/len(up):.2f} | only Asia low ({len(dn)}d): RTH down {sum(info[d]["rth"]<0 for d in dn)/len(dn):.2f}')
for k,w in (('V4p_.4.4_none_2R',(1,0)),('D2b',(1,1))):
    tr=[t for t in stream(k,w) if t['d'] in info]
    for lab,key in (('London dir',lambda t: 'with' if sg(info[t['d']]['london'])==t['side'] else 'against'),
                    ('overnight dir',lambda t: 'with' if sg(info[t['d']]['on'])==t['side'] else 'against'),
                    ('Asia+London agree with trade',lambda t: 'both with' if sg(info[t['d']]['asia'])==t['side']==sg(info[t['d']]['london']) else ('both against' if sg(info[t['d']]['asia'])==-t['side']==sg(info[t['d']]['london']) else 'mixed'))):
        g=collections.defaultdict(list)
        for t in tr: g[key(t)].append(t)
        print(f"{k:18s} {lab:30s} "+' | '.join(f"{a}: n{len(v)} PF{summary(v,20220101,20241231)['pf']}/{summary(v,20250101,20261231)['pf']} avgR{summary(v)['avgR']:+.2f}" for a,v in sorted(g.items())))
