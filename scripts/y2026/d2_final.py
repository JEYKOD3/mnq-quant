"""Final D2 table: old vs recommended vs alternatives, per year 1 MNQ and team eval (stop-day off and N=3)."""
import json
from d2_team import *
V = {'OLD 0.5 ADR, 10:30 market, exit 15:00': None, 'NEW 0.6 ADR, 10:30 market, exit 13:15': dict(th=.6, flat=795),
     'ALT 0.5 ADR, 10:30 market, exit 13:30': dict(th=.5, flat=810), 'FAST 0.5 ADR, 60 min cap': dict(th=.5, cap=60, flat=840),
     'TARGET 0.5 ADR, 1R target, exit 14:00': dict(th=.5, tgtR=1.0, flat=840), 'BE 0.6 ADR, BE at +1R, exit 13:15': dict(th=.6, flat=795, be_R=1.0),
     'No D2': 'none'}
res = {}
for k, c in V.items():
    d2t = [t for t in O if t['strat'] == 'D2'] if c is None else ([] if c == 'none' else d2(**c))
    tr = sorted(OTH + d2t, key=lambda t: (t['d'], t['eT']))
    yr = {y: stat1(d2t, y * 10000 + 101, y * 10000 + 1231) for y in range(2022, 2027)}
    res[k] = dict(yr=yr, ev50=evals(tr, cons=.5), ev=evals(tr), ev3=evals(tr, sd=3), why={w: sum(1 for t in d2t if t['d'] >= 20260101 and t['why'] == w) for w in ('stop', 'target', 'time exit', 'breakeven', 'trail')})
    print(k, yr[2026]); print('  40%', res[k]['ev']); print('  50%', res[k]['ev50']); print('  40%+N3', res[k]['ev3'])
json.dump(res, open('d2_final.json', 'w'), indent=1)
