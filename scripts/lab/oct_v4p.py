import sys; sys.path.insert(0,'.')
exec(open('last4m.py').read().split("# V4+")[0])
tr={t['d']:t for t in v4_trades(days,F,tf=1,tgtR=2,bias=lambda f: v4bias(f,.4,.4,0))}
hm=lambda m:f"{m//60}:{m%60:02d}"
tot=0
for d,b in days:
    if d<20261001: continue
    f=F[d]; tdir=trend(d); i=D.index(d); sma=sum(C[x] for x in D[i-20:i])/20
    g,od=f['gap'],f['orDir']
    G=abs(g)>=.4; Dd=abs(od)>=.4
    bias=(1 if g>0 else -1) if G else ((1 if od>0 else -1) if Dd else 0)
    why=f"gap {g:+.2f} ADR, first-15 {od:+.2f} | trend {'UP' if tdir>0 else 'DOWN'} (prior close {C[D[i-1]]:.0f} vs SMA20 {sma:.0f})"
    if not bias: print(f"{d}  no trade: open not committed | {why}"); continue
    if bias!=tdir: print(f"{d}  no trade: bias {'LONG' if bias>0 else 'SHORT'} is AGAINST the daily trend | {why}"); continue
    t=tr.get(d)
    if not t or t['side']!=bias: print(f"{d}  bias {'LONG' if bias>0 else 'SHORT'} with trend, but no breakout-retest-rejection before 13:00 | {why}"); continue
    net=t['pts']-2*COMM/PV; tot+=net
    print(f"{d}  {'LONG ' if t['side']>0 else 'SHORT'} {hm(t['eT'])} @{t['eP']:.2f}  stop {t['stp']:.2f} ({t['r']:.0f}pt)  target {t['eP']+t['side']*2*t['r']:.2f}  -> {t['why']} {hm(t['xT'])} @{t['xP']:.2f}  {net:+.1f}pt = {net*2:+.0f}$/MNQ ({net/t['r']:+.2f}R) | {why}")
print(f"October total: {tot:+.1f} pts = {tot*2:+.0f}$ per MNQ")
print('\nWhat the trend filter skipped (counter-trend setups that would have been taken):')
s=0
for d in sorted(tr):
    t=tr[d]
    if d>=20261001 and trend(d)!=t['side']:
        net=t['pts']-2*COMM/PV; s+=net
        print(f"  {d} {'LONG ' if t['side']>0 else 'SHORT'} {hm(t['eT'])} -> {t['why']} {net:+.1f}pt ({net*2:+.0f}$)")
print(f"  skipped total {s:+.1f}pt = {s*2:+.0f}$")
