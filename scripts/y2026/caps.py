"""Priority 2: no hold to the close for Pinball, TDP, H2 (and V4+). Each variant swapped into the team (new D2 + live rules
for the rest). 1 MNQ per year + team eval (40% consistency, $50,100 lock). Writes caps.json."""
import json
from d2_team import evals
from common import *
O = old_team()
ND2 = d2(th=.6, flat=795)
BASE = [t for t in O if t['strat'] != 'D2'] + ND2
def ev_swap(name, tr):
    T_ = sorted([t for t in BASE if t['strat'] != name] + tr, key=lambda t: (t['d'], t['eT']))
    return evals(T_)
G = []
for tg in (None, 1, 1.5, 2):
    for cap in (0, 60, 120, 180, 240):
        for fl in (780, 840, 900, 955):
            G.append(('Pinball', dict(tgtR=tg, cap=cap, flat=fl), pinball))
for tg in (1, 1.25, 1.5, 2):
    for cap in (0, 60, 120, 180):
        for fl in (780, 840, 900, 955):
            G.append(('TDP', dict(tgtR=tg, cap=cap, flat=fl), tdp))
for tg in (1.5, 2):
    for cap in (None, 30, 60, 90):
        for fl in (780, 840, 900, 955):
            G.append(('H2', dict(tgtR=tg, cap=cap, flat=fl), h2))
for cap in (0, 120, 180, 240):
    for fl in (780, 840, 900, 955):
        G.append(('V4+', dict(cap=cap, flat=fl), v4))
out = []
for name, kw, fn in G:
    tr = fn(**kw)
    yr = {y: stat1(tr, y * 10000 + 101, y * 10000 + 1231) for y in range(2022, 2027)}
    ev = ev_swap(name, tr)
    out.append(dict(s=name, kw=kw, yr=yr, ev=ev))
    print(f"{name:7s} {str(kw):45s} " + ' '.join(f"{y}:{yr[y]['net']:6d}/{yr[y]['pf']:.2f}" for y in yr) + f" h{yr[2026]['hold']} | " +
          ' '.join(f"{l} {e['p40']:.0%}/{e['fail']:.0%}" for l, e in ev.items()), flush=True)
json.dump(out, open('caps.json', 'w'))
