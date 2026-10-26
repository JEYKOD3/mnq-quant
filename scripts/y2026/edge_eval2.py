"""Eval effect of exit variants (stage 4b). Split = the same entry as two half-weight trades with different targets."""
import os, sys, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import more_eval as ME
import fast_pass as FP
import common as CM
from fast_plans import BASE
HERE = os.path.dirname(os.path.abspath(__file__))
def run(v4=None, tdp=None, pin=None, d2=None, evening=False):
    v4 = v4 or [(dict(tgtR=1.25), 1.0)]; tdp = tdp or [(dict(tgtR=1.5), 1.0)]; pin = pin or [(dict(tgtR=2), 1.0)]; d2 = d2 or [(dict(), 1.0)]
    tr = CM.news() + CM.h2(tgtR=2, flat=900)
    for kw, w in v4:
        for t in CM.v4(flat=900, **kw): u = dict(t); u['w'] = t['w'] * w; tr.append(u)
    for kw, w in tdp:
        for t in CM.tdp(flat=900, **kw): u = dict(t); u['w'] = t['w'] * w; tr.append(u)
    for kw, w in pin:
        for t in CM.pinball(cap=180, flat=900, **kw): u = dict(t); u['w'] = t['w'] * w; tr.append(u)
    for kw, w in d2:
        for t in CM.d2(th=.6, flat=795, **kw): u = dict(t); u['w'] = t['w'] * w; tr.append(u)
    if evening: tr += ME.EVT
    tr = [t for t in tr if t['d'] <= FP.LAST]; tr.sort(key=lambda t: (t['d'], t['eT'], FP.PRI.get(t['strat'], 9)))
    return FP.byday(tr)
V = [('BASE', {}),
     ('V4+ 1.0R', dict(v4=[(dict(tgtR=1.0), 1.0)])),
     ('V4+ 1.0R no BE', dict(v4=[(dict(tgtR=1.0, be_R=None), 1.0)])),
     ('V4+ split 1.25R/2R', dict(v4=[(dict(tgtR=1.25), .5), (dict(tgtR=2.0), .5)])),
     ('TDP 1.0R', dict(tdp=[(dict(tgtR=1.0), 1.0)])),
     ('TDP no target', dict(tdp=[(dict(tgtR=None), 1.0)])),
     ('Pinball 1.5R', dict(pin=[(dict(tgtR=1.5), 1.0)])),
     ('D2 tgt 1R', dict(d2=[(dict(tgtR=1.0), 1.0)])),
     ('D2 be0.5', dict(d2=[(dict(be_R=.5), 1.0)])),
     ('V4+1R TDP1R D2 1R +ev', dict(v4=[(dict(tgtR=1.0), 1.0)], tdp=[(dict(tgtR=1.0), 1.0)], d2=[(dict(tgtR=1.0), 1.0)], evening=True)),
     ('+ evening', dict(evening=True)),
]
out = {}
for nm, kw in V:
    byd = run(**kw); row = {y: FP.summ(FP.roll(byd, BASE, a, z)) for y, (a, z) in FP.YEARS.items()}; out[nm] = row
    print(f"{nm:28s} " + ' | '.join(f"{y}: p8 {row[y]['p8']:.3f} p10 {row[y]['p10']:.3f} p20 {row[y]['p20']:.3f} bust {row[y]['bust20']:.3f} med {row[y]['med']}" for y in FP.YEARS), flush=True)
json.dump(out, open(os.path.join(HERE, 'edge_eval2.json'), 'w'), indent=1, default=str)
