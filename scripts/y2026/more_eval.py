"""Eval impact of the more-trades survivors (Oct 26 2026). Same Lucid Flex sim and v31 sizing as fast_pass.py (BASE plan).
Evening SGP/WCC: own $200 budget (q = floor(200 / risk per MNQ), still under the room guard and the Lucid DLL), booked at the
start of the next trading day. RTH add-ons share the day budget like any team strategy (sized after the team, Pine order).
'solo' = the add-on is skipped if a team trade was entered earlier that day (knowable in real time)."""
import os, sys, json, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import fast_pass as FP
import more_trades as MT
from fast_plans import BASE

base = FP.build_trades()
EVT = []
for t in json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'more_evening.json'))):
    EVT.append(dict(d=t['d'], strat=t['strat'], side=t['side'], eT=0, eP=0.0, stp=0.0, xT=1, xP=0.0, why=t['why'], r=t['r'], pts=t['pts'], be=None, w=1.0, evb=200))

_orig = FP.size_plan
def size_plan(trs, cush, P, dayn, prof0, best0, target=3000., cons=.4):
    ev = [t for t in trs if t.get('evb')]; rest = [t for t in trs if not t.get('evb')]
    done = []; evnet = 0.0
    for t in ev:
        rc = (t['r'] + FP.SLIP * FP.T) * FP.PVX + 2 * FP.COMMX
        pts = t['pts'] - (2.0 if t['why'] == 'stop' else 0)          # evening stop stress, as in e7_module
        pc = pts * FP.PVX - 2 * FP.COMMX
        q = int(t['evb'] // rc)
        while q > 0 and q * FP.risk1(t) > cush - 100: q -= 1
        u = dict(t); u['q'] = q; u['rc'] = rc; u['pc'] = pc; u['netq'] = q * pc; done.append(u); evnet += u['netq']
    done += _orig(rest, cush + evnet, P, dayn, prof0 + evnet, best0, target, cons)
    return done
FP.size_plan = size_plan

ADD = {
    'TWAP-PB': lambda: MT.twap_pb(.2, .2, 1.5),
    'M2H': lambda: MT.m2h(.5),
    'PD-break': lambda: MT.pdlvl('break', .2, .5),
}
CACHE = {k: f() for k, f in ADD.items()}
first = collections.defaultdict(lambda: 9999)
for t in base: first[t['d']] = min(first[t['d']], t['eT'])

def team(adds=(), w=1.0, solo=False, evening=False):
    tr = list(base)
    for k in adds:
        for t in CACHE[k]:
            if solo and first[t['d']] < t['eT']: continue
            u = dict(t); u['w'] = w; tr.append(u)
    if evening: tr += EVT
    tr = [t for t in tr if t['d'] <= FP.LAST]
    tr.sort(key=lambda t: (t['d'], t['eT'], FP.PRI.get(t['strat'], 9)))
    return FP.byday(tr)

VARS = [
    ('BASE v31', dict()),
    ('+ evening SGP+WCC $200', dict(evening=True)),
    ('+ TWAP-PB', dict(adds=('TWAP-PB',))),
    ('+ M2H', dict(adds=('M2H',))),
    ('+ PD-break', dict(adds=('PD-break',))),
    ('+ TWAP-PB + M2H', dict(adds=('TWAP-PB', 'M2H'))),
    ('+ TWAP-PB + M2H solo', dict(adds=('TWAP-PB', 'M2H'), solo=True)),
    ('+ TWAP-PB + M2H half', dict(adds=('TWAP-PB', 'M2H'), w=.5)),
    ('+ TWAP-PB + M2H + evening', dict(adds=('TWAP-PB', 'M2H'), evening=True)),
    ('+ all three + evening', dict(adds=('TWAP-PB', 'M2H', 'PD-break'), evening=True)),
    ('+ all three + evening solo', dict(adds=('TWAP-PB', 'M2H', 'PD-break'), evening=True, solo=True)),
]

if __name__ == '__main__':
    out = {}
    for nm, kw in VARS:
        byd = team(**kw); row = {}
        for y, (a, z) in FP.YEARS.items(): row[y] = FP.summ(FP.roll(byd, BASE, a, z))
        act = sum(1 for d, v in byd.items() if 20260101 <= d and v)
        row['active_days_2026'] = act
        out[nm] = row
        print(f"{nm:30s} act26 {act:3d} | " + ' | '.join(f"{y}: p5 {row[y]['p5']:.3f} p8 {row[y]['p8']:.3f} p10 {row[y]['p10']:.3f} p20 {row[y]['p20']:.3f} bust {row[y]['bust20']:.3f} med {row[y]['med']}" for y in FP.YEARS), flush=True)
    json.dump(out, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'more_eval.json'), 'w'), indent=1, default=str)
