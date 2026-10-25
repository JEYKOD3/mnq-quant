from fp import *
import statistics as st
tr = [t for t in run(diag=True) if t['kind'] == 'rev']
L = [t for t in tr if t['why'] == 'stop']; W = [t for t in tr if t['why'] == 'tgt']
print(f"trades {len(tr)}  targets {len(W)}  stops {len(L)}  time exits {len(tr)-len(W)-len(L)}")
print(f"stops: median minutes to stop {st.median(t['bars'] for t in L)}, stopped within 3 min: {sum(t['bars']<=3 for t in L)/len(L):.0%}")
print(f"stops: median best gain before being stopped {st.median(t['mfe'] for t in L):.1f} pts; reached +10 first: {sum(t['mfe']>=10 for t in L)/len(L):.0%}, +19 (half target): {sum(t['mfe']>=19 for t in L)/len(L):.0%}")
print(f"stops that later hit the old target: {sum(t['after']['t'] for t in L)/len(L):.0%}; later reached fair price: {sum(t['after']['f'] for t in L)/len(L):.0%}")
print(f"winners: median minutes {st.median(t['bars'] for t in W)}, median worst drawdown first {st.median(t['mae'] for t in W):.1f} pts, went -15 first: {sum(t['mae']>=15 for t in W)/len(W):.0%}")
def by(lab, key, buckets):
    print('\n' + lab)
    for nm, f in buckets:
        v = [t for t in tr if f(key(t))]
        if v: s = stats(v); print(f"  {nm:22s} n {s['n']:5d} win {s['win']:.0%} PF {s['pf']:.2f}  avgR {s['avgR']:+.2f}")
by('distance to fair at entry (pts)', lambda t: t['dist'], [('30-50', lambda x: x < 50), ('50-75', lambda x: 50 <= x < 75), ('75-100', lambda x: 75 <= x < 100), ('100-150', lambda x: 100 <= x < 150), ('150+', lambda x: x >= 150)])
by('entry time', lambda t: t['em'], [('9:30-9:40', lambda x: x < 580), ('9:40-10:00', lambda x: 580 <= x < 600), ('10:00-10:30', lambda x: 600 <= x < 630), ('10:30-11:00', lambda x: x >= 630)])
by('trade # of the day', lambda t: t, [])
seq = collections.defaultdict(list); cnt = collections.Counter()
for t in tr: cnt[t['d']] += 1; seq[cnt[t['d']]].append(t)
for k in sorted(seq): s = stats(seq[k]); print(f"  trade {k}               n {s['n']:5d} win {s['win']:.0%} PF {s['pf']:.2f}")
by('stop size vs ADR (25 pts as % of 10-day avg range)', lambda t: 25 / FEAT[t['d']]['adr'] if t['d'] in FEAT else 0, [('<7%', lambda x: x < .07), ('7-10%', lambda x: .07 <= x < .10), ('10-14%', lambda x: .10 <= x < .14), ('>=14%', lambda x: x >= .14)])
by('news day (8:30 CPI/PPI/NFP)', lambda t: bool(EV.get(t['d'])), [('news', lambda x: x), ('normal', lambda x: not x)])
# did price ever return to F that day 9:30-11:00 (regime: reverting vs trending day)?
ret = {}
for d, b in DAYS:
    F = b[0][1]; touched = 0
    for x in b:
        if x[0] < 575 or x[0] >= 660: continue
        if x[3] <= F <= x[2]: touched += 1
    ret[d] = touched
by('day type: minutes price traded at the open price 9:35-11:00', lambda t: ret[t['d']], [('0 (trend day)', lambda x: x == 0), ('1-5', lambda x: 1 <= x <= 5), ('6+', lambda x: x > 5)])
print('\nshare of days by type:', collections.Counter('0' if v == 0 else '1-5' if v <= 5 else '6+' for v in ret.values()))
print('ADR by year:', {y: round(st.mean(f['adr'] for d, f in FEAT.items() if d // 10000 == y)) for y in range(2022, 2027)})
