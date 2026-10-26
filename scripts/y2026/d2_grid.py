"""D2 exit / entry grid, 1 MNQ, costs in. Writes d2_grid.json (one row per config: 2026 and 2022-25 stats)."""
import itertools, json, multiprocessing as mp
from common import *
MG = {'none': {}, 'be.5': dict(be_R=.5), 'be1': dict(be_R=1.0), 'tr.5@1': dict(trail_R=.5, trail_trig=1.0),
      'tr.5@.75': dict(trail_R=.5, trail_trig=.75), 't5@0': dict(t5=0.0), 't5@.5': dict(t5=.5), 't5@1': dict(t5=1.0)}
def job(c):
    th, entry, stop, tg, cap, flat, mg = c
    x = d2(th=th, entry=entry, stop=stop, tgtR=tg, cap=cap, flat=flat, **MG[mg])
    return dict(th=th, entry=entry, stop=stop, tgt=tg, cap=cap, flat=flat, mg=mg, z=stat1(x, 20260101), a=stat1(x, 20220101, 20251231),
                yr={y: stat1(x, y * 10000 + 101, y * 10000 + 1231)['net'] for y in range(2022, 2027)})
if __name__ == '__main__':
    C = [(th, e, st, tg, cap, fl, mg) for th in (.4, .5, .6) for e in ('mkt', 'pb0.1', 'pb5') for st in ('open', 'half') for tg in (None, .75, 1, 1.25, 1.5, 2)
         for cap in (0, 30, 60, 90, 120, 180) for fl in (780, 840) for mg in MG if not (st == 'half' and e != 'mkt')]
    C += [(.5, 'mkt', 'open', None, 0, 900, 'none')]  # live baseline
    with mp.Pool(2) as p: R = p.map(job, C, chunksize=40)
    json.dump(R, open('d2_grid.json', 'w'))
    print(len(R))
