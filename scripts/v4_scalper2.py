"""Round 2: friction + target floor + management variants, Jun-Oct 2026 dev, holdouts reported. Priority grid."""
import sys,itertools,statistics; sys.argv=['x']
src=open('scripts/v4_scalper.py').read().split("if __name__=='__main__':")[0]
exec(src)
DEV=('20260601','20261020'); HO1=('20260101','20260531'); HO2=('20220101','20251231')
def show(tag,P):
    e=evaluate(P,*DEV); h1=evaluate(P,*HO1); h2=evaluate(P,*HO2)
    print(f"{tag:58s} DEV net{e['net']:+6d} n{e['n']:3d} win{e['win']}% PF{e['pf']:.2f} G/R{e['g']}/{e['r']} DD{e['dd']} | JanMay PF{h1['pf']:.2f} {h1['net']:+d} | 22-25 PF{h2['pf']:.2f} {h2['net']:+d}")
    return e
for comm in [2.37,0.50]:
    globals()['COMM']=comm
    print(f'\n===== commission ${comm}/side/contract =====')
    best=[]
    for tp1,maxStop,runR,be,trail,first,last,maxTr in itertools.product([10,15,20,25,30],[20,30],[2,3],[True,False],[0,3],[585,600],[645,840],[2,4]):
        P=dict(BASE); P.update(tp1pts=tp1,maxStop=maxStop,runR=runR,be=be,trail=trail,first=first,last=last,maxTr=maxTr,lvlD=0.75,maxHold=60)
        e=evaluate(P,*DEV); best.append((e['pf'] if e['n']>=25 else 0,e,P))
    best.sort(key=lambda x:(x[0],x[1]['net']),reverse=True)
    print('median PF across grid:', statistics.median(x[0] for x in best), ' | top 8:')
    for _,e,P in best[:8]:
        show(f"tp1 {P['tp1pts']} stop<={P['maxStop']} run{P['runR']}R be{int(P['be'])} trail{P['trail']} {P['first']}-{P['last']} max{P['maxTr']}",P)
    # by tp1 size: best PF for each
    print('best PF by TP1 size:', {t:max(x[0] for x in best if x[2]['tp1pts']==t) for t in [10,15,20,25,30]})
