"""Edge optimization, stage 4: Lucid Flex 50K eval sim (same as fast_pass.py / more_eval.py) for the validated changes and
'A+ mode' sizing tilts. Strategy grades come from IS 2022-24 average net R per trade only (edge_slice.json):
A = Pinball, V4+ (2R exit), NEWS; B = TDP, D2 with the daily trend; C = H2, D2 against the trend.
Weight w scales the per-trade budget share (size_plan: b = min(w * f * cush, f * cush - used, budget - used)).
Writes edge_eval.json."""
import os, sys, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import more_eval as ME          # patches FP.size_plan with the evening $200 module; EVT = evening trades
import fast_pass as FP
import common as CM
from fast_plans import BASE
HERE = os.path.dirname(os.path.abspath(__file__))

def team(v4R=1.25, h2_from=0, evening=False, wA=1.0, wB=None, wC=None, drop=()):
    tr = CM.news() + CM.v4(tgtR=v4R, flat=900) + CM.d2(th=.6, flat=795) + CM.tdp(tgtR=1.5, flat=900) + CM.pinball(tgtR=2, cap=180, flat=900) + CM.h2(tgtR=2, flat=900)
    out = []
    for t in tr:
        if t['strat'] in drop: continue
        if t['strat'] == 'H2' and t['eT'] < h2_from: continue
        u = dict(t)
        if wB is not None or wC is not None:
            s = t['strat']
            if s in ('Pinball', 'V4+', 'NEWS'): u['w'] = wA
            elif s == 'TDP' or (s == 'D2' and t['w'] >= 1): u['w'] = wB if wB is not None else t['w']
            else: u['w'] = wC if wC is not None else t['w']
        out.append(u)
    if evening: out += ME.EVT
    out = [t for t in out if t['d'] <= FP.LAST]
    out.sort(key=lambda t: (t['d'], t['eT'], FP.PRI.get(t['strat'], 9)))
    return FP.byday(out)

def P(**k): d = dict(BASE); d.update(k); return d
VARS = [
    ('BASE v31', {}, BASE),
    ('+ evening', dict(evening=True), BASE),
    ('V4+ 2R', dict(v4R=2.0), BASE),
    ('V4+ 2R + H2 from 11:05', dict(v4R=2.0, h2_from=665), BASE),
    ('V4+ 2R + H2 11:05 + evening', dict(v4R=2.0, h2_from=665, evening=True), BASE),
    ('A+ tilt A1/B.6/C.3 +ev', dict(v4R=2.0, h2_from=665, evening=True, wA=1.0, wB=.6, wC=.3), BASE),
    ('A+ tilt A1/B.5/C0 +ev', dict(v4R=2.0, h2_from=665, evening=True, wA=1.0, wB=.5, wC=0.0), BASE),
    ('A+ tilt bud1500 A1/B.5/C.3 +ev', dict(v4R=2.0, h2_from=665, evening=True, wA=1.0, wB=.5, wC=.3), P(budget=1500)),
    ('A+ tilt bud1500 f.8 A1/B.5/C.3 +ev', dict(v4R=2.0, h2_from=665, evening=True, wA=1.0, wB=.5, wC=.3), P(budget=1500, f=.8)),
    ('A-only (Pin,V4+,NEWS) +ev', dict(v4R=2.0, evening=True, drop=('TDP', 'D2', 'H2')), BASE),
    ('A-only bud1500 +ev', dict(v4R=2.0, evening=True, drop=('TDP', 'D2', 'H2')), P(budget=1500)),
    ('V4+2R H2 11:05 ev bud1300', dict(v4R=2.0, h2_from=665, evening=True), P(budget=1300)),
]
if __name__ == '__main__':
    out = {}
    for nm, kw, plan in VARS:
        byd = team(**kw); row = {}
        for y, (a, z) in FP.YEARS.items(): row[y] = FP.summ(FP.roll(byd, plan, a, z))
        out[nm] = row
        print(f"{nm:36s} " + ' | '.join(f"{y}: p5 {row[y]['p5']:.3f} p8 {row[y]['p8']:.3f} p10 {row[y]['p10']:.3f} p20 {row[y]['p20']:.3f} bust {row[y]['bust20']:.3f} med {row[y]['med']} worst {row[y]['worst']}" for y in FP.YEARS), flush=True)
    json.dump(out, open(os.path.join(HERE, 'edge_eval.json'), 'w'), indent=1, default=str)
