"""D2 second scan near the robust zone, scored inside the team eval sim. Writes d2_scan2.json."""
import json
from d2_team import *
MG = {'none': {}, 'be1': dict(be_R=1.0), 'tr.5@1': dict(trail_R=.5, trail_trig=1.0)}
out = []
for th in (.5, .55, .6, .65, .7):
    for ex in (780, 795, 810):
        for mg in MG:
            for tg in (None, 1.5, 2):
                d2t = d2(th=th, flat=ex, tgtR=tg, **MG[mg]); tr = sorted(OTH + d2t, key=lambda t: (t['d'], t['eT']))
                yr = {y: stat1(d2t, y * 10000 + 101, y * 10000 + 1231) for y in range(2022, 2027)}; ev = evals(tr)
                out.append(dict(th=th, ex=ex, mg=mg, tg=tg, yr=yr, ev=ev))
                print(f"th{th} {ex//60}:{ex%60:02d} {mg:6s} tg{tg} " + ' '.join(f"{y}:{yr[y]['net']:6d}" for y in yr) + ' | ' + ' '.join(f"{l} {e['p40']:.0%}/{e['fail']:.0%}" for l, e in ev.items()), flush=True)
json.dump(out, open('d2_scan2.json', 'w'))
