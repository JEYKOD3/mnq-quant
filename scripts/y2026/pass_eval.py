"""Eval impact of the pass-strategy survivors (Oct 26 2026). Same Lucid Flex sim, v31 sizing (fast_plans.BASE) and evening module
handling as more_eval.py. Variants: survivor alone, v31 + evening + survivor, and 'stop the whole day after the first win of the
add-on' (team trades entered after the add-on's winning exit are dropped; knowable in real time)."""
import os, sys, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import more_eval as ME          # patches FP.size_plan for the evening module ($200 own budget)
FP = ME.FP
import pass_tested as PT
from fast_plans import BASE
HERE = os.path.dirname(os.path.abspath(__file__))

ADD = {
    'MC5 2R HTF (survivor)': PT.wmode(lambda: PT.mc5(2., True)),
    'MC1m 1R stop-after-win (headline, not a survivor)': PT.wmode(lambda: PT.mc1(1.)),
}
CACHE = {k: f() for k, f in ADD.items()}

def team(add=None, base=True, evening=True, daystop=False):
    tr = list(ME.base) if base else []
    if evening: tr += ME.EVT
    if add:
        a = [dict(t, w=1.0) for t in CACHE[add]]
        if daystop:
            winx = {}
            for t in a:
                if t['pts'] > 0: winx[t['d']] = min(winx.get(t['d'], 9999), t['xT'])
            tr = [t for t in tr if not (t['d'] in winx and t['eT'] >= winx[t['d']] and not t.get('evb'))]
        tr += a
    tr = [t for t in tr if t['d'] <= FP.LAST]
    tr.sort(key=lambda t: (t['d'], t['eT'], FP.PRI.get(t['strat'], 9)))
    return FP.byday(tr)

VARS = [('v31 + evening (reference)', dict())]
for k in ADD:
    VARS += [(f'{k} alone', dict(add=k, base=False, evening=False)),
             (f'v31 + evening + {k}', dict(add=k)),
             (f'v31 + evening + {k}, whole day stops after its first win', dict(add=k, daystop=True))]

if __name__ == '__main__':
    out = {}
    for nm, kw in VARS:
        byd = team(**kw); row = {}
        for y, (a, z) in FP.YEARS.items(): row[y] = FP.summ(FP.roll(byd, BASE, a, z))
        out[nm] = row
        print(f"{nm:80s} | " + ' | '.join(f"{y}: p5 {row[y]['p5']:.3f} p8 {row[y]['p8']:.3f} p10 {row[y]['p10']:.3f} p20 {row[y]['p20']:.3f} bust {row[y]['bust20']:.3f}" for y in FP.YEARS), flush=True)
    json.dump(out, open(os.path.join(HERE, 'pass_eval.json'), 'w'), indent=1, default=str)
