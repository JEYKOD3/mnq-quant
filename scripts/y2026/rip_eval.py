"""Eval impact of the two rip_lvl survivors (v5tod k4, t15) added to v31 + evening. Same sim as pass_eval.py."""
import os, sys, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import more_eval as ME
FP = ME.FP
import rip_lvl as RL
from fast_plans import BASE
HERE = os.path.dirname(os.path.abspath(__file__))
ADD = {'RIP v5tod k4 open t15': RL.runB('v5tod', 4, 'open', 'bar', 't15', 930),
       'RIP v5tod k4 vwap t15': RL.runB('v5tod', 4, 'vwap', 'bar', 't15', 930)}
def team(add=None):
    tr = list(ME.base) + ME.EVT
    if add: tr += [dict(t, w=1.0) for t in ADD[add]]
    tr = [t for t in tr if t['d'] <= FP.LAST]
    tr.sort(key=lambda t: (t['d'], t['eT'], FP.PRI.get(t['strat'], 9)))
    return FP.byday(tr)
out = {}
for nm in [None] + list(ADD):
    byd = team(nm); row = {}
    for y, (a, z) in FP.YEARS.items(): row[y] = FP.summ(FP.roll(byd, BASE, a, z))
    out[nm or 'v31 + evening (reference)'] = row
    print(f"{nm or 'reference':28s} | " + ' | '.join(f"{y}: p5 {row[y]['p5']:.3f} p8 {row[y]['p8']:.3f} p10 {row[y]['p10']:.3f} p20 {row[y]['p20']:.3f} bust {row[y]['bust20']:.3f}" for y in FP.YEARS), flush=True)
json.dump(out, open(os.path.join(HERE, 'rip_eval.json'), 'w'), indent=1, default=str)
