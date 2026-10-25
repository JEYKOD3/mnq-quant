from base import *
import datetime
rows = []
prevtype = {}
for d, b in DAYS:
    if d not in FEAT or len(b) < 380: continue
    f = FEAT[d]; adr = f['adr']
    hi = max(x[2] for x in b); lo = min(x[3] for x in b); o = b[0][1]; c = b[-1][4]
    trend = abs(c - o) >= .5 * (hi - lo)
    cut = 60  # 10:30
    h1 = max(x[2] for x in b[:cut]); l1 = min(x[3] for x in b[:cut]); p = b[cut - 1][4]
    on = overnight(d)
    r = dict(d=d, P=per(d), trend=trend, up=c > o,
             eff=abs(p - o) / ((h1 - l1) or 1), w=(h1 - l1) / adr, gap=abs(f['gap']), onr=((on[0] - on[1]) / adr) if on else None,
             outside=p > f['pdh'] or p < f['pdl'], prevtrend=prevtype.get('last'), news=bool(EV.get(d)), fomc=d in FOMC,
             wd=datetime.date(d // 10000, d // 100 % 100, d % 100).weekday(), pdrel=f['pdRel'],
             cont=(c - p) * (1 if p > o else -1) / adr, contpos=(c - p) * (1 if p > o else -1) > 0,
             atpx=p, nearext=(p - l1) / ((h1 - l1) or 1))
    rows.append(r); prevtype['last'] = trend
def show(lab, fn):
    out = []
    for P in 'AZ':
        v = [r for r in rows if r['P'] == P and fn(r)]
        if not v: out.append('-'); continue
        out.append(f"trend {sum(r['trend'] for r in v)/len(v):.0%} | 10:30->close same way {sum(r['contpos'] for r in v)/len(v):.0%} avg {100*sum(r['cont'] for r in v)/len(v):+.1f}% ADR (n{len(v)})")
    print(f"  {lab:38s} 22-24: {out[0]:58s} 25-26: {out[1]}")
print('Q6. Trend day = close-open >= 50% of day range. Features known at 10:30.')
show('ALL DAYS', lambda r: True)
for a, b_ in ((0, .3), (.3, .6), (.6, 1.01)): show(f'first-hour efficiency {a}-{b_}', lambda r, a=a, b_=b_: a <= r['eff'] < b_)
for a, b_ in ((0, .3), (.3, .45), (.45, 9)): show(f'first-hour range {int(a*100)}-{int(b_*100) if b_<9 else "up"}% ADR', lambda r, a=a, b_=b_: a <= r['w'] < b_)
show('price outside prior-day range at 10:30', lambda r: r['outside'])
show('price inside prior-day range at 10:30', lambda r: not r['outside'])
for a, b_ in ((0, .2), (.2, .5), (.5, 9)): show(f'gap {int(a*100)}-{int(b_*100) if b_<9 else "up"}% ADR', lambda r, a=a, b_=b_: a <= r['gap'] < b_)
for a, b_ in ((0, .35), (.35, .55), (.55, 9)): show(f'overnight range {int(a*100)}-{int(b_*100) if b_<9 else "up"}% ADR', lambda r, a=a, b_=b_: r['onr'] is not None and a <= r['onr'] < b_)
show('prior day was a trend day', lambda r: r['prevtrend'] is True)
show('prior day was a range day', lambda r: r['prevtrend'] is False)
show('10:30 price at extreme of first hour (top/bottom 15%)', lambda r: r['nearext'] >= .85 or r['nearext'] <= .15)
show('eff>=0.6 AND outside prior range', lambda r: r['eff'] >= .6 and r['outside'])
show('eff>=0.6 AND at extreme', lambda r: r['eff'] >= .6 and (r['nearext'] >= .85 or r['nearext'] <= .15))
print('\nQ7. Segments')
for i, n in enumerate(['Mon', 'Tue', 'Wed', 'Thu', 'Fri']): show(n, lambda r, i=i: r['wd'] == i)
show('CPI/PPI/NFP day', lambda r: r['news']); show('FOMC day', lambda r: r['fomc'])
show('prior day range > 1.2 ADR (volatile)', lambda r: r['pdrel'] > 1.2); show('prior day range < 0.8 ADR (quiet)', lambda r: r['pdrel'] < .8)
