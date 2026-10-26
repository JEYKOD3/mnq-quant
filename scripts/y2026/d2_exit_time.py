"""D2 (0.5 ADR, market at 10:30, stop at open) with a single hard exit time: per year 1 MNQ and team eval pass rate."""
from d2_team import *
for th in (.5, .4, .6):
    for ex in (720, 750, 780, 795, 810, 825, 840, 870, 900):
        d2t = d2(th=th, flat=ex); tr = sorted(OTH + d2t, key=lambda t: (t['d'], t['eT']))
        yr = {y: stat1(d2t, y * 10000 + 101, y * 10000 + 1231) for y in range(2022, 2027)}; ev = evals(tr)
        print(f"th{th} exit {ex//60}:{ex%60:02d} " + ' '.join(f"{y}:{yr[y]['net']:6d}/{yr[y]['pf']:.2f}" for y in yr) + ' | ' + ' '.join(f"{l} {e['p40']:.0%}/{e['fail']:.0%}" for l, e in ev.items()), flush=True)
