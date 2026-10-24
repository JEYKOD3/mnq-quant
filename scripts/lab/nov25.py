import sys; sys.path.insert(0,'.')
exec(open('month_all.py').read().split("for lab,a,z in")[0])
hm=lambda m:f"{m//60}:{m%60:02d}"
for mode in ('1mnq','eval'):
    net,per,n,rows=run(20251101,20251130,mode)
    g=sum(1 for _,p,_ in rows if p>0); rd=sum(1 for _,p,_ in rows if p<0)
    print(f"NOVEMBER 2025 [{'1 MNQ per signal' if mode=='1mnq' else 'eval sizing 50K'}]: net {net:+.0f}$ | "+', '.join(f"{k} {per[k]:+.0f}$ ({n[k]} tr)" for k in ('V4+','D2','PIN','H2'))+f" | days {len(rows)}: {g} green / {rd} red")
print('trades:')
for d in sorted(x for x in S if 20251101<=x<=20251130):
    for t in S[d]:
        nm='H2' if 'setup' in t else ('D2' if t['eT']==630 and 'w' in t else ('V4+' if t in E.V4 else 'PIN'))
        net=t['pts']-2*COMM/PV
        print(f"  {d} {nm:4s} {'LONG ' if t['side']>0 else 'SHORT'} {hm(t['eT'])} stop {t['r']:.0f}pt -> {t['why']:6s} {net:+7.1f}pt {net*2:+6.0f}$")
import statistics
nov=[v for k,v in mo.items() if k%100==11]; print('all Novembers 2022-2025 at 1 MNQ:',{k:round(v) for k,v in mo.items() if k%100==11})
