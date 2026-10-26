"""Strategy-variant ablation for the fast pass (BASE v31 sizing, Lucid Flex rules, rolling 20-day evals)."""
import json
from fast_pass import *
from fast_plans import BASE, V
def team(news_=True, v4k={}, d2k={}, tdk={}, pnk={}, h2k={}, h2w=None, drop=()):
    tr = (CM.news() if news_ and SYM == 'MNQ' else []) + CM.v4(**dict(dict(flat=900), **v4k)) + CM.d2(**dict(dict(th=.6, flat=795), **d2k)) + \
         CM.tdp(**dict(dict(tgtR=1.5, flat=900), **tdk)) + CM.pinball(**dict(dict(tgtR=2, cap=180, flat=900), **pnk)) + CM.h2(**dict(dict(tgtR=2, flat=900), **h2k))
    tr = [dict(t) for t in tr if t['strat'] not in drop and t['d'] <= LAST]
    if h2w is not None:
        for t in tr:
            if t['strat'] == 'H2': t['w'] = h2w
    tr.sort(key=lambda t: (t['d'], t['eT'], PRI.get(t['strat'], 9)))
    return tr
VARS = [
    ('BASE team', {}),
    ('D2 th .5', dict(d2k=dict(th=.5))),
    ('D2 half stop', dict(d2k=dict(stop='half'))),
    ('D2 th .5 half stop', dict(d2k=dict(th=.5, stop='half'))),
    ('D2 2R target', dict(d2k=dict(tgtR=2))),
    ('V4+ 2R', dict(v4k=dict(tgtR=2.0))),
    ('V4+ 1R', dict(v4k=dict(tgtR=1.0))),
    ('V4+ no BE', dict(v4k=dict(be_R=None))),
    ('TDP 1R', dict(tdk=dict(tgtR=1.0))),
    ('TDP 2R', dict(tdk=dict(tgtR=2.0))),
    ('H2 full size', dict(h2w=1.0)),
    ('H2 1.5R', dict(h2k=dict(tgtR=1.5))),
    ('H2 th .3', dict(h2k=dict(th=.3))),
    ('drop Pinball', dict(drop=('Pinball',))),
    ('drop TDP', dict(drop=('TDP',))),
    ('H2 full + drop Pin', dict(h2w=1.0, drop=('Pinball',))),
    ('H2 full + D2 th.5', dict(h2w=1.0, d2k=dict(th=.5))),
]
if __name__ == '__main__':
    out = {}
    for nm, k in VARS:
        tr = team(**k); byd = byday(tr); row = {}
        for y, (a, z) in YEARS.items(): row[y] = summ(roll(byd, BASE, a, z))
        s1 = {y: stat1(tr, a, z)['net'] for y, (a, z) in YEARS.items()}
        out[nm] = dict(k=str(k), net1=s1, **row)
        print(f"{nm:22s} 1lot {s1} |", ' | '.join(f"{y}: p5 {row[y]['p5']:.2f} p8 {row[y]['p8']:.2f} p10 {row[y]['p10']:.2f} p20 {row[y]['p20']:.2f} bust {row[y]['bust20']:.2f}" for y in YEARS), flush=True)
    json.dump(out, open(f'fast_variants_{SYM}.json', 'w'), indent=1, default=str)
