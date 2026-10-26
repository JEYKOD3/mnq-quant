"""D2 candidates inside the full team eval sim (other 5 strategies on live rules). Rolling start every trading day (2026, 2025)
and every 2nd day (2022, 2023-24). Pass within 40 trading days, fail, median days to pass. Also 1 MNQ per-year net."""
import json, sys
from common import *
O = old_team(); OTH = [t for t in O if t['strat'] != 'D2']
CAND = {
    'OLD 0.5 mkt, exit 15:00': None,
    'no D2': 'none',
    'A 0.5 mkt, flat 14:00': dict(th=.5, flat=840),
    'A2 0.5 mkt, 180m cap, flat 14:00': dict(th=.5, cap=180, flat=840),
    'B 0.4 pb5, flat 14:00': dict(th=.4, entry='pb5', flat=840),
    'B1 0.4 pb5, BE +1R, flat 14:00': dict(th=.4, entry='pb5', flat=840, be_R=1.0),
    'B2 0.4 pb5, 180m cap, flat 14:00': dict(th=.4, entry='pb5', cap=180, flat=840),
    'B3 0.4 pb5, flat 14:30': dict(th=.4, entry='pb5', flat=870),
    'B4 0.4 pb5, flat 15:00': dict(th=.4, entry='pb5', flat=900),
    'B5 0.35 pb5, flat 14:00': dict(th=.35, entry='pb5', flat=840),
    'B6 0.45 pb5, flat 14:00': dict(th=.45, entry='pb5', flat=840),
    'C 0.5 pb5, flat 14:00': dict(th=.5, entry='pb5', flat=840),
    'F 0.4 pb5, flat 13:00': dict(th=.4, entry='pb5', flat=780),
    'G 0.5 mkt, 60m cap': dict(th=.5, cap=60, flat=840),
    'H 0.5 mkt, 1R target, flat 14:00': dict(th=.5, tgtR=1.0, flat=840),
}
WIN = (('2026', 20260101, 20261023, 1), ('2025', 20250101, 20251231, 1), ('2022', 20220301, 20221231, 2), ('2023-24', 20230101, 20241231, 2))
def evals(tr, sd=None, **kw):
    out = {}
    for lab, a, z, st in WIN:
        r = rolling(tr, a, z, step=st, horizon=60, sd=sd, **kw)
        P = [x['n'] for x in r['R'] if x['res'] == 'P']
        out[lab] = dict(p40=round(sum(n <= 40 for n in P) / r['n'], 3), fail=round(r['f'], 3), med=sorted(P)[len(P) // 2] if P else None)
    return out
if __name__ == '__main__':
    res = {}
    for k, c in CAND.items():
        if c is None: d2t = [t for t in O if t['strat'] == 'D2']
        elif c == 'none': d2t = []
        else: d2t = d2(**c)
        tr = sorted(OTH + d2t, key=lambda t: (t['d'], t['eT']))
        yr = {y: stat1(d2t, y * 10000 + 101, y * 10000 + 1231) for y in range(2022, 2027)}
        ev = evals(tr)
        res[k] = dict(yr=yr, ev=ev)
        print(f"{k:36s} 1MNQ " + ' '.join(f"{y}:{yr[y]['net']:6d}/{yr[y]['pf']:.2f}" for y in yr) +
              ' | ' + ' '.join(f"{l} p40 {e['p40']:.0%} f {e['fail']:.0%} med {e['med']}" for l, e in ev.items()), flush=True)
    json.dump(res, open('d2_team.json', 'w'), indent=1)
