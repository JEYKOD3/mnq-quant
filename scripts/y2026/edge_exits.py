"""Edge optimization, stage 3: exits. MFE/MAE profile of the live (v31) exits, then an exit grid per strategy built with
the same 1m walker (common.py). Selection on IS 2022-24 by average net R per trade (1 lot, after costs), report VAL 2025 /
OOS 2026. Partial take-profit = 50/50 blend of two exit variants on the same entries (R is linear in contracts).
Writes edge_exits.json."""
import os, sys, json, statistics, itertools
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common as CM
import fast_pass as FP
HERE = os.path.dirname(os.path.abspath(__file__))
PV = 2.0; SLIPX = 8.0
def blk(d): return 'IS' if d < 20250101 else ('VAL' if d < 20260101 else 'OOS')
def netR(t):
    rk = (t['r'] + CM.SLIP * CM.T + SLIPX) * PV + 2 * CM.COMM
    pts = t['pts'] - (SLIPX if t['why'] in CM.STOPWHY else 0)
    return (pts * PV - 2 * CM.COMM) / rk
def stats(tr):
    o = {}
    for b in ('IS', 'VAL', 'OOS'):
        R = [netR(t) for t in tr if blk(t['d']) == b and t['d'] <= FP.LAST]
        o[b] = dict(n=len(R), avg=round(sum(R) / len(R), 3) if R else None, sum=round(sum(R), 2))
    return o
def blend(a, b):
    kb = {(t['d'], t['eT'], t['side']): t for t in b}
    out = []
    for t in a:
        u = kb.get((t['d'], t['eT'], t['side']))
        if u is None: continue
        out.append((t, u))
    o = {}
    for bk in ('IS', 'VAL', 'OOS'):
        R = [(netR(x) + netR(y)) / 2 for x, y in out if blk(x['d']) == bk]
        o[bk] = dict(n=len(R), avg=round(sum(R) / len(R), 3) if R else None, sum=round(sum(R), 2))
    return o

GRID = {
    'V4+': [('live 1.25R be1', dict(tgtR=1.25, be_R=1.0, flat=900))] + [(f'{t}R be{b}', dict(tgtR=t, be_R=b, flat=900)) for t, b in itertools.product((1.0, 1.5, 2.0, 3.0), (None, .5, 1.0)) if not (t == 1.25 and b == 1.0)],
    'TDP': [('live 1.5R', dict(tgtR=1.5, flat=900))] + [(f'{t}R be{b}', dict(tgtR=t, be_R=b, flat=900)) for t, b in itertools.product((1.0, 2.0, 3.0, None), (None, 1.0)) ] + [('1.5R be1', dict(tgtR=1.5, be_R=1.0, flat=900))],
    'Pinball': [('live 2R 180m', dict(tgtR=2, cap=180, flat=900))] + [(f'{t}R be{b} 180m', dict(tgtR=t, be_R=b, cap=180, flat=900)) for t, b in itertools.product((1.0, 1.5, 3.0, None), (None, 1.0))] + [('2R be1 180m', dict(tgtR=2, be_R=1.0, cap=180, flat=900))],
    'H2': [('live 2R', dict(tgtR=2.0, flat=900))] + [(f'{t}R', dict(tgtR=t, flat=900)) for t in (1.0, 1.5, 3.0)],
    'D2': [('live 13:15', dict(th=.6, flat=795))] + [(f'be{b}', dict(th=.6, flat=795, be_R=b)) for b in (.5, 1.0)] + [(f'trail{tr}@{tg}', dict(th=.6, flat=795, trail_R=tr, trail_trig=tg)) for tr, tg in ((1.0, 1.0), (.75, 1.0), (1.0, 1.5))] + [(f'tgt{t}R', dict(th=.6, flat=795, tgtR=t)) for t in (1.0, 1.5, 2.0)] + [('t5 swing @1R', dict(th=.6, flat=795, t5=1.0))],
}
FN = {'V4+': CM.v4, 'TDP': CM.tdp, 'Pinball': CM.pinball, 'H2': CM.h2, 'D2': CM.d2}

def mfe_profile(tr):
    """for losers: share that first reached +0.5R / +1R; for winners: median MAE (R)."""
    o = {}
    for b in ('ALL',):
        L = [t for t in tr if netR(t) < 0]; W = [t for t in tr if netR(t) > 0]
        def mfe(t):
            bb = CM.DB.get(t['d']); s = t['side']; mx = 0; mn = 0
            for m, op, h, l, c in bb:
                if m < t['eT']: continue
                if m >= t['xT']: break
                mx = max(mx, (h - t['eP']) * s if s > 0 else t['eP'] - l); mn = max(mn, (t['eP'] - l) if s > 0 else h - t['eP'])
            return mx / t['r'], mn / t['r']
        Lm = [mfe(t)[0] for t in L]; Wm = [mfe(t)[1] for t in W]; Wx = [mfe(t)[0] for t in W]
        o = dict(losers=len(L), los_mfe_05=round(sum(x >= .5 for x in Lm) / max(1, len(Lm)), 2), los_mfe_1=round(sum(x >= 1 for x in Lm) / max(1, len(Lm)), 2),
                 win_mae_med=round(statistics.median(Wm), 2) if Wm else None, win_mae_p80=round(sorted(Wm)[int(.8 * len(Wm))], 2) if Wm else None,
                 win_mfe_med=round(statistics.median(Wx), 2) if Wx else None)
    return o

out = {}
for s, grid in GRID.items():
    res = {}; trs = {}
    for nm, kw in grid:
        tr = FN[s](**kw); trs[nm] = tr; res[nm] = stats(tr)
    live = grid[0][0]
    prof = mfe_profile([t for t in trs[live] if t['eT'] >= 570])
    # partial: live + each other variant 50/50
    part = {}
    for nm, _ in grid[1:]:
        part[f'50% {live} + 50% {nm}'] = blend(trs[live], trs[nm])
    allv = {**res, **part}
    best = max(allv, key=lambda k: (allv[k]['IS']['avg'] or -9))
    out[s] = dict(profile=prof, variants=res, partials=part, best_IS=best, tried=len(allv))
    print(f"\n=== {s}  MFE/MAE (live): {prof}")
    for k, v in sorted(allv.items(), key=lambda kv: -(kv[1]['IS']['avg'] or -9))[:8]:
        print(f"   {k:40s} " + ' | '.join(f"{b} n{v[b]['n']} {v[b]['avg']:+.3f}" if v[b]['avg'] is not None else f"{b} -" for b in ('IS', 'VAL', 'OOS')))
    print(f"   live {live:34s} " + ' | '.join(f"{b} n{res[live][b]['n']} {res[live][b]['avg']:+.3f}" for b in ('IS', 'VAL', 'OOS')), f"  (tried {len(allv)})")
json.dump(out, open(os.path.join(HERE, 'edge_exits.json'), 'w'), indent=1)
