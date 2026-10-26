"""Dump SGP + WCC evening trades (rules from scripts/evening/e7_module.py) to JSON for the eval sim (separate process: module-name clash on 'common')."""
import sys, json
sys.path.insert(0, '/home/claude/mnq-quant/scripts/evening')
from ev_common import *
def sgp():
    tr = []
    for d in keys((0,)):
        e = EV[d]; a = e['adr']; g = e['o18'] - e['c17']
        if abs(g) < .05 * a: continue
        s = 1 if g > 0 else -1
        t = lim(d, s, e['o18'] - s * .5 * abs(g), 0, 17, .15 * a, None, 24)
        if t: t['rule'] = 'SGP'; t['rpts'] = .15 * a; tr.append(t)
    return tr
def wcc():
    tr = []
    for d in keys((3,)):
        e = EV[d]; a = e['adr']; x = e['o18'] - e['c16']
        if abs(x) < .05 * a or x == 0: continue
        t = mkt(d, 1 if x > 0 else -1, 1, .2 * a, None, 24)
        if t: t['rule'] = 'WCC'; t['rpts'] = .2 * a; tr.append(t)
    return tr
out = []
for t in sgp() + wcc():
    out.append(dict(d=t['d'], strat=t['rule'], side=t.get('side', t.get('s')), pts=t['pts'], r=t['rpts'], why='stop' if t['why'] == 'stop' else 'time exit', net=t.get('net')))
print(len(out), list(t.keys()))
json.dump(out, open('/home/claude/mnq-quant/scripts/y2026/more_evening.json', 'w'))
