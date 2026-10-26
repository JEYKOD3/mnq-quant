"""FOMC-minutes days: existing strategies lose. Breakdown + permutation check (random 39-day sets, and Wednesdays only)."""
import random, datetime as dt, collections
from avoid import ALL, EXT, rep
random.seed(3)
MD = sorted(d for d in EXT if 'FOMC_MIN' in EXT[d])
tr = [t for t in ALL if t['d'] in MD]
for t in tr: print(f"  {t['d']} {t['strat']:7s} entry {t['eT']//60}:{t['eT']%60:02d} exit {t['xT']//60}:{t['xT']%60:02d} ${t['net']:+.0f}")
rep('minutes days, trades closed before 13:55', [t for t in tr if t['xT'] < 835])
rep('minutes days, trades open at/after 13:55', [t for t in tr if t['xT'] >= 835])
for s in ('V4+', 'D2', 'Pinball', 'H2', 'TDP'): rep(f'minutes days {s}', [t for t in tr if t['strat'] == s])
byday = collections.defaultdict(float)
for t in ALL: byday[t['d']] += t['net']
alld = sorted(set(d for d, in [(t['d'],) for t in ALL]))
from fp import DAYS
DL = [d for d, _ in DAYS]
obs = sum(byday.get(d, 0) for d in MD if d in set(DL))
wed = [d for d in DL if dt.date(d // 10000, d // 100 % 100, d % 100).weekday() == 2 and d not in MD]
n = sum(1 for d in MD if d in set(DL))
for lab, pool in (('any day', [d for d in DL if d not in MD]), ('Wednesdays', wed)):
    k = sum(sum(byday.get(d, 0) for d in random.sample(pool, n)) <= obs for _ in range(5000))
    print(f'  observed total on {n} minutes days ${obs:+.0f}; random {lab}: p = {k / 5000:.3f}')
print('\nby strategy x event day')
for s in ('V4+', 'D2', 'Pinball', 'H2', 'TDP'):
    print(s)
    for ev in ('CPI', 'PPI', 'NFP', 'GDP', 'PCE', 'RETAIL', 'ISM_MFG', 'ISM_SRV', 'JOLTS', 'FOMC', 'FOMC_MIN', 'TESTIMONY'):
        rep(f'  {s} on {ev} days', [t for t in ALL if t['strat'] == s and ev in EXT.get(t['d'], {})])
    rep(f'  {s} all', [t for t in ALL if t['strat'] == s])
